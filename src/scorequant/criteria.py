"""Supported information criteria with explicit solver semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ._errors import ContractError
from ._typing import JsonValue
from .sources import ScoreSchema


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
        The parameters of interest, either as unique nonnegative score-column
        indices or as unique parameter names. Names require a
        :class:`~scorequant.ScoreSchema` on the sample being optimized and are
        resolved to indices once, at the public task boundary. At least one
        nuisance column must remain when the criterion is applied.

    Examples
    --------
    >>> ProfiledDOptimality(interest=(4,)).interest
    (4,)
    >>> ProfiledDOptimality(interest=("HSPCs",)).interest
    ('HSPCs',)
    """

    interest: tuple[int, ...] | tuple[str, ...]
    name: Literal["profiled_d_optimality"] = field(default="profiled_d_optimality", init=False)

    def __post_init__(self) -> None:
        """Validate the representation-independent part of the block contract."""
        if not self.interest:
            raise ContractError("interest must contain at least one score column or parameter name")
        if len(set(self.interest)) != len(self.interest):
            raise ContractError("interest entries must be unique")
        entries: tuple[int | str, ...] = tuple(self.interest)
        if self.named:
            if any(not isinstance(entry, str) or not entry.strip() for entry in entries):
                raise TypeError("interest must be all integer indices or all parameter names")
            return
        if any(isinstance(entry, bool) or not isinstance(entry, int) for entry in entries):
            raise TypeError("interest must be all integer indices or all parameter names")
        if any(int(entry) < 0 for entry in entries):
            raise ContractError("interest indices must be nonnegative")

    @property
    def named(self) -> bool:
        """Whether ``interest`` is expressed as parameter names rather than indices."""
        return any(isinstance(entry, str) for entry in self.interest)

    @property
    def interest_indices(self) -> tuple[int, ...]:
        """Return the parameters of interest as score-column indices.

        Every consumer downstream of the public task boundary -- the profiled
        objective, the information algebra, the soft solver and the reports --
        reads this rather than ``interest``, so an unresolved criterion fails
        here by name instead of indexing a score matrix with a string.
        """
        if self.named:
            raise ContractError(
                "profiled interest is still expressed by name; it is resolved against "
                "the sample schema at the public task boundary, so this criterion did "
                "not come through optimize_partition or fit_quantizer"
            )
        return tuple(int(index) for index in self.interest)

    def resolve(self, schema: ScoreSchema | None) -> ProfiledDOptimality:
        """Return an equivalent criterion whose ``interest`` is score-column indices.

        Downstream information algebra, solvers and reports consume indices
        only, so names are translated exactly once here rather than being
        re-resolved at every consumer.

        Raises
        ------
        ValueError
            When names were supplied but the sample carries no schema to
            resolve them against.
        KeyError
            When a name is not declared by the schema.
        """
        if not self.named:
            return self
        if schema is None:
            names = ", ".join(str(entry) for entry in self.interest)
            raise ContractError(
                f"interest was declared by name ({names}) but the scores carry no "
                "ScoreSchema; pass schema=ScoreSchema(...) on the sample, or use "
                "score-column indices"
            )
        return ProfiledDOptimality(interest=schema.select(*(str(n) for n in self.interest)))

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
