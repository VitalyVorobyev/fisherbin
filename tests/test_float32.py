from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np

import fisherbin


def test_float32_fit_and_soft_step() -> None:
    scores = jax.random.normal(jax.random.PRNGKey(5), (256, 3), dtype=jnp.float32)
    result = fisherbin.fit(
        scores,
        n_bins=5,
        config=fisherbin.SoftVoronoiConfig(
            n_init=1,
            kmeans_max_iter=20,
            max_steps=5,
            record_every=5,
        ),
    )
    assert result.centers.dtype == jnp.float32
    assert np.isfinite(result.train_report.geometric_mean_retention)
    assert result.train_report.psd_residual_min_eigenvalue >= -1e-3
