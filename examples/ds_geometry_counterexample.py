"""An exactly optimal profiled partition that violates its own geometry.

This script is the single deterministic generator behind the
`docs/examples/ds-geometry-counterexample.md` page. Everything it computes about
the eight-row fixture is done in exact rational arithmetic with
`fractions.Fraction`, so no sign below depends on a floating-point tolerance:

* it enumerates all 966 three-cell labelings of the eight-row table once each,
  and ranks them by the exact profiled objective with column 0 of interest;
* it builds, for every labeling, the rank-one efficient semimetric that the
  labeling itself induces, and records whether every row sits in a nearest cell
  under it;
* it does the same enumeration for the plain determinant, where the global
  optimum is self-consistent exactly as the D theorem requires;
* it reproduces the profiled optimum through `scorequant.optimize_partition`
  and records the refusal of `compile_quantizer`;

and writes `docs/examples/assets/ds-geometry-counterexample.json` plus
`docs/examples/assets/ds-geometry-counterexample.png`.

Run it with::

    JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run python -m examples.ds_geometry_counterexample
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from itertools import product
from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

import scorequant as sq

FIGURE_PATH = Path("docs/examples/assets/ds-geometry-counterexample.png")
METRICS_PATH = Path("docs/examples/assets/ds-geometry-counterexample.json")

#: The eight integer score vectors of the fixture, before the exact shift that
#: makes the table sum to zero the way a score sample from a normalized model
#: does. Integers keep every derived quantity a rational with a small
#: denominator, which is what makes the whole demonstration exact.
RAW_TABLE = ((4, -4), (-5, 2), (-1, 0), (-5, -1), (2, -2), (4, 3), (2, 4), (2, -4))
#: Cells of the enumeration.
N_CELLS = 3
#: Score columns of the fixture.
N_COLUMNS = 2
#: Score column of the parameter of interest; the other column is nuisance.
INTEREST = (0,)

type ExactMatrix = list[list[Fraction]]


def exact_table() -> ExactMatrix:
    """Return the eight-row score table in exact rational arithmetic.

    The integers of `RAW_TABLE` are shifted once by their own exact mean, so
    the table sums to zero by construction. That is a property of the fixture,
    not a preprocessing step applied to data: a score sample from a normalized
    model has mean zero under its own reference measure, and building the
    fixture that way is what makes it a plausible score table.

    Returns
    -------
    list of list of fractions.Fraction
        Eight rows of two exact rationals with denominator eight.
    """
    centre = [
        Fraction(sum(row[column] for row in RAW_TABLE), len(RAW_TABLE))
        for column in range(N_COLUMNS)
    ]
    return [
        [Fraction(row[column]) - centre[column] for column in range(N_COLUMNS)] for row in RAW_TABLE
    ]


def canonical_labelings() -> list[tuple[int, ...]]:
    """Return every three-cell labeling of eight rows, once each.

    Bin names carry no meaning, so labelings are enumerated in restricted-growth
    form: the first row is in cell 0 and a new cell may only be opened by the
    smallest unused index. That visits each partition exactly once instead of
    once per relabeling of its cells.

    Returns
    -------
    list of tuple of int
        The 966 labelings, in lexicographic order.
    """
    return [
        labels
        for labels in product(range(N_CELLS), repeat=len(RAW_TABLE))
        if labels[0] == 0
        and set(labels) == set(range(N_CELLS))
        and all(labels[index] <= max(labels[:index]) + 1 for index in range(1, len(RAW_TABLE)))
    ]


def cell_moments(labels: tuple[int, ...], table: ExactMatrix) -> tuple[list[Fraction], ExactMatrix]:
    """Return the exact rational mass and score moment of every cell.

    Parameters
    ----------
    labels
        One labeling of the eight rows.
    table
        The exact score table.

    Returns
    -------
    tuple
        Cell masses and cell score moments, both exact.
    """
    weight = Fraction(1, len(table))
    masses = [Fraction(0)] * N_CELLS
    moments: ExactMatrix = [[Fraction(0)] * N_COLUMNS for _ in range(N_CELLS)]
    for row, cell in enumerate(labels):
        masses[cell] += weight
        for column in range(N_COLUMNS):
            moments[cell][column] += weight * table[row][column]
    return masses, moments


def binned_information(labels: tuple[int, ...], table: ExactMatrix) -> ExactMatrix:
    """Return the exact binned Fisher information of one labeling."""
    masses, moments = cell_moments(labels, table)
    return [
        [
            sum(
                moments[cell][first] * moments[cell][second] / masses[cell]
                for cell in range(N_CELLS)
            )
            for second in range(N_COLUMNS)
        ]
        for first in range(N_COLUMNS)
    ]


def profiled_value(labels: tuple[int, ...], table: ExactMatrix) -> Fraction:
    """Return the exact scalar Schur complement with column 0 of interest.

    Parameters
    ----------
    labels
        One labeling of the eight rows.
    table
        The exact score table.

    Returns
    -------
    fractions.Fraction
        The information about the interest parameter that survives after the
        nuisance column has been estimated from the same labels and profiled
        out. Its logarithm is the profiled objective.
    """
    matrix = binned_information(labels, table)
    return matrix[0][0] - matrix[0][1] * matrix[1][0] / matrix[1][1]


def determinant_value(labels: tuple[int, ...], table: ExactMatrix) -> Fraction:
    """Return the exact determinant of the binned information of one labeling."""
    matrix = binned_information(labels, table)
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def _inverse(matrix: ExactMatrix) -> ExactMatrix | None:
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    if determinant == 0:
        return None
    return [
        [matrix[1][1] / determinant, -matrix[0][1] / determinant],
        [-matrix[1][0] / determinant, matrix[0][0] / determinant],
    ]


def efficient_semimetric(labels: tuple[int, ...], table: ExactMatrix) -> ExactMatrix | None:
    """Return the exact rank-one semimetric a profiled labeling induces.

    The gradient of the profiled objective is the inverse information minus the
    embedded inverse of its nuisance block. It has rank one here, so its level
    sets are bands of constant efficient score.

    Parameters
    ----------
    labels
        One labeling of the eight rows.
    table
        The exact score table.

    Returns
    -------
    list of list of fractions.Fraction or None
        The two-by-two semimetric, exactly, or ``None`` when the labeling's
        binned information is singular and induces no geometry at all.
    """
    matrix = binned_information(labels, table)
    inverse = _inverse(matrix)
    if inverse is None:
        return None
    return [
        [inverse[0][0], inverse[0][1]],
        [inverse[1][0], inverse[1][1] - 1 / matrix[1][1]],
    ]


def mahalanobis_metric(labels: tuple[int, ...], table: ExactMatrix) -> ExactMatrix | None:
    """Return the exact inverse binned information, or ``None`` if it is singular."""
    return _inverse(binned_information(labels, table))


def violation_margins(
    labels: tuple[int, ...], table: ExactMatrix, metric: ExactMatrix
) -> list[Fraction]:
    """Return how much farther each row is from its own cell than from the nearest.

    Parameters
    ----------
    labels
        One labeling of the eight rows.
    table
        The exact score table.
    metric
        The semimetric or metric distances are measured in.

    Returns
    -------
    list of fractions.Fraction
        One nonnegative rational per row. Zero means the row sits in a nearest
        cell; a strictly positive value is an exact violation of the geometry
        the labeling itself induces.
    """
    masses, moments = cell_moments(labels, table)
    means = [
        [moments[cell][column] / masses[cell] for column in range(N_COLUMNS)]
        for cell in range(N_CELLS)
    ]
    margins: list[Fraction] = []
    for row in range(len(table)):
        distances = []
        for cell in range(N_CELLS):
            offset = [table[row][column] - means[cell][column] for column in range(N_COLUMNS)]
            distances.append(
                sum(
                    offset[first] * metric[first][second] * offset[second]
                    for first in range(N_COLUMNS)
                    for second in range(N_COLUMNS)
                )
            )
        margins.append(distances[labels[row]] - min(distances))
    return margins


@dataclass(frozen=True, slots=True)
class Ranking:
    """One exact enumeration of all 966 labelings under one criterion.

    Attributes
    ----------
    criterion
        ``"profiled"`` or ``"determinant"``.
    values
        Exact criterion value of every labeling, ranked best first, as floats.
    consistent_ranks
        Zero-based ranks of the labelings that satisfy their own geometry.
    singular_labelings
        Labelings whose binned information is singular, so they induce no
        geometry to satisfy and are excluded from `consistent_ranks`.
    optimum
        The best labeling.
    optimum_value, runner_up_margin
        Its exact value and its exact margin over the runner-up, as strings so
        the committed metrics stay exactly rational.
    optimum_is_consistent
        Whether the best labeling satisfies its own geometry.
    optimum_margins
        Per-row violation margins of the best labeling, as strings.
    best_consistent_rank, best_consistent_labels
        The best labeling that does satisfy its own geometry, and where it ranks.
    best_consistent_ratio
        Its criterion value divided by the optimum's.
    """

    criterion: str
    values: list[float] = field(repr=False)
    consistent_ranks: list[int] = field(repr=False)
    singular_labelings: int = 0
    optimum: list[int] = field(default_factory=list)
    optimum_value: str = ""
    runner_up_margin: str = ""
    optimum_is_consistent: bool = False
    optimum_margins: list[str] = field(default_factory=list)
    best_consistent_rank: int = -1
    best_consistent_labels: list[int] = field(default_factory=list)
    best_consistent_ratio: float = 0.0


def rank_labelings(criterion: str, table: ExactMatrix) -> Ranking:
    """Enumerate every labeling exactly and measure its own self-consistency.

    Parameters
    ----------
    criterion
        ``"profiled"`` for the Schur complement with column 0 of interest, or
        ``"determinant"`` for the plain determinant.
    table
        The exact score table.

    Returns
    -------
    Ranking
        The ranked values, which labelings are self-consistent, and where the
        best self-consistent one sits.
    """
    if criterion == "profiled":
        value = profiled_value
        geometry = efficient_semimetric
    elif criterion == "determinant":
        value = determinant_value
        geometry = mahalanobis_metric
    else:
        raise ValueError(f"unknown criterion {criterion!r}")

    ranked = sorted(
        ((value(labels, table), labels) for labels in canonical_labelings()), reverse=True
    )
    consistent_ranks: list[int] = []
    singular = 0
    for rank, (_, labels) in enumerate(ranked):
        metric = geometry(labels, table)
        if metric is None:
            singular += 1
            continue
        if max(violation_margins(labels, table, metric)) == 0:
            consistent_ranks.append(rank)

    best_value, optimum = ranked[0]
    best_rank = consistent_ranks[0]
    optimum_metric = geometry(optimum, table)
    if optimum_metric is None:  # pragma: no cover - the optimum is never singular
        raise RuntimeError("the optimal labeling must induce a geometry")
    return Ranking(
        criterion=criterion,
        values=[float(entry) for entry, _ in ranked],
        consistent_ranks=consistent_ranks,
        singular_labelings=singular,
        optimum=list(optimum),
        optimum_value=str(best_value),
        runner_up_margin=str(best_value - ranked[1][0]),
        optimum_is_consistent=best_rank == 0,
        optimum_margins=[
            str(margin) for margin in violation_margins(optimum, table, geometry(optimum, table))
        ],
        best_consistent_rank=best_rank,
        best_consistent_labels=list(ranked[best_rank][1]),
        best_consistent_ratio=float(ranked[best_rank][0] / best_value),
    )


def float_table() -> tuple[np.ndarray, np.ndarray]:
    """Return the same fixture as a float score matrix with equal weights.

    Returns
    -------
    tuple of numpy.ndarray
        The eight-by-two score matrix and the eight equal weights the library
        consumes.
    """
    raw = np.asarray(RAW_TABLE, dtype=float)
    return raw - raw.mean(axis=0), np.full(len(RAW_TABLE), 1.0 / len(RAW_TABLE))


@dataclass(frozen=True, slots=True)
class LibraryRun:
    """What the library reports on the same eight rows.

    Attributes
    ----------
    profiled_labels
        Labels the profiled exchange reaches from a cold start.
    profiled_information
        ``exp`` of the profiled objective, which the exact enumeration gives as
        a rational.
    violating_moves, maximum_positive_violation
        The measured violation of the efficient geometry at that labeling.
    maximum_bound_residual, bound_certified
        The approximate-geometry proposition, measured.
    compile_refusal
        The error message `compile_quantizer` raises on a profiled result.
    d_labels, d_objective
        Labels and whitened objective of the plain determinant partition on the
        same rows.
    d_voronoi_consistent, d_violating_moves
        The determinant geometry report, which the theorem forces to be clean.
    d_compiles
        Whether the compiled rule reproduces its own training labels.
    d_certificate_status, d_incumbent_was_optimal, d_nodes_explored
        What bounded global certification proves about that labeling.
    """

    profiled_labels: list[int]
    profiled_information: float
    violating_moves: int
    maximum_positive_violation: float
    maximum_bound_residual: float
    bound_certified: bool
    compile_refusal: str
    d_labels: list[int]
    d_objective: float
    d_voronoi_consistent: bool
    d_violating_moves: int
    d_compiles: bool
    d_certificate_status: str
    d_incumbent_was_optimal: bool
    d_nodes_explored: int


def library_run() -> LibraryRun:
    """Reproduce both optima with the library and record what it refuses.

    Returns
    -------
    LibraryRun
        The profiled result with its measured violation and its refusal, and
        the determinant result with its clean geometry and its certificate.
    """
    scores, weights = float_table()
    config = sq.DExchangeConfig(seed=1, n_init=32, max_scans=200)

    profiled = sq.optimize_partition(
        scores,
        weights=weights,
        n_bins=N_CELLS,
        criterion=sq.ProfiledDOptimality(INTEREST),
        config=config,
    )
    geometry = profiled.profiled_geometry
    if geometry is None:  # pragma: no cover - a profiled result always carries one
        raise RuntimeError("a profiled partition must report profiled geometry")
    try:
        profiled.compile_quantizer()
        refusal = ""
    except ValueError as error:
        refusal = str(error)

    plain = sq.optimize_partition(scores, weights=weights, n_bins=N_CELLS, config=config)
    plain_geometry = plain.geometry
    if plain_geometry is None:  # pragma: no cover - a D result always carries one
        raise RuntimeError("a determinant partition must report geometry")
    compiled = plain.compile_quantizer()
    certificate = sq.certify_partition(
        scores, weights=weights, n_bins=N_CELLS, incumbent=plain.labels
    )

    return LibraryRun(
        profiled_labels=[int(value) for value in np.asarray(profiled.labels)],
        profiled_information=float(np.exp(profiled.objective)),
        violating_moves=int(geometry.violating_moves),
        maximum_positive_violation=float(geometry.maximum_positive_violation),
        maximum_bound_residual=float(geometry.maximum_bound_residual),
        bound_certified=bool(geometry.bound_certified),
        compile_refusal=refusal,
        d_labels=[int(value) for value in np.asarray(plain.labels)],
        d_objective=float(plain.objective),
        d_voronoi_consistent=bool(plain_geometry.voronoi_consistent),
        d_violating_moves=int(plain_geometry.violating_moves),
        d_compiles=bool(
            np.array_equal(np.asarray(compiled.predict_scores(scores)), np.asarray(plain.labels))
        ),
        d_certificate_status=str(certificate.status),
        d_incumbent_was_optimal=bool(certificate.incumbent_was_optimal),
        d_nodes_explored=int(certificate.nodes_explored),
    )


@dataclass(frozen=True, slots=True)
class Study:
    """Everything the page and the figure need from one deterministic run."""

    metrics: dict[str, object]
    profiled: Ranking = field(repr=False)
    determinant: Ranking = field(repr=False)
    library: LibraryRun = field(repr=False)


def run_study() -> Study:
    """Run both exact enumerations and the library reproduction.

    Returns
    -------
    Study
        The exact structure written to
        ``docs/examples/assets/ds-geometry-counterexample.json``, plus the
        rankings the figure draws.
    """
    table = exact_table()
    profiled = rank_labelings("profiled", table)
    determinant = rank_labelings("determinant", table)
    library = library_run()

    matrix = binned_information(tuple(profiled.optimum), table)
    regression = matrix[1][0] / matrix[1][1]
    metrics: dict[str, object] = {
        "raw_table": [list(row) for row in RAW_TABLE],
        "n_labelings": len(profiled.values),
        "efficient_regression": str(regression),
        "profiled": asdict(profiled),
        "determinant": asdict(determinant),
        "library": asdict(library),
    }
    return Study(metrics=metrics, profiled=profiled, determinant=determinant, library=library)


def efficient_coordinate(table: ExactMatrix, labels: tuple[int, ...]) -> tuple[np.ndarray, float]:
    """Return each row's efficient score under one labeling, and the coefficient.

    Parameters
    ----------
    table
        The exact score table.
    labels
        The labeling whose nuisance regression defines the efficient score.

    Returns
    -------
    tuple
        The eight efficient scores as floats, and the regression coefficient
        that defines them.
    """
    matrix = binned_information(labels, table)
    regression = matrix[1][0] / matrix[1][1]
    values = np.asarray([float(row[0] - regression * row[1]) for row in table])
    return values, float(regression)


def make_figure(study: Study) -> Figure:
    """Render the two-panel profiled-geometry counterexample.

    Parameters
    ----------
    study
        The object returned by `run_study`.

    Returns
    -------
    matplotlib.figure.Figure
        The eight rows with the bands of the semimetric they induce, and the
        exact ranking of all 966 labelings with the self-consistent ones marked.
    """
    figure, axes = plt.subplots(1, 2, figsize=(12.5, 5.0), constrained_layout=True)
    colors = ["#38618c", "#c0563c", "#4f9d69"]

    table = exact_table()
    optimum = tuple(study.profiled.optimum)
    scores, _ = float_table()
    efficient, regression = efficient_coordinate(table, optimum)
    masses, moments = cell_moments(optimum, table)
    means = np.asarray(
        [[float(moments[cell][column] / masses[cell]) for column in range(2)] for cell in range(3)]
    )
    projected = means[:, 0] - regression * means[:, 1]

    order = np.argsort(projected)
    boundaries = [
        0.5 * (projected[order[index]] + projected[order[index + 1]]) for index in range(2)
    ]
    span = np.linspace(scores[:, 1].min() - 1.0, scores[:, 1].max() + 1.0, 32)
    for boundary in boundaries:
        axes[0].plot(
            boundary + regression * span,
            span,
            linestyle="--",
            linewidth=1.0,
            color="#999999",
        )
    for cell in range(3):
        rows = np.asarray(optimum) == cell
        axes[0].scatter(
            scores[rows, 0], scores[rows, 1], s=90, color=colors[cell], label=f"cell {cell}"
        )
    axes[0].scatter(means[:, 0], means[:, 1], marker="x", s=110, color="#333333")
    violating = int(
        np.argmax([float(Fraction(margin)) for margin in study.profiled.optimum_margins])
    )
    axes[0].annotate(
        f"row {violating} sits in the band of another cell,\n"
        f"by exactly {study.profiled.optimum_margins[violating]}",
        xy=(scores[violating, 0] - 0.15, scores[violating, 1] + 0.15),
        xytext=(-6.2, 5.6),
        fontsize=9,
        arrowprops={"arrowstyle": "->", "color": "#333333"},
    )
    axes[0].set(
        xlim=(-6.6, 5.2),
        ylim=(-5.4, 6.4),
        xlabel="score column 0 (of interest)",
        ylabel="score column 1 (nuisance)",
        title="The globally optimal profiled labeling",
    )
    axes[0].legend(loc="lower left")

    # The determinant is a product over two parameters and the Schur complement
    # is a single one, so the determinant is shown per parameter to put both
    # criteria on one comparable scale.
    for name, ranking, color, marker, power in (
        ("profiled $D_s$", study.profiled, "#c0563c", "o", 1.0),
        ("plain D", study.determinant, "#38618c", "s", 0.5),
    ):
        values = np.asarray(ranking.values)
        normalized = np.power(np.maximum(values / values[0], 0.0), power)
        ranks = np.arange(values.shape[0])
        axes[1].plot(ranks, normalized, color=color, linewidth=1.2, label=name)
        consistent = np.asarray(ranking.consistent_ranks, dtype=int)
        axes[1].scatter(
            consistent,
            normalized[consistent],
            s=80,
            facecolors="none",
            edgecolors=color,
            marker=marker,
            linewidths=1.6,
            label=f"{name}: self-consistent ({consistent.shape[0]} of 966)",
        )
    best = study.profiled.best_consistent_rank
    axes[1].annotate(
        f"the only self-consistent profiled labeling\nranks {best}, "
        f"at {100 * study.profiled.best_consistent_ratio:.1f}% of the optimum",
        xy=(best + 1.0, study.profiled.best_consistent_ratio),
        xytext=(16, 0.99),
        fontsize=9,
        color="#c0563c",
        arrowprops={"arrowstyle": "->", "color": "#c0563c"},
    )
    axes[1].set(
        xlim=(-2, 80),
        ylim=(0.3, 1.04),
        xlabel="rank among all 966 labelings",
        ylabel="criterion per parameter, relative to the optimum",
        title="Which labelings satisfy their own geometry",
    )
    axes[1].legend(loc="lower left", fontsize=8)

    figure.suptitle("An optimum outside the geometry it induces")
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
