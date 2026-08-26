"""Render the E-optimality figure for chapter 11.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch11_e_geometry.py

The left panel draws the committed eight-row fixture with its globally
E-optimal three-cell labeling, the slabs of the rank-one nearest-cell rule that
its own minimum eigenvector induces, and the single row that violates them. The
right panel plots every three-cell labeling of the fixture in the
(log-determinant, minimum-eigenvalue) plane, marking the two criteria's optima.

The script uses NumPy only; no JAX configuration is required for the numbers it
computes, so the rendered figure is byte-identical whatever the caller's
floating-point configuration is.
"""

from __future__ import annotations

from itertools import product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch11_e_geometry.png"

TABLE = np.array(
    [
        [-0.226534, 0.428773],
        [-0.629944, -1.223406],
        [1.253439, -0.109445],
        [1.807897, 0.734952],
        [-1.520937, -0.061786],
        [-0.488606, -0.002247],
        [0.710355, 1.154412],
        [-0.905669, -0.921253],
    ]
)
VIOLATING_ROW = 7
N_BINS = 3


def binned_information(table: np.ndarray, labels: tuple[int, ...]) -> np.ndarray:
    """Return the between-cell information matrix of one labeling.

    Parameters
    ----------
    table
        Score rows with shape ``[N, 2]``.
    labels
        Cell index of every row.

    Returns
    -------
    numpy.ndarray
        Weighted scatter of the cell means about the score-space origin.
    """
    assignment = np.asarray(labels)
    mass = np.bincount(assignment, minlength=N_BINS).astype(float)
    sums = np.zeros((N_BINS, table.shape[1]))
    np.add.at(sums, assignment, table)
    means = sums / mass[:, None]
    return np.einsum("b,bp,bq->pq", mass, means, means)


def canonical_labelings(n_rows: int, n_bins: int) -> list[tuple[int, ...]]:
    """Return every labeling with nonempty cells, once per unlabeled partition."""
    return [
        labels
        for labels in product(range(n_bins), repeat=n_rows)
        if labels[0] == 0
        and set(labels) == set(range(n_bins))
        and all(labels[index] <= max(labels[:index]) + 1 for index in range(1, n_rows))
    ]


def main() -> None:
    """Build and save the figure."""
    table = TABLE - TABLE.mean(axis=0)
    labelings = canonical_labelings(8, N_BINS)
    matrices = {labels: binned_information(table, labels) for labels in labelings}
    smallest = np.array([float(np.linalg.eigvalsh(matrices[k])[0]) for k in labelings])
    volumes = np.array([float(np.linalg.slogdet(matrices[k])[1]) for k in labelings])

    e_index = int(np.argmax(smallest))
    d_index = int(np.argmax(volumes))
    optimum = labelings[e_index]
    eigenvalues, eigenvectors = np.linalg.eigh(matrices[optimum])
    direction = eigenvectors[:, 0]
    assignment = np.asarray(optimum)
    means = np.stack([table[assignment == cell].mean(axis=0) for cell in range(N_BINS)])
    projected_means = means @ direction
    order = np.argsort(projected_means)
    boundaries = 0.5 * (projected_means[order][:-1] + projected_means[order][1:])
    distances = np.square((table[:, None, :] - means[None, :, :]) @ direction)
    margin = float(
        distances[VIOLATING_ROW, assignment[VIOLATING_ROW]] - distances[VIOLATING_ROW].min()
    )
    print(f"E optimum {optimum} margin {margin:.6f} gap {eigenvalues[1] - eigenvalues[0]:.4f}")

    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.7), constrained_layout=True)

    span = np.array([-2.6, 2.6])
    normal = np.array([-direction[1], direction[0]])
    for boundary in boundaries:
        points = boundary * direction + span[:, None] * normal[None, :]
        axes[0].plot(points[:, 0], points[:, 1], linestyle="--", color="0.45", linewidth=1.1)
    for cell in range(N_BINS):
        member = assignment == cell
        axes[0].scatter(
            table[member, 0],
            table[member, 1],
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
    axes[0].annotate(
        "",
        xy=tuple(1.6 * direction),
        xytext=(0.0, 0.0),
        arrowprops={"arrowstyle": "->", "color": "0.2", "linewidth": 1.6},
        zorder=5,
    )
    axes[0].annotate(
        "$v$", xy=tuple(1.72 * direction), color="0.2", fontsize=11, ha="center", va="center"
    )
    axes[0].scatter(
        table[VIOLATING_ROW, 0],
        table[VIOLATING_ROW, 1],
        s=260,
        facecolor="none",
        edgecolor="C3",
        linewidth=2.0,
        zorder=5,
    )
    axes[0].annotate(
        f"row 7: labeled cell 1,\nnearest cell 2 by {margin:.4f}",
        xy=(table[VIOLATING_ROW, 0], table[VIOLATING_ROW, 1]),
        xytext=(-2.45, -2.45),
        color="C3",
        fontsize=9,
        arrowprops={"arrowstyle": "->", "color": "C3", "linewidth": 1.2},
    )
    axes[0].set_xlim(-2.6, 2.9)
    axes[0].set_ylim(-2.7, 2.2)
    axes[0].set_xlabel("score coordinate $s_1$")
    axes[0].set_ylabel("score coordinate $s_2$")
    axes[0].set_aspect("equal")
    axes[0].legend(loc="upper left", fontsize=9)
    axes[0].set_title("the global E optimum\nand its own rank-one slabs")

    axes[1].scatter(volumes, smallest, s=12, color="0.65", linewidths=0, label="all 966 labelings")
    axes[1].scatter(
        [volumes[e_index]],
        [smallest[e_index]],
        s=110,
        color="C0",
        zorder=4,
        label="E optimum",
    )
    axes[1].scatter(
        [volumes[d_index]],
        [smallest[d_index]],
        s=110,
        color="C3",
        marker="D",
        zorder=4,
        label="D optimum",
    )
    axes[1].set_xlabel(r"$\log\det I_q$")
    axes[1].set_ylabel(r"$\lambda_{\min}(I_q)$")
    axes[1].set_xlim(-1.0, 3.1)
    axes[1].legend(loc="lower left", fontsize=9)
    axes[1].set_title("two criteria, two optima,\nand no domination")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
