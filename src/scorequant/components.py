"""Linear-intensity models and the intensity score adapter."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from ._execution import canonical_array, execution_scope
from ._execution import xp as jnp
from ._json import json_ready
from ._typing import ArrayLike, JsonValue
from ._validation import promote_low_precision
from .config import ExecutionConfig

ComponentFunction = Callable[[np.ndarray], ArrayLike]


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


@execution_scope
def scores_from_components(
    components: ArrayLike,
    coefficients: ArrayLike,
    *,
    execution: ExecutionConfig | None = None,
) -> np.ndarray:
    """Construct scores for a linear intensity model.

    Parameters
    ----------
    components
        Finite component matrix with shape ``[N, M]``.
    coefficients
        Finite reference coefficients with shape ``[M]``.

    Returns
    -------
    numpy.ndarray
        Score matrix ``components / (components @ coefficients)[:, None]``
        with shape ``[N, M]``.

    Raises
    ------
    ValueError
        If shapes are incompatible, values are non-finite, or the reference
        intensity is not strictly positive at every row.

    Notes
    -----
    Components and coefficients may be signed and need not be normalized.
    They must be finite, and their resulting reference intensity must be
    strictly positive at every supplied integration point.

    The map is invariant under a common event-wise rescaling of a row: for
    any positive ``c(x)``, replacing ``components[i, :]`` by
    ``c(x_i) * components[i, :]`` leaves the scores unchanged. Component
    densities and component density *ratios* in any gauge therefore produce
    identical scores; absolute normalization is never required.
    """
    del execution
    component_array = jnp.asarray(components)
    if component_array.ndim != 2 or min(component_array.shape) == 0:
        raise ValueError("components must have non-empty shape [N, M]")
    component_array = promote_low_precision(component_array)
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
    return canonical_array(component_array / intensity[:, None])


@dataclass(frozen=True, slots=True, init=False)
class LinearProblem:
    """Represent an evaluated linear intensity on an integration sample.

    Parameters
    ----------
    components
        Component matrix with shape ``[N, M]``.
    coefficients
        Reference coefficient vector with shape ``[M]``.
    weights
        Optional finite, nonnegative integration weights with shape ``[N]``.
    component_names
        Optional unique component names. Stable generated names are used when
        omitted.
    variables
        Optional physical-variable names retained as metadata.
    """

    components: jnp.ndarray
    coefficients: jnp.ndarray
    weights: jnp.ndarray | None
    component_names: tuple[str, ...]
    variables: tuple[str, ...] | None

    @execution_scope
    def __init__(
        self,
        components: ArrayLike,
        coefficients: ArrayLike,
        weights: ArrayLike | None = None,
        component_names: Sequence[str] | None = None,
        variables: Sequence[str] | None = None,
        execution: ExecutionConfig | None = None,
    ) -> None:
        """Validate arrays and freeze their normalized representations."""
        component_array = jnp.asarray(components)
        scores = scores_from_components(
            component_array,
            coefficients,
            execution=execution,
        )
        component_array = component_array.astype(scores.dtype)
        coefficient_array = jnp.asarray(coefficients, dtype=scores.dtype)
        if weights is None:
            weight_array = None
        else:
            weight_array = jnp.asarray(weights, dtype=scores.dtype)
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
            component_names,
            component_array.shape[1],
            prefix="component",
        )
        variables = (
            None if variables is None else _names(variables, len(variables), prefix="variable")
        )
        object.__setattr__(self, "components", canonical_array(component_array))
        object.__setattr__(self, "coefficients", canonical_array(coefficient_array))
        object.__setattr__(
            self,
            "weights",
            None if weight_array is None else canonical_array(weight_array),
        )
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

    def to_dict(self) -> dict[str, JsonValue]:
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
    """Define vectorized linear-intensity components on physical variables.

    Parameters
    ----------
    components
        Either an insertion-ordered mapping from names to callables or a
        sequence of callables. Each callable receives ``X`` with shape
        ``[N, K]`` and returns one finite value per row.
    coefficients
        A mapping with exactly the component keys or a coefficient sequence
        aligned with sequence components.
    variables
        Optional unique physical-variable names used to validate ``K``.
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
        """Validate and freeze component order, coefficients, and metadata."""
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

    @execution_scope
    def evaluate_components(
        self,
        X: ArrayLike,
        *,
        execution: ExecutionConfig | None = None,
    ) -> np.ndarray:
        """Evaluate every component function.

        Parameters
        ----------
        X
            Finite numeric physical-variable matrix with shape ``[N, K]``.

        Returns
        -------
        numpy.ndarray
            Evaluated component matrix with shape ``[N, M]``.
        """
        del execution
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
        return canonical_array(jnp.stack(columns, axis=1))

    def evaluate(
        self,
        X: ArrayLike,
        *,
        weights: ArrayLike | None = None,
        execution: ExecutionConfig | None = None,
    ) -> LinearProblem:
        """Create a reusable evaluated problem.

        Parameters
        ----------
        X
            Finite numeric physical-variable matrix with shape ``[N, K]``.
        weights
            Optional finite, nonnegative integration weights with shape ``[N]``.

        Returns
        -------
        LinearProblem
            Validated components, coefficients, weights, and metadata.
        """
        return LinearProblem(
            components=self.evaluate_components(X, execution=execution),
            coefficients=self.coefficients,
            weights=weights,
            component_names=self.component_names,
            variables=self.variables,
            execution=execution,
        )

    def to_dict(self) -> dict[str, JsonValue]:
        """Return serializable model metadata; callables are intentionally omitted."""
        return json_ready(
            {
                "coefficients": self.coefficients,
                "component_names": self.component_names,
                "variables": self.variables,
            }
        )
