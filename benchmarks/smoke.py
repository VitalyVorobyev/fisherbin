"""Moderate-scale allocation and compilation smoke benchmark; not a timing promise."""

from __future__ import annotations

import jax
import jax.numpy as jnp

import scorequant
from scorequant.quantizers import soft_responsibilities


def main() -> None:
    key = jax.random.PRNGKey(2026)
    scores = jax.random.normal(key, (100_000, 16))
    weights = jnp.ones(scores.shape[0])
    result = scorequant.fit_quantizer(
        scorequant.ScoreSample(scores, weights),
        n_bins=64,
        criterion=scorequant.NormalizedTrace(),
        config=scorequant.KMeansConfig(n_init=1, max_iter=2),
    )
    labels = result.predict_scores(scores)
    report = result.evaluate_scores(scores, weights)
    responsibilities = jax.jit(soft_responsibilities)(
        result.transform.apply(scores), result.centers, 0.1
    )
    jax.block_until_ready(responsibilities)
    print(labels.shape, report.geometric_mean_retention, responsibilities.shape)


if __name__ == "__main__":
    main()
