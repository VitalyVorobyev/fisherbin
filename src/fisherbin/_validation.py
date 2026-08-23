"""Input validation shared by public entry points."""

from __future__ import annotations

from typing import Any

import jax.numpy as jnp
import numpy as np


def validate_scores_weights(
    scores: Any,
    weights: Any | None = None,
    *,
    expected_features: int | None = None,
) -> tuple[jnp.ndarray, jnp.ndarray]:
    """Validate and normalize score/weight inputs without normalizing weight scale."""

    score_array = jnp.asarray(scores)
    if score_array.ndim != 2:
        raise ValueError(f"scores must have shape [N, P], got {score_array.shape}")
    if score_array.shape[0] == 0 or score_array.shape[1] == 0:
        raise ValueError("scores must contain at least one observation and one parameter")
    if expected_features is not None and score_array.shape[1] != expected_features:
        raise ValueError(
            f"scores have {score_array.shape[1]} parameters, expected {expected_features}"
        )
    if not jnp.issubdtype(score_array.dtype, jnp.inexact):
        score_array = score_array.astype(jnp.float32)
    elif score_array.dtype in (jnp.float16, jnp.bfloat16):
        score_array = score_array.astype(jnp.float32)

    if weights is None:
        weight_array = jnp.ones(score_array.shape[0], dtype=score_array.dtype)
    else:
        weight_array = jnp.asarray(weights, dtype=score_array.dtype)
        if weight_array.shape != (score_array.shape[0],):
            raise ValueError(
                f"weights must have shape [{score_array.shape[0]}], got {weight_array.shape}"
            )

    # These conversions intentionally happen at the public validation boundary.
    if not bool(np.asarray(jnp.all(jnp.isfinite(score_array)))):
        raise ValueError("scores must be finite")
    if not bool(np.asarray(jnp.all(jnp.isfinite(weight_array)))):
        raise ValueError("weights must be finite")
    if bool(np.asarray(jnp.any(weight_array < 0))):
        raise ValueError("weights must be nonnegative; signed weights are not supported")
    if not bool(np.asarray(jnp.any(weight_array > 0))):
        raise ValueError("at least one weight must be positive")

    positive = weight_array > 0
    return score_array[positive], weight_array[positive]


def validate_n_bins(n_bins: int, n_observations: int) -> None:
    """Validate a requested hard partition size."""

    if isinstance(n_bins, bool) or not isinstance(n_bins, int):
        raise TypeError("n_bins must be an integer")
    if n_bins < 1:
        raise ValueError("n_bins must be at least one")
    if n_bins > n_observations:
        raise ValueError("n_bins cannot exceed the number of positive-weight observations")
