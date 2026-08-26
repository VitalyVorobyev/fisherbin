"""The solver shootout: every applicable solver and baseline on one problem.

This script is the single deterministic generator behind the
`docs/examples/solver-shootout.md` page. It runs

* every configuration type the dispatch table in `scorequant.api` accepts, on
  each task that accepts it;
* the three canonical baselines from `examples.baselines`;
* a bin-budget sweep of the score-space versus observation-space gap;
* a score-rescaling probe that isolates what the Fisher metric buys;

and writes `docs/examples/assets/solver_shootout.json` plus
`docs/examples/assets/solver_shootout.png`.

Run it with::

    JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run python -m examples.solver_shootout

Timings are wall-clock medians measured on one machine after a warm-up call,
so the absolute seconds in the JSON are hardware-specific. Only their ratios
are quoted in prose.
"""

from __future__ import annotations

import json
import platform
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

import scorequant as sq
from examples._env import example_scale
from examples.baselines import (
    equal_frequency_1d,
    euclidean_kmeans_scores,
    rectangular_observation_bins,
)
from examples.synthetic_problems import (
    SyntheticProblem,
    separable_1d_direction,
    signal_background_shape,
    two_parameter_gaussian_mixture,
)

FIGURE_PATH = Path("docs/examples/assets/solver_shootout.png")
METRICS_PATH = Path("docs/examples/assets/solver_shootout.json")

#: Bin budget of the headline table. Sixteen is the generator's own default
#: and a perfect square, so the rectangular baseline gets a fair 4x4 grid.
HEADLINE_BINS = 16
#: Perfect-square budgets, so every sweep point gives the rectangular grid an
#: exact cell count rather than a rounded one.
BUDGET_SWEEP = (4, 9, 16, 25)
#: Multipliers applied to one score column in the rescaling probe.
SCALE_FACTORS = (1.0, 5.0, 25.0, 100.0)
#: Bin budget of the rescaling probe, which runs on a three-parameter problem.
SCALE_PROBE_BINS = 8
#: Seed shared by every solver in the comparison.
SOLVER_SEED = 7

type PartitionSolverConfig = sq.DExchangeConfig | sq.MahalanobisLloydConfig
type QuantizerSolverConfig = (
    sq.DExchangeConfig | sq.MahalanobisLloydConfig | sq.KMeansConfig | sq.SoftVoronoiConfig
)
type SolverCriterion = sq.DOptimality | sq.NormalizedTrace
type MetricRow = dict[str, object]


@dataclass(frozen=True, slots=True)
class MethodResult:
    """One method's retention and cost on the shootout problem.

    Attributes
    ----------
    key
        Stable machine-readable identifier, used as the JSON key and as the
        name the documentation page's assertions refer to.
    label
        Human-readable name used in the figure and the published tables.
    task
        ``"optimize_partition"``, ``"fit_quantizer"``, or ``"baseline"``.
    family
        ``"information_aware"`` for a ScoreQuant solver, ``"baseline"`` for
        one of the three canonical naive alternatives.
    train_retention
        D-efficiency of the training labeling.
    test_retention
        D-efficiency on the untouched test split, or ``None`` for
        `scorequant.optimize_partition`, whose result deliberately carries no
        predictor.
    seconds
        Median wall-clock seconds of one fit after a warm-up call.
    """

    key: str
    label: str
    task: str
    family: str
    train_retention: float
    test_retention: float | None
    seconds: float


def retention(scores: np.ndarray, labels: np.ndarray, weights: np.ndarray, n_bins: int) -> float:
    """Return the D-efficiency of an arbitrary hard labeling.

    Parameters
    ----------
    scores
        Score matrix with shape ``[N, P]``.
    labels
        Integer bin label per row, with shape ``[N]``.
    weights
        Nonnegative measure weights with shape ``[N]``.
    n_bins
        Number of bins the labeling uses, including empty ones.

    Returns
    -------
    float
        The geometric mean of the retained-information eigenvalues, from
        `scorequant.information_report`. Baseline labelings are scored with
        exactly this function, so no baseline number is hand-rolled algebra.
    """
    report = sq.information_report(scores, labels, weights, n_bins=n_bins)
    return float(report.geometric_mean_retention)


def median_seconds(run: Callable[[], object], repeats: int) -> float:
    """Time a callable honestly: one warm-up call, then the median of `repeats`.

    Parameters
    ----------
    run
        Zero-argument callable performing exactly one fit.
    repeats
        Number of timed repetitions after the warm-up call.

    Returns
    -------
    float
        Median wall-clock seconds. The warm-up call absorbs JAX tracing and
        compilation, so the reported median measures steady-state work.
    """
    run()
    samples = [_one_timing(run) for _ in range(repeats)]
    return float(np.median(samples))


def _one_timing(run: Callable[[], object]) -> float:
    start = time.perf_counter()
    run()
    return time.perf_counter() - start


def projection_direction(problem: SyntheticProblem) -> np.ndarray:
    """Return the training-set 1D projection axis the scalar solvers share.

    Parameters
    ----------
    problem
        A synthetic problem whose training split defines the axis.

    Returns
    -------
    numpy.ndarray
        A unit direction with shape ``[P]``. Both the scalar dynamic program
        and the equal-frequency baseline project every split onto this one
        training-set axis, so the two scalar methods are compared on the same
        coordinate.
    """
    return separable_1d_direction(problem.train.scores, problem.train.weights)


def _partition_entries(problem: SyntheticProblem, *, timing_repeats: int) -> list[MethodResult]:
    train = problem.train
    entries: list[MethodResult] = []
    solvers: list[tuple[str, str, PartitionSolverConfig]] = [
        ("partition_d_exchange", "Exact D exchange", sq.DExchangeConfig(seed=SOLVER_SEED)),
        (
            "partition_mahalanobis_lloyd",
            "Guarded Mahalanobis-Lloyd",
            sq.MahalanobisLloydConfig(seed=SOLVER_SEED),
        ),
    ]
    for key, label, config in solvers:

        def fit(config: PartitionSolverConfig = config) -> sq.PartitionResult:
            return sq.optimize_partition(
                train.scores,
                weights=train.weights,
                n_bins=problem.n_bins,
                criterion=sq.DOptimality(),
                config=config,
            )

        entries.append(
            MethodResult(
                key=key,
                label=label,
                task="optimize_partition",
                family="information_aware",
                train_retention=float(fit().report().geometric_mean_retention),
                test_retention=None,
                seconds=median_seconds(fit, timing_repeats),
            )
        )
    return entries


def _quantizer_entries(
    problem: SyntheticProblem, *, soft_steps: int, timing_repeats: int
) -> list[MethodResult]:
    train, test = problem.train, problem.test
    n_bins = problem.n_bins
    source = sq.ScoreSample(train.scores, train.weights)
    entries: list[MethodResult] = []
    solvers: list[tuple[str, str, SolverCriterion, QuantizerSolverConfig]] = [
        (
            "quantizer_d_exchange",
            "Exact D exchange",
            sq.DOptimality(),
            sq.DExchangeConfig(seed=SOLVER_SEED),
        ),
        (
            "quantizer_mahalanobis_lloyd",
            "Guarded Mahalanobis-Lloyd",
            sq.DOptimality(),
            sq.MahalanobisLloydConfig(seed=SOLVER_SEED),
        ),
        (
            "quantizer_whitened_kmeans",
            "Whitened k-means",
            sq.NormalizedTrace(),
            sq.KMeansConfig(seed=SOLVER_SEED, n_init=8),
        ),
        (
            "quantizer_soft_voronoi",
            "Soft gradient descent",
            sq.DOptimality(),
            sq.SoftVoronoiConfig(
                seed=SOLVER_SEED,
                n_init=8,
                max_steps=soft_steps,
                record_every=max(soft_steps // 8, 1),
            ),
        ),
    ]
    for key, label, criterion, config in solvers:

        def fit(
            criterion: SolverCriterion = criterion, config: QuantizerSolverConfig = config
        ) -> sq.QuantizerResult:
            return sq.fit_quantizer(source, n_bins=n_bins, criterion=criterion, config=config)

        rule = fit()
        entries.append(
            MethodResult(
                key=key,
                label=label,
                task="fit_quantizer",
                family="information_aware",
                train_retention=retention(
                    train.scores,
                    np.asarray(rule.predict_scores(train.scores)),
                    train.weights,
                    n_bins,
                ),
                test_retention=retention(
                    test.scores,
                    np.asarray(rule.predict_scores(test.scores)),
                    test.weights,
                    n_bins,
                ),
                seconds=median_seconds(fit, timing_repeats),
            )
        )
    return entries


def _scalar_dp_entry(
    problem: SyntheticProblem,
    projected_train: np.ndarray,
    projected_test: np.ndarray,
    *,
    timing_repeats: int,
) -> MethodResult:
    train, test = problem.train, problem.test

    def fit() -> sq.QuantizerResult:
        return sq.fit_quantizer(
            sq.ScoreSample(projected_train, train.weights),
            n_bins=problem.n_bins,
            criterion=sq.DOptimality(),
            config=sq.ScalarDPConfig(seed=SOLVER_SEED),
        )

    rule = fit()
    return MethodResult(
        key="quantizer_scalar_dp",
        label="Scalar DP on the 1D projection",
        task="fit_quantizer",
        family="information_aware",
        train_retention=retention(
            train.scores,
            np.asarray(rule.predict_scores(projected_train)),
            train.weights,
            problem.n_bins,
        ),
        test_retention=retention(
            test.scores,
            np.asarray(rule.predict_scores(projected_test)),
            test.weights,
            problem.n_bins,
        ),
        seconds=median_seconds(fit, timing_repeats),
    )


def _baseline_entries(
    problem: SyntheticProblem,
    projected_train: np.ndarray,
    projected_test: np.ndarray,
    *,
    timing_repeats: int,
) -> list[MethodResult]:
    train, test = problem.train, problem.test
    n_bins = problem.n_bins

    rectangular_train = rectangular_observation_bins(train.observations, total_budget=n_bins)
    rectangular_test = rectangular_observation_bins(test.observations, total_budget=n_bins)
    euclidean_train = euclidean_kmeans_scores(train.scores, n_bins, seed=SOLVER_SEED)
    euclidean_test = euclidean_kmeans_scores(test.scores, n_bins, seed=SOLVER_SEED)
    frequency_train = equal_frequency_1d(projected_train[:, 0], n_bins)
    frequency_test = equal_frequency_1d(projected_test[:, 0], n_bins)
    return [
        MethodResult(
            key="baseline_rectangular_observation_bins",
            label="Rectangular observation bins",
            task="baseline",
            family="baseline",
            train_retention=retention(
                train.scores, rectangular_train, train.weights, int(rectangular_train.max()) + 1
            ),
            test_retention=retention(
                test.scores, rectangular_test, test.weights, int(rectangular_test.max()) + 1
            ),
            seconds=median_seconds(
                lambda: rectangular_observation_bins(train.observations, total_budget=n_bins),
                timing_repeats,
            ),
        ),
        MethodResult(
            key="baseline_euclidean_kmeans_scores",
            label="Euclidean k-means on raw scores",
            task="baseline",
            family="baseline",
            train_retention=retention(train.scores, euclidean_train, train.weights, n_bins),
            test_retention=retention(test.scores, euclidean_test, test.weights, n_bins),
            seconds=median_seconds(
                lambda: euclidean_kmeans_scores(train.scores, n_bins, seed=SOLVER_SEED),
                timing_repeats,
            ),
        ),
        MethodResult(
            key="baseline_equal_frequency_1d",
            label="Equal-frequency 1D bins",
            task="baseline",
            family="baseline",
            train_retention=retention(train.scores, frequency_train, train.weights, n_bins),
            test_retention=retention(test.scores, frequency_test, test.weights, n_bins),
            seconds=median_seconds(
                lambda: equal_frequency_1d(projected_train[:, 0], n_bins), timing_repeats
            ),
        ),
    ]


def compare_methods(
    problem: SyntheticProblem, *, soft_steps: int, timing_repeats: int
) -> list[MethodResult]:
    """Run every applicable solver and every baseline on one problem.

    Parameters
    ----------
    problem
        A synthetic problem with train and test splits.
    soft_steps
        Adam step budget of the soft-Voronoi solver.
    timing_repeats
        Timed repetitions per method, after one warm-up call.

    Returns
    -------
    list of MethodResult
        One entry per method, in publication order: the two partition
        solvers, the five quantizer solvers, then the three baselines.
    """
    direction = projection_direction(problem)
    projected_train = (problem.train.scores @ direction)[:, None]
    projected_test = (problem.test.scores @ direction)[:, None]
    return [
        *_partition_entries(problem, timing_repeats=timing_repeats),
        *_quantizer_entries(problem, soft_steps=soft_steps, timing_repeats=timing_repeats),
        _scalar_dp_entry(problem, projected_train, projected_test, timing_repeats=timing_repeats),
        *_baseline_entries(problem, projected_train, projected_test, timing_repeats=timing_repeats),
    ]


def rectangular_gap_sweep(
    budgets: tuple[int, ...], *, sizes: tuple[int, int, int]
) -> list[dict[str, float]]:
    """Measure the score-space versus rectangular-grid gap at several budgets.

    Parameters
    ----------
    budgets
        Perfect-square bin budgets, so the equal-width observation grid gets
        an exact cell count at every point.
    sizes
        Train, validation, and test split sizes handed to the generator.

    Returns
    -------
    list of dict
        One entry per budget with the exact-exchange quantizer's held-out
        D-efficiency, the rectangular baseline's, and their difference.
    """
    rows: list[dict[str, float]] = []
    for n_bins in budgets:
        problem = two_parameter_gaussian_mixture(n_bins=n_bins, sizes=sizes)
        train, test = problem.train, problem.test
        rule = sq.fit_quantizer(
            sq.ScoreSample(train.scores, train.weights),
            n_bins=n_bins,
            criterion=sq.DOptimality(),
            config=sq.DExchangeConfig(seed=SOLVER_SEED),
        )
        score_space = retention(
            test.scores, np.asarray(rule.predict_scores(test.scores)), test.weights, n_bins
        )
        grid = rectangular_observation_bins(test.observations, total_budget=n_bins)
        observation_space = retention(test.scores, grid, test.weights, int(grid.max()) + 1)
        rows.append(
            {
                "n_bins": float(n_bins),
                "score_space": score_space,
                "observation_space": observation_space,
                "gap": score_space - observation_space,
            }
        )
    return rows


def whitening_probe(problem: SyntheticProblem) -> dict[str, float]:
    """Compare whitened and unwhitened k-means on the shootout problem.

    An exact linear component score satisfies ``sum_k c_k s_k = 1``, so a
    two-parameter problem's whole score cloud lies on one affine line. Every
    linear map, whitening included, acts along that line as a single uniform
    rescaling, and k-means is invariant to a uniform rescaling. This probe
    measures that prediction instead of asserting it.

    Parameters
    ----------
    problem
        The shootout problem.

    Returns
    -------
    dict
        Held-out D-efficiency with ``whiten=True`` and with ``whiten=False``.
    """
    train, test = problem.train, problem.test
    values: dict[str, float] = {}
    for name, whiten in (("whitened", True), ("unwhitened", False)):
        rule = sq.fit_quantizer(
            sq.ScoreSample(train.scores, train.weights),
            n_bins=problem.n_bins,
            criterion=sq.NormalizedTrace(),
            config=sq.KMeansConfig(seed=SOLVER_SEED, n_init=8, whiten=whiten),
        )
        values[name] = retention(
            test.scores,
            np.asarray(rule.predict_scores(test.scores)),
            test.weights,
            problem.n_bins,
        )
    return values


def scale_sensitivity(
    *, scales: tuple[float, ...], n_bins: int, sizes: tuple[int, int, int]
) -> list[dict[str, float]]:
    """Rescale one score column and watch which method survives it.

    The shootout's own two-parameter score cloud is confined to a line, where
    rescaling cannot change any k-means partition at all. This probe therefore
    runs on `examples.synthetic_problems.signal_background_shape` with two
    background shapes, whose three score columns span a genuinely
    two-dimensional cloud, and multiplies the signal column by each scale.
    Rescaling a score column is a reparameterization, and D-efficiency is
    invariant under a reparameterization, so any change in a method's number
    is that method reacting to units it should not be able to see.

    Parameters
    ----------
    scales
        Multipliers applied to score column zero.
    n_bins
        Bin budget for both methods.
    sizes
        Train, validation, and test split sizes handed to the generator.

    Returns
    -------
    list of dict
        One entry per scale with the whitened-fit and the raw-score Euclidean
        k-means held-out D-efficiency.
    """
    problem = signal_background_shape(background_rates=(1.0, 4.0), n_bins=n_bins, sizes=sizes)
    train, test = problem.train, problem.test
    rows: list[dict[str, float]] = []
    for scale in scales:
        factors = np.ones(train.scores.shape[1])
        factors[0] = scale
        scaled_train = train.scores * factors
        scaled_test = test.scores * factors
        rule = sq.fit_quantizer(
            sq.ScoreSample(scaled_train, train.weights),
            n_bins=n_bins,
            criterion=sq.NormalizedTrace(),
            config=sq.KMeansConfig(seed=SOLVER_SEED, n_init=8),
        )
        rows.append(
            {
                "scale": float(scale),
                "whitened": retention(
                    scaled_test,
                    np.asarray(rule.predict_scores(scaled_test)),
                    test.weights,
                    n_bins,
                ),
                "euclidean": retention(
                    scaled_test,
                    euclidean_kmeans_scores(scaled_test, n_bins, seed=SOLVER_SEED),
                    test.weights,
                    n_bins,
                ),
            }
        )
    return rows


def machine_note() -> dict[str, str]:
    """Describe the machine the committed timings were measured on.

    Returns
    -------
    dict
        Platform, machine architecture, and Python version strings.
    """
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
    }


def run_study(
    *,
    n_bins: int = HEADLINE_BINS,
    sizes: tuple[int, int, int] | None = None,
    soft_steps: int | None = None,
    timing_repeats: int | None = None,
    budgets: tuple[int, ...] = BUDGET_SWEEP,
    scales: tuple[float, ...] = SCALE_FACTORS,
) -> dict[str, object]:
    """Run the whole shootout and return its JSON-ready metrics.

    Parameters
    ----------
    n_bins
        Bin budget of the headline comparison.
    sizes
        Train, validation, and test split sizes. Defaults to the fast-mode
        aware sizes from `examples._env.example_scale`.
    soft_steps
        Adam step budget of the soft-Voronoi solver.
    timing_repeats
        Timed repetitions per method after one warm-up call.
    budgets
        Bin budgets used by the score-space-versus-grid sweep.
    scales
        Score-column multipliers used by the rescaling probe.

    Returns
    -------
    dict
        The exact structure written to
        ``docs/examples/assets/solver_shootout.json``.
    """
    sizes = example_scale((4_000, 2_000, 15_000), (800, 400, 2_000)) if sizes is None else sizes
    soft_steps = example_scale(400, 60) if soft_steps is None else soft_steps
    timing_repeats = example_scale(5, 1) if timing_repeats is None else timing_repeats

    problem = two_parameter_gaussian_mixture(n_bins=n_bins, sizes=sizes)
    methods = compare_methods(problem, soft_steps=soft_steps, timing_repeats=timing_repeats)
    fastest = min(method.seconds for method in methods if method.family == "information_aware")
    return {
        "problem": problem.name,
        "n_bins": n_bins,
        "n_train": int(problem.train.scores.shape[0]),
        "n_test": int(problem.test.scores.shape[0]),
        "soft_steps": soft_steps,
        "timing_repeats": timing_repeats,
        "timing_note": (
            "Wall-clock seconds on one machine: one warm-up call, then the median of "
            "timing_repeats runs. Absolute values are hardware-specific; compare ratios."
        ),
        "machine": machine_note(),
        "fastest_information_aware_seconds": fastest,
        "methods": [
            {**asdict(method), "seconds_ratio": method.seconds / fastest} for method in methods
        ],
        "budget_sweep": rectangular_gap_sweep(budgets, sizes=sizes),
        "whitening_probe": whitening_probe(problem),
        "scale_probe": {
            "problem": "signal_background_shape",
            "n_bins": SCALE_PROBE_BINS,
            "entries": scale_sensitivity(scales=scales, n_bins=SCALE_PROBE_BINS, sizes=sizes),
        },
    }


def _rows(metrics: dict[str, object], key: str) -> list[MetricRow]:
    value = metrics[key]
    if not isinstance(value, list):
        raise TypeError(f"metrics[{key!r}] must be a list of rows")
    return [row for row in value if isinstance(row, dict)]


def _number(row: MetricRow, key: str) -> float:
    value = row[key]
    if not isinstance(value, (int, float)):
        raise TypeError(f"row[{key!r}] must be numeric")
    return float(value)


def _text(row: MetricRow, key: str) -> str:
    value = row[key]
    if not isinstance(value, str):
        raise TypeError(f"row[{key!r}] must be a string")
    return value


def make_figure(metrics: dict[str, object]) -> Figure:
    """Render the four-panel shootout dashboard.

    Parameters
    ----------
    metrics
        The mapping returned by `run_study`.

    Returns
    -------
    matplotlib.figure.Figure
        Retention by method, cost per fit, the bin-budget sweep, and the
        score-rescaling probe.
    """
    rows = _rows(metrics, "methods")
    figure, axes = plt.subplots(2, 2, figsize=(13.5, 9.0), constrained_layout=True)

    scored = [row for row in rows if row["test_retention"] is not None]
    held_out = [_number(row, "test_retention") for row in scored]
    train_values = [_number(row, "train_retention") for row in scored]
    # Every method here retains more than 93% of the information, so plotting
    # retention directly compresses the interesting differences into the last
    # pixel of the axis. The deficit ``1 - D-efficiency`` on a log axis keeps
    # the ordering and shows the two orders of magnitude that separate the
    # information-aware solvers from the observation-space grid.
    positions = np.arange(len(scored))
    bars = axes[0, 0].barh(
        positions,
        [1.0 - value for value in held_out],
        color=["#c0563c" if _text(row, "family") == "baseline" else "#38618c" for row in scored],
    )
    axes[0, 0].scatter(
        [1.0 - value for value in train_values],
        positions,
        color="black",
        s=18,
        zorder=3,
        label="train deficit",
    )
    axes[0, 0].bar_label(bars, labels=[f"{value:.5f}" for value in held_out], padding=4)
    axes[0, 0].set(
        yticks=positions,
        yticklabels=[_text(row, "label") for row in scored],
        xscale="log",
        xlim=(3e-4, 1.0),
        xlabel="held-out information deficit, 1 - D-efficiency (lower is better)",
        title="Retention by method (bar labels are D-efficiency)",
    )
    axes[0, 0].invert_yaxis()
    axes[0, 0].legend(loc="lower right")

    seconds = [_number(row, "seconds") for row in rows]
    cost_positions = np.arange(len(rows))
    axes[0, 1].barh(
        cost_positions,
        seconds,
        color=["#c0563c" if _text(row, "family") == "baseline" else "#38618c" for row in rows],
    )
    axes[0, 1].set(
        yticks=cost_positions,
        yticklabels=[
            f"{_text(row, 'label')} ({_text(row, 'task').replace('_', ' ')})" for row in rows
        ],
        xscale="log",
        xlabel="median seconds per fit (log scale)",
        title="Cost per fit on one machine",
    )
    axes[0, 1].invert_yaxis()

    sweep = _rows(metrics, "budget_sweep")
    budgets = [_number(row, "n_bins") for row in sweep]
    axes[1, 0].plot(
        budgets,
        [_number(row, "score_space") for row in sweep],
        marker="o",
        color="#38618c",
        label="score space (exact D exchange)",
    )
    axes[1, 0].plot(
        budgets,
        [_number(row, "observation_space") for row in sweep],
        marker="s",
        color="#c0563c",
        label="rectangular observation grid",
    )
    axes[1, 0].set(
        xlabel="bin budget",
        ylabel="held-out D-efficiency",
        xticks=budgets,
        title="The gap holds at every bin budget",
    )
    axes[1, 0].legend()

    probe = metrics["scale_probe"]
    if not isinstance(probe, dict):
        raise TypeError("metrics['scale_probe'] must be a mapping")
    entries = _rows(probe, "entries")
    scales = [_number(row, "scale") for row in entries]
    axes[1, 1].plot(
        scales,
        [_number(row, "whitened") for row in entries],
        marker="o",
        color="#38618c",
        label="whitened fit",
    )
    axes[1, 1].plot(
        scales,
        [_number(row, "euclidean") for row in entries],
        marker="s",
        color="#c0563c",
        label="Euclidean k-means on raw scores",
    )
    axes[1, 1].set(
        xscale="log",
        xlabel="multiplier on one score column",
        ylabel="held-out D-efficiency",
        title="Rescaling one score column",
    )
    axes[1, 1].legend()

    figure.suptitle("Solver shootout: two-parameter Gaussian mixture")
    return figure


def main() -> None:
    """Run the study, then write the committed JSON and figure."""
    jax.config.update("jax_enable_x64", True)

    metrics = run_study()
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with METRICS_PATH.open("w", encoding="utf-8") as stream:
        json.dump(metrics, stream, indent=2)
        stream.write("\n")
    figure = make_figure(metrics)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(FIGURE_PATH, dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    main()
