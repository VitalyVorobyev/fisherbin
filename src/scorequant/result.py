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

import numpy as np

from ._chunking import assignment_chunk_rows
from ._execution import backend_array, canonical_array, canonicalize_public, use_execution
from ._execution import xp as jnp
from ._json import json_ready
from ._typing import ArrayLike, JsonValue
from .config import ExecutionConfig, MahalanobisLloydConfig, PartitionConfig, QuantizerConfig
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
from .sources import ScoreProvenance, ScoreSchema
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

    steps: np.ndarray
    centers: np.ndarray
    objective: np.ndarray
    bin_weights: np.ndarray
    train_hard_retention: np.ndarray
    objective_label: str
    validation_hard_retention: np.ndarray | None = None
    soft_retention: np.ndarray | None = None
    temperatures: np.ndarray | None = None
    gradient_norms: np.ndarray | None = None

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""
        return json_ready(asdict(self))


@dataclass(frozen=True, slots=True)
class QuantizerResult:
    """Represent a reusable hard rule on raw score vectors."""

    centers: np.ndarray
    metric: np.ndarray | None
    transform: FisherTransform
    criterion: Criterion
    config: QuantizerConfig
    execution: ExecutionConfig
    trace: OptimizationTrace
    labels: np.ndarray
    train_report: InformationReport
    validation_report: InformationReport | None
    provenance: ScoreProvenance
    hardening_gap: float | None = None
    source_kind: str = "score_sample"
    train_profiled_report: ProfiledInformationReport | None = None
    validation_profiled_report: ProfiledInformationReport | None = None
    schema: ScoreSchema | None = None

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
        """Describe whether supplied-score matrices justify exact Fisher language.

        ``"supplied_score_surrogate"`` means the reported matrices measure
        ``Var(E[s_hat | q])`` for the supplied vectors ``s_hat``, which is
        the model's Fisher information only when ``s_hat`` equals the model
        score.
        """
        return "exact_fisher" if self.provenance.exact_fisher else "supplied_score_surrogate"

    def predict_scores(
        self,
        scores: ArrayLike,
        *,
        execution: ExecutionConfig | None = None,
    ) -> np.ndarray:
        """Assign raw score rows with the frozen score-space rule.

        Rows are assigned in memory-bounded chunks so that predicting on a
        large sample never materializes the full ``[n_rows, n_bins, rank]``
        distance tensor at once; each row's distance and nearest-center
        argmin are independent of every other row, so chunking is
        bit-identical to the unchunked computation.
        """
        with use_execution(execution or self.execution):
            coordinates = self.transform.apply(scores, execution=execution or self.execution)
            return canonical_array(_chunked_predict_labels(coordinates, self.centers, self.metric))

    def evaluate_scores(
        self,
        scores: ArrayLike,
        weights: ArrayLike | None = None,
        *,
        execution: ExecutionConfig | None = None,
    ) -> InformationReport:
        """Evaluate the frozen rule on a new weighted score sample."""
        return information_report(
            scores,
            self.predict_scores(scores, execution=execution or self.execution),
            weights,
            n_bins=self.n_bins,
            rank_rtol=self.config.rank_rtol,
            execution=execution or self.execution,
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
                "execution": self.execution.to_dict(),
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

    ``exchange_stable`` and ``geometry`` are verdicts at ``config.gain_tolerance``,
    which ``GeometryReport`` records, and never claims at tolerance zero. A
    finite solver stops at that threshold, so verifying its output against a
    stricter one would reject partitions it legitimately converged on.
    """

    labels: np.ndarray
    training_scores: np.ndarray
    cell_weights: np.ndarray
    cell_score_sums: np.ndarray
    cell_score_means: np.ndarray
    information_full: np.ndarray
    information_partitioned: np.ndarray
    objective: float
    transform: FisherTransform
    transformed_centers: np.ndarray | None
    metric: np.ndarray | None
    criterion: DOptimality | ProfiledDOptimality
    config: PartitionConfig
    execution: ExecutionConfig
    train_report: InformationReport
    provenance: ScoreProvenance
    accepted_moves: int
    scans: int
    exchange_stable: bool
    best_remaining_gain: float
    objective_history: np.ndarray
    positive_weight_mask: np.ndarray
    lloyd_iterations: int = 0
    accepted_lloyd_steps: int = 0
    geometry: GeometryReport | None = None
    profiled_report: ProfiledInformationReport | None = None
    profiled_geometry: ProfiledGeometryReport | None = None
    schema: ScoreSchema | None = None

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
        """Describe whether supplied-score matrices justify exact Fisher language.

        ``"supplied_score_surrogate"`` means the reported matrices measure
        ``Var(E[s_hat | q])`` for the supplied vectors ``s_hat``, which is
        the model's Fisher information only when ``s_hat`` equals the model
        score.
        """
        return "exact_fisher" if self.provenance.exact_fisher else "supplied_score_surrogate"

    def report(self) -> InformationReport:
        """Return supplied-score information for the fixed partition."""
        return self.train_report

    def compile_quantizer(
        self,
        *,
        execution: ExecutionConfig | None = None,
    ) -> QuantizerResult:
        r"""Compile an exchange-stable D partition into its canonical rule.

        Theorem 3 makes a one-point-exchange-stable, nonsingular D partition a
        self-consistent \(I^{-1}\)-Mahalanobis Voronoi partition of the observed
        rows, so the compiled rule
        \(\hat q(s)=\arg\min_b (s-\mu_b)^\top I^{-1}(s-\mu_b)\) is bookkeeping
        rather than a new fit. The theorem is exact; the partition behind it is
        not. A finite solver stops at ``config.gain_tolerance``, so the
        guarantee this method can offer is self-consistency *at that tolerance*:
        the rule reproduces every training label except on rows whose relocation
        is worth no more than ``gain_tolerance``, which the ``geometry``
        certificate has already measured and stamped with the same tolerance.
        Requiring exact reproduction instead verifies at tolerance zero and
        refuses partitions the solver converged on, which is what a boundary row
        in a million becomes.

        Boundary ties are never resolved here. ``predict_scores`` keeps the
        ordinary ``argmin`` rule, which is deterministic and breaks a tie toward
        the lowest cell index; the tolerance governs verification, not
        assignment.

        Returns
        -------
        QuantizerResult
            Reusable score-space rule carrying the partition's centers, metric,
            labels, and training report.

        Raises
        ------
        ValueError
            When the criterion is not ``DOptimality``, when the partition is not
            exchange-stable, when the compilation geometry is missing, or when
            the rule relabels a training row by more than ``gain_tolerance``.
        """
        resolved_execution = execution or self.execution
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
        with use_execution(resolved_execution):
            coordinates = self.transform.apply(self.training_scores, execution=resolved_execution)
            predicted = _chunked_predict_labels(coordinates, self.transformed_centers, self.metric)
        positive = np.asarray(self.positive_weight_mask)
        if not np.array_equal(np.asarray(predicted)[positive], np.asarray(self.labels)[positive]):
            # Only the solver-side certificate can price a disagreement, because
            # only it holds the row weights the exact relocation gain needs.
            if self.geometry is None or not self.geometry.voronoi_consistent:
                raise ValueError(
                    "D compilation is degenerate: the compiled rule relabels training rows "
                    "by more than the gain tolerance the partition was certified at; "
                    "inspect geometry.maximum_violation_gain"
                )
        trace = OptimizationTrace(
            steps=np.arange(self.objective_history.shape[0]),
            centers=np.repeat(
                self.transformed_centers[None, :, :], self.objective_history.shape[0], axis=0
            ),
            objective=self.objective_history,
            bin_weights=np.repeat(
                self.cell_weights[None, :], self.objective_history.shape[0], axis=0
            ),
            train_hard_retention=np.full(
                self.objective_history.shape,
                self.train_report.geometric_mean_retention,
                dtype=self.cell_weights.dtype,
            ),
            objective_label="logdet_retained",
        )
        return canonicalize_public(
            QuantizerResult(
                centers=self.transformed_centers,
                metric=self.metric,
                transform=self.transform,
                criterion=self.criterion,
                config=self.config,
                execution=resolved_execution,
                trace=trace,
                labels=self.labels,
                train_report=self.train_report,
                validation_report=None,
                provenance=self.provenance,
                hardening_gap=0.0,
                source_kind="compiled_partition",
            )
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
                "execution": self.execution.to_dict(),
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

    Public results store canonical NumPy arrays, so the stored centers and
    metric are placed on the active backend once here. Without it the broadcast
    difference and its square would be evaluated by NumPy on every chunk even
    under the JAX backend, materializing host temporaries that the selected
    runtime is supposed to own.
    """
    coordinates = backend_array(coordinates)
    centers = backend_array(centers)
    if metric is not None:
        metric = backend_array(metric)
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
