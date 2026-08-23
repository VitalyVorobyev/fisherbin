"""Adapters that produce FisherBin's canonical score representation."""

from __future__ import annotations

from typing import Any

import jax.numpy as jnp
import numpy as np


def scores_from_components(components: Any, coefficients: Any) -> jnp.ndarray:
    """Return scores for ``lambda(x) = sum_k coefficients[k] * components[:, k]``.

    Components and coefficients must be finite and nonnegative, and the total
    intensity must be strictly positive for every observation.
    """

    component_array = jnp.asarray(components)
    if component_array.ndim != 2 or min(component_array.shape) == 0:
        raise ValueError("components must have non-empty shape [N, P]")
    if not jnp.issubdtype(component_array.dtype, jnp.inexact):
        component_array = component_array.astype(jnp.float32)
    coefficient_array = jnp.asarray(coefficients, dtype=component_array.dtype)
    if coefficient_array.shape != (component_array.shape[1],):
        raise ValueError(
            f"coefficients must have shape [{component_array.shape[1]}], "
            f"got {coefficient_array.shape}"
        )
    if not bool(np.asarray(jnp.all(jnp.isfinite(component_array)))):
        raise ValueError("components must be finite")
    if not bool(np.asarray(jnp.all(jnp.isfinite(coefficient_array)))):
        raise ValueError("coefficients must be finite")
    if bool(np.asarray(jnp.any(component_array < 0))) or bool(
        np.asarray(jnp.any(coefficient_array < 0))
    ):
        raise ValueError("components and coefficients must be nonnegative")
    intensity = component_array @ coefficient_array
    if bool(np.asarray(jnp.any(intensity <= 0))):
        raise ValueError("total intensity must be strictly positive for every observation")
    return component_array / intensity[:, None]
