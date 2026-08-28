from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path

import numpy as np
import pytest

import scorequant as sq

from ._oracles import _exhaustive_d_oracle

# The research workspace holding the counterexample bank; if it moves, update
# this constant and tests/test_research_registry.py together.
RESEARCH_WORKSPACE = Path(__file__).parents[1] / "agenticresearch"


def _canonical_partitions(n_rows: int, n_bins: int) -> list[tuple[int, ...]]:
    return [
        labels
        for labels in product(range(n_bins), repeat=n_rows)
        if labels[0] == 0
        and set(labels) == set(range(n_bins))
        and all(labels[index] <= max(labels[:index]) + 1 for index in range(1, n_rows))
    ]


def _information(scores: np.ndarray, labels: tuple[int, ...], n_bins: int) -> np.ndarray:
    return np.asarray(sq.binned_fisher_information(scores, labels, n_bins=n_bins))


def test_small_d_exchange_matches_exhaustive_global_oracle() -> None:
    scores = np.array(
        [[-2.0, -1.0], [-1.0, 1.0], [-0.2, -0.4], [0.3, 0.8], [1.1, -0.8], [1.8, 0.7]]
    )
    scores -= scores.mean(axis=0)
    _, optimum = _exhaustive_d_oracle(scores, None, 3)
    result = sq.optimize_partition(
        scores,
        n_bins=3,
        config=sq.DExchangeConfig(seed=8, n_init=12, max_scans=200),
    )
    assert result.objective == pytest.approx(optimum, abs=1e-10)


def test_d_cell_separation_bound_and_training_geometry() -> None:
    rng = np.random.default_rng(91)
    scores = rng.normal(size=(48, 2))
    scores -= scores.mean(axis=0)
    result = sq.optimize_partition(scores, n_bins=3)
    means = np.asarray(result.transformed_centers)
    metric = np.asarray(result.metric)
    masses = np.asarray(result.cell_weights)
    for first in range(result.n_bins):
        for second in range(first):
            difference = means[first] - means[second]
            separation = difference @ metric @ difference
            assert separation <= 1 / masses[first] + 1 / masses[second] + 1e-8
    assert np.array_equal(
        np.asarray(result.compile_quantizer().predict_scores(scores)),
        np.asarray(result.labels),
    )


def test_d_voronoi_violation_has_positive_gain_lower_bound() -> None:
    rng = np.random.default_rng(2026)
    scores = rng.normal(size=(24, 2))
    weights = rng.uniform(0.2, 2.0, size=len(scores))
    weights /= weights.sum()
    labels = np.tile(np.arange(3), 8)
    masses = np.bincount(labels, weights=weights, minlength=3)
    means = np.asarray(
        [
            np.average(scores[labels == label], axis=0, weights=weights[labels == label])
            for label in range(3)
        ]
    )
    information = np.asarray(sq.binned_fisher_information(scores, labels, weights, n_bins=3))
    metric = np.linalg.inv(information)
    checked = 0
    for row, source in enumerate(labels):
        if masses[source] <= weights[row]:
            continue
        source_residual = scores[row] - means[source]
        q_source = source_residual @ metric @ source_residual
        alpha = weights[row] * masses[source] / (masses[source] - weights[row])
        for destination in range(3):
            if destination == source:
                continue
            destination_residual = scores[row] - means[destination]
            q_destination = destination_residual @ metric @ destination_residual
            if q_source < q_destination:
                continue
            beta = weights[row] * masses[destination] / (masses[destination] + weights[row])
            q_cross = source_residual @ metric @ destination_residual
            determinant_increment = (
                alpha * q_source
                - beta * q_destination
                - alpha * beta * (q_source * q_destination - q_cross**2)
            )
            center_difference = means[destination] - means[source]
            separation = center_difference @ metric @ center_difference
            lower_bound = alpha * beta * separation**2 / 4
            assert determinant_increment >= lower_bound - 1e-10
            checked += 1
    assert checked > 0


def test_unmerged_duplicate_atoms_are_an_exact_boundary_failure() -> None:
    """Split duplicates can be vacuously stable without strict score geometry."""
    fixture_path = RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-D-UNMERGED-DUPLICATES-001.json"
    assert fixture_path.is_file(), (
        f"counterexample fixture missing at {fixture_path}; the research "
        "workspace may have moved — update RESEARCH_WORKSPACE"
    )
    fixture = json.loads(fixture_path.read_text())
    scores = tuple(Fraction(row[0]) for row in fixture["scores"])
    weights = tuple(Fraction(value) for value in fixture["weights"])
    labels = tuple(fixture["labels_before"])

    assert sum(weight * score for score, weight in zip(scores, weights, strict=True)) == 0
    assert sum(weight * score**2 for score, weight in zip(scores, weights, strict=True)) == 1
    assert all(labels.count(label) == 1 for label in range(fixture["K"]))
    assert scores[0] == scores[1]
    centroids = {
        label: sum(
            weight * score
            for score, weight, row_label in zip(scores, weights, labels, strict=True)
            if row_label == label
        )
        / sum(
            weight for weight, row_label in zip(weights, labels, strict=True) if row_label == label
        )
        for label in range(fixture["K"])
    }
    # the two coincident atoms sit exactly on both of their singleton centroids,
    # so no deterministic score-only rule can separate their labels
    assert (scores[0] - centroids[labels[0]]) ** 2 == 0
    assert (scores[0] - centroids[labels[1]]) ** 2 == 0


def test_adaptive_mahalanobis_lloyd_step_can_decrease_d_objective() -> None:
    scores = np.array(
        [
            [0.1116, 0.4427],
            [-0.2932, 0.6537],
            [-0.5995, -1.2685],
            [-0.6848, -1.5456],
            [0.4810, 0.9521],
            [1.6707, 0.9370],
            [0.1689, 1.7090],
            [-0.8548, -1.8805],
        ]
    )
    labels = np.array([1, 0, 0, 1, 2, 2, 2, 1])
    weights = np.full(len(scores), 1 / len(scores))
    information = np.asarray(sq.binned_fisher_information(scores, labels, weights, n_bins=3))
    means = np.asarray([scores[labels == label].mean(axis=0) for label in range(3)])
    residuals = scores[:, None, :] - means[None, :, :]
    distances = np.einsum("nkp,pq,nkq->nk", residuals, np.linalg.inv(information), residuals)
    updated_labels = np.argmin(distances, axis=1)
    updated = np.asarray(sq.binned_fisher_information(scores, updated_labels, weights, n_bins=3))
    decrease = np.linalg.slogdet(information)[1] - np.linalg.slogdet(updated)[1]
    assert np.array_equal(updated_labels, [0, 0, 1, 1, 2, 1, 0, 1])
    assert decrease == pytest.approx(0.136521, abs=2e-6)


def test_global_profiled_ds_partition_can_violate_its_own_metric_rule() -> None:
    raw = [(4, -4), (-5, 2), (-1, 0), (-5, -1), (2, -2), (4, 3), (2, 4), (2, -4)]
    n_rows, n_bins = 8, 3
    weight = Fraction(1, n_rows)
    mean = [Fraction(sum(row[column] for row in raw), n_rows) for column in range(2)]
    scores = [[Fraction(row[column]) - mean[column] for column in range(2)] for row in raw]

    def statistics(labels: tuple[int, ...]) -> tuple[list[Fraction], list[list[Fraction]]]:
        masses = [Fraction(0)] * n_bins
        moments = [[Fraction(0), Fraction(0)] for _ in range(n_bins)]
        for row, label in enumerate(labels):
            masses[label] += weight
            for column in range(2):
                moments[label][column] += weight * scores[row][column]
        return masses, moments

    def information(labels: tuple[int, ...]) -> list[list[Fraction]]:
        masses, moments = statistics(labels)
        return [
            [
                sum(
                    moments[label][row] * moments[label][column] / masses[label]
                    for label in range(n_bins)
                )
                for column in range(2)
            ]
            for row in range(2)
        ]

    def objective(labels: tuple[int, ...]) -> Fraction:
        matrix = information(labels)
        return matrix[0][0] - matrix[0][1] * matrix[1][0] / matrix[1][1]

    ranked = sorted(
        ((objective(labels), labels) for labels in _canonical_partitions(n_rows, n_bins)),
        reverse=True,
    )
    best, labels = ranked[0]
    matrix = information(labels)
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    inverse = [
        [matrix[1][1] / determinant, -matrix[0][1] / determinant],
        [-matrix[1][0] / determinant, matrix[0][0] / determinant],
    ]
    metric = [
        [inverse[0][0], inverse[0][1]],
        [inverse[1][0], inverse[1][1] - 1 / matrix[1][1]],
    ]
    masses, moments = statistics(labels)
    means = [
        [moments[label][column] / masses[label] for column in range(2)] for label in range(n_bins)
    ]

    def distance(row: int, label: int) -> Fraction:
        residual = [scores[row][column] - means[label][column] for column in range(2)]
        return sum(
            residual[first] * metric[first][second] * residual[second]
            for first in range(2)
            for second in range(2)
        )

    row = 6
    distances = [distance(row, label) for label in range(n_bins)]
    nearest = min(range(n_bins), key=distances.__getitem__)
    assert labels == (0, 1, 2, 1, 2, 0, 0, 2)
    assert best == Fraction(20449, 1920)
    assert best - ranked[1][0] == Fraction(2929, 21120)
    assert nearest == 2
    assert distances[labels[row]] - distances[nearest] == Fraction(8, 195)


def test_global_e_partition_can_violate_simple_eigenvector_rule() -> None:
    scores = np.array(
        [
            [-0.226534, 0.428773],
            [-0.629944, -1.223406],
            [1.253439, -0.109445],
            [1.807897, 0.734952],
            [-1.520937, -0.061786],
            [-0.488606, -0.002247],
            [0.710355, 1.154412],
            [-0.905669, -0.921253],
        ]
    )
    scores -= scores.mean(axis=0)
    ranked = sorted(
        (
            (np.linalg.eigvalsh(_information(scores, labels, 3))[0], labels)
            for labels in _canonical_partitions(8, 3)
        ),
        reverse=True,
    )
    _, labels = ranked[0]
    matrix = _information(scores, labels, 3)
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    direction = eigenvectors[:, 0]
    label_array = np.asarray(labels)
    means = np.asarray([scores[label_array == label].mean(axis=0) for label in range(3)])
    row = 7
    distances = np.square((scores[row] - means) @ direction)
    assert labels == (0, 1, 1, 2, 0, 0, 0, 1)
    assert eigenvalues[1] - eigenvalues[0] > 1e-4
    assert int(np.argmin(distances)) == 2
    assert distances[labels[row]] - distances.min() > 0.06
