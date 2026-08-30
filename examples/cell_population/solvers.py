"""Every applicable solver, and the three canonical baselines, on real data.

`docs/examples/solver-shootout.md` runs the whole dispatch table on one
synthetic problem. This module repeats that exercise on the FlowCyt study's
own rows: the same 27,607-row partition subsample and 200,000-row held-out
cohort every other page in `docs/usecases/flowcyt/` uses, split by the same
patient cohorts declared in `examples.cell_population.data`.

It answers the question the synthetic shootout cannot: whether the small
differences among information-aware solvers, and the large gap to the naive
baselines, survive contact with an estimated classifier score, unequal
patient weights, and a genuinely shifted held-out cohort. `run_solver_comparison`
returns the metrics `docs/usecases/flowcyt/solvers.md` quotes; every number on
that page is asserted from the committed JSON this module writes.

Every number this module produces is application code built on ScoreQuant's
public surface; it adds nothing to the library.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA

import scorequant as sq
from examples.baselines import (
    equal_frequency_1d,
    euclidean_kmeans_scores,
    rectangular_observation_bins,
)
from examples.solver_shootout import machine_note, median_seconds, retention
from examples.synthetic_problems import separable_1d_direction

from .data import FlowCytData
from .experiment import _prepare_experiment

#: Seed shared by every solver in this study, matching the rest of the section.
SEED = 2026

#: Operating bin budget, shared with the main experiment and the profiled study.
OPERATING_BINS = 8


@dataclass(frozen=True, slots=True)
class SolverInputs:
    """The rows and weights the solver comparison consumes.

    Attributes
    ----------
    partition_scores, partition_weights
        The 27,607-row partition subsample and its reference-measure weights,
        identical to the rows every learned rule in the main study is fitted
        on.
    partition_markers, test_markers
        Two leading PCA coordinates of the robust-transformed twelve markers,
        the same projection `quantization.md`'s two-dimensional grid baseline
        uses. `rectangular_observation_bins` operates on these coordinates
        rather than the raw twelve-axis marker space: a genuine twelve-axis
        equal-width grid with an eight-cell budget has less than one bin per
        axis and is not a meaningful baseline. The PCA is fit once on the
        partition rows and applied unchanged to the held-out rows.
    test_scores
        The frozen held-out cohort's score matrix.
    rows
        Row counts of every role, recorded for provenance.
    preparation_seconds
        Wall-clock seconds the score model, score construction, and the
        marker PCA took, carried with the inputs so a resumed run still
        publishes an honest total.
    """

    partition_scores: np.ndarray
    partition_weights: np.ndarray
    partition_markers: np.ndarray
    test_scores: np.ndarray
    test_markers: np.ndarray
    rows: dict[str, int]
    preparation_seconds: float


def solver_inputs_from_data(
    data: FlowCytData,
    *,
    quick: bool,
    seed: int = SEED,
    score_max_per_patient_class: int | None = None,
    score_max_iter: int | None = None,
) -> SolverInputs:
    """Build the solver-comparison inputs with the main study's own preparation path.

    Parameters
    ----------
    data
        The frozen fixture or the bounded all-patient sample.
    quick
        Use the short score-model settings.
    seed
        Seed of the score model, the deterministic role masks, and the marker
        PCA.
    score_max_per_patient_class, score_max_iter
        Optional overrides of the score-model budget. They exist so a
        fixture-scale regression test can exercise this path in seconds;
        published runs leave them unset.

    Returns
    -------
    SolverInputs
        The prepared inputs, carrying the preparation wall clock.
    """
    started = time.perf_counter()
    context = _prepare_experiment(
        data,
        quick=quick,
        seed=seed,
        score_max_per_patient_class=score_max_per_patient_class,
        score_max_iter=score_max_iter,
    )
    pca = PCA(n_components=2, random_state=seed).fit(
        context.transformed_markers[context.partition_mask]
    )
    inputs = SolverInputs(
        partition_scores=context.reference_scores[context.partition_mask],
        partition_weights=context.weights,
        partition_markers=np.asarray(
            pca.transform(context.transformed_markers[context.partition_mask])
        ),
        test_scores=context.test_scores,
        test_markers=np.asarray(pca.transform(context.transformed_test_markers)),
        rows={
            "total": int(len(data.labels)),
            "reference": int(len(context.reference.labels)),
            "test": int(len(context.test.labels)),
            "partition": int(np.count_nonzero(context.partition_mask)),
        },
        preparation_seconds=time.perf_counter() - started,
    )
    return inputs


def save_solver_inputs(inputs: SolverInputs, path: Path) -> None:
    """Cache prepared inputs so a long run can resume without refitting scores."""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        rows_json=np.asarray(json.dumps(inputs.rows)),
        preparation_seconds=np.asarray(inputs.preparation_seconds),
        **{
            name: np.asarray(getattr(inputs, name))
            for name in (
                "partition_scores",
                "partition_weights",
                "partition_markers",
                "test_scores",
                "test_markers",
            )
        },
    )


def load_solver_inputs(path: Path) -> SolverInputs:
    """Load inputs cached by `save_solver_inputs`."""
    with np.load(path, allow_pickle=False) as payload:
        return SolverInputs(
            partition_scores=payload["partition_scores"],
            partition_weights=payload["partition_weights"],
            partition_markers=payload["partition_markers"],
            test_scores=payload["test_scores"],
            test_markers=payload["test_markers"],
            rows=json.loads(str(payload["rows_json"])),
            preparation_seconds=float(payload["preparation_seconds"]),
        )


@dataclass(frozen=True, slots=True)
class MethodRow:
    """One solver or baseline's retention, cost, and search effort.

    The solver counters are never merged, following the library's own
    convention: `scans` and `accepted_moves` describe exchange work,
    `lloyd_iterations` describes guarded batch relabelings, and `iterations`
    describes k-means or soft-Voronoi step counts. A method that performs
    none of these leaves the corresponding field `None` rather than zero, so
    the JSON never claims a search that did not happen.

    Attributes
    ----------
    key, label, task, family, solver
        Identity of the method. `family` is ``"information_aware"`` for a
        ScoreQuant solver and ``"baseline"`` for one of the three canonical
        naive alternatives from `examples.baselines`.
    train_retention
        D-efficiency on the partition subsample, under the reference
        integration weights.
    held_out_retention
        D-efficiency on the frozen held-out cohort, under the empirical test
        measure (one unit of weight per cell), exactly as the rest of the
        section reports it.
    scans, accepted_moves, exchange_stable
        Exact-exchange counters, for `DExchangeConfig` and the exchange
        phase of `MahalanobisLloydConfig`.
    lloyd_iterations
        Guarded batch-relabeling count, for `MahalanobisLloydConfig` only.
    iterations
        Recorded step count of the k-means or soft-Voronoi trace.
    hardening_gap
        Soft-to-hard objective gap, for `SoftVoronoiConfig` only.
    seconds
        Median wall-clock seconds of one fit, after one warm-up call.
    """

    key: str
    label: str
    task: str
    family: str
    solver: str
    train_retention: float
    held_out_retention: float
    scans: int | None
    accepted_moves: int | None
    exchange_stable: bool | None
    lloyd_iterations: int | None
    iterations: int | None
    hardening_gap: float | None
    seconds: float


def _finite_rows(
    inputs: SolverInputs, *, n_bins: int, seed: int, initializer_restarts: int, timing_repeats: int
) -> list[MethodRow]:
    scores, weights = inputs.partition_scores, inputs.partition_weights
    test_scores = inputs.test_scores
    test_weights = np.ones(len(test_scores))
    source = sq.ScoreSample(scores, weights)
    specifications: list[tuple[str, str, str, sq.DExchangeConfig | sq.MahalanobisLloydConfig]] = [
        (
            "d_exchange",
            "Exact D exchange",
            "DExchangeConfig",
            sq.DExchangeConfig(seed=seed, initializer_restarts=initializer_restarts),
        ),
        (
            "mahalanobis_lloyd",
            "Guarded Mahalanobis-Lloyd",
            "MahalanobisLloydConfig",
            sq.MahalanobisLloydConfig(seed=seed, initializer_restarts=initializer_restarts),
        ),
    ]
    rows: list[MethodRow] = []
    for key, label, solver_name, config in specifications:
        partition = sq.optimize_partition(
            scores, weights=weights, n_bins=n_bins, criterion=sq.DOptimality(), config=config
        )

        def fit(
            config: sq.DExchangeConfig | sq.MahalanobisLloydConfig = config,
        ) -> sq.QuantizerResult:
            return sq.fit_quantizer(
                source, n_bins=n_bins, criterion=sq.DOptimality(), config=config
            )

        rule = fit()
        rows.append(
            MethodRow(
                key=key,
                label=label,
                task="fit_quantizer",
                family="information_aware",
                solver=solver_name,
                train_retention=float(partition.train_report.geometric_mean_retention),
                held_out_retention=retention(
                    test_scores,
                    np.asarray(rule.predict_scores(test_scores)),
                    test_weights,
                    n_bins,
                ),
                scans=int(partition.scans),
                accepted_moves=int(partition.accepted_moves),
                exchange_stable=bool(partition.exchange_stable),
                lloyd_iterations=int(partition.lloyd_iterations),
                iterations=None,
                hardening_gap=(None if rule.hardening_gap is None else float(rule.hardening_gap)),
                seconds=median_seconds(fit, timing_repeats),
            )
        )
    return rows


def _geometric_rows(
    inputs: SolverInputs,
    *,
    n_bins: int,
    seed: int,
    initializer_restarts: int,
    soft_steps: int,
    timing_repeats: int,
) -> list[MethodRow]:
    scores, weights = inputs.partition_scores, inputs.partition_weights
    test_scores = inputs.test_scores
    test_weights = np.ones(len(test_scores))
    source = sq.ScoreSample(scores, weights)
    rows: list[MethodRow] = []

    def fit_kmeans() -> sq.QuantizerResult:
        return sq.fit_quantizer(
            source,
            n_bins=n_bins,
            criterion=sq.NormalizedTrace(),
            config=sq.KMeansConfig(seed=seed, solver_restarts=initializer_restarts),
        )

    kmeans_rule = fit_kmeans()
    rows.append(
        MethodRow(
            key="whitened_kmeans",
            label="Whitened k-means",
            task="fit_quantizer",
            family="information_aware",
            solver="KMeansConfig",
            train_retention=float(kmeans_rule.train_report.geometric_mean_retention),
            held_out_retention=retention(
                test_scores,
                np.asarray(kmeans_rule.predict_scores(test_scores)),
                test_weights,
                n_bins,
            ),
            scans=None,
            accepted_moves=None,
            exchange_stable=None,
            lloyd_iterations=None,
            iterations=int(np.asarray(kmeans_rule.trace.steps)[-1]),
            hardening_gap=None,
            seconds=median_seconds(fit_kmeans, timing_repeats),
        )
    )

    def fit_soft() -> sq.QuantizerResult:
        return sq.fit_quantizer(
            source,
            n_bins=n_bins,
            criterion=sq.DOptimality(),
            config=sq.SoftVoronoiConfig(
                seed=seed,
                initializer_restarts=initializer_restarts,
                max_steps=soft_steps,
                record_every=max(soft_steps // 8, 1),
            ),
        )

    soft_rule = fit_soft()
    rows.append(
        MethodRow(
            key="soft_voronoi",
            label="Soft gradient descent",
            task="fit_quantizer",
            family="information_aware",
            solver="SoftVoronoiConfig",
            train_retention=float(soft_rule.train_report.geometric_mean_retention),
            held_out_retention=retention(
                test_scores,
                np.asarray(soft_rule.predict_scores(test_scores)),
                test_weights,
                n_bins,
            ),
            scans=None,
            accepted_moves=None,
            exchange_stable=None,
            lloyd_iterations=None,
            iterations=int(np.asarray(soft_rule.trace.steps)[-1]),
            hardening_gap=(
                None if soft_rule.hardening_gap is None else float(soft_rule.hardening_gap)
            ),
            seconds=median_seconds(fit_soft, timing_repeats),
        )
    )
    return rows


def _scalar_dp_row(
    inputs: SolverInputs, *, n_bins: int, seed: int, timing_repeats: int
) -> tuple[MethodRow, np.ndarray]:
    """Fit the exact scalar dynamic program on the study's 1D projection.

    Returns
    -------
    tuple of MethodRow, numpy.ndarray
        The method row, and the leading weighted-variance direction used for
        the projection -- the equal-frequency baseline shares the same
        direction, so the two scalar methods are compared on the same
        coordinate.
    """
    scores, weights = inputs.partition_scores, inputs.partition_weights
    test_scores = inputs.test_scores
    test_weights = np.ones(len(test_scores))
    direction = separable_1d_direction(scores, weights)
    projected_train = (scores @ direction)[:, None]
    projected_test = (test_scores @ direction)[:, None]

    def fit() -> sq.QuantizerResult:
        return sq.fit_quantizer(
            sq.ScoreSample(projected_train, weights),
            n_bins=n_bins,
            criterion=sq.DOptimality(),
            config=sq.ScalarDPConfig(seed=seed, max_rows=max(len(scores), 1)),
        )

    rule = fit()
    row = MethodRow(
        key="scalar_dp",
        label="Scalar DP on the 1D projection",
        task="fit_quantizer",
        family="information_aware",
        solver="ScalarDPConfig",
        train_retention=retention(
            scores, np.asarray(rule.predict_scores(projected_train)), weights, n_bins
        ),
        held_out_retention=retention(
            test_scores, np.asarray(rule.predict_scores(projected_test)), test_weights, n_bins
        ),
        scans=None,
        accepted_moves=None,
        exchange_stable=None,
        lloyd_iterations=None,
        iterations=None,
        hardening_gap=None,
        seconds=median_seconds(fit, timing_repeats),
    )
    return row, direction


def _baseline_rows(
    inputs: SolverInputs,
    direction: np.ndarray,
    *,
    n_bins: int,
    seed: int,
    timing_repeats: int,
) -> list[MethodRow]:
    """Score the three canonical baselines, each fit independently per split.

    Each baseline is recomputed on the training and the held-out split from
    that split's own rows, which is deliberately generous: the held-out
    column is really an in-sample fit, and the baselines still lose.
    """
    scores, weights = inputs.partition_scores, inputs.partition_weights
    test_scores = inputs.test_scores
    test_weights = np.ones(len(test_scores))
    projected_train = scores @ direction
    projected_test = test_scores @ direction

    rectangular_train = rectangular_observation_bins(inputs.partition_markers, total_budget=n_bins)
    rectangular_test = rectangular_observation_bins(inputs.test_markers, total_budget=n_bins)
    euclidean_train = euclidean_kmeans_scores(scores, n_bins, seed=seed)
    euclidean_test = euclidean_kmeans_scores(test_scores, n_bins, seed=seed)
    frequency_train = equal_frequency_1d(projected_train, n_bins)
    frequency_test = equal_frequency_1d(projected_test, n_bins)

    def empty_counters() -> dict[str, None]:
        return {
            "scans": None,
            "accepted_moves": None,
            "exchange_stable": None,
            "lloyd_iterations": None,
            "iterations": None,
            "hardening_gap": None,
        }

    return [
        MethodRow(
            key="rectangular_observation_bins",
            label="Rectangular observation bins (2D marker PCA)",
            task="baseline",
            family="baseline",
            solver="n/a",
            train_retention=retention(
                scores, rectangular_train, weights, int(rectangular_train.max()) + 1
            ),
            held_out_retention=retention(
                test_scores, rectangular_test, test_weights, int(rectangular_test.max()) + 1
            ),
            seconds=median_seconds(
                lambda: rectangular_observation_bins(inputs.partition_markers, total_budget=n_bins),
                timing_repeats,
            ),
            **empty_counters(),
        ),
        MethodRow(
            key="euclidean_kmeans_scores",
            label="Euclidean k-means on raw scores",
            task="baseline",
            family="baseline",
            solver="n/a",
            train_retention=retention(scores, euclidean_train, weights, n_bins),
            held_out_retention=retention(test_scores, euclidean_test, test_weights, n_bins),
            seconds=median_seconds(
                lambda: euclidean_kmeans_scores(scores, n_bins, seed=seed), timing_repeats
            ),
            **empty_counters(),
        ),
        MethodRow(
            key="equal_frequency_1d",
            label="Equal-frequency 1D bins",
            task="baseline",
            family="baseline",
            solver="n/a",
            train_retention=retention(scores, frequency_train, weights, n_bins),
            held_out_retention=retention(test_scores, frequency_test, test_weights, n_bins),
            seconds=median_seconds(
                lambda: equal_frequency_1d(projected_train, n_bins), timing_repeats
            ),
            **empty_counters(),
        ),
    ]


def run_solver_comparison(
    inputs: SolverInputs,
    *,
    quick: bool,
    n_bins: int = OPERATING_BINS,
    seed: int = SEED,
    provenance: dict[str, object] | None = None,
) -> dict[str, object]:
    """Run every applicable solver and every canonical baseline on real data.

    Parameters
    ----------
    inputs
        Prepared inputs from `solver_inputs_from_data`.
    quick
        Use short optimizer settings and fewer timing repeats.
    n_bins
        Bin budget, shared with the study's operating point.
    seed
        Seed shared by every solver.
    provenance
        Free-form provenance recorded verbatim in the metrics.

    Returns
    -------
    dict
        The metrics written to the committed JSON evidence, keyed exactly as
        `docs/usecases/flowcyt/solvers.md` asserts them.
    """
    initializer_restarts = 3 if quick else 8
    soft_steps = 50 if quick else 160
    timing_repeats = 1 if quick else 3
    started = time.perf_counter()

    dp_row, direction = _scalar_dp_row(
        inputs, n_bins=n_bins, seed=seed, timing_repeats=timing_repeats
    )
    methods = [
        *_finite_rows(
            inputs,
            n_bins=n_bins,
            seed=seed,
            initializer_restarts=initializer_restarts,
            timing_repeats=timing_repeats,
        ),
        *_geometric_rows(
            inputs,
            n_bins=n_bins,
            seed=seed,
            initializer_restarts=initializer_restarts,
            soft_steps=soft_steps,
            timing_repeats=timing_repeats,
        ),
        dp_row,
        *_baseline_rows(inputs, direction, n_bins=n_bins, seed=seed, timing_repeats=timing_repeats),
    ]
    fastest = min(row.seconds for row in methods if row.family == "information_aware")
    return {
        "study": "flowcyt_solvers",
        "n_bins": n_bins,
        "methods": [{**asdict(row), "seconds_ratio": row.seconds / fastest} for row in methods],
        "fastest_information_aware_seconds": fastest,
        "timing_note": (
            "Wall-clock seconds on one machine: one warm-up call, then the median of "
            "timing_repeats runs. Absolute values are hardware-specific; compare ratios."
        ),
        "machine": machine_note(),
        "run": {
            "quick": quick,
            "seed": seed,
            "initializer_restarts": initializer_restarts,
            "soft_steps": soft_steps,
            "timing_repeats": timing_repeats,
            "rows": dict(inputs.rows),
            "provenance": dict(provenance or {}),
            "seconds": {
                "score_model_and_scores": inputs.preparation_seconds,
                "study": time.perf_counter() - started,
            },
        },
    }


def write_solver_metrics(metrics: dict[str, object], path: Path) -> None:
    """Write one scale's metrics into the committed multi-scale evidence file.

    Parameters
    ----------
    metrics
        Metrics returned by `run_solver_comparison`.
    path
        JSON evidence path. Scales already present are preserved, so the
        fixture-scale and sample-scale runs regenerate independently.
    """
    run = metrics["run"]
    if not isinstance(run, dict):
        raise TypeError("metrics['run'] must be a mapping")
    scale = "fixture_scale" if run["quick"] else "sample_scale"
    payload: dict[str, object] = {}
    if path.is_file():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            payload = loaded
    payload[scale] = metrics
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2)
        stream.write("\n")
