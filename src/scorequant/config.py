"""Public optimizer configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

import numpy as np

from ._json import json_ready
from ._typing import JsonValue


def _validate_bool(name: str, value: object) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a boolean")


def _validate_integer(name: str, value: object, *, minimum: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")


def _validate_finite(name: str, value: object, *, positive: bool) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    if not np.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if positive and value <= 0:
        raise ValueError(f"{name} must be positive")
    if not positive and value < 0:
        raise ValueError(f"{name} must be nonnegative")


def _validate_common_config(
    *,
    whiten: bool,
    rank_rtol: float | None,
    seed: int,
    n_init: int,
    tolerance: float,
    record_every: int,
) -> None:
    _validate_bool("whiten", whiten)
    if rank_rtol is not None:
        _validate_finite("rank_rtol", rank_rtol, positive=False)
        if rank_rtol >= 1:
            raise ValueError("rank_rtol must be less than one")
    _validate_integer("seed", seed, minimum=0)
    _validate_integer("n_init", n_init, minimum=1)
    _validate_finite("tolerance", tolerance, positive=False)
    _validate_integer("record_every", record_every, minimum=1)


@dataclass(frozen=True, slots=True)
class KMeansConfig:
    """Configure deterministic weighted score-space k-means.

    Parameters
    ----------
    whiten
        Whiten retained Fisher directions before computing distances.
    rank_rtol
        Relative eigenvalue threshold for informative-rank selection. The
        dtype-aware default is used when omitted.
    seed
        Nonnegative JAX random seed.
    n_init
        Number of weighted k-means++ restarts after invariant row ordering.
    max_iter
        Maximum Lloyd iterations per restart.
    tolerance
        Relative objective-change convergence tolerance.
    record_every
        Number of Lloyd iterations between trace snapshots.
    """

    method: Literal["kmeans"] = field(default="kmeans", init=False)
    whiten: bool = True
    rank_rtol: float | None = None
    seed: int = 0
    n_init: int = 8
    max_iter: int = 100
    tolerance: float = 1e-6
    record_every: int = 1

    def __post_init__(self) -> None:
        """Validate the complete configuration at construction time."""
        _validate_common_config(
            whiten=self.whiten,
            rank_rtol=self.rank_rtol,
            seed=self.seed,
            n_init=self.n_init,
            tolerance=self.tolerance,
            record_every=self.record_every,
        )
        _validate_integer("max_iter", self.max_iter, minimum=1)

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible configuration mapping."""
        return json_ready(asdict(self))


@dataclass(frozen=True, slots=True)
class SoftVoronoiConfig:
    """Configure differentiable D-optimal soft Voronoi fitting.

    Parameters
    ----------
    whiten
        Whiten retained Fisher directions before computing distances.
    rank_rtol
        Relative eigenvalue threshold for informative-rank selection. The
        dtype-aware default is used when omitted.
    seed
        Nonnegative JAX random seed.
    n_init
        Number of k-means restarts used to initialize the centers.
    kmeans_max_iter
        Maximum Lloyd iterations for each initialization restart.
    tolerance
        Relative convergence tolerance for initialization.
    max_steps
        Number of Adam updates.
    learning_rate
        Adam learning rate before scaling by initial center separation.
    gradient_clip
        Global gradient-norm clipping threshold.
    temperature_end_ratio
        Final temperature divided by the initial temperature.
    record_every
        Number of Adam steps between trace snapshots.
    """

    method: Literal["soft_voronoi"] = field(default="soft_voronoi", init=False)
    whiten: bool = True
    rank_rtol: float | None = None
    seed: int = 0
    n_init: int = 8
    kmeans_max_iter: int = 100
    tolerance: float = 1e-6
    max_steps: int = 1000
    learning_rate: float = 1e-2
    gradient_clip: float = 10.0
    temperature_end_ratio: float = 0.05
    record_every: int = 10

    def __post_init__(self) -> None:
        """Validate the complete configuration at construction time."""
        _validate_common_config(
            whiten=self.whiten,
            rank_rtol=self.rank_rtol,
            seed=self.seed,
            n_init=self.n_init,
            tolerance=self.tolerance,
            record_every=self.record_every,
        )
        _validate_integer("kmeans_max_iter", self.kmeans_max_iter, minimum=1)
        _validate_integer("max_steps", self.max_steps, minimum=1)
        _validate_finite("learning_rate", self.learning_rate, positive=True)
        _validate_finite("gradient_clip", self.gradient_clip, positive=True)
        _validate_finite("temperature_end_ratio", self.temperature_end_ratio, positive=True)
        if self.temperature_end_ratio > 1:
            raise ValueError("temperature_end_ratio must be at most one")

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible configuration mapping."""
        return json_ready(asdict(self))


@dataclass(frozen=True, slots=True)
class DExchangeConfig:
    """Configure exact positive-gain D-optimal point exchange.

    Parameters
    ----------
    rank_rtol
        Relative threshold for the informative Fisher subspace.
    seed
        Seed used by deterministic k-means initialization.
    n_init
        Number of k-means initialization restarts.
    max_sweeps
        Maximum complete scans of candidate point moves.
    gain_tolerance
        Strict minimum accepted log-determinant gain.
    first_improvement
        Accept the first improving move in deterministic row/bin order instead
        of the best move in a sweep.
    """

    method: Literal["d_exchange"] = field(default="d_exchange", init=False)
    rank_rtol: float | None = None
    seed: int = 0
    n_init: int = 8
    max_sweeps: int = 200
    gain_tolerance: float = 1e-10
    first_improvement: bool = False

    def __post_init__(self) -> None:
        """Validate exchange settings at construction time."""
        if self.rank_rtol is not None:
            _validate_finite("rank_rtol", self.rank_rtol, positive=False)
            if self.rank_rtol >= 1:
                raise ValueError("rank_rtol must be less than one")
        _validate_integer("seed", self.seed, minimum=0)
        _validate_integer("n_init", self.n_init, minimum=1)
        _validate_integer("max_sweeps", self.max_sweeps, minimum=1)
        _validate_finite("gain_tolerance", self.gain_tolerance, positive=False)
        _validate_bool("first_improvement", self.first_improvement)

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible configuration mapping."""
        return json_ready(asdict(self))


@dataclass(frozen=True, slots=True)
class ScalarDPConfig:
    """Configure exact interval dynamic programming for one score coordinate.

    Parameters
    ----------
    rank_rtol
        Relative threshold for the informative score direction.
    max_rows
        Maximum number of distinct positive-weight score atoms. The exact
        dynamic program uses quadratic storage and work in this count.
    """

    method: Literal["scalar_dp"] = field(default="scalar_dp", init=False)
    rank_rtol: float | None = None
    max_rows: int = 2_000

    def __post_init__(self) -> None:
        """Validate the exact-solver capacity contract."""
        if self.rank_rtol is not None:
            _validate_finite("rank_rtol", self.rank_rtol, positive=False)
            if self.rank_rtol >= 1:
                raise ValueError("rank_rtol must be less than one")
        _validate_integer("max_rows", self.max_rows, minimum=1)

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible configuration mapping."""
        return json_ready(asdict(self))


type QuantizerConfig = KMeansConfig | SoftVoronoiConfig | DExchangeConfig | ScalarDPConfig
