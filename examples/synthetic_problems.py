"""Deterministic synthetic problems used by scripts, notebooks, and tests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from fisherbin import scores_from_components


@dataclass(frozen=True, slots=True)
class SyntheticDataset:
    observations: np.ndarray
    scores: np.ndarray
    weights: np.ndarray


@dataclass(frozen=True, slots=True)
class SyntheticProblem:
    name: str
    title: str
    n_bins: int
    train: SyntheticDataset
    validation: SyntheticDataset
    test: SyntheticDataset


def _three_splits(
    generator: Callable[[np.random.Generator, int], SyntheticDataset],
    *,
    seed: int,
    sizes: tuple[int, int, int],
) -> tuple[SyntheticDataset, SyntheticDataset, SyntheticDataset]:
    generators = [np.random.default_rng(value) for value in np.random.SeedSequence(seed).spawn(3)]
    return tuple(generator(rng, size) for rng, size in zip(generators, sizes, strict=True))  # type: ignore[return-value]


def gaussian_location(
    *, seed: int = 10, sizes: tuple[int, int, int] = (2_000, 1_000, 10_000)
) -> SyntheticProblem:
    """A one-parameter Gaussian location problem with analytic score ``s(x)=x``."""

    def generate(rng: np.random.Generator, size: int) -> SyntheticDataset:
        observations = rng.normal(size=(size, 1))
        return SyntheticDataset(observations, observations.copy(), np.ones(size))

    train, validation, test = _three_splits(generate, seed=seed, sizes=sizes)
    return SyntheticProblem("gaussian_location", "Gaussian location", 4, train, validation, test)


def _spectral_components(x: np.ndarray) -> np.ndarray:
    first = 0.08 + np.exp(-0.5 * ((x - 0.22) / 0.055) ** 2)
    first += 0.65 * np.exp(-0.5 * ((x - 0.78) / 0.075) ** 2)
    second = 0.10 + 0.9 * np.exp(-0.5 * ((x - 0.48) / 0.09) ** 2)
    second += 0.75 * np.exp(-0.5 * ((x - 0.90) / 0.035) ** 2)
    return np.column_stack([first, second])


def spectral_templates(
    *, seed: int = 20, sizes: tuple[int, int, int] = (4_000, 2_000, 15_000)
) -> SyntheticProblem:
    """A weighted two-parameter non-monotonic template-intensity problem."""

    coefficients = np.asarray([1.0, 0.8])

    def generate(rng: np.random.Generator, size: int) -> SyntheticDataset:
        x = rng.uniform(0, 1, size)
        components = _spectral_components(x)
        intensity = components @ coefficients
        scores = np.asarray(scores_from_components(components, coefficients))
        return SyntheticDataset(x[:, None], scores, intensity)

    train, validation, test = _three_splits(generate, seed=seed, sizes=sizes)
    return SyntheticProblem(
        "spectral_templates", "Overlapping spectral templates", 8, train, validation, test
    )


def _spatial_components(xy: np.ndarray) -> np.ndarray:
    x, y = xy[:, 0], xy[:, 1]

    def gaussian(cx: float, cy: float, width: float) -> np.ndarray:
        return np.exp(-0.5 * ((x - cx) ** 2 + (y - cy) ** 2) / width**2)

    first = 0.025 + gaussian(-0.48, -0.18, 0.24) + 0.55 * gaussian(0.46, 0.50, 0.17)
    second = 0.025 + gaussian(0.40, -0.30, 0.27) + 0.60 * gaussian(-0.38, 0.53, 0.19)
    return np.column_stack([first, second])


def spatial_sources(
    *, seed: int = 30, sizes: tuple[int, int, int] = (6_000, 3_000, 20_000)
) -> SyntheticProblem:
    """A two-dimensional importance-weighted overlapping-source problem."""

    coefficients = np.asarray([1.0, 0.9])

    def generate(rng: np.random.Generator, size: int) -> SyntheticDataset:
        observations = rng.uniform(-1, 1, size=(size, 2))
        components = _spatial_components(observations)
        intensity = components @ coefficients
        scores = np.asarray(scores_from_components(components, coefficients))
        return SyntheticDataset(observations, scores, intensity)

    train, validation, test = _three_splits(generate, seed=seed, sizes=sizes)
    return SyntheticProblem(
        "spatial_sources", "Overlapping spatial sources", 16, train, validation, test
    )


PROBLEMS = {
    "gaussian_location": gaussian_location,
    "spectral_templates": spectral_templates,
    "spatial_sources": spatial_sources,
}
