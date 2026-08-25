"""Render the conditional-score-mean figure for chapter 5.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch05_cell_means.py

The left panel shows where the retained information lives: the weighted scatter
of the cell means about the score-space origin, with the within-cell residuals
that the labels destroy. The right panel tracks both retained eigenvalues and
their geometric mean against the cell budget, so the rank ceiling at ``K = 2``
is visible as a direction pinned to zero.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np

import scorequant as sq

BIN_COUNTS = (2, 3, 4, 5, 6, 7)
PANEL_BINS = 4
RESIDUAL_ROWS = 150
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch05_cell_means.png"


def mean_zero_scores(seed: int = 15, n_pairs: int = 900) -> np.ndarray:
    """Return a two-parameter score table whose mean vanishes by construction.

    Parameters
    ----------
    seed
        Generator seed.
    n_pairs
        Number of antipodal row pairs; the table has ``2 * n_pairs`` rows.

    Returns
    -------
    numpy.ndarray
        Score matrix with shape ``[2 * n_pairs, 2]``.
    """
    rng = np.random.default_rng(seed)
    half = rng.normal(size=(n_pairs, 2)) @ np.array([[1.0, 0.55], [0.0, 1.15]])
    return np.concatenate([half, -half], axis=0)


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)
    scores = mean_zero_scores()

    panel = sq.optimize_partition(scores, n_bins=PANEL_BINS, config=sq.DExchangeConfig(seed=0))
    labels = np.asarray(panel.labels)
    means = np.asarray(panel.cell_score_means)

    eigenvalues = []
    geometric = []
    for n_bins in BIN_COUNTS:
        if n_bins == 2:
            # Two cells of a mean-zero law give antipodal moments, so the
            # partition is exactly rank one and no D solver is well posed.
            report = sq.information_report(scores, (scores[:, 0] > 0.0).astype(int), n_bins=2)
        else:
            report = sq.optimize_partition(
                scores, n_bins=n_bins, config=sq.DExchangeConfig(seed=0)
            ).train_report
        eigenvalues.append(np.sort(np.asarray(report.retained_eigenvalues)))
        geometric.append(float(report.geometric_mean_retention))
    eigenvalues = np.asarray(eigenvalues)

    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), constrained_layout=True)

    rng = np.random.default_rng(0)
    shown = rng.choice(scores.shape[0], size=RESIDUAL_ROWS, replace=False)
    for row in shown:
        cell = int(labels[row])
        axes[0].plot(
            [scores[row, 0], means[cell, 0]],
            [scores[row, 1], means[cell, 1]],
            color="0.7",
            linewidth=0.5,
            zorder=1,
        )
    for cell in range(PANEL_BINS):
        member = labels == cell
        axes[0].scatter(
            scores[member, 0],
            scores[member, 1],
            s=3,
            color=f"C{cell}",
            alpha=0.35,
            linewidths=0,
            zorder=2,
        )
        axes[0].plot(
            means[cell, 0],
            means[cell, 1],
            marker="X",
            markersize=11,
            color=f"C{cell}",
            markeredgecolor="black",
            markeredgewidth=0.8,
            zorder=4,
        )
        axes[0].annotate(
            "",
            xy=(means[cell, 0], means[cell, 1]),
            xytext=(0.0, 0.0),
            arrowprops={"arrowstyle": "->", "color": "black", "linewidth": 1.2},
            zorder=3,
        )
    axes[0].plot(
        0.0, 0.0, marker="o", markersize=8, markerfacecolor="white", color="black", zorder=5
    )
    axes[0].set_xlabel("score coordinate $s_1$")
    axes[0].set_ylabel("score coordinate $s_2$")
    axes[0].set_aspect("equal")

    axes[1].plot(
        BIN_COUNTS, eigenvalues[:, 1], marker="o", color="C0", label="larger retained eigenvalue"
    )
    axes[1].plot(
        BIN_COUNTS, eigenvalues[:, 0], marker="s", color="C3", label="smaller retained eigenvalue"
    )
    axes[1].plot(
        BIN_COUNTS, geometric, marker="^", color="black", linestyle="--", label="geometric mean"
    )
    axes[1].axhline(0.0, color="0.6", linewidth=0.8)
    axes[1].annotate(
        "rank ceiling:\n$K-1 < d$",
        xy=(2, 0.0),
        xytext=(3.3, 0.09),
        arrowprops={"arrowstyle": "->", "color": "0.35", "linewidth": 1.0},
        color="0.35",
    )
    axes[1].set_xlabel("number of cells $K$")
    axes[1].set_ylabel("retained fraction")
    axes[1].set_ylim(-0.03, 1.0)
    axes[1].legend(loc="lower right")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
