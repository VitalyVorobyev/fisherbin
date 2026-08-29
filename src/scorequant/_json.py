"""Small JSON conversion helpers for public result objects."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from typing import overload

import numpy as np

from ._typing import JsonValue


@overload
def json_ready(value: Mapping[str, object]) -> dict[str, JsonValue]: ...


@overload
def json_ready(value: object) -> JsonValue: ...


def json_ready(value: object) -> JsonValue:
    """Recursively convert arrays, NumPy scalars, and dataclasses to JSON values.

    A non-finite float (``inf``, ``-inf``, ``nan``) becomes the string
    ``"Infinity"``, ``"-Infinity"``, or ``"NaN"`` rather than ``None``, so a
    genuinely missing value and a certified-unbounded one (for example
    ``StabilityReport.best_gain`` on a labeling with no admissible
    relocation) stay distinguishable in the JSON output. ``json.dumps`` with
    ``allow_nan=False`` still succeeds, since every value returned here is a
    standard JSON type.
    """
    if is_dataclass(value) and not isinstance(value, type):
        return json_ready(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, np.ndarray) or (
        type(value).__module__.startswith("jax")
        and hasattr(value, "shape")
        and hasattr(value, "dtype")
    ):
        return json_ready(np.asarray(value).tolist())
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if np.isnan(value):
            return "NaN"
        if np.isinf(value):
            return "Infinity" if value > 0 else "-Infinity"
        return value
    raise TypeError(f"cannot convert {type(value).__name__} to JSON")
