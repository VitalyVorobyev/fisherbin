"""Framework-neutral observation-to-score providers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

import jax.numpy as jnp
import numpy as np

from ._json import json_ready
from ._typing import ArrayLike, JsonValue
from .components import LinearComponents, mixture_scores_from_posteriors, scores_from_components
from .sources import ScoreProvenance


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


@dataclass(frozen=True, slots=True, init=False)
class MixturePosteriorTransform:
    """Convert ready multiclass posteriors into finite-mixture scores."""

    class_priors: jnp.ndarray
    reference_fractions: jnp.ndarray
    reference_component: int

    def __init__(
        self,
        class_priors: ArrayLike,
        reference_fractions: ArrayLike,
        *,
        reference_component: int = -1,
    ) -> None:
        object.__setattr__(self, "class_priors", jnp.asarray(class_priors))
        object.__setattr__(self, "reference_fractions", jnp.asarray(reference_fractions))
        object.__setattr__(self, "reference_component", reference_component)

    def transform(self, posteriors: ArrayLike) -> jnp.ndarray:
        """Apply the explicit prior-corrected mixture-score algebra."""
        return mixture_scores_from_posteriors(
            posteriors,
            self.class_priors,
            self.reference_fractions,
            reference_component=self.reference_component,
        )


@dataclass(frozen=True, slots=True, init=False)
class CentralLogRatioTransform:
    """Convert calibrated minus/plus class probabilities into central scores.

    Input has shape ``[N, P, 2]`` with class order ``(minus, plus)``. A
    two-dimensional ``[N, 2]`` input is accepted for a single score direction.
    """

    deltas: jnp.ndarray
    class_priors: jnp.ndarray

    def __init__(self, deltas: ArrayLike, class_priors: ArrayLike) -> None:
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
        object.__setattr__(self, "deltas", delta_array)
        object.__setattr__(self, "class_priors", priors)

    def transform(self, probabilities: ArrayLike) -> jnp.ndarray:
        """Apply prior correction and divide central logits by ``2 * delta``."""
        values = jnp.asarray(probabilities, dtype=self.deltas.dtype)
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


type ClassifierTransform = MixturePosteriorTransform | CentralLogRatioTransform


@dataclass(frozen=True, slots=True)
class ClassifierScore:
    """Wrap a ready classifier callback and a pure score transformation.

    Training, calibration, splitting, and model persistence remain outside the
    library. This provider always records estimated-classifier provenance.
    """

    predict: Callable[[ArrayLike], ArrayLike]
    transform: ClassifierTransform
    description: str | None = None
    metadata: Mapping[str, JsonValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the ready-predictor contract."""
        if not callable(self.predict):
            raise TypeError("predict must be callable")
        if not isinstance(self.transform, (MixturePosteriorTransform, CentralLogRatioTransform)):
            raise TypeError("transform must be a supported classifier-score transform")

    @property
    def provenance(self) -> ScoreProvenance:
        """Return non-exact classifier provenance."""
        if isinstance(self.transform, CentralLogRatioTransform):
            transform_metadata: dict[str, JsonValue] = {
                "transform": "central_log_ratio",
                "deltas": json_ready(self.transform.deltas),
                "class_priors": json_ready(self.transform.class_priors),
            }
        else:
            transform_metadata = {
                "transform": "mixture_posterior",
                "class_priors": json_ready(self.transform.class_priors),
                "reference_fractions": json_ready(self.transform.reference_fractions),
                "reference_component": self.transform.reference_component,
            }
        return ScoreProvenance(
            kind="estimated_classifier",
            description=self.description,
            metadata={**dict(self.metadata), **transform_metadata},
        )

    def score(self, observations: ArrayLike) -> jnp.ndarray:
        """Evaluate ready classifier outputs and convert them to scores."""
        return self.transform.transform(self.predict(observations))


type ScoreProvider = ScoreFunction | LinearComponentScore | ClassifierScore
