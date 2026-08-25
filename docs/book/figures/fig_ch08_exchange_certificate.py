"""Render the exchange-geometry and certificate figure for chapter 8.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch08_exchange_certificate.py

The left panel draws a terminal exchange-stable D partition in raw score
coordinates together with the Mahalanobis rule it compiles into: straight cell
boundaries, cell means, and one level set of the quadratic form that produced
them. The right panel follows five exchange runs on a twenty-four-row table
small enough to certify by branch and bound, against the certified global
optimum, with an inset on the terminal values.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Ellipse

import scorequant as sq

PANEL_ROWS = 600
PANEL_BINS = 4
CERTIFIED_ROWS = 24
CERTIFIED_BINS = 4
GRID = 380
MIXING = np.array([[1.5, 0.0], [1.1, 0.6]])
GAP_FLOOR = 1e-4
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch08_exchange_certificate.png"


def metric_ellipse(center: np.ndarray, metric: np.ndarray, major: float) -> Ellipse:
    """Return a level set of one quadratic form, scaled to a drawable size.

    Parameters
    ----------
    center
        Ellipse center with shape ``[2]``.
    metric
        Symmetric positive-definite matrix with shape ``[2, 2]``.
    major
        Target length of the longest semi-axis; the level is chosen to match it,
        so only the shape and orientation of the form are being displayed.

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
        edgecolor="black",
        linestyle="--",
        linewidth=1.3,
    )


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)

    rng = np.random.default_rng(8)
    scores = rng.normal(size=(PANEL_ROWS, 2)) @ MIXING.T
    partition = sq.optimize_partition(scores, n_bins=PANEL_BINS, config=sq.DExchangeConfig(seed=0))
    compiled = partition.compile_quantizer()
    labels = np.asarray(partition.labels)
    means = np.asarray(partition.cell_score_means)

    # predict_scores whitens internally, so the rule's quadratic form on raw
    # score vectors is the whitening matrix conjugating the criterion metric.
    whitener = np.asarray(partition.transform.matrix)
    raw_metric = whitener @ np.asarray(partition.metric) @ whitener.T

    reach = 1.1 * float(np.max(np.abs(scores)))
    axis = np.linspace(-reach, reach, GRID)
    mesh_x, mesh_y = np.meshgrid(axis, axis)
    grid = np.stack([mesh_x.ravel(), mesh_y.ravel()], axis=1)
    regions = np.asarray(compiled.predict_scores(grid)).reshape(GRID, GRID)

    small = np.random.default_rng(8).normal(size=(CERTIFIED_ROWS, 2))
    certificate = sq.certify_partition(small, n_bins=CERTIFIED_BINS)
    histories = []
    for seed in range(4):
        run = sq.optimize_partition(
            small,
            n_bins=CERTIFIED_BINS,
            config=sq.DExchangeConfig(seed=seed, init="random", batch_moves=False, n_init=1),
        )
        histories.append((f"random restart {seed}", np.asarray(run.objective_history)))
    seeded = sq.optimize_partition(
        small,
        n_bins=CERTIFIED_BINS,
        config=sq.DExchangeConfig(seed=0, init="kmeans++", batch_moves=False, n_init=1),
    )
    gaps = [certificate.objective - float(history[-1]) for _, history in histories]
    print(
        f"certified optimum {certificate.objective:.6f} "
        f"({certificate.status}, {certificate.nodes_explored} nodes); "
        f"k-means++ start reached {seeded.objective:.6f}"
    )
    print("random-restart gaps: " + ", ".join(f"{gap:.4f}" for gap in gaps))

    colours = ListedColormap([f"C{index}" for index in range(PANEL_BINS)])
    figure, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), constrained_layout=True)

    axes[0].pcolormesh(
        mesh_x,
        mesh_y,
        regions,
        cmap=colours,
        vmin=-0.5,
        vmax=PANEL_BINS - 0.5,
        alpha=0.28,
        shading="auto",
    )
    for cell in range(PANEL_BINS):
        member = labels == cell
        axes[0].scatter(
            scores[member, 0],
            scores[member, 1],
            s=4,
            color=f"C{cell}",
            alpha=0.6,
            linewidths=0,
        )
        axes[0].plot(
            means[cell, 0],
            means[cell, 1],
            marker="X",
            markersize=10,
            color="black",
            markeredgecolor="white",
            markeredgewidth=0.8,
        )
    axes[0].add_patch(metric_ellipse(np.zeros(2), raw_metric, 0.72 * reach))
    axes[0].annotate(
        "level set of the rule's metric",
        xy=(-0.95 * reach, 0.88 * reach),
        fontsize=8,
    )
    axes[0].set_xlim(-reach, reach)
    axes[0].set_ylim(-reach, reach)
    axes[0].set_aspect("equal")
    axes[0].set_xlabel("score coordinate $s_1$")
    axes[0].set_ylabel("score coordinate $s_2$")
    axes[0].set_title("terminal partition and the compiled\nMahalanobis rule it reproduces")

    def shortfall(history: np.ndarray) -> np.ndarray:
        """Return the display gap to the certified optimum, floored for a log axis."""
        return np.maximum(certificate.objective - history, GAP_FLOOR)

    for index, (name, history) in enumerate(histories):
        axes[1].step(
            np.arange(history.size), shortfall(history), where="post", color=f"C{index}", label=name
        )
        axes[1].plot(history.size - 1, shortfall(history)[-1], marker="o", color=f"C{index}")
    terminal = np.asarray(seeded.objective_history)
    axes[1].step(
        np.arange(terminal.size),
        shortfall(terminal),
        where="post",
        color="black",
        linewidth=1.8,
        label="k-means++ start",
    )
    axes[1].plot(terminal.size - 1, shortfall(terminal)[-1], marker="o", color="black")
    axes[1].axhline(GAP_FLOOR, color="0.35", linestyle="--", linewidth=1.2)
    axes[1].annotate(
        "certified global optimum",
        xy=(0.4, 1.35 * GAP_FLOOR),
        color="0.35",
        fontsize=8,
    )
    axes[1].set_yscale("log")
    axes[1].set_xlabel("accepted single-row relocations")
    axes[1].set_ylabel("shortfall from the certified optimum (nat)")
    axes[1].set_ylim(0.5 * GAP_FLOOR, 6.0)
    axes[1].legend(loc="upper right", fontsize=8)
    axes[1].set_title("monotone exchange on 24 rows,\nagainst a branch-and-bound certificate")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
