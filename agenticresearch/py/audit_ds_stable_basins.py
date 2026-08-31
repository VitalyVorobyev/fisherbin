"""Independent numerical audit harness for the DS17 stable-basins complex.

This script deliberately does not import ``ds_stable_basins``. Exact finite
checks use :class:`fractions.Fraction`; population moments are evaluated by an
independently derived Gaussian-mixture formula and cross-checked by adaptive
quadrature and the public ``IntegrationSource`` API.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from importlib import metadata
from itertools import product
from pathlib import Path

import numpy as np
from scipy.integrate import quad_vec
from scipy.optimize import brentq, least_squares
from scipy.special import ndtr
from scipy.stats import qmc

RESEARCH = Path(__file__).resolve().parents[1]
WORKSPACE = RESEARCH.parent
SOURCE_FROZEN = "ce8d59db4fb63a25341f65da01996e69aac4fafd"
AUDIT_ID = "AUDIT-DS-STABLE-BASINS-001"
SCHEMA_VERSION = 1
SEED_BASE = 20260831


@dataclass(frozen=True)
class GaussianMixture:
    """Centered planar Gaussian mixture used as an audit input."""

    name: str
    weights: tuple[float, ...]
    means: tuple[tuple[float, float], ...]
    covariances: tuple[tuple[tuple[float, float], tuple[float, float]], ...]

    def second_moment(self) -> np.ndarray:
        """Return E[SS^T] from the declared mixture parameters."""
        result = np.zeros((2, 2), dtype=float)
        for weight, mean, covariance in zip(
            self.weights, self.means, self.covariances, strict=True
        ):
            vector = np.asarray(mean, dtype=float)
            result += weight * (np.asarray(covariance, dtype=float) + np.outer(vector, vector))
        return result

    def as_record(self) -> dict[str, object]:
        """Return JSON-safe law parameters."""
        return {
            "name": self.name,
            "weights": list(self.weights),
            "means": [list(value) for value in self.means],
            "covariances": [[list(row) for row in value] for value in self.covariances],
        }


def gaussian(name: str, a: float, c: float, d: float) -> GaussianMixture:
    """Construct one centered Gaussian law."""
    return GaussianMixture(name, (1.0,), ((0.0, 0.0),), (((a, c), (c, d)),))


def bimodal(magnitude: float, scale: float = 0.4) -> GaussianMixture:
    """Construct the product bimodal-nuisance law."""
    covariance = ((1.0, 0.0), (0.0, scale * scale))
    return GaussianMixture(
        f"bimodal(m={magnitude},s={scale})",
        (0.5, 0.5),
        ((0.0, -magnitude), (0.0, magnitude)),
        (covariance, covariance),
    )


def xcorr(correlation: float) -> GaussianMixture:
    """Construct the dependent conditionally-centered mixture."""
    return GaussianMixture(
        f"xcorr(c={correlation})",
        (0.5, 0.5),
        ((0.0, 0.0), (0.0, 0.0)),
        (
            ((1.0, correlation), (correlation, 1.0)),
            ((1.0, -correlation), (-correlation, 1.0)),
        ),
    )


def mix3() -> GaussianMixture:
    """Construct the off-class three-component control."""
    covariance = ((0.25, 0.0), (0.0, 0.25))
    return GaussianMixture(
        "mix3",
        (1 / 3, 1 / 3, 1 / 3),
        ((-2.0, 1.0), (0.0, -2.0), (2.0, 1.0)),
        (covariance, covariance, covariance),
    )


def all_laws() -> list[GaussianMixture]:
    """Return all laws named by the DS17 scan ledger."""
    return [
        gaussian("gauss00", 1.0, 0.0, 1.0),
        gaussian("gauss06", 1.0, 0.6, 1.0),
        gaussian("gauss09", 1.0, 0.9, 1.0),
        gaussian("gauss_anisotropic", 2.0, 0.5, 0.75),
        *(bimodal(value) for value in (0.75, 1.0, 1.5, 2.0, 3.0)),
        *(xcorr(value) for value in (0.5, 0.8, 0.95)),
        mix3(),
    ]


def sha256(path: Path) -> str:
    """Hash a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_output(*arguments: str) -> str:
    """Run one read-only git query."""
    return subprocess.run(
        ["git", *arguments],
        cwd=WORKSPACE,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


def package_version(name: str) -> str:
    """Return an installed package version or an explicit unavailable marker."""
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "unavailable"


def envelope(
    mode: str,
    parameters: dict[str, object],
    tolerances: dict[str, object],
    summary: dict[str, object],
    assertions: list[dict[str, object]],
    started: float,
) -> dict[str, object]:
    """Create the provenance-complete artifact envelope."""
    script = Path(__file__).resolve()
    return {
        "schema_version": SCHEMA_VERSION,
        "audit_id": AUDIT_ID,
        "mode": mode,
        "created_utc": datetime.now(UTC).isoformat(),
        "source_frozen": SOURCE_FROZEN,
        "git_revision": git_output("rev-parse", "HEAD"),
        "git_clean": not bool(git_output("status", "--short")),
        "script_sha256": sha256(script),
        "uv_lock_sha256": sha256(WORKSPACE / "uv.lock"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy_version": package_version("numpy"),
        "scipy_version": package_version("scipy"),
        "scorequant_version": package_version("scorequant"),
        "argv": sys.argv,
        "parameters": parameters,
        "tolerances": tolerances,
        "seed_base": SEED_BASE,
        "seed_formula": "library: SEED_BASE + 1000*N + rep; search Sobol: SEED_BASE",
        "runtime_seconds": time.monotonic() - started,
        "summary": summary,
        "assertions": assertions,
        "result": "PASS" if all(bool(item["passed"]) for item in assertions) else "FAIL",
    }


def canonical_partitions(size: int, bins: int) -> Iterator[tuple[int, ...]]:
    """Yield label-permutation-canonical surjective partitions."""
    for labels in product(range(bins), repeat=size):
        if labels[0] != 0 or set(labels) != set(range(bins)):
            continue
        if all(labels[index] <= max(labels[:index]) + 1 for index in range(1, size)):
            yield labels


def exact_cells(
    scores: list[tuple[Fraction, Fraction]],
    weights: list[Fraction],
    labels: tuple[int, ...],
    bins: int,
) -> tuple[list[Fraction], list[tuple[Fraction, Fraction]]]:
    """Rebuild exact cell masses and first moments."""
    masses = [Fraction(0)] * bins
    moments = [[Fraction(0), Fraction(0)] for _ in range(bins)]
    for score, weight, label in zip(scores, weights, labels, strict=True):
        masses[label] += weight
        moments[label][0] += weight * score[0]
        moments[label][1] += weight * score[1]
    return masses, [(value[0], value[1]) for value in moments]


def exact_information(
    scores: list[tuple[Fraction, Fraction]],
    weights: list[Fraction],
    labels: tuple[int, ...],
    bins: int,
) -> list[list[Fraction]]:
    """Rebuild exact binned information from cell moments."""
    masses, moments = exact_cells(scores, weights, labels, bins)
    return [
        [
            sum(
                moment[first] * moment[second] / mass
                for mass, moment in zip(masses, moments, strict=True)
            )
            for second in range(2)
        ]
        for first in range(2)
    ]


def exact_profiled(information: list[list[Fraction]]) -> Fraction | None:
    """Return the ordinary scalar profiled value, or None if nuisance is singular."""
    if information[1][1] == 0:
        return None
    return information[0][0] - information[0][1] ** 2 / information[1][1]


def exact_stationarity(
    scores: list[tuple[Fraction, Fraction]],
    weights: list[Fraction],
    labels: tuple[int, ...],
    bins: int,
) -> dict[str, object]:
    """Check exact projected-nearest-centroid stationarity."""
    masses, moments = exact_cells(scores, weights, labels, bins)
    information = exact_information(scores, weights, labels, bins)
    if information[1][1] == 0:
        return {"defined": False, "violations": None}
    beta = information[0][1] / information[1][1]
    centers = [
        moment[0] / mass - beta * moment[1] / mass
        for mass, moment in zip(masses, moments, strict=True)
    ]
    violations = 0
    for score, label in zip(scores, labels, strict=True):
        projected = score[0] - beta * score[1]
        distances = [(projected - center) ** 2 for center in centers]
        violations += int(distances[label] > min(distances))
    return {
        "defined": True,
        "beta": beta,
        "projected_centroids": centers,
        "violations": violations,
    }


def load_fixture(identifier: str) -> dict[str, object]:
    """Load one counterexample fixture."""
    path = RESEARCH / "COUNTEREXAMPLES" / f"{identifier}.json"
    return json.loads(path.read_text())


def parse_fixture(
    fixture: dict[str, object],
) -> tuple[list[tuple[Fraction, Fraction]], list[Fraction], tuple[int, ...], int]:
    """Parse raw exact arrays from a counterexample fixture."""
    scores = [tuple(Fraction(value) for value in row) for row in fixture["scores"]]
    weights = [Fraction(value) for value in fixture["weights"]]
    labels = tuple(int(value) for value in fixture["labels_before"])
    return scores, weights, labels, int(fixture["K"])


def run_exact() -> tuple[dict[str, object], list[dict[str, object]]]:
    """Run exact identities, fixtures, and the fixture-minimization attack."""
    assertions: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        assertions.append({"name": name, "passed": bool(passed), "detail": detail})

    sign_fixture = load_fixture("CE-DS-LCM-SIGNSPLIT-MARGIN-001")
    scores, weights, labels, bins = parse_fixture(sign_fixture)
    masses, moments = exact_cells(scores, weights, labels, bins)
    information = exact_information(scores, weights, labels, bins)
    stationary = exact_stationarity(scores, weights, labels, bins)
    profiled = exact_profiled(information)
    check(
        "signsplit_information", information == [[Fraction(4), 0], [0, Fraction(9, 8)]], information
    )
    check("signsplit_profiled", profiled == 4, profiled)
    check("signsplit_stationary", stationary["violations"] == 0, stationary)

    beta = Fraction(1, 2)
    centroids = [
        (moment[0] / mass, moment[1] / mass) for mass, moment in zip(masses, moments, strict=True)
    ]
    t_means = [psi - beta * nuisance for psi, nuisance in centroids]
    numerator = sum(
        mass * t_value * centroid[1]
        for mass, t_value, centroid in zip(masses, t_means, centroids, strict=True)
    )
    quotient = numerator / information[1][1]
    check(
        "tilt_residual_identity",
        numerator == Fraction(-9, 16) and quotient == -beta,
        {"beta": beta, "t_means": t_means, "numerator": numerator, "quotient": quotient},
    )

    reduced = tuple(0 if label in (0, 1) else 1 for label in labels)
    reduced_information = exact_information(scores, weights, reduced, 2)
    check("signsplit_reduced_singular", reduced_information[1][1] == 0, reduced_information)

    wasted_fixture = load_fixture("CE-DS-POP-WASTED-CELLS-001")
    wasted_scores, wasted_weights, wasted_labels, wasted_bins = parse_fixture(wasted_fixture)
    wasted_information = exact_information(
        wasted_scores, wasted_weights, wasted_labels, wasted_bins
    )
    wasted_stationary = exact_stationarity(
        wasted_scores, wasted_weights, wasted_labels, wasted_bins
    )
    check(
        "wasted_k4",
        wasted_information == [[Fraction(4), 0], [0, Fraction(9, 4)]]
        and wasted_stationary["violations"] == 0,
        {"information": wasted_information, "stationarity": wasted_stationary},
    )

    stable_fixture = load_fixture("CE-DS-STABLE-MARGIN-RETAINING-001")
    stable_scores, stable_weights, stable_labels, stable_bins = parse_fixture(stable_fixture)
    stable_value = exact_profiled(
        exact_information(stable_scores, stable_weights, stable_labels, stable_bins)
    )
    gains: list[Fraction] = []
    for row, source in enumerate(stable_labels):
        if stable_labels.count(source) < 2:
            continue
        for destination in range(stable_bins):
            if destination == source:
                continue
            moved = list(stable_labels)
            moved[row] = destination
            moved_value = exact_profiled(
                exact_information(stable_scores, stable_weights, tuple(moved), stable_bins)
            )
            if moved_value is not None and stable_value is not None:
                gains.append(moved_value - stable_value)
    best_value: Fraction | None = None
    partition_count = 0
    for candidate in canonical_partitions(len(stable_scores), stable_bins):
        partition_count += 1
        candidate_value = exact_profiled(
            exact_information(stable_scores, stable_weights, candidate, stable_bins)
        )
        if candidate_value is not None and (best_value is None or candidate_value > best_value):
            best_value = candidate_value
    check(
        "stable_fixture_exhaustive",
        len(gains) == 16
        and max(gains) <= 0
        and partition_count == 966
        and best_value > stable_value,
        {
            "admissible_moves": len(gains),
            "max_gain": max(gains),
            "canonical_partitions": partition_count,
            "witness_value": stable_value,
            "best_value": best_value,
        },
    )

    minimal_scores = [
        (Fraction(-1), Fraction(1)),
        (Fraction(-1), Fraction(-1)),
        (Fraction(2), Fraction(0)),
    ]
    minimal_weights = [Fraction(1, 3)] * 3
    minimal_labels = (0, 1, 2)
    minimal_information = exact_information(minimal_scores, minimal_weights, minimal_labels, 3)
    minimal_stationary = exact_stationarity(minimal_scores, minimal_weights, minimal_labels, 3)
    minimal_center = [
        sum(
            weight * score[column]
            for weight, score in zip(minimal_weights, minimal_scores, strict=True)
        )
        for column in range(2)
    ]
    check(
        "support_minimization_boundary",
        minimal_center == [0, 0]
        and minimal_information == [[Fraction(2), 0], [0, Fraction(2, 3)]]
        and minimal_stationary["violations"] == 0,
        {
            "scores": minimal_scores,
            "weights": minimal_weights,
            "labels": minimal_labels,
            "center": minimal_center,
            "information": minimal_information,
            "stationarity": minimal_stationary,
            "interpretation": (
                "absolute support-minimal atomic algebra witness; "
                "atomic population stationarity is vacuous"
            ),
        },
    )

    gaussian_cases = [
        (Fraction(1), Fraction(0), Fraction(1), Fraction(-4)),
        (Fraction(1), Fraction(3, 5), Fraction(1), Fraction(-64, 25)),
        (Fraction(1), Fraction(9, 10), Fraction(1), Fraction(-19, 25)),
        (Fraction(2), Fraction(1, 2), Fraction(3, 4), Fraction(-5)),
    ]
    discriminants = [4 * (c * c - a * d) for a, c, d, _ in gaussian_cases]
    check(
        "gaussian_moebius_discriminants",
        all(
            value == case[3] and value < 0
            for value, case in zip(discriminants, gaussian_cases, strict=True)
        ),
        discriminants,
    )

    return {
        "signsplit": {
            "masses": masses,
            "information": information,
            "profiled": profiled,
            "stationarity": stationary,
            "reduced_information": reduced_information,
        },
        "tilt_identity": {
            "beta": beta,
            "t_means": t_means,
            "numerator": numerator,
            "quotient": quotient,
        },
        "stable_fixture": {
            "canonical_partitions": partition_count,
            "admissible_moves": len(gains),
            "max_gain": max(gains),
            "witness_value": stable_value,
            "global_value": best_value,
        },
        "minimal_atomic_boundary": assertions[-2]["detail"],
        "gaussian_discriminants": discriminants,
    }, assertions


def normal_pdf(value: float) -> float:
    """Return the standard normal density."""
    return math.exp(-0.5 * value * value) / math.sqrt(2 * math.pi)


def closed_form_cells(
    law: GaussianMixture, beta: float, cuts: tuple[float, float]
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate strip masses and score moments from independently derived formulas."""
    direction = np.array([1.0, -beta])
    edges = (-math.inf, cuts[0], cuts[1], math.inf)
    masses = np.zeros(3)
    moments = np.zeros((3, 2))
    for mixture_weight, mean_raw, covariance_raw in zip(
        law.weights, law.means, law.covariances, strict=True
    ):
        mean = np.asarray(mean_raw, dtype=float)
        covariance = np.asarray(covariance_raw, dtype=float)
        t_mean = float(direction @ mean)
        covariance_st = covariance @ direction
        t_variance = float(direction @ covariance_st)
        t_scale = math.sqrt(t_variance)
        for cell, (lower, upper) in enumerate(zip(edges[:-1], edges[1:], strict=True)):
            z_lower = (lower - t_mean) / t_scale
            z_upper = (upper - t_mean) / t_scale
            probability = float(ndtr(z_upper) - ndtr(z_lower))
            centered_t_moment = t_scale * (normal_pdf(z_lower) - normal_pdf(z_upper))
            masses[cell] += mixture_weight * probability
            moments[cell] += mixture_weight * (
                mean * probability + covariance_st / t_variance * centered_t_moment
            )
    return masses, moments


def adaptive_cells(
    law: GaussianMixture,
    beta: float,
    cuts: tuple[float, float],
    epsabs: float,
    epsrel: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Evaluate moments by independent adaptive one-dimensional quadrature."""
    direction = np.array([1.0, -beta])
    edges = (-math.inf, cuts[0], cuts[1], math.inf)
    masses = np.zeros(3)
    moments = np.zeros((3, 2))
    error = 0.0

    def integrand(value: float) -> np.ndarray:
        output = np.zeros(3)
        for mixture_weight, mean_raw, covariance_raw in zip(
            law.weights, law.means, law.covariances, strict=True
        ):
            mean = np.asarray(mean_raw, dtype=float)
            covariance = np.asarray(covariance_raw, dtype=float)
            t_mean = float(direction @ mean)
            covariance_st = covariance @ direction
            t_variance = float(direction @ covariance_st)
            density = normal_pdf((value - t_mean) / math.sqrt(t_variance)) / math.sqrt(t_variance)
            conditional = mean + covariance_st / t_variance * (value - t_mean)
            output += mixture_weight * np.array([1.0, conditional[0], conditional[1]]) * density
        return output

    for cell, bounds in enumerate(zip(edges[:-1], edges[1:], strict=True)):
        integral, estimate = quad_vec(integrand, bounds[0], bounds[1], epsabs=epsabs, epsrel=epsrel)
        masses[cell] = integral[0]
        moments[cell] = integral[1:]
        error = max(error, float(estimate))
    return masses, moments, error


def mixture_density(law: GaussianMixture, values: np.ndarray) -> np.ndarray:
    """Evaluate a planar Gaussian-mixture density."""
    output = np.zeros(values.shape[0])
    for weight, mean_raw, covariance_raw in zip(
        law.weights, law.means, law.covariances, strict=True
    ):
        mean = np.asarray(mean_raw)
        covariance = np.asarray(covariance_raw)
        inverse = np.linalg.inv(covariance)
        determinant = np.linalg.det(covariance)
        residual = values - mean
        exponent = -0.5 * np.einsum("ni,ij,nj->n", residual, inverse, residual)
        output += weight * np.exp(exponent) / (2 * math.pi * math.sqrt(determinant))
    return output


def integration_source_cells(
    law: GaussianMixture, beta: float, cuts: tuple[float, float], order: int, truncation: float
) -> tuple[np.ndarray, np.ndarray]:
    """Cross-check moments through the public tensor Gauss-Legendre source."""
    from scorequant import GaussLegendreConfig, IntegrationSource

    edges = (-truncation, cuts[0], cuts[1], truncation)
    masses = np.zeros(3)
    moments = np.zeros((3, 2))
    for cell, (lower, upper) in enumerate(zip(edges[:-1], edges[1:], strict=True)):

        def rotated_density(points: np.ndarray) -> np.ndarray:
            scores = np.column_stack([points[:, 0] + beta * points[:, 1], points[:, 1]])
            return mixture_density(law, scores)

        source = IntegrationSource(
            [[lower, upper], [-truncation, truncation]],
            density=rotated_density,
            quadrature=GaussLegendreConfig(order=order, max_points=order * order),
        ).materialize()
        rotated = np.asarray(source.observations)
        weights = np.asarray(source.weights)
        scores = np.column_stack([rotated[:, 0] + beta * rotated[:, 1], rotated[:, 1]])
        masses[cell] = float(weights.sum())
        moments[cell] = np.sum(weights[:, None] * scores, axis=0)
    return masses, moments


def run_quadrature() -> tuple[dict[str, object], list[dict[str, object]]]:
    """Cross-check independent adaptive, closed-form, and public-library routes."""
    law = bimodal(1.5, 0.4)
    beta = 0.7
    cuts = (-0.9, 0.8)
    closed_masses, closed_moments = closed_form_cells(law, beta, cuts)
    adaptive_masses, adaptive_moments, adaptive_error = adaptive_cells(
        law, beta, cuts, 1e-12, 1e-11
    )
    records = []
    for order, truncation in ((40, 8.0), (80, 10.0), (120, 12.0)):
        masses, moments = integration_source_cells(law, beta, cuts, order, truncation)
        records.append(
            {
                "order": order,
                "truncation": truncation,
                "masses": masses,
                "moments": moments,
                "max_mass_error_vs_adaptive": float(np.max(np.abs(masses - adaptive_masses))),
                "max_moment_error_vs_adaptive": float(np.max(np.abs(moments - adaptive_moments))),
            }
        )
    assertions = [
        {
            "name": "closed_form_vs_adaptive_mass",
            "passed": bool(np.max(np.abs(closed_masses - adaptive_masses)) < 1e-10),
            "detail": float(np.max(np.abs(closed_masses - adaptive_masses))),
        },
        {
            "name": "closed_form_vs_adaptive_moment",
            "passed": bool(np.max(np.abs(closed_moments - adaptive_moments)) < 1e-10),
            "detail": float(np.max(np.abs(closed_moments - adaptive_moments))),
        },
        {
            "name": "integration_source_converges",
            "passed": records[-1]["max_mass_error_vs_adaptive"] < 2e-8
            and records[-1]["max_moment_error_vs_adaptive"] < 2e-7,
            "detail": records[-1],
        },
    ]
    return {
        "law": law.as_record(),
        "beta": beta,
        "cuts": cuts,
        "adaptive": {
            "masses": adaptive_masses,
            "moments": adaptive_moments,
            "error_estimate": adaptive_error,
        },
        "closed_form": {"masses": closed_masses, "moments": closed_moments},
        "integration_source": records,
    }, assertions


def binned_quantities(masses: np.ndarray, moments: np.ndarray, beta: float) -> dict[str, object]:
    """Compute gate quantities from population cells."""
    means = moments / masses[:, None]
    information = sum(
        np.outer(moment, moment) / mass for mass, moment in zip(masses, moments, strict=True)
    )
    t_means = means[:, 0] - beta * means[:, 1]
    residual = float(information[0, 1] - beta * information[1, 1])
    eigenvalues = np.linalg.eigvalsh(information)
    profiled = (
        float(information[0, 0] - information[0, 1] ** 2 / information[1, 1])
        if information[1, 1] > 1e-15
        else None
    )
    return {
        "masses": masses,
        "moments": moments,
        "means": means,
        "information": information,
        "determinant": float(np.linalg.det(information)),
        "eigenvalues": eigenvalues,
        "lambda_min": float(eigenvalues[0]),
        "t_means": t_means,
        "projected_separation": float(np.min(np.diff(np.sort(t_means)))),
        "tilt_residual": residual,
        "profiled_value": profiled,
    }


def mixture_quantile(law: GaussianMixture, beta: float, probability: float) -> float:
    """Invert the scalar mixture CDF of T_beta."""
    direction = np.array([1.0, -beta])
    component_data = []
    for weight, mean_raw, covariance_raw in zip(
        law.weights, law.means, law.covariances, strict=True
    ):
        mean = float(direction @ np.asarray(mean_raw))
        variance = float(direction @ np.asarray(covariance_raw) @ direction)
        component_data.append((weight, mean, math.sqrt(variance)))
    lower = min(mean - 12 * scale for _, mean, scale in component_data)
    upper = max(mean + 12 * scale for _, mean, scale in component_data)

    def cdf(value: float) -> float:
        return sum(
            weight * float(ndtr((value - mean) / scale)) for weight, mean, scale in component_data
        )

    return float(brentq(lambda value: cdf(value) - probability, lower, upper))


def search_law(
    law: GaussianMixture,
    kappa: float,
    c0: float,
    gamma: float,
    levels: tuple[int, ...],
    sobol_power: int,
) -> dict[str, object]:
    """Run bounded full-window multistart over beta and two ordered cuts."""
    second = law.second_moment()
    moment_bound = float(np.trace(second))
    beta_bound = 2 * moment_bound / kappa
    direction_endpoints = [np.array([1.0, -value]) for value in (-beta_bound, beta_bound)]
    cut_bound = 0.0
    for direction in direction_endpoints:
        for mean_raw, covariance_raw in zip(law.means, law.covariances, strict=True):
            mean = abs(float(direction @ np.asarray(mean_raw)))
            scale = math.sqrt(float(direction @ np.asarray(covariance_raw) @ direction))
            cut_bound = max(cut_bound, mean + 10 * scale)
    minimum_gap = max(1e-6, cut_bound * 1e-8)
    log_gap_bounds = (math.log(minimum_gap), math.log(2 * cut_bound))

    def unpack(parameters: np.ndarray) -> tuple[float, tuple[float, float]]:
        beta, midpoint, log_gap = parameters
        gap = math.exp(log_gap)
        return float(beta), (float(midpoint - gap / 2), float(midpoint + gap / 2))

    def residual(parameters: np.ndarray) -> np.ndarray:
        beta, cuts = unpack(parameters)
        masses, moments = closed_form_cells(law, beta, cuts)
        if np.any(masses <= 1e-14):
            return np.array([1e3, 1e3, 1e3])
        means = moments / masses[:, None]
        t_means = means[:, 0] - beta * means[:, 1]
        information = sum(
            np.outer(moment, moment) / mass for mass, moment in zip(masses, moments, strict=True)
        )
        scale = max(1.0, moment_bound)
        return np.array(
            [
                cuts[0] - 0.5 * (t_means[0] + t_means[1]),
                cuts[1] - 0.5 * (t_means[1] + t_means[2]),
                (information[0, 1] - beta * information[1, 1]) / scale,
            ]
        )

    lower_bounds = np.array([-beta_bound, -cut_bound, log_gap_bounds[0]])
    upper_bounds = np.array([beta_bound, cut_bound, log_gap_bounds[1]])
    probability_pairs = ((0.10, 0.50), (0.15, 0.70), (0.25, 0.75), (0.30, 0.85), (0.50, 0.90))
    starts: list[np.ndarray] = []
    refinement_counts: list[dict[str, int]] = []
    for count in levels:
        before = len(starts)
        for beta in np.linspace(-beta_bound, beta_bound, count):
            for first_probability, second_probability in probability_pairs:
                first = mixture_quantile(law, float(beta), first_probability)
                second_cut = mixture_quantile(law, float(beta), second_probability)
                starts.append(
                    np.array([beta, 0.5 * (first + second_cut), math.log(second_cut - first)])
                )
        refinement_counts.append({"beta_grid": count, "new_starts": len(starts) - before})
    sampler = qmc.Sobol(d=3, scramble=True, seed=SEED_BASE)
    sobol = sampler.random_base2(sobol_power)
    starts.extend(lower_bounds + sobol * (upper_bounds - lower_bounds))

    candidates: list[dict[str, object]] = []
    converged = 0
    boundary_solutions = 0
    singular_jacobians = 0
    for start in starts:
        fitted = least_squares(
            residual,
            np.clip(start, lower_bounds, upper_bounds),
            bounds=(lower_bounds, upper_bounds),
            xtol=1e-11,
            ftol=1e-11,
            gtol=1e-11,
            max_nfev=300,
        )
        residual_norm = float(np.max(np.abs(residual(fitted.x))))
        if not fitted.success or residual_norm > 1e-8:
            continue
        converged += 1
        if np.any(np.minimum(fitted.x - lower_bounds, upper_bounds - fitted.x) < 1e-7):
            boundary_solutions += 1
        singular_values = np.linalg.svd(fitted.jac, compute_uv=False)
        singular_jacobians += int(singular_values[-1] < 1e-7)
        beta, cuts = unpack(fitted.x)
        masses, moments, integration_error = adaptive_cells(law, beta, cuts, 1e-12, 1e-11)
        quantities = binned_quantities(masses, moments, beta)
        reintegrated_residual = max(
            abs(cuts[0] - 0.5 * (quantities["t_means"][0] + quantities["t_means"][1])),
            abs(cuts[1] - 0.5 * (quantities["t_means"][1] + quantities["t_means"][2])),
            abs(quantities["tilt_residual"]) / max(1.0, moment_bound),
        )
        if reintegrated_residual > 2e-8:
            continue
        key = np.array([beta, cuts[0], cuts[1]])
        if any(np.max(np.abs(key - np.array(item["root"]))) < 1e-7 for item in candidates):
            continue
        gate_pass = (
            quantities["lambda_min"] >= kappa
            and float(np.min(masses)) >= c0
            and quantities["projected_separation"] >= gamma
        )
        candidates.append(
            {
                "root": key,
                "residual": reintegrated_residual,
                "integration_error": integration_error,
                "gate_pass": gate_pass,
                **quantities,
            }
        )

    return {
        "law": law.as_record(),
        "M": moment_bound,
        "kappa": kappa,
        "c0": c0,
        "gamma": gamma,
        "beta_bound": beta_bound,
        "cut_bound": cut_bound,
        "refinement": refinement_counts,
        "sobol_points": 2**sobol_power,
        "starts": len(starts),
        "converged_starts": converged,
        "boundary_solutions": boundary_solutions,
        "singular_jacobians": singular_jacobians,
        "roots": candidates,
        "root_count": len(candidates),
        "gate_root_count": sum(int(item["gate_pass"]) for item in candidates),
        "interpretation": (
            "measured exhaustive multistart over the compact bound; "
            "not interval-certified proof of absence"
        ),
    }


def run_search(
    kappa: float, c0: float, gamma: float, levels: tuple[int, ...], sobol_power: int
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Search all registered law inputs independently."""
    records = []
    for law in all_laws():
        record = search_law(law, kappa, c0, gamma, levels, sobol_power)
        records.append(record)
        print(
            f"[search] {law.name}: B={record['beta_bound']:.4g} "
            f"starts={record['starts']} roots={record['root_count']} "
            f"gate={record['gate_root_count']}",
            flush=True,
        )
    mix_record = next(record for record in records if record["law"]["name"] == "mix3")
    class_l_records = [record for record in records if record["law"]["name"] != "mix3"]
    assertions = [
        {
            "name": "full_beta_bounds_used",
            "passed": all(
                abs(record["beta_bound"] - 2 * record["M"] / kappa) < 1e-12 for record in records
            ),
            "detail": {record["law"]["name"]: record["beta_bound"] for record in records},
        },
        {
            "name": "class_L_no_gate_roots_found",
            "passed": all(record["gate_root_count"] == 0 for record in class_l_records),
            "detail": {
                record["law"]["name"]: record["gate_root_count"] for record in class_l_records
            },
        },
        {
            "name": "mix3_gate_root_found",
            "passed": mix_record["gate_root_count"] >= 1,
            "detail": mix_record["roots"],
        },
    ]
    return {
        "laws": records,
        "totals": {
            "laws": len(records),
            "starts": sum(record["starts"] for record in records),
            "roots": sum(record["root_count"] for record in records),
            "gate_roots": sum(record["gate_root_count"] for record in records),
        },
    }, assertions


def sample_law(law: GaussianMixture, size: int, seed: int) -> np.ndarray:
    """Sample a declared mixture independently with NumPy's seeded generator."""
    rng = np.random.default_rng(seed)
    components = rng.choice(len(law.weights), size=size, p=law.weights)
    output = np.empty((size, 2), dtype=float)
    for component in range(len(law.weights)):
        selected = np.flatnonzero(components == component)
        if len(selected):
            output[selected] = rng.multivariate_normal(
                law.means[component], law.covariances[component], size=len(selected)
            )
    return output - output.mean(axis=0)


def empirical_geometry(scores: np.ndarray, labels: np.ndarray, bins: int) -> dict[str, object]:
    """Recompute terminal geometry directly from labels."""
    weights = np.full(len(scores), 1 / len(scores))
    masses = np.bincount(labels, weights=weights, minlength=bins)
    moments = np.vstack(
        [
            np.sum(weights[labels == cell, None] * scores[labels == cell], axis=0)
            for cell in range(bins)
        ]
    )
    quantities = binned_quantities(masses, moments, 0.0)
    information = quantities["information"]
    beta = float(information[0, 1] / information[1, 1])
    means = moments / masses[:, None]
    projected = means[:, 0] - beta * means[:, 1]
    return {
        "beta": beta,
        "information": information,
        "lambda_min": float(np.linalg.eigvalsh(information)[0]),
        "i11": float(information[1, 1]),
        "min_mass": float(np.min(masses)),
        "projected_separation": float(
            np.min(np.abs(projected[:, None] - projected[None, :] + np.eye(bins) * 1e100))
        ),
    }


def run_library(
    law_name: str, size: int, rep: int, seed_kind: str
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Run one seeded public-library audit reproduction."""
    from scorequant import (
        DExchangeConfig,
        ProfiledDOptimality,
        efficient_score_bound,
        optimize_partition,
    )

    law_map = {law.name: law for law in all_laws()}
    law = law_map[law_name]
    seed = SEED_BASE + 1000 * size + rep
    scores = sample_law(law, size, seed)
    bound = efficient_score_bound(scores, interest=(0,), n_bins=3)
    configuration = DExchangeConfig(
        seed=seed,
        solver_restarts=1,
        **({"init": "random"} if seed_kind == "random" else {}),
    )
    keyword_arguments: dict[str, object] = {}
    if seed_kind == "efficient":
        keyword_arguments["initial_labels"] = np.asarray(bound.labels)
    result = optimize_partition(
        scores,
        n_bins=3,
        criterion=ProfiledDOptimality(interest=(0,)),
        config=configuration,
        **keyword_arguments,
    )
    labels = np.asarray(result.labels)
    geometry = empirical_geometry(scores, labels, 3)
    record = {
        "law": law.as_record(),
        "size": size,
        "rep": rep,
        "seed": seed,
        "seed_kind": seed_kind,
        "objective_log": float(result.objective),
        "upper_bound_log": float(bound.upper_bound),
        "gap_log": float(bound.upper_bound - result.objective),
        "exchange_stable": bool(result.exchange_stable),
        "geometry": geometry,
    }
    assertions = [
        {
            "name": "library_terminal_exchange_stable",
            "passed": bool(result.exchange_stable),
            "detail": record,
        },
        {
            "name": "seed_formula",
            "passed": seed == 20560832 if size == 300 and rep == 1 else True,
            "detail": seed,
        },
    ]
    return record, assertions


def json_default(value: object) -> object:
    """Serialize exact and NumPy values."""
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer, np.bool_)):
        return value.item()
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


def main() -> int:
    """Run one explicitly selected audit mode."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("mode", choices=("exact", "quadrature", "search", "library"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--kappa", type=float, default=1.0)
    parser.add_argument("--c0", type=float, default=0.05)
    parser.add_argument("--gamma", type=float, default=0.1)
    parser.add_argument("--levels", default="17,33")
    parser.add_argument("--sobol-power", type=int, default=8)
    parser.add_argument("--law", default="mix3")
    parser.add_argument("--size", type=int, default=300)
    parser.add_argument("--rep", type=int, default=1)
    parser.add_argument(
        "--seed-kind", choices=("efficient", "kmeans", "random"), default="efficient"
    )
    arguments = parser.parse_args()
    started = time.monotonic()
    if arguments.mode == "exact":
        summary, assertions = run_exact()
        parameters = {
            "fixtures": [
                "CE-DS-LCM-SIGNSPLIT-MARGIN-001",
                "CE-DS-POP-WASTED-CELLS-001",
                "CE-DS-STABLE-MARGIN-RETAINING-001",
            ]
        }
        tolerances = {"claim_relevant": "fractions.Fraction; no floating tolerance"}
    elif arguments.mode == "quadrature":
        summary, assertions = run_quadrature()
        parameters = {"law": "bimodal(m=1.5,s=0.4)", "beta": 0.7, "cuts": [-0.9, 0.8]}
        tolerances = {"adaptive_epsabs": 1e-12, "adaptive_epsrel": 1e-11}
    elif arguments.mode == "search":
        levels = tuple(int(value) for value in arguments.levels.split(","))
        summary, assertions = run_search(
            arguments.kappa, arguments.c0, arguments.gamma, levels, arguments.sobol_power
        )
        parameters = {
            "kappa": arguments.kappa,
            "c0": arguments.c0,
            "gamma": arguments.gamma,
            "levels": levels,
            "sobol_power": arguments.sobol_power,
        }
        tolerances = {
            "solver": 1e-11,
            "root_acceptance": 1e-8,
            "adaptive_recheck": 2e-8,
            "deduplication": 1e-7,
        }
    else:
        summary, assertions = run_library(
            arguments.law, arguments.size, arguments.rep, arguments.seed_kind
        )
        parameters = {
            "law": arguments.law,
            "size": arguments.size,
            "rep": arguments.rep,
            "seed_kind": arguments.seed_kind,
        }
        tolerances = {"runtime": "JAX float64", "stability": "public result.exchange_stable"}
    artifact = envelope(arguments.mode, parameters, tolerances, summary, assertions, started)
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    arguments.out.write_text(json.dumps(artifact, indent=2, default=json_default) + "\n")
    print(
        f"[{arguments.mode}] {artifact['result']} runtime={artifact['runtime_seconds']:.2f}s "
        f"artifact={arguments.out}",
        flush=True,
    )
    return 0 if artifact["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
