"""Representation-explicit public fitting workflows."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np

from ._typing import ArrayLike
from ._validation import _ValidatedSample, validate_n_bins, validate_sample
from .components import LinearComponents, LinearProblem
from .config import FitConfig, KMeansConfig, SoftVoronoiConfig
from .information import _unbinned_fisher, information_report
from .quantizers import QuantizerRun, hard_assign, soft_voronoi, weighted_kmeans
from .result import (
    ComponentFitResult,
    FitResult,
    InformationReport,
    ModelFitResult,
    OptimizationTrace,
)
from .transforms import FisherTransform, fisher_transform


@dataclass(frozen=True, slots=True)
class _PreparedFit:
    """Validated score samples and their fitted optimization coordinates."""

    config: FitConfig
    train_sample: _ValidatedSample
    validation_sample: _ValidatedSample | None
    transform: FisherTransform
    train_coordinates: jnp.ndarray
    all_train_coordinates: jnp.ndarray
    validation_coordinates: jnp.ndarray | None


@dataclass(frozen=True, slots=True)
class _FitDiagnostics:
    """Final labels, reports, and hardened-retention histories."""

    labels: jnp.ndarray
    train_report: InformationReport
    validation_report: InformationReport | None
    train_hard_retention: list[float]
    validation_hard_retention: list[float] | None


def _hard_retention_history(
    scores: jnp.ndarray,
    weights: ArrayLike | None,
    transformed_scores: jnp.ndarray,
    run: QuantizerRun,
    *,
    rank_rtol: float | None,
) -> list[float]:
    values: list[float] = []
    for centers in run.center_history:
        labels = hard_assign(transformed_scores, centers)
        report = information_report(
            scores, labels, weights, n_bins=centers.shape[0], rank_rtol=rank_rtol
        )
        values.append(report.geometric_mean_retention)
    return values


def _prepare_score_fit(
    scores: ArrayLike,
    weights: ArrayLike | None,
    n_bins: int,
    config: FitConfig | None,
    validation_scores: ArrayLike | None,
    validation_weights: ArrayLike | None,
) -> _PreparedFit:
    resolved_config = KMeansConfig() if config is None else config
    if not isinstance(resolved_config, (KMeansConfig, SoftVoronoiConfig)):
        raise TypeError("config must be KMeansConfig or SoftVoronoiConfig")
    train_sample = validate_sample(scores, weights)
    validate_n_bins(n_bins, train_sample.n_effective)
    transform = fisher_transform(
        _unbinned_fisher(train_sample),
        whiten=resolved_config.whiten,
        rank_rtol=resolved_config.rank_rtol,
    )
    train_coordinates = transform.apply(train_sample.effective_scores)
    unique_count = np.unique(np.asarray(train_coordinates), axis=0).shape[0]
    if n_bins > unique_count:
        raise ValueError("n_bins exceeds the number of distinct positive-weight score coordinates")

    if validation_scores is None:
        if validation_weights is not None:
            raise ValueError("validation_weights requires validation_scores")
        validation_sample = None
        validation_coordinates = None
    else:
        validation_sample = validate_sample(
            validation_scores,
            validation_weights,
            expected_features=train_sample.scores.shape[1],
        )
        validation_coordinates = transform.apply(validation_sample.scores)
    return _PreparedFit(
        config=resolved_config,
        train_sample=train_sample,
        validation_sample=validation_sample,
        transform=transform,
        train_coordinates=train_coordinates,
        all_train_coordinates=transform.apply(train_sample.scores),
        validation_coordinates=validation_coordinates,
    )


def _run_quantizer(prepared: _PreparedFit, n_bins: int) -> QuantizerRun:
    if isinstance(prepared.config, KMeansConfig):
        return weighted_kmeans(
            prepared.train_coordinates,
            prepared.train_sample.effective_weights,
            n_bins,
            prepared.config,
        )
    return soft_voronoi(
        prepared.train_coordinates,
        prepared.train_sample.effective_weights,
        n_bins,
        prepared.transform.rank,
        prepared.config,
    )


def _build_fit_diagnostics(
    prepared: _PreparedFit,
    run: QuantizerRun,
    n_bins: int,
) -> _FitDiagnostics:
    train_hard = _hard_retention_history(
        prepared.train_sample.scores,
        prepared.train_sample.weights,
        prepared.all_train_coordinates,
        run,
        rank_rtol=prepared.config.rank_rtol,
    )
    labels = hard_assign(prepared.all_train_coordinates, run.centers)
    train_report = information_report(
        prepared.train_sample.scores,
        labels,
        prepared.train_sample.weights,
        n_bins=n_bins,
        rank_rtol=prepared.config.rank_rtol,
    )
    if prepared.validation_sample is None or prepared.validation_coordinates is None:
        validation_hard = None
        validation_report = None
    else:
        validation_hard = _hard_retention_history(
            prepared.validation_sample.scores,
            prepared.validation_sample.weights,
            prepared.validation_coordinates,
            run,
            rank_rtol=prepared.config.rank_rtol,
        )
        validation_report = information_report(
            prepared.validation_sample.scores,
            hard_assign(prepared.validation_coordinates, run.centers),
            prepared.validation_sample.weights,
            n_bins=n_bins,
            rank_rtol=prepared.config.rank_rtol,
        )
    return _FitDiagnostics(
        labels=labels,
        train_report=train_report,
        validation_report=validation_report,
        train_hard_retention=train_hard,
        validation_hard_retention=validation_hard,
    )


def _build_optimization_trace(
    run: QuantizerRun,
    diagnostics: _FitDiagnostics,
) -> OptimizationTrace:
    return OptimizationTrace(
        steps=jnp.asarray(run.steps),
        centers=jnp.stack(run.center_history),
        objective=jnp.asarray(run.objective_history),
        bin_weights=jnp.stack(run.bin_weight_history),
        train_hard_retention=jnp.asarray(diagnostics.train_hard_retention),
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


def fit_scores(
    scores: ArrayLike,
    *,
    weights: ArrayLike | None = None,
    n_bins: int,
    config: FitConfig | None = None,
    validation_scores: ArrayLike | None = None,
    validation_weights: ArrayLike | None = None,
) -> FitResult:
    """Fit an information-preserving hard partition in score space.

    Parameters
    ----------
    scores
        Finite score matrix with shape ``[N, P]``.
    weights
        Optional finite, nonnegative measure weights with shape ``[N]``.
        Zero-weight rows are ignored during fitting but remain predictable.
    n_bins
        Number of hard bins to fit.
    config
        Validated optimizer configuration. Defaults to `KMeansConfig`.
    validation_scores
        Optional held-out score matrix with shape ``[N_valid, P]``.
    validation_weights
        Optional weights aligned with ``validation_scores``.

    Returns
    -------
    FitResult
        Frozen score-space partition, training labels, reports, and trace.

    Notes
    -----
    Scores are projected onto informative Fisher directions and are never
    mean-centered. Validation data is diagnostic only: it never affects
    gradients, stopping, checkpoint selection, or returned centers.

    Raises
    ------
    ValueError
        If inputs violate the numerical contract or the requested partition
        cannot be represented by the effective score coordinates.
    """
    prepared = _prepare_score_fit(
        scores,
        weights,
        n_bins,
        config,
        validation_scores,
        validation_weights,
    )
    run = _run_quantizer(prepared, n_bins)
    diagnostics = _build_fit_diagnostics(prepared, run, n_bins)
    return FitResult(
        centers=run.centers,
        transform=prepared.transform,
        config=prepared.config,
        trace=_build_optimization_trace(run, diagnostics),
        labels=diagnostics.labels,
        train_report=diagnostics.train_report,
        validation_report=diagnostics.validation_report,
    )


def _coerce_problem(
    components: ArrayLike | LinearProblem,
    coefficients: ArrayLike | None,
    weights: ArrayLike | None,
    component_names: Sequence[str] | None,
) -> LinearProblem:
    if isinstance(components, LinearProblem):
        if coefficients is not None or weights is not None or component_names is not None:
            raise ValueError(
                "coefficients, weights, and component_names must be omitted "
                "when passing LinearProblem"
            )
        return components
    if coefficients is None:
        raise ValueError("coefficients are required when components is a matrix")
    return LinearProblem(
        components=components,
        coefficients=coefficients,
        weights=weights,
        component_names=component_names,
    )


def fit_components(
    components: ArrayLike | LinearProblem,
    *,
    coefficients: ArrayLike | None = None,
    weights: ArrayLike | None = None,
    component_names: Sequence[str] | None = None,
    n_bins: int,
    config: FitConfig | None = None,
    validation_components: ArrayLike | LinearProblem | None = None,
    validation_weights: ArrayLike | None = None,
) -> ComponentFitResult:
    """Fit from evaluated linear components or a `LinearProblem`.

    Parameters
    ----------
    components
        Component matrix with shape ``[N, M]`` or an evaluated problem.
    coefficients
        Reference coefficients with shape ``[M]``. Required for a matrix and
        omitted for a `LinearProblem`.
    weights
        Optional integration weights for a matrix input.
    component_names
        Optional stable component names for a matrix input.
    n_bins
        Number of hard bins to fit.
    config
        Validated optimizer configuration. Defaults to `KMeansConfig`.
    validation_components
        Optional held-out component matrix or compatible evaluated problem.
    validation_weights
        Optional weights for a held-out matrix.

    Returns
    -------
    ComponentFitResult
        Frozen partition whose prediction input is a component matrix.

    Notes
    -----
    Matrix inputs require reference ``coefficients``. A ``LinearProblem``
    already owns coefficients, weights, and component names, so conflicting
    keyword values are rejected rather than silently overridden.
    """
    problem = _coerce_problem(components, coefficients, weights, component_names)
    if validation_components is None:
        if validation_weights is not None:
            raise ValueError("validation_weights requires validation_components")
        validation_problem = None
    elif isinstance(validation_components, LinearProblem):
        if validation_weights is not None:
            raise ValueError("validation_weights must be omitted for validation LinearProblem")
        validation_problem = validation_components
        if validation_problem.component_names != problem.component_names:
            raise ValueError("validation problem component names must match the fitting problem")
        if not bool(
            np.asarray(jnp.allclose(validation_problem.coefficients, problem.coefficients))
        ):
            raise ValueError("validation problem coefficients must match the fitting problem")
    else:
        validation_problem = LinearProblem(
            components=validation_components,
            coefficients=problem.coefficients,
            weights=validation_weights,
            component_names=problem.component_names,
        )

    score_result = fit_scores(
        problem.scores,
        weights=problem.weights,
        n_bins=n_bins,
        config=config,
        validation_scores=(None if validation_problem is None else validation_problem.scores),
        validation_weights=(None if validation_problem is None else validation_problem.weights),
    )
    return ComponentFitResult(
        score_result=score_result,
        coefficients=problem.coefficients,
        component_names=problem.component_names,
    )


def fit(
    X: ArrayLike,
    *,
    model: LinearComponents,
    weights: ArrayLike | None = None,
    n_bins: int,
    config: FitConfig | None = None,
    validation_X: ArrayLike | None = None,
    validation_weights: ArrayLike | None = None,
) -> ModelFitResult:
    """Fit from physical variables through a linear component model.

    Parameters
    ----------
    X
        Finite numeric physical-variable matrix with shape ``[N, K]``.
    model
        Vectorized component model evaluated before score-space fitting.
    weights
        Optional finite, nonnegative integration weights with shape ``[N]``.
    n_bins
        Number of hard bins to fit.
    config
        Validated optimizer configuration. Defaults to `KMeansConfig`.
    validation_X
        Optional held-out physical-variable matrix.
    validation_weights
        Optional weights aligned with ``validation_X``.

    Returns
    -------
    ModelFitResult
        Frozen partition that retains the model and predicts from new ``X``.
    """
    if not isinstance(model, LinearComponents):
        raise TypeError("model must be LinearComponents")
    problem = model.evaluate(X, weights=weights)
    if validation_X is None:
        if validation_weights is not None:
            raise ValueError("validation_weights requires validation_X")
        validation_problem = None
    else:
        validation_problem = model.evaluate(validation_X, weights=validation_weights)
    component_result = fit_components(
        problem,
        n_bins=n_bins,
        config=config,
        validation_components=validation_problem,
    )
    return ModelFitResult(component_result=component_result, model=model)
