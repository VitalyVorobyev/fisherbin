from __future__ import annotations

import numpy as np
import pytest

import scorequant as sq
from examples.baselines import (
    equal_frequency_1d,
    euclidean_kmeans_scores,
    rectangular_observation_bins,
)
from examples.synthetic_problems import gaussian_location, spatial_sources


def test_rectangular_observation_bins_drops_and_renumbers_empty_cells() -> None:
    # Two far-apart clusters span a requested five-cell grid along axis 1, so
    # the three middle cells are empty and the surviving two renumber to 0/1.
    axis0 = np.zeros(40)
    axis1 = np.concatenate([np.zeros(20), np.full(20, 10.0)])
    observations = np.column_stack([axis0, axis1])
    labels = rectangular_observation_bins(observations, n_bins_per_axis=(1, 5))
    assert labels.shape == (40,)
    assert set(np.unique(labels).tolist()) == {0, 1}


def test_rectangular_observation_bins_axis_counts_and_budget_agree() -> None:
    rng = np.random.default_rng(0)
    observations = rng.uniform(-1, 1, size=(500, 2))
    per_axis = rectangular_observation_bins(observations, n_bins_per_axis=(4, 4))
    budget = rectangular_observation_bins(observations, total_budget=16)
    assert len(np.unique(per_axis)) <= 16
    assert len(np.unique(budget)) <= 16


def test_rectangular_observation_bins_is_deterministic() -> None:
    rng = np.random.default_rng(1)
    observations = rng.normal(size=(200, 3))
    first = rectangular_observation_bins(observations, n_bins_per_axis=3)
    second = rectangular_observation_bins(observations, n_bins_per_axis=3)
    np.testing.assert_array_equal(first, second)


def test_rectangular_observation_bins_rejects_ambiguous_or_bad_arguments() -> None:
    observations = np.zeros((5, 2))
    with pytest.raises(ValueError):
        rectangular_observation_bins(observations)
    with pytest.raises(ValueError):
        rectangular_observation_bins(observations, n_bins_per_axis=2, total_budget=4)
    with pytest.raises(ValueError):
        rectangular_observation_bins(observations, n_bins_per_axis=(2, 2, 2))
    with pytest.raises(ValueError):
        rectangular_observation_bins(observations, n_bins_per_axis=0)


def test_euclidean_kmeans_scores_is_deterministic_and_bounded() -> None:
    rng = np.random.default_rng(2)
    scores = rng.normal(size=(300, 2))
    first = euclidean_kmeans_scores(scores, n_bins=6, seed=7)
    second = euclidean_kmeans_scores(scores, n_bins=6, seed=7)
    np.testing.assert_array_equal(first, second)
    assert first.shape == (300,)
    assert first.min() >= 0
    assert first.max() < 6


def test_euclidean_kmeans_scores_rejects_bad_arguments() -> None:
    with pytest.raises(ValueError):
        euclidean_kmeans_scores(np.zeros((0, 2)), n_bins=2)
    with pytest.raises(ValueError):
        euclidean_kmeans_scores(np.zeros((5, 2)), n_bins=0)


def test_equal_frequency_1d_masses_are_within_one_row() -> None:
    rng = np.random.default_rng(3)
    values = rng.normal(size=997)
    labels = equal_frequency_1d(values, n_bins=10)
    counts = np.bincount(labels)
    assert counts.max() - counts.min() <= 1
    assert len(counts) <= 10


def test_equal_frequency_1d_is_deterministic() -> None:
    rng = np.random.default_rng(4)
    values = rng.uniform(size=250)
    first = equal_frequency_1d(values, n_bins=5)
    second = equal_frequency_1d(values, n_bins=5)
    np.testing.assert_array_equal(first, second)


def test_equal_frequency_1d_rejects_bad_arguments() -> None:
    with pytest.raises(ValueError):
        equal_frequency_1d(np.zeros(0), n_bins=2)
    with pytest.raises(ValueError):
        equal_frequency_1d(np.zeros(5), n_bins=0)
    with pytest.raises(ValueError):
        equal_frequency_1d(np.array([1.0, np.nan, 2.0]), n_bins=2)


def test_baseline_retention_is_computable_on_a_toy_problem() -> None:
    """Every baseline's labels feed straight into `scorequant.information_report`."""
    problem = gaussian_location(sizes=(400, 200, 800))
    values = problem.test.observations[:, 0]

    grid_labels = rectangular_observation_bins(problem.test.observations, n_bins_per_axis=4)
    kmeans_labels = euclidean_kmeans_scores(problem.test.scores, n_bins=4, seed=0)
    quantile_labels = equal_frequency_1d(values, n_bins=4)

    for labels in (grid_labels, kmeans_labels, quantile_labels):
        report = sq.information_report(
            problem.test.scores, labels, problem.test.weights, n_bins=int(labels.max()) + 1
        )
        assert np.isfinite(report.geometric_mean_retention)
        assert 0.0 <= report.geometric_mean_retention <= 1.0 + 1e-9


def test_rectangular_observation_bins_on_two_dimensional_problem() -> None:
    problem = spatial_sources(sizes=(300, 200, 600))
    labels = rectangular_observation_bins(problem.test.observations, total_budget=problem.n_bins)
    report = sq.information_report(
        problem.test.scores, labels, problem.test.weights, n_bins=int(labels.max()) + 1
    )
    assert np.isfinite(report.geometric_mean_retention)
