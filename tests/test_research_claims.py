from __future__ import annotations

import json
from fractions import Fraction
from itertools import product
from pathlib import Path

import numpy as np
import pytest

import scorequant as sq
from scorequant import api
from scorequant.information import binned_information_is_degenerate

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
        config=sq.DExchangeConfig(seed=8, initializer_restarts=12, max_scans=200),
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


def _exact_ds_cells(
    scores: list[list[Fraction]], labels: tuple[int, ...], n_bins: int
) -> tuple[list[Fraction], list[list[Fraction]]]:
    weight = Fraction(1, len(scores))
    masses = [Fraction(0)] * n_bins
    moments = [[Fraction(0), Fraction(0)] for _ in range(n_bins)]
    for row, label in enumerate(labels):
        masses[label] += weight
        for column in range(2):
            moments[label][column] += weight * scores[row][column]
    return masses, moments


def _exact_binned_information(
    scores: list[list[Fraction]], labels: tuple[int, ...], n_bins: int
) -> list[list[Fraction]]:
    masses, moments = _exact_ds_cells(scores, labels, n_bins)
    return [
        [
            sum(
                moments[label][row] * moments[label][column] / masses[label]
                for label in range(n_bins)
                if masses[label] > 0
            )
            for column in range(2)
        ]
        for row in range(2)
    ]


def test_global_profiled_ds_optimum_can_be_a_degenerate_tie_class() -> None:
    path = RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-DS-DEGENERATE-GLOBAL-TIE-001.json"
    fixture = json.loads(path.read_text())
    scores = [[Fraction(value) for value in row] for row in fixture["scores"]]
    n_rows, n_bins = 8, 3

    def profiled(labels: tuple[int, ...]) -> Fraction | None:
        info = _exact_binned_information(scores, labels, n_bins)
        if info[1][1] == 0:
            return None
        return info[0][0] - info[0][1] * info[1][0] / info[1][1]

    ranked: list[tuple[Fraction, tuple[int, ...]]] = []
    infeasible: list[tuple[int, ...]] = []
    for labels in _canonical_partitions(n_rows, n_bins):
        value = profiled(labels)
        if value is None:
            infeasible.append(labels)
        else:
            ranked.append((value, labels))
    ranked.sort(reverse=True)
    best = ranked[0][0]
    ties = [labels for value, labels in ranked if value == best]
    next_distinct = next(value for value, _ in ranked if value < best)

    assert len(ranked) == 964
    assert best == Fraction(1083, 4096)
    assert len(ties) == 31
    assert best - next_distinct == Fraction(237, 16640)

    # Every tied optimum refines the reduced bipartition {0,1,2,4,6,7} | {3,5}
    # and has two cells with exactly coincident projected centroids.
    group = {0, 1, 2, 4, 6, 7}
    for labels in ties:
        cells = [{row for row in range(n_rows) if labels[row] == label} for label in range(n_bins)]
        assert all(cell <= group or cell <= (set(range(n_rows)) - group) for cell in cells)
        info = _exact_binned_information(scores, labels, n_bins)
        slope = info[0][1] / info[1][1]
        masses, moments = _exact_ds_cells(scores, labels, n_bins)
        projected = sorted(
            moments[label][0] / masses[label] - slope * moments[label][1] / masses[label]
            for label in range(n_bins)
        )
        assert projected in (
            [Fraction(-19, 64), Fraction(-19, 64), Fraction(57, 64)],
            [Fraction(-19, 64), Fraction(57, 64), Fraction(57, 64)],
        )

    # The unique infeasible refinement has an exactly singular nuisance block and
    # a generalized pseudo-inverse value strictly above the feasible optimum.
    assert len(infeasible) == 2
    singular = (0, 0, 1, 2, 1, 2, 0, 1)
    assert singular in infeasible
    info = _exact_binned_information(scores, singular, n_bins)
    assert info[1][1] == 0
    assert info[0][1] == 0
    assert info[0][0] == Fraction(1191, 4096)
    assert info[0][0] > best


def test_symmetric_wasted_cells_defeat_the_efficient_semimetric_rule() -> None:
    fixture = json.loads(
        (RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-DS-POP-WASTED-CELLS-001.json").read_text()
    )
    scores = [[Fraction(value) for value in row] for row in fixture["scores"]]
    labels = tuple(fixture["labels_after_or_optimum"])
    coarse = tuple(0 if scores[row][0] < 0 else 1 for row in range(8))

    fine_info = _exact_binned_information(scores, labels, 4)
    coarse_info = _exact_binned_information(scores, coarse, 2)
    assert coarse_info[1][1] == 0
    assert coarse_info[0][0] == Fraction(4)
    assert fine_info[1][1] == Fraction(9, 4)
    assert fine_info[0][1] == 0
    profiled = fine_info[0][0] - fine_info[0][1] * fine_info[1][0] / fine_info[1][1]
    assert profiled == Fraction(4)

    masses, moments = _exact_ds_cells(scores, labels, 4)
    determinant = fine_info[0][0] * fine_info[1][1] - fine_info[0][1] * fine_info[1][0]
    inverse = [
        [fine_info[1][1] / determinant, -fine_info[0][1] / determinant],
        [-fine_info[1][0] / determinant, fine_info[0][0] / determinant],
    ]
    metric = [row[:] for row in inverse]
    metric[1][1] -= 1 / fine_info[1][1]
    means = [[moments[label][column] / masses[label] for column in range(2)] for label in range(4)]
    slope = fine_info[0][1] / fine_info[1][1]
    projected = [means[label][0] - slope * means[label][1] for label in range(4)]
    assert sorted(projected) == [Fraction(-2), Fraction(-2), Fraction(2), Fraction(2)]

    def distance(row: int, label: int) -> Fraction:
        residual = [scores[row][column] - means[label][column] for column in range(2)]
        return sum(
            residual[first] * metric[first][second] * residual[second]
            for first in range(2)
            for second in range(2)
        )

    for row, label in enumerate(labels):
        distances = [distance(row, other) for other in range(4)]
        assert distances[label] == min(distances)


def test_ds13_leverage_bound_at_every_stable_state_with_vector_nuisance() -> None:
    """DS13 audit pin: the leverage bound holds at every exchange-stable state.

    Exhaustive exact verification in a configuration class the original
    packet evidence never exercised: d=3 with a two-dimensional nuisance
    block. All canonical surjective labelings are enumerated, one-point
    exchange stability is decided by exact determinant-ratio comparison, and
    the DS13 bound s_aa - s_bb <= beta * q_aa * q_bb is asserted for every
    admissible move at every stable state, including moves whose destination
    nuisance block is exactly singular.
    """
    scores = [
        [Fraction(2), Fraction(1), Fraction(0)],
        [Fraction(-1), Fraction(1), Fraction(1)],
        [Fraction(0), Fraction(-2), Fraction(1)],
        [Fraction(1), Fraction(0), Fraction(-1)],
        [Fraction(-2), Fraction(-1), Fraction(0)],
        [Fraction(1), Fraction(2), Fraction(2)],
        [Fraction(-1), Fraction(-1), Fraction(-2)],
    ]
    weight = Fraction(1, 7)
    n_bins = 3
    nuisance = (1, 2)

    def determinant(matrix: list[list[Fraction]]) -> Fraction:
        size = len(matrix)
        if size == 1:
            return matrix[0][0]
        if size == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        total = Fraction(0)
        for column in range(size):
            minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
            total += (-1 if column % 2 else 1) * matrix[0][column] * determinant(minor)
        return total

    def inverse(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
        size = len(matrix)
        full = determinant(matrix)
        cofactors = [
            [
                (-1 if (i + j) % 2 else 1)
                * determinant([row[:j] + row[j + 1 :] for k, row in enumerate(matrix) if k != i])
                for j in range(size)
            ]
            for i in range(size)
        ]
        return [[cofactors[j][i] / full for j in range(size)] for i in range(size)]

    def binned(labels: tuple[int, ...]) -> tuple[list[Fraction], list[list[Fraction]]]:
        masses = [Fraction(0)] * n_bins
        moments = [[Fraction(0)] * 3 for _ in range(n_bins)]
        for row, label in enumerate(labels):
            masses[label] += weight
            for column in range(3):
                moments[label][column] += weight * scores[row][column]
        info = [[Fraction(0)] * 3 for _ in range(3)]
        for mass, moment in zip(masses, moments, strict=True):
            if mass == 0:
                continue
            for i in range(3):
                for j in range(3):
                    info[i][j] += moment[i] * moment[j] / mass
        return masses, info

    def dets(labels: tuple[int, ...]) -> tuple[Fraction, Fraction]:
        _, info = binned(labels)
        lam = [[info[i][j] for j in nuisance] for i in nuisance]
        return determinant(info), determinant(lam)

    def quadratic(u: list[Fraction], g: list[list[Fraction]]) -> Fraction:
        return sum(u[i] * g[i][j] * u[j] for i in range(3) for j in range(3))

    feasible = stable = checked = degenerate_destinations = 0
    max_ratio = Fraction(0)
    for labels in _canonical_partitions(7, n_bins):
        masses, info = binned(labels)
        lam = [[info[i][j] for j in nuisance] for i in nuisance]
        det_info, det_lam = determinant(info), determinant(lam)
        if det_info <= 0 or det_lam <= 0:
            continue
        feasible += 1
        counts = [labels.count(label) for label in range(n_bins)]
        improvable = False
        for row, source in enumerate(labels):
            if counts[source] <= 1:
                continue
            for destination in range(n_bins):
                if destination == source:
                    continue
                moved = labels[:row] + (destination,) + labels[row + 1 :]
                moved_info, moved_lam = dets(moved)
                if moved_info > 0 and moved_lam > 0 and moved_info * det_lam > det_info * moved_lam:
                    improvable = True
                    break
            if improvable:
                break
        if improvable:
            continue
        stable += 1
        full_inverse = inverse(info)
        lam_inverse = inverse(lam)
        metric = [row[:] for row in full_inverse]
        for a, i in enumerate(nuisance):
            for b, j in enumerate(nuisance):
                metric[i][j] -= lam_inverse[a][b]
        cell_moments = [[Fraction(0)] * 3 for _ in range(n_bins)]
        for row, label in enumerate(labels):
            for column in range(3):
                cell_moments[label][column] += weight * scores[row][column]
        means = [
            [cell_moments[label][column] / masses[label] for column in range(3)]
            for label in range(n_bins)
        ]
        for row, source in enumerate(labels):
            if counts[source] <= 1:
                continue
            residual_source = [scores[row][c] - means[source][c] for c in range(3)]
            violation_own = quadratic(residual_source, metric)
            leverage_own = quadratic(residual_source, full_inverse)
            for destination in range(n_bins):
                if destination == source:
                    continue
                residual_dest = [scores[row][c] - means[destination][c] for c in range(3)]
                gap = violation_own - quadratic(residual_dest, metric)
                beta = weight * masses[destination] / (masses[destination] + weight)
                bound = beta * leverage_own * quadratic(residual_dest, full_inverse)
                assert gap <= bound
                checked += 1
                if gap > 0 and bound > 0:
                    max_ratio = max(max_ratio, gap / bound)
                moved = labels[:row] + (destination,) + labels[row + 1 :]
                if dets(moved)[1] == 0:
                    degenerate_destinations += 1
    assert (feasible, stable, checked) == (258, 17, 212)
    assert degenerate_destinations == 14
    assert max_ratio == Fraction(4, 15)


def test_ds15_profiled_value_is_bounded_by_the_efficient_score_interval_optimum() -> None:
    """DS15's finite half: exact projection-tax identity and sandwich.

    For every feasible labeling z of an exactly centered sample, with the
    efficient scores shat built from the full-sample empirical regression,

        profiled(z) = between(shat; z) - cross(z)^2 / I_ll(z)
                    <= between(shat; z) <= scalar interval optimum of shat,

    all in exact rationals, and the scalar optimum over arbitrary groupings is
    attained by interval groupings (1-D contiguity). The global profiled
    optimum sits strictly below the interval optimum on this sample.
    """
    fixture = json.loads(
        (RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-DS-GLOBAL-GEOMETRY-001.json").read_text()
    )
    scores = [[Fraction(value) for value in row] for row in fixture["scores"]]
    n_rows, n_bins = len(scores), 3
    weight = Fraction(1, n_rows)
    full = [[sum(weight * row[a] * row[b] for row in scores) for b in range(2)] for a in range(2)]
    slope = full[0][1] / full[1][1]
    shat = [row[0] - slope * row[1] for row in scores]
    assert sum(weight * shat[row] * scores[row][1] for row in range(n_rows)) == 0

    def between(labels: tuple[int, ...]) -> Fraction:
        masses = [Fraction(0)] * n_bins
        sums = [Fraction(0)] * n_bins
        for row, label in enumerate(labels):
            masses[label] += weight
            sums[label] += weight * shat[row]
        return sum(sums[b] ** 2 / masses[b] for b in range(n_bins) if masses[b] > 0)

    order = sorted(range(n_rows), key=shat.__getitem__)
    interval_best = Fraction(0)
    for first_cut in range(1, n_rows - 1):
        for second_cut in range(first_cut + 1, n_rows):
            labels = [0] * n_rows
            for position, row in enumerate(order):
                labels[row] = 0 if position < first_cut else (1 if position < second_cut else 2)
            interval_best = max(interval_best, between(tuple(labels)))

    n_feasible = 0
    best_profiled = Fraction(0)
    grouping_best = Fraction(0)
    for labels in _canonical_partitions(n_rows, n_bins):
        masses, moments = _exact_ds_cells(scores, labels, n_bins)
        info = _exact_binned_information(scores, labels, n_bins)
        cell_between = between(labels)
        grouping_best = max(grouping_best, cell_between)
        assert cell_between <= interval_best
        if info[1][1] == 0:
            continue
        n_feasible += 1
        profiled = info[0][0] - info[0][1] * info[1][0] / info[1][1]
        cross = sum(
            (moments[b][0] - slope * moments[b][1]) * moments[b][1] / masses[b]
            for b in range(n_bins)
        )
        assert profiled == cell_between - cross**2 / info[1][1]
        assert profiled <= cell_between
        best_profiled = max(best_profiled, profiled)

    assert n_feasible == 966
    assert grouping_best == interval_best
    assert best_profiled == Fraction(6241, 984)
    assert interval_best == Fraction(135987641, 19993584)
    assert best_profiled < interval_best


def test_ds15_rank_deficiency_zeroes_every_feasible_profiled_value() -> None:
    """DS15's K = d_lambda + 1 rank boundary (CE-DS-MARGINS-RANK-VACUITY-001).

    Exact centering forces rank(I_z) <= K - 1, so with a scalar POI and a
    d_lambda = K - 1 nuisance every labeling with a nonsingular binned
    nuisance block has profiled Schur value exactly 0 - on every sample -
    while the efficient-score interval optimum stays strictly positive and
    K = d_lambda + 2 restores a positive value on the same atoms. Conclusion
    (i) of DS15 therefore needs K >= d_lambda + 2, not K >= 3.
    """
    fixture = json.loads(
        (RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-DS-MARGINS-RANK-VACUITY-001.json").read_text()
    )
    scores = [[Fraction(value) for value in row] for row in fixture["scores"]]
    n_rows = len(scores)
    weight = Fraction(1, n_rows)
    assert all(sum(row[column] for row in scores) == 0 for column in range(3))

    def blocks(labels: tuple[int, ...], n_bins: int) -> list[list[Fraction]]:
        masses = [Fraction(0)] * n_bins
        moments = [[Fraction(0)] * 3 for _ in range(n_bins)]
        for row, label in enumerate(labels):
            masses[label] += weight
            for column in range(3):
                moments[label][column] += weight * scores[row][column]
        return [
            [
                sum(
                    moments[b][row] * moments[b][column] / masses[b]
                    for b in range(n_bins)
                    if masses[b] > 0
                )
                for column in range(3)
            ]
            for row in range(3)
        ]

    def schur(info: list[list[Fraction]]) -> Fraction | None:
        det_l = info[1][1] * info[2][2] - info[1][2] * info[2][1]
        if det_l == 0:
            return None
        adj = info[0][1] * (info[2][2] * info[0][1] - info[1][2] * info[0][2]) + info[0][2] * (
            info[1][1] * info[0][2] - info[1][2] * info[0][1]
        )
        return info[0][0] - adj / det_l

    n_feasible = 0
    for labels in _canonical_partitions(n_rows, 3):
        value = schur(blocks(labels, 3))
        if value is not None:
            n_feasible += 1
            assert value == 0
    assert n_feasible == 6

    full = blocks((0, 1, 2, 3), 4)
    det_l = full[1][1] * full[2][2] - full[1][2] * full[2][1]
    slope_1 = (full[0][1] * full[2][2] - full[0][2] * full[1][2]) / det_l
    slope_2 = (full[0][2] * full[1][1] - full[0][1] * full[2][1]) / det_l
    shat = [row[0] - slope_1 * row[1] - slope_2 * row[2] for row in scores]
    order = sorted(range(n_rows), key=shat.__getitem__)
    interval_best = Fraction(0)
    for first_cut in range(1, n_rows - 1):
        for second_cut in range(first_cut + 1, n_rows):
            masses = [Fraction(0)] * 3
            sums = [Fraction(0)] * 3
            for position, row in enumerate(order):
                cell = 0 if position < first_cut else (1 if position < second_cut else 2)
                masses[cell] += weight
                sums[cell] += weight * shat[row]
            interval_best = max(
                interval_best, sum(sums[b] ** 2 / masses[b] for b in range(3) if masses[b] > 0)
            )
    assert interval_best == Fraction(81, 50)
    assert schur(full) == Fraction(9, 5)


def test_ds15_rank_vacuity_diagnosis_does_not_depend_on_the_labeling() -> None:
    """Every onto labeling is degenerate by a wide margin, so the message is stable.

    Two guards can refuse this configuration: the whole-matrix rank test, which
    names the bin budget, and the nuisance-block test, which names the
    parameterization. Only the first is the true cause. The library orders the
    rank test first, but that ordering is only worth something if the rank test
    fires for *every* labeling a solver might land on - otherwise the surviving
    message would be decided by whichever state the platform's linear algebra
    happened to produce, which is exactly how this was first observed to differ
    between macOS and Linux CI.

    The theorem supplies that guarantee: at K = d_lambda + 1 on a centered
    sample the binned information is rank deficient for every feasible labeling.
    This checks the numerical version of it, with the margin, so a future change
    to the rank tolerance cannot silently reopen the platform split.
    """
    fixture = json.loads(
        (RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-DS-MARGINS-RANK-VACUITY-001.json").read_text()
    )
    scores = np.array([[float(Fraction(v)) for v in row] for row in fixture["scores"]])
    weights = np.array([float(Fraction(w)) for w in fixture["weights"]])
    n_bins = int(fixture["K"])

    worst_ratio = 0.0
    labelings = 0
    for labels in product(range(n_bins), repeat=scores.shape[0]):
        if len(set(labels)) != n_bins:
            continue
        labelings += 1
        binned = sq.information_report(
            scores, np.array(labels), weights=weights, n_bins=n_bins
        ).fisher_binned
        assert binned_information_is_degenerate(binned)
        eigenvalues = np.linalg.eigvalsh(np.asarray(binned))
        worst_ratio = max(worst_ratio, float(eigenvalues.min() / eigenvalues.max()))

    assert labelings > 0
    # Six orders of magnitude below the float64 threshold of 1e-10. The smallest
    # eigenvalue is rounding noise, which is why the sign of a log determinant -
    # the test this replaced - was not reproducible across platforms.
    assert worst_ratio < 1e-14


def _refuse_to_report(*args: object, **kwargs: object) -> object:
    """Stand in for the profiled report so that reaching it is a test failure."""
    raise AssertionError("a degenerate profiled budget must be refused before anything is reported")


def test_ds15_rank_vacuity_is_refused_by_both_public_tasks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The library refuses the vacuous configuration instead of scoring it.

    The exact-arithmetic test above proves the profiled value is identically
    zero at K = d_lambda + 1 on a centered sample. This drives the same fixture
    through the public API, where the same fact has to surface as a refusal
    rather than as a number: ``optimize_partition`` hits a singular initial
    state, and ``fit_quantizer`` would otherwise return a rule whose profiled
    retention is zero, because the soft solver checks n_bins only against the
    Fisher rank, which this configuration satisfies.

    The K = d_lambda + 2 control on the same atoms must still succeed and
    reproduce the fixture's recorded exact value 9/5.
    """
    fixture = json.loads(
        (RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-DS-MARGINS-RANK-VACUITY-001.json").read_text()
    )
    scores = np.array([[float(Fraction(v)) for v in row] for row in fixture["scores"]])
    weights = np.array([float(Fraction(w)) for w in fixture["weights"]])
    interest = tuple(fixture["poi_indices"])
    vacuous_bins = int(fixture["K"])
    dimension = scores.shape[1]
    assert vacuous_bins == len(fixture["nuisance_indices"]) + 1 == dimension
    np.testing.assert_allclose(weights @ scores, 0.0, atol=0.0)

    criterion = sq.ProfiledDOptimality(interest=interest)
    provenance = sq.ScoreProvenance(kind="exact", reference_point=(0.0,) * dimension)
    for config in (sq.DExchangeConfig(seed=0), sq.MahalanobisLloydConfig(seed=0)):
        with pytest.raises(ValueError, match="rank at most n_bins"):
            sq.optimize_partition(
                scores,
                weights=weights,
                n_bins=vacuous_bins,
                criterion=criterion,
                config=config,
                provenance=provenance,
            )

    sample = sq.ScoreSample(scores, weights, provenance=provenance)
    with pytest.raises(ValueError, match="profiled-D fit is degenerate"):
        sq.fit_quantizer(
            sample,
            n_bins=vacuous_bins,
            criterion=criterion,
            config=sq.SoftVoronoiConfig(seed=0),
        )

    # The refusal above is a claim about ordering, not only about wording. The
    # fit builds a retention history by scoring recorded snapshots through
    # profiled_information_report, whose own nuisance guard decides singularity
    # from a factorization whose last bits are platform dependent. Whenever that
    # guard fires first it blames the nuisance parameterization for what is a
    # bin-budget fact, and the refusal below never runs - which is exactly how
    # this regressed. So the invariant is stronger than the message: on a
    # degenerate budget nothing profiled may be reported at all.
    with monkeypatch.context() as patched:
        patched.setattr(
            api,
            "profiled_information_report",
            _refuse_to_report,
        )
        with pytest.raises(ValueError, match="profiled-D fit is degenerate"):
            sq.fit_quantizer(
                sample,
                n_bins=vacuous_bins,
                criterion=criterion,
                config=sq.SoftVoronoiConfig(seed=0),
            )

    # One more bin lifts the rank ceiling and the value becomes positive. All
    # four atoms are singletons there, which is the state the fixture priced.
    restored = sq.optimize_partition(
        scores,
        weights=weights,
        n_bins=vacuous_bins + 1,
        criterion=criterion,
        config=sq.DExchangeConfig(seed=0),
        provenance=provenance,
    )
    expected = fixture["exact_quantities"]["k_equals_d_lambda_plus_2_all_singletons_value"]
    assert restored.objective == pytest.approx(float(np.log(float(Fraction(expected)))), abs=1e-12)


def test_profiled_bins_equal_to_dimension_stay_legal_off_the_centered_class() -> None:
    """The bin guard is centering-agnostic on purpose, so this must not regress.

    The rank ceiling that makes n_bins == dimension vacuous is
    ``sum_b w_b m_b = 0``, which holds only for an exactly centered sample.
    Scores away from the true reference point have a nonzero weighted mean, the
    ceiling rises to n_bins, and the configuration is feasible. Tightening the
    guard to n_bins > dimension for every sample - the obvious reading of
    CE-DS-MARGINS-RANK-VACUITY-001 - would refuse this legitimate case.
    """
    rng = np.random.default_rng(11)
    scores = rng.normal(size=(60, 2)) + 0.9
    weights = np.full(60, 1.0 / 60)
    assert not np.allclose(weights @ scores, 0.0, atol=1e-3)

    result = sq.optimize_partition(
        scores,
        weights=weights,
        n_bins=scores.shape[1],
        criterion=sq.ProfiledDOptimality(interest=(0,)),
        config=sq.DExchangeConfig(seed=0),
        provenance=sq.ScoreProvenance(kind="exact", reference_point=(0.0, 0.0)),
    )
    assert np.isfinite(result.objective)


def test_ds15_projection_tax_identity_survives_ties_duplicates_and_unequal_weights() -> None:
    """Proposition 4 is pure finite algebra: it holds off DS15's assumptions.

    Duplicate atoms with unequal positive weights, and a nuisance-symmetric
    sample whose efficient scores carry exact duplicate values, both satisfy
    the exact identity profiled = between - cross^2 / I_ll on every feasible
    labeling; on singular-nuisance labelings the pseudo-inverse value
    collapses to the between value exactly.
    """
    datasets = [
        (
            [(2, 1), (2, 1), (-1, 2), (0, -3), (-1, -1), (-2, 0)],
            [Fraction(1, 4)] + [Fraction(1, 8)] * 3 + [Fraction(1, 4), Fraction(1, 8)],
            88,
            2,
        ),
        (
            [(1, 1), (1, -1), (-1, 2), (-1, -2), (0, 3), (0, -3)],
            [Fraction(1, 6)] * 6,
            89,
            1,
        ),
    ]
    for raw, weights, expected_feasible, expected_singular in datasets:
        total = sum(weights)
        mean = [
            sum(w * Fraction(r[c]) for w, r in zip(weights, raw, strict=True)) / total
            for c in range(2)
        ]
        scores = [[Fraction(r[c]) - mean[c] for c in range(2)] for r in raw]
        n_rows = len(scores)
        full = [
            [
                sum(w * row[a] * row[b] for w, row in zip(weights, scores, strict=True)) / total
                for b in range(2)
            ]
            for a in range(2)
        ]
        slope = full[0][1] / full[1][1]
        shat = [row[0] - slope * row[1] for row in scores]
        assert sum(w * s * row[1] for w, s, row in zip(weights, shat, scores, strict=True)) == 0

        n_feasible = n_singular = 0
        for labels in _canonical_partitions(n_rows, 3):
            masses = [Fraction(0)] * 3
            shat_sums = [Fraction(0)] * 3
            lam_sums = [Fraction(0)] * 3
            psi_sums = [Fraction(0)] * 3
            for row, label in enumerate(labels):
                masses[label] += weights[row]
                shat_sums[label] += weights[row] * shat[row]
                lam_sums[label] += weights[row] * scores[row][1]
                psi_sums[label] += weights[row] * scores[row][0]
            between = sum(s**2 / m for s, m in zip(shat_sums, masses, strict=True))
            cross = sum(s * ell / m for s, ell, m in zip(shat_sums, lam_sums, masses, strict=True))
            i_ll = sum(ell**2 / m for ell, m in zip(lam_sums, masses, strict=True))
            i_pp = sum(p**2 / m for p, m in zip(psi_sums, masses, strict=True))
            i_pl = sum(p * ell / m for p, ell, m in zip(psi_sums, lam_sums, masses, strict=True))
            if i_ll == 0:
                n_singular += 1
                assert cross == 0 and i_pl == 0
                assert i_pp == between
                continue
            n_feasible += 1
            assert i_pp - i_pl**2 / i_ll == between - cross**2 / i_ll
        assert (n_feasible, n_singular) == (expected_feasible, expected_singular)


def test_ds16_exchange_stable_state_can_retain_macroscopic_margins() -> None:
    """One-point exchange stability does not force the DS15 degeneracy.

    A non-global one-point exchange-stable profiled-Ds labeling - all 16
    admissible one-point moves have exact profiled gain <= 0 - carries a
    macroscopic nuisance block, conditioning bound, minimum cell mass, and
    projected-centroid separation, at a price below the exact efficient-score
    interval optimum v_K. The global optimum's nuisance block is four times
    smaller than the witness's: the value ranking is anti-aligned with the
    conditioning margin. Exchange stability does not preclude the DS14
    margins; it prices them (CE-DS-STABLE-MARGIN-RETAINING-001).
    """
    fixture = json.loads(
        (
            RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-DS-STABLE-MARGIN-RETAINING-001.json"
        ).read_text()
    )
    scores = [[Fraction(value) for value in row] for row in fixture["scores"]]
    n_rows, n_bins = len(scores), 3
    labels = tuple(fixture["labels_before"])
    exact = fixture["exact_quantities"]

    def profiled(candidate: tuple[int, ...]) -> Fraction | None:
        info = _exact_binned_information(scores, candidate, n_bins)
        if info[1][1] == 0:
            return None
        return info[0][0] - info[0][1] * info[1][0] / info[1][1]

    witness_value = profiled(labels)
    assert witness_value == Fraction(exact["witness_profiled_value"])

    info = _exact_binned_information(scores, labels, n_bins)
    masses, moments = _exact_ds_cells(scores, labels, n_bins)
    assert info[1][1] == Fraction(exact["witness_nuisance_block_I11"])
    assert min(masses) == Fraction(exact["witness_min_cell_mass"])

    slope = info[0][1] / info[1][1]
    projected = [
        moments[b][0] / masses[b] - slope * moments[b][1] / masses[b] for b in range(n_bins)
    ]
    separation = min(
        abs(projected[b] - projected[c]) for b in range(n_bins) for c in range(b + 1, n_bins)
    )
    assert separation == Fraction(exact["witness_projected_centroid_separation"])

    determinant = info[0][0] * info[1][1] - info[0][1] * info[1][0]
    trace = info[0][0] + info[1][1]
    assert determinant / trace == Fraction(exact["witness_lambda_min_lower_bound_det_over_trace"])

    # Every admissible one-point move (source cell has >= 2 rows) has exact
    # nonpositive profiled gain: this is one-point exchange stability.
    gains: list[Fraction] = []
    for row in range(n_rows):
        source = labels[row]
        if sum(1 for label in labels if label == source) < 2:
            continue
        for target in range(n_bins):
            if target == source:
                continue
            moved = list(labels)
            moved[row] = target
            moved_value = profiled(tuple(moved))
            assert moved_value is not None
            gains.append(moved_value - witness_value)
    assert len(gains) == 16
    assert all(gain <= 0 for gain in gains)
    assert max(gains) == Fraction(exact["witness_max_residual_move_gain"])

    # The witness is exchange-stable but not the exact global optimum, and the
    # global optimum's nuisance block is markedly smaller than the witness's.
    best_value: Fraction | None = None
    best_labels: tuple[int, ...] | None = None
    for candidate in _canonical_partitions(n_rows, n_bins):
        value = profiled(candidate)
        if value is None:
            continue
        if best_value is None or value > best_value:
            best_value, best_labels = value, candidate
    assert best_labels is not None
    assert best_value == Fraction(exact["global_optimum_value"])
    assert best_value > witness_value
    assert "".join(str(label) for label in best_labels) == exact["global_optimum_labels"]

    global_info = _exact_binned_information(scores, best_labels, n_bins)
    assert global_info[1][1] == Fraction(exact["global_optimum_nuisance_block_I11"])
    assert global_info[1][1] < info[1][1]

    # The efficient-score interval optimum v_K strictly exceeds the witness,
    # by the recorded exact gap.
    weight = Fraction(1, n_rows)
    full = [[sum(weight * row[a] * row[b] for row in scores) for b in range(2)] for a in range(2)]
    bhat = full[0][1] / full[1][1]
    assert bhat == Fraction(exact["full_sample_regression_slope_Bhat"])
    shat = [row[0] - bhat * row[1] for row in scores]

    order = sorted(range(n_rows), key=shat.__getitem__)
    interval_optimum = Fraction(0)
    for first_cut in range(1, n_rows - 1):
        for second_cut in range(first_cut + 1, n_rows):
            cell_masses = [Fraction(0)] * n_bins
            cell_sums = [Fraction(0)] * n_bins
            for position, row in enumerate(order):
                cell = 0 if position < first_cut else (1 if position < second_cut else 2)
                cell_masses[cell] += weight
                cell_sums[cell] += weight * shat[row]
            interval_optimum = max(
                interval_optimum,
                sum(
                    cell_sums[b] ** 2 / cell_masses[b] for b in range(n_bins) if cell_masses[b] > 0
                ),
            )
    assert interval_optimum == Fraction(exact["efficient_score_interval_optimum_v_K"])
    assert witness_value < interval_optimum
    assert interval_optimum - witness_value == Fraction(exact["value_gap_v_K_minus_witness"])


def test_ds16_efficient_score_interval_seed_is_not_exchange_stable() -> None:
    """The efficient-score interval labeling is not one-point exchange-stable.

    The exact interval optimum of the full-sample efficient score shat - the
    documented profiled initializer, and the finite analogue of DS15's
    degenerate attainer J* - admits an improving one-point move: relocating
    row 7 raises the profiled value by an exact positive gain while growing
    the binned nuisance block 27-fold, buying back nuisance information, the
    finite mechanism behind DS15 Proposition 6's steering
    (CE-DS-INTERVAL-SEED-UNSTABLE-001).
    """
    fixture = json.loads(
        (
            RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-DS-INTERVAL-SEED-UNSTABLE-001.json"
        ).read_text()
    )
    scores = [[Fraction(value) for value in row] for row in fixture["scores"]]
    n_rows, n_bins = len(scores), 3
    exact = fixture["exact_quantities"]
    weight = Fraction(1, n_rows)

    full = [[sum(weight * row[a] * row[b] for row in scores) for b in range(2)] for a in range(2)]
    bhat = full[0][1] / full[1][1]
    assert bhat == Fraction(exact["full_sample_regression_slope_Bhat"])
    shat = [row[0] - bhat * row[1] for row in scores]

    # Enumerate the C(7, 2) contiguous cut placements over the sorted shat
    # order and keep the best-scoring interval grouping.
    order = sorted(range(n_rows), key=shat.__getitem__)
    interval_optimum = Fraction(0)
    interval_labels: tuple[int, ...] | None = None
    for first_cut in range(1, n_rows - 1):
        for second_cut in range(first_cut + 1, n_rows):
            labeling = [0] * n_rows
            for position, row in enumerate(order):
                labeling[row] = 0 if position < first_cut else (1 if position < second_cut else 2)
            cell_masses = [Fraction(0)] * n_bins
            cell_sums = [Fraction(0)] * n_bins
            for row in range(n_rows):
                cell_masses[labeling[row]] += weight
                cell_sums[labeling[row]] += weight * shat[row]
            value = sum(
                cell_sums[b] ** 2 / cell_masses[b] for b in range(n_bins) if cell_masses[b] > 0
            )
            if value > interval_optimum:
                interval_optimum = value
                interval_labels = tuple(labeling)
    assert interval_labels is not None
    assert interval_optimum == Fraction(exact["interval_value_v_K"])

    def canonicalize(labeling: tuple[int, ...]) -> tuple[int, ...]:
        seen: dict[int, int] = {}
        canonical = []
        for label in labeling:
            if label not in seen:
                seen[label] = len(seen)
            canonical.append(seen[label])
        return tuple(canonical)

    labels_before = canonicalize(interval_labels)
    assert labels_before == tuple(fixture["labels_before"])

    def profiled(candidate: tuple[int, ...]) -> Fraction | None:
        info = _exact_binned_information(scores, candidate, n_bins)
        if info[1][1] == 0:
            return None
        return info[0][0] - info[0][1] * info[1][0] / info[1][1]

    value_before = profiled(labels_before)
    assert value_before == Fraction(exact["interval_labeling_profiled_value"])
    info_before = _exact_binned_information(scores, labels_before, n_bins)
    assert info_before[1][1] == Fraction(exact["interval_labeling_nuisance_block_I11"])

    move = exact["improving_move"]
    assert labels_before[move["row"]] == move["from_cell"]
    labels_after = list(labels_before)
    labels_after[move["row"]] = move["to_cell"]
    labels_after = tuple(labels_after)
    assert labels_after == tuple(fixture["labels_after_or_optimum"])

    value_after = profiled(labels_after)
    gain = value_after - value_before
    assert gain == Fraction(exact["exact_gain"])
    assert gain > 0

    info_after = _exact_binned_information(scores, labels_after, n_bins)
    assert info_after[1][1] == Fraction(exact["post_move_nuisance_block_I11"])
    assert info_after[1][1] > info_before[1][1]


def test_ds17_signsplit_stationary_state_retains_margins_without_separation() -> None:
    """A bounded-packet stationary K=3 state can retain (M2)+(M3) margins
    with zero projected-centroid separation, i.e. without (M5).

    The sign-split sibling of CE-DS-POP-WASTED-CELLS-001 on the same 8-atom
    nuisance-sign-symmetric law splits the left half {s_psi < 0} by
    sign(s_lambda) into two cells and leaves the right half as one cell.
    The binned information is full rank with a macroscopic minimum
    eigenvalue and minimum cell mass, yet the two left cells' projected
    centroids exactly coincide - zero separation - and every atom still
    satisfies the nearest-projected-centroid stationarity rule, with ties.
    Merging the coincident pair collapses to the K=2 s_psi-threshold rule,
    whose nuisance block is exactly singular: the compilable reduction
    carries no margin (CE-DS-LCM-SIGNSPLIT-MARGIN-001).
    """
    fixture = json.loads(
        (RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-DS-LCM-SIGNSPLIT-MARGIN-001.json").read_text()
    )
    scores = [[Fraction(value) for value in row] for row in fixture["scores"]]
    weights = [Fraction(value) for value in fixture["weights"]]
    assert weights == [Fraction(1, 8)] * 8
    labels = tuple(fixture["labels_before"])
    assert labels == (0, 1, 0, 1, 2, 2, 2, 2)
    n_rows, n_bins = len(scores), 3
    exact = fixture["exact_quantities"]

    # (1) cell masses.
    masses, moments = _exact_ds_cells(scores, labels, n_bins)
    assert masses == [Fraction(value) for value in exact["cell_masses"]]
    assert masses == [Fraction(1, 4), Fraction(1, 4), Fraction(1, 2)]

    # (2) binned information.
    info = _exact_binned_information(scores, labels, n_bins)
    assert info == [[Fraction(value) for value in row] for row in exact["binned_information"]]
    assert info == [[Fraction(4), Fraction(0)], [Fraction(0), Fraction(9, 8)]]

    # (3) profiled value and lambda_min (the off-diagonal is exactly zero,
    # so lambda_min of the 2x2 block is the smaller diagonal entry).
    profiled_value = info[0][0] - info[0][1] * info[1][0] / info[1][1]
    assert profiled_value == Fraction(4)
    assert profiled_value == Fraction(exact["profiled_value"])
    assert info[0][1] == 0
    lambda_min = min(info[0][0], info[1][1])
    assert lambda_min == Fraction(9, 8)
    assert lambda_min == Fraction(exact["lambda_min"])

    # (4) slope, projected centroids, and the coincident pair's separation.
    slope = info[0][1] / info[1][1]
    assert slope == 0
    projected = [
        moments[b][0] / masses[b] - slope * moments[b][1] / masses[b] for b in range(n_bins)
    ]
    assert projected == [Fraction(-2), Fraction(-2), Fraction(2)]
    assert projected == [Fraction(value) for value in exact["projected_centroids"]]
    separation = min(
        abs(projected[b] - projected[c]) for b in range(n_bins) for c in range(b + 1, n_bins)
    )
    assert separation == Fraction(0)

    # (5) stationarity with ties: every atom is at least as close (in the
    # efficient score e(s) = s_psi, since B* = 0) to its own cell's
    # projected centroid as to any other cell's.
    violations = 0
    for row in range(n_rows):
        e_row = scores[row][0] - slope * scores[row][1]
        own_distance = abs(e_row - projected[labels[row]])
        for cell in range(n_bins):
            other_distance = abs(e_row - projected[cell])
            assert own_distance <= other_distance
            if other_distance < own_distance:
                violations += 1
    assert violations == 0
    assert violations == exact["first_order_violations"]

    # (6) the reduced rule: merging cells 0 and 1 gives the K=2
    # s_psi-threshold rule, whose nuisance block is exactly singular.
    reduced_labels = tuple(0 if label in (0, 1) else 1 for label in labels)
    assert reduced_labels == (0, 0, 0, 0, 1, 1, 1, 1)
    reduced_info = _exact_binned_information(scores, reduced_labels, 2)
    assert reduced_info[1][1] == Fraction(0)

    # (7) value identity: the K=3 profiled value equals the K'=2
    # between-value of the projected law.
    w_left = masses[0] + masses[1]
    w_right = masses[2]
    assert w_left == Fraction(1, 2)
    assert w_right == Fraction(1, 2)
    group_between = w_left * Fraction(-2) ** 2 + w_right * Fraction(2) ** 2
    assert group_between == Fraction(4)
    assert profiled_value == group_between


def test_ds17_minimal_atomic_signsplit_is_only_a_boundary_witness() -> None:
    """The N=3 sign-split algebra is minimal but outside DS17's hypotheses."""
    fixture = json.loads(
        (
            RESEARCH_WORKSPACE / "COUNTEREXAMPLES" / "CE-DS-LCM-SIGNSPLIT-MINIMAL-001.json"
        ).read_text()
    )
    scores = [[Fraction(value) for value in row] for row in fixture["scores"]]
    weights = [Fraction(value) for value in fixture["weights"]]
    labels = tuple(fixture["labels_before"])
    n_rows, n_bins = len(scores), fixture["K"]
    exact = fixture["exact_quantities"]

    assert n_rows == n_bins == 3
    assert weights == [Fraction(1, 3)] * 3
    assert labels == (0, 1, 2)
    assert [
        sum(weight * score[column] for weight, score in zip(weights, scores, strict=True))
        for column in range(2)
    ] == [Fraction(value) for value in exact["weighted_score_mean"]]

    masses, moments = _exact_ds_cells(scores, labels, n_bins)
    assert masses == [Fraction(value) for value in exact["cell_masses"]]
    info = _exact_binned_information(scores, labels, n_bins)
    assert info == [[Fraction(value) for value in row] for row in exact["binned_information"]]
    assert info == [[Fraction(2), Fraction(0)], [Fraction(0), Fraction(2, 3)]]

    slope = info[0][1] / info[1][1]
    projected = [
        moments[cell][0] / masses[cell] - slope * moments[cell][1] / masses[cell]
        for cell in range(n_bins)
    ]
    assert slope == 0
    assert projected == [Fraction(value) for value in exact["projected_centroids"]]
    assert projected == [Fraction(-1), Fraction(-1), Fraction(2)]
    assert (
        min(
            abs(projected[first] - projected[second])
            for first in range(n_bins)
            for second in range(first + 1, n_bins)
        )
        == 0
    )

    profiled = info[0][0] - info[0][1] * info[1][0] / info[1][1]
    assert profiled == Fraction(exact["profiled_value"])
    assert min(info[0][0], info[1][1]) == Fraction(exact["lambda_min"])

    admissible_moves = 0
    for source in labels:
        if labels.count(source) <= 1:
            continue
        for destination in range(n_bins):
            if destination != source:
                admissible_moves += 1
    assert admissible_moves == exact["admissible_nonempty_preserving_one_point_moves"] == 0

    reduced_labels = (0, 0, 1)
    reduced_info = _exact_binned_information(scores, reduced_labels, 2)
    assert reduced_info[1][1] == Fraction(exact["reduced_rule_nuisance_block"])

    # An atom sits on its own zero-width slab with mass 1/3 for every positive
    # width, so no uniform slab modulus can tend to zero: (M4) fails. The
    # coincident projected centroids also make (M5) fail. These checks keep
    # the fixture classified as a boundary witness, never a DS17 refutation.
    slab_center = scores[0][0]
    for width in (Fraction(1, 10), Fraction(1, 100), Fraction(1, 1000)):
        slab_mass = sum(
            weight
            for weight, score in zip(weights, scores, strict=True)
            if abs(score[0] - slab_center) <= width
        )
        assert slab_mass == Fraction(2, 3)
    assert fixture["claim_falsified"].startswith("None:")


def test_ds18_population_cut_labels_need_not_be_exchange_stable() -> None:
    """Boundary noise can defeat the raw population labels at finite N."""
    fixture = json.loads(
        (
            RESEARCH_WORKSPACE
            / "COUNTEREXAMPLES"
            / "CE-DS-NONCENTERED-POPULATION-CUT-UNSTABLE-001.json"
        ).read_text()
    )
    scores = [[Fraction(value) for value in row] for row in fixture["scores"]]
    weights = [Fraction(value) for value in fixture["weights"]]
    before = tuple(fixture["labels_before"])
    after = tuple(fixture["labels_after_or_optimum"])

    assert len(scores) == 4
    assert fixture["K"] == 3
    assert [
        sum(weight * score[column] for weight, score in zip(weights, scores, strict=True))
        for column in range(2)
    ] == [Fraction(0), Fraction(0)]

    before_information = _exact_binned_information(scores, before, 3)
    after_information = _exact_binned_information(scores, after, 3)
    assert before_information == [
        [Fraction(value) for value in row]
        for row in fixture["exact_quantities"]["information_before"]
    ]
    assert after_information == [
        [Fraction(value) for value in row]
        for row in fixture["exact_quantities"]["information_after"]
    ]

    before_value = (
        before_information[0][0]
        - before_information[0][1] ** 2 / before_information[1][1]
    )
    after_value = (
        after_information[0][0]
        - after_information[0][1] ** 2 / after_information[1][1]
    )
    assert before_value == Fraction(fixture["objective_before"])
    assert after_value == Fraction(fixture["objective_after"])
    assert after_value - before_value == Fraction(fixture["exact_quantities"]["exact_gain"])
    assert after_value > before_value

    partitions = _canonical_partitions(4, 3)
    regular_values = []
    for labels in partitions:
        information = _exact_binned_information(scores, labels, 3)
        if information[1][1] == 0:
            continue
        value = information[0][0] - information[0][1] ** 2 / information[1][1]
        regular_values.append((value, labels))
    assert max(regular_values) == (after_value, after)


def test_ds18_named_off_class_root_and_margins_are_exact() -> None:
    """The bounded off-(L) law has the registered regular DS17 root exactly."""
    masses = [Fraction(1, 3)] * 3
    means_psi = [Fraction(-2, 3), Fraction(0), Fraction(2, 3)]
    means_lambda = [Fraction(4, 9), Fraction(-8, 9), Fraction(4, 9)]
    information = [
        [
            sum(
                mass * (means_psi if first == 0 else means_lambda)[cell]
                * (means_psi if second == 0 else means_lambda)[cell]
                for cell, mass in enumerate(masses)
            )
            for second in range(2)
        ]
        for first in range(2)
    ]
    full_information = [
        [Fraction(1, 3), Fraction(0)],
        [Fraction(0), Fraction(17, 15)],
    ]

    assert information == [
        [Fraction(8, 27), Fraction(0)],
        [Fraction(0), Fraction(32, 81)],
    ]
    assert min(information[0][0], information[1][1]) == Fraction(8, 27)
    assert information[0][1] == 0  # DS17 root residual and beta numerator
    assert means_psi == [Fraction(-2, 3), Fraction(0), Fraction(2, 3)]
    assert [
        (means_psi[index] + means_psi[index + 1]) / 2 for index in range(2)
    ] == [Fraction(-1, 3), Fraction(1, 3)]
    assert min(
        means_psi[index + 1] - means_psi[index] for index in range(2)
    ) == Fraction(2, 3)
    assert information[0][0] / full_information[0][0] == Fraction(8, 9)
    assert Fraction(1, 4) < min(masses)
    assert Fraction(1, 4) < min(information[0][0], information[1][1])
    assert Fraction(1, 2) < Fraction(2, 3)

    artifact = json.loads(
        (
            RESEARCH_WORKSPACE
            / "WORK"
            / "artifacts"
            / "OPEN-DS-MARGINS-NONCENTERED"
            / "exact-falsification.json"
        ).read_text()
    )
    exact = artifact["population_exact"]
    assert exact["binned_information"] == [["8/27", "0"], ["0", "32/81"]]
    assert exact["full_information"] == [["1/3", "0"], ["0", "17/15"]]
    assert exact["root_residual"] == "0"
    assert exact["ds_retention"] == "8/9"
