"""Render the three-doors figure for book chapter 4.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch04_three_doors.py

The model is Gaussian location at the reference point, whose score is the
identity. The left panel compares the exact score map against two
classifier-derived ones: a correctly declared classifier that recovers the score
exactly, and one whose training priors were misdeclared. The right panel shows
what that misdeclaration does to the two different numbers a result can report.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np

import scorequant as sq

DELTA = 0.5
TRUE_PRIORS = (0.4, 0.6)
BIN_COUNTS = (2, 3, 4)
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch04_three_doors.png"


def calibrated_probabilities(observations: np.ndarray) -> np.ndarray:
    """Return Bayes-optimal minus/plus probabilities under equal training priors.

    Parameters
    ----------
    observations
        Observation matrix with shape ``[N, 1]``.

    Returns
    -------
    numpy.ndarray
        Probability pairs with shape ``[N, 2]`` in ``(minus, plus)`` order.
    """
    values = np.asarray(observations)[:, 0]
    plus = 1.0 / (1.0 + np.exp(-2.0 * DELTA * values))
    return np.stack([1.0 - plus, plus], axis=1)


def imbalanced_probabilities(observations: np.ndarray) -> np.ndarray:
    """Return the same posteriors trained with unequal class priors.

    Parameters
    ----------
    observations
        Observation matrix with shape ``[N, 1]``.

    Returns
    -------
    numpy.ndarray
        Probability pairs with shape ``[N, 2]`` in ``(minus, plus)`` order.
    """
    values = np.asarray(observations)[:, 0]
    odds = np.exp(2.0 * DELTA * values) * (TRUE_PRIORS[1] / TRUE_PRIORS[0])
    plus = odds / (1.0 + odds)
    return np.stack([1.0 - plus, plus], axis=1)


def door_scores() -> tuple[sq.CentralLogRatioScore, sq.CentralLogRatioScore]:
    """Return the correctly declared and the misdeclared classifier providers.

    Returns
    -------
    tuple of scorequant.CentralLogRatioScore
        The provider that recovers the score and the one that does not.
    """
    return (
        sq.CentralLogRatioScore(calibrated_probabilities, [DELTA], [0.5, 0.5]),
        sq.CentralLogRatioScore(imbalanced_probabilities, [DELTA], [0.5, 0.5]),
    )


def retention_pair(
    observations: np.ndarray, provider: sq.CentralLogRatioScore, n_bins: int
) -> tuple[float, float]:
    """Return reported and true retention for one classifier provider.

    Parameters
    ----------
    observations
        Observation matrix with shape ``[N, 1]``; the exact score equals it.
    provider
        Classifier-derived score provider.
    n_bins
        Cell budget.

    Returns
    -------
    tuple of float
        Retention the fitted result reports from its own supplied scores, and
        retention of the exact score under the same labels.
    """
    estimated = np.asarray(provider.score(observations))
    result = sq.fit_quantizer(
        sq.ScoreSample(estimated),
        n_bins=n_bins,
        criterion=sq.DOptimality(),
        config=sq.ScalarDPConfig(),
    )
    reported = float(result.train_report.geometric_mean_retention)
    exact = sq.information_report(observations, result.labels, n_bins=n_bins)
    return reported, float(exact.geometric_mean_retention)


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)
    rng = np.random.default_rng(4)
    observations = rng.normal(size=(4_000, 1))
    calibrated, misdeclared = door_scores()

    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.0), constrained_layout=True)

    grid = np.linspace(-3.0, 3.0, 241)[:, None]
    axes[0].plot(grid[:, 0], grid[:, 0], color="C0", linewidth=3.0, label="exact score $s(x)=x$")
    axes[0].plot(
        grid[:, 0],
        np.asarray(calibrated.score(grid))[:, 0],
        color="C1",
        linestyle="--",
        label="classifier, priors declared",
    )
    axes[0].plot(
        grid[:, 0],
        np.asarray(misdeclared.score(grid))[:, 0],
        color="C3",
        linestyle=":",
        label="classifier, priors misdeclared",
    )
    axes[0].axhline(0.0, color="0.6", linewidth=0.8)
    axes[0].axvline(0.0, color="0.6", linewidth=0.8)
    axes[0].set_xlabel("observation $x$")
    axes[0].set_ylabel("score coordinate")
    axes[0].legend(loc="upper left")

    positions = np.arange(len(BIN_COUNTS), dtype=float)
    width = 0.26
    good = [retention_pair(observations, calibrated, k)[0] for k in BIN_COUNTS]
    reported = [retention_pair(observations, misdeclared, k)[0] for k in BIN_COUNTS]
    truth = [retention_pair(observations, misdeclared, k)[1] for k in BIN_COUNTS]
    axes[1].bar(positions - width, good, width, color="C1", label="declared: reported = true")
    axes[1].bar(positions, reported, width, color="C3", label="misdeclared: reported")
    axes[1].bar(
        positions + width,
        truth,
        width,
        color="C3",
        alpha=0.45,
        hatch="//",
        label="misdeclared: true",
    )
    axes[1].set_xticks(positions)
    axes[1].set_xticklabels([f"$K={count}$" for count in BIN_COUNTS])
    axes[1].set_ylabel("retained information")
    axes[1].set_ylim(0.0, 1.32)
    axes[1].legend(loc="upper left")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
