"""Immutable public result and diagnostic objects."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Literal

import jax.numpy as jnp
import numpy as np

from ._json import json_ready
from ._typing import ArrayLike, JsonValue
from .config import MahalanobisLloydConfig, PartitionConfig, QuantizerConfig
from .criteria import Criterion, DOptimality, ProfiledDOptimality
from .sources import ScoreProvenance
from .transforms import FisherTransform

if TYPE_CHECKING:
    from matplotlib.figure import Figure


@dataclass(frozen=True, slots=True)
class InformationReport:
    """Report supplied-score retention and per-bin diagnostics for one sample."""

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

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""
        return json_ready(asdict(self))

    def __str__(self) -> str:
        """Format headline supplied-score diagnostics."""
        eigenvalues = ", ".join(f"{float(value):.4f}" for value in self.retained_eigenvalues)
        return (
            "ScoreQuant information report\n"
            f"  effective rank: {self.effective_rank}\n"
            f"  D-efficiency: {self.geometric_mean_retention:.6f}\n"
            f"  mean retention: {self.arithmetic_mean_retention:.6f}\n"
            f"  retained eigenvalues: [{eigenvalues}]\n"
            f"  minimum PSD residual eigenvalue: {self.psd_residual_min_eigenvalue:.3e}"
        )


@dataclass(frozen=True, slots=True)
class ProfiledInformationReport:
    """Report same-label profiled information for interest and nuisance blocks."""

    interest: tuple[int, ...]
    nuisance: tuple[int, ...]
    schur_unbinned: jnp.ndarray
    schur_binned: jnp.ndarray
    nuisance_unbinned: jnp.ndarray
    nuisance_binned: jnp.ndarray
    objective: float
    logdet_retention: float
    geometric_mean_retention: float
    interest_rank: int
    nuisance_rank: int

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible profiled-information representation."""
        return json_ready(asdict(self))


@dataclass(frozen=True, slots=True)
class GeometryReport:
    r"""Certify the self-consistent Voronoi geometry of a finite D partition.

    At a one-point-exchange-stable, positive-definite D partition every
    admissible move that violates the Mahalanobis-Voronoi rule of the terminal
    metric \(I^{-1}\) would raise the log determinant by at least
    \(\log(1+\alpha\beta q_\delta^2/4)>0\), where
    \(q_\delta=(\mu_a-\mu_b)^\top I^{-1}(\mu_a-\mu_b)\) separates the two cell
    means. Exchange stability therefore forces strict Voronoi geometry, which is
    what makes ``PartitionResult.compile_quantizer`` well posed. This report
    measures both sides of that statement on the terminal state instead of
    assuming them.

    All quadratic forms use the same metric and cell means the solver ended
    with, evaluated over the distinct positive-weight score atoms.

    Attributes
    ----------
    maximum_voronoi_violation
        Largest value over rows of the own-cell distance minus the smallest
        other-cell distance. A nonpositive value means every row already sits in
        its nearest cell under the terminal metric. It is ``-inf`` for a
        single-cell partition, which has no alternative destination.
    guaranteed_violation_gain
        Largest Theorem-3 lower bound \(\log(1+\alpha\beta q_\delta^2/4)\) over
        admissible Voronoi-violating moves, and exactly ``0.0`` when no such
        move exists. A positive value is the log-determinant gain that
        exchange stability rules out.
    maximum_separation_residual
        Largest value over unordered cell pairs of \(q_\delta-(1/W_a+1/W_b)\).
        The leverage lemma makes this nonpositive for every labeling, so a
        positive value indicates numerical trouble rather than a better
        partition. It is ``-inf`` for a single-cell partition.
    violating_moves, evaluated_moves
        Number of admissible Voronoi-violating moves and of admissible moves.
        A move is admissible when its source cell keeps positive weight and its
        destination differs from its source.
    voronoi_consistent
        Whether ``maximum_voronoi_violation`` is nonpositive.
    separation_certified
        Whether ``maximum_separation_residual`` respects the leverage lemma up
        to a small relative floating-point tolerance.
    """

    maximum_voronoi_violation: float
    guaranteed_violation_gain: float
    maximum_separation_residual: float
    violating_moves: int
    evaluated_moves: int
    voronoi_consistent: bool
    separation_certified: bool

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible Voronoi-geometry representation."""
        return json_ready(asdict(self))


@dataclass(frozen=True, slots=True)
class StabilityReport:
    """Certify that no single-row relocation improves one supplied labeling.

    The report is produced by ``exchange_stability_report`` from exactly one
    complete exact scan, so it verifies labels of any origin: a guarded
    Mahalanobis-Lloyd run that stopped early, an external tool, or a hand edit.

    Attributes
    ----------
    stable
        Whether no admissible relocation improves the criterion by more than the
        requested gain tolerance.
    best_gain
        Largest exact objective gain found in the scan. It is ``-inf`` when the
        labeling admits no relocation at all.
    best_move
        ``(row, destination)`` of that gain in original input row indexing, or
        ``None`` when the labeling is stable.
    objective
        Exact criterion value of the supplied labeling, in the convention
        ``PartitionResult.objective`` uses for the same criterion.
    n_bins
        Number of cells the labeling declares.
    criterion
        Criterion the scan certified against.
    """

    stable: bool
    best_gain: float
    best_move: tuple[int, int] | None
    objective: float
    n_bins: int
    criterion: DOptimality | ProfiledDOptimality

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible stability representation."""
        return json_ready(asdict(self))


@dataclass(frozen=True, slots=True)
class ProfiledGeometryReport:
    """Diagnose the finite efficient-semimetric gap of a profiled partition."""

    metric: jnp.ndarray
    maximum_positive_violation: float
    maximum_theoretical_bound: float
    maximum_bound_residual: float
    violating_moves: int
    evaluated_moves: int
    bound_certified: bool

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible geometry-gap representation."""
        return json_ready(asdict(self))


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
        """Assign raw score rows with the frozen score-space rule."""
        coordinates = self.transform.apply(scores)
        differences = coordinates[:, None, :] - self.centers[None, :, :]
        distances = (
            jnp.sum(differences**2, axis=2)
            if self.metric is None
            else jnp.einsum("nbr,rs,nbs->nb", differences, self.metric, differences)
        )
        return jnp.argmin(distances, axis=1)

    def evaluate_scores(
        self, scores: ArrayLike, weights: ArrayLike | None = None
    ) -> InformationReport:
        """Evaluate the frozen rule on a new weighted score sample."""
        from .information import information_report

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
        predicted = _predict_transformed(coordinates, self.transformed_centers, self.metric)
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


@dataclass(frozen=True, slots=True)
class PartitionCertificate:
    r"""Report what a bounded global D search actually proved.

    ``certify_partition`` explores hard labelings with the singleton-completion
    upper bound: any completion of a partial assignment is coarser than the
    partial cells together with singleton cells for the unassigned atoms, so
    Loewner monotonicity of the log determinant makes
    \(\log\det(I_{\text{partial}}+R_t)\) a valid ceiling for the whole subtree.
    The search is exponential in the worst case and therefore explicitly
    bounded; the certificate always states which of the two outcomes occurred.

    Attributes
    ----------
    status
        ``"optimal"`` when the tree was exhausted, so no labeling beats
        ``objective`` by more than the configured gain tolerance.
        ``"budget_exhausted"`` when the node budget stopped the search first.
    objective
        Best log determinant found, in the Fisher-whitened convention of
        ``PartitionResult.objective`` under ``DOptimality``.
    labels
        Labels attaining ``objective``, defined for every input row.
        Zero-weight rows carry the label of their nearest cell mean in the
        terminal metric and never influenced the search.
    upper_bound
        Global ceiling at termination. It equals ``objective`` for a proved
        optimum and is otherwise the best bound still outstanding on an
        abandoned subtree.
    gap
        ``upper_bound`` minus ``objective``, nonnegative by construction and
        exactly zero for a proved optimum.
    nodes_explored
        Number of search nodes visited, including pruned children.
    incumbent_was_optimal
        Whether the search proved the starting incumbent optimal without
        improving it. It is ``False`` whenever the budget was exhausted,
        because an unfinished search proves nothing about the incumbent.
    """

    status: Literal["optimal", "budget_exhausted"]
    objective: float
    labels: jnp.ndarray
    upper_bound: float
    gap: float
    nodes_explored: int
    incumbent_was_optimal: bool

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation of the certificate."""
        return json_ready(asdict(self))


@dataclass(frozen=True, slots=True)
class EfficientScoreBound:
    r"""Certify a ceiling on profiled information from the full-data efficient score.

    Let \(\hat s=s_\psi-B^\ast s_\lambda\) be the efficient score built from the
    *full-data* information matrix, and let \(q\) be any hard rule with at most
    ``n_bins`` cells. Efficient-score domination states

    \[
        \mathrm{Schur}_\psi\!\left(I_q\right)\;\preceq\;
        \mathbb{E}\!\left[\hat s \mid q\right]\text{-between-cell information},
    \]

    so maximizing the right-hand side over all ``n_bins``-cell rules of
    \(\hat s\) upper-bounds the profiled objective of every ``n_bins``-cell rule
    of the *full* score space. For one parameter of interest the right-hand side
    is scalar, the maximizer has ordered interval cells, and the exact weighted
    interval dynamic program attains it. ``upper_bound`` is the logarithm of
    that maximum, in the same convention as ``PartitionResult.objective`` under
    ``ProfiledDOptimality``: an uncentered between-cell second moment of raw
    score columns, never a mean-centered variance.

    Attributes
    ----------
    upper_bound
        Log-scale certified ceiling on the profiled objective.
    labels
        Interval labels of the efficient score, defined for every input row.
        Zero-weight rows carry the label of their nearest cell mean and never
        influence the bound. These labels are also a strong initializer: pass
        them as ``initial_labels`` to ``optimize_partition`` under
        ``ProfiledDOptimality``.
    efficient_scores
        Full-information efficient scores with shape ``[N, 1]``.
    n_bins, interest
        Cell budget and interest columns the bound was certified for.

    Notes
    -----
    The bound is a property of one weighted score table. Comparing it to a
    partition of different scores or weights is meaningless, and ``gap_to``
    cannot detect that mismatch; it only checks the criterion convention and the
    cell budget. Refinement monotonicity makes the bound valid for any partition
    with at most ``n_bins`` cells.
    """

    upper_bound: float
    labels: jnp.ndarray
    efficient_scores: jnp.ndarray
    n_bins: int
    interest: tuple[int, ...]

    def gap_to(self, partition_result: PartitionResult) -> float:
        r"""Return the certified slack between the bound and an achieved objective.

        Parameters
        ----------
        partition_result
            Profiled-\(D_s\) result on the same weighted score table, with the
            same interest columns and at most ``n_bins`` cells.

        Returns
        -------
        float
            ``upper_bound`` minus the achieved profiled objective. The value is
            nonnegative up to floating-point error on valid inputs.
        """
        criterion = partition_result.criterion
        if not isinstance(criterion, ProfiledDOptimality):
            raise ValueError(
                "the efficient-score bound compares only against a profiled-D partition"
            )
        if criterion.interest != self.interest:
            raise ValueError(
                f"partition interest {criterion.interest} differs from the certified "
                f"interest {self.interest}"
            )
        if partition_result.n_bins > self.n_bins:
            raise ValueError(
                f"the bound certifies at most {self.n_bins} cells, but the partition "
                f"has {partition_result.n_bins}"
            )
        return self.upper_bound - partition_result.objective

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation of the certified bound."""
        return json_ready(asdict(self))


def _predict_transformed(
    coordinates: jnp.ndarray, centers: jnp.ndarray, metric: jnp.ndarray
) -> jnp.ndarray:
    differences = coordinates[:, None, :] - centers[None, :, :]
    distances = jnp.einsum("nbr,rs,nbs->nb", differences, metric, differences)
    return jnp.argmin(distances, axis=1)
