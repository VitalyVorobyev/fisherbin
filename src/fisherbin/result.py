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

    from .components import LinearComponents


@dataclass(frozen=True, slots=True)
class InformationReport:
    """Report Fisher retention and per-bin diagnostics for one sample.

    Attributes
    ----------
    fisher_unbinned, fisher_binned
        Unregularized Fisher matrices before and after hard binning.
    retained_matrix, retained_eigenvalues
        Fisher-normalized retained matrix and its informative-direction spectrum.
    arithmetic_mean_retention, geometric_mean_retention, logdet_retention
        Scalar A- and D-style retention summaries.
    bin_weights, bin_counts, bin_effective_sample_sizes
        Per-bin weighted and unweighted occupancy diagnostics.
    effective_rank, rank_threshold
        Numerical informative rank and the absolute eigenvalue threshold used.
    psd_residual_min_eigenvalue
        Smallest eigenvalue of ``F_unbinned - F_binned``; small negative values
        quantify floating-point PSD residuals.
    """

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

    def __str__(self) -> str:
        """Format the headline retention diagnostics for interactive use."""
        eigenvalues = ", ".join(f"{float(value):.4f}" for value in self.retained_eigenvalues)
        return (
            "FisherBin information report\n"
            f"  effective rank: {self.effective_rank}\n"
            f"  D-efficiency: {self.geometric_mean_retention:.6f}\n"
            f"  mean retention: {self.arithmetic_mean_retention:.6f}\n"
            f"  retained eigenvalues: [{eigenvalues}]\n"
            f"  minimum PSD residual eigenvalue: {self.psd_residual_min_eigenvalue:.3e}"
        )


@dataclass(frozen=True, slots=True)
class OptimizationTrace:
    """Store aggregate optimization history.

    Center snapshots and aggregate metrics are retained at configured trace
    steps. Per-observation assignments and responsibilities are never stored.
    Method-specific fields are ``None`` when they do not apply.
    """

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
    """Represent a fitted hard score-space partition and its diagnostics.

    Prediction and evaluation accept raw score matrices with the same parameter
    dimension used during fitting.
    """

    centers: jnp.ndarray
    transform: FisherTransform
    config: FitConfig
    trace: OptimizationTrace
    labels: jnp.ndarray
    train_report: InformationReport
    validation_report: InformationReport | None = None

    @property
    def n_bins(self) -> int:
        """Return the number of fitted hard bins."""
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
        return information_report(
            scores,
            labels,
            weights=weights,
            n_bins=self.n_bins,
            rank_rtol=self.config.rank_rtol,
        )

    def report(self) -> InformationReport:
        """Return the final hard-partition report on the fitting sample."""
        return self.train_report

    def to_dict(self) -> dict[str, object]:
        """Return all stable in-memory fields as JSON-compatible data."""
        return json_ready(
            {
                "centers": self.centers,
                "transform": self.transform.to_dict(),
                "config": self.config.to_dict(),
                "trace": self.trace.to_dict(),
                "labels": self.labels,
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


class _ResultView:
    """Shared read-only view over a representation-specific score result."""

    __slots__ = ()

    @property
    def _fit_result(self) -> FitResult:
        raise NotImplementedError

    @property
    def labels(self) -> jnp.ndarray:
        """Final hard labels for the fitting rows."""
        return self._fit_result.labels

    @property
    def n_bins(self) -> int:
        """Number of fitted hard bins."""
        return self._fit_result.n_bins

    @property
    def centers(self) -> jnp.ndarray:
        """Fitted centers in optimization coordinates."""
        return self._fit_result.centers

    @property
    def transform(self) -> FisherTransform:
        """Fitted informative-subspace transform."""
        return self._fit_result.transform

    @property
    def config(self) -> FitConfig:
        """Validated optimizer configuration used for fitting."""
        return self._fit_result.config

    @property
    def trace(self) -> OptimizationTrace:
        """Recorded aggregate optimization history."""
        return self._fit_result.trace

    @property
    def train_report(self) -> InformationReport:
        """Final hard-partition report on the fitting sample."""
        return self._fit_result.train_report

    @property
    def validation_report(self) -> InformationReport | None:
        """Optional final report on the diagnostic validation sample."""
        return self._fit_result.validation_report

    def report(self) -> InformationReport:
        """Return the final hard-partition report on the fitting sample."""
        return self.train_report


@dataclass(frozen=True, slots=True)
class ComponentFitResult(_ResultView):
    """Represent a fitted partition whose prediction input is components.

    The reference coefficients and component ordering are frozen with the
    score-level result so prediction cannot silently change parameter order.
    """

    score_result: FitResult
    coefficients: jnp.ndarray
    component_names: tuple[str, ...]

    @property
    def _fit_result(self) -> FitResult:
        return self.score_result

    def predict(self, components: Any) -> jnp.ndarray:
        """Assign a new component matrix using the frozen reference coefficients."""
        from .components import scores_from_components

        return self.score_result.predict(scores_from_components(components, self.coefficients))

    def evaluate(self, components: Any, weights: Any | None = None) -> InformationReport:
        """Evaluate the fixed partition on a new weighted component sample."""
        from .components import scores_from_components

        return self.score_result.evaluate(
            scores_from_components(components, self.coefficients), weights
        )

    def to_dict(self) -> dict[str, object]:
        """Return component metadata and the score result as JSON-ready data."""
        return json_ready(
            {
                "input_representation": "components",
                "coefficients": self.coefficients,
                "component_names": self.component_names,
                "score_result": self.score_result.to_dict(),
            }
        )

    def plot_summary(self, components: Any, weights: Any | None = None) -> Figure:
        """Create a score-space summary from a component matrix."""
        from .components import scores_from_components

        return self.score_result.plot_summary(
            scores_from_components(components, self.coefficients), weights
        )


@dataclass(frozen=True, slots=True)
class ModelFitResult(_ResultView):
    """Represent a fitted partition whose prediction input is physical variables.

    The in-memory component model is retained for prediction. Callable component
    functions are intentionally omitted from JSON conversion.
    """

    component_result: ComponentFitResult
    model: LinearComponents

    @property
    def _fit_result(self) -> FitResult:
        return self.component_result.score_result

    def predict(self, X: Any) -> jnp.ndarray:
        """Evaluate the frozen model and assign physical observations to bins."""
        return self.component_result.predict(self.model.evaluate_components(X))

    def evaluate(self, X: Any, weights: Any | None = None) -> InformationReport:
        """Evaluate the frozen model and partition on a new weighted sample."""
        return self.component_result.evaluate(self.model.evaluate_components(X), weights)

    def to_dict(self) -> dict[str, object]:
        """Return model metadata and nested fitted state as JSON-ready data."""
        return json_ready(
            {
                "input_representation": "variables",
                "model": self.model.to_dict(),
                "component_result": self.component_result.to_dict(),
            }
        )

    def plot_summary(self, X: Any, weights: Any | None = None) -> Figure:
        """Evaluate the model and create a score-space summary figure."""
        return self.component_result.plot_summary(self.model.evaluate_components(X), weights)
