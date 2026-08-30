"""Input validation shared by public entry points."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ._execution import apply_precision, use_execution
from ._execution import xp as jnp
from ._typing import ArrayLike
from .config import ExecutionConfig

# ``None`` means automatic: below this many effective rows, collapsing pays
# for itself because its O(N log N) sort is negligible next to the O(N)
# exchange scan it speeds up by merging repeated score atoms; above it the
# up-front sort is skipped by default so a huge sample is not forced to pay
# for a benefit it may not need.
_AUTO_COLLAPSE_MAX_ROWS = 100_000


def promote_low_precision(array: jnp.ndarray) -> jnp.ndarray:
    """Promote a non-float, float16, or bfloat16 array to float32.

    ScoreQuant's numerical kernels assume at least float32 precision. This
    conversion happens once, at a public validation boundary, never inside a
    JIT-compiled hot path.
    """
    return apply_precision(array)


def resolve_collapse_duplicates(collapse_duplicates: bool | None, n_rows: int) -> bool:
    """Resolve the auto/opt-out duplicate-score-collapsing policy.

    ``None`` (the config default) collapses below ``_AUTO_COLLAPSE_MAX_ROWS``
    effective rows and skips it above; an explicit ``True``/``False`` always
    wins.
    """
    if collapse_duplicates is None:
        return n_rows <= _AUTO_COLLAPSE_MAX_ROWS
    return collapse_duplicates


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
    score_array = promote_low_precision(score_array)

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


def canonical_sample(
    scores: ArrayLike,
    weights: ArrayLike | None = None,
    *,
    expected_features: int | None = None,
) -> _ValidatedSample:
    """Validate a public sample without requiring an optional execution backend."""
    with use_execution(ExecutionConfig(backend="numpy")):
        return validate_sample(scores, weights, expected_features=expected_features)


def validate_n_bins(n_bins: int, n_observations: int) -> None:
    """Validate a requested hard partition size."""
    if isinstance(n_bins, bool) or not isinstance(n_bins, int):
        raise TypeError("n_bins must be an integer")
    if n_bins < 1:
        raise ValueError("n_bins must be at least one")
    if n_bins > n_observations:
        raise ValueError("n_bins cannot exceed the number of positive-weight observations")


def collapse_duplicate_scores(
    scores: jnp.ndarray, weights: jnp.ndarray
) -> tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """Merge identical score atoms and return their inverse row mapping."""
    unique, inverse = np.unique(np.asarray(scores), axis=0, return_inverse=True)
    collapsed_weights = np.bincount(inverse, weights=np.asarray(weights), minlength=len(unique))
    return (
        jnp.asarray(unique, dtype=scores.dtype),
        jnp.asarray(collapsed_weights, dtype=weights.dtype),
        jnp.asarray(inverse),
    )
