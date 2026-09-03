"""Private solver façade re-exporting the solver package's kernels."""

from __future__ import annotations

from .solvers.common import QuantizerRun, chunked_hard_assign, hard_assign, squared_distances
from .solvers.kmeans import weighted_kmeans
from .solvers.scalar import scalar_interval_dp, scalar_weighted_kmeans_dp
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
