"""Immutable public result and diagnostic objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import jax.numpy as jnp

from ._json import json_ready
from .config import FitConfig
from .transforms import FisherTransform

if TYPE_CHECKING:
    from matplotlib.figure import Figure


@dataclass(frozen=True, slots=True)
class InformationReport:
    """Fisher retention and per-bin diagnostics for one evaluated sample."""

    fisher_unbinned: jnp.ndarray
    fisher_binned: jnp.ndarray
    retained_matrix: jnp.ndarray
    retained_eigenvalues: jnp.ndarray
    arithmetic_mean_retention: float
    geometric_mean_retention: float
    logdet_retention: float
    bin_weights: jnp.ndarray
    bin_counts: jnp.ndarray
    bin_effective_sample_sizes: jnp.ndarray
    effective_rank: int
    rank_threshold: float
    psd_residual_min_eigenvalue: float

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""

        return json_ready(self)


@dataclass(frozen=True, slots=True)
class OptimizationTrace:
    """Aggregate optimization history; never stores per-observation assignments."""

    steps: jnp.ndarray
    centers: jnp.ndarray
    objective: jnp.ndarray
    bin_weights: jnp.ndarray
    train_hard_retention: jnp.ndarray
    validation_hard_retention: jnp.ndarray | None = None
    soft_retention: jnp.ndarray | None = None
    temperatures: jnp.ndarray | None = None
    gradient_norms: jnp.ndarray | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""

        return json_ready(self)


@dataclass(frozen=True, slots=True)
class FitResult:
    """A fitted hard score-space partition and its diagnostics."""

    centers: jnp.ndarray
    transform: FisherTransform
    config: FitConfig
    trace: OptimizationTrace
    train_report: InformationReport
    validation_report: InformationReport | None = None

    @property
    def n_bins(self) -> int:
        return int(self.centers.shape[0])

    def predict(self, scores: Any) -> jnp.ndarray:
        """Assign new raw score vectors to their nearest fitted center."""

        coordinates = self.transform.apply(scores)
        distances = jnp.sum((coordinates[:, None, :] - self.centers[None, :, :]) ** 2, axis=2)
        return jnp.argmin(distances, axis=1)

    def evaluate(self, scores: Any, weights: Any | None = None) -> InformationReport:
        """Evaluate the fixed hard partition on a new weighted sample."""

        from .information import information_report

        labels = self.predict(scores)
        return information_report(scores, labels, weights=weights, n_bins=self.n_bins)

    def to_dict(self) -> dict[str, object]:
        """Return all stable in-memory fields as JSON-compatible data."""

        return json_ready(
            {
                "centers": self.centers,
                "transform": self.transform.to_dict(),
                "config": self.config.to_dict(),
                "trace": self.trace.to_dict(),
                "train_report": self.train_report.to_dict(),
                "validation_report": (
                    None if self.validation_report is None else self.validation_report.to_dict()
                ),
            }
        )

    def plot_summary(self, scores: Any, weights: Any | None = None) -> Figure:
        """Create the optional Matplotlib summary figure."""

        from .visualization import plot_summary

        return plot_summary(self, scores, weights)
