"""Render the one-dimensional Gaussian-location figure for book chapter 2.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch02_gaussian_by_hand.py

Everything here is a closed-form population computation on the standard normal
score law: no sampling, no seeds, no solver. The left panel sweeps the single
threshold of a two-cell rule, the middle panel compares optimal against
equal-frequency edges for two to twelve cells, and the right panel shows the
high-resolution decay of the residual loss.
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

BIN_COUNTS = tuple(range(2, 13))
PANTER_DITE = float(np.sqrt(3.0) * np.pi / 2.0)
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch02_gaussian_by_hand.png"


def normal_pdf(x: np.ndarray) -> np.ndarray:
    """Return the standard normal density.

    Parameters
    ----------
    x
        Evaluation points.

    Returns
    -------
    numpy.ndarray
        Density values with the shape of ``x``.
    """
    values = np.asarray(x, dtype=float)
    return np.exp(-0.5 * values**2) / np.sqrt(2.0 * np.pi)


def normal_cdf(x: np.ndarray) -> np.ndarray:
    """Return the standard normal distribution function.

    Parameters
    ----------
    x
        Evaluation points.

    Returns
    -------
    numpy.ndarray
        Cumulative probabilities with the shape of ``x``.
    """
    values = np.asarray(x, dtype=float)
    return 0.5 * (1.0 + np.vectorize(math.erf)(values / math.sqrt(2.0)))


def retained_information(thresholds: np.ndarray) -> float:
    """Return the information a threshold rule keeps from the Gaussian score.

    Parameters
    ----------
    thresholds
        Sorted interior cut points with shape ``[K - 1]``.

    Returns
    -------
    float
        The between-cell second moment ``sum_b m_b^2 / W_b``. The unbinned
        information of this model is one, so the value is also the retained
        fraction.
    """
    edges = np.concatenate(([-np.inf], np.asarray(thresholds, dtype=float), [np.inf]))
    cell_weights = normal_cdf(edges[1:]) - normal_cdf(edges[:-1])
    cell_moments = normal_pdf(edges[:-1]) - normal_pdf(edges[1:])
    return float(np.sum(cell_moments**2 / cell_weights))


@lru_cache(maxsize=1)
def _quantile_grid() -> tuple[np.ndarray, np.ndarray]:
    """Return the dense grid and cumulative values used to invert the normal law."""
    grid = np.linspace(-8.0, 8.0, 200_001)
    return grid, normal_cdf(grid)


def equal_frequency_thresholds(n_bins: int) -> np.ndarray:
    """Return the cut points that give every cell the same probability.

    Parameters
    ----------
    n_bins
        Number of cells.

    Returns
    -------
    numpy.ndarray
        Interior cut points with shape ``[n_bins - 1]``.
    """
    grid, cdf = _quantile_grid()
    return np.interp(np.arange(1, n_bins) / n_bins, cdf, grid)


def optimal_thresholds(n_bins: int, iterations: int = 2_000) -> np.ndarray:
    """Return the population-optimal cut points by midpoint fixed-point iteration.

    Each cut point is repeatedly moved to the midpoint of the conditional score
    means of the two cells it separates, which is the stationarity condition of
    a rank-one score law.

    Parameters
    ----------
    n_bins
        Number of cells.
    iterations
        Number of fixed-point sweeps.

    Returns
    -------
    numpy.ndarray
        Interior cut points with shape ``[n_bins - 1]``.
    """
    thresholds = equal_frequency_thresholds(n_bins)
    for _ in range(iterations):
        edges = np.concatenate(([-np.inf], thresholds, [np.inf]))
        cell_weights = normal_cdf(edges[1:]) - normal_cdf(edges[:-1])
        cell_means = (normal_pdf(edges[:-1]) - normal_pdf(edges[1:])) / cell_weights
        thresholds = 0.5 * (cell_means[:-1] + cell_means[1:])
    return thresholds


def main() -> None:
    """Build and save the figure."""
    figure, axes = plt.subplots(1, 3, figsize=(13.5, 4.0), constrained_layout=True)

    grid = np.linspace(-2.5, 2.5, 501)
    sweep = np.array([retained_information(np.array([t])) for t in grid])
    axes[0].plot(grid, sweep, color="C0")
    axes[0].axhline(2.0 / np.pi, color="C3", linestyle="--", linewidth=1.0)
    axes[0].plot([0.0], [2.0 / np.pi], marker="o", color="C3")
    axes[0].annotate(
        r"$2/\pi$",
        xy=(0.0, 2.0 / np.pi),
        xytext=(0.55, 0.60),
        color="C3",
    )
    axes[0].set_xlabel(r"threshold $t$ of the two-cell rule")
    axes[0].set_ylabel("retained information")
    axes[0].set_ylim(0.0, 0.72)

    optimal = np.array([retained_information(optimal_thresholds(k)) for k in BIN_COUNTS])
    equal = np.array([retained_information(equal_frequency_thresholds(k)) for k in BIN_COUNTS])
    axes[1].plot(BIN_COUNTS, optimal, marker="o", color="C0", label="optimal edges")
    axes[1].plot(BIN_COUNTS, equal, marker="s", color="C2", label="equal-frequency edges")
    axes[1].axhline(1.0, color="0.5", linewidth=0.8, linestyle=":")
    axes[1].set_xlabel("number of cells $K$")
    axes[1].set_ylabel("retained information")
    axes[1].set_ylim(0.6, 1.02)
    axes[1].legend(loc="lower right")

    counts = np.asarray(BIN_COUNTS, dtype=float)
    axes[2].loglog(counts, 1.0 - optimal, marker="o", color="C0", label="optimal edges")
    axes[2].loglog(counts, 1.0 - equal, marker="s", color="C2", label="equal-frequency edges")
    axes[2].loglog(
        counts,
        PANTER_DITE / counts**2,
        color="C3",
        linestyle="--",
        label=r"$(\sqrt{3}\pi/2)\,K^{-2}$",
    )
    ticks = (2, 3, 4, 6, 8, 12)
    axes[2].set_xticks(list(ticks))
    axes[2].set_xticklabels([str(count) for count in ticks])
    axes[2].set_xticks([], minor=True)
    axes[2].set_xlabel("number of cells $K$")
    axes[2].set_ylabel("information lost, $1 - $ retained")
    axes[2].legend(loc="lower left")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
