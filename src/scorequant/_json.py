"""Small JSON conversion helpers for public result objects."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from typing import overload

import jax
import numpy as np

from ._typing import JsonValue


@overload
def json_ready(value: Mapping[str, object]) -> dict[str, JsonValue]: ...


@overload
def json_ready(value: object) -> JsonValue: ...


def json_ready(value: object) -> JsonValue:
    """Recursively convert arrays, NumPy scalars, and dataclasses to JSON values."""
    if is_dataclass(value) and not isinstance(value, type):
        return json_ready(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, (jax.Array, np.ndarray)):
        return json_ready(np.asarray(value).tolist())
    if isinstance(value, np.generic):
        return json_ready(value.item())
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if np.isfinite(value) else None
    raise TypeError(f"cannot convert {type(value).__name__} to JSON")
