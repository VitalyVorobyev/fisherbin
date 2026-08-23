from __future__ import annotations

import json

import jax.numpy as jnp
import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import fisherbin


def test_hard_information_loss_identity_and_psd() -> None:
    scores = jnp.asarray([[-1.0, 0.2], [-0.8, 0.1], [0.7, 0.4], [1.2, 0.5]])
    weights = jnp.asarray([1.0, 2.0, 1.5, 0.5])
    labels = jnp.asarray([0, 0, 1, 1])
    full = fisherbin.fisher_information(scores, weights)
    binned = fisherbin.binned_fisher_information(scores, labels, weights, n_bins=2)
    residual = np.asarray(full - binned)
    assert np.linalg.eigvalsh(residual).min() >= -1e-6

    direct = np.zeros((2, 2))
    for bin_index in range(2):
        mask = np.asarray(labels) == bin_index
        mean = np.average(np.asarray(scores)[mask], axis=0, weights=np.asarray(weights)[mask])
        differences = np.asarray(scores)[mask] - mean
        direct += np.einsum("n,np,nq->pq", np.asarray(weights)[mask], differences, differences)
    np.testing.assert_allclose(residual, direct, rtol=1e-6, atol=1e-6)


def test_fractional_information_is_bounded() -> None:
    scores = jnp.asarray([[-1.0], [0.0], [1.0], [2.0]])
    responsibilities = jnp.asarray([[0.9, 0.1], [0.6, 0.4], [0.2, 0.8], [0.05, 0.95]])
    full = fisherbin.fisher_information(scores)
    soft = fisherbin.fractional_fisher_information(scores, responsibilities)
    assert float((full - soft)[0, 0]) >= -1e-6


@settings(max_examples=10, deadline=None)
@given(seed=st.integers(min_value=0, max_value=10_000))
def test_psd_loss_property_across_seeded_samples(seed: int) -> None:
    rng = np.random.default_rng(seed)
    scores = rng.normal(size=(30, 3))
    weights = rng.lognormal(size=30)
    labels = rng.integers(0, 5, size=30)
    full = fisherbin.fisher_information(scores, weights)
    binned = fisherbin.binned_fisher_information(scores, labels, weights, n_bins=5)
    scale = max(float(np.linalg.eigvalsh(np.asarray(full)).max()), 1.0)
    assert np.linalg.eigvalsh(np.asarray(full - binned)).min() >= -1e-5 * scale


def test_weight_splitting_and_global_scaling_preserve_normalized_report() -> None:
    scores = jnp.asarray([[-1.0], [0.5], [2.0]])
    weights = jnp.asarray([2.0, 1.0, 3.0])
    labels = jnp.asarray([0, 0, 1])
    report = fisherbin.information_report(scores, labels, weights, n_bins=2)

    split_scores = jnp.asarray([[-1.0], [-1.0], [0.5], [2.0]])
    split_weights = jnp.asarray([0.75, 1.25, 1.0, 3.0])
    split_labels = jnp.asarray([0, 0, 0, 1])
    split = fisherbin.information_report(split_scores, split_labels, split_weights, n_bins=2)
    scaled = fisherbin.information_report(scores, labels, weights * 11, n_bins=2)
    np.testing.assert_allclose(report.retained_matrix, split.retained_matrix, atol=1e-6)
    np.testing.assert_allclose(report.retained_matrix, scaled.retained_matrix, atol=1e-6)


def test_event_order_bin_relabeling_and_partition_limits() -> None:
    scores = jnp.asarray([[-2.0, 0.5], [-0.5, 1.0], [1.0, -0.2], [2.0, 0.7]])
    weights = jnp.asarray([1.0, 2.0, 0.5, 3.0])
    labels = jnp.asarray([0, 0, 1, 2])
    expected = fisherbin.binned_fisher_information(scores, labels, weights, n_bins=3)
    order = jnp.asarray([2, 0, 3, 1])
    reordered = fisherbin.binned_fisher_information(
        scores[order], labels[order], weights[order], n_bins=3
    )
    relabeled = fisherbin.binned_fisher_information(
        scores, jnp.asarray([2, 2, 0, 1]), weights, n_bins=3
    )
    np.testing.assert_allclose(expected, reordered, atol=1e-6)
    np.testing.assert_allclose(expected, relabeled, atol=1e-6)

    one_bin = fisherbin.binned_fisher_information(
        scores, jnp.zeros(4, dtype=jnp.int32), weights, n_bins=1
    )
    mean = np.average(np.asarray(scores), axis=0, weights=np.asarray(weights))
    np.testing.assert_allclose(one_bin, np.sum(np.asarray(weights)) * np.outer(mean, mean))
    unique = fisherbin.binned_fisher_information(scores, jnp.arange(4), weights, n_bins=4)
    np.testing.assert_allclose(unique, fisherbin.fisher_information(scores, weights), atol=1e-6)


def test_rank_projection_and_json_are_explicit() -> None:
    scores = jnp.asarray([[-1.0, -2.0], [0.0, 0.0], [1.0, 2.0]])
    result = fisherbin.fit(scores, n_bins=2)
    assert result.transform.rank == 1
    assert result.transform.dropped_directions == 1
    json.dumps(result.to_dict(), allow_nan=False)


def test_component_adapter() -> None:
    components = jnp.asarray([[1.0, 2.0], [3.0, 1.0]])
    coefficients = jnp.asarray([2.0, 0.5])
    expected = np.asarray(components) / (np.asarray(components) @ np.asarray(coefficients))[:, None]
    np.testing.assert_allclose(fisherbin.scores_from_components(components, coefficients), expected)
    with pytest.raises(ValueError, match="strictly positive"):
        fisherbin.scores_from_components(jnp.zeros((2, 2)), coefficients)


@pytest.mark.parametrize("bad_weights", [[1.0, -1.0], [0.0, 0.0], [1.0, np.nan]])
def test_invalid_weights_fail(bad_weights: list[float]) -> None:
    with pytest.raises(ValueError):
        fisherbin.fisher_information(jnp.asarray([[0.0], [1.0]]), bad_weights)
