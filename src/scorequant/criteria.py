"""Supported information criteria with explicit solver semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ._typing import JsonValue


@dataclass(frozen=True, slots=True)
class DOptimality:
    """Maximize the log determinant in the informative score subspace."""

    name: Literal["d_optimality"] = field(default="d_optimality", init=False)

    def to_dict(self) -> dict[str, JsonValue]:
        """Return the JSON-compatible criterion contract."""
        return {"name": self.name}


@dataclass(frozen=True, slots=True)
class NormalizedTrace:
    """Minimize within-bin distortion after Fisher whitening."""

    name: Literal["normalized_trace"] = field(default="normalized_trace", init=False)

    def to_dict(self) -> dict[str, JsonValue]:
        """Return the JSON-compatible criterion contract."""
        return {"name": self.name}


type Criterion = DOptimality | NormalizedTrace
