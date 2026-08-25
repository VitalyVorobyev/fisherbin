"""Immutable public result objects.

Diagnostic and certificate report types (``InformationReport`` and friends)
now live in ``reports.py``, which does not import this module. That is what
lets ``QuantizerResult.evaluate_scores`` import ``information_report`` at
module scope below instead of inside the method: ``result -> information ->
reports`` is a chain, not a cycle.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

import jax.numpy as jnp
import numpy as np

from ._chunking import assignment_chunk_rows
from ._json import json_ready
from ._typing import ArrayLike, JsonValue
from .config import MahalanobisLloydConfig, PartitionConfig, QuantizerConfig
from .criteria import Criterion, DOptimality, ProfiledDOptimality
from .information import information_report
from .reports import (
    EfficientScoreBound,
    GeometryReport,
    InformationReport,
    PartitionCertificate,
    ProfiledGeometryReport,
    ProfiledInformationReport,
    StabilityReport,
)
from .sources import ScoreProvenance
from .transforms import FisherTransform

if TYPE_CHECKING:
    from matplotlib.figure import Figure

__all__ = [
    "EfficientScoreBound",
    "GeometryReport",
    "InformationReport",
    "OptimizationTrace",
    "PartitionCertificate",
    "PartitionResult",
    "ProfiledGeometryReport",
    "ProfiledInformationReport",
    "QuantizerResult",
    "StabilityReport",
]


@dataclass(frozen=True, slots=True)
class OptimizationTrace:
    """Store aggregate quantizer optimization history.

    Attributes
    ----------
    objective_label
        Units of ``objective``. Solvers do not share one objective convention:
        ``"whitened_sse"`` is a minimized weighted within-cell squared error in
        Fisher-whitened coordinates, ``"logdet_retained"`` is a maximized
        retained log determinant, and ``"profiled_logdet"`` is a maximized
        profiled log determinant. Never compare two traces across labels.
    """

    steps: jnp.ndarray
    centers: jnp.ndarray
    objective: jnp.ndarray
    bin_weights: jnp.ndarray
    train_hard_retention: jnp.ndarray
    objective_label: str
    validation_hard_retention: jnp.ndarray | None = None
    soft_retention: jnp.ndarray | None = None
    temperatures: jnp.ndarray | None = None
    gradient_norms: jnp.ndarray | None = None

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""
        return json_ready(asdict(self))


@dataclass(frozen=True, slots=True)
class QuantizerResult:
    """Represent a reusable hard rule on raw score vectors."""

    centers: jnp.ndarray
    metric: jnp.ndarray | None
    transform: FisherTransform
    criterion: Criterion
    config: QuantizerConfig
    trace: OptimizationTrace
    labels: jnp.ndarray
    train_report: InformationReport
    validation_report: InformationReport | None
    provenance: ScoreProvenance
    hardening_gap: float | None = None
    source_kind: str = "score_sample"
    train_profiled_report: ProfiledInformationReport | None = None
    validation_profiled_report: ProfiledInformationReport | None = None

    @property
    def n_bins(self) -> int:
        """Return the number of hard output labels."""
        return int(self.centers.shape[0])

    @property
    def rank(self) -> int:
        """Return the numerically informative score-space rank."""
        return self.transform.rank

    @property
    def information_kind(self) -> str:
        """Describe whether supplied-score matrices justify exact Fisher language."""
        return "exact_fisher" if self.provenance.exact_fisher else "supplied_score_surrogate"

    def predict_scores(self, scores: ArrayLike) -> jnp.ndarray:
        """Assign raw score rows with the frozen score-space rule.

        Rows are assigned in memory-bounded chunks so that predicting on a
        large sample never materializes the full ``[n_rows, n_bins, rank]``
        distance tensor at once; each row's distance and nearest-center
        argmin are independent of every other row, so chunking is
        bit-identical to the unchunked computation.
        """
        coordinates = self.transform.apply(scores)
        return _chunked_predict_labels(coordinates, self.centers, self.metric)

    def evaluate_scores(
        self, scores: ArrayLike, weights: ArrayLike | None = None
    ) -> InformationReport:
        """Evaluate the frozen rule on a new weighted score sample."""
        return information_report(
            scores,
            self.predict_scores(scores),
            weights,
            n_bins=self.n_bins,
            rank_rtol=self.config.rank_rtol,
        )

    def report(self) -> InformationReport:
        """Return final hard training-sample diagnostics."""
        return self.train_report

    def to_dict(self) -> dict[str, JsonValue]:
        """Return JSON-ready in-memory state, not a versioned artifact format."""
        return json_ready(
            {
                "centers": self.centers,
                "metric": self.metric,
                "transform": self.transform.to_dict(),
                "criterion": self.criterion.to_dict(),
                "config": self.config.to_dict(),
                "trace": self.trace.to_dict(),
                "labels": self.labels,
                "train_report": self.train_report.to_dict(),
                "validation_report": (
                    None if self.validation_report is None else self.validation_report.to_dict()
                ),
                "provenance": self.provenance.to_dict(),
                "information_kind": self.information_kind,
                "hardening_gap": self.hardening_gap,
                "source_kind": self.source_kind,
                "train_profiled_report": (
                    None
                    if self.train_profiled_report is None
                    else self.train_profiled_report.to_dict()
                ),
                "validation_profiled_report": (
                    None
                    if self.validation_profiled_report is None
                    else self.validation_profiled_report.to_dict()
                ),
            }
        )

    def plot_summary(self, scores: ArrayLike, weights: ArrayLike | None = None) -> Figure:
        """Create the optional score-space summary figure."""
        from .visualization import plot_summary

        return plot_summary(self, scores, weights)


@dataclass(frozen=True, slots=True)
class PartitionResult:
    """Represent optimized labels of one fixed weighted score table.

    The solver counters are reported separately and never merged: ``scans`` and
    ``accepted_moves`` describe exchange work, while ``lloyd_iterations`` and
    ``accepted_lloyd_steps`` describe guarded batch relabelings. Both stay zero
    for a solver that performs neither. ``objective_history`` records every
    accepted step of every phase in order and is strictly increasing.

    Geometry diagnostics are criterion-specific and never shared: a
    ``DOptimality`` result carries ``geometry`` and no ``profiled_geometry``, a
    ``ProfiledDOptimality`` result carries ``profiled_geometry`` and no
    ``geometry``. The two measure different objects — a strict Mahalanobis
    Voronoi rule that exchange stability guarantees, and an efficient
    semimetric whose Voronoi rule a stable profiled partition may violate — so
    one name for both would claim an implication that does not hold.
    """

    labels: jnp.ndarray
    training_scores: jnp.ndarray
    cell_weights: jnp.ndarray
    cell_score_sums: jnp.ndarray
    cell_score_means: jnp.ndarray
    information_full: jnp.ndarray
    information_partitioned: jnp.ndarray
    objective: float
    transform: FisherTransform
    transformed_centers: jnp.ndarray | None
    metric: jnp.ndarray | None
    criterion: DOptimality | ProfiledDOptimality
    config: PartitionConfig
    train_report: InformationReport
    provenance: ScoreProvenance
    accepted_moves: int
    scans: int
    exchange_stable: bool
    best_remaining_gain: float
    objective_history: jnp.ndarray
    positive_weight_mask: jnp.ndarray
    lloyd_iterations: int = 0
    accepted_lloyd_steps: int = 0
    geometry: GeometryReport | None = None
    profiled_report: ProfiledInformationReport | None = None
    profiled_geometry: ProfiledGeometryReport | None = None

    @property
    def n_bins(self) -> int:
        """Return the number of nonempty requested cells."""
        return int(self.cell_weights.shape[0])

    @property
    def rank(self) -> int:
        """Return the numerically informative score-space rank."""
        return self.transform.rank

    @property
    def information_kind(self) -> str:
        """Describe whether supplied-score matrices justify exact Fisher language."""
        return "exact_fisher" if self.provenance.exact_fisher else "supplied_score_surrogate"

    def report(self) -> InformationReport:
        """Return supplied-score information for the fixed partition."""
        return self.train_report

    def compile_quantizer(self) -> QuantizerResult:
        """Compile an exchange-stable D partition into its canonical rule."""
        if not isinstance(self.criterion, DOptimality):
            raise ValueError(
                "finite profiled-D labels have no canonical inductive compilation; "
                "fit an explicit quantizer instead"
            )
        if not self.exchange_stable:
            remedy = (
                "set guard='exchange'"
                if isinstance(self.config, MahalanobisLloydConfig)
                else "raise max_scans, or leave it unset to run until stability"
            )
            raise ValueError(
                "only an exchange-stable D partition can be compiled; inspect "
                f"best_remaining_gain and {remedy}"
            )
        if self.transformed_centers is None or self.metric is None:
            raise ValueError("D compilation geometry is unavailable")
        coordinates = self.transform.apply(self.training_scores)
        predicted = _chunked_predict_labels(coordinates, self.transformed_centers, self.metric)
        positive = np.asarray(self.positive_weight_mask)
        if not np.array_equal(np.asarray(predicted)[positive], np.asarray(self.labels)[positive]):
            raise ValueError(
                "D compilation is degenerate: training labels are not strictly reproduced"
            )
        trace = OptimizationTrace(
            steps=jnp.arange(self.objective_history.shape[0]),
            centers=jnp.repeat(
                self.transformed_centers[None, :, :], self.objective_history.shape[0], axis=0
            ),
            objective=self.objective_history,
            bin_weights=jnp.repeat(
                self.cell_weights[None, :], self.objective_history.shape[0], axis=0
            ),
            train_hard_retention=jnp.full(
                self.objective_history.shape,
                self.train_report.geometric_mean_retention,
                dtype=self.cell_weights.dtype,
            ),
            objective_label="logdet_retained",
        )
        return QuantizerResult(
            centers=self.transformed_centers,
            metric=self.metric,
            transform=self.transform,
            criterion=self.criterion,
            config=self.config,
            trace=trace,
            labels=self.labels,
            train_report=self.train_report,
            validation_report=None,
            provenance=self.provenance,
            hardening_gap=0.0,
            source_kind="compiled_partition",
        )

    def to_dict(self) -> dict[str, JsonValue]:
        """Return the fixed-sample result as JSON-ready data."""
        return json_ready(
            {
                "labels": self.labels,
                "cell_weights": self.cell_weights,
                "cell_score_sums": self.cell_score_sums,
                "cell_score_means": self.cell_score_means,
                "information_full": self.information_full,
                "information_partitioned": self.information_partitioned,
                "objective": self.objective,
                "transform": self.transform.to_dict(),
                "transformed_centers": self.transformed_centers,
                "metric": self.metric,
                "criterion": self.criterion.to_dict(),
                "config": self.config.to_dict(),
                "train_report": self.train_report.to_dict(),
                "provenance": self.provenance.to_dict(),
                "information_kind": self.information_kind,
                "accepted_moves": self.accepted_moves,
                "scans": self.scans,
                "lloyd_iterations": self.lloyd_iterations,
                "accepted_lloyd_steps": self.accepted_lloyd_steps,
                "exchange_stable": self.exchange_stable,
                "best_remaining_gain": self.best_remaining_gain,
                "objective_history": self.objective_history,
                "geometry": (None if self.geometry is None else self.geometry.to_dict()),
                "profiled_report": (
                    None if self.profiled_report is None else self.profiled_report.to_dict()
                ),
                "profiled_geometry": (
                    None if self.profiled_geometry is None else self.profiled_geometry.to_dict()
                ),
            }
        )


def _predict_distances(
    coordinates: jnp.ndarray, centers: jnp.ndarray, metric: jnp.ndarray | None
) -> jnp.ndarray:
    """Return the dense ``[chunk_rows, n_bins]`` assignment-distance table."""
    differences = coordinates[:, None, :] - centers[None, :, :]
    if metric is None:
        return jnp.sum(differences**2, axis=2)
    return jnp.einsum("nbr,rs,nbs->nb", differences, metric, differences)


def _predict_labels(
    coordinates: jnp.ndarray, centers: jnp.ndarray, metric: jnp.ndarray | None
) -> jnp.ndarray:
    """Assign one chunk of rows to its nearest center."""
    return jnp.argmin(_predict_distances(coordinates, centers, metric), axis=1)


def _chunked_predict_labels(
    coordinates: jnp.ndarray, centers: jnp.ndarray, metric: jnp.ndarray | None
) -> jnp.ndarray:
    """Assign every row to its nearest center in memory-bounded chunks.

    Bit-identical to the unchunked assignment: each row's distance and
    argmin are independent of every other row, so partitioning rows into
    chunks never materializes the full ``[n_rows, n_bins, rank]`` tensor and
    changes nothing about the arithmetic.
    """
    n_rows = int(coordinates.shape[0])
    chunk_rows = assignment_chunk_rows(
        coordinates.dtype, n_rows, int(centers.shape[0]), coordinates.shape[1]
    )
    if chunk_rows >= n_rows:
        return _predict_labels(coordinates, centers, metric)
    chunks = [
        _predict_labels(coordinates[start : start + chunk_rows], centers, metric)
        for start in range(0, n_rows, chunk_rows)
    ]
    return jnp.concatenate(chunks)
