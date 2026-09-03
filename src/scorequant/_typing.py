"""Shared private type contracts for array inputs and JSON output."""

from __future__ import annotations

from numpy.typing import ArrayLike as _NumPyArrayLike
from numpy.typing import DTypeLike as _NumPyDTypeLike

type ArrayLike = _NumPyArrayLike
type DTypeLike = _NumPyDTypeLike
type JsonScalar = None | bool | int | float | str
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]
