"""Representation-explicit public fitting workflows."""

from __future__ import annotations

from typing import Any

import jax.numpy as jnp
import numpy as np

from ._validation import validate_n_bins, validate_scores_weights
from .components import LinearComponents, LinearProblem
from .config import FitConfig, KMeansConfig, SoftVoronoiConfig
from .information import fisher_information, information_report
from .quantizers import QuantizerRun, hard_assign, soft_voronoi, weighted_kmeans
from .result import ComponentFitResult, FitResult, ModelFitResult, OptimizationTrace
from .transforms import fisher_transform


def _hard_retention_history(
    scores: jnp.ndarray,
    weights: Any | None,
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


def fit_scores(
    scores: Any,
    *,
    weights: Any | None = None,
    n_bins: int,
    config: FitConfig | None = None,
    validation_scores: Any | None = None,
    validation_weights: Any | None = None,
) -> FitResult:
    """Fit an information-preserving hard partition in score space.

    Validation data is diagnostic only: it never affects gradients, stopping,
    checkpoint selection, or the returned final centers.
    """

    resolved_config = KMeansConfig() if config is None else config
    if not isinstance(resolved_config, (KMeansConfig, SoftVoronoiConfig)):
        raise TypeError("config must be KMeansConfig or SoftVoronoiConfig")
    raw_scores = jnp.asarray(scores)
    train_scores, train_weights = validate_scores_weights(raw_scores, weights)
    validate_n_bins(n_bins, train_scores.shape[0])
    train_fisher = fisher_information(train_scores, train_weights)
    transform = fisher_transform(
        train_fisher,
        whiten=resolved_config.whiten,
        rank_rtol=resolved_config.rank_rtol,
    )
    train_coordinates = transform.apply(train_scores)
    unique_count = np.unique(np.asarray(train_coordinates), axis=0).shape[0]
    if n_bins > unique_count:
        raise ValueError("n_bins exceeds the number of distinct positive-weight score coordinates")

    if validation_scores is None:
        if validation_weights is not None:
            raise ValueError("validation_weights requires validation_scores")
        raw_validation_scores = None
        validation_coordinates = None
    else:
        raw_validation_scores = jnp.asarray(validation_scores)
        valid_scores, _ = validate_scores_weights(
            raw_validation_scores,
            validation_weights,
            expected_features=train_scores.shape[1],
        )
        # Trace metrics need one coordinate per original row, including zero-weight rows.
        transform.apply(valid_scores)
        validation_coordinates = transform.apply(raw_validation_scores)

    if isinstance(resolved_config, KMeansConfig):
        run = weighted_kmeans(train_coordinates, train_weights, n_bins, resolved_config)
    else:
        run = soft_voronoi(
            train_coordinates,
            train_weights,
            n_bins,
            transform.rank,
            resolved_config,
        )

    # Use the original row count for labels; zero-weight rows remain
    # predictable but do not contribute.
    all_train_coordinates = transform.apply(raw_scores)
    train_hard = _hard_retention_history(
        raw_scores,
        weights,
        all_train_coordinates,
        run,
        rank_rtol=resolved_config.rank_rtol,
    )
    if raw_validation_scores is None or validation_coordinates is None:
        validation_hard = None
    else:
        validation_hard = _hard_retention_history(
            raw_validation_scores,
            validation_weights,
            validation_coordinates,
            run,
            rank_rtol=resolved_config.rank_rtol,
        )

    final_train_labels = hard_assign(all_train_coordinates, run.centers)
    train_report = information_report(
        raw_scores,
        final_train_labels,
        weights,
        n_bins=n_bins,
        rank_rtol=resolved_config.rank_rtol,
    )
    if raw_validation_scores is None or validation_coordinates is None:
        validation_report = None
    else:
        validation_report = information_report(
            raw_validation_scores,
            hard_assign(validation_coordinates, run.centers),
            validation_weights,
            n_bins=n_bins,
            rank_rtol=resolved_config.rank_rtol,
        )

    trace = OptimizationTrace(
        steps=jnp.asarray(run.steps),
        centers=jnp.stack(run.center_history),
        objective=jnp.asarray(run.objective_history),
        bin_weights=jnp.stack(run.bin_weight_history),
        train_hard_retention=jnp.asarray(train_hard),
        validation_hard_retention=(
            None if validation_hard is None else jnp.asarray(validation_hard)
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
    return FitResult(
        centers=run.centers,
        transform=transform,
        config=resolved_config,
        trace=trace,
        labels=final_train_labels,
        train_report=train_report,
        validation_report=validation_report,
    )


def _coerce_problem(
    components: Any | LinearProblem,
    coefficients: Any | None,
    weights: Any | None,
    component_names: Any | None,
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
    components: Any | LinearProblem,
    *,
    coefficients: Any | None = None,
    weights: Any | None = None,
    component_names: Any | None = None,
    n_bins: int,
    config: FitConfig | None = None,
    validation_components: Any | LinearProblem | None = None,
    validation_weights: Any | None = None,
) -> ComponentFitResult:
    """Fit from evaluated component values or a :class:`LinearProblem`.

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
    X: Any,
    *,
    model: LinearComponents,
    weights: Any | None = None,
    n_bins: int,
    config: FitConfig | None = None,
    validation_X: Any | None = None,
    validation_weights: Any | None = None,
) -> ModelFitResult:
    """Fit from physical variables through a frozen linear component model."""

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
