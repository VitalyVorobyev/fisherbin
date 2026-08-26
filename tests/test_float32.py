from __future__ import annotations

import jax
import jax.numpy as jnp
import numpy as np

import scorequant
from tests._fit import fit_test_quantizer


def test_float32_fit_and_soft_step() -> None:
    scores = jax.random.normal(jax.random.PRNGKey(5), (256, 3), dtype=jnp.float32)
    result = fit_test_quantizer(
        scores,
        n_bins=5,
        config=scorequant.SoftVoronoiConfig(
            n_init=1,
            kmeans_max_iter=20,
            max_steps=5,
            record_every=5,
        ),
    )
    assert result.centers.dtype == jnp.float32
    assert np.isfinite(result.train_report.geometric_mean_retention)
    assert result.train_report.psd_residual_min_eigenvalue >= -1e-3


def test_float32_ratio_algebra_promotes_low_precision() -> None:
    posteriors = jnp.asarray(
        [[0.5, 0.25, 0.25], [0.125, 0.375, 0.5]],
        dtype=jnp.float16,
    )
    ratios = scorequant.ratios_from_posteriors(posteriors, [0.5, 0.25, 0.25])
    scores = scorequant.mixture_scores_from_ratios(ratios, [0.25, 0.25, 0.5])
    assert ratios.dtype == jnp.float32
    assert scores.dtype == jnp.float32
    assert np.isfinite(np.asarray(scores)).all()
