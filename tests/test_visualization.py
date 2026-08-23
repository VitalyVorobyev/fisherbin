from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import jax.numpy as jnp

import fisherbin


def test_all_visualizations_construct_figures() -> None:
    scores = jnp.linspace(-2, 2, 80)[:, None]
    result = fisherbin.fit_scores(
        scores,
        n_bins=4,
        config=fisherbin.KMeansConfig(n_init=2),
    )
    figures = [
        fisherbin.plot_optimization(result.trace),
        fisherbin.plot_partition(result, scores),
        fisherbin.plot_information(result.train_report),
        fisherbin.plot_summary(result, scores),
        result.plot_summary(scores),
    ]
    assert all(figure.axes for figure in figures)
