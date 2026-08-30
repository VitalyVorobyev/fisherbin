"""Render the naive-baseline comparison for chapter 14.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch14_baselines.py

The left panel scores five four-cell rules on four two-parameter score laws:
exact D exchange, whitened k-means, Euclidean k-means on raw score columns, a
rectangular two-by-two grid at the coordinate medians, and equal-frequency cuts
on the first score coordinate. The right panel isolates the one-dimensional
case, where equal frequency is a genuinely reasonable rule.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np

import scorequant as sq

OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch14_baselines.png"

N_BINS = 4
SCALAR_BUDGETS = (2, 4, 8, 16, 32)
METHODS = (
    "exact D exchange",
    "whitened k-means",
    "raw k-means",
    "rectangular grid",
    "equal frequency",
)


def retention(table: np.ndarray, labels: np.ndarray, n_bins: int) -> float:
    """Geometric mean retention of one labeling of one score table."""
    return float(sq.information_report(table, labels, n_bins=n_bins).geometric_mean_retention)


def rectangular_labels(table: np.ndarray, n_side: int) -> np.ndarray:
    """Label rows by a quantile grid on the raw score coordinates."""
    quantiles = np.linspace(0.0, 1.0, n_side + 1)[1:-1]
    index = [np.digitize(table[:, axis], np.quantile(table[:, axis], quantiles)) for axis in (0, 1)]
    return index[0] * n_side + index[1]


def equal_frequency_labels(column: np.ndarray, n_bins: int) -> np.ndarray:
    """Label rows by equal-frequency cuts on one coordinate."""
    quantiles = np.linspace(0.0, 1.0, n_bins + 1)[1:-1]
    return np.digitize(column, np.quantile(column, quantiles))


def score_laws() -> dict[str, np.ndarray]:
    """Build the four committed two-parameter score laws."""
    rng = np.random.default_rng(14)
    base = rng.normal(size=(3_000, 2))
    centres = np.array([[3.0, 0.2], [-1.0, 2.6], [-2.0, -2.4], [0.5, -0.4]])
    pick = rng.integers(0, 4, size=3_000)
    clustered = centres[pick] + rng.normal(scale=0.55, size=(3_000, 2))
    return {
        "balanced": base,
        "mismatched\nunits": np.stack([40.0 * base[:, 0], 0.05 * base[:, 1]], axis=1),
        "correlated": base @ np.array([[1.0, 0.0], [0.95, 0.31]]),
        "clustered": clustered - clustered.mean(axis=0),
    }


def evaluate(table: np.ndarray) -> list[float]:
    """Score every rule on one law, in the order of ``METHODS``."""
    exchange = sq.optimize_partition(table, n_bins=N_BINS, config=sq.DExchangeConfig(seed=0))
    whitened = sq.fit_quantizer(
        sq.ScoreSample(table),
        n_bins=N_BINS,
        criterion=sq.NormalizedTrace(),
        config=sq.KMeansConfig(seed=0, solver_restarts=8),
    )
    raw = sq.fit_quantizer(
        sq.ScoreSample(table),
        n_bins=N_BINS,
        criterion=sq.NormalizedTrace(),
        config=sq.KMeansConfig(seed=0, solver_restarts=8, whiten=False),
    )
    return [
        float(exchange.train_report.geometric_mean_retention),
        float(whitened.train_report.geometric_mean_retention),
        retention(table, np.asarray(raw.labels), N_BINS),
        retention(table, rectangular_labels(table, 2), 4),
        retention(table, equal_frequency_labels(table[:, 0], N_BINS), N_BINS),
    ]


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)

    laws = score_laws()
    values = np.array([evaluate(table) for table in laws.values()])
    print(np.round(values, 5))

    column = np.random.default_rng(2).normal(size=(4_000, 1))
    ratios = []
    for n_bins in SCALAR_BUDGETS:
        exact = sq.fit_quantizer(
            sq.ScoreSample(column),
            n_bins=n_bins,
            criterion=sq.DOptimality(),
            config=sq.ScalarDPConfig(),
        )
        frequency = retention(column, equal_frequency_labels(column[:, 0], n_bins), n_bins)
        ratios.append(frequency / float(exact.train_report.geometric_mean_retention))
    print(np.round(ratios, 5))

    figure, axes = plt.subplots(1, 2, figsize=(11.4, 4.4), constrained_layout=True)

    positions = np.arange(len(laws))
    width = 0.16
    for index, method in enumerate(METHODS):
        axes[0].bar(
            positions + (index - 2) * width,
            values[:, index],
            width=width,
            label=method,
            color=f"C{index}",
        )
    axes[0].set_xticks(positions, list(laws))
    axes[0].set_ylabel("geometric mean retention")
    axes[0].set_ylim(0.0, 1.05)
    axes[0].legend(loc="upper left", fontsize=8, ncols=2)
    axes[0].set_title("four cells, four score laws:\nwhen a naive rule is fine and when it is not")

    axes[1].axhline(1.0, color="0.35", linestyle="--", linewidth=1.1, label="exact interval rule")
    axes[1].plot(
        SCALAR_BUDGETS, ratios, marker="o", color="C4", linewidth=1.7, label="equal frequency"
    )
    axes[1].set_xscale("log", base=2)
    axes[1].set_xticks(list(SCALAR_BUDGETS), [str(budget) for budget in SCALAR_BUDGETS])
    axes[1].set_xticks([], [], minor=True)
    axes[1].set_ylim(0.955, 1.008)
    axes[1].set_xlabel("cells $K$")
    axes[1].set_ylabel("retention relative to the exact rule")
    axes[1].legend(loc="lower right", fontsize=9)
    axes[1].set_title("one dimension:\nequal frequency costs at most 2.5%")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
