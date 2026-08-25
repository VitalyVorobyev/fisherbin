"""Exact finite-sample D-optimal partition optimization."""

from __future__ import annotations

from collections.abc import Iterator
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
from .criteria import DOptimality
from .information import information_report
from .quantizers import hard_assign, weighted_kmeans
from .result import PartitionResult
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
class _Move:
    row: int
    destination: int
    gain: float


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
        labels = labels.at[move.row].set(move.destination)
        state = _cell_state(coordinates, effective_weights, labels, n_bins)
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


def _exact_d_move_gain(
    information_inverse: ArrayLike,
    source_residual: ArrayLike,
    destination_residual: ArrayLike,
    *,
    point_weight: float,
    source_weight: float,
    destination_weight: float,
) -> float:
    """Return the exact log-determinant gain of one admissible relocation."""
    if point_weight <= 0:
        raise ValueError("point_weight must be positive")
    if source_weight <= point_weight:
        raise ValueError("a relocation cannot empty its source cell")
    if destination_weight <= 0:
        raise ValueError("destination_weight must be positive")
    inverse = jnp.asarray(information_inverse)
    source = jnp.asarray(source_residual, dtype=inverse.dtype)
    destination = jnp.asarray(destination_residual, dtype=inverse.dtype)
    alpha = point_weight * source_weight / (source_weight - point_weight)
    beta = point_weight * destination_weight / (destination_weight + point_weight)
    q_source = float(np.asarray(source @ inverse @ source))
    q_destination = float(np.asarray(destination @ inverse @ destination))
    q_cross = float(np.asarray(source @ inverse @ destination))
    determinant_ratio = (1 + alpha * q_source) * (
        1 - beta * q_destination
    ) + alpha * beta * q_cross**2
    return float(np.log(determinant_ratio)) if determinant_ratio > 0 else float("-inf")


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


def _best_move(
    scores: jnp.ndarray,
    weights: jnp.ndarray,
    labels: jnp.ndarray,
    state: _CellState,
    config: DExchangeConfig,
) -> _Move | None:
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
    gain_array = np.asarray(gains)
    if config.first_improvement:
        improving = np.argwhere(gain_array > config.gain_tolerance)
        if improving.size:
            row, destination = improving[0]
            return _Move(int(row), int(destination), float(gain_array[row, destination]))
    flat_index = int(np.argmax(gain_array))
    row, destination = np.unravel_index(flat_index, gain_array.shape)
    gain = float(gain_array[row, destination])
    return None if not np.isfinite(gain) else _Move(int(row), int(destination), gain)


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


def _exhaustive_d_oracle(
    scores: ArrayLike,
    weights: ArrayLike | None,
    n_bins: int,
    *,
    rank_rtol: float | None = None,
) -> tuple[jnp.ndarray, float]:
    """Return the globally D-optimal labels for a tiny regression instance.

    This deliberately private oracle is exponentially expensive and exists for
    mathematical regression tests, not as a production solver.
    """
    sample = validate_sample(scores, weights)
    validate_n_bins(n_bins, sample.n_effective)
    effective_scores, effective_weights, _ = collapse_duplicate_scores(
        sample.effective_scores, sample.effective_weights
    )
    if n_bins > effective_scores.shape[0]:
        raise ValueError("n_bins exceeds distinct positive-weight score rows")
    if effective_scores.shape[0] > 12:
        raise ValueError("the exhaustive D oracle is limited to 12 positive-weight rows")
    full_information = jnp.einsum(
        "n,np,nq->pq", effective_weights, effective_scores, effective_scores
    )
    transform = fisher_transform(full_information, whiten=True, rank_rtol=rank_rtol)
    coordinates = transform.apply(effective_scores)
    best_labels: jnp.ndarray | None = None
    best_objective = float("-inf")
    for candidate in _restricted_growth_partitions(effective_scores.shape[0], n_bins):
        labels = jnp.asarray(candidate)
        try:
            objective = _cell_state(coordinates, effective_weights, labels, n_bins).objective
        except ValueError:
            continue
        if objective > best_objective:
            best_labels = labels
            best_objective = objective
    if best_labels is None:
        raise ValueError("no nonsingular D partition exists for this instance")
    return best_labels, best_objective


def _restricted_growth_partitions(n_rows: int, n_bins: int) -> Iterator[tuple[int, ...]]:
    labels = [0] * n_rows

    def visit(position: int, maximum: int) -> Iterator[tuple[int, ...]]:
        if position == n_rows:
            if maximum == n_bins - 1:
                yield tuple(labels)
            return
        for label in range(min(maximum + 1, n_bins - 1) + 1):
            labels[position] = label
            yield from visit(position + 1, max(maximum, label))

    yield from visit(1, 0)
