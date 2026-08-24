"""Linear-intensity models and adapters to FisherBin's score representation."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import jax.numpy as jnp
import numpy as np

from ._json import json_ready

ComponentFunction = Callable[[np.ndarray], Any]


def _names(
    names: Sequence[str] | None,
    size: int,
    *,
    prefix: str,
) -> tuple[str, ...]:
    resolved = (
        tuple(f"{prefix}_{index}" for index in range(size)) if names is None else tuple(names)
    )
    if len(resolved) != size:
        raise ValueError(f"expected {size} {prefix} names, got {len(resolved)}")
    if any(not isinstance(name, str) or not name for name in resolved):
        raise ValueError(f"{prefix} names must be non-empty strings")
    if len(set(resolved)) != len(resolved):
        raise ValueError(f"{prefix} names must be unique")
    return resolved


def scores_from_components(components: Any, coefficients: Any) -> jnp.ndarray:
    """Return scores for ``lambda(x) = sum_k theta[k] * phi_k(x)``.

    Components and coefficients may be signed and need not be normalized.
    They must be finite, and their resulting reference intensity must be
    strictly positive at every supplied integration point.
    """

    component_array = jnp.asarray(components)
    if component_array.ndim != 2 or min(component_array.shape) == 0:
        raise ValueError("components must have non-empty shape [N, M]")
    if not jnp.issubdtype(component_array.dtype, jnp.inexact):
        component_array = component_array.astype(jnp.float32)
    elif component_array.dtype in (jnp.float16, jnp.bfloat16):
        component_array = component_array.astype(jnp.float32)
    coefficient_array = jnp.asarray(coefficients, dtype=component_array.dtype)
    if coefficient_array.shape != (component_array.shape[1],):
        raise ValueError(
            f"coefficients must have shape [{component_array.shape[1]}], "
            f"got {coefficient_array.shape}"
        )
    if not bool(np.asarray(jnp.all(jnp.isfinite(component_array)))):
        raise ValueError("components must be finite")
    if not bool(np.asarray(jnp.all(jnp.isfinite(coefficient_array)))):
        raise ValueError("coefficients must be finite")
    intensity = component_array @ coefficient_array
    if bool(np.asarray(jnp.any(~jnp.isfinite(intensity)))) or bool(
        np.asarray(jnp.any(intensity <= 0))
    ):
        raise ValueError("reference intensity must be finite and strictly positive at every row")
    return component_array / intensity[:, None]


@dataclass(frozen=True, slots=True)
class LinearProblem:
    """An evaluated linear-intensity problem on an integration sample."""

    components: Any
    coefficients: Any
    weights: Any | None = None
    component_names: Sequence[str] | None = None
    variables: Sequence[str] | None = None

    def __post_init__(self) -> None:
        component_array = jnp.asarray(self.components)
        scores = scores_from_components(component_array, self.coefficients)
        component_array = component_array.astype(scores.dtype)
        coefficient_array = jnp.asarray(self.coefficients, dtype=scores.dtype)
        if self.weights is None:
            weight_array = None
        else:
            weight_array = jnp.asarray(self.weights, dtype=scores.dtype)
            if weight_array.shape != (component_array.shape[0],):
                raise ValueError(
                    f"weights must have shape [{component_array.shape[0]}], "
                    f"got {weight_array.shape}"
                )
            if not bool(np.asarray(jnp.all(jnp.isfinite(weight_array)))):
                raise ValueError("weights must be finite")
            if bool(np.asarray(jnp.any(weight_array < 0))):
                raise ValueError("weights must be nonnegative")
            if not bool(np.asarray(jnp.any(weight_array > 0))):
                raise ValueError("at least one weight must be positive")
        component_names = _names(
            self.component_names,
            component_array.shape[1],
            prefix="component",
        )
        variables = (
            None
            if self.variables is None
            else _names(self.variables, len(self.variables), prefix="variable")
        )
        object.__setattr__(self, "components", component_array)
        object.__setattr__(self, "coefficients", coefficient_array)
        object.__setattr__(self, "weights", weight_array)
        object.__setattr__(self, "component_names", component_names)
        object.__setattr__(self, "variables", variables)

    @property
    def density(self) -> jnp.ndarray:
        """Reference intensity evaluated on every integration point."""

        return self.components @ self.coefficients

    @property
    def scores(self) -> jnp.ndarray:
        """Inference score representation derived from the components."""

        return self.components / self.density[:, None]

    def to_dict(self) -> dict[str, object]:
        """Return the evaluated problem as JSON-compatible data."""

        return json_ready(
            {
                "components": self.components,
                "coefficients": self.coefficients,
                "weights": self.weights,
                "component_names": self.component_names,
                "variables": self.variables,
            }
        )


@dataclass(frozen=True, slots=True, init=False)
class LinearComponents:
    """A vectorized linear-intensity model evaluated on physical variables.

    Named component mappings preserve insertion order and require an exactly
    matching coefficient mapping. Sequence components use generated names.
    Each component callable receives a NumPy array with shape ``[N, K]`` and
    must return one finite value per row.
    """

    components: tuple[ComponentFunction, ...]
    coefficients: tuple[float, ...]
    component_names: tuple[str, ...]
    variables: tuple[str, ...] | None

    def __init__(
        self,
        components: Mapping[str, ComponentFunction] | Sequence[ComponentFunction],
        coefficients: Mapping[str, float] | Sequence[float],
        *,
        variables: Sequence[str] | None = None,
    ) -> None:
        if isinstance(components, Mapping):
            if not isinstance(coefficients, Mapping):
                raise TypeError("named components require a coefficient mapping")
            component_names = tuple(components.keys())
            if set(coefficients) != set(component_names):
                missing = sorted(set(component_names) - set(coefficients))
                extra = sorted(set(coefficients) - set(component_names))
                raise ValueError(
                    f"coefficient keys must match component keys; missing={missing}, extra={extra}"
                )
            functions = tuple(components[name] for name in component_names)
            coefficient_values = tuple(coefficients[name] for name in component_names)
        else:
            if isinstance(coefficients, Mapping):
                raise TypeError("sequence components require a coefficient sequence")
            functions = tuple(components)
            coefficient_values = tuple(coefficients)
            component_names = tuple(f"component_{index}" for index in range(len(functions)))
        if not functions:
            raise ValueError("at least one component function is required")
        if len(coefficient_values) != len(functions):
            raise ValueError(
                f"expected {len(functions)} coefficients, got {len(coefficient_values)}"
            )
        if any(not callable(function) for function in functions):
            raise TypeError("every component must be callable")
        resolved_names = _names(component_names, len(functions), prefix="component")
        coefficient_array = np.asarray(coefficient_values, dtype=float)
        if coefficient_array.shape != (len(functions),):
            raise ValueError("coefficients must be a one-dimensional scalar sequence")
        if not np.isfinite(coefficient_array).all():
            raise ValueError("coefficients must be finite")
        variable_names = None if variables is None else tuple(variables)
        resolved_variables = (
            None
            if variable_names is None
            else _names(variable_names, len(variable_names), prefix="variable")
        )
        object.__setattr__(self, "components", functions)
        object.__setattr__(self, "coefficients", tuple(float(value) for value in coefficient_array))
        object.__setattr__(self, "component_names", resolved_names)
        object.__setattr__(self, "variables", resolved_variables)

    def evaluate_components(self, X: Any) -> jnp.ndarray:
        """Evaluate every component function on a physical-variable matrix."""

        observations = np.asarray(X)
        if observations.ndim != 2 or min(observations.shape) == 0:
            raise ValueError("X must have non-empty shape [N, K]")
        if not np.issubdtype(observations.dtype, np.number) or not np.isfinite(observations).all():
            raise ValueError("X must be numeric and finite")
        if self.variables is not None and observations.shape[1] != len(self.variables):
            raise ValueError(
                f"X has {observations.shape[1]} variables, expected {len(self.variables)}"
            )
        columns: list[jnp.ndarray] = []
        for name, function in zip(self.component_names, self.components, strict=True):
            values = jnp.asarray(function(observations))
            if values.shape != (observations.shape[0],):
                raise ValueError(
                    f"component {name!r} must return shape [{observations.shape[0]}], "
                    f"got {values.shape}"
                )
            if not bool(np.asarray(jnp.all(jnp.isfinite(values)))):
                raise ValueError(f"component {name!r} returned a non-finite value")
            columns.append(values)
        return jnp.stack(columns, axis=1)

    def evaluate(self, X: Any, *, weights: Any | None = None) -> LinearProblem:
        """Evaluate the model and create a reusable component-level problem."""

        return LinearProblem(
            components=self.evaluate_components(X),
            coefficients=self.coefficients,
            weights=weights,
            component_names=self.component_names,
            variables=self.variables,
        )

    def to_dict(self) -> dict[str, object]:
        """Return serializable model metadata; callables are intentionally omitted."""

        return json_ready(
            {
                "coefficients": self.coefficients,
                "component_names": self.component_names,
                "variables": self.variables,
            }
        )
