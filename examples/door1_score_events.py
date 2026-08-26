"""Render the committed figure for the door1-score-events documentation page.

The page and its matching notebook both build the same Gaussian-location
`ScoreSample`; this script exists only to regenerate
`docs/examples/assets/door1-score-events.png` deterministically.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

import scorequant as sq
from examples.synthetic_problems import gaussian_location

ASSET_PATH = Path("docs/examples/assets/door1-score-events.png")


def make_figure() -> Figure:
    """Render the training histogram and the compiled test-set partition.

    Returns
    -------
    matplotlib.figure.Figure
        A two-panel figure: the training score histogram, and the held-out
        test observations colored by their compiled hard-bin label.
    """
    problem = gaussian_location()
    train, test = problem.train, problem.test

    partition = sq.optimize_partition(
        train.scores,
        weights=train.weights,
        n_bins=4,
        criterion=sq.DOptimality(),
        config=sq.DExchangeConfig(seed=12),
        provenance=sq.ScoreProvenance(kind="exact", reference_point=(0.0,)),
    )
    quantizer = partition.compile_quantizer()
    test_labels = np.asarray(quantizer.predict_scores(test.scores))

    figure, axes = plt.subplots(1, 2, figsize=(10, 3.6), constrained_layout=True)
    axes[0].hist(np.asarray(train.observations[:, 0]), bins=40, density=True, alpha=0.75)
    axes[0].set(
        xlabel="measurement x = score s(x)",
        ylabel="density",
        title="Training events (Door 1: precomputed scores)",
    )

    order = np.argsort(np.asarray(test.observations[:, 0]))
    x = np.asarray(test.observations[order, 0])
    axes[1].scatter(x, test_labels[order], c=test_labels[order], cmap="tab10", s=5)
    axes[1].set(
        xlabel="measurement x",
        ylabel="compiled hard-bin label",
        yticks=range(quantizer.n_bins),
        title="compile_quantizer() applied to held-out events",
    )
    return figure


def main() -> None:
    """Regenerate and save the committed door1 figure."""
    figure = make_figure()
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(ASSET_PATH, dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    main()
