"""Signal fraction with a background-shape nuisance: plain D against profiled D_s.

This script is the single deterministic generator behind the
`docs/examples/nuisance-profiled-ds.md` page. It runs

* the same bin budget under `scorequant.DOptimality` and under
  `scorequant.ProfiledDOptimality`, and scores both labelings twice -- once on
  the full Fisher matrix and once on the profiled (efficient) information of
  the signal fraction alone;
* the certified efficient-score ceiling from `scorequant.efficient_score_bound`,
  the measured gap between that ceiling and what exchange achieves, and the same
  exchange restarted from the ceiling's own interval labels;
* reusable rules for both criteria, so the comparison also has a held-out
  column: a compiled D partition for `DOptimality`, and a soft profiled fit for
  `ProfiledDOptimality`, which has no compile bridge;
* a downstream extended-Poisson binned maximum-likelihood fit of the signal
  fraction with the background coefficients floating, scanned deterministically
  with a profile likelihood;

and writes `docs/examples/assets/nuisance-profiled-ds.json` plus
`docs/examples/assets/nuisance-profiled-ds.png`.

Run it with::

    JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run python -m examples.nuisance_profiled_ds
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

import scorequant as sq
from examples._env import example_scale
from examples.synthetic_problems import SignalBackgroundProblem, signal_background_shape

FIGURE_PATH = Path("docs/examples/assets/nuisance-profiled-ds.png")
METRICS_PATH = Path("docs/examples/assets/nuisance-profiled-ds.json")

#: Bin budget of the headline comparison. A tight budget is where the choice of
#: criterion has to matter: with enough cells every sensible rule retains almost
#: everything and the two criteria stop disagreeing.
HEADLINE_BINS = 4
#: Bin budgets swept against the certified ceiling. Three is the smallest budget
#: a three-parameter score law admits under plain D.
BUDGET_SWEEP = (3, 4, 5, 6, 8)
#: Seed shared by every solver in the study.
SOLVER_SEED = 11
#: Expectation-maximization steps used to profile the background coefficients at
#: each scanned signal fraction. The profile problem is a concave Poisson
#: likelihood in two coefficients, so this is a generous budget.
EM_ITERATIONS = 400
#: Points in the profile-likelihood scan of the signal fraction.
SCAN_POINTS = 121
#: Half-width of that scan, in units of the reference standard deviation.
SCAN_WIDTH_IN_SIGMA = 3.0

type MetricRow = dict[str, object]


def build_problem(
    *, n_bins: int = HEADLINE_BINS, sizes: tuple[int, int, int] | None = None
) -> SignalBackgroundProblem:
    """Return the signal-plus-two-backgrounds problem this study runs on.

    Parameters
    ----------
    n_bins
        Bin budget recorded on the problem.
    sizes
        Train, validation, and test split sizes. Defaults to the fast-mode
        aware sizes from `examples._env.example_scale`.

    Returns
    -------
    SignalBackgroundProblem
        Column 0 of every score matrix is the signal fraction; columns 1 and 2
        are the two background-shape nuisances.
    """
    resolved = example_scale((4_000, 2_000, 15_000), (800, 400, 2_000)) if sizes is None else sizes
    return signal_background_shape(
        background_rates=(1.0, 4.0), n_bins=n_bins, sizes=resolved, seed=50
    )


@dataclass(frozen=True, slots=True)
class LabelingScore:
    """Both retention numbers a labeling earns, plus the profiled information.

    Attributes
    ----------
    full_retention
        Geometric-mean retention of the whole three-parameter Fisher matrix,
        from `scorequant.information_report`.
    profiled_retention
        Geometric-mean retention of the profiled (efficient) information of the
        signal fraction alone, from `scorequant.profiled_information_report`.
    profiled_information
        The scalar binned Schur complement itself, whose reciprocal square root
        is the asymptotic standard deviation of the binned signal-fraction
        estimate.
    """

    full_retention: float
    profiled_retention: float
    profiled_information: float


def score_labeling(
    scores: np.ndarray,
    labels: np.ndarray,
    weights: np.ndarray,
    *,
    interest: tuple[int, ...],
    n_bins: int,
) -> LabelingScore:
    """Score one hard labeling on both the full and the profiled criterion.

    Parameters
    ----------
    scores
        Score matrix with shape ``[N, P]`` in the declared parameter order.
    labels
        Integer bin label per row, with shape ``[N]``.
    weights
        Nonnegative measure weights with shape ``[N]``.
    interest
        Score-column indices of the parameters of interest.
    n_bins
        Number of bins the labeling uses, including empty ones.

    Returns
    -------
    LabelingScore
        Both retention numbers and the binned profiled information. Neither
        number depends on which criterion produced `labels`, which is what
        makes the two criteria comparable at all.
    """
    full = sq.information_report(scores, labels, weights, n_bins=n_bins)
    profiled = sq.profiled_information_report(
        scores, labels, interest=interest, weights=weights, n_bins=n_bins
    )
    return LabelingScore(
        full_retention=float(full.geometric_mean_retention),
        profiled_retention=float(profiled.geometric_mean_retention),
        profiled_information=float(np.asarray(profiled.schur_binned)[0, 0]),
    )


def unbinned_profiled_information(
    scores: np.ndarray, weights: np.ndarray, *, interest: tuple[int, ...]
) -> float:
    """Return the unbinned profiled information of the interest parameter.

    Parameters
    ----------
    scores, weights
        The weighted score table defining the reference measure.
    interest
        Score-column indices of the parameters of interest. Exactly one is
        supported, matching the certified bound.

    Returns
    -------
    float
        The scalar Schur complement of the unbinned Fisher matrix. This is the
        ceiling no binning can reach, and dividing a binned value by it gives
        the profiled retention.
    """
    information = np.asarray(sq.fisher_information(scores, weights))
    nuisance = [index for index in range(information.shape[0]) if index not in set(interest)]
    interest_indices = list(interest)
    block = information[np.ix_(interest_indices, interest_indices)]
    cross = information[np.ix_(interest_indices, nuisance)]
    nuisance_block = information[np.ix_(nuisance, nuisance)]
    schur = block - cross @ np.linalg.solve(nuisance_block, cross.T)
    return float(schur[0, 0])


def partition_agreement(first: np.ndarray, second: np.ndarray, n_bins: int) -> float:
    """Return the adjusted Rand index between two labelings of the same rows.

    Bin labels carry no meaning of their own, so two partitions can only be
    compared through which rows they place together. The adjusted Rand index
    does exactly that, is invariant to relabeling, equals one for identical
    partitions, and is near zero for unrelated ones. It is computed from the
    ``[n_bins, n_bins]`` contingency table, so the cost is linear in the number
    of rows.

    Parameters
    ----------
    first, second
        Integer labelings with shape ``[N]``.
    n_bins
        Number of bins both labelings declare.

    Returns
    -------
    float
        The adjusted Rand index.
    """
    table = np.zeros((n_bins, n_bins))
    np.add.at(table, (np.asarray(first), np.asarray(second)), 1.0)

    def pairs(counts: np.ndarray) -> float:
        return float(np.sum(counts * (counts - 1.0) / 2.0))

    within = pairs(table)
    rows = pairs(table.sum(axis=1))
    columns = pairs(table.sum(axis=0))
    total = pairs(np.asarray([table.sum()]))
    expected = rows * columns / total
    return (within - expected) / ((rows + columns) / 2.0 - expected)


def interval_runs(observations: np.ndarray, labels: np.ndarray) -> int:
    """Count the contiguous observation intervals one labeling induces.

    Parameters
    ----------
    observations
        One-dimensional observation coordinates with shape ``[N, 1]``.
    labels
        Integer bin label per row.

    Returns
    -------
    int
        Number of maximal runs of a constant label once rows are sorted by
        observation. A partition whose cells are plain intervals of the
        observable uses exactly as many runs as it has cells; more runs mean
        cells that the observable alone cannot separate.
    """
    order = np.argsort(np.asarray(observations)[:, 0], kind="stable")
    sequence = np.asarray(labels)[order]
    return 1 + int(np.sum(np.diff(sequence) != 0))


@dataclass(frozen=True, slots=True)
class PartitionRow:
    """One finite partition of the training sample, scored both ways.

    Attributes
    ----------
    key, label, criterion
        Stable identifier, published name, and the criterion that produced it.
    full_retention, profiled_retention
        The two retention numbers from `score_labeling`.
    objective
        The criterion's own objective at the terminal labeling.
    scans, accepted_moves
        Exchange counters of the run.
    seconds
        Wall-clock seconds of the single fit.
    cell_weights
        Reference measure carried by each cell.
    """

    key: str
    label: str
    criterion: str
    full_retention: float
    profiled_retention: float
    objective: float
    scans: int
    accepted_moves: int
    seconds: float
    cell_weights: list[float]


def _partition_row(
    key: str,
    label: str,
    criterion: str,
    result: sq.PartitionResult,
    score: LabelingScore,
    seconds: float,
) -> PartitionRow:
    return PartitionRow(
        key=key,
        label=label,
        criterion=criterion,
        full_retention=score.full_retention,
        profiled_retention=score.profiled_retention,
        objective=float(result.objective),
        scans=int(result.scans),
        accepted_moves=int(result.accepted_moves),
        seconds=seconds,
        cell_weights=[float(value) for value in np.asarray(result.cell_weights)],
    )


@dataclass(frozen=True, slots=True)
class FinitePartitions:
    """The three finite partitions the page compares, with their labels.

    Attributes
    ----------
    rows
        Published rows for plain D, generically seeded profiled D_s, and
        profiled D_s started from the certified ceiling's own labels.
    d_labels, cold_labels, warm_labels
        The three labelings themselves, kept for the figure and the downstream
        likelihood fit.
    cold_history, warm_history
        Objective histories of the two profiled runs.
    """

    rows: list[PartitionRow]
    d_labels: np.ndarray = field(repr=False)
    cold_labels: np.ndarray = field(repr=False)
    warm_labels: np.ndarray = field(repr=False)
    cold_history: np.ndarray = field(repr=False)
    warm_history: np.ndarray = field(repr=False)


def finite_partitions(
    problem: SignalBackgroundProblem,
    *,
    n_bins: int,
    bound: sq.EfficientScoreBound,
) -> FinitePartitions:
    """Optimize the same sample under both criteria, and both profiled seedings.

    Parameters
    ----------
    problem
        The signal-plus-backgrounds problem.
    n_bins
        Bin budget shared by all three runs.
    bound
        The certified efficient-score ceiling for this sample and budget. Its
        labels seed the third run.

    Returns
    -------
    FinitePartitions
        Published rows plus the labelings and objective histories.
    """
    train = problem.train
    config = sq.DExchangeConfig(seed=SOLVER_SEED)
    profiled_criterion = sq.ProfiledDOptimality(problem.interest)

    def scored(result: sq.PartitionResult) -> LabelingScore:
        return score_labeling(
            train.scores,
            np.asarray(result.labels),
            train.weights,
            interest=problem.interest,
            n_bins=n_bins,
        )

    start = time.perf_counter()
    plain = sq.optimize_partition(
        train.scores,
        weights=train.weights,
        n_bins=n_bins,
        criterion=sq.DOptimality(),
        config=config,
    )
    plain_seconds = time.perf_counter() - start

    start = time.perf_counter()
    cold = sq.optimize_partition(
        train.scores,
        weights=train.weights,
        n_bins=n_bins,
        criterion=profiled_criterion,
        config=config,
    )
    cold_seconds = time.perf_counter() - start

    start = time.perf_counter()
    warm = sq.optimize_partition(
        train.scores,
        weights=train.weights,
        n_bins=n_bins,
        criterion=profiled_criterion,
        config=config,
        initial_labels=bound.labels,
    )
    warm_seconds = time.perf_counter() - start

    rows = [
        _partition_row(
            "d_partition", "Plain D", "DOptimality", plain, scored(plain), plain_seconds
        ),
        _partition_row(
            "ds_partition_seeded",
            "Profiled D_s, generic seeding",
            "ProfiledDOptimality",
            cold,
            scored(cold),
            cold_seconds,
        ),
        _partition_row(
            "ds_partition_initialized",
            "Profiled D_s, ceiling-initialized",
            "ProfiledDOptimality",
            warm,
            scored(warm),
            warm_seconds,
        ),
    ]
    return FinitePartitions(
        rows=rows,
        d_labels=np.asarray(plain.labels),
        cold_labels=np.asarray(cold.labels),
        warm_labels=np.asarray(warm.labels),
        cold_history=np.asarray(cold.objective_history),
        warm_history=np.asarray(warm.objective_history),
    )


@dataclass(frozen=True, slots=True)
class RuleRow:
    """One reusable rule, scored on the training and the held-out split.

    Attributes
    ----------
    key, label, criterion, solver
        Identity of the fit.
    train_full_retention, train_profiled_retention
        Retention of the rule's own training labels.
    test_full_retention, test_profiled_retention
        Retention of the same rule applied to the untouched test split.
    """

    key: str
    label: str
    criterion: str
    solver: str
    train_full_retention: float
    train_profiled_retention: float
    test_full_retention: float
    test_profiled_retention: float


def reusable_rules(
    problem: SignalBackgroundProblem, *, n_bins: int, soft_steps: int
) -> list[RuleRow]:
    """Fit a reusable rule under each criterion and score it out of sample.

    The two criteria need different solvers here, and the reason is a theorem
    rather than a preference. An exchange-stable D partition compiles into a
    Mahalanobis nearest-cell rule that reproduces its own labels; a profiled
    partition has no such canonical extension, so a reusable profiled rule must
    be fitted as one, which `scorequant.SoftVoronoiConfig` does.

    Parameters
    ----------
    problem
        The signal-plus-backgrounds problem.
    n_bins
        Bin budget shared by both fits.
    soft_steps
        Adam step budget of the soft profiled fit.

    Returns
    -------
    list of RuleRow
        One row per criterion, each with a train and a held-out column.
    """
    train, test = problem.train, problem.test
    source = sq.ScoreSample(train.scores, train.weights)
    fits: list[tuple[str, str, str, str, sq.QuantizerResult]] = [
        (
            "d_rule",
            "Plain D, compiled exchange",
            "DOptimality",
            "DExchangeConfig",
            sq.fit_quantizer(
                source,
                n_bins=n_bins,
                criterion=sq.DOptimality(),
                config=sq.DExchangeConfig(seed=SOLVER_SEED),
            ),
        ),
        (
            "ds_rule",
            "Profiled D_s, soft Voronoi",
            "ProfiledDOptimality",
            "SoftVoronoiConfig",
            sq.fit_quantizer(
                source,
                validation=sq.ScoreSample(test.scores, test.weights),
                n_bins=n_bins,
                criterion=sq.ProfiledDOptimality(problem.interest),
                config=sq.SoftVoronoiConfig(
                    seed=SOLVER_SEED,
                    n_init=8,
                    max_steps=soft_steps,
                    record_every=max(soft_steps // 8, 1),
                ),
            ),
        ),
    ]
    rows: list[RuleRow] = []
    for key, label, criterion, solver, rule in fits:
        on_train = score_labeling(
            train.scores,
            np.asarray(rule.predict_scores(train.scores)),
            train.weights,
            interest=problem.interest,
            n_bins=n_bins,
        )
        on_test = score_labeling(
            test.scores,
            np.asarray(rule.predict_scores(test.scores)),
            test.weights,
            interest=problem.interest,
            n_bins=n_bins,
        )
        rows.append(
            RuleRow(
                key=key,
                label=label,
                criterion=criterion,
                solver=solver,
                train_full_retention=on_train.full_retention,
                train_profiled_retention=on_train.profiled_retention,
                test_full_retention=on_test.full_retention,
                test_profiled_retention=on_test.profiled_retention,
            )
        )
    return rows


def ceiling_sweep(
    problem: SignalBackgroundProblem, budgets: tuple[int, ...]
) -> list[dict[str, float]]:
    """Sweep the bin budget against the certified profiled ceiling.

    Every budget runs three fits: the plain-D partition, the profiled partition
    from generic seeding, and the profiled partition started from the ceiling's
    own interval labels. Recording all three is what separates the two things
    the initializer can buy -- a better optimum, and the same optimum sooner.

    Parameters
    ----------
    problem
        The signal-plus-backgrounds problem.
    budgets
        Bin budgets to evaluate.

    Returns
    -------
    list of dict
        One entry per budget with the three profiled retentions, the certified
        ceiling, both certified gaps, and the exchange counters of both
        profiled runs.
    """
    train = problem.train
    reference = unbinned_profiled_information(
        train.scores, train.weights, interest=problem.interest
    )
    config = sq.DExchangeConfig(seed=SOLVER_SEED)
    criterion = sq.ProfiledDOptimality(problem.interest)
    rows: list[dict[str, float]] = []

    def profiled_retention(result: sq.PartitionResult, n_bins: int) -> float:
        return score_labeling(
            train.scores,
            np.asarray(result.labels),
            train.weights,
            interest=problem.interest,
            n_bins=n_bins,
        ).profiled_retention

    for n_bins in budgets:
        bound = sq.efficient_score_bound(
            train.scores, interest=problem.interest, weights=train.weights, n_bins=n_bins
        )
        plain = sq.optimize_partition(
            train.scores,
            weights=train.weights,
            n_bins=n_bins,
            criterion=sq.DOptimality(),
            config=config,
        )
        seeded = sq.optimize_partition(
            train.scores,
            weights=train.weights,
            n_bins=n_bins,
            criterion=criterion,
            config=config,
        )
        initialized = sq.optimize_partition(
            train.scores,
            weights=train.weights,
            n_bins=n_bins,
            criterion=criterion,
            config=config,
            initial_labels=bound.labels,
        )
        rows.append(
            {
                "n_bins": float(n_bins),
                "d_profiled_retention": profiled_retention(plain, n_bins),
                "ds_seeded_retention": profiled_retention(seeded, n_bins),
                "ds_initialized_retention": profiled_retention(initialized, n_bins),
                "ceiling_retention": float(np.exp(bound.upper_bound - np.log(reference))),
                "seeded_gap": float(bound.gap_to(seeded)),
                "initialized_gap": float(bound.gap_to(initialized)),
                "seeded_scans": float(seeded.scans),
                "initialized_scans": float(initialized.scans),
                "seeded_moves": float(seeded.accepted_moves),
                "initialized_moves": float(initialized.accepted_moves),
            }
        )
    return rows


def component_bin_matrix(
    problem: SignalBackgroundProblem, labels: np.ndarray, *, n_bins: int
) -> np.ndarray:
    """Accumulate each component's expected yield in each bin.

    The reference coordinates are drawn uniformly on the unit interval, so a
    plain sum of a component density over the rows of a bin is a Monte Carlo
    estimate of that component's integral over the bin, scaled by the row count.
    Writing the expected bin contents as ``nu_b(c) = sum_k c_k A[b, k]`` then
    makes the extended Poisson likelihood's Fisher information *exactly* the
    matrix `scorequant.binned_fisher_information` returns for the same labels,
    which is what lets the scan below be checked against the library rather than
    merely illustrate it.

    Parameters
    ----------
    problem
        The signal-plus-backgrounds problem, whose exact component densities are
        evaluated at the sample.
    labels
        Integer bin label per training row.
    n_bins
        Number of bins, including empty ones.

    Returns
    -------
    numpy.ndarray
        Matrix with shape ``[n_bins, n_components]``. Empty bins are dropped by
        `profile_scan`, which cannot take the logarithm of a zero expectation.
    """
    components = problem.evaluate_components(problem.train.observations)
    matrix = np.zeros((n_bins, components.shape[1]))
    np.add.at(matrix, np.asarray(labels), components)
    return matrix


def profile_scan(
    matrix: np.ndarray,
    coefficients: np.ndarray,
    values: np.ndarray,
    *,
    iterations: int = EM_ITERATIONS,
) -> np.ndarray:
    """Profile the background coefficients out at every scanned signal fraction.

    The data are the expected bin contents at the reference coefficients, so the
    fit is an Asimov one: it reports the interval the binning implies
    asymptotically rather than the outcome of one simulated experiment. The
    likelihood is the extended Poisson likelihood
    ``sum_b [n_b log nu_b - nu_b]`` with ``nu_b`` linear in the coefficients,
    which is concave, and the background coefficients are maximized out by the
    standard multiplicative expectation-maximization iteration for that model.

    Parameters
    ----------
    matrix
        Component yields per bin with shape ``[B, K]``, from
        `component_bin_matrix`.
    coefficients
        Reference coefficients with shape ``[K]``; entry 0 is the signal
        fraction.
    values
        Signal-fraction values to scan, with shape ``[G]``.
    iterations
        Expectation-maximization steps per scanned value.

    Returns
    -------
    numpy.ndarray
        ``-2 log`` likelihood ratio against the reference point, with shape
        ``[G]``. It is zero at the reference coefficients by construction.
    """
    occupied = matrix.sum(axis=1) > 0
    rows = matrix[occupied]
    counts = rows @ coefficients
    efficiency = rows.sum(axis=0)
    scanned = np.repeat(np.asarray(coefficients, dtype=float)[None, :], values.shape[0], axis=0)
    scanned[:, 0] = values
    for _ in range(iterations):
        expected = scanned @ rows.T
        update = (counts[None, :] / expected) @ rows
        scanned[:, 1:] *= update[:, 1:] / efficiency[None, 1:]
    expected = scanned @ rows.T
    profiled = np.sum(counts[None, :] * np.log(expected) - expected, axis=1)
    best = float(np.sum(counts * np.log(counts) - counts))
    return 2.0 * (best - profiled)


def scan_interval(
    values: np.ndarray, deviance: np.ndarray, reference: float
) -> tuple[float, float]:
    """Return the one-unit-deviance interval of a profile-likelihood scan.

    Parameters
    ----------
    values
        Scanned signal-fraction values, increasing.
    deviance
        ``-2 log`` likelihood ratio at those values.
    reference
        Signal fraction at which the deviance vanishes.

    Returns
    -------
    tuple of float
        Lower and upper crossing of one unit of deviance, interpolated
        linearly between scan points.
    """
    lower_side = values <= reference
    upper_side = values >= reference
    lower = float(
        np.interp(1.0, deviance[lower_side][::-1], values[lower_side][::-1])  # type: ignore[arg-type]
    )
    upper = float(np.interp(1.0, deviance[upper_side], values[upper_side]))  # type: ignore[arg-type]
    return lower, upper


@dataclass(frozen=True, slots=True)
class IntervalRow:
    """The binned confidence interval one labeling implies for the fraction.

    Attributes
    ----------
    key, label
        Identity of the labeling.
    lower, upper, half_width
        The one-unit-deviance interval and half its width.
    fisher_half_width
        The reciprocal square root of the binned profiled information, which the
        scan must reproduce.
    """

    key: str
    label: str
    lower: float
    upper: float
    half_width: float
    fisher_half_width: float


@dataclass(frozen=True, slots=True)
class IntervalStudy:
    """The scan curves and their intervals for the two headline labelings."""

    rows: list[IntervalRow]
    values: np.ndarray = field(repr=False)
    curves: dict[str, np.ndarray] = field(repr=False)


def interval_study(
    problem: SignalBackgroundProblem,
    labelings: dict[str, tuple[str, np.ndarray]],
    *,
    n_bins: int,
) -> IntervalStudy:
    """Fit the signal fraction from binned counts under each labeling.

    Parameters
    ----------
    problem
        The signal-plus-backgrounds problem.
    labelings
        Mapping from key to ``(published label, labels)``.
    n_bins
        Bin budget shared by every labeling.

    Returns
    -------
    IntervalStudy
        One interval row per labeling plus the scan curves behind them.
    """
    train = problem.train
    reference = float(problem.coefficients[0])
    first_key = next(iter(labelings))
    sigma = 1.0 / np.sqrt(
        score_labeling(
            train.scores,
            labelings[first_key][1],
            train.weights,
            interest=problem.interest,
            n_bins=n_bins,
        ).profiled_information
    )
    values = np.linspace(
        reference - SCAN_WIDTH_IN_SIGMA * sigma,
        reference + SCAN_WIDTH_IN_SIGMA * sigma,
        SCAN_POINTS,
    )
    rows: list[IntervalRow] = []
    curves: dict[str, np.ndarray] = {}
    for key, (label, labels) in labelings.items():
        matrix = component_bin_matrix(problem, labels, n_bins=n_bins)
        deviance = profile_scan(matrix, np.asarray(problem.coefficients, dtype=float), values)
        lower, upper = scan_interval(values, deviance, reference)
        information = score_labeling(
            train.scores,
            labels,
            train.weights,
            interest=problem.interest,
            n_bins=n_bins,
        ).profiled_information
        rows.append(
            IntervalRow(
                key=key,
                label=label,
                lower=lower,
                upper=upper,
                half_width=0.5 * (upper - lower),
                fisher_half_width=float(1.0 / np.sqrt(information)),
            )
        )
        curves[key] = deviance
    return IntervalStudy(rows=rows, values=values, curves=curves)


@dataclass(frozen=True, slots=True)
class Study:
    """Everything the page and the figure need from one deterministic run."""

    metrics: dict[str, object]
    observations: np.ndarray = field(repr=False)
    efficient: np.ndarray = field(repr=False)
    partitions: FinitePartitions = field(repr=False)
    intervals: IntervalStudy = field(repr=False)


def run_study(
    *,
    n_bins: int = HEADLINE_BINS,
    sizes: tuple[int, int, int] | None = None,
    soft_steps: int | None = None,
    budgets: tuple[int, ...] = BUDGET_SWEEP,
) -> Study:
    """Run the whole profiled-D_s study and return its metrics and arrays.

    Parameters
    ----------
    n_bins
        Bin budget of the headline comparison.
    sizes
        Train, validation, and test split sizes.
    soft_steps
        Adam step budget of the soft profiled fit.
    budgets
        Bin budgets swept against the certified ceiling.

    Returns
    -------
    Study
        The exact structure written to
        ``docs/examples/assets/nuisance-profiled-ds.json``, together with the
        arrays the figure draws.
    """
    soft_steps = example_scale(400, 80) if soft_steps is None else soft_steps
    problem = build_problem(n_bins=n_bins, sizes=sizes)
    train = problem.train

    start = time.perf_counter()
    bound = sq.efficient_score_bound(
        train.scores, interest=problem.interest, weights=train.weights, n_bins=n_bins
    )
    bound_seconds = time.perf_counter() - start

    partitions = finite_partitions(problem, n_bins=n_bins, bound=bound)
    by_key = {row.key: row for row in partitions.rows}
    reference = unbinned_profiled_information(
        train.scores, train.weights, interest=problem.interest
    )
    intervals = interval_study(
        problem,
        {
            "d_partition": ("Plain D", partitions.d_labels),
            "ds_partition_initialized": ("Profiled D_s", partitions.warm_labels),
        },
        n_bins=n_bins,
    )
    rules = reusable_rules(problem, n_bins=n_bins, soft_steps=soft_steps)
    metrics: dict[str, object] = {
        "problem": problem.name,
        "n_bins": n_bins,
        "n_train": int(train.scores.shape[0]),
        "n_test": int(problem.test.scores.shape[0]),
        "interest": list(problem.interest),
        "nuisance": list(problem.nuisance),
        "signal_fraction": float(problem.coefficients[0]),
        "soft_steps": soft_steps,
        "partitions": [asdict(row) for row in partitions.rows],
        "rules": [asdict(row) for row in rules],
        "agreement": {
            "adjusted_rand_index": partition_agreement(
                partitions.d_labels, partitions.warm_labels, n_bins
            ),
            "d_interval_runs": interval_runs(train.observations, partitions.d_labels),
            "ds_interval_runs": interval_runs(train.observations, partitions.warm_labels),
        },
        "bound": {
            "upper_bound": float(bound.upper_bound),
            "ceiling_retention": float(np.exp(bound.upper_bound - np.log(reference))),
            "seconds": bound_seconds,
            "seeded_gap": float(bound.upper_bound - by_key["ds_partition_seeded"].objective),
            "initialized_gap": float(
                bound.upper_bound - by_key["ds_partition_initialized"].objective
            ),
            "seeded_scans": by_key["ds_partition_seeded"].scans,
            "initialized_scans": by_key["ds_partition_initialized"].scans,
            "seeded_moves": by_key["ds_partition_seeded"].accepted_moves,
            "initialized_moves": by_key["ds_partition_initialized"].accepted_moves,
            "seeded_seconds": by_key["ds_partition_seeded"].seconds,
            "initialized_seconds": by_key["ds_partition_initialized"].seconds,
        },
        "ceiling_sweep": ceiling_sweep(problem, budgets),
        "intervals": {
            "unbinned_half_width": float(1.0 / np.sqrt(reference)),
            "rows": [asdict(row) for row in intervals.rows],
        },
    }
    return Study(
        metrics=metrics,
        observations=np.asarray(train.observations)[:, 0],
        efficient=np.asarray(
            sq.efficient_scores(train.scores, interest=problem.interest, weights=train.weights)
        )[:, 0],
        partitions=partitions,
        intervals=intervals,
    )


def _rows(metrics: dict[str, object], key: str) -> list[MetricRow]:
    value = metrics[key]
    if not isinstance(value, list):
        raise TypeError(f"metrics[{key!r}] must be a list of rows")
    return [row for row in value if isinstance(row, dict)]


def _mapping(metrics: dict[str, object], key: str) -> dict[str, object]:
    value = metrics[key]
    if not isinstance(value, dict):
        raise TypeError(f"metrics[{key!r}] must be a mapping")
    return value


def _number(row: MetricRow, key: str) -> float:
    value = row[key]
    if not isinstance(value, (int, float)):
        raise TypeError(f"row[{key!r}] must be numeric")
    return float(value)


def _label_bands(
    axis: Axes, x: np.ndarray, labels: np.ndarray, row: float, colors: list[str]
) -> None:
    """Draw one labeling as a colored strip along the observation axis."""
    order = np.argsort(x, kind="stable")
    sorted_x, sorted_labels = x[order], labels[order]
    edges = np.flatnonzero(np.diff(sorted_labels) != 0)
    starts = np.concatenate([[0], edges + 1])
    stops = np.concatenate([edges + 1, [len(sorted_x)]])
    for start, stop in zip(starts, stops, strict=True):
        left = float(sorted_x[start])
        right = float(sorted_x[stop - 1])
        axis.broken_barh(
            [(left, max(right - left, 1e-3))],
            (row - 0.4, 0.8),
            facecolors=colors[int(sorted_labels[start]) % len(colors)],
        )


def make_figure(study: Study) -> Figure:
    """Render the four-panel profiled-D_s dashboard.

    Parameters
    ----------
    study
        The object returned by `run_study`.

    Returns
    -------
    matplotlib.figure.Figure
        The two partitions in observation space, the efficient score behind
        them, the ceiling sweep, and the downstream profile-likelihood scan.
    """
    metrics = study.metrics
    figure, axes = plt.subplots(2, 2, figsize=(13.5, 9.0), constrained_layout=True)
    colors = [
        "#38618c",
        "#c0563c",
        "#4f9d69",
        "#b8860b",
        "#7b5ea7",
        "#3c8f9c",
        "#a8577e",
        "#666666",
    ]

    x = study.observations
    axes[0, 0].set(
        xlim=(0.0, 1.0),
        ylim=(-0.8, 1.8),
        yticks=[0.0, 1.0],
        yticklabels=["plain D", "profiled $D_s$"],
        xlabel="observation $x$",
        title="Two criteria, two partitions of the same sample",
    )
    _label_bands(axes[0, 0], x, study.partitions.d_labels, 0.0, colors)
    _label_bands(axes[0, 0], x, study.partitions.warm_labels, 1.0, colors)

    order = np.argsort(x, kind="stable")
    twin = axes[0, 1]
    twin.plot(x[order], study.efficient[order], color="#38618c", linewidth=1.2)
    twin.axhline(0.0, color="#999999", linewidth=0.8, linestyle=":")
    twin.set(
        xlabel="observation $x$",
        ylabel="efficient score $\\hat s(x)$",
        title="The efficient score the ceiling is built from",
    )

    sweep = _rows(metrics, "ceiling_sweep")
    budgets = [_number(row, "n_bins") for row in sweep]
    axes[1, 0].plot(
        budgets,
        [_number(row, "ceiling_retention") for row in sweep],
        marker="^",
        linestyle="--",
        color="#666666",
        label="certified ceiling",
    )
    axes[1, 0].plot(
        budgets,
        [_number(row, "ds_initialized_retention") for row in sweep],
        marker="o",
        color="#38618c",
        label="profiled $D_s$ partition",
    )
    axes[1, 0].plot(
        budgets,
        [_number(row, "d_profiled_retention") for row in sweep],
        marker="s",
        color="#c0563c",
        label="plain D partition",
    )
    axes[1, 0].set(
        xlabel="bin budget",
        ylabel="retained information about the fraction",
        xticks=budgets,
        title="Profiled retention against the certified ceiling",
    )
    axes[1, 0].legend()

    reference = float(_mapping(metrics, "intervals")["unbinned_half_width"])  # type: ignore[arg-type]
    interval_rows = {row.key: row for row in study.intervals.rows}
    for key, color, marker in (
        ("d_partition", "#c0563c", "s"),
        ("ds_partition_initialized", "#38618c", "o"),
    ):
        row = interval_rows[key]
        axes[1, 1].plot(
            study.intervals.values,
            study.intervals.curves[key],
            color=color,
            marker=marker,
            markevery=12,
            label=f"{row.label.replace('D_s', '$D_s$')} bins, $\\pm${row.half_width:.5f}",
        )
    axes[1, 1].axhline(1.0, color="#999999", linewidth=0.8, linestyle=":")
    axes[1, 1].set(
        ylim=(0.0, 4.0),
        xlabel="signal fraction",
        ylabel="$-2\\,\\log$ likelihood ratio",
        title=f"Binned fit of the fraction (unbinned $\\pm${reference:.5f})",
    )
    axes[1, 1].legend()

    figure.suptitle("Signal fraction with a background-shape nuisance")
    return figure


def main() -> None:
    """Run the study, then write the committed JSON and figure."""
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
