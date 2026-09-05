"""The HEP classifier study: profiled D_s against two naive baselines.

Runs the whole arc: a profiled-\\(D_s\\) partition at a headline bin budget and
a sweep against the certified `efficient_score_bound` ceiling (D6, D7); the two
naive baselines a physicist would reach for first, scored on the *same*
criteria (D5); a three-point `delta` convergence study (D4); and a reusable
`fit_quantizer`/`SoftVoronoiConfig` rule (D8).

Every labeling is scored twice -- full-D and profiled D_s -- because that
disagreement is the whole point (D7). D6 states the central claim as a
*prediction*: measure it, and report whatever the run produces, including a
small, zero, or reversed gap.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

import scorequant as sq
from examples._env import example_scale

from .data import HepData, load_fixture
from .scores import (
    INTEREST,
    SCHEMA,
    HepScoreProvider,
    SignalBackgroundOOF,
    assemble_score_sample,
    event_folds,
    fit_final_provider,
    fit_signal_background_oof,
    fit_tes_oof,
)

FIGURE_PATH = Path("docs/examples/assets/hep-classifier.png")
METRICS_PATH = Path("docs/examples/assets/hep-classifier.json")

#: Bin budget of the headline comparison. The spike's own record (D9) reports
#: an effective rank of 3 -- the full parameter count -- at this budget.
HEADLINE_BINS = 6
#: Bin budgets swept against the certified profiled ceiling.
BUDGET_SWEEP = (3, 4, 6, 8)
#: Headline finite-difference half-offset (D4) and the three-point
#: convergence study around it, matching the fixture's committed tes points.
HEADLINE_DELTA = 0.05
DELTA_SWEEP = (0.025, 0.05, 0.10)
#: Seed shared by every finite-D and soft solver in the study.
SOLVER_SEED = 11
#: Base seed for the deterministic event-fold assignment.
FOLD_SEED = 2026

type MetricRow = dict[str, object]


@dataclass(frozen=True, slots=True)
class LabelingScore:
    """Both retention numbers a labeling earns, and the binned profiled information.

    Attributes
    ----------
    full_retention
        Geometric-mean retention of the whole three-parameter Fisher matrix.
    profiled_retention
        Geometric-mean retention of the profiled information of
        `mu_htautau` alone.
    profiled_information
        The scalar binned Schur complement itself.
    """

    full_retention: float
    profiled_retention: float
    profiled_information: float


def score_labeling(
    scores: np.ndarray, labels: np.ndarray, weights: np.ndarray, *, n_bins: int
) -> LabelingScore:
    """Score one hard labeling on both the full and the profiled criterion."""
    full = sq.information_report(scores, labels, weights, n_bins=n_bins)
    profiled = sq.profiled_information_report(
        scores, labels, interest=INTEREST, weights=weights, n_bins=n_bins
    )
    return LabelingScore(
        full_retention=float(full.geometric_mean_retention),
        profiled_retention=float(profiled.geometric_mean_retention),
        profiled_information=float(np.asarray(profiled.schur_binned)[0, 0]),
    )


def unbinned_profiled_information(scores: np.ndarray, weights: np.ndarray) -> float:
    """Return the unbinned profiled information of `mu_htautau`.

    This is the certified ceiling's reference denominator.
    """
    information = np.asarray(sq.fisher_information(scores, weights))
    nuisance = [index for index in range(information.shape[0]) if index not in set(INTEREST)]
    interest_indices = list(INTEREST)
    block = information[np.ix_(interest_indices, interest_indices)]
    cross = information[np.ix_(interest_indices, nuisance)]
    nuisance_block = information[np.ix_(nuisance, nuisance)]
    schur = block - cross @ np.linalg.solve(nuisance_block, cross.T)
    return float(schur[0, 0])


def equal_frequency_labels(signal_posterior: np.ndarray, n_bins: int) -> np.ndarray:
    """Bin events into equal-frequency cells of the calibrated signal posterior.

    This is D5's first naive baseline: "bin the network output", the
    standard practice a physicist reaches for first.
    """
    edges = np.quantile(signal_posterior, np.linspace(0.0, 1.0, n_bins + 1)[1:-1])
    return np.digitize(signal_posterior, edges)


def logit_equal_width_labels(signal_posterior: np.ndarray, n_bins: int) -> np.ndarray:
    """Bin events into equal-width cells of the logit of the signal posterior.

    The strongest one-dimensional binning of the classifier output found for
    this study, and the one the headline gap is quoted against. Equal-width
    cells in the posterior itself waste most of their range, because a
    calibrated posterior on a 0.1% signal fraction piles up near zero; the
    logit spreads that pile out. Keeping it alongside the equal-frequency
    baseline is the point: *how* the network output is binned moves the
    retained profiled information by more than a factor of two, so a single
    "we binned the classifier" number would not have been a fair comparison.
    """
    logit = np.log(signal_posterior / (1.0 - signal_posterior))
    edges = np.linspace(logit.min(), logit.max(), n_bins + 1)[1:-1]
    return np.digitize(logit, edges)


def threshold_cut_labels(
    signal_posterior: np.ndarray, weights: np.ndarray, is_signal: np.ndarray
) -> tuple[np.ndarray, float]:
    """Return the two-bin signal-region cut maximizing weighted S/sqrt(B).

    D5's second naive baseline: the most recognizable one there is.
    """
    order = np.argsort(signal_posterior)
    sorted_posterior = signal_posterior[order]
    signal_weight = np.where(is_signal[order], weights[order], 0.0)
    background_weight = np.where(~is_signal[order], weights[order], 0.0)
    cumulative_signal = np.cumsum(signal_weight[::-1])[::-1]
    cumulative_background = np.cumsum(background_weight[::-1])[::-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        significance = np.where(
            cumulative_background > 0,
            cumulative_signal / np.sqrt(cumulative_background),
            0.0,
        )
    best_index = int(np.argmax(significance))
    threshold = float(sorted_posterior[best_index])
    labels = (signal_posterior >= threshold).astype(np.int64)
    return labels, threshold


@dataclass(frozen=True, slots=True)
class PartitionRow:
    """One labeling of the training sample, scored both ways.

    Attributes
    ----------
    key, label, criterion
        Stable identifier, published name, and the criterion (or baseline
        recipe) that produced the labels.
    n_bins
        Number of bins the labeling actually uses.
    full_retention, profiled_retention
        The two retention numbers from `score_labeling`.
    """

    key: str
    label: str
    criterion: str
    n_bins: int
    full_retention: float
    profiled_retention: float


def _row(
    key: str,
    label: str,
    criterion: str,
    scores: np.ndarray,
    labels: np.ndarray,
    weights: np.ndarray,
    n_bins: int,
) -> PartitionRow:
    scored = score_labeling(scores, labels, weights, n_bins=n_bins)
    return PartitionRow(
        key, label, criterion, n_bins, scored.full_retention, scored.profiled_retention
    )


@dataclass(frozen=True, slots=True)
class HeadlinePartitions:
    """The ScoreQuant partitions and naive baselines the headline table compares.

    Attributes
    ----------
    rows
        Published rows for every labeling.
    d_labels, ds_labels
        The two ScoreQuant labelings, kept for the figure.
    ceiling
        The certified efficient-score bound at `HEADLINE_BINS`.
    """

    rows: list[PartitionRow]
    d_labels: np.ndarray = field(repr=False)
    ds_labels: np.ndarray = field(repr=False)
    ds_partition: sq.PartitionResult = field(repr=False)
    ceiling: sq.EfficientScoreBound = field(repr=False)


def headline_partitions(
    sample: sq.ScoreSample,
    signal_posterior: np.ndarray,
    is_signal: np.ndarray,
    *,
    n_bins: int = HEADLINE_BINS,
) -> HeadlinePartitions:
    """Optimize the ScoreQuant partitions and score both naive baselines.

    Parameters
    ----------
    sample
        Out-of-fold `ScoreSample` from `assemble_score_sample`.
    signal_posterior
        Calibrated out-of-fold signal posterior, shape ``[N]``, the input the
        two naive baselines bin directly.
    is_signal
        Boolean signal label per event.
    n_bins
        Bin budget shared by the ScoreQuant partitions and the classifier-
        quantile baseline. The threshold-cut baseline always uses two.

    Returns
    -------
    HeadlinePartitions
        Every published row plus the ScoreQuant labelings and the ceiling.
    """
    config = sq.DExchangeConfig(seed=SOLVER_SEED)
    ceiling = sq.efficient_score_bound(
        sample.scores, interest=INTEREST, weights=sample.weights, n_bins=n_bins
    )
    d_partition = sq.optimize_partition(
        sample, n_bins=n_bins, criterion=sq.DOptimality(), config=config
    )
    ds_partition = sq.optimize_partition(
        sample,
        n_bins=n_bins,
        criterion=sq.ProfiledDOptimality(("mu_htautau",)),
        config=config,
        initial_labels=ceiling.labels,
    )
    quantile_labels = equal_frequency_labels(signal_posterior, n_bins)
    logit_labels = logit_equal_width_labels(signal_posterior, n_bins)
    threshold_labels, threshold = threshold_cut_labels(
        signal_posterior, np.asarray(sample.weights), is_signal
    )
    rows = [
        _row(
            "d_partition",
            "Plain D",
            "DOptimality",
            sample.scores,
            np.asarray(d_partition.labels),
            sample.weights,
            n_bins,
        ),
        _row(
            "ds_partition",
            "Profiled D_s",
            "ProfiledDOptimality",
            sample.scores,
            np.asarray(ds_partition.labels),
            sample.weights,
            n_bins,
        ),
        _row(
            "classifier_quantile",
            f"Classifier quantile bins ({n_bins})",
            "naive baseline",
            sample.scores,
            quantile_labels,
            sample.weights,
            n_bins,
        ),
        _row(
            "classifier_logit_equal_width",
            f"Classifier logit equal-width bins ({n_bins})",
            "naive baseline",
            sample.scores,
            logit_labels,
            sample.weights,
            n_bins,
        ),
        _row(
            "threshold_cut",
            f"Threshold cut at eta_s={threshold:.4f}",
            "naive baseline",
            sample.scores,
            threshold_labels,
            sample.weights,
            2,
        ),
    ]
    return HeadlinePartitions(
        rows=rows,
        d_labels=np.asarray(d_partition.labels),
        ds_labels=np.asarray(ds_partition.labels),
        ds_partition=ds_partition,
        ceiling=ceiling,
    )


def ceiling_sweep(
    sample: sq.ScoreSample, signal_posterior: np.ndarray, budgets: tuple[int, ...]
) -> list[MetricRow]:
    """Sweep the bin budget: profiled D_s, the classifier-quantile baseline, and the ceiling."""
    reference = unbinned_profiled_information(sample.scores, sample.weights)
    config = sq.DExchangeConfig(seed=SOLVER_SEED)
    criterion = sq.ProfiledDOptimality(("mu_htautau",))
    rows: list[MetricRow] = []
    for n_bins in budgets:
        bound = sq.efficient_score_bound(
            sample.scores, interest=INTEREST, weights=sample.weights, n_bins=n_bins
        )
        ds_partition = sq.optimize_partition(
            sample, n_bins=n_bins, criterion=criterion, config=config, initial_labels=bound.labels
        )
        ds_score = score_labeling(
            sample.scores, np.asarray(ds_partition.labels), sample.weights, n_bins=n_bins
        )
        quantile_labels = equal_frequency_labels(signal_posterior, n_bins)
        quantile_score = score_labeling(
            sample.scores, quantile_labels, sample.weights, n_bins=n_bins
        )
        rows.append(
            {
                "n_bins": float(n_bins),
                "ds_profiled_retention": ds_score.profiled_retention,
                "classifier_quantile_profiled_retention": quantile_score.profiled_retention,
                "ceiling_retention": float(np.exp(bound.upper_bound - np.log(reference))),
                "gap": float(bound.gap_to(ds_partition)),
                "scans": int(ds_partition.scans),
                "accepted_moves": int(ds_partition.accepted_moves),
            }
        )
    return rows


@dataclass(frozen=True, slots=True)
class DeltaRow:
    """One point of the delta convergence study.

    Attributes
    ----------
    delta
        The finite-difference half-offset.
    minus_plus_auc
        Out-of-fold AUC of the minus/plus classification task itself.
    near_half_fraction
        Fraction of events within `NEAR_HALF_TOLERANCE` of an
        undecided (0.5) posterior at the nominal point.
    ds_profiled_retention
        Profiled D_s retention at `HEADLINE_BINS` under this delta's score.
    ceiling_retention
        The certified ceiling at `HEADLINE_BINS` under this delta's score.
    """

    delta: float
    minus_plus_auc: float
    near_half_fraction: float
    ds_profiled_retention: float
    ceiling_retention: float


def delta_convergence_study(
    data: HepData, sigbg: SignalBackgroundOOF, fold_ids: np.ndarray, *, max_iter: int
) -> tuple[list[DeltaRow], dict[str, float]]:
    """Recompute the tes score at each swept delta and report the agreement (D4).

    Parameters
    ----------
    data
        The loaded fixture.
    sigbg
        Out-of-fold signal/background posteriors, shared across every delta
        (the rate columns do not depend on delta).
    fold_ids
        Shared per-event fold assignment.
    max_iter
        Boosting round budget for each delta's `tes` classifier.

    Returns
    -------
    tuple
        The three-point table, and an agreement summary between the headline
        delta and delta/2 -- "a disagreement is a result to report, not a
        parameter to tune away" (D4).
    """
    rows: list[DeltaRow] = []
    tes_columns: dict[float, np.ndarray] = {}
    config = sq.DExchangeConfig(seed=SOLVER_SEED)
    criterion = sq.ProfiledDOptimality(("mu_htautau",))
    for delta in DELTA_SWEEP:
        tes = fit_tes_oof(
            data, delta=delta, fold_ids=fold_ids, max_iter=max_iter, seed=FOLD_SEED + 500
        )
        sample = assemble_score_sample(data, sigbg, tes)
        tes_columns[delta] = np.asarray(sample.scores)[:, 2]
        bound = sq.efficient_score_bound(
            sample.scores, interest=INTEREST, weights=sample.weights, n_bins=HEADLINE_BINS
        )
        reference = unbinned_profiled_information(sample.scores, sample.weights)
        ds_partition = sq.optimize_partition(
            sample,
            n_bins=HEADLINE_BINS,
            criterion=criterion,
            config=config,
            initial_labels=bound.labels,
        )
        scored = score_labeling(
            sample.scores, np.asarray(ds_partition.labels), sample.weights, n_bins=HEADLINE_BINS
        )
        rows.append(
            DeltaRow(
                delta=delta,
                minus_plus_auc=tes.minus_plus_auc,
                near_half_fraction=tes.near_half_fraction,
                ds_profiled_retention=scored.profiled_retention,
                ceiling_retention=float(np.exp(bound.upper_bound - np.log(reference))),
            )
        )
    half = HEADLINE_DELTA / 2.0
    headline_column = tes_columns[HEADLINE_DELTA]
    half_column = next(value for delta, value in tes_columns.items() if abs(delta - half) < 1e-9)
    correlation = float(np.corrcoef(headline_column, half_column)[0, 1])
    by_delta = {row.delta: row for row in rows}
    agreement = {
        "headline_delta": HEADLINE_DELTA,
        "half_delta": half,
        "score_correlation": correlation,
        "retention_gap": abs(
            by_delta[HEADLINE_DELTA].ds_profiled_retention - by_delta[half].ds_profiled_retention
        ),
    }
    return rows, agreement


@dataclass(frozen=True, slots=True)
class ReusableRuleRow:
    """The reusable soft-Voronoi rule, scored on its own training sample.

    Attributes
    ----------
    train_full_retention, train_profiled_retention
        Retention of the rule's own labels, read from `QuantizerResult`'s
        own guarded reports -- the same reports `fit_quantizer` computes and
        checks internally, rather than re-deriving them from a different
        score realization.
    """

    train_full_retention: float
    train_profiled_retention: float
    hardening_gap: float | None


def reusable_rule(
    data: HepData, provider: HepScoreProvider, *, n_bins: int, soft_steps: int
) -> ReusableRuleRow:
    """Fit a reusable rule with `fit_quantizer`/`SoftVoronoiConfig` (D8).

    Finite profiled-D_s labels have no compile bridge, so a reusable profiled
    rule must be fitted as one. The rule is trained and scored on the
    full-sample classifiers (D8: "the classifier is trained inside the
    example"): an honest, explicitly in-sample deliverable given the fixture
    has no separate held-out split. Its train report is *not* re-derived
    against the leakage-free out-of-fold study sample -- the two score
    tables are different realizations of the same classifiers (full-fit
    versus cross-fitted), and predicting one rule's labels onto the other's
    score table can starve a bin's nuisance columns of rank in a way
    `fit_quantizer`'s own guard never sees, so this reads the guarded
    reports `fit_quantizer` already computed instead.
    """
    source = sq.ObservationSample(data.features_at(1.0), data.weights)
    rule = sq.fit_quantizer(
        source,
        provider=provider,
        n_bins=n_bins,
        criterion=sq.ProfiledDOptimality(("mu_htautau",)),
        config=sq.SoftVoronoiConfig(
            seed=SOLVER_SEED,
            initializer_restarts=8,
            max_steps=soft_steps,
            record_every=max(soft_steps // 8, 1),
        ),
    )
    if rule.train_profiled_report is None:
        raise ValueError("a ProfiledDOptimality fit must report train_profiled_report")
    return ReusableRuleRow(
        float(rule.train_report.geometric_mean_retention),
        float(rule.train_profiled_report.geometric_mean_retention),
        rule.hardening_gap,
    )


@dataclass(frozen=True, slots=True)
class Study:
    """Everything the doc page, the figure, and the tests need from one run."""

    metrics: dict[str, object]
    signal_posterior: np.ndarray = field(repr=False)
    tes_score: np.ndarray = field(repr=False)
    is_signal: np.ndarray = field(repr=False)
    d_labels: np.ndarray = field(repr=False)
    ds_labels: np.ndarray = field(repr=False)


def run_study(
    *,
    max_iter: int | None = None,
    n_folds: int | None = None,
    soft_steps: int | None = None,
    budgets: tuple[int, ...] | None = None,
) -> Study:
    """Run the whole HEP classifier study and return its metrics and arrays.

    Parameters
    ----------
    max_iter
        Boosting round budget for every classifier fit. Defaults to
        `examples._env.example_scale(300, 60)`.
    n_folds
        Number of stratified event folds. Defaults to ``example_scale(5, 3)``.
    soft_steps
        Adam step budget of the reusable soft-Voronoi rule. Defaults to
        ``example_scale(400, 80)``.
    budgets
        Bin budgets swept against the certified ceiling. Defaults to
        ``example_scale(BUDGET_SWEEP, (3, 6))``.

    Returns
    -------
    Study
        The exact structure written to
        ``docs/examples/assets/hep-classifier.json``, together with the
        arrays the figure draws.
    """
    max_iter = example_scale(300, 60) if max_iter is None else max_iter
    n_folds = example_scale(5, 3) if n_folds is None else n_folds
    soft_steps = example_scale(400, 80) if soft_steps is None else soft_steps
    budgets = example_scale(BUDGET_SWEEP, (3, 6)) if budgets is None else budgets

    data = load_fixture()
    fold_ids = event_folds(data.is_signal, n_folds=n_folds, seed=FOLD_SEED)

    start = time.perf_counter()
    sigbg = fit_signal_background_oof(
        data, fold_ids=fold_ids, max_iter=max_iter, seed=FOLD_SEED + 100
    )
    sigbg_seconds = time.perf_counter() - start

    start = time.perf_counter()
    tes = fit_tes_oof(
        data, delta=HEADLINE_DELTA, fold_ids=fold_ids, max_iter=max_iter, seed=FOLD_SEED + 500
    )
    tes_seconds = time.perf_counter() - start

    sample = assemble_score_sample(data, sigbg, tes)
    signal_posterior = sigbg.probabilities[:, 1]

    headline = headline_partitions(sample, signal_posterior, data.is_signal, n_bins=HEADLINE_BINS)
    sweep = ceiling_sweep(sample, signal_posterior, budgets)
    delta_rows, delta_agreement = delta_convergence_study(data, sigbg, fold_ids, max_iter=max_iter)

    start = time.perf_counter()
    final_provider = fit_final_provider(
        data, delta=HEADLINE_DELTA, max_iter=max_iter, seed=FOLD_SEED + 900
    )
    rule = reusable_rule(data, final_provider, n_bins=HEADLINE_BINS, soft_steps=soft_steps)
    rule_seconds = time.perf_counter() - start

    reference = unbinned_profiled_information(sample.scores, sample.weights)
    by_key = {row.key: row for row in headline.rows}
    metrics: dict[str, object] = {
        "fixture": {
            "n_events": data.n_events,
            "weight_sum": float(np.sum(data.weights)),
            "signal_events": int(np.count_nonzero(data.is_signal)),
            "background_events": int(np.count_nonzero(~data.is_signal)),
        },
        "n_bins": HEADLINE_BINS,
        "interest": list(INTEREST),
        "schema": list(SCHEMA.parameters),
        "delta": HEADLINE_DELTA,
        "n_folds": n_folds,
        "classifier_max_iter": max_iter,
        "soft_steps": soft_steps,
        "classifiers": {
            "signal_weighted_auc": sigbg.weighted_auc,
            "signal_temperature": sigbg.temperature,
            "signal_fraction": sigbg.signal_fraction,
            "signal_seconds": sigbg_seconds,
            "tes_minus_plus_auc": tes.minus_plus_auc,
            "tes_temperature": tes.temperature,
            "tes_near_half_fraction": tes.near_half_fraction,
            "tes_seconds": tes_seconds,
        },
        "partitions": [asdict(row) for row in headline.rows],
        "criterion_trade": {
            "full_retention_given_up": (
                by_key["d_partition"].full_retention - by_key["ds_partition"].full_retention
            ),
            "profiled_retention_gained": (
                by_key["ds_partition"].profiled_retention - by_key["d_partition"].profiled_retention
            ),
        },
        # The gap is quoted against the *strongest* classifier-output binning, not
        # the first one tried. Equal-frequency and logit-equal-width cells of the
        # same posterior differ by more than a factor of two in retained profiled
        # information, so naming one of them "the naive baseline" would have set
        # the comparison's difficulty by accident.
        "scorequant_vs_classifier_binning": {
            "best_baseline_key": max(
                ("classifier_quantile", "classifier_logit_equal_width"),
                key=lambda key: by_key[key].profiled_retention,
            ),
            "profiled_retention_gap": (
                by_key["ds_partition"].profiled_retention
                - max(
                    by_key["classifier_quantile"].profiled_retention,
                    by_key["classifier_logit_equal_width"].profiled_retention,
                )
            ),
            "profiled_retention_gap_to_equal_frequency": (
                by_key["ds_partition"].profiled_retention
                - by_key["classifier_quantile"].profiled_retention
            ),
            "baseline_spread": abs(
                by_key["classifier_quantile"].profiled_retention
                - by_key["classifier_logit_equal_width"].profiled_retention
            ),
            "full_retention_gap": (
                by_key["ds_partition"].full_retention
                - max(
                    by_key["classifier_quantile"].full_retention,
                    by_key["classifier_logit_equal_width"].full_retention,
                )
            ),
        },
        "ceiling": {
            "upper_bound": float(headline.ceiling.upper_bound),
            "ceiling_retention": float(np.exp(headline.ceiling.upper_bound - np.log(reference))),
            "gap_to_ds_partition": float(headline.ceiling.gap_to(headline.ds_partition)),
        },
        "ceiling_sweep": sweep,
        "delta_convergence": {
            "rows": [asdict(row) for row in delta_rows],
            "agreement": delta_agreement,
        },
        "reusable_rule": {
            "train_full_retention": rule.train_full_retention,
            "train_profiled_retention": rule.train_profiled_retention,
            "hardening_gap": rule.hardening_gap,
            "seconds": rule_seconds,
        },
    }
    return Study(
        metrics=metrics,
        signal_posterior=signal_posterior,
        tes_score=np.asarray(sample.scores)[:, 2],
        is_signal=data.is_signal,
        d_labels=headline.d_labels,
        ds_labels=headline.ds_labels,
    )


def main() -> None:
    """Run the study and write the committed JSON and figure."""
    import jax
    import matplotlib.pyplot as plt

    from .figures import make_figure

    jax.config.update("jax_enable_x64", True)

    study = run_study()
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with METRICS_PATH.open("w", encoding="utf-8") as stream:
        json.dump(study.metrics, stream, indent=2)
        stream.write("\n")
    figure = make_figure(study)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURE_PATH, dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    main()
