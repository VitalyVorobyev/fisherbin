"""Small JSON conversion helpers for public result objects."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

import jax
import numpy as np


def json_ready(value: Any) -> Any:
    """Recursively convert arrays, NumPy scalars, and dataclasses to JSON values."""

    if is_dataclass(value):
        return json_ready(asdict(value))
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, (jax.Array, np.ndarray)):
        return json_ready(np.asarray(value).tolist())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value
