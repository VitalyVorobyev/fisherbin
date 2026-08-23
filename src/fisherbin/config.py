"""Public optimizer configuration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class KMeansConfig:
    """Configuration for deterministic weighted score-space k-means."""

    method: Literal["kmeans"] = "kmeans"
    whiten: bool = True
    rank_rtol: float | None = None
    seed: int = 0
    n_init: int = 8
    max_iter: int = 100
    tolerance: float = 1e-6
    record_every: int = 1

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible configuration mapping."""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class SoftVoronoiConfig:
    """Configuration for differentiable D-optimal soft Voronoi fitting."""

    method: Literal["soft_voronoi"] = "soft_voronoi"
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

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible configuration mapping."""

        return asdict(self)


FitConfig = KMeansConfig | SoftVoronoiConfig
