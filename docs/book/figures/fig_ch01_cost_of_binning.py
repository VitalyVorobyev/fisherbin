"""Render the cost-of-binning figure for book chapter 1.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch01_cost_of_binning.py

The left panel measures how much Fisher information a Gaussian location sample
keeps after equal-width binning, together with the standard-error inflation that
loss implies. The right panel shows the same statement as two sampling
distributions: the unbinned sample mean against the estimator that sees only a
single yes/no count.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

import math
from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np

import scorequant as sq

BIN_COUNTS = (2, 4, 8, 16, 32)
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch01_cost_of_binning.png"


def inverse_normal_cdf(probabilities: np.ndarray) -> np.ndarray:
    """Invert the standard normal distribution function on a dense grid.

    Parameters
    ----------
    probabilities
        Probabilities in ``(0, 1)``.

    Returns
    -------
    numpy.ndarray
        Quantiles with the shape of ``probabilities``.
    """
    grid = np.linspace(-8.0, 8.0, 200_001)
    cdf = 0.5 * (1.0 + np.vectorize(math.erf)(grid / math.sqrt(2.0)))
    return np.interp(probabilities, cdf, grid)


def equal_width_labels(values: np.ndarray, n_bins: int, span: float = 4.0) -> np.ndarray:
    """Return equal-width bin labels on ``[-span, span]`` with open end cells.

    Parameters
    ----------
    values
        Scalar score coordinates with shape ``[N]``.
    n_bins
        Number of equal-width cells.
    span
        Half-width of the interior grid; the two outer cells are unbounded.

    Returns
    -------
    numpy.ndarray
        Integer labels with shape ``[N]``.
    """
    edges = np.linspace(-span, span, n_bins + 1)[1:-1]
    return np.digitize(values, edges)


def retention_curve(scores: np.ndarray) -> np.ndarray:
    """Return retained-information fractions for every entry of ``BIN_COUNTS``.

    Parameters
    ----------
    scores
        Score matrix with shape ``[N, 1]``.

    Returns
    -------
    numpy.ndarray
        Retained-information fractions with shape ``[len(BIN_COUNTS)]``.
    """
    values = []
    for n_bins in BIN_COUNTS:
        labels = equal_width_labels(scores[:, 0], n_bins)
        report = sq.information_report(scores, labels, n_bins=n_bins)
        values.append(float(report.geometric_mean_retention))
    return np.asarray(values)


def sampling_distributions(
    rng: np.random.Generator, n_events: int, n_replicates: int
) -> tuple[np.ndarray, np.ndarray]:
    """Return unbinned and two-bin estimates of a Gaussian location parameter.

    Parameters
    ----------
    rng
        Seeded generator.
    n_events
        Events per replicate.
    n_replicates
        Number of independent replicates.

    Returns
    -------
    tuple of numpy.ndarray
        Sample means and sign-count estimates, each with shape
        ``[n_replicates]``.
    """
    draws = rng.normal(size=(n_replicates, n_events))
    unbinned = draws.mean(axis=1)
    fraction = (draws > 0.0).mean(axis=1)
    binned = inverse_normal_cdf(np.clip(fraction, 1e-6, 1 - 1e-6))
    return unbinned, binned


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)
    rng = np.random.default_rng(0)
    scores = rng.normal(size=(20_000, 1))
    retention = retention_curve(scores)
    unbinned, binned = sampling_distributions(rng, n_events=2_000, n_replicates=20_000)

    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4.0), constrained_layout=True)

    axes[0].plot(BIN_COUNTS, retention, marker="o", color="C0")
    axes[0].axhline(1.0, color="0.5", linewidth=0.8, linestyle=":")
    axes[0].set_xscale("log", base=2)
    axes[0].set_xticks(BIN_COUNTS)
    axes[0].set_xticklabels([str(count) for count in BIN_COUNTS])
    axes[0].set_xlabel("equal-width bins")
    axes[0].set_ylabel("fraction of Fisher information kept", color="C0")
    axes[0].tick_params(axis="y", colors="C0")
    axes[0].set_ylim(0.55, 1.05)
    inflation = axes[0].twinx()
    inflation.plot(BIN_COUNTS, 1.0 / np.sqrt(retention), marker="s", color="C3")
    inflation.set_ylabel("standard-error inflation", color="C3")
    inflation.tick_params(axis="y", colors="C3")

    edges = np.linspace(-0.11, 0.11, 45)
    axes[1].hist(
        unbinned,
        bins=edges,
        density=True,
        histtype="stepfilled",
        alpha=0.55,
        color="C0",
        label="unbinned sample mean",
    )
    axes[1].hist(
        binned,
        bins=edges,
        density=True,
        histtype="stepfilled",
        alpha=0.55,
        color="C3",
        label="one two-bin count",
    )
    axes[1].axvline(0.0, color="0.3", linewidth=0.8)
    axes[1].set_xlabel(r"estimate of $\theta$ (truth $\theta = 0$)")
    axes[1].set_ylabel("density")
    axes[1].legend(loc="upper right")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
