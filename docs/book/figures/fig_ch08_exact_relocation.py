"""Render the exact-relocation and Theorem-3 figure for chapter 8.

Run from anywhere::

    MPLBACKEND=Agg uv run python docs/book/figures/fig_ch08_exact_relocation.py

The left panel checks the closed determinant gain of a single-row relocation
against a full recomputation of the binned information, over every admissible
move of one configuration. The right panel checks the Theorem-3 lower bound
against the exact gain, over every admissible move that violates the current
Mahalanobis-Voronoi rule.

The script requests double precision from JAX so that the rendered figure is
byte-identical whatever the caller's floating-point configuration is.
"""

from __future__ import annotations

from pathlib import Path

import jax
import matplotlib.pyplot as plt
import numpy as np

import scorequant as sq

N_ROWS = 120
N_BINS = 4
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "fig_ch08_exact_relocation.png"


def whitened_configuration(seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Return whitened coordinates and a balanced labeling of one random table.

    Parameters
    ----------
    seed
        Generator seed.

    Returns
    -------
    tuple of numpy.ndarray
        Whitened coordinates with shape ``[N, 2]`` and integer labels ``[N]``.
    """
    rng = np.random.default_rng(seed)
    scores = rng.normal(size=(N_ROWS, 2)) @ np.array([[1.0, 0.45], [0.0, 1.25]])
    eigenvalues, basis = np.linalg.eigh(np.asarray(sq.fisher_information(scores)))
    coordinates = scores @ (basis / np.sqrt(eigenvalues))
    labels = np.asarray(
        sq.optimize_partition(scores, n_bins=N_BINS, config=sq.DExchangeConfig(seed=seed)).labels
    )
    # Scramble a slice so the configuration carries genuine Voronoi violations.
    labels = labels.copy()
    labels[::5] = (labels[::5] + 1) % N_BINS
    return coordinates, labels


def cell_moments(
    coordinates: np.ndarray, labels: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return cell masses, cell means, and the binned information of a labeling.

    Parameters
    ----------
    coordinates
        Whitened score coordinates with shape ``[N, R]``.
    labels
        Integer labels with shape ``[N]``.

    Returns
    -------
    tuple of numpy.ndarray
        Cell masses ``[B]``, cell means ``[B, R]``, and information ``[R, R]``.
    """
    mass = np.bincount(labels, minlength=N_BINS).astype(float)
    sums = np.zeros((N_BINS, coordinates.shape[1]))
    np.add.at(sums, labels, coordinates)
    means = sums / mass[:, None]
    return mass, means, np.einsum("b,bp,bq->pq", mass, means, means)


def main() -> None:
    """Build and save the figure."""
    jax.config.update("jax_enable_x64", True)

    lemma_gains, exact_gains = [], []
    bounds, violating_gains = [], []
    for seed in range(12):
        coordinates, labels = whitened_configuration(seed)
        mass, means, information = cell_moments(coordinates, labels)
        sign, base = np.linalg.slogdet(information)
        if sign <= 0:
            continue
        inverse = np.linalg.inv(information)

        for row in range(N_ROWS):
            source = int(labels[row])
            if mass[source] <= 1.0:
                continue
            source_residual = coordinates[row] - means[source]
            q_source = source_residual @ inverse @ source_residual
            for destination in range(N_BINS):
                if destination == source:
                    continue
                destination_residual = coordinates[row] - means[destination]
                q_destination = destination_residual @ inverse @ destination_residual
                q_cross = source_residual @ inverse @ destination_residual
                alpha = mass[source] / (mass[source] - 1.0)
                beta = mass[destination] / (mass[destination] + 1.0)
                ratio = (1.0 + alpha * q_source) * (1.0 - beta * q_destination)
                ratio += alpha * beta * q_cross**2
                if ratio <= 0:
                    continue

                moved = labels.copy()
                moved[row] = destination
                _, _, updated = cell_moments(coordinates, moved)
                moved_sign, moved_logdet = np.linalg.slogdet(updated)
                if moved_sign <= 0:
                    continue
                lemma_gains.append(float(np.log(ratio)))
                exact_gains.append(float(moved_logdet - base))

                if q_source >= q_destination:
                    separation = means[source] - means[destination]
                    q_delta = separation @ inverse @ separation
                    bounds.append(float(np.log1p(alpha * beta * q_delta**2 / 4.0)))
                    violating_gains.append(float(moved_logdet - base))

    lemma_gains = np.asarray(lemma_gains)
    exact_gains = np.asarray(exact_gains)
    bounds = np.asarray(bounds)
    violating_gains = np.asarray(violating_gains)
    residual = float(np.max(np.abs(lemma_gains - exact_gains)))
    slack = float(np.min(violating_gains - bounds))
    print(f"{lemma_gains.size} moves, largest lemma residual {residual:.3e} nat")
    print(f"{bounds.size} Voronoi-violating moves, smallest slack {slack:.4f} nat")

    figure, axes = plt.subplots(1, 2, figsize=(11.0, 4.6), constrained_layout=True)

    span = [float(exact_gains.min()), float(exact_gains.max())]
    axes[0].plot(span, span, color="0.5", linewidth=1.0, zorder=1)
    axes[0].scatter(lemma_gains, exact_gains, s=6, color="C0", alpha=0.35, linewidths=0, zorder=2)
    axes[0].set_xlabel("determinant-lemma gain (nat)")
    axes[0].set_ylabel("recomputed gain (nat)")
    axes[0].set_title(
        f"{lemma_gains.size} admissible moves\nlargest disagreement {residual:.1e} nat"
    )

    edge = [
        float(min(bounds.min(), violating_gains.min())),
        float(max(bounds.max(), violating_gains.max())),
    ]
    axes[1].plot(edge, edge, color="0.5", linewidth=1.0, zorder=1)
    axes[1].scatter(bounds, violating_gains, s=8, color="C3", alpha=0.4, linewidths=0, zorder=2)
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel(r"lower bound $\log(1+\alpha\beta q_\delta^2/4)$ (nat)")
    axes[1].set_ylabel("exact gain (nat)")
    axes[1].set_title(
        f"{bounds.size} Voronoi-violating moves\n"
        f"smallest slack {slack:.1e} nat, none below the line"
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    main()
