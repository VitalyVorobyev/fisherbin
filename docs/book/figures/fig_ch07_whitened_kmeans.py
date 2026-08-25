"""Render the raw-versus-whitened k-means figure for chapter 7.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch07_whitened_kmeans.py

A two-parameter score law whose coordinates carry very different numerical
scales is fitted twice with weighted k-means: once in raw coordinates, once
after Fisher whitening. Both fits are drawn in the same whitened frame, where
every direction is worth the same, so the raw fit's blindness to the second
direction is visible directly.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np

import scorequant as sq

N_ROWS = 2_000
N_BINS = 4
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch07_whitened_kmeans.png"


def anisotropic_scores(seed: int = 7, n_rows: int = N_ROWS) -> np.ndarray:
    """Return a two-parameter score table with very unequal coordinate scales.

    Parameters
    ----------
    seed
        Generator seed.
    n_rows
        Number of score rows.

    Returns
    -------
    numpy.ndarray
        Score matrix with shape ``[n_rows, 2]``.
    """
    base = np.random.default_rng(seed).normal(size=(n_rows, 2))
    return np.stack([40.0 * base[:, 0], 0.05 * base[:, 1]], axis=1)


def four_cell_fit(scores: np.ndarray, whiten: bool) -> sq.QuantizerResult:
    """Fit four weighted k-means cells with or without Fisher whitening.

    Parameters
    ----------
    scores
        Score matrix with shape ``[N, 2]``.
    whiten
        Whether to whiten the informative subspace before measuring distance.

    Returns
    -------
    scorequant.QuantizerResult
        Fitted rule with its retained-information report.
    """
    return sq.fit_quantizer(
        sq.ScoreSample(scores),
        n_bins=N_BINS,
        criterion=sq.NormalizedTrace(),
        config=sq.KMeansConfig(seed=0, n_init=4, whiten=whiten),
    )


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)
    scores = anisotropic_scores()
    raw = four_cell_fit(scores, whiten=False)
    whitened = four_cell_fit(scores, whiten=True)
    # ``fisher_transform`` orders directions by ascending eigenvalue; plot the
    # numerically dominant raw direction horizontally so the raw fit's bands are
    # perpendicular to the coordinate it spent every cell on.
    order = np.argsort(-np.asarray(whitened.transform.retained_eigenvalues))
    coordinates = np.asarray(whitened.transform.apply(scores))[:, order]

    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), constrained_layout=True)

    for panel, fit, title in (
        (axes[0], raw, "k-means on raw scores"),
        (axes[1], whitened, "k-means after whitening"),
    ):
        labels = np.asarray(fit.labels)
        for cell in range(N_BINS):
            member = labels == cell
            panel.scatter(
                coordinates[member, 0],
                coordinates[member, 1],
                s=4,
                color=f"C{cell}",
                alpha=0.45,
                linewidths=0,
            )
        panel.set_xlabel("whitened coordinate $u_1$")
        panel.set_aspect("equal")
        panel.set_title(title)
    axes[0].set_ylabel("whitened coordinate $u_2$")

    positions = np.arange(2)
    width = 0.36
    for offset, fit, colour, name in (
        (-width / 2, raw, "C3", "raw"),
        (width / 2, whitened, "C0", "whitened"),
    ):
        report = fit.train_report
        eigenvalues = np.sort(np.asarray(report.retained_eigenvalues))[::-1]
        axes[2].bar(positions + offset, eigenvalues, width=width, color=colour, label=name)
        axes[2].plot(
            positions + offset,
            np.full(2, float(report.geometric_mean_retention)),
            marker="_",
            markersize=18,
            linestyle="none",
            color="black",
        )
    axes[2].set_xticks(positions)
    axes[2].set_xticklabels(["best-kept direction", "worst-kept direction"])
    axes[2].set_ylabel("retained fraction")
    axes[2].set_ylim(0.0, 1.0)
    axes[2].legend(loc="upper right")
    axes[2].set_title("retained eigenvalues (bars),\ngeometric mean (dashes)")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
