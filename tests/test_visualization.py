from __future__ import annotations

import matplotlib
import numpy as np

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
    assert figures[2].axes[0].images[0].get_clim() == (-1.0, 1.0)
    assert figures[3].axes[1].images[0].get_clim() == (-1.0, 1.0)
    for figure in figures:
        figure.clf()


def test_retained_information_plot_preserves_negative_matrix_entries() -> None:
    scores = jnp.asarray([[-1.0, 1.0], [0.0, 0.2], [1.0, -1.0], [2.0, 0.5]])
    labels = jnp.asarray([0, 0, 1, 1])
    report = fisherbin.information_report(scores, labels, n_bins=2)
    assert np.asarray(report.retained_matrix).min() < 0
    figure = fisherbin.plot_information(report)
    image = figure.axes[0].images[0]
    assert image.get_cmap().name == "coolwarm"
    assert image.get_clim() == (-1.0, 1.0)
    figure.clf()
