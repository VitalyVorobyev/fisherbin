"""The soft Voronoi relaxation: annealing, the hardening gap, and purification.

This script is the single deterministic generator behind the
`docs/examples/soft-purification.md` page. It runs

* one annealed fit whose full recorded history is re-scored, so the soft
  objective and the hard rule it implies can be plotted against the same
  temperature schedule;
* a hardening-gap ladder over several problems and several final temperatures,
  measuring what the last hardening step actually costs;
* a purification probe that compares a genuinely randomized (fractional) rule
  with the deterministic rule obtained by hardening it at the same centers;
* the same problems fitted by exact D exchange, and by exact D exchange started
  from the soft fit's own labels;

and writes `docs/examples/assets/soft-purification.json` plus
`docs/examples/assets/soft-purification.png`.

Run it with::

    JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run python -m examples.soft_purification
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

import scorequant as sq
from examples._env import example_scale
from examples.synthetic_problems import (
    gaussian_location,
    signal_background_shape,
    spectral_templates,
    two_parameter_gaussian_mixture,
)

FIGURE_PATH = Path("docs/examples/assets/soft-purification.png")
METRICS_PATH = Path("docs/examples/assets/soft-purification.json")

#: Seed shared by every solver in the study.
SOLVER_SEED = 3
#: Final temperatures, as a fraction of the schedule's starting temperature.
TEMPERATURE_RATIOS = (0.8, 0.4, 0.2, 0.05, 0.01)
#: Softmax temperatures of the purification probe, as a fraction of the median
#: nearest-center separation -- the same unit the library builds its own
#: schedule in.
PROBE_TEMPERATURES = (1.0, 0.5, 0.25, 0.1, 0.05)
#: Problem the annealing panel follows step by step.
SCHEDULE_PROBLEM = "signal_background_shape"

type MetricRow = dict[str, object]


@dataclass(frozen=True, slots=True)
class LadderProblem:
    """One weighted score table in the ladder, with its bin budget.

    Attributes
    ----------
    key, title
        Stable identifier and published name.
    scores, weights
        The training score table and its reference measure.
    n_bins
        Bin budget every solver in the study uses on this problem.
    """

    key: str
    title: str
    scores: np.ndarray = field(repr=False)
    weights: np.ndarray = field(repr=False)
    n_bins: int


def build_ladder(*, sizes: tuple[int, int, int] | None = None) -> list[LadderProblem]:
    """Return the problem ladder every measurement in this study runs on.

    The ladder spans one, two, and three score columns and both uniform and
    strongly nonuniform reference measures, because a hardening gap measured on
    a single table says nothing about whether the behavior is general.

    Parameters
    ----------
    sizes
        Train, validation, and test split sizes handed to each generator.
        Defaults to the fast-mode aware sizes from
        `examples._env.example_scale`.

    Returns
    -------
    list of LadderProblem
        Four problems, in publication order.
    """
    resolved = example_scale((4_000, 2_000, 15_000), (800, 400, 2_000)) if sizes is None else sizes
    builders: list[tuple[str, str, Callable[[], object], int]] = [
        ("gaussian_location", "Gaussian location", lambda: gaussian_location(sizes=resolved), 4),
        (
            "spectral_templates",
            "Overlapping spectral templates",
            lambda: spectral_templates(sizes=resolved),
            8,
        ),
        (
            "two_parameter_gaussian_mixture",
            "Two-parameter Gaussian mixture",
            lambda: two_parameter_gaussian_mixture(sizes=resolved),
            8,
        ),
        (
            SCHEDULE_PROBLEM,
            "Signal fraction with background shapes",
            lambda: signal_background_shape(sizes=resolved),
            6,
        ),
    ]
    ladder: list[LadderProblem] = []
    for key, title, builder, n_bins in builders:
        problem = builder()
        train = problem.train  # type: ignore[attr-defined]
        ladder.append(
            LadderProblem(
                key=key,
                title=title,
                scores=np.asarray(train.scores),
                weights=np.asarray(train.weights),
                n_bins=n_bins,
            )
        )
    return ladder


def fractional_retention(
    scores: np.ndarray, responsibilities: np.ndarray, weights: np.ndarray
) -> float:
    """Return the D-efficiency of a randomized rule.

    `scorequant.fractional_fisher_information` returns the Fisher information of
    a randomized quantizer exactly, on the same footing as
    `scorequant.binned_fisher_information` for a hard one. Turning that matrix
    into the same D-efficiency number `scorequant.information_report` publishes
    is one line of algebra when the unbinned information is nonsingular: the
    whitening that normalizes the retained matrix contributes
    ``det(I_full)^-1``, so the geometric mean of the retained eigenvalues is
    ``(det I_soft / det I_full) ** (1 / P)``. Applying this function to a
    one-hot responsibility matrix reproduces
    ``information_report(...).geometric_mean_retention`` exactly, which is the
    check the documentation page runs before trusting any soft number.

    Parameters
    ----------
    scores
        Score matrix with shape ``[N, P]``.
    responsibilities
        Nonnegative rows summing to one, with shape ``[N, B]``.
    weights
        Nonnegative measure weights with shape ``[N]``.

    Returns
    -------
    float
        Geometric-mean retention of the randomized rule, or ``0.0`` when the
        randomized information is singular.

    Raises
    ------
    ValueError
        If the unbinned Fisher information is numerically singular, in which
        case a determinant ratio is not a retention at all.
    """
    soft = np.asarray(sq.fractional_fisher_information(scores, responsibilities, weights))
    full = np.asarray(sq.fisher_information(scores, weights))
    full_sign, full_logdet = np.linalg.slogdet(full)
    if full_sign <= 0:
        raise ValueError("fractional retention requires nonsingular unbinned information")
    soft_sign, soft_logdet = np.linalg.slogdet(soft)
    if soft_sign <= 0:
        return 0.0
    return float(np.exp((soft_logdet - full_logdet) / full.shape[0]))


def hard_retention(
    scores: np.ndarray, labels: np.ndarray, weights: np.ndarray, n_bins: int
) -> float:
    """Return the D-efficiency of a hard labeling.

    Parameters
    ----------
    scores
        Score matrix with shape ``[N, P]``.
    labels
        Integer bin label per row.
    weights
        Nonnegative measure weights.
    n_bins
        Number of bins, including empty ones.

    Returns
    -------
    float
        `scorequant.information_report`'s geometric-mean retention.
    """
    report = sq.information_report(scores, labels, weights, n_bins=n_bins)
    return float(report.geometric_mean_retention)


def center_separation(centers: np.ndarray) -> float:
    """Return the median nearest-center distance of a fitted rule.

    This is the unit the library builds its own annealing schedule in: the
    starting temperature of `scorequant.SoftVoronoiConfig` is exactly this
    quantity, so expressing probe temperatures as multiples of it keeps them
    comparable across problems of very different information scale.

    Parameters
    ----------
    centers
        Fitted centers in the whitened coordinate system, with shape
        ``[B, R]``.

    Returns
    -------
    float
        Median over cells of the distance to the nearest other cell.
    """
    array = np.asarray(centers)
    distances = np.sqrt(np.sum((array[:, None, :] - array[None, :, :]) ** 2, axis=2))
    np.fill_diagonal(distances, np.inf)
    return float(np.median(np.min(distances, axis=1)))


def softmax_responsibilities(
    coordinates: np.ndarray, centers: np.ndarray, temperature: float
) -> np.ndarray:
    """Build the randomized rule the soft relaxation optimizes.

    The responsibilities are ``softmax_b(-||s - c_b||^2 / (2 tau^2))`` in the
    whitened coordinates the quantizer was fitted in, which is the family
    `scorequant.SoftVoronoiConfig` parameterizes. As the temperature falls the
    rows approach one-hot vectors, and their argmax is exactly what
    `QuantizerResult.predict_scores` returns.

    Parameters
    ----------
    coordinates
        Whitened score coordinates with shape ``[N, R]``, from
        ``QuantizerResult.transform.apply``.
    centers
        Fitted centers with shape ``[B, R]``.
    temperature
        Positive softmax temperature.

    Returns
    -------
    numpy.ndarray
        Responsibility matrix with shape ``[N, B]`` whose rows sum to one.
    """
    squared = np.sum((coordinates[:, None, :] - centers[None, :, :]) ** 2, axis=2)
    logits = -squared / (2.0 * temperature**2)
    stabilized = np.exp(logits - logits.max(axis=1, keepdims=True))
    return stabilized / stabilized.sum(axis=1, keepdims=True)


@dataclass(frozen=True, slots=True)
class ScheduleTrace:
    """One annealed fit's recorded history, re-scored at every snapshot."""

    steps: np.ndarray = field(repr=False)
    temperatures: np.ndarray = field(repr=False)
    soft_retention: np.ndarray = field(repr=False)
    hard_retention: np.ndarray = field(repr=False)
    problem: str = ""
    n_bins: int = 0
    hardening_gap: float = 0.0


def schedule_trace(problem: LadderProblem, *, max_steps: int, record_every: int) -> ScheduleTrace:
    """Fit one problem with the full diagnostic history recorded.

    ``diagnostics="full"`` re-scores every recorded center snapshot with a
    complete information report, which is the only way to see what the hard rule
    was doing while the soft objective climbed. It costs one full pass per
    snapshot, which is why it is not the default.

    Parameters
    ----------
    problem
        The ladder entry to fit.
    max_steps
        Adam step budget.
    record_every
        Steps between recorded snapshots.

    Returns
    -------
    ScheduleTrace
        Steps, temperatures, soft retention, and hard retention, all aligned.
    """
    rule = sq.fit_quantizer(
        sq.ScoreSample(problem.scores, problem.weights),
        n_bins=problem.n_bins,
        criterion=sq.DOptimality(),
        config=sq.SoftVoronoiConfig(
            seed=SOLVER_SEED,
            initializer_restarts=4,
            max_steps=max_steps,
            record_every=record_every,
            temperature_end_ratio=0.02,
        ),
        diagnostics="full",
    )
    trace = rule.trace
    if trace.soft_retention is None or trace.temperatures is None:
        raise ValueError("a soft Voronoi fit must record its schedule")
    return ScheduleTrace(
        steps=np.asarray(trace.steps),
        temperatures=np.asarray(trace.temperatures),
        soft_retention=np.asarray(trace.soft_retention),
        hard_retention=np.asarray(trace.train_hard_retention),
        problem=problem.key,
        n_bins=problem.n_bins,
        hardening_gap=float(rule.hardening_gap or 0.0),
    )


@dataclass(frozen=True, slots=True)
class HardeningRow:
    """One (problem, final temperature) entry of the hardening-gap ladder.

    Attributes
    ----------
    problem, n_bins, temperature_ratio
        Which fit this row describes.
    soft_retention
        Retention of the randomized rule at the last recorded step.
    hard_retention
        Retention of the deterministic rule those same centers imply.
    hardening_gap
        ``soft_retention - hard_retention``, as `QuantizerResult` reports it. A
        negative value means hardening *gained* information.
    """

    problem: str
    n_bins: int
    temperature_ratio: float
    soft_retention: float
    hard_retention: float
    hardening_gap: float


def hardening_ladder(
    ladder: list[LadderProblem],
    *,
    ratios: tuple[float, ...] = TEMPERATURE_RATIOS,
    max_steps: int,
) -> list[HardeningRow]:
    """Measure the hardening gap across problems and final temperatures.

    Parameters
    ----------
    ladder
        Problems to fit.
    ratios
        Final temperatures, as a fraction of the starting temperature.
    max_steps
        Adam step budget of every fit.

    Returns
    -------
    list of HardeningRow
        One row per (problem, ratio) pair.
    """
    rows: list[HardeningRow] = []
    for problem in ladder:
        source = sq.ScoreSample(problem.scores, problem.weights)
        for ratio in ratios:
            rule = sq.fit_quantizer(
                source,
                n_bins=problem.n_bins,
                criterion=sq.DOptimality(),
                config=sq.SoftVoronoiConfig(
                    seed=SOLVER_SEED,
                    initializer_restarts=4,
                    max_steps=max_steps,
                    record_every=max_steps,
                    temperature_end_ratio=ratio,
                ),
            )
            soft = float(np.asarray(rule.trace.soft_retention)[-1])
            hard = float(rule.train_report.geometric_mean_retention)
            rows.append(
                HardeningRow(
                    problem=problem.key,
                    n_bins=problem.n_bins,
                    temperature_ratio=float(ratio),
                    soft_retention=soft,
                    hard_retention=hard,
                    hardening_gap=float(rule.hardening_gap or 0.0),
                )
            )
    return rows


@dataclass(frozen=True, slots=True)
class PurificationRow:
    """One randomized rule and the deterministic rule that purifies it.

    Attributes
    ----------
    problem, n_bins, temperature_ratio
        Which randomized rule this row describes; the temperature is a multiple
        of the median nearest-center separation.
    randomized_retention
        D-efficiency of the randomized rule, from
        `scorequant.fractional_fisher_information`.
    purified_retention
        D-efficiency of the deterministic rule obtained by taking each row's
        most probable cell.
    purification_gain
        ``purified_retention - randomized_retention``.
    """

    problem: str
    n_bins: int
    temperature_ratio: float
    randomized_retention: float
    purified_retention: float
    purification_gain: float


def purification_probe(
    ladder: list[LadderProblem],
    *,
    temperatures: tuple[float, ...] = PROBE_TEMPERATURES,
    max_steps: int,
) -> list[PurificationRow]:
    """Compare randomized rules with the deterministic rules that harden them.

    Each problem is fitted once; the fitted centers are then used to build a
    family of genuinely randomized rules at several temperatures. For each one
    the randomized information and the information of its own argmax rule are
    both measured with public functions, so the comparison never leans on
    anything the optimizer reports about itself.

    Parameters
    ----------
    ladder
        Problems to probe.
    temperatures
        Softmax temperatures, as multiples of the median nearest-center
        separation.
    max_steps
        Adam step budget of the fit that supplies the centers.

    Returns
    -------
    list of PurificationRow
        One row per (problem, temperature) pair.
    """
    rows: list[PurificationRow] = []
    for problem in ladder:
        rule = sq.fit_quantizer(
            sq.ScoreSample(problem.scores, problem.weights),
            n_bins=problem.n_bins,
            criterion=sq.DOptimality(),
            config=sq.SoftVoronoiConfig(
                seed=SOLVER_SEED,
                initializer_restarts=4,
                max_steps=max_steps,
                record_every=max_steps,
            ),
        )
        coordinates = np.asarray(rule.transform.apply(problem.scores))
        centers = np.asarray(rule.centers)
        separation = center_separation(centers)
        for ratio in temperatures:
            responsibilities = softmax_responsibilities(coordinates, centers, ratio * separation)
            randomized = fractional_retention(problem.scores, responsibilities, problem.weights)
            purified = hard_retention(
                problem.scores,
                np.argmax(responsibilities, axis=1),
                problem.weights,
                problem.n_bins,
            )
            rows.append(
                PurificationRow(
                    problem=problem.key,
                    n_bins=problem.n_bins,
                    temperature_ratio=float(ratio),
                    randomized_retention=randomized,
                    purified_retention=purified,
                    purification_gain=purified - randomized,
                )
            )
    return rows


@dataclass(frozen=True, slots=True)
class SolverRow:
    """One problem solved three ways, for the soft-against-exchange comparison.

    Attributes
    ----------
    problem, n_bins
        Which problem this row describes.
    soft_retention
        D-efficiency of the hardened soft fit.
    exchange_retention
        D-efficiency of the exact positive-gain exchange partition from generic
        seeding.
    exchange_from_soft_retention
        D-efficiency of the same exchange started from the soft fit's labels.
    exchange_scans, exchange_from_soft_scans
        Scan counters of the two exchange runs.
    """

    problem: str
    n_bins: int
    soft_retention: float
    exchange_retention: float
    exchange_from_soft_retention: float
    exchange_scans: int
    exchange_from_soft_scans: int


def soft_versus_exchange(ladder: list[LadderProblem], *, max_steps: int) -> list[SolverRow]:
    """Compare the soft path with exact exchange, and with exchange seeded by it.

    Parameters
    ----------
    ladder
        Problems to compare on.
    max_steps
        Adam step budget of the soft fit.

    Returns
    -------
    list of SolverRow
        One row per problem.
    """
    rows: list[SolverRow] = []
    for problem in ladder:
        rule = sq.fit_quantizer(
            sq.ScoreSample(problem.scores, problem.weights),
            n_bins=problem.n_bins,
            criterion=sq.DOptimality(),
            config=sq.SoftVoronoiConfig(
                seed=SOLVER_SEED,
                initializer_restarts=4,
                max_steps=max_steps,
                record_every=max_steps,
            ),
        )
        soft_labels = np.asarray(rule.predict_scores(problem.scores))
        exchange = sq.optimize_partition(
            problem.scores,
            weights=problem.weights,
            n_bins=problem.n_bins,
            config=sq.DExchangeConfig(seed=SOLVER_SEED),
        )
        from_soft = sq.optimize_partition(
            problem.scores,
            weights=problem.weights,
            n_bins=problem.n_bins,
            config=sq.DExchangeConfig(seed=SOLVER_SEED),
            initial_labels=soft_labels,
        )
        rows.append(
            SolverRow(
                problem=problem.key,
                n_bins=problem.n_bins,
                soft_retention=float(rule.train_report.geometric_mean_retention),
                exchange_retention=float(exchange.train_report.geometric_mean_retention),
                exchange_from_soft_retention=float(from_soft.train_report.geometric_mean_retention),
                exchange_scans=int(exchange.scans),
                exchange_from_soft_scans=int(from_soft.scans),
            )
        )
    return rows


@dataclass(frozen=True, slots=True)
class Study:
    """Everything the page and the figure need from one deterministic run."""

    metrics: dict[str, object]
    trace: ScheduleTrace = field(repr=False)


def run_study(
    *,
    sizes: tuple[int, int, int] | None = None,
    max_steps: int | None = None,
    schedule_steps: int | None = None,
) -> Study:
    """Run the whole soft-relaxation study and return its metrics.

    Parameters
    ----------
    sizes
        Train, validation, and test split sizes handed to every generator.
    max_steps
        Adam step budget of the ladder fits.
    schedule_steps
        Adam step budget of the single fully traced fit.

    Returns
    -------
    Study
        The exact structure written to
        ``docs/examples/assets/soft-purification.json``, plus the traced fit.
    """
    max_steps = example_scale(200, 60) if max_steps is None else max_steps
    schedule_steps = example_scale(300, 90) if schedule_steps is None else schedule_steps
    ladder = build_ladder(sizes=sizes)
    traced = next(problem for problem in ladder if problem.key == SCHEDULE_PROBLEM)
    trace = schedule_trace(
        traced, max_steps=schedule_steps, record_every=max(schedule_steps // 30, 1)
    )
    metrics: dict[str, object] = {
        "problems": [
            {"key": problem.key, "title": problem.title, "n_bins": problem.n_bins}
            for problem in ladder
        ],
        "n_train": int(ladder[0].scores.shape[0]),
        "max_steps": max_steps,
        "schedule_steps": schedule_steps,
        "schedule": {
            "problem": trace.problem,
            "n_bins": trace.n_bins,
            "hardening_gap": trace.hardening_gap,
            "first_hard_retention": float(trace.hard_retention[0]),
            "final_hard_retention": float(trace.hard_retention[-1]),
            "first_soft_retention": float(trace.soft_retention[0]),
            "final_soft_retention": float(trace.soft_retention[-1]),
            "temperature_ratio": float(trace.temperatures[-1] / trace.temperatures[0]),
        },
        "hardening": [asdict(row) for row in hardening_ladder(ladder, max_steps=max_steps)],
        "purification": [asdict(row) for row in purification_probe(ladder, max_steps=max_steps)],
        "solvers": [asdict(row) for row in soft_versus_exchange(ladder, max_steps=max_steps)],
    }
    return Study(metrics=metrics, trace=trace)


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


PALETTE = ("#38618c", "#c0563c", "#4f9d69", "#b8860b")


def make_figure(study: Study) -> Figure:
    """Render the four-panel soft-relaxation dashboard.

    Parameters
    ----------
    study
        The object returned by `run_study`.

    Returns
    -------
    matplotlib.figure.Figure
        The annealing schedule, the hardening-gap ladder, the purification
        probe, and the soft-against-exchange comparison.
    """
    metrics = study.metrics
    figure, axes = plt.subplots(2, 2, figsize=(13.5, 9.0), constrained_layout=True)
    titles = {_text(row, "key"): _text(row, "title") for row in _rows(metrics, "problems")}

    trace = study.trace
    axes[0, 0].plot(
        trace.temperatures,
        trace.soft_retention,
        color="#38618c",
        marker="o",
        markersize=3,
        label="randomized rule being optimized",
    )
    axes[0, 0].plot(
        trace.temperatures,
        trace.hard_retention,
        color="#c0563c",
        marker="s",
        markersize=3,
        label="hard rule the same centers imply",
    )
    axes[0, 0].set(
        xscale="log",
        xlabel="temperature (annealed from left to right)",
        ylabel="D-efficiency",
        title=f"Annealing on {titles[trace.problem].lower()}",
    )
    axes[0, 0].invert_xaxis()
    axes[0, 0].legend(loc="lower right")

    hardening = _rows(metrics, "hardening")
    for index, key in enumerate(titles):
        rows = [row for row in hardening if _text(row, "problem") == key]
        axes[0, 1].plot(
            [_number(row, "temperature_ratio") for row in rows],
            [abs(_number(row, "hardening_gap")) for row in rows],
            marker="o",
            color=PALETTE[index % len(PALETTE)],
            label=titles[key],
        )
    axes[0, 1].set(
        xscale="log",
        yscale="log",
        xlabel="final temperature / starting temperature",
        ylabel="absolute hardening gap",
        title="What the last hardening step costs",
    )
    axes[0, 1].legend(fontsize=8)

    purification = _rows(metrics, "purification")
    for index, key in enumerate(titles):
        rows = [row for row in purification if _text(row, "problem") == key]
        axes[1, 0].plot(
            [_number(row, "temperature_ratio") for row in rows],
            [_number(row, "purification_gain") for row in rows],
            marker="o",
            color=PALETTE[index % len(PALETTE)],
            label=titles[key],
        )
    axes[1, 0].axhline(0.0, color="#999999", linewidth=0.8, linestyle=":")
    axes[1, 0].set(
        xscale="log",
        yscale="log",
        xlabel="softmax temperature / median center separation",
        ylabel="D-efficiency gained by hardening",
        title="Purification never costs information here",
    )
    axes[1, 0].legend(fontsize=8)

    solvers = _rows(metrics, "solvers")
    positions = np.arange(len(solvers))
    width = 0.34
    for offset, key, color, label in (
        (-width / 2, "soft_retention", "#38618c", "soft fit, hardened"),
        (width / 2, "exchange_from_soft_retention", "#4f9d69", "exchange from soft labels"),
    ):
        deficits = [
            1e6 * (_number(row, "exchange_retention") - _number(row, key)) for row in solvers
        ]
        bars = axes[1, 1].barh(positions + offset, deficits, height=width, color=color, label=label)
        axes[1, 1].bar_label(bars, labels=[f"{value:.1f}" for value in deficits], padding=3)
    axes[1, 1].axvline(0.0, color="#c0563c", linewidth=1.4)
    axes[1, 1].set(
        yticks=positions,
        yticklabels=[titles[_text(row, "problem")] for row in solvers],
        xlabel="D-efficiency below exact D exchange, in parts per million",
        title="The soft path against exact exchange",
    )
    axes[1, 1].invert_yaxis()
    axes[1, 1].legend(fontsize=8, loc="lower right")

    figure.suptitle("Soft rules: annealing, hardening, and purification")
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
