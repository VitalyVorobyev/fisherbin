"""Framework-neutral observation-to-score providers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np

from ._typing import ArrayLike, JsonValue
from .components import LinearComponents, scores_from_components
from .ratios import (
    IntensityParameterization,
    MixtureParameterization,
    RatioParameterization,
    _validate_simplex_vector,
    ratios_from_posteriors,
)
from .sources import RatioProvenance, ScoreProvenance


@dataclass(frozen=True, slots=True)
class ScoreFunction:
    """Wrap an exact or estimated callable ``[N, D] -> [N, P]``."""

    function: Callable[[ArrayLike], ArrayLike]
    provenance: ScoreProvenance = ScoreProvenance()

    def __post_init__(self) -> None:
        """Reject non-callable providers at construction time."""
        if not callable(self.function):
            raise TypeError("function must be callable")

    def score(self, observations: ArrayLike) -> jnp.ndarray:
        """Evaluate and validate a finite score matrix."""
        values = jnp.asarray(self.function(observations))
        if values.ndim != 2 or values.shape[0] != jnp.asarray(observations).shape[0]:
            raise ValueError("score function must return shape [N, P]")
        if values.shape[1] == 0 or not bool(np.asarray(jnp.all(jnp.isfinite(values)))):
            raise ValueError("score function must return finite non-empty scores")
        return values


@dataclass(frozen=True, slots=True)
class LinearComponentScore:
    """Evaluate a frozen linear-component model and return local scores."""

    model: LinearComponents
    provenance: ScoreProvenance = ScoreProvenance(
        kind="exact", description="linear-component event score"
    )

    def __post_init__(self) -> None:
        """Validate the model boundary."""
        if not isinstance(self.model, LinearComponents):
            raise TypeError("model must be LinearComponents")

    def score(self, observations: ArrayLike) -> jnp.ndarray:
        """Evaluate components and their frozen reference score."""
        components = self.model.evaluate_components(observations)
        return scores_from_components(components, self.model.coefficients)


def _parameterization_facts(parameterization: RatioParameterization) -> RatioProvenance:
    if isinstance(parameterization, IntensityParameterization):
        return RatioProvenance(
            parameterization="intensity",
            coefficients=tuple(float(value) for value in parameterization.coefficients),
        )
    return RatioProvenance(
        parameterization="mixture",
        reference_fractions=tuple(float(value) for value in parameterization.reference_fractions),
        reference_component=parameterization.reference_component % parameterization.n_components,
    )


def _merge_ratio_provenance(
    supplied: RatioProvenance | None, facts: RatioProvenance
) -> RatioProvenance:
    if supplied is None:
        return facts
    for field_name in (
        "parameterization",
        "coefficients",
        "reference_fractions",
        "reference_component",
    ):
        supplied_value = getattr(supplied, field_name)
        derived_value = getattr(facts, field_name)
        if supplied_value is not None and supplied_value != derived_value:
            raise ValueError(
                f"provenance.ratio.{field_name}={supplied_value!r} conflicts with the "
                f"declared parameterization value {derived_value!r}"
            )
    return RatioProvenance(
        estimator=supplied.estimator,
        parameterization=facts.parameterization,
        coefficients=facts.coefficients,
        reference_fractions=facts.reference_fractions,
        reference_component=facts.reference_component,
        training_priors=supplied.training_priors,
        calibration=supplied.calibration,
        deltas=supplied.deltas,
    )


@dataclass(frozen=True, slots=True, init=False)
class DensityRatioScore:
    """Map observations to model density ratios and evaluate declared scores.

    The ratio callback is the statistical representation: any oracle for the
    component density ratios — an analytic formula, a calibrated classifier,
    a direct ratio estimator such as KLIEP or uLSIF, or an external ratio
    model — determines the score once a parameterization declares how the
    components combine. Ratio estimation, calibration, and cross-fitting stay
    outside the library.

    Parameters
    ----------
    ratio
        Callable ``[N, D] -> [N, K]`` returning finite nonnegative model
        density ratios, defined up to one common event-wise factor.
    parameterization
        ``IntensityParameterization`` or ``MixtureParameterization`` declaring
        the ratio-to-score map and the reference point.
    provenance
        Optional score provenance. Estimated ratios are the default
        (``kind="estimated_ratio"``); an analytic ratio may declare
        ``kind="exact"`` under the same caller responsibility as
        ``ScoreFunction``. Parameterization facts are always recorded in
        ``provenance.ratio`` and a conflicting supplied record is rejected.
    """

    ratio: Callable[[ArrayLike], ArrayLike]
    parameterization: RatioParameterization
    provenance: ScoreProvenance

    def __init__(
        self,
        ratio: Callable[[ArrayLike], ArrayLike],
        parameterization: RatioParameterization,
        *,
        provenance: ScoreProvenance | None = None,
    ) -> None:
        if not callable(ratio):
            raise TypeError("ratio must be callable")
        if not isinstance(parameterization, (IntensityParameterization, MixtureParameterization)):
            raise TypeError(
                "parameterization must be IntensityParameterization or MixtureParameterization"
            )
        facts = _parameterization_facts(parameterization)
        if provenance is None:
            resolved = ScoreProvenance(kind="estimated_ratio", ratio=facts)
        else:
            resolved = ScoreProvenance(
                kind=provenance.kind,
                description=provenance.description,
                reference_point=provenance.reference_point,
                metadata=provenance.metadata,
                ratio=_merge_ratio_provenance(provenance.ratio, facts),
            )
        object.__setattr__(self, "ratio", ratio)
        object.__setattr__(self, "parameterization", parameterization)
        object.__setattr__(self, "provenance", resolved)

    @classmethod
    def from_classifier(
        cls,
        predict: Callable[[ArrayLike], ArrayLike],
        class_priors: ArrayLike,
        parameterization: RatioParameterization,
        *,
        calibration: str | None = None,
        description: str | None = None,
        metadata: Mapping[str, JsonValue] | None = None,
    ) -> DensityRatioScore:
        """Build a ratio provider from a calibrated multiclass classifier.

        The classifier is one estimator of density ratios: calibrated
        posteriors ``eta_k`` under training priors ``pi_k`` give
        ``r_k = eta_k / pi_k`` up to a common event-wise factor, so the
        scores are ``(eta_k / pi_k) / sum_j theta_j eta_j / pi_j`` under the
        intensity parameterization. When ``pi`` is proportional to
        ``theta_0`` the denominator is identically one. The provider always
        records estimated provenance — a classifier-derived ratio can never
        claim exact Fisher semantics.

        Parameters
        ----------
        predict
            Callable ``[N, D] -> [N, K]`` returning calibrated posterior
            rows summing to one.
        class_priors
            Strictly positive training priors with shape ``[K]`` and unit
            sum.
        parameterization
            Ratio-to-score map; ``K`` must match its component count.
        calibration
            Optional name of the upstream calibration method, recorded in
            provenance.
        description, metadata
            Optional free-form provenance carried on the score record.
        """
        if not callable(predict):
            raise TypeError("predict must be callable")
        priors = jnp.asarray(class_priors)
        if not isinstance(parameterization, (IntensityParameterization, MixtureParameterization)):
            raise TypeError(
                "parameterization must be IntensityParameterization or MixtureParameterization"
            )
        _validate_simplex_vector(priors, "class_priors", parameterization.n_components)

        def ratio(observations: ArrayLike) -> jnp.ndarray:
            return ratios_from_posteriors(predict(observations), priors)

        provenance = ScoreProvenance(
            kind="estimated_ratio",
            description=description,
            metadata={} if metadata is None else metadata,
            ratio=RatioProvenance(
                estimator="calibrated_classifier",
                training_priors=tuple(float(value) for value in priors),
                calibration=calibration,
            ),
        )
        return cls(ratio, parameterization, provenance=provenance)

    def score(self, observations: ArrayLike) -> jnp.ndarray:
        """Evaluate the ratio callback and apply the declared score map."""
        values = jnp.asarray(self.ratio(observations))
        if values.ndim != 2 or values.shape[0] != jnp.asarray(observations).shape[0]:
            raise ValueError("ratio callback must return shape [N, K]")
        expected = self.parameterization.n_components
        if values.shape[1] != expected:
            raise ValueError(
                f"ratio callback must return {expected} components, got {values.shape[1]}"
            )
        return self.parameterization.scores(values)


@dataclass(frozen=True, slots=True, init=False)
class CentralLogRatioScore:
    """Estimate central finite-difference scores from paired density ratios.

    A calibrated classifier trained to separate samples generated at
    ``theta_0 - delta e_p`` from ``theta_0 + delta e_p`` estimates the
    directional log density ratio, and
    ``(log(p_plus / p_minus) - log(pi_plus / pi_minus)) / (2 delta)`` is a
    central finite-difference estimate of the score component ``s_p``. The
    prediction callback must return shape ``[N, P, 2]`` with class order
    ``(minus, plus)``; a two-dimensional ``[N, 2]`` input is accepted for a
    single score direction. Provenance is always estimated.

    Parameters
    ----------
    predict
        Callable returning calibrated minus/plus probability pairs.
    deltas
        Strictly positive finite-difference offsets with shape ``[P]``.
    class_priors
        Training priors per direction with shape ``[2]`` or ``[P, 2]``;
        rows are normalized to sum to one.
    description, metadata
        Optional free-form provenance carried on the score record.
    """

    predict: Callable[[ArrayLike], ArrayLike]
    deltas: jnp.ndarray
    class_priors: jnp.ndarray
    description: str | None
    metadata: Mapping[str, JsonValue]

    def __init__(
        self,
        predict: Callable[[ArrayLike], ArrayLike],
        deltas: ArrayLike,
        class_priors: ArrayLike,
        *,
        description: str | None = None,
        metadata: Mapping[str, JsonValue] | None = None,
    ) -> None:
        if not callable(predict):
            raise TypeError("predict must be callable")
        delta_array = jnp.asarray(deltas)
        if delta_array.ndim != 1 or delta_array.shape[0] == 0:
            raise ValueError("deltas must have shape [P]")
        if not bool(np.asarray(jnp.all(jnp.isfinite(delta_array)))) or bool(
            np.asarray(jnp.any(delta_array <= 0))
        ):
            raise ValueError("deltas must be finite and positive")
        priors = jnp.asarray(class_priors, dtype=delta_array.dtype)
        if priors.shape == (2,):
            priors = jnp.broadcast_to(priors, (delta_array.shape[0], 2))
        if priors.shape != (delta_array.shape[0], 2):
            raise ValueError("class_priors must have shape [2] or [P, 2]")
        if not bool(np.asarray(jnp.all(jnp.isfinite(priors)))) or bool(
            np.asarray(jnp.any(priors <= 0))
        ):
            raise ValueError("class_priors must be finite and positive")
        priors = priors / jnp.sum(priors, axis=1, keepdims=True)
        object.__setattr__(self, "predict", predict)
        object.__setattr__(self, "deltas", delta_array)
        object.__setattr__(self, "class_priors", priors)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "metadata", {} if metadata is None else metadata)

    @property
    def provenance(self) -> ScoreProvenance:
        """Return estimated-ratio provenance with the central-difference facts."""
        return ScoreProvenance(
            kind="estimated_ratio",
            description=self.description,
            metadata=self.metadata,
            ratio=RatioProvenance(
                estimator="calibrated_classifier",
                parameterization="central_log_ratio",
                training_priors=tuple(
                    (float(row[0]), float(row[1])) for row in np.asarray(self.class_priors)
                ),
                deltas=tuple(float(value) for value in self.deltas),
            ),
        )

    def score(self, observations: ArrayLike) -> jnp.ndarray:
        """Apply prior correction and divide central logits by ``2 * delta``."""
        values = jnp.asarray(self.predict(observations), dtype=self.deltas.dtype)
        if values.ndim == 2 and values.shape[1] == 2 and self.deltas.shape[0] == 1:
            values = values[:, None, :]
        if values.ndim != 3 or values.shape[1:] != self.class_priors.shape:
            raise ValueError(f"probabilities must have shape [N, {self.deltas.shape[0]}, 2]")
        if not bool(np.asarray(jnp.all(jnp.isfinite(values)))) or bool(
            np.asarray(jnp.any(values <= 0))
        ):
            raise ValueError("probabilities must be finite and strictly positive")
        if not bool(np.asarray(jnp.allclose(jnp.sum(values, axis=2), 1))):
            raise ValueError("classifier probability pairs must sum to one")
        log_ratio = jnp.log(values[:, :, 1] / values[:, :, 0])
        prior_log_ratio = jnp.log(self.class_priors[:, 1] / self.class_priors[:, 0])
        return (log_ratio - prior_log_ratio[None, :]) / (2 * self.deltas[None, :])


type ScoreProvider = ScoreFunction | LinearComponentScore | DensityRatioScore | CentralLogRatioScore
