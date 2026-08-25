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
class ProfiledDOptimality:
    """Maximize profiled information for declared parameters of interest.

    Nuisance information is estimated from the same labels. The full-data
    efficient-score upper problem is intentionally a separate workflow.

    Parameters
    ----------
    interest
        Unique nonnegative score-column indices for the parameters of interest.
        At least one nuisance column must remain when the criterion is applied.
    """

    interest: tuple[int, ...]
    name: Literal["profiled_d_optimality"] = field(default="profiled_d_optimality", init=False)

    def __post_init__(self) -> None:
        """Validate the representation-independent part of the block contract."""
        if not self.interest:
            raise ValueError("interest must contain at least one score-column index")
        if any(isinstance(index, bool) or not isinstance(index, int) for index in self.interest):
            raise TypeError("interest indices must be integers")
        if any(index < 0 for index in self.interest):
            raise ValueError("interest indices must be nonnegative")
        if len(set(self.interest)) != len(self.interest):
            raise ValueError("interest indices must be unique")

    def to_dict(self) -> dict[str, JsonValue]:
        """Return the JSON-compatible same-label profiling contract."""
        return {"name": self.name, "interest": list(self.interest)}


@dataclass(frozen=True, slots=True)
class NormalizedTrace:
    """Minimize within-bin distortion after Fisher whitening."""

    name: Literal["normalized_trace"] = field(default="normalized_trace", init=False)

    def to_dict(self) -> dict[str, JsonValue]:
        """Return the JSON-compatible criterion contract."""
        return {"name": self.name}


type Criterion = DOptimality | ProfiledDOptimality | NormalizedTrace
