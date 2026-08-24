"""Input validation shared by public entry points."""

from __future__ import annotations

from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np

from ._typing import ArrayLike


@dataclass(frozen=True, slots=True)
class _ValidatedSample:
    """Validated score rows with their original and effective weight views."""

    scores: jnp.ndarray
    weights: jnp.ndarray
    positive_weight_mask: jnp.ndarray

    @property
    def effective_scores(self) -> jnp.ndarray:
        """Return score rows that contribute positive measure."""
        return self.scores[self.positive_weight_mask]

    @property
    def effective_weights(self) -> jnp.ndarray:
        """Return strictly positive weights aligned with effective scores."""
        return self.weights[self.positive_weight_mask]

    @property
    def n_effective(self) -> int:
        """Return the number of positive-weight observations."""
        return int(self.effective_scores.shape[0])


def validate_sample(
    scores: ArrayLike,
    weights: ArrayLike | None = None,
    *,
    expected_features: int | None = None,
) -> _ValidatedSample:
    """Validate scores and weights without normalizing their measure scale."""
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
    return _ValidatedSample(
        scores=score_array,
        weights=weight_array,
        positive_weight_mask=positive,
    )


def validate_n_bins(n_bins: int, n_observations: int) -> None:
    """Validate a requested hard partition size."""
    if isinstance(n_bins, bool) or not isinstance(n_bins, int):
        raise TypeError("n_bins must be an integer")
    if n_bins < 1:
        raise ValueError("n_bins must be at least one")
    if n_bins > n_observations:
        raise ValueError("n_bins cannot exceed the number of positive-weight observations")
