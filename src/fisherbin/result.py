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

    def __str__(self) -> str:
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
    labels: jnp.ndarray
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


@dataclass(frozen=True, slots=True)
class ComponentFitResult:
    """A fitted partition whose prediction input is a component matrix."""

    score_result: FitResult
    coefficients: jnp.ndarray
    component_names: tuple[str, ...]

    @property
    def labels(self) -> jnp.ndarray:
        return self.score_result.labels

    @property
    def n_bins(self) -> int:
        return self.score_result.n_bins

    @property
    def centers(self) -> jnp.ndarray:
        return self.score_result.centers

    @property
    def transform(self) -> FisherTransform:
        return self.score_result.transform

    @property
    def config(self) -> FitConfig:
        return self.score_result.config

    @property
    def trace(self) -> OptimizationTrace:
        return self.score_result.trace

    @property
    def train_report(self) -> InformationReport:
        return self.score_result.train_report

    @property
    def validation_report(self) -> InformationReport | None:
        return self.score_result.validation_report

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

    def report(self) -> InformationReport:
        return self.train_report

    def to_dict(self) -> dict[str, object]:
        return json_ready(
            {
                "input_representation": "components",
                "coefficients": self.coefficients,
                "component_names": self.component_names,
                "score_result": self.score_result.to_dict(),
            }
        )

    def plot_summary(self, components: Any, weights: Any | None = None) -> Figure:
        from .components import scores_from_components

        return self.score_result.plot_summary(
            scores_from_components(components, self.coefficients), weights
        )


@dataclass(frozen=True, slots=True)
class ModelFitResult:
    """A fitted partition whose prediction input is a physical-variable matrix."""

    component_result: ComponentFitResult
    model: LinearComponents

    @property
    def labels(self) -> jnp.ndarray:
        return self.component_result.labels

    @property
    def n_bins(self) -> int:
        return self.component_result.n_bins

    @property
    def centers(self) -> jnp.ndarray:
        return self.component_result.centers

    @property
    def transform(self) -> FisherTransform:
        return self.component_result.transform

    @property
    def config(self) -> FitConfig:
        return self.component_result.config

    @property
    def trace(self) -> OptimizationTrace:
        return self.component_result.trace

    @property
    def train_report(self) -> InformationReport:
        return self.component_result.train_report

    @property
    def validation_report(self) -> InformationReport | None:
        return self.component_result.validation_report

    def predict(self, X: Any) -> jnp.ndarray:
        """Evaluate the frozen model and assign physical observations to bins."""

        return self.component_result.predict(self.model.evaluate_components(X))

    def evaluate(self, X: Any, weights: Any | None = None) -> InformationReport:
        """Evaluate the frozen model and partition on a new weighted sample."""

        return self.component_result.evaluate(self.model.evaluate_components(X), weights)

    def report(self) -> InformationReport:
        return self.train_report

    def to_dict(self) -> dict[str, object]:
        return json_ready(
            {
                "input_representation": "variables",
                "model": self.model.to_dict(),
                "component_result": self.component_result.to_dict(),
            }
        )

    def plot_summary(self, X: Any, weights: Any | None = None) -> Figure:
        return self.component_result.plot_summary(self.model.evaluate_components(X), weights)
