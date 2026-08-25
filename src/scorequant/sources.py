"""Reference-measure sources for empirical and bounded population fitting."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Literal

import jax.numpy as jnp
import numpy as np

from ._json import json_ready
from ._typing import ArrayLike, JsonValue
from ._validation import validate_sample

type ScoreKind = Literal[
    "unknown",
    "exact",
    "autodiff",
    "estimated_classifier",
    "custom_estimated",
]


@dataclass(frozen=True, slots=True)
class ScoreProvenance:
    """Describe where supplied score coordinates came from.

    ``exact_fisher`` is derived from ``kind`` rather than accepted as an
    independent flag, so estimated scores cannot accidentally claim exact
    Fisher semantics.
    """

    kind: ScoreKind = "unknown"
    description: str | None = None
    reference_point: tuple[float, ...] | None = None
    metadata: Mapping[str, JsonValue] = field(default_factory=dict)

    @property
    def exact_fisher(self) -> bool:
        """Return whether exact-Fisher language is permitted."""
        return self.kind in ("exact", "autodiff")

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible provenance mapping."""
        return json_ready(
            {
                "kind": self.kind,
                "description": self.description,
                "reference_point": self.reference_point,
                "metadata": dict(self.metadata),
                "exact_fisher": self.exact_fisher,
            }
        )


@dataclass(frozen=True, slots=True, init=False)
class ScoreSample:
    """A finite weighted score table representing an empirical score law."""

    scores: jnp.ndarray
    weights: jnp.ndarray
    provenance: ScoreProvenance

    def __init__(
        self,
        scores: ArrayLike,
        weights: ArrayLike | None = None,
        *,
        provenance: ScoreProvenance | None = None,
    ) -> None:
        sample = validate_sample(scores, weights)
        object.__setattr__(self, "scores", sample.scores)
        object.__setattr__(self, "weights", sample.weights)
        object.__setattr__(self, "provenance", provenance or ScoreProvenance())


@dataclass(frozen=True, slots=True, init=False)
class ObservationSample:
    """A finite weighted observation table requiring a score provider."""

    observations: jnp.ndarray
    weights: jnp.ndarray

    def __init__(self, observations: ArrayLike, weights: ArrayLike | None = None) -> None:
        array = jnp.asarray(observations)
        if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
            raise ValueError("observations must have non-empty shape [N, D]")
        if not jnp.issubdtype(array.dtype, jnp.inexact):
            array = array.astype(jnp.float32)
        if not bool(np.asarray(jnp.all(jnp.isfinite(array)))):
            raise ValueError("observations must be finite")
        weight_array = (
            jnp.ones(array.shape[0], dtype=array.dtype)
            if weights is None
            else jnp.asarray(weights, dtype=array.dtype)
        )
        if weight_array.shape != (array.shape[0],):
            raise ValueError(f"weights must have shape [{array.shape[0]}]")
        if not bool(np.asarray(jnp.all(jnp.isfinite(weight_array)))):
            raise ValueError("weights must be finite")
        if bool(np.asarray(jnp.any(weight_array < 0))):
            raise ValueError("weights must be nonnegative")
        if not bool(np.asarray(jnp.any(weight_array > 0))):
            raise ValueError("at least one weight must be positive")
        object.__setattr__(self, "observations", array)
        object.__setattr__(self, "weights", weight_array)


@dataclass(frozen=True, slots=True)
class GaussLegendreConfig:
    """Configure deterministic tensor-product Gauss-Legendre quadrature."""

    order: int = 16
    max_points: int = 1_000_000

    def __post_init__(self) -> None:
        """Validate quadrature capacity before materialization."""
        if isinstance(self.order, bool) or not isinstance(self.order, int) or self.order < 2:
            raise ValueError("order must be an integer of at least two")
        if (
            isinstance(self.max_points, bool)
            or not isinstance(self.max_points, int)
            or self.max_points < 1
        ):
            raise ValueError("max_points must be a positive integer")


@dataclass(frozen=True, slots=True, init=False)
class IntegrationSource:
    """A finite box, density, and deterministic quadrature reference measure.

    This source is intentionally limited to low-dimensional bounded domains.
    The density or intensity is mandatory; bounds alone never imply a uniform
    statistical measure.
    """

    bounds: jnp.ndarray
    density: Callable[[ArrayLike], ArrayLike]
    quadrature: GaussLegendreConfig

    def __init__(
        self,
        bounds: ArrayLike,
        *,
        density: Callable[[ArrayLike], ArrayLike],
        quadrature: GaussLegendreConfig | None = None,
    ) -> None:
        array = jnp.asarray(bounds)
        if array.ndim != 2 or array.shape[1] != 2 or array.shape[0] == 0:
            raise ValueError("bounds must have shape [D, 2]")
        if not jnp.issubdtype(array.dtype, jnp.inexact):
            array = array.astype(jnp.float32)
        if not bool(np.asarray(jnp.all(jnp.isfinite(array)))):
            raise ValueError("bounds must be finite")
        if not bool(np.asarray(jnp.all(array[:, 1] > array[:, 0]))):
            raise ValueError("every upper bound must be greater than its lower bound")
        if not callable(density):
            raise TypeError("density must be callable")
        object.__setattr__(self, "bounds", array)
        object.__setattr__(self, "density", density)
        object.__setattr__(self, "quadrature", quadrature or GaussLegendreConfig())

    def materialize(self) -> ObservationSample:
        """Evaluate tensor quadrature nodes and density-weighted measure weights."""
        dimension = int(self.bounds.shape[0])
        point_count = self.quadrature.order**dimension
        if point_count > self.quadrature.max_points:
            raise ValueError(
                "tensor quadrature would create "
                f"{point_count} points, exceeding max_points={self.quadrature.max_points}"
            )
        canonical_nodes, canonical_weights = np.polynomial.legendre.leggauss(self.quadrature.order)
        nodes_per_axis: list[np.ndarray] = []
        weights_per_axis: list[np.ndarray] = []
        for lower, upper in np.asarray(self.bounds):
            half_width = 0.5 * (upper - lower)
            midpoint = 0.5 * (upper + lower)
            nodes_per_axis.append(midpoint + half_width * canonical_nodes)
            weights_per_axis.append(half_width * canonical_weights)
        node_mesh = np.meshgrid(*nodes_per_axis, indexing="ij")
        weight_mesh = np.meshgrid(*weights_per_axis, indexing="ij")
        observations = np.stack([axis.reshape(-1) for axis in node_mesh], axis=1)
        quadrature_weights = np.prod(
            np.stack([axis.reshape(-1) for axis in weight_mesh], axis=1), axis=1
        )
        density_values = jnp.asarray(self.density(observations))
        if density_values.shape != (point_count,):
            raise ValueError(f"density must return shape [{point_count}]")
        if not bool(np.asarray(jnp.all(jnp.isfinite(density_values)))):
            raise ValueError("density values must be finite")
        if bool(np.asarray(jnp.any(density_values < 0))):
            raise ValueError("density values must be nonnegative")
        weights = density_values * jnp.asarray(quadrature_weights, dtype=density_values.dtype)
        return ObservationSample(observations, weights)


type Source = ScoreSample | ObservationSample | IntegrationSource
