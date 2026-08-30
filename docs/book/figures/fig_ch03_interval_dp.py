"""Render the exact one-dimensional dynamic-programming figure for chapter 3.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch03_interval_dp.py

The score law is a bulk with two small, far-away, highly informative satellite
groups. The left panel shows where the exact interval solver puts its cuts
against equal-frequency cuts; the right panel tracks retained information
against the cell budget for the exact solver, equal-frequency edges, and a
single-restart Lloyd run.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np

import scorequant as sq

BIN_COUNTS = (3, 4, 5, 6, 7, 8)
PANEL_BINS = 6
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch03_interval_dp.png"


def satellite_scores(seed: int = 3, n_rows: int = 2_000) -> np.ndarray:
    """Return a bulk-plus-satellite scalar score table.

    Parameters
    ----------
    seed
        Generator seed.
    n_rows
        Number of score rows.

    Returns
    -------
    numpy.ndarray
        Score matrix with shape ``[n_rows, 1]``.
    """
    rng = np.random.default_rng(seed)
    uniform = rng.random(n_rows)
    values = np.where(
        uniform < 0.05,
        rng.normal(-8.0, 0.2, n_rows),
        np.where(uniform < 0.10, rng.normal(8.0, 0.2, n_rows), rng.normal(0.0, 1.0, n_rows)),
    )
    return values[:, None]


def equal_frequency_labels(scores: np.ndarray, n_bins: int) -> np.ndarray:
    """Return labels of the equal-frequency rule with ``n_bins`` cells.

    Parameters
    ----------
    scores
        Score matrix with shape ``[N, 1]``.
    n_bins
        Number of cells.

    Returns
    -------
    numpy.ndarray
        Integer labels with shape ``[N]``.
    """
    cuts = np.quantile(scores[:, 0], np.arange(1, n_bins) / n_bins)
    return np.digitize(scores[:, 0], cuts)


def label_boundaries(values: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Return the midpoints separating consecutive interval cells.

    Parameters
    ----------
    values
        Scalar coordinates with shape ``[N]``.
    labels
        Integer labels with shape ``[N]``.

    Returns
    -------
    numpy.ndarray
        Interior cut points of the induced interval rule.
    """
    order = np.argsort(values, kind="stable")
    ordered_values = values[order]
    ordered_labels = np.asarray(labels)[order]
    changes = np.flatnonzero(ordered_labels[1:] != ordered_labels[:-1])
    return 0.5 * (ordered_values[changes] + ordered_values[changes + 1])


def retention(scores: np.ndarray, labels: np.ndarray, n_bins: int) -> float:
    """Return the retained-information fraction of one labeling.

    Parameters
    ----------
    scores
        Score matrix with shape ``[N, 1]``.
    labels
        Integer labels with shape ``[N]``.
    n_bins
        Number of declared cells.

    Returns
    -------
    float
        Retained fraction of the unbinned information.
    """
    report = sq.information_report(scores, np.asarray(labels), n_bins=n_bins)
    return float(report.geometric_mean_retention)


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)
    scores = satellite_scores()
    values = scores[:, 0]

    exact_curve, equal_curve = [], []
    lloyd_low, lloyd_high = [], []
    for n_bins in BIN_COUNTS:
        exact = sq.fit_quantizer(
            sq.ScoreSample(scores),
            n_bins=n_bins,
            criterion=sq.DOptimality(),
            config=sq.ScalarDPConfig(),
        )
        restarts = []
        for seed in range(8):
            lloyd = sq.fit_quantizer(
                sq.ScoreSample(scores),
                n_bins=n_bins,
                criterion=sq.NormalizedTrace(),
                config=sq.KMeansConfig(seed=seed, solver_restarts=1),
            )
            restarts.append(retention(scores, lloyd.labels, n_bins))
        exact_curve.append(retention(scores, exact.labels, n_bins))
        lloyd_low.append(min(restarts))
        lloyd_high.append(max(restarts))
        equal_curve.append(retention(scores, equal_frequency_labels(scores, n_bins), n_bins))
        if n_bins == PANEL_BINS:
            exact_cuts = label_boundaries(values, np.asarray(exact.labels))
            equal_cuts = label_boundaries(values, equal_frequency_labels(scores, n_bins))

    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.0), constrained_layout=True)

    axes[0].hist(values, bins=100, color="0.8", log=True)
    for index, cut in enumerate(exact_cuts):
        axes[0].axvline(
            cut,
            color="C0",
            linewidth=1.6,
            label="exact interval cuts" if index == 0 else None,
        )
    for index, cut in enumerate(equal_cuts):
        axes[0].axvline(
            cut,
            color="C2",
            linewidth=1.6,
            linestyle="--",
            ymax=0.55,
            label="equal-frequency cuts" if index == 0 else None,
        )
    axes[0].set_xlabel(f"score coordinate ({PANEL_BINS} cells)")
    axes[0].set_ylabel("events per bin")
    axes[0].legend(loc="upper center")

    axes[1].plot(BIN_COUNTS, exact_curve, marker="o", color="C0", label="exact interval program")
    axes[1].fill_between(
        BIN_COUNTS,
        lloyd_low,
        lloyd_high,
        color="C1",
        alpha=0.35,
        label="Lloyd, single restart (8 seeds)",
    )
    axes[1].plot(BIN_COUNTS, equal_curve, marker="s", color="C2", label="equal frequency")
    axes[1].set_xlabel("number of cells $K$")
    axes[1].set_ylabel("retained information")
    axes[1].set_ylim(0.4, 1.02)
    axes[1].legend(loc="lower right")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
