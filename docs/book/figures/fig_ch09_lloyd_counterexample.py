"""Render the guarded-Lloyd counterexample figure for chapter 9.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch09_lloyd_counterexample.py

The left panel draws the committed eight-row fixture, its three cells, their
means, one level set of the induced Mahalanobis metric, and the four rows a
frozen-metric batch step relocates. The right panel contrasts the objective
that step reaches with the guarded solver's monotone climb from the same
labels.

Log determinants are reported in the raw convention, ``log det I_q`` of the
weighted cell moments, which differs from the library's Fisher-whitened
``objective`` by the rule-independent constant ``log det I_full``.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse

import scorequant as sq

N_BINS = 3
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch09_lloyd_counterexample.png"

SCORES = np.array(
    [
        [0.1116, 0.4427],
        [-0.2932, 0.6537],
        [-0.5995, -1.2685],
        [-0.6848, -1.5456],
        [0.4810, 0.9521],
        [1.6707, 0.9370],
        [0.1689, 1.7090],
        [-0.8548, -1.8805],
    ]
)
LABELS = np.array([1, 0, 0, 1, 2, 2, 2, 1])


def metric_ellipse(center: np.ndarray, metric: np.ndarray, major: float) -> Ellipse:
    """Return a level set of one quadratic form, scaled to a drawable size.

    Parameters
    ----------
    center
        Ellipse center with shape ``[2]``.
    metric
        Symmetric positive-definite matrix with shape ``[2, 2]``.
    major
        Target length of the longest semi-axis.

    Returns
    -------
    matplotlib.patches.Ellipse
        Outline of one level set of ``(x - center)^T metric (x - center)``.
    """
    eigenvalues, eigenvectors = np.linalg.eigh(metric)
    level = float(np.min(eigenvalues)) * major**2
    widths = 2.0 * np.sqrt(level / eigenvalues)
    angle = float(np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])))
    return Ellipse(
        tuple(center),
        width=float(widths[0]),
        height=float(widths[1]),
        angle=angle,
        fill=False,
        edgecolor="0.4",
        linestyle=":",
        linewidth=1.1,
    )


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)
    weights = np.full(SCORES.shape[0], 1.0 / SCORES.shape[0])

    information = np.asarray(sq.binned_fisher_information(SCORES, LABELS, weights, n_bins=N_BINS))
    means = np.stack([SCORES[LABELS == cell].mean(axis=0) for cell in range(N_BINS)])
    metric = np.linalg.inv(information)
    residuals = SCORES[:, None, :] - means[None, :, :]
    batch = np.argmin(np.einsum("nkp,pq,nkq->nk", residuals, metric, residuals), axis=1)

    before = float(np.linalg.slogdet(information)[1])
    after = float(
        np.linalg.slogdet(
            np.asarray(sq.binned_fisher_information(SCORES, batch, weights, n_bins=N_BINS))
        )[1]
    )
    offset = float(np.linalg.slogdet(np.asarray(sq.fisher_information(SCORES, weights)))[1])
    rescued = sq.optimize_partition(
        SCORES,
        weights=weights,
        n_bins=N_BINS,
        config=sq.MahalanobisLloydConfig(seed=0, guard="exchange"),
        initial_labels=LABELS,
    )
    climb = np.asarray(rescued.objective_history) + offset
    print(f"batch step {after - before:+.6f} nat; guarded climb {climb[-1] - climb[0]:+.6f} nat")

    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.7), constrained_layout=True)

    for cell in range(N_BINS):
        member = LABELS == cell
        axes[0].scatter(
            SCORES[member, 0], SCORES[member, 1], s=70, color=f"C{cell}", zorder=3, linewidths=0
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
        axes[0].add_patch(metric_ellipse(means[cell], metric, 0.85))
    for row in np.flatnonzero(batch != LABELS):
        axes[0].annotate(
            "",
            xy=tuple(means[batch[row]]),
            xytext=tuple(SCORES[row]),
            arrowprops={
                "arrowstyle": "->",
                "color": f"C{batch[row]}",
                "linewidth": 1.4,
                "shrinkA": 6,
                "shrinkB": 8,
            },
            zorder=2,
        )
    axes[0].set_xlabel("score coordinate $s_1$")
    axes[0].set_ylabel("score coordinate $s_2$")
    axes[0].set_aspect("equal")
    axes[0].set_title("eight rows, three cells,\nand the four the batch step moves")

    steps = np.arange(climb.size)
    axes[1].step(steps, climb, where="post", color="black", linewidth=1.8, label="guarded solver")
    axes[1].plot(steps, climb, linestyle="none", marker="o", color="black")
    axes[1].annotate(
        "",
        xy=(0.45, after),
        xytext=(0.0, before),
        arrowprops={"arrowstyle": "->", "color": "C3", "linewidth": 1.8},
    )
    axes[1].plot([0.45], [after], marker="o", color="C3")
    axes[1].annotate(
        f"unguarded batch step\n{after - before:+.6f} nat",
        xy=(0.55, after),
        xytext=(0.62, after - 0.62),
        color="C3",
        fontsize=9,
    )
    axes[1].annotate(
        f"four exact relocations\n{climb[-1] - climb[0]:+.4f} nat",
        xy=(3.0, climb[-1]),
        xytext=(1.35, climb[-1] - 1.05),
        arrowprops={"arrowstyle": "->", "color": "0.35", "linewidth": 1.0},
        fontsize=9,
    )
    axes[1].set_xlabel("accepted steps")
    axes[1].set_ylabel(r"$\log\det I_q$")
    axes[1].set_xlim(-0.25, 4.3)
    axes[1].set_ylim(-4.85, -0.65)
    axes[1].legend(loc="lower right")
    axes[1].set_title("the same starting labels,\nwith and without the guard")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
