"""Render the committed figure for the door2-mixture-densities documentation page.

Both the page and the shared logic here build a `LinearComponents` model on
top of `examples.synthetic_problems.signal_background_shape`. This script
regenerates `docs/examples/assets/door2-mixture-densities.png` deterministically.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

import scorequant as sq
from examples.synthetic_problems import SignalBackgroundProblem, signal_background_shape

ASSET_PATH = Path("docs/examples/assets/door2-mixture-densities.png")


def build_component_model(problem: SignalBackgroundProblem) -> sq.LinearComponents:
    """Wrap a `SignalBackgroundProblem`'s exact densities as `LinearComponents`.

    Parameters
    ----------
    problem
        A signal-fraction problem with exactly one background shape, as
        returned by `signal_background_shape`.

    Returns
    -------
    scorequant.LinearComponents
        A model whose components are `problem.signal_density` and
        `problem.background_densities[0]`, reachable through
        `LinearComponentScore`.
    """

    def signal_component(x: np.ndarray) -> np.ndarray:
        return problem.signal_density(np.asarray(x)[:, 0])

    def background_component(x: np.ndarray) -> np.ndarray:
        return problem.background_densities[0](np.asarray(x)[:, 0])

    return sq.LinearComponents(
        components={"signal": signal_component, "background": background_component},
        coefficients={
            "signal": float(problem.coefficients[0]),
            "background": float(problem.coefficients[1]),
        },
        variables=["x"],
    )


def make_figure() -> Figure:
    """Render the component densities and the fitted bin structure.

    Returns
    -------
    matplotlib.figure.Figure
        A two-panel figure: the signal and background densities, and the
        IntegrationSource-fitted quantizer's label as a function of x.
    """
    problem = signal_background_shape(background_rates=(2.5,), n_bins=6)
    model = build_component_model(problem)
    provider = sq.LinearComponentScore(model)

    source = sq.IntegrationSource(
        problem.bounds, density=problem.intensity, quadrature=sq.GaussLegendreConfig(order=64)
    )
    quantizer = sq.fit_quantizer(
        source,
        score=provider,
        n_bins=problem.n_bins,
        criterion=sq.DOptimality(),
        config=sq.DExchangeConfig(seed=50),
    )

    grid = np.linspace(0.0, 1.0, 800)[:, None]
    grid_scores = np.asarray(provider.score(grid))
    grid_labels = np.asarray(quantizer.predict_scores(grid_scores))

    figure, axes = plt.subplots(1, 2, figsize=(10, 3.6), constrained_layout=True)
    axes[0].plot(grid[:, 0], problem.signal_density(grid[:, 0]), label="signal shape")
    axes[0].plot(grid[:, 0], problem.background_densities[0](grid[:, 0]), label="background shape")
    axes[0].set(xlabel="x", ylabel="density", title="Component pdfs (Door 2)")
    axes[0].legend()

    axes[1].scatter(grid[:, 0], grid_labels, c=grid_labels, cmap="tab10", s=4)
    axes[1].set(
        xlabel="x",
        ylabel="hard-bin label",
        yticks=range(quantizer.n_bins),
        title="IntegrationSource-fitted quantizer",
    )
    return figure


def main() -> None:
    """Regenerate and save the committed door2 figure."""
    figure = make_figure()
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(ASSET_PATH, dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    main()
