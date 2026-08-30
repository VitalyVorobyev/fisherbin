"""Independent exact audit harness for the DS16 stable-margins complex.

This program deliberately does not import ``ds_stable_margins`` or any of its
classification helpers.  Claim-relevant finite calculations use
``fractions.Fraction`` and every candidate relocation is evaluated by rebuilding
the complete binned information matrix from the moved labeling.

Modes
-----
fixtures
    Recompute both DS16 N=8 fixtures from raw scores and labels, including full
    partition-lattice globality/interval checks and every admissible move.
census
    Reproduce selected researcher census instances (centered06 and mix3,
    N=10 and N=12, rep 1) with the independent from-scratch classifier.
adversarial
    Exhaustive small rational attacks: unequal weights, duplicates, ties,
    singleton pressure, singular/near-singular nuisance, and d=1/d=3 rank
    controls.
library
    Public-API seed comparison at N=100.  This is the only floating-point mode.
all-exact
    fixtures + census + adversarial.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import statistics
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[1]
SEED_BASE = 20260830


def provenance(mode: str, parameters: dict[str, object]) -> dict[str, object]:
    """Return the reproducibility record required by the numerical protocol."""
    script = Path(__file__)
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=RESEARCH.parent,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()
    return {
        "mode": mode,
        "parameters": parameters,
        "git_revision": revision,
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }


class Lcg:
    """Small deterministic integer generator, independent of NumPy."""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def integer(self, low: int, high: int) -> int:
        self.state = (1664525 * self.state + 1013904223) & 0xFFFFFFFF
        return low + (self.state >> 16) % (high - low + 1)


def normal_grid(rng: Lcg, denominator: int = 1024) -> Fraction:
    """Twelve-uniform exact rational approximation to a standard normal."""
    return Fraction(sum(rng.integer(0, denominator - 1) for _ in range(12)), denominator) - 6


def sample_law(law: str, size: int, seed: int) -> list[tuple[Fraction, Fraction]]:
    """Generate the two census laws directly from their mathematical definitions."""
    rng = Lcg(seed)
    rows: list[tuple[Fraction, Fraction]] = []
    for _ in range(size):
        z1 = normal_grid(rng)
        z2 = normal_grid(rng)
        if law == "centered06":
            rows.append((z1, Fraction(3, 5) * z1 + Fraction(4, 5) * z2))
        elif law == "mix3":
            component = rng.integer(0, 2)
            location = [(-2, 1), (0, -2), (2, 1)][component]
            rows.append((Fraction(location[0]) + z1 / 2, Fraction(location[1]) + z2 / 2))
        else:
            raise ValueError(f"unknown law: {law}")
    return rows


def center(rows: list[tuple[Fraction, ...]], weights: list[Fraction]) -> list[tuple[Fraction, ...]]:
    """Center rows with their normalized positive weights."""
    total = sum(weights)
    dimension = len(rows[0])
    mean = [
        sum(w * row[j] for row, w in zip(rows, weights, strict=True)) / total
        for j in range(dimension)
    ]
    return [tuple(row[j] - mean[j] for j in range(dimension)) for row in rows]


def canonical_partitions(size: int, bins: int):
    """Yield surjective restricted-growth labelings without labeled duplicates."""
    labels = [0] * size

    def visit(position: int, largest: int):
        if position == size:
            if largest == bins - 1:
                yield tuple(labels)
            return
        missing = bins - 1 - largest
        if size - position < missing:
            return
        for label in range(min(largest + 1, bins - 1) + 1):
            labels[position] = label
            yield from visit(position + 1, max(largest, label))

    yield from visit(1, 0)


def canonicalize(labels: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    mapping: dict[int, int] = {}
    result = []
    for label in labels:
        mapping.setdefault(label, len(mapping))
        result.append(mapping[label])
    return tuple(result)


def cell_state(
    rows: list[tuple[Fraction, ...]],
    weights: list[Fraction],
    labels: tuple[int, ...] | list[int],
    bins: int,
) -> tuple[list[Fraction], list[list[Fraction]], list[list[Fraction]]]:
    """Rebuild all cell moments and the full binned information matrix."""
    dimension = len(rows[0])
    masses = [Fraction(0) for _ in range(bins)]
    moments = [[Fraction(0) for _ in range(dimension)] for _ in range(bins)]
    for row, weight, label in zip(rows, weights, labels, strict=True):
        masses[label] += weight
        for coordinate in range(dimension):
            moments[label][coordinate] += weight * row[coordinate]
    if any(mass <= 0 for mass in masses):
        raise ValueError("labeling contains an empty or zero-mass cell")
    information = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for mass, moment in zip(masses, moments, strict=True):
        for row_index in range(dimension):
            for column_index in range(dimension):
                information[row_index][column_index] += (
                    moment[row_index] * moment[column_index] / mass
                )
    return masses, moments, information


def profiled_value(information: list[list[Fraction]], nuisance_dimension: int) -> Fraction | None:
    """Return the scalar-POI Schur value, or None at singular nuisance."""
    if nuisance_dimension == 1:
        nuisance = information[1][1]
        if nuisance == 0:
            return None
        return information[0][0] - information[0][1] ** 2 / nuisance
    if nuisance_dimension == 2:
        a = information[1][1]
        b = information[1][2]
        c = information[2][2]
        determinant = a * c - b * b
        if determinant == 0:
            return None
        p = information[0][1]
        q = information[0][2]
        tax = (c * p * p - 2 * b * p * q + a * q * q) / determinant
        return information[0][0] - tax
    raise ValueError("audit supports nuisance dimension one or two")


def value_for(
    rows: list[tuple[Fraction, ...]],
    weights: list[Fraction],
    labels: tuple[int, ...] | list[int],
    bins: int,
) -> Fraction | None:
    _, _, information = cell_state(rows, weights, labels, bins)
    return profiled_value(information, len(rows[0]) - 1)


def admissible_moves(labels: tuple[int, ...] | list[int], bins: int):
    counts = [labels.count(label) for label in range(bins)]
    for row_index, source in enumerate(labels):
        if counts[source] <= 1:
            continue
        for destination in range(bins):
            if destination != source:
                yield row_index, source, destination


def move_labels(
    labels: tuple[int, ...] | list[int], row_index: int, destination: int
) -> tuple[int, ...]:
    moved = list(labels)
    moved[row_index] = destination
    return tuple(moved)


def stability_report(
    rows: list[tuple[Fraction, ...]],
    weights: list[Fraction],
    labels: tuple[int, ...] | list[int],
    bins: int,
) -> dict[str, object]:
    """Classify stability by rebuilding every moved state from scratch."""
    current = value_for(rows, weights, labels, bins)
    if current is None:
        return {"feasible": False, "stable": None, "move_count": 0, "max_gain": None}
    gains: list[Fraction] = []
    for row_index, _, destination in admissible_moves(labels, bins):
        candidate = value_for(rows, weights, move_labels(labels, row_index, destination), bins)
        if candidate is not None:
            gains.append(candidate - current)
    maximum = max(gains) if gains else None
    return {
        "feasible": True,
        "stable": maximum is None or maximum <= 0,
        "move_count": len(gains),
        "max_gain": maximum,
    }


def full_second_moment(
    rows: list[tuple[Fraction, Fraction]], weights: list[Fraction]
) -> list[list[Fraction]]:
    total = sum(weights)
    return [
        [
            sum(weight * row[i] * row[j] for row, weight in zip(rows, weights, strict=True)) / total
            for j in range(2)
        ]
        for i in range(2)
    ]


def efficient_scores(
    rows: list[tuple[Fraction, Fraction]], weights: list[Fraction]
) -> tuple[list[Fraction], Fraction]:
    information = full_second_moment(rows, weights)
    slope = information[0][1] / information[1][1]
    scores = [row[0] - slope * row[1] for row in rows]
    assert (
        sum(
            weight * score * row[1]
            for row, weight, score in zip(rows, weights, scores, strict=True)
        )
        == 0
    )
    return scores, slope


def between_value(
    values: list[Fraction], weights: list[Fraction], labels: tuple[int, ...] | list[int], bins: int
) -> Fraction:
    masses = [Fraction(0) for _ in range(bins)]
    sums = [Fraction(0) for _ in range(bins)]
    for value, weight, label in zip(values, weights, labels, strict=True):
        masses[label] += weight
        sums[label] += weight * value
    return sum(value_sum * value_sum / mass for value_sum, mass in zip(sums, masses, strict=True))


def interval_optimum(
    values: list[Fraction], weights: list[Fraction], bins: int
) -> tuple[Fraction, tuple[int, ...]]:
    order = sorted(range(len(values)), key=lambda index: (values[index], index))
    best_value: Fraction | None = None
    best_labels: tuple[int, ...] | None = None
    for cuts in itertools.combinations(range(1, len(values)), bins - 1):
        bounds = (0, *cuts, len(values))
        labels = [0] * len(values)
        for label, (start, stop) in enumerate(zip(bounds, bounds[1:])):
            for position in range(start, stop):
                labels[order[position]] = label
        candidate = between_value(values, weights, labels, bins)
        if best_value is None or candidate > best_value:
            best_value = candidate
            best_labels = tuple(labels)
    assert best_value is not None and best_labels is not None
    return best_value, best_labels


def exact_margins(
    rows: list[tuple[Fraction, Fraction]],
    weights: list[Fraction],
    labels: tuple[int, ...] | list[int],
    bins: int,
) -> dict[str, Fraction]:
    masses, moments, information = cell_state(rows, weights, labels, bins)
    value = profiled_value(information, 1)
    assert value is not None
    nuisance = information[1][1]
    determinant = information[0][0] * nuisance - information[0][1] ** 2
    trace = information[0][0] + nuisance
    slope = information[0][1] / nuisance
    projected = [
        moment[0] / mass - slope * moment[1] / mass
        for mass, moment in zip(masses, moments, strict=True)
    ]
    separation = min(
        abs(projected[left] - projected[right])
        for left in range(bins)
        for right in range(left + 1, bins)
    )
    return {
        "value": value,
        "i11": nuisance,
        "det_over_trace": determinant / trace if trace else Fraction(0),
        "min_mass": min(masses),
        "projected_separation": separation,
    }


def fixture_rows(identifier: str):
    fixture = json.loads((RESEARCH / "COUNTEREXAMPLES" / f"{identifier}.json").read_text())
    rows = [tuple(Fraction(value) for value in row) for row in fixture["scores"]]
    weights = [Fraction(value) for value in fixture["weights"]]
    return fixture, rows, weights


def run_fixtures() -> dict[str, object]:
    """Recompute the two declared fixtures without consuming derived fields."""
    output: dict[str, object] = {}

    fixture, rows, weights = fixture_rows("CE-DS-STABLE-MARGIN-RETAINING-001")
    bins = int(fixture["K"])
    labels = tuple(fixture["labels_before"])
    margins = exact_margins(rows, weights, labels, bins)
    stability = stability_report(rows, weights, labels, bins)
    best_value: Fraction | None = None
    best_labels: tuple[int, ...] | None = None
    lattice_size = 0
    for candidate in canonical_partitions(len(rows), bins):
        lattice_size += 1
        candidate_value = value_for(rows, weights, candidate, bins)
        if candidate_value is not None and (best_value is None or candidate_value > best_value):
            best_value = candidate_value
            best_labels = candidate
    efficient, slope = efficient_scores(rows, weights)
    interval_value, interval_labels = interval_optimum(efficient, weights, bins)
    assert stability["stable"] is True and best_value is not None and best_labels is not None
    assert margins["value"] < best_value <= interval_value
    output[fixture["id"]] = {
        "lattice_size": lattice_size,
        "profiled_value": margins["value"],
        "global_value": best_value,
        "global_labels": "".join(str(label) for label in best_labels),
        "interval_value": interval_value,
        "interval_labels": canonicalize(interval_labels),
        "full_sample_slope": slope,
        "stability": stability,
        "margins": margins,
    }

    fixture, rows, weights = fixture_rows("CE-DS-INTERVAL-SEED-UNSTABLE-001")
    bins = int(fixture["K"])
    efficient, slope = efficient_scores(rows, weights)
    interval_value, interval_labels = interval_optimum(efficient, weights, bins)
    interval_labels = canonicalize(interval_labels)
    move = fixture["exact_quantities"]["improving_move"]
    before = value_for(rows, weights, interval_labels, bins)
    after_labels = move_labels(interval_labels, int(move["row"]), int(move["to_cell"]))
    after = value_for(rows, weights, after_labels, bins)
    assert before is not None and after is not None and after > before
    output[fixture["id"]] = {
        "interval_value": interval_value,
        "interval_labels": interval_labels,
        "full_sample_slope": slope,
        "profiled_value_before": before,
        "profiled_value_after": after,
        "exact_gain": after - before,
        "before_margins": exact_margins(rows, weights, interval_labels, bins),
        "after_margins": exact_margins(rows, weights, after_labels, bins),
        "stability": stability_report(rows, weights, interval_labels, bins),
    }

    return {"provenance": provenance("fixtures", {"fixtures": list(output)}), "fixtures": output}


def pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2 or statistics.pstdev(left) == 0 or statistics.pstdev(right) == 0:
        return None
    left_mean = statistics.fmean(left)
    right_mean = statistics.fmean(right)
    covariance = statistics.fmean(
        (x - left_mean) * (y - right_mean) for x, y in zip(left, right, strict=True)
    )
    return covariance / (statistics.pstdev(left) * statistics.pstdev(right))


def source_instance(law: str, size: int, rep: int) -> dict[str, object]:
    source = json.loads(
        (
            RESEARCH / "WORK" / "artifacts" / "DS-STABLE-MARGINS-COMPILE" / "census-summary.json"
        ).read_text()
    )
    for instance in source["census"]["instances"]:
        if instance["law"] == law and instance["n"] == size and instance["rep"] == rep:
            return instance
    raise KeyError((law, size, rep))


def census_instance(law: str, size: int, rep: int = 1, bins: int = 3) -> dict[str, object]:
    seed = SEED_BASE + 1000 * size + rep
    weights = [Fraction(1, size) for _ in range(size)]
    rows = center(sample_law(law, size, seed), weights)
    efficient, slope = efficient_scores(rows, weights)
    interval_value, interval_labels = interval_optimum(efficient, weights, bins)
    interval_labels = canonicalize(interval_labels)
    start = time.monotonic()
    feasible = 0
    singular = 0
    stable_rows: list[dict[str, object]] = []
    global_value: Fraction | None = None
    global_labels: tuple[int, ...] | None = None
    tie_count = 0
    lattice_size = 0
    for labels in canonical_partitions(size, bins):
        lattice_size += 1
        value = value_for(rows, weights, labels, bins)
        if value is None:
            singular += 1
            continue
        feasible += 1
        if global_value is None or value > global_value:
            global_value = value
            global_labels = labels
            tie_count = 1
        elif value == global_value:
            tie_count += 1
        classification = stability_report(rows, weights, labels, bins)
        if classification["stable"]:
            margins = exact_margins(rows, weights, labels, bins)
            assert (
                margins["value"]
                <= between_value(efficient, weights, labels, bins)
                <= interval_value
            )
            stable_rows.append(
                {"labels": labels, **margins, "max_gain": classification["max_gain"]}
            )
    assert global_value is not None and global_labels is not None
    nonglobal = [row for row in stable_rows if row["value"] < global_value]
    gaps = [float((interval_value - row["value"]) / interval_value) for row in stable_rows]
    nuisances = [float(row["i11"]) for row in stable_rows]
    reference = source_instance(law, size, rep)
    interval_stability = stability_report(rows, weights, interval_labels, bins)

    # Exact agreement gates.  These consume only the committed output summary,
    # never the researcher's implementation or classifier.
    assert lattice_size == reference["canonical_labelings"]
    assert feasible == reference["feasible"] and singular == reference["singular"]
    assert len(stable_rows) == reference["stable"]
    assert len(nonglobal) == reference["stable_nonglobal"]
    assert str(global_value) == reference["global"]["phi"]
    assert str(interval_value) == reference["interval_value_v_k"]
    assert interval_stability["stable"] == reference["interval_labeling"]["stable"]

    result = {
        "law": law,
        "n": size,
        "rep": rep,
        "seed": seed,
        "lattice_size": lattice_size,
        "feasible": feasible,
        "singular": singular,
        "stable": len(stable_rows),
        "stable_nonglobal": len(nonglobal),
        "exact_tie_multiplicity": tie_count,
        "global_value": global_value,
        "global_labels": global_labels,
        "interval_value": interval_value,
        "interval_stable": interval_stability["stable"],
        "slope": slope,
        "stable_i11_min": min(row["i11"] for row in stable_rows),
        "stable_i11_max": max(row["i11"] for row in stable_rows),
        "margin_threshold_i11": Fraction(1, 25),
        "margin_retaining_nonglobal": sum(row["i11"] > Fraction(1, 25) for row in nonglobal),
        "gap_i11_pearson": pearson(gaps, nuisances),
        "source_summary_exact_match": True,
        "wall_seconds": round(time.monotonic() - start, 3),
    }
    print(
        f"[census] {law} N={size}: {len(stable_rows)} stable, "
        f"{len(nonglobal)} nonglobal, corr={result['gap_i11_pearson']:.3f}, "
        f"interval_stable={result['interval_stable']}, wall={result['wall_seconds']}s",
        flush=True,
    )
    return result


def run_census() -> dict[str, object]:
    """Run the four exact sample instances and compare committed headlines."""
    instances = [census_instance(law, size) for law in ("centered06", "mix3") for size in (10, 12)]
    source = json.loads(
        (
            RESEARCH / "WORK" / "artifacts" / "DS-STABLE-MARGINS-COMPILE" / "census-summary.json"
        ).read_text()
    )
    source_stable_counts = [instance["stable"] for instance in source["census"]["instances"]]
    return {
        "provenance": provenance(
            "census", {"laws": ["centered06", "mix3"], "sizes": [10, 12], "rep": 1}
        ),
        "instances": instances,
        "headline_checks": {
            "all_source_counts_match": all(
                instance["source_summary_exact_match"] for instance in instances
            ),
            "all_have_nonglobal_stable_states": all(
                instance["stable_nonglobal"] > 0 for instance in instances
            ),
            "all_centered_correlations_negative": all(
                instance["gap_i11_pearson"] is not None and instance["gap_i11_pearson"] < 0
                for instance in instances
                if instance["law"] == "centered06"
            ),
            "all_centered_have_margin_retaining_nonglobal": all(
                instance["margin_retaining_nonglobal"] > 0
                for instance in instances
                if instance["law"] == "centered06"
            ),
            "committed_full_census_stable_range": [
                min(source_stable_counts),
                max(source_stable_counts),
            ],
            "registered_range_18_to_944_is_accurate": min(source_stable_counts) == 18,
        },
    }


ADVERSARIAL = [
    {
        "name": "duplicates",
        "rows": [(2, 1), (2, 1), (-1, 2), (-1, -1), (-1, -1), (-1, -2)],
        "weights": ["1/6"] * 6,
    },
    {
        "name": "unequal_weights",
        "rows": [(3, 1), (1, -2), (-1, 2), (-2, -1), (0, 3), (-1, -3)],
        "weights": ["1/4", "1/8", "1/8", "1/8", "1/4", "1/8"],
    },
    {
        "name": "exact_ties",
        "rows": [(2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 3), (-2, -3), (2, 2), (2, -2)],
        "weights": ["1/8"] * 8,
    },
    {
        "name": "near_singular_nuisance",
        "rows": [
            (3, "1/10000"),
            (1, "-2/10000"),
            (-1, "2/10000"),
            (-2, "-1/10000"),
            (0, "3/10000"),
            (-1, "-3/10000"),
        ],
        "weights": ["1/6"] * 6,
    },
    {
        "name": "tiny_cell_pressure",
        "rows": [(4, 2), (-4, -2), (1, -1), (-1, 1), (2, -2), (-2, 2), (3, 3)],
        "weights": ["1/2", "1/12", "1/12", "1/12", "1/12", "1/12", "1/12"],
    },
]


def adversarial_case(configuration: dict[str, object], bins: int = 3) -> dict[str, object]:
    raw_rows = [tuple(Fraction(value) for value in row) for row in configuration["rows"]]
    raw_weights = [Fraction(value) for value in configuration["weights"]]
    total = sum(raw_weights)
    weights = [weight / total for weight in raw_weights]
    rows = center(raw_rows, weights)
    efficient, _ = efficient_scores(rows, weights)
    interval_value, _ = interval_optimum(efficient, weights, bins)
    feasible = singular = stable = identity_failures = 0
    global_value: Fraction | None = None
    tie_count = 0
    for labels in canonical_partitions(len(rows), bins):
        value = value_for(rows, weights, labels, bins)
        if value is None:
            singular += 1
            continue
        feasible += 1
        between = between_value(efficient, weights, labels, bins)
        if not (value <= between <= interval_value):
            identity_failures += 1
        if global_value is None or value > global_value:
            global_value = value
            tie_count = 1
        elif value == global_value:
            tie_count += 1
        if stability_report(rows, weights, labels, bins)["stable"]:
            stable += 1
    assert identity_failures == 0
    return {
        "name": configuration["name"],
        "n": len(rows),
        "canonical_labelings": feasible + singular,
        "feasible": feasible,
        "singular": singular,
        "stable": stable,
        "global_tie_multiplicity": tie_count,
        "sandwich_failures": identity_failures,
    }


def run_adversarial() -> dict[str, object]:
    datasets = [adversarial_case(configuration) for configuration in ADVERSARIAL]

    # d=3, d_lambda=2 cardinality boundary, recomputed from the raw fixture.
    rank_fixture = json.loads(
        (RESEARCH / "COUNTEREXAMPLES" / "CE-DS-MARGINS-RANK-VACUITY-001.json").read_text()
    )
    rows3 = [tuple(Fraction(value) for value in row) for row in rank_fixture["scores"]]
    weights3 = [Fraction(value) for value in rank_fixture["weights"]]
    k3_values = [
        value_for(rows3, weights3, labels, 3) for labels in canonical_partitions(len(rows3), 3)
    ]
    feasible_k3 = [value for value in k3_values if value is not None]
    assert feasible_k3 and all(value == 0 for value in feasible_k3)
    k4_labels = tuple(range(len(rows3)))
    k4_value = value_for(rows3, weights3, k4_labels, 4)
    assert k4_value is not None and k4_value > 0

    # d=1 is not an in-bin profiled problem; retain it as a rank control.
    scalar = [Fraction(-3), Fraction(-1), Fraction(1), Fraction(3)]
    scalar_labels = (0, 0, 1, 1)
    scalar_moments = [
        sum(scalar[i] for i in range(4) if scalar_labels[i] == cell) for cell in range(2)
    ]
    scalar_rank_positive = any(moment != 0 for moment in scalar_moments)

    return {
        "provenance": provenance(
            "adversarial", {"datasets": [item["name"] for item in ADVERSARIAL]}
        ),
        "datasets": datasets,
        "d1_rank_control": {
            "profiled_ds_applicable": False,
            "between_rank_positive": scalar_rank_positive,
        },
        "d3_rank_boundary": {
            "n": len(rows3),
            "d_lambda": 2,
            "k3_feasible": len(feasible_k3),
            "k3_all_profiled_zero": True,
            "k4_profiled_positive": k4_value,
        },
        "new_counterexample_found": False,
    }


def float_margins(scores, labels, bins: int) -> dict[str, float]:
    import numpy as np

    information = np.zeros((2, 2), dtype=float)
    centroids = []
    masses = []
    for label in range(bins):
        selected = labels == label
        mass = float(selected.mean())
        moment = scores[selected].sum(axis=0) / scores.shape[0]
        information += np.outer(moment, moment) / mass
        masses.append(mass)
        centroids.append(moment / mass)
    eigenvalues = np.linalg.eigvalsh(information)
    slope = information[0, 1] / information[1, 1]
    projected = [centroid[0] - slope * centroid[1] for centroid in centroids]
    separation = min(
        abs(projected[left] - projected[right])
        for left in range(bins)
        for right in range(left + 1, bins)
    )
    return {
        "i11": float(information[1, 1]),
        "lambda_min": float(eigenvalues[0]),
        "min_mass": min(masses),
        "projected_separation": float(separation),
    }


def run_library(size: int = 100, bins: int = 3) -> dict[str, object]:
    import numpy as np

    from scorequant import (
        DExchangeConfig,
        ProfiledDOptimality,
        efficient_score_bound,
        optimize_partition,
    )

    runs = []
    for law in ("gauss06", "mix3"):
        seed = SEED_BASE + 100000 + 1000 * size + 1
        rng = np.random.default_rng(seed)
        if law == "gauss06":
            scores = rng.multivariate_normal([0.0, 0.0], [[1.0, 0.6], [0.6, 1.0]], size=size)
        else:
            components = rng.integers(0, 3, size=size)
            locations = np.array([[-2.0, 1.0], [0.0, -2.0], [2.0, 1.0]])
            scores = locations[components] + rng.normal(size=(size, 2)) / 2
        scores -= scores.mean(axis=0)
        bound = efficient_score_bound(scores, interest=(0,), n_bins=bins)
        configurations = {
            "efficient": (DExchangeConfig(seed=seed, solver_restarts=1), np.asarray(bound.labels)),
            "kmeans++": (DExchangeConfig(seed=seed, solver_restarts=1), None),
            "random": (DExchangeConfig(seed=seed, solver_restarts=1, init="random"), None),
        }
        for seed_kind, (configuration, initial) in configurations.items():
            result = optimize_partition(
                scores,
                n_bins=bins,
                criterion=ProfiledDOptimality(interest=(0,)),
                config=configuration,
                initial_labels=initial,
            )
            margins = float_margins(scores, np.asarray(result.labels), bins)
            record = {
                "law": law,
                "n": size,
                "seed": seed,
                "seed_kind": seed_kind,
                "objective_log": float(result.objective),
                "upper_bound_log": float(bound.upper_bound),
                "gap_log": float(bound.upper_bound - result.objective),
                "exchange_stable": bool(result.exchange_stable),
                **margins,
            }
            runs.append(record)
            print(
                f"[library] {law} {seed_kind}: gap={record['gap_log']:.5f}, "
                f"N*I11={size * record['i11']:.3f}, lambda_min={record['lambda_min']:.5f}",
                flush=True,
            )
    return {"provenance": provenance("library", {"size": size, "bins": bins}), "runs": runs}


def json_default(value: object):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, tuple):
        return list(value)
    raise TypeError(f"cannot serialize {type(value).__name__}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "mode", choices=("fixtures", "census", "adversarial", "library", "all-exact")
    )
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.mode == "fixtures":
        report = {"fixtures": run_fixtures()}
    elif args.mode == "census":
        report = {"census": run_census()}
    elif args.mode == "adversarial":
        report = {"adversarial": run_adversarial()}
    elif args.mode == "library":
        report = {"library": run_library()}
    else:
        report = {
            "fixtures": run_fixtures(),
            "census": run_census(),
            "adversarial": run_adversarial(),
        }
    payload = json.dumps(report, indent=1, default=json_default) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload)
        print(f"wrote {args.out}", flush=True)
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
