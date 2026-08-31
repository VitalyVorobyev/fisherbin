"""Exact falsification harness for the off-(L) global-basin transfer packet.

The named population law is

    X, Z iid Uniform[-1, 1],
    S_psi = X,
    S_lambda = 3 X^2 - 1 + Z.

All theorem-facing calculations and finite enumerations use
``fractions.Fraction``.  The script is evidence and regression support, never
the theorem authority; the proof lives in ``KNOWN_RESULTS/05b-ds-bridge.md``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from fractions import Fraction
from itertools import product
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[1]
WORKSPACE = RESEARCH.parent
DEFAULT_OUTPUT = (
    RESEARCH
    / "WORK"
    / "artifacts"
    / "OPEN-DS-MARGINS-NONCENTERED"
    / "exact-falsification.json"
)
N_BINS = 3


def canonical_partitions(size: int, bins: int = N_BINS) -> Iterator[tuple[int, ...]]:
    """Yield label-permutation-canonical surjective partitions."""
    for labels in product(range(bins), repeat=size):
        if labels[0] != 0 or set(labels) != set(range(bins)):
            continue
        if all(labels[index] <= max(labels[:index]) + 1 for index in range(1, size)):
            yield labels


def law_score(x_value: Fraction, z_value: Fraction) -> tuple[Fraction, Fraction]:
    """Return one exact score pair from the named law."""
    return x_value, 3 * x_value * x_value - 1 + z_value


def cells(
    scores: list[tuple[Fraction, Fraction]],
    weights: list[Fraction],
    labels: tuple[int, ...],
    bins: int = N_BINS,
) -> tuple[list[Fraction], list[tuple[Fraction, Fraction]]]:
    """Return exact cell masses and first moments."""
    masses = [Fraction(0)] * bins
    moments = [[Fraction(0), Fraction(0)] for _ in range(bins)]
    for score, weight, label in zip(scores, weights, labels, strict=True):
        masses[label] += weight
        moments[label][0] += weight * score[0]
        moments[label][1] += weight * score[1]
    return masses, [(row[0], row[1]) for row in moments]


def information(
    scores: list[tuple[Fraction, Fraction]],
    weights: list[Fraction],
    labels: tuple[int, ...],
    bins: int = N_BINS,
) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
    """Return exact binned information."""
    masses, moments = cells(scores, weights, labels, bins)
    return tuple(
        tuple(
            sum(
                moment[first] * moment[second] / mass
                for mass, moment in zip(masses, moments, strict=True)
                if mass > 0
            )
            for second in range(2)
        )
        for first in range(2)
    )  # type: ignore[return-value]


def profiled_value(
    info: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
) -> Fraction | None:
    """Return the ordinary scalar profiled value, or ``None`` when singular."""
    if info[1][1] == 0:
        return None
    return info[0][0] - info[0][1] * info[1][0] / info[1][1]


def population_labels(scores: list[tuple[Fraction, Fraction]]) -> tuple[int, ...]:
    """Label scores by the population cuts -1/3 and 1/3."""
    lower = Fraction(-1, 3)
    upper = Fraction(1, 3)
    return tuple(0 if row[0] < lower else 1 if row[0] <= upper else 2 for row in scores)


def best_scalar_between(
    scores: list[tuple[Fraction, Fraction]], weights: list[Fraction]
) -> Fraction:
    """Return the exact best three-interval between-X value."""
    ordered = sorted(zip(scores, weights, strict=True), key=lambda item: item[0][0])
    best: Fraction | None = None
    for first in range(1, len(ordered) - 1):
        for second in range(first + 1, len(ordered)):
            groups = (ordered[:first], ordered[first:second], ordered[second:])
            value = Fraction(0)
            for group in groups:
                mass = sum(weight for _, weight in group)
                moment = sum(weight * score[0] for score, weight in group)
                value += moment * moment / mass
            if best is None or value > best:
                best = value
    if best is None:
        raise ValueError("at least three observations are required")
    return best


def exchange_report(
    scores: list[tuple[Fraction, Fraction]],
    weights: list[Fraction],
    labels: tuple[int, ...],
) -> dict[str, object]:
    """Recompute every admissible one-point move exactly."""
    current = profiled_value(information(scores, weights, labels))
    if current is None:
        return {"regular": False, "admissible_moves": 0, "max_gain": None}
    gains: list[Fraction] = []
    for row, source in enumerate(labels):
        if labels.count(source) <= 1:
            continue
        for destination in range(N_BINS):
            if destination == source:
                continue
            moved = list(labels)
            moved[row] = destination
            candidate = profiled_value(information(scores, weights, tuple(moved)))
            if candidate is not None:
                gains.append(candidate - current)
    return {
        "regular": True,
        "admissible_moves": len(gains),
        "max_gain": max(gains) if gains else None,
        "exchange_stable": not gains or max(gains) <= 0,
    }


def population_exact() -> dict[str, object]:
    """Return and assert the exact population root, margins, and retention."""
    masses = [Fraction(1, 3)] * 3
    means_psi = [Fraction(-2, 3), Fraction(0), Fraction(2, 3)]
    means_lambda = [Fraction(4, 9), Fraction(-8, 9), Fraction(4, 9)]
    info = (
        (
            sum(w * value * value for w, value in zip(masses, means_psi, strict=True)),
            sum(
                w * psi * nuisance
                for w, psi, nuisance in zip(masses, means_psi, means_lambda, strict=True)
            ),
        ),
        (
            Fraction(0),
            sum(w * value * value for w, value in zip(masses, means_lambda, strict=True)),
        ),
    )
    info = ((info[0][0], info[0][1]), (info[0][1], info[1][1]))
    full = ((Fraction(1, 3), Fraction(0)), (Fraction(0), Fraction(17, 15)))
    assert info == ((Fraction(8, 27), Fraction(0)), (Fraction(0), Fraction(32, 81)))
    assert full == ((Fraction(1, 3), Fraction(0)), (Fraction(0), Fraction(17, 15)))
    assert info[0][1] == 0
    assert min(info[0][0], info[1][1]) == Fraction(8, 27)
    assert min(means_psi[1] - means_psi[0], means_psi[2] - means_psi[1]) == Fraction(2, 3)
    return {
        "law": "X,Z iid Uniform[-1,1]; S=(X, 3X^2-1+Z)",
        "cuts": [Fraction(-1, 3), Fraction(1, 3)],
        "masses": masses,
        "cell_means": list(zip(means_psi, means_lambda, strict=True)),
        "full_information": full,
        "binned_information": info,
        "beta": Fraction(0),
        "root_residual": Fraction(0),
        "lambda_min": Fraction(8, 27),
        "projected_separation": Fraction(2, 3),
        "profiled_value": Fraction(8, 27),
        "ds_retention": Fraction(8, 9),
        "declared_eventual_margins": {
            "c0": Fraction(1, 4),
            "kappa": Fraction(1, 4),
            "gamma": Fraction(1, 2),
        },
    }


def midpoint_case(size: int) -> tuple[list[tuple[Fraction, Fraction]], list[Fraction]]:
    """Return a symmetric midpoint approximation with Z=0."""
    x_values = [Fraction(-1) + Fraction(2 * index + 1, size) for index in range(size)]
    return [law_score(value, Fraction(0)) for value in x_values], [Fraction(1, size)] * size


def product_case(size: int) -> tuple[list[tuple[Fraction, Fraction]], list[Fraction]]:
    """Return an X-midpoint by Z=+-1/2 product quadrature."""
    x_count = size // 2
    x_values = [Fraction(-1) + Fraction(2 * index + 1, x_count) for index in range(x_count)]
    scores = [law_score(value, z_value) for value in x_values for z_value in (-Fraction(1, 2), Fraction(1, 2))]
    return scores, [Fraction(1, size)] * size


def exhaustive_case(
    name: str,
    scores: list[tuple[Fraction, Fraction]],
    weights: list[Fraction],
    require_population_global: bool,
) -> dict[str, object]:
    """Exhaust one finite table and attack the two exact sandwiches."""
    scalar_best = best_scalar_between(scores, weights)
    best_profiled: Fraction | None = None
    best_labels: list[tuple[int, ...]] = []
    regular = 0
    singular = 0
    count = 0
    for labels in canonical_partitions(len(scores)):
        count += 1
        info = information(scores, weights, labels)
        value = profiled_value(info)
        if value is None:
            singular += 1
            continue
        regular += 1
        assert value <= info[0][0] <= scalar_best
        if best_profiled is None or value > best_profiled:
            best_profiled = value
            best_labels = [labels]
        elif value == best_profiled:
            best_labels.append(labels)
    if best_profiled is None:
        return {
            "name": name,
            "observations": len(scores),
            "partitions": count,
            "regular_partitions": regular,
            "singular_partitions": singular,
            "all_profiled_states_singular": True,
            "scalar_upper": scalar_best,
        }
    report: dict[str, object] = {
        "name": name,
        "observations": len(scores),
        "partitions": count,
        "regular_partitions": regular,
        "singular_partitions": singular,
        "scalar_upper": scalar_best,
        "global_profiled": best_profiled,
        "global_multiplicity_canonical": len(best_labels),
        "global_exchange_reports": [exchange_report(scores, weights, labels) for labels in best_labels],
    }
    if require_population_global:
        labels = population_labels(scores)
        assert set(labels) == set(range(N_BINS))
        candidate = profiled_value(information(scores, weights, labels))
        assert candidate == best_profiled
        assert best_labels == [labels]
        report["population_labels"] = labels
        report["population_labels_exchange"] = exchange_report(scores, weights, labels)
    return report


def adversarial_cases() -> list[tuple[str, list[tuple[Fraction, Fraction]], list[Fraction]]]:
    """Return exact edge cases required by the numerical protocol."""
    unequal_x = [Fraction(-3, 4), Fraction(-1, 4), Fraction(1, 4), Fraction(3, 4)]
    unequal_z = [Fraction(-1), Fraction(-3, 4), Fraction(1), Fraction(1)]
    unequal_weights_raw = [Fraction(1), Fraction(2), Fraction(3), Fraction(4)]
    unequal_weights = [value / sum(unequal_weights_raw) for value in unequal_weights_raw]

    duplicate_x = [Fraction(-2, 3), Fraction(-2, 3), Fraction(0), Fraction(0), Fraction(2, 3), Fraction(2, 3)]
    duplicate_z = [Fraction(-1, 2), Fraction(-1, 2), Fraction(0), Fraction(0), Fraction(1, 2), Fraction(1, 2)]

    tie_x = [Fraction(-1), Fraction(-1, 3), Fraction(-1, 3), Fraction(0), Fraction(1, 3), Fraction(1, 3), Fraction(1)]
    tie_z = [Fraction(0)] * len(tie_x)

    tiny_x = [Fraction(-4, 5), Fraction(-2, 5), Fraction(0), Fraction(2, 5), Fraction(4, 5)]
    tiny_z = [Fraction(-1, 2), Fraction(1, 2), Fraction(0), Fraction(-1, 2), Fraction(1, 2)]
    tiny_raw = [Fraction(1, 100), Fraction(1), Fraction(1), Fraction(1), Fraction(1)]
    tiny_weights = [value / sum(tiny_raw) for value in tiny_raw]

    singular_x = [Fraction(-3, 4), Fraction(-1, 4), Fraction(1, 4), Fraction(3, 4)]
    singular_z = [1 - 3 * value * value for value in singular_x]

    return [
        (
            "unequal_weights",
            [law_score(x_value, z_value) for x_value, z_value in zip(unequal_x, unequal_z, strict=True)],
            unequal_weights,
        ),
        (
            "duplicate_scores",
            [law_score(x_value, z_value) for x_value, z_value in zip(duplicate_x, duplicate_z, strict=True)],
            [Fraction(1, len(duplicate_x))] * len(duplicate_x),
        ),
        (
            "exact_boundary_ties",
            [law_score(x_value, z_value) for x_value, z_value in zip(tie_x, tie_z, strict=True)],
            [Fraction(1, len(tie_x))] * len(tie_x),
        ),
        (
            "tiny_positive_weight",
            [law_score(x_value, z_value) for x_value, z_value in zip(tiny_x, tiny_z, strict=True)],
            tiny_weights,
        ),
        (
            "singular_nuisance",
            [law_score(x_value, z_value) for x_value, z_value in zip(singular_x, singular_z, strict=True)],
            [Fraction(1, len(singular_x))] * len(singular_x),
        ),
    ]


def boundary_counterexample() -> dict[str, object]:
    """Return the minimized finite boundary-noise witness."""
    x_values = [Fraction(-3, 4), Fraction(-1, 4), Fraction(1, 4), Fraction(3, 4)]
    z_values = [Fraction(-1), Fraction(-3, 4), Fraction(1), Fraction(1)]
    scores = [law_score(x_value, z_value) for x_value, z_value in zip(x_values, z_values, strict=True)]
    weights = [Fraction(1, 4)] * 4
    before = (0, 1, 1, 2)
    after = (0, 1, 2, 2)
    before_value = profiled_value(information(scores, weights, before))
    after_value = profiled_value(information(scores, weights, after))
    assert before_value == Fraction(363, 2656)
    assert after_value == Fraction(49, 352)
    assert after_value - before_value == Fraction(37, 14608)
    assert population_labels(scores) == before
    return {
        "scores": scores,
        "weights": weights,
        "labels_before": before,
        "labels_after": after,
        "information_before": information(scores, weights, before),
        "information_after": information(scores, weights, after),
        "objective_before": before_value,
        "objective_after": after_value,
        "exact_gain": after_value - before_value,
        "population_labels_exchange": exchange_report(scores, weights, before),
        "after_exchange": exchange_report(scores, weights, after),
    }


def sha256(path: Path) -> str:
    """Hash one file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_output(*arguments: str) -> str:
    """Run one read-only Git query."""
    return subprocess.run(
        ["git", *arguments],
        cwd=WORKSPACE,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


def json_default(value: object) -> str:
    """Serialize exact rationals without converting them to floats."""
    if isinstance(value, Fraction):
        return str(value)
    raise TypeError(f"unserializable value: {type(value)}")


def run() -> dict[str, object]:
    """Run every exact falsification stage and return a provenance envelope."""
    started = time.monotonic()
    midpoint = []
    for size in range(3, 11):
        scores, weights = midpoint_case(size)
        midpoint.append(exhaustive_case(f"midpoint_n{size}", scores, weights, True))
    product_reports = []
    for size in (6, 8, 10):
        scores, weights = product_case(size)
        product_reports.append(exhaustive_case(f"product_n{size}", scores, weights, True))
    adversarial = [
        exhaustive_case(name, scores, weights, False)
        for name, scores, weights in adversarial_cases()
    ]
    script = Path(__file__).resolve()
    return {
        "schema_version": 1,
        "artifact_id": "N-DS-NONCENTERED-EXACT-FALSIFICATION",
        "created_utc": datetime.now(UTC).isoformat(),
        "git_revision_before_commit": git_output("rev-parse", "HEAD"),
        "git_status_short": git_output("status", "--short"),
        "script_sha256": sha256(script),
        "uv_lock_sha256": sha256(WORKSPACE / "uv.lock"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "runtime_seconds": time.monotonic() - started,
        "population_exact": population_exact(),
        "boundary_counterexample": boundary_counterexample(),
        "midpoint_exhaustive": midpoint,
        "product_exhaustive": product_reports,
        "adversarial_exhaustive": adversarial,
        "summary": {
            "midpoint_partitions": sum(int(row["partitions"]) for row in midpoint),
            "product_partitions": sum(int(row["partitions"]) for row in product_reports),
            "adversarial_partitions": sum(int(row["partitions"]) for row in adversarial),
            "sandwich_violations": 0,
            "valid_counterexamples_to_global_transfer": 0,
            "boundary_counterexamples": 1,
        },
        "result": "PASS",
    }


def main() -> None:
    """Run the harness and write its JSON artifact."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    result = run()
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    arguments.out.write_text(json.dumps(result, indent=2, default=json_default) + "\n")
    print(
        "[exact] "
        f"midpoint={result['summary']['midpoint_partitions']} "
        f"product={result['summary']['product_partitions']} "
        f"adversarial={result['summary']['adversarial_partitions']} "
        f"wrote={arguments.out}",
        flush=True,
    )


if __name__ == "__main__":
    main()
