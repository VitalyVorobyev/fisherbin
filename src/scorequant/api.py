"""Task-explicit public partition and quantizer workflows."""

from __future__ import annotations

from dataclasses import dataclass, replace

import jax.numpy as jnp

from ._typing import ArrayLike
from ._validation import (
    _ValidatedSample,
    collapse_duplicate_scores,
    validate_n_bins,
    validate_sample,
)
from .config import (
    DExchangeConfig,
    KMeansConfig,
    MahalanobisLloydConfig,
    PartitionConfig,
    QuantizerConfig,
    ScalarDPConfig,
    SoftVoronoiConfig,
)
from .criteria import Criterion, DOptimality, NormalizedTrace, ProfiledDOptimality
from .information import information_report, profiled_information_report
from .partition import optimize_d_partition, optimize_profiled_d_partition
from .providers import ScoreProvider
from .quantizers import (
    QuantizerRun,
    hard_assign,
    scalar_weighted_kmeans_dp,
    soft_voronoi,
    weighted_kmeans,
)
from .result import InformationReport, OptimizationTrace, PartitionResult, QuantizerResult
from .sources import (
    IntegrationSource,
    ObservationSample,
    ScoreProvenance,
    ScoreSample,
    Source,
)
from .transforms import FisherTransform, fisher_transform


@dataclass(frozen=True, slots=True)
class _PreparedFit:
    config: KMeansConfig | SoftVoronoiConfig | ScalarDPConfig
    train_sample: _ValidatedSample
    validation_sample: _ValidatedSample | None
    transform: FisherTransform
    train_coordinates: jnp.ndarray
    train_weights: jnp.ndarray
    train_objective_scores: jnp.ndarray
    all_train_coordinates: jnp.ndarray
    validation_coordinates: jnp.ndarray | None


@dataclass(frozen=True, slots=True)
class _FitDiagnostics:
    labels: jnp.ndarray
    train_report: InformationReport
    validation_report: InformationReport | None
    train_hard_retention: list[float]
    validation_hard_retention: list[float] | None


def optimize_partition(
    scores: ArrayLike,
    *,
    weights: ArrayLike | None = None,
    n_bins: int,
    criterion: DOptimality | ProfiledDOptimality | None = None,
    config: PartitionConfig | None = None,
    provenance: ScoreProvenance | None = None,
    initial_labels: ArrayLike | None = None,
) -> PartitionResult:
    """Optimize labels of one fixed score table without prediction semantics.

    Both finite criteria accept either the exact positive-gain exchange or the
    guarded Mahalanobis-Lloyd solver; the guarded batch never accepts a step
    that the exactly rebuilt objective does not certify.

    Parameters
    ----------
    scores, weights, n_bins, criterion, config, provenance
        Fixed-sample assignment contract described in the API guide.
    initial_labels
        Optional starting labeling with shape ``[N]`` and values in
        ``[0, n_bins)``, for example
        ``EfficientScoreBound.labels``. Zero-weight rows carry
        no measure and their labels are ignored; identical score rows are merged
        before the solver runs and must therefore already agree on their bin,
        and every requested cell must remain nonempty afterwards. Supplied
        labels replace the seeding of the first exchange restart only, so
        ``init`` and ``n_init`` still govern any further restart; the guarded
        Mahalanobis-Lloyd solver starts from them directly.
    """
    resolved_criterion = DOptimality() if criterion is None else criterion
    resolved_config = DExchangeConfig() if config is None else config
    if not isinstance(resolved_config, (DExchangeConfig, MahalanobisLloydConfig)):
        raise TypeError("optimize_partition requires DExchangeConfig or MahalanobisLloydConfig")
    if isinstance(resolved_criterion, DOptimality):
        return optimize_d_partition(
            scores,
            weights=weights,
            n_bins=n_bins,
            config=resolved_config,
            provenance=provenance or ScoreProvenance(),
            initial_labels=initial_labels,
        )
    if isinstance(resolved_criterion, ProfiledDOptimality):
        return optimize_profiled_d_partition(
            scores,
            weights=weights,
            n_bins=n_bins,
            criterion=resolved_criterion,
            config=resolved_config,
            provenance=provenance or ScoreProvenance(),
            initial_labels=initial_labels,
        )
    raise TypeError("finite assignment supports DOptimality or ProfiledDOptimality")


def fit_quantizer(
    source: Source,
    *,
    score: ScoreProvider | None = None,
    validation: Source | None = None,
    n_bins: int,
    criterion: Criterion | None = None,
    config: QuantizerConfig | None = None,
) -> QuantizerResult:
    """Fit a reusable hard rule from an empirical or bounded score law.

    A score callback alone is deliberately insufficient: observations must be
    paired with an empirical or integration source that defines their measure.
    """
    train, source_kind = _materialize_source(source, score)
    validation_sample = None
    if validation is not None:
        validation_provider = None if isinstance(validation, ScoreSample) else score
        validation_sample, _ = _materialize_source(validation, validation_provider)
        if validation_sample.scores.shape[1] != train.scores.shape[1]:
            raise ValueError("validation scores must use the training parameter order")
    resolved_config = DExchangeConfig() if config is None else config
    resolved_criterion: Criterion = DOptimality() if criterion is None else criterion
    _validate_solver_pair(resolved_criterion, resolved_config)

    if isinstance(resolved_config, (DExchangeConfig, MahalanobisLloydConfig)):
        if not isinstance(resolved_criterion, DOptimality):
            raise ValueError(
                "finite profiled-D exchange has no implicit inductive rule; "
                "use optimize_partition or SoftVoronoiConfig"
            )
        partition = optimize_d_partition(
            train.scores,
            weights=train.weights,
            n_bins=n_bins,
            config=resolved_config,
            provenance=train.provenance,
        )
        result = partition.compile_quantizer()
        validation_report = (
            None
            if validation_sample is None
            else result.evaluate_scores(validation_sample.scores, validation_sample.weights)
        )
        return replace(
            result,
            validation_report=validation_report,
            source_kind=source_kind,
        )

    prepared = _prepare_score_fit(
        train,
        validation_sample,
        n_bins=n_bins,
        config=resolved_config,
    )
    run = _run_geometric_quantizer(prepared, n_bins, resolved_criterion)
    diagnostics = _build_fit_diagnostics(prepared, run, n_bins, resolved_criterion)
    train_profiled_report = None
    validation_profiled_report = None
    hard_retention = diagnostics.train_report.geometric_mean_retention
    if isinstance(resolved_criterion, ProfiledDOptimality):
        train_profiled_report = profiled_information_report(
            prepared.train_sample.scores,
            diagnostics.labels,
            interest=resolved_criterion.interest,
            weights=prepared.train_sample.weights,
            n_bins=n_bins,
        )
        hard_retention = train_profiled_report.geometric_mean_retention
        if prepared.validation_sample is not None and prepared.validation_coordinates is not None:
            validation_profiled_report = profiled_information_report(
                prepared.validation_sample.scores,
                hard_assign(prepared.validation_coordinates, run.centers),
                interest=resolved_criterion.interest,
                weights=prepared.validation_sample.weights,
                n_bins=n_bins,
            )
    hardening_gap = None
    if run.soft_retention_history:
        hardening_gap = run.soft_retention_history[-1] - hard_retention
    return QuantizerResult(
        centers=run.centers,
        metric=None,
        transform=prepared.transform,
        criterion=resolved_criterion,
        config=resolved_config,
        trace=_build_optimization_trace(run, diagnostics),
        labels=diagnostics.labels,
        train_report=diagnostics.train_report,
        validation_report=diagnostics.validation_report,
        provenance=train.provenance,
        hardening_gap=hardening_gap,
        source_kind=source_kind,
        train_profiled_report=train_profiled_report,
        validation_profiled_report=validation_profiled_report,
    )


def _materialize_source(source: Source, provider: ScoreProvider | None) -> tuple[ScoreSample, str]:
    if isinstance(source, ScoreSample):
        if provider is not None:
            raise ValueError("score must be omitted when source is ScoreSample")
        return source, "score_sample"
    if isinstance(source, IntegrationSource):
        if provider is None:
            raise ValueError("IntegrationSource requires a score provider")
        observations = source.materialize()
        return (
            ScoreSample(
                provider.score(observations.observations),
                observations.weights,
                provenance=provider.provenance,
            ),
            "integration_source",
        )
    if isinstance(source, ObservationSample):
        if provider is None:
            raise ValueError("ObservationSample requires a score provider")
        return (
            ScoreSample(
                provider.score(source.observations),
                source.weights,
                provenance=provider.provenance,
            ),
            "observation_sample",
        )
    raise TypeError("source must be ScoreSample, ObservationSample, or IntegrationSource")


def _validate_solver_pair(criterion: Criterion, config: QuantizerConfig) -> None:
    if isinstance(config, KMeansConfig) and not isinstance(criterion, NormalizedTrace):
        raise ValueError("KMeansConfig implements only NormalizedTrace")
    if isinstance(config, (DExchangeConfig, MahalanobisLloydConfig)) and not isinstance(
        criterion, DOptimality
    ):
        raise ValueError(f"{type(config).__name__} implements only DOptimality")
    if isinstance(config, ScalarDPConfig) and not isinstance(criterion, DOptimality):
        raise ValueError("ScalarDPConfig implements only DOptimality")
    if isinstance(config, SoftVoronoiConfig) and not isinstance(
        criterion, (DOptimality, ProfiledDOptimality)
    ):
        raise ValueError("SoftVoronoiConfig implements DOptimality or ProfiledDOptimality")


def _prepare_score_fit(
    source: ScoreSample,
    validation: ScoreSample | None,
    *,
    n_bins: int,
    config: KMeansConfig | SoftVoronoiConfig | ScalarDPConfig,
) -> _PreparedFit:
    train_sample = validate_sample(source.scores, source.weights)
    validate_n_bins(n_bins, train_sample.n_effective)
    effective_scores, effective_weights, _ = collapse_duplicate_scores(
        train_sample.effective_scores, train_sample.effective_weights
    )
    if n_bins > effective_scores.shape[0]:
        raise ValueError("n_bins exceeds distinct positive-weight score rows")
    full_information = jnp.einsum(
        "n,np,nq->pq", effective_weights, effective_scores, effective_scores
    )
    transform = fisher_transform(
        full_information,
        whiten=config.whiten,
        rank_rtol=config.rank_rtol,
    )
    train_coordinates = transform.apply(effective_scores)
    validation_sample = (
        None
        if validation is None
        else validate_sample(
            validation.scores,
            validation.weights,
            expected_features=train_sample.scores.shape[1],
        )
    )
    return _PreparedFit(
        config=config,
        train_sample=train_sample,
        validation_sample=validation_sample,
        transform=transform,
        train_coordinates=train_coordinates,
        train_weights=effective_weights,
        train_objective_scores=effective_scores,
        all_train_coordinates=transform.apply(train_sample.scores),
        validation_coordinates=(
            None if validation_sample is None else transform.apply(validation_sample.scores)
        ),
    )


def _run_geometric_quantizer(
    prepared: _PreparedFit, n_bins: int, criterion: Criterion
) -> QuantizerRun:
    if isinstance(prepared.config, KMeansConfig):
        return weighted_kmeans(
            prepared.train_coordinates,
            prepared.train_weights,
            n_bins,
            prepared.config,
        )
    if isinstance(prepared.config, ScalarDPConfig):
        return scalar_weighted_kmeans_dp(
            prepared.train_coordinates,
            prepared.train_weights,
            n_bins,
            prepared.config,
        )
    if not isinstance(criterion, (DOptimality, ProfiledDOptimality)):
        raise ValueError("SoftVoronoiConfig requires a D-family criterion")
    return soft_voronoi(
        prepared.train_coordinates,
        prepared.train_objective_scores,
        prepared.train_weights,
        n_bins,
        prepared.transform.rank,
        criterion,
        prepared.config,
    )


def _hard_retention_history(
    scores: jnp.ndarray,
    weights: jnp.ndarray,
    transformed_scores: jnp.ndarray,
    run: QuantizerRun,
    *,
    rank_rtol: float | None,
    criterion: Criterion,
) -> list[float]:
    values: list[float] = []
    for centers in run.center_history:
        labels = hard_assign(transformed_scores, centers)
        if isinstance(criterion, ProfiledDOptimality):
            retention = profiled_information_report(
                scores,
                labels,
                interest=criterion.interest,
                weights=weights,
                n_bins=centers.shape[0],
            ).geometric_mean_retention
        else:
            retention = information_report(
                scores,
                labels,
                weights,
                n_bins=centers.shape[0],
                rank_rtol=rank_rtol,
            ).geometric_mean_retention
        values.append(retention)
    return values


def _build_fit_diagnostics(
    prepared: _PreparedFit, run: QuantizerRun, n_bins: int, criterion: Criterion
) -> _FitDiagnostics:
    labels = hard_assign(prepared.all_train_coordinates, run.centers)
    train_hard = _hard_retention_history(
        prepared.train_sample.scores,
        prepared.train_sample.weights,
        prepared.all_train_coordinates,
        run,
        rank_rtol=prepared.config.rank_rtol,
        criterion=criterion,
    )
    train_report = information_report(
        prepared.train_sample.scores,
        labels,
        prepared.train_sample.weights,
        n_bins=n_bins,
        rank_rtol=prepared.config.rank_rtol,
    )
    if prepared.validation_sample is None or prepared.validation_coordinates is None:
        return _FitDiagnostics(labels, train_report, None, train_hard, None)
    validation_hard = _hard_retention_history(
        prepared.validation_sample.scores,
        prepared.validation_sample.weights,
        prepared.validation_coordinates,
        run,
        rank_rtol=prepared.config.rank_rtol,
        criterion=criterion,
    )
    validation_report = information_report(
        prepared.validation_sample.scores,
        hard_assign(prepared.validation_coordinates, run.centers),
        prepared.validation_sample.weights,
        n_bins=n_bins,
        rank_rtol=prepared.config.rank_rtol,
    )
    return _FitDiagnostics(
        labels,
        train_report,
        validation_report,
        train_hard,
        validation_hard,
    )


def _build_optimization_trace(run: QuantizerRun, diagnostics: _FitDiagnostics) -> OptimizationTrace:
    return OptimizationTrace(
        steps=jnp.asarray(run.steps),
        centers=jnp.stack(run.center_history),
        objective=jnp.asarray(run.objective_history),
        bin_weights=jnp.stack(run.bin_weight_history),
        train_hard_retention=jnp.asarray(diagnostics.train_hard_retention),
        objective_label=run.objective_label,
        validation_hard_retention=(
            None
            if diagnostics.validation_hard_retention is None
            else jnp.asarray(diagnostics.validation_hard_retention)
        ),
        soft_retention=(
            None if run.soft_retention_history is None else jnp.asarray(run.soft_retention_history)
        ),
        temperatures=(
            None if run.temperature_history is None else jnp.asarray(run.temperature_history)
        ),
        gradient_norms=(
            None if run.gradient_norm_history is None else jnp.asarray(run.gradient_norm_history)
        ),
    )
