"""Render the labeling-versus-rule figure for chapter 6.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch06_two_extensions.py

One optimal four-cell labeling of 400 score rows is extended to the whole plane
in two ways that both reproduce every training label: the canonical Mahalanobis
rule a stable D partition compiles into, and the nearest-training-row rule. The
fraction of the plotted region on which they disagree is printed when the script
runs, and is the number quoted in the caption.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

import scorequant as sq

N_ROWS = 400
N_BINS = 4
GRID = 420
SPAN = 3.4
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch06_two_extensions.png"


def nearest_row_labels(grid: np.ndarray, scores: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Label grid points by the label of their nearest training row.

    Parameters
    ----------
    grid
        Query points with shape ``[M, 2]``.
    scores
        Training score rows with shape ``[N, 2]``.
    labels
        Training labels with shape ``[N]``.

    Returns
    -------
    numpy.ndarray
        Integer labels with shape ``[M]``.
    """
    assigned = np.empty(grid.shape[0], dtype=np.int64)
    for start in range(0, grid.shape[0], 4_000):
        stop = min(start + 4_000, grid.shape[0])
        distances = np.sum((grid[start:stop, None, :] - scores[None, :, :]) ** 2, axis=2)
        assigned[start:stop] = labels[np.argmin(distances, axis=1)]
    return assigned


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)
    rng = np.random.default_rng(6)
    scores = rng.normal(size=(N_ROWS, 2)) @ np.array([[1.0, 0.4], [0.0, 1.1]])

    partition = sq.optimize_partition(scores, n_bins=N_BINS, config=sq.DExchangeConfig(seed=0))
    labels = np.asarray(partition.labels)
    compiled = partition.compile_quantizer()

    axis = np.linspace(-SPAN, SPAN, GRID)
    mesh_x, mesh_y = np.meshgrid(axis, axis)
    grid = np.stack([mesh_x.ravel(), mesh_y.ravel()], axis=1)

    mahalanobis = np.asarray(compiled.predict_scores(grid))
    nearest = nearest_row_labels(grid, scores, labels)
    region = 100.0 * float(np.mean(mahalanobis != nearest))
    print(f"extensions disagree on {region:.1f}% of the plotted region")

    fresh = np.random.default_rng(60).normal(size=(20_000, 2)) @ np.array([[1.0, 0.4], [0.0, 1.1]])
    fresh_disagreement = float(
        np.mean(
            np.asarray(compiled.predict_scores(fresh)) != nearest_row_labels(fresh, scores, labels)
        )
    )
    print(f"extensions disagree on {100 * fresh_disagreement:.1f}% of fresh events")

    colours = ListedColormap([f"C{index}" for index in range(N_BINS)])
    figure, axes = plt.subplots(1, 3, figsize=(13.5, 5.0), constrained_layout=True)

    for panel in axes:
        panel.set_xlim(-SPAN, SPAN)
        panel.set_ylim(-SPAN, SPAN)
        panel.set_aspect("equal")
        panel.set_xlabel("score coordinate $s_1$")
    axes[0].set_ylabel("score coordinate $s_2$")

    for cell in range(N_BINS):
        member = labels == cell
        axes[0].scatter(scores[member, 0], scores[member, 1], s=12, color=f"C{cell}", linewidths=0)
    axes[0].set_title("labels on 400 rows")

    for panel, assigned, title in (
        (axes[1], mahalanobis, "Mahalanobis extension"),
        (axes[2], nearest, "nearest-row extension"),
    ):
        panel.pcolormesh(
            mesh_x,
            mesh_y,
            assigned.reshape(GRID, GRID),
            cmap=colours,
            vmin=-0.5,
            vmax=N_BINS - 0.5,
            alpha=0.35,
            shading="auto",
        )
        panel.scatter(scores[:, 0], scores[:, 1], s=6, color="black", linewidths=0)
        panel.set_title(title)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
