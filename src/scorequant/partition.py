"""Exact finite-sample D-optimal partition optimization."""

from __future__ import annotations

from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np

from ._typing import ArrayLike
from ._validation import (
    _ValidatedSample,
    collapse_duplicate_scores,
    validate_n_bins,
    validate_sample,
)
from .config import DExchangeConfig, KMeansConfig
from .criteria import DOptimality, ProfiledDOptimality
from .information import information_report, profiled_information_report
from .quantizers import hard_assign, weighted_kmeans
from .result import PartitionResult, ProfiledGeometryReport
from .sources import ScoreProvenance
from .transforms import fisher_transform


@dataclass(frozen=True, slots=True)
class _CellState:
    weights: jnp.ndarray
    sums: jnp.ndarray
    means: jnp.ndarray
    information: jnp.ndarray
    inverse: jnp.ndarray
    objective: float


@dataclass(frozen=True, slots=True)
class _ProfiledCellState:
    weights: jnp.ndarray
    sums: jnp.ndarray
    means: jnp.ndarray
    information: jnp.ndarray
    inverse: jnp.ndarray
    nuisance_information: jnp.ndarray
    nuisance_inverse: jnp.ndarray
    nuisance: tuple[int, ...]
    objective: float


@dataclass(frozen=True, slots=True)
class _Move:
    row: int
    destination: int
    gain: float


_CANDIDATE_WORKING_SET_BYTES = 64 * 1024 * 1024


def optimize_d_partition(
    scores: ArrayLike,
    *,
    weights: ArrayLike | None,
    n_bins: int,
    config: DExchangeConfig,
    provenance: ScoreProvenance,
) -> PartitionResult:
    """Optimize arbitrary labels of one fixed weighted score table."""
    sample = validate_sample(scores, weights)
    validate_n_bins(n_bins, sample.n_effective)
    effective_scores, effective_weights, inverse_rows = collapse_duplicate_scores(
        sample.effective_scores, sample.effective_weights
    )
    if n_bins > effective_scores.shape[0]:
        raise ValueError("n_bins exceeds distinct positive-weight score rows")
    full_information = jnp.einsum(
        "n,np,nq->pq", effective_weights, effective_scores, effective_scores
    )
    transform = fisher_transform(full_information, whiten=True, rank_rtol=config.rank_rtol)
    coordinates = transform.apply(effective_scores)
    if n_bins < transform.rank:
        raise ValueError(
            "D-optimality requires at least as many bins as informative directions; "
            "a normalized mean-zero score law generally requires one additional bin"
        )
    initializer = weighted_kmeans(
        coordinates,
        effective_weights,
        n_bins,
        KMeansConfig(
            whiten=False,
            rank_rtol=config.rank_rtol,
            seed=config.seed,
            n_init=config.n_init,
            max_iter=100,
            tolerance=1e-8,
            record_every=100,
        ),
    )
    labels = hard_assign(coordinates, initializer.centers)
    state = _cell_state(coordinates, effective_weights, labels, n_bins)
    objective_history = [state.objective]
    accepted_moves = 0
    scans = 0
    exchange_stable = False
    best_remaining_gain = float("-inf")

    for _ in range(config.max_sweeps):
        scans += 1
        move = _best_move(
            coordinates,
            effective_weights,
            labels,
            state,
            config,
        )
        best_remaining_gain = move.gain if move is not None else float("-inf")
        if move is None or move.gain <= config.gain_tolerance:
            exchange_stable = True
            break
        state = _apply_move(coordinates, effective_weights, labels, state, move)
        labels = labels.at[move.row].set(move.destination)
        objective_history.append(state.objective)
        accepted_moves += 1

    if not exchange_stable:
        final_move = _best_move(
            coordinates,
            effective_weights,
            labels,
            state,
            config,
        )
        best_remaining_gain = final_move.gain if final_move is not None else float("-inf")
        exchange_stable = final_move is None or final_move.gain <= config.gain_tolerance

    # The D theorem supplies the only canonical labels for zero-measure rows.
    all_coordinates = transform.apply(sample.scores)
    compiled_labels = _metric_assign(all_coordinates, state.means, state.inverse)
    effective_labels = labels[inverse_rows]
    compiled_labels = compiled_labels.at[sample.positive_weight_mask].set(effective_labels)
    if exchange_stable:
        geometric = _metric_assign(coordinates, state.means, state.inverse)
        if not np.array_equal(np.asarray(geometric), np.asarray(labels)):
            raise ValueError(
                "terminal D state is geometrically degenerate; duplicate/tied score atoms "
                "must be merged or assigned consistently"
            )

    raw_weights, raw_sums, raw_means = _raw_cell_statistics(sample, effective_labels, n_bins)
    raw_information = jnp.einsum("b,bp,bq->pq", raw_weights, raw_means, raw_means)
    report = information_report(
        sample.scores,
        compiled_labels,
        sample.weights,
        n_bins=n_bins,
        rank_rtol=config.rank_rtol,
    )
    return PartitionResult(
        labels=compiled_labels,
        training_scores=sample.scores,
        cell_weights=raw_weights,
        cell_score_sums=raw_sums,
        cell_score_means=raw_means,
        information_full=full_information,
        information_partitioned=raw_information,
        objective=state.objective,
        transform=transform,
        transformed_centers=state.means,
        metric=state.inverse,
        criterion=DOptimality(),
        config=config,
        train_report=report,
        provenance=provenance,
        accepted_moves=accepted_moves,
        sweeps=scans,
        exchange_stable=exchange_stable,
        best_remaining_gain=best_remaining_gain,
        objective_history=jnp.asarray(objective_history),
        positive_weight_mask=sample.positive_weight_mask,
    )


def optimize_profiled_d_partition(
    scores: ArrayLike,
    *,
    weights: ArrayLike | None,
    n_bins: int,
    criterion: ProfiledDOptimality,
    config: DExchangeConfig,
    provenance: ScoreProvenance,
) -> PartitionResult:
    """Optimize same-label profiled-D labels of one fixed score table."""
    sample = validate_sample(scores, weights)
    validate_n_bins(n_bins, sample.n_effective)
    effective_scores, effective_weights, inverse_rows = collapse_duplicate_scores(
        sample.effective_scores, sample.effective_weights
    )
    if n_bins > effective_scores.shape[0]:
        raise ValueError("n_bins exceeds distinct positive-weight score rows")
    dimension = effective_scores.shape[1]
    if any(index >= dimension for index in criterion.interest):
        raise ValueError(f"interest indices must be smaller than score dimension {dimension}")
    interest_set = set(criterion.interest)
    nuisance = tuple(index for index in range(dimension) if index not in interest_set)
    if not nuisance:
        raise ValueError("profiled D requires a nuisance block; use DOptimality")
    full_information = jnp.einsum(
        "n,np,nq->pq", effective_weights, effective_scores, effective_scores
    )
    transform = fisher_transform(full_information, whiten=True, rank_rtol=config.rank_rtol)
    if transform.rank != dimension:
        raise ValueError(
            "profiled D requires full-rank supplied-score information in the declared "
            "interest/nuisance parameterization"
        )
    coordinates = transform.apply(effective_scores)
    if n_bins < dimension:
        raise ValueError("profiled D requires at least as many bins as score dimensions")
    initializer = weighted_kmeans(
        coordinates,
        effective_weights,
        n_bins,
        KMeansConfig(
            whiten=False,
            rank_rtol=config.rank_rtol,
            seed=config.seed,
            n_init=config.n_init,
            max_iter=100,
            tolerance=1e-8,
            record_every=100,
        ),
    )
    labels = hard_assign(coordinates, initializer.centers)
    state = _profiled_cell_state(
        effective_scores, effective_weights, labels, n_bins, nuisance=nuisance
    )
    objective_history = [state.objective]
    accepted_moves = 0
    scans = 0
    exchange_stable = False
    best_remaining_gain = float("-inf")
    for _ in range(config.max_sweeps):
        scans += 1
        move = _best_profiled_move(effective_scores, effective_weights, labels, state, config)
        best_remaining_gain = move.gain if move is not None else float("-inf")
        if move is None or move.gain <= config.gain_tolerance:
            exchange_stable = True
            break
        state = _apply_profiled_move(effective_scores, effective_weights, labels, state, move)
        labels = labels.at[move.row].set(move.destination)
        objective_history.append(state.objective)
        accepted_moves += 1
    if not exchange_stable:
        final_move = _best_profiled_move(effective_scores, effective_weights, labels, state, config)
        best_remaining_gain = final_move.gain if final_move is not None else float("-inf")
        exchange_stable = final_move is None or final_move.gain <= config.gain_tolerance

    all_coordinates = transform.apply(sample.scores)
    extension_labels = hard_assign(all_coordinates, transform.apply(state.means))
    effective_labels = labels[inverse_rows]
    compiled_labels = extension_labels.at[sample.positive_weight_mask].set(effective_labels)
    raw_weights, raw_sums, raw_means = _raw_cell_statistics(sample, effective_labels, n_bins)
    raw_information = jnp.einsum("b,bp,bq->pq", raw_weights, raw_means, raw_means)
    report = information_report(
        sample.scores,
        compiled_labels,
        sample.weights,
        n_bins=n_bins,
        rank_rtol=config.rank_rtol,
    )
    profiled_report = profiled_information_report(
        sample.scores,
        compiled_labels,
        interest=criterion.interest,
        weights=sample.weights,
        n_bins=n_bins,
    )
    profiled_geometry = _profiled_geometry_report(
        effective_scores,
        effective_weights,
        labels,
        state,
        exchange_stable=exchange_stable,
    )
    return PartitionResult(
        labels=compiled_labels,
        training_scores=sample.scores,
        cell_weights=raw_weights,
        cell_score_sums=raw_sums,
        cell_score_means=raw_means,
        information_full=full_information,
        information_partitioned=raw_information,
        objective=state.objective,
        transform=transform,
        transformed_centers=None,
        metric=None,
        criterion=criterion,
        config=config,
        train_report=report,
        provenance=provenance,
        accepted_moves=accepted_moves,
        sweeps=scans,
        exchange_stable=exchange_stable,
        best_remaining_gain=best_remaining_gain,
        objective_history=jnp.asarray(objective_history),
        positive_weight_mask=sample.positive_weight_mask,
        profiled_report=profiled_report,
        profiled_geometry=profiled_geometry,
    )


def _cell_state(
    scores: jnp.ndarray, weights: jnp.ndarray, labels: jnp.ndarray, n_bins: int
) -> _CellState:
    cell_weights = jnp.zeros(n_bins, dtype=weights.dtype).at[labels].add(weights)
    sums = jnp.zeros((n_bins, scores.shape[1]), dtype=scores.dtype)
    sums = sums.at[labels].add(weights[:, None] * scores)
    if bool(np.asarray(jnp.any(cell_weights <= 0))):
        raise ValueError("D exchange requires exactly n_bins nonempty cells")
    means = sums / cell_weights[:, None]
    information = jnp.einsum("b,bp,bq->pq", cell_weights, means, means)
    information = 0.5 * (information + information.T)
    sign, logdet = jnp.linalg.slogdet(information)
    if float(np.asarray(sign)) <= 0:
        raise ValueError(
            "initial D partition is singular; increase n_bins or use a different reference sample"
        )
    return _CellState(
        weights=cell_weights,
        sums=sums,
        means=means,
        information=information,
        inverse=jnp.linalg.inv(information),
        objective=float(np.asarray(logdet)),
    )


def _profiled_cell_state(
    scores: jnp.ndarray,
    weights: jnp.ndarray,
    labels: jnp.ndarray,
    n_bins: int,
    *,
    nuisance: tuple[int, ...],
) -> _ProfiledCellState:
    cell_weights = jnp.zeros(n_bins, dtype=weights.dtype).at[labels].add(weights)
    sums = jnp.zeros((n_bins, scores.shape[1]), dtype=scores.dtype)
    sums = sums.at[labels].add(weights[:, None] * scores)
    if bool(np.asarray(jnp.any(cell_weights <= 0))):
        raise ValueError("profiled-D exchange requires exactly n_bins nonempty cells")
    means = sums / cell_weights[:, None]
    information = jnp.einsum("b,bp,bq->pq", cell_weights, means, means)
    information = 0.5 * (information + information.T)
    nuisance_indices = jnp.asarray(nuisance)
    nuisance_information = information[jnp.ix_(nuisance_indices, nuisance_indices)]
    full_sign, full_logdet = jnp.linalg.slogdet(information)
    nuisance_sign, nuisance_logdet = jnp.linalg.slogdet(nuisance_information)
    if float(np.asarray(full_sign)) <= 0 or float(np.asarray(nuisance_sign)) <= 0:
        raise ValueError(
            "initial profiled-D partition is singular; increase n_bins or use a different sample"
        )
    return _ProfiledCellState(
        weights=cell_weights,
        sums=sums,
        means=means,
        information=information,
        inverse=jnp.linalg.inv(information),
        nuisance_information=nuisance_information,
        nuisance_inverse=jnp.linalg.inv(nuisance_information),
        nuisance=nuisance,
        objective=float(np.asarray(full_logdet - nuisance_logdet)),
    )


def _profiled_geometry_report(
    scores: jnp.ndarray,
    weights: jnp.ndarray,
    labels: jnp.ndarray,
    state: _ProfiledCellState,
    *,
    exchange_stable: bool,
) -> ProfiledGeometryReport:
    nuisance_indices = jnp.asarray(state.nuisance)
    metric = state.inverse.at[jnp.ix_(nuisance_indices, nuisance_indices)].add(
        -state.nuisance_inverse
    )
    metric = 0.5 * (metric + metric.T)
    source_residuals = scores - state.means[labels]
    destination_residuals = scores[:, None, :] - state.means[None, :, :]
    source_distances = jnp.einsum("nr,rs,ns->n", source_residuals, metric, source_residuals)
    destination_distances = jnp.einsum(
        "nbr,rs,nbs->nb", destination_residuals, metric, destination_residuals
    )
    violations = jnp.maximum(source_distances[:, None] - destination_distances, 0)
    q_source = jnp.einsum("nr,rs,ns->n", source_residuals, state.inverse, source_residuals)
    source_weights = state.weights[labels]
    bounds = (
        weights[:, None]
        * q_source[:, None]
        * (1 / source_weights[:, None] + 1 / state.weights[None, :])
    )
    destinations = jnp.arange(state.weights.shape[0])[None, :]
    admissible = (source_weights > weights)[:, None] & (destinations != labels[:, None])
    evaluated_violations = jnp.where(admissible, violations, 0)
    evaluated_bounds = jnp.where(admissible, bounds, 0)
    residuals = jnp.where(admissible, violations - bounds, -jnp.inf)
    return ProfiledGeometryReport(
        metric=metric,
        maximum_positive_violation=float(np.asarray(jnp.max(evaluated_violations))),
        maximum_theoretical_bound=float(np.asarray(jnp.max(evaluated_bounds))),
        maximum_bound_residual=float(np.asarray(jnp.max(residuals))),
        violating_moves=int(np.asarray(jnp.sum(admissible & (violations > 0)))),
        evaluated_moves=int(np.asarray(jnp.sum(admissible))),
        bound_certified=exchange_stable,
    )


def _best_move(
    scores: jnp.ndarray,
    weights: jnp.ndarray,
    labels: jnp.ndarray,
    state: _CellState,
    config: DExchangeConfig,
) -> _Move | None:
    chunk_rows = _candidate_chunk_rows(scores, state.weights.shape[0])
    best: _Move | None = None
    for start in range(0, scores.shape[0], chunk_rows):
        stop = min(start + chunk_rows, scores.shape[0])
        gain_array = _move_gains(
            scores[start:stop],
            weights[start:stop],
            labels[start:stop],
            state,
        )
        if config.first_improvement:
            improving = np.argwhere(gain_array > config.gain_tolerance)
            if improving.size:
                row, destination = improving[0]
                return _Move(
                    start + int(row),
                    int(destination),
                    float(gain_array[row, destination]),
                )
        flat_index = int(np.argmax(gain_array))
        row, destination = np.unravel_index(flat_index, gain_array.shape)
        gain = float(gain_array[row, destination])
        if np.isfinite(gain) and (best is None or gain > best.gain):
            best = _Move(start + int(row), int(destination), gain)
    return best


def _best_profiled_move(
    scores: jnp.ndarray,
    weights: jnp.ndarray,
    labels: jnp.ndarray,
    state: _ProfiledCellState,
    config: DExchangeConfig,
) -> _Move | None:
    chunk_rows = _candidate_chunk_rows(scores, state.weights.shape[0])
    best: _Move | None = None
    for start in range(0, scores.shape[0], chunk_rows):
        stop = min(start + chunk_rows, scores.shape[0])
        gain_array = _profiled_move_gains(
            scores[start:stop], weights[start:stop], labels[start:stop], state
        )
        if config.first_improvement:
            improving = np.argwhere(gain_array > config.gain_tolerance)
            if improving.size:
                row, destination = improving[0]
                return _Move(
                    start + int(row), int(destination), float(gain_array[row, destination])
                )
        flat_index = int(np.argmax(gain_array))
        row, destination = np.unravel_index(flat_index, gain_array.shape)
        gain = float(gain_array[row, destination])
        if np.isfinite(gain) and (best is None or gain > best.gain):
            best = _Move(start + int(row), int(destination), gain)
    return best


def _candidate_chunk_rows(scores: jnp.ndarray, n_bins: int) -> int:
    item_size = np.dtype(scores.dtype).itemsize
    rank = scores.shape[1]
    values_per_row = n_bins * (rank + 4) + 4 * rank
    return max(
        1, min(scores.shape[0], _CANDIDATE_WORKING_SET_BYTES // (item_size * values_per_row))
    )


def _move_gains(
    scores: jnp.ndarray,
    weights: jnp.ndarray,
    labels: jnp.ndarray,
    state: _CellState,
) -> np.ndarray:
    source_weights = state.weights[labels]
    source_residuals = scores - state.means[labels]
    destination_residuals = scores[:, None, :] - state.means[None, :, :]
    source_denominator = jnp.where(source_weights > weights, source_weights - weights, 1)
    alpha = weights * source_weights / source_denominator
    beta = weights[:, None] * state.weights[None, :] / (state.weights[None, :] + weights[:, None])
    q_source = jnp.einsum("nr,rs,ns->n", source_residuals, state.inverse, source_residuals)
    q_destination = jnp.einsum(
        "nbr,rs,nbs->nb", destination_residuals, state.inverse, destination_residuals
    )
    q_cross = jnp.einsum("nr,rs,nbs->nb", source_residuals, state.inverse, destination_residuals)
    determinant_ratio = (1 + alpha[:, None] * q_source[:, None]) * (
        1 - beta * q_destination
    ) + alpha[:, None] * beta * q_cross**2
    destinations = jnp.arange(state.weights.shape[0])[None, :]
    admissible = (source_weights > weights)[:, None] & (destinations != labels[:, None])
    gains = jnp.where(admissible & (determinant_ratio > 0), jnp.log(determinant_ratio), -jnp.inf)
    return np.asarray(gains)


def _profiled_move_gains(
    scores: jnp.ndarray,
    weights: jnp.ndarray,
    labels: jnp.ndarray,
    state: _ProfiledCellState,
) -> np.ndarray:
    source_weights = state.weights[labels]
    source_residuals = scores - state.means[labels]
    destination_residuals = scores[:, None, :] - state.means[None, :, :]
    source_denominator = jnp.where(source_weights > weights, source_weights - weights, 1)
    alpha = weights * source_weights / source_denominator
    beta = weights[:, None] * state.weights[None, :] / (state.weights[None, :] + weights[:, None])

    def ratios(source: jnp.ndarray, destination: jnp.ndarray, inverse: jnp.ndarray) -> jnp.ndarray:
        q_source = jnp.einsum("nr,rs,ns->n", source, inverse, source)
        q_destination = jnp.einsum("nbr,rs,nbs->nb", destination, inverse, destination)
        q_cross = jnp.einsum("nr,rs,nbs->nb", source, inverse, destination)
        return (1 + alpha[:, None] * q_source[:, None]) * (1 - beta * q_destination) + alpha[
            :, None
        ] * beta * q_cross**2

    full_ratios = ratios(source_residuals, destination_residuals, state.inverse)
    nuisance_indices = jnp.asarray(state.nuisance)
    nuisance_ratios = ratios(
        source_residuals[:, nuisance_indices],
        destination_residuals[:, :, nuisance_indices],
        state.nuisance_inverse,
    )
    destinations = jnp.arange(state.weights.shape[0])[None, :]
    admissible = (source_weights > weights)[:, None] & (destinations != labels[:, None])
    gains = jnp.where(
        admissible & (full_ratios > 0) & (nuisance_ratios > 0),
        jnp.log(full_ratios) - jnp.log(nuisance_ratios),
        -jnp.inf,
    )
    return np.asarray(gains)


def _apply_move(
    scores: jnp.ndarray,
    weights: jnp.ndarray,
    labels: jnp.ndarray,
    state: _CellState,
    move: _Move,
) -> _CellState:
    source = int(labels[move.row])
    destination = move.destination
    point_weight = weights[move.row]
    point = scores[move.row]
    source_weight = state.weights[source]
    destination_weight = state.weights[destination]
    source_residual = point - state.means[source]
    destination_residual = point - state.means[destination]
    alpha = point_weight * source_weight / (source_weight - point_weight)
    beta = point_weight * destination_weight / (destination_weight + point_weight)

    information = (
        state.information
        + alpha * jnp.outer(source_residual, source_residual)
        - beta * jnp.outer(destination_residual, destination_residual)
    )
    information = 0.5 * (information + information.T)
    inverse = _rank_two_inverse_update(
        state.inverse,
        source_residual,
        destination_residual,
        alpha,
        beta,
        information,
    )
    cell_weights = state.weights.at[source].add(-point_weight).at[destination].add(point_weight)
    sums = (
        state.sums.at[source].add(-point_weight * point).at[destination].add(point_weight * point)
    )
    means = sums / cell_weights[:, None]
    sign, logdet = jnp.linalg.slogdet(information)
    if float(np.asarray(sign)) <= 0:
        raise FloatingPointError("an accepted D move produced singular information")
    return _CellState(
        weights=cell_weights,
        sums=sums,
        means=means,
        information=information,
        inverse=inverse,
        objective=float(np.asarray(logdet)),
    )


def _apply_profiled_move(
    scores: jnp.ndarray,
    weights: jnp.ndarray,
    labels: jnp.ndarray,
    state: _ProfiledCellState,
    move: _Move,
) -> _ProfiledCellState:
    source = int(labels[move.row])
    destination = move.destination
    point_weight = weights[move.row]
    point = scores[move.row]
    source_weight = state.weights[source]
    destination_weight = state.weights[destination]
    source_residual = point - state.means[source]
    destination_residual = point - state.means[destination]
    alpha = point_weight * source_weight / (source_weight - point_weight)
    beta = point_weight * destination_weight / (destination_weight + point_weight)
    information = (
        state.information
        + alpha * jnp.outer(source_residual, source_residual)
        - beta * jnp.outer(destination_residual, destination_residual)
    )
    information = 0.5 * (information + information.T)
    inverse = _rank_two_inverse_update(
        state.inverse,
        source_residual,
        destination_residual,
        alpha,
        beta,
        information,
    )
    nuisance_indices = jnp.asarray(state.nuisance)
    nuisance_source = source_residual[nuisance_indices]
    nuisance_destination = destination_residual[nuisance_indices]
    nuisance_information = (
        state.nuisance_information
        + alpha * jnp.outer(nuisance_source, nuisance_source)
        - beta * jnp.outer(nuisance_destination, nuisance_destination)
    )
    nuisance_information = 0.5 * (nuisance_information + nuisance_information.T)
    nuisance_inverse = _rank_two_inverse_update(
        state.nuisance_inverse,
        nuisance_source,
        nuisance_destination,
        alpha,
        beta,
        nuisance_information,
    )
    cell_weights = state.weights.at[source].add(-point_weight).at[destination].add(point_weight)
    sums = (
        state.sums.at[source].add(-point_weight * point).at[destination].add(point_weight * point)
    )
    means = sums / cell_weights[:, None]
    full_sign, full_logdet = jnp.linalg.slogdet(information)
    nuisance_sign, nuisance_logdet = jnp.linalg.slogdet(nuisance_information)
    if float(np.asarray(full_sign)) <= 0 or float(np.asarray(nuisance_sign)) <= 0:
        raise FloatingPointError("an accepted profiled-D move produced singular information")
    return _ProfiledCellState(
        weights=cell_weights,
        sums=sums,
        means=means,
        information=information,
        inverse=inverse,
        nuisance_information=nuisance_information,
        nuisance_inverse=nuisance_inverse,
        nuisance=state.nuisance,
        objective=float(np.asarray(full_logdet - nuisance_logdet)),
    )


def _rank_two_inverse_update(
    inverse: jnp.ndarray,
    source_residual: jnp.ndarray,
    destination_residual: jnp.ndarray,
    alpha: jnp.ndarray,
    beta: jnp.ndarray,
    information: jnp.ndarray,
) -> jnp.ndarray:
    source_projection = inverse @ source_residual
    source_denominator = 1 + alpha * (source_residual @ source_projection)
    first = inverse - alpha * jnp.outer(source_projection, source_projection) / source_denominator
    destination_projection = first @ destination_residual
    destination_denominator = 1 - beta * (destination_residual @ destination_projection)
    updated = (
        first
        + beta * jnp.outer(destination_projection, destination_projection) / destination_denominator
    )
    updated = 0.5 * (updated + updated.T)
    identity = jnp.eye(information.shape[0], dtype=information.dtype)
    residual = jnp.max(jnp.abs(information @ updated - identity))
    tolerance = 1e-8 if information.dtype == jnp.float64 else 2e-3
    if (
        not bool(np.asarray(jnp.isfinite(destination_denominator)))
        or float(np.asarray(destination_denominator)) <= 0
        or not bool(np.asarray(jnp.isfinite(residual)))
        or float(np.asarray(residual)) > tolerance
    ):
        return jnp.linalg.inv(information)
    return updated


def _metric_assign(scores: jnp.ndarray, means: jnp.ndarray, inverse: jnp.ndarray) -> jnp.ndarray:
    residuals = scores[:, None, :] - means[None, :, :]
    distances = jnp.einsum("nbr,rs,nbs->nb", residuals, inverse, residuals)
    return jnp.argmin(distances, axis=1)


def _raw_cell_statistics(
    sample: _ValidatedSample, labels: jnp.ndarray, n_bins: int
) -> tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    weights = sample.effective_weights
    scores = sample.effective_scores
    cell_weights = jnp.zeros(n_bins, dtype=weights.dtype).at[labels].add(weights)
    sums = jnp.zeros((n_bins, scores.shape[1]), dtype=scores.dtype)
    sums = sums.at[labels].add(weights[:, None] * scores)
    return cell_weights, sums, sums / cell_weights[:, None]
