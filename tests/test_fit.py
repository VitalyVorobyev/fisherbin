from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np
import pytest

import fisherbin


def _scores(n: int = 400) -> jnp.ndarray:
    first = jax.random.normal(jax.random.PRNGKey(1), (n // 2, 2)) * 0.25 - 1
    second = jax.random.normal(jax.random.PRNGKey(2), (n - n // 2, 2)) * 0.25 + 1
    return jnp.concatenate([first, second])


def test_kmeans_fit_predict_evaluate_and_monotonic_trace() -> None:
    scores = _scores()
    result = fisherbin.fit(
        scores,
        n_bins=4,
        config=fisherbin.KMeansConfig(seed=4, n_init=3, max_iter=40),
    )
    assert result.predict(scores).shape == (scores.shape[0],)
    assert result.evaluate(scores).geometric_mean_retention > 0.7
    objective = np.asarray(result.trace.objective)
    assert np.all(np.diff(objective) <= 1e-5)
    assert result.train_report.psd_residual_min_eigenvalue >= -1e-4


def test_zero_weights_are_ignored_but_rows_remain_predictable() -> None:
    scores = jnp.asarray([[-2.0], [-1.0], [1.0], [2.0], [100.0]])
    weights = jnp.asarray([1.0, 1.0, 1.0, 1.0, 0.0])
    result = fisherbin.fit(
        scores,
        weights=weights,
        n_bins=2,
        config=fisherbin.KMeansConfig(n_init=2),
    )
    assert result.predict(scores).shape == (5,)
    assert int(np.asarray(result.train_report.bin_counts).sum()) == 4


def test_validation_is_diagnostic_only() -> None:
    scores = _scores()
    config = fisherbin.KMeansConfig(seed=9, n_init=2)
    without = fisherbin.fit(scores, n_bins=3, config=config)
    with_validation = fisherbin.fit(
        scores,
        n_bins=3,
        config=config,
        validation_scores=scores[::-1],
    )
    np.testing.assert_allclose(without.centers, with_validation.centers)
    assert with_validation.validation_report is not None
    assert with_validation.trace.validation_hard_retention is not None


def test_same_seed_reproduces_centers_and_trace() -> None:
    scores = _scores(240)
    config = fisherbin.KMeansConfig(seed=17, n_init=3)
    first = fisherbin.fit(scores, n_bins=5, config=config)
    second = fisherbin.fit(scores, n_bins=5, config=config)
    np.testing.assert_allclose(first.centers, second.centers)
    np.testing.assert_allclose(first.trace.objective, second.trace.objective)


def test_soft_voronoi_has_finite_trace_and_hard_result() -> None:
    scores = _scores(240)
    result = fisherbin.fit(
        scores,
        n_bins=3,
        config=fisherbin.SoftVoronoiConfig(
            seed=3,
            n_init=2,
            kmeans_max_iter=30,
            max_steps=30,
            record_every=5,
        ),
    )
    assert np.isfinite(np.asarray(result.trace.objective)).all()
    assert np.isfinite(np.asarray(result.trace.gradient_norms)).all()
    assert np.isfinite(np.asarray(result.trace.soft_retention)).all()
    assert result.train_report.geometric_mean_retention > 0.55


def test_soft_requires_enough_bins_for_rank() -> None:
    with pytest.raises(ValueError, match="n_bins >="):
        fisherbin.fit(
            _scores(100),
            n_bins=1,
            config=fisherbin.SoftVoronoiConfig(max_steps=2),
        )


def test_whitened_partition_is_parameter_reparameterization_invariant() -> None:
    scores = _scores(300)
    change = jnp.asarray([[2.0, 0.3], [-0.4, 1.3]])
    transformed_scores = scores @ jnp.linalg.inv(change)
    config = fisherbin.KMeansConfig(seed=11, n_init=4)
    original = np.asarray(fisherbin.fit(scores, n_bins=4, config=config).predict(scores))
    transformed_result = fisherbin.fit(transformed_scores, n_bins=4, config=config)
    changed = np.asarray(transformed_result.predict(transformed_scores))
    np.testing.assert_array_equal(
        original[:, None] == original[None, :], changed[:, None] == changed[None, :]
    )


def test_too_many_distinct_bins_fails() -> None:
    with pytest.raises(ValueError, match="distinct"):
        fisherbin.fit(jnp.asarray([[0.0], [0.0], [1.0]]), n_bins=3)
