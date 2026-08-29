"""Private solver façade preserving established internal import paths."""

from __future__ import annotations

import numpy as np

from ._execution import xp as jnp
from .config import ScalarDPConfig
from .solvers import scalar as _scalar
from .solvers.common import QuantizerRun, chunked_hard_assign, hard_assign, squared_distances
from .solvers.kmeans import weighted_kmeans
from .solvers.soft import (
    criterion_objective_label,
    soft_objective_and_center_gradient,
    soft_responsibilities,
    soft_voronoi,
)

__all__ = [
    "QuantizerRun",
    "chunked_hard_assign",
    "criterion_objective_label",
    "hard_assign",
    "scalar_interval_dp",
    "scalar_weighted_kmeans_dp",
    "soft_objective_and_center_gradient",
    "soft_responsibilities",
    "soft_voronoi",
    "squared_distances",
    "weighted_kmeans",
]

# Compatibility for the established private test seam. New code imports the
# responsibility module directly; this façade keeps monkeypatched memory
# budgets observable until the private path is retired.
_DYNAMIC_WORKING_SET_BYTES = _scalar._DYNAMIC_WORKING_SET_BYTES


def scalar_interval_dp(
    values: np.ndarray,
    weights: np.ndarray,
    n_bins: int,
) -> tuple[np.ndarray, float]:
    """Delegate exact scalar DP through the compatibility memory budget."""
    _scalar._DYNAMIC_WORKING_SET_BYTES = _DYNAMIC_WORKING_SET_BYTES
    return _scalar.scalar_interval_dp(values, weights, n_bins)


def scalar_weighted_kmeans_dp(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    config: ScalarDPConfig,
) -> QuantizerRun:
    """Delegate the scalar quantizer through the responsibility module."""
    _scalar._DYNAMIC_WORKING_SET_BYTES = _DYNAMIC_WORKING_SET_BYTES
    return _scalar.scalar_weighted_kmeans_dp(points, weights, n_bins, config)
