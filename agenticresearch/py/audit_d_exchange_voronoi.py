#!/usr/bin/env python3
"""Exact-rational adversarial audit of the finite D exchange theorem.

The audit enumerates every unlabeled nonempty partition of deterministic small
weighted score tables.  All matrix algebra, determinant ratios, Voronoi
comparisons, and theorem lower bounds use ``fractions.Fraction``.  Floating
point is deliberately absent from the claim checks.
"""

from __future__ import annotations

import json
import random
from collections.abc import Iterator
from fractions import Fraction

Scalar = Fraction
Vector = tuple[Scalar, ...]
Matrix = tuple[Vector, ...]
Labels = tuple[int, ...]


def _canonical_partitions(n_rows: int, n_bins: int) -> Iterator[Labels]:
    """Yield restricted-growth encodings of all nonempty unlabeled partitions."""
    labels = [0] * n_rows

    def visit(row: int, maximum: int) -> Iterator[Labels]:
        if row == n_rows:
            if maximum == n_bins - 1:
                yield tuple(labels)
            return
        for label in range(min(maximum + 1, n_bins - 1) + 1):
            labels[row] = label
            yield from visit(row + 1, max(maximum, label))

    yield from visit(1, 0)


def _determinant(matrix: Matrix) -> Scalar:
    """Return an exact determinant by fraction-preserving elimination."""
    size = len(matrix)
    work = [list(row) for row in matrix]
    determinant = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant = -determinant
        value = work[column][column]
        determinant *= value
        for row in range(column + 1, size):
            if not work[row][column]:
                continue
            factor = work[row][column] / value
            for inner in range(column + 1, size):
                work[row][inner] -= factor * work[column][inner]
    return determinant


def _inverse(matrix: Matrix) -> Matrix | None:
    """Return an exact inverse, or ``None`` when the matrix is singular."""
    size = len(matrix)
    work = [
        list(row) + [Fraction(int(row_index == column)) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return None
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(work[row], work[column], strict=True)
            ]
    return tuple(tuple(row[size:]) for row in work)


def _quadratic(vector: Vector, matrix: Matrix, other: Vector | None = None) -> Scalar:
    """Return ``vector.T @ matrix @ other`` exactly."""
    right = vector if other is None else other
    return sum(
        vector[row] * matrix[row][column] * right[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def _subtract(first: Vector, second: Vector) -> Vector:
    return tuple(left - right for left, right in zip(first, second, strict=True))


def _center(scores: tuple[Vector, ...], weights: tuple[Scalar, ...]) -> tuple[Vector, ...]:
    total = sum(weights)
    mean = tuple(
        sum(weight * score[column] for score, weight in zip(scores, weights, strict=True)) / total
        for column in range(len(scores[0]))
    )
    return tuple(_subtract(score, mean) for score in scores)


def _statistics(
    scores: tuple[Vector, ...], weights: tuple[Scalar, ...], labels: Labels, n_bins: int
) -> tuple[tuple[Scalar, ...], tuple[Vector, ...], tuple[Vector, ...]]:
    dimension = len(scores[0])
    masses = [Fraction(0) for _ in range(n_bins)]
    moments = [[Fraction(0) for _ in range(dimension)] for _ in range(n_bins)]
    for score, weight, label in zip(scores, weights, labels, strict=True):
        masses[label] += weight
        for column in range(dimension):
            moments[label][column] += weight * score[column]
    means = [tuple(moment / masses[label] for moment in moments[label]) for label in range(n_bins)]
    return tuple(masses), tuple(tuple(moment) for moment in moments), tuple(means)


def _information(masses: tuple[Scalar, ...], moments: tuple[Vector, ...]) -> Matrix:
    dimension = len(moments[0])
    return tuple(
        tuple(
            sum(
                moment[row] * moment[column] / mass
                for mass, moment in zip(masses, moments, strict=True)
            )
            for column in range(dimension)
        )
        for row in range(dimension)
    )


def _move_ratio(
    scores: tuple[Vector, ...],
    weights: tuple[Scalar, ...],
    labels: Labels,
    n_bins: int,
    row: int,
    destination: int,
    determinant: Scalar,
) -> Scalar:
    moved = list(labels)
    moved[row] = destination
    masses, moments, _ = _statistics(scores, weights, tuple(moved), n_bins)
    return _determinant(_information(masses, moments)) / determinant


def _audit_partition(
    scores: tuple[Vector, ...],
    weights: tuple[Scalar, ...],
    labels: Labels,
    n_bins: int,
) -> tuple[int, int, bool]:
    masses, moments, means = _statistics(scores, weights, labels, n_bins)
    information = _information(masses, moments)
    determinant = _determinant(information)
    inverse = _inverse(information)
    if determinant <= 0 or inverse is None:
        return 0, 0, False

    premise_moves = 0
    admissible_moves = 0
    stable = True
    counts = tuple(labels.count(label) for label in range(n_bins))
    for row, (score, weight, source) in enumerate(zip(scores, weights, labels, strict=True)):
        source_residual = _subtract(score, means[source])
        q_source = _quadratic(source_residual, inverse)
        for destination in range(n_bins):
            if destination == source:
                continue
            destination_residual = _subtract(score, means[destination])
            q_destination = _quadratic(destination_residual, inverse)
            if counts[source] == 1:
                if means[source] != means[destination] and not q_source < q_destination:
                    raise AssertionError("a singleton is not strictly nearest to a distinct center")
                continue

            admissible_moves += 1
            ratio = _move_ratio(scores, weights, labels, n_bins, row, destination, determinant)
            stable &= ratio <= 1
            if q_source < q_destination:
                continue

            premise_moves += 1
            alpha = weight * masses[source] / (masses[source] - weight)
            beta = weight * masses[destination] / (masses[destination] + weight)
            q_cross = _quadratic(source_residual, inverse, destination_residual)
            algebraic_ratio = (1 + alpha * q_source) * (
                1 - beta * q_destination
            ) + alpha * beta * q_cross**2
            if ratio != algebraic_ratio:
                raise AssertionError("rank-two determinant ratio disagrees with recomputation")
            center_difference = _subtract(means[source], means[destination])
            separation = _quadratic(center_difference, inverse)
            lower = 1 + alpha * beta * separation**2 / 4
            if separation > 0 and (ratio < lower or lower <= 1):
                raise AssertionError(
                    "Voronoi violation failed the strict determinant bound: "
                    f"scores={scores}, weights={weights}, labels={labels}, row={row}, "
                    f"destination={destination}, q_source={q_source}, "
                    f"q_destination={q_destination}, q_cross={q_cross}, "
                    f"separation={separation}, alpha={alpha}, beta={beta}, "
                    f"ratio={ratio}, lower={lower}"
                )

    if stable:
        for row, (score, source) in enumerate(zip(scores, labels, strict=True)):
            own = _quadratic(_subtract(score, means[source]), inverse)
            for destination in range(n_bins):
                if destination == source:
                    continue
                competing = _quadratic(_subtract(score, means[destination]), inverse)
                if not own < competing:
                    raise AssertionError(
                        f"stable non-Voronoi partition at row {row}: {scores}, {weights}, {labels}"
                    )
    return admissible_moves, premise_moves, stable


def _random_instance(
    generator: random.Random, dimension: int, n_rows: int, *, near_singular: bool
) -> tuple[tuple[Vector, ...], tuple[Scalar, ...]]:
    while True:
        raw = {
            tuple(Fraction(generator.randint(-4, 4)) for _ in range(dimension))
            for _ in range(n_rows)
        }
        if len(raw) != n_rows:
            continue
        scores = tuple(sorted(raw))
        if near_singular and dimension > 1:
            scores = tuple(score[:-1] + (score[-1] / Fraction(10_000),) for score in scores)
        weights = tuple(Fraction(generator.randint(1, 7)) for _ in range(n_rows))
        return _center(scores, weights), weights


def _check_unmerged_duplicate_boundary() -> None:
    """Verify the minimal split-duplicate failure of the unqualified theorem."""
    scores = ((Fraction(1),), (Fraction(1),), (Fraction(-1),))
    weights = (Fraction(1, 4), Fraction(1, 4), Fraction(1, 2))
    labels = (0, 1, 2)
    masses, moments, means = _statistics(scores, weights, labels, 3)
    information = _information(masses, moments)
    if information != ((Fraction(1),),):
        raise AssertionError("duplicate boundary fixture lost positive-definite information")
    if any(labels.count(label) != 1 for label in range(3)):
        raise AssertionError("duplicate boundary fixture is not vacuously exchange stable")
    if means[0] != means[1]:
        raise AssertionError("duplicate boundary fixture lost its tied centroids")


def main() -> None:
    """Run the exact audit and print a stable JSON summary."""
    generator = random.Random(20260826)
    totals = {
        "datasets": 0,
        "positive_definite_partitions": 0,
        "admissible_moves": 0,
        "voronoi_premise_moves": 0,
        "exchange_stable_partitions": 0,
    }
    for dimension, n_rows, n_bins, repetitions in (
        (1, 6, 2, 24),
        (1, 7, 3, 16),
        (2, 6, 3, 24),
        (3, 6, 4, 16),
    ):
        for repetition in range(repetitions):
            scores, weights = _random_instance(
                generator,
                dimension,
                n_rows,
                near_singular=repetition % 4 == 0,
            )
            totals["datasets"] += 1
            for labels in _canonical_partitions(n_rows, n_bins):
                moves, premise, stable = _audit_partition(scores, weights, labels, n_bins)
                if not moves:
                    continue
                totals["positive_definite_partitions"] += 1
                totals["admissible_moves"] += moves
                totals["voronoi_premise_moves"] += premise
                totals["exchange_stable_partitions"] += int(stable)
    _check_unmerged_duplicate_boundary()
    totals["unmerged_duplicate_boundary_verified"] = True
    totals["result"] = "PASS"
    print(json.dumps(totals, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
