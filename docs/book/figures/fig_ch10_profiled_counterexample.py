"""Render the profiled-D_s figure for chapter 10.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch10_profiled_counterexample.py

The left panel draws the committed eight-row rational counterexample with its
globally optimal three-cell labeling, the rank-one efficient semimetric it
induces, and the single row that sits outside its own nearest band. The right
panel compares the certified efficient-score ceiling with the profiled
objective that exchange reaches from generic seeding and from the bound's own
labels.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np

import scorequant as sq

OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch10_profiled_counterexample.png"

RAW = [(4, -4), (-5, 2), (-1, 0), (-5, -1), (2, -2), (4, 3), (2, 4), (2, -4)]
OPTIMUM = (0, 1, 2, 1, 2, 0, 0, 2)
VIOLATING_ROW = 6
MIXING = np.array([[1.0, 0.6, -0.3], [0.0, 1.1, 0.4], [0.0, 0.0, 0.9]])
CELL_BUDGETS = range(3, 9)


def efficient_direction() -> tuple[float, np.ndarray]:
    """Return the nuisance regression coefficient and the optimum's cell means.

    Returns
    -------
    tuple
        The scalar coefficient ``c`` of the efficient projection
        ``e(s) = s_1 + c * s_2`` induced by the globally optimal labeling, and
        the ``[3, 2]`` array of cell means of that labeling.
    """
    weight = Fraction(1, 8)
    centre = [Fraction(sum(row[axis] for row in RAW), 8) for axis in range(2)]
    table = [[Fraction(row[axis]) - centre[axis] for axis in range(2)] for row in RAW]
    mass = [Fraction(0)] * 3
    moment = [[Fraction(0), Fraction(0)] for _ in range(3)]
    for row, cell in enumerate(OPTIMUM):
        mass[cell] += weight
        for axis in range(2):
            moment[cell][axis] += weight * table[row][axis]
    matrix = [
        [sum(moment[cell][i] * moment[cell][j] / mass[cell] for cell in range(3)) for j in range(2)]
        for i in range(2)
    ]
    coefficient = -matrix[0][1] / matrix[1][1]
    means = np.array(
        [[float(moment[cell][axis] / mass[cell]) for axis in range(2)] for cell in range(3)]
    )
    return float(coefficient), means


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)

    coefficient, means = efficient_direction()
    scores = np.asarray(RAW, dtype=float) - np.asarray(RAW, dtype=float).mean(axis=0)
    labels = np.asarray(OPTIMUM)
    projected_means = means[:, 0] + coefficient * means[:, 1]
    order = np.argsort(projected_means)
    boundaries = 0.5 * (projected_means[order][:-1] + projected_means[order][1:])

    rng = np.random.default_rng(13)
    table = rng.normal(size=(400, 3)) @ MIXING
    ceilings, plain, warm = [], [], []
    for n_bins in CELL_BUDGETS:
        bound = sq.efficient_score_bound(table, interest=(0,), n_bins=n_bins)
        cold = sq.optimize_partition(
            table,
            n_bins=n_bins,
            criterion=sq.ProfiledDOptimality((0,)),
            config=sq.DExchangeConfig(seed=0, initializer_restarts=8),
        )
        hot = sq.optimize_partition(
            table,
            n_bins=n_bins,
            criterion=sq.ProfiledDOptimality((0,)),
            config=sq.DExchangeConfig(seed=0, initializer_restarts=8),
            initial_labels=bound.labels,
        )
        ceilings.append(bound.upper_bound)
        plain.append(cold.objective)
        warm.append(hot.objective)
    print(f"ceiling {ceilings[1]:.6f} plain {plain[1]:.6f} warm {warm[1]:.6f}")

    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.7), constrained_layout=True)

    lower, upper = -7.0, 6.0
    for boundary in boundaries:
        axes[0].plot(
            [boundary - coefficient * lower, boundary - coefficient * upper],
            [lower, upper],
            linestyle="--",
            color="0.45",
            linewidth=1.1,
        )
    for cell in range(3):
        member = labels == cell
        axes[0].scatter(
            scores[member, 0],
            scores[member, 1],
            s=90,
            color=f"C{cell}",
            zorder=3,
            linewidths=0,
            label=f"cell {cell}",
        )
        axes[0].plot(
            means[cell, 0],
            means[cell, 1],
            marker="X",
            markersize=13,
            color=f"C{cell}",
            markeredgecolor="black",
            markeredgewidth=0.9,
            zorder=4,
        )
        axes[0].plot(
            [projected_means[cell]],
            [lower + 0.35],
            marker="|",
            markersize=14,
            color=f"C{cell}",
            zorder=4,
        )
    axes[0].scatter(
        scores[VIOLATING_ROW, 0],
        scores[VIOLATING_ROW, 1],
        s=260,
        facecolor="none",
        edgecolor="C3",
        linewidth=2.0,
        zorder=5,
    )
    axes[0].annotate(
        "row 6: labeled cell 0,\nnearest cell 2 by 8/195",
        xy=(scores[VIOLATING_ROW, 0], scores[VIOLATING_ROW, 1]),
        xytext=(-6.6, 4.6),
        color="C3",
        fontsize=9,
        arrowprops={"arrowstyle": "->", "color": "C3", "linewidth": 1.2},
    )
    axes[0].axhline(lower + 0.35, color="0.75", linewidth=0.8, zorder=1)
    axes[0].set_xlim(lower, upper)
    axes[0].set_ylim(lower, upper)
    axes[0].set_xlabel("score coordinate $s_1$")
    axes[0].set_ylabel("score coordinate $s_2$")
    axes[0].set_aspect("equal")
    axes[0].legend(loc="lower right", fontsize=9)
    axes[0].set_title("the global profiled optimum\nand its own efficient bands")

    budgets = np.asarray(list(CELL_BUDGETS))
    axes[1].plot(
        budgets, ceilings, marker="s", color="black", linewidth=1.8, label="certified ceiling"
    )
    axes[1].plot(
        budgets, warm, marker="o", color="C0", linewidth=1.5, label="exchange from the bound"
    )
    axes[1].plot(
        budgets, plain, marker="^", color="C3", linewidth=1.5, label="exchange from k-means++"
    )
    axes[1].set_xlabel("cells $K$")
    axes[1].set_ylabel(r"$\log\det S_\psi(I_q)$")
    axes[1].legend(loc="lower right", fontsize=9)
    axes[1].set_title("what no rule can exceed,\nand what two starts reach")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
