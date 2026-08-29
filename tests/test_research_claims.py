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
    full = [
        [sum(weight * row[a] * row[b] for row in scores) for b in range(2)] for a in range(2)
    ]
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
