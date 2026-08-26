"""Render the estimated-score quality figure for chapter 13.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch13_classifier_quality.py

A three-component mixture supplies an exactly computable score. Histogram
classifiers trained on nested samples of growing size supply estimates of it.
The left panel compares the worst and best estimated score coordinate with the
exact one; the right panel tracks what the resulting four-cell partitions report
and what they actually retain.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np

import scorequant as sq

OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch13_classifier_quality.png"

FRACTIONS = np.array([0.5, 0.3, 0.2])
MEANS = np.array([-1.6, 0.0, 1.9])
SIGMAS = np.array([0.8, 0.6, 0.9])
EDGES = np.linspace(-5.0, 5.0, 41)
TRAINING_SIZES = (200, 800, 3200, 12800, 51200)
N_BINS = 4


def component_densities(values: np.ndarray) -> np.ndarray:
    """Return the ``[N, 3]`` matrix of component densities at ``values``."""
    exponent = -0.5 * ((values[:, None] - MEANS) / SIGMAS) ** 2
    return np.exp(exponent) / (SIGMAS * np.sqrt(2.0 * np.pi))


def draw(n_rows: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Draw observations and their generating component index."""
    generator = np.random.default_rng(seed)
    component = generator.choice(3, size=n_rows, p=FRACTIONS)
    return generator.normal(MEANS[component], SIGMAS[component]), component


def exact_posteriors(values: np.ndarray) -> np.ndarray:
    """Return exact component posteriors under the reference fractions."""
    joint = FRACTIONS * component_densities(values)
    return joint / joint.sum(axis=1, keepdims=True)


def histogram_table(index: np.ndarray, component: np.ndarray, n_train: int) -> np.ndarray:
    """Build Laplace-smoothed per-bin class frequencies from the first rows."""
    counts = np.ones((len(EDGES) - 1, 3))
    np.add.at(counts, (index[:n_train], component[:n_train]), 1.0)
    return counts / counts.sum(axis=1, keepdims=True)


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)

    training, components = draw(TRAINING_SIZES[-1], 77)
    training_index = np.clip(np.digitize(training, EDGES) - 1, 0, len(EDGES) - 2)
    observations, _ = draw(4_000, 0)
    exact = np.asarray(
        sq.mixture_scores_from_ratios(
            sq.ratios_from_posteriors(exact_posteriors(observations), FRACTIONS), FRACTIONS
        )
    )
    reference = sq.optimize_partition(exact, n_bins=N_BINS, config=sq.DExchangeConfig(seed=0))
    best = float(reference.train_report.geometric_mean_retention)

    estimates, errors, reported, retained = {}, [], [], []
    for n_train in TRAINING_SIZES:
        table = histogram_table(training_index, components, n_train)
        posteriors = table[np.clip(np.digitize(observations, EDGES) - 1, 0, len(EDGES) - 2)]
        estimated = np.asarray(
            sq.mixture_scores_from_ratios(
                sq.ratios_from_posteriors(posteriors, FRACTIONS), FRACTIONS
            )
        )
        fitted = sq.optimize_partition(estimated, n_bins=N_BINS, config=sq.DExchangeConfig(seed=0))
        estimates[n_train] = estimated
        errors.append(float(np.sqrt(np.mean((estimated - exact) ** 2))))
        reported.append(float(fitted.train_report.geometric_mean_retention))
        delivered = sq.information_report(exact, fitted.labels, n_bins=N_BINS)
        retained.append(float(delivered.geometric_mean_retention))
    print(f"exact {best:.6f} reported {np.round(reported, 5)} retained {np.round(retained, 5)}")

    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), constrained_layout=True)

    span = np.array([-5.2, 2.7])
    axes[0].plot(span, span, color="0.35", linestyle="--", linewidth=1.1, label="exact score")
    for n_train, colour in ((TRAINING_SIZES[0], "C3"), (TRAINING_SIZES[-1], "C0")):
        axes[0].scatter(
            exact[:, 0],
            estimates[n_train][:, 0],
            s=6,
            alpha=0.35,
            color=colour,
            linewidths=0,
            label=f"{n_train:,} training events",
        )
    axes[0].set_xlim(-5.2, 2.7)
    axes[0].set_ylim(-5.2, 2.7)
    axes[0].set_aspect("equal")
    axes[0].set_xlabel("exact score $s_1$")
    axes[0].set_ylabel("estimated score $\\hat s_1$")
    axes[0].legend(loc="upper left", fontsize=9, markerscale=2.0)
    axes[0].set_title("what a classifier gets wrong,\nand how that shrinks")

    sizes = np.asarray(TRAINING_SIZES, dtype=float)
    axes[1].axhline(best, color="0.35", linestyle="--", linewidth=1.1, label="exact-score rule")
    axes[1].plot(sizes, reported, marker="^", color="C3", linewidth=1.6, label="reported retention")
    axes[1].plot(
        sizes, retained, marker="o", color="C0", linewidth=1.6, label="retention delivered"
    )
    axes[1].set_xscale("log")
    axes[1].set_xlabel("classifier training events")
    axes[1].set_ylabel("geometric mean retention")
    axes[1].set_ylim(0.79, 0.96)
    axes[1].legend(loc="lower right", fontsize=9)
    axes[1].set_title("the reported number is blind\nto the damage it is reporting on")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
