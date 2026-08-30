"""Deterministic weighted score-space k-means."""

from __future__ import annotations

import numpy as np

from scorequant._binstats import scatter_bin_statistics
from scorequant._execution import (
    RandomSeed,
    backend_jit,
    scatter_set,
    split_seeds,
    weighted_choice,
)
from scorequant._execution import xp as jnp
from scorequant.config import KMeansConfig

from .common import QuantizerRun, _bin_weights, squared_distances


def _weighted_kmeans_plus_plus(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    seed: RandomSeed,
) -> jnp.ndarray:
    seeds = split_seeds(seed, n_bins)
    first = weighted_choice(seeds[0], weights / jnp.sum(weights))
    indices = [first]
    minimum_distances = squared_distances(points, points[first : first + 1])[:, 0]
    for bin_index in range(1, n_bins):
        probabilities = weights * minimum_distances
        total = float(np.asarray(jnp.sum(probabilities)))
        if not np.isfinite(total) or total <= 0:
            raise ValueError(
                "n_bins exceeds the number of distinct positive-weight score coordinates"
            )
        chosen = weighted_choice(seeds[bin_index], probabilities / jnp.sum(probabilities))
        indices.append(chosen)
        candidate_distances = squared_distances(points, points[chosen : chosen + 1])[:, 0]
        minimum_distances = jnp.minimum(minimum_distances, candidate_distances)
    return points[jnp.asarray(indices)]


def _repair_empty_bins(
    proposed: jnp.ndarray, occupancies: jnp.ndarray, residual: jnp.ndarray, points: jnp.ndarray
) -> jnp.ndarray:
    """Reseed every empty bin from the row of largest remaining residual.

    In-graph port of the eager repair: bin indices are scanned in order
    ``0..n_bins - 1`` and, for each empty one, the current
    ``jnp.argmax(residual)`` row becomes its new center and is then excluded
    (``-inf``) from later picks in the same pass, exactly as the eager
    ``for empty_bin in np.flatnonzero(...)`` loop did. Non-empty bins pass
    ``proposed``/``residual`` through unchanged via ``jnp.where``, so this is
    bit-identical to the eager repair, not merely close to it.
    """
    repaired = proposed
    remaining = residual
    for bin_index in np.flatnonzero(np.asarray(occupancies) == 0):
        replacement = int(np.asarray(jnp.argmax(remaining)))
        repaired = scatter_set(repaired, bin_index, points[replacement])
        remaining = scatter_set(remaining, replacement, -jnp.inf)
    return repaired


@backend_jit(static_argnames=("n_bins",))
def _lloyd_step(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    centers: jnp.ndarray,
    n_bins: int,
) -> tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    """Assign, score, and re-centre once, as a single compiled step.

    Everything the iteration needs from the device is returned together so the
    caller pays one host sync per iteration rather than one per query. Under
    JAX this also keeps the ``[N, B, R]`` tensor ``squared_distances`` builds
    inside a fused reduction instead of materializing it; under NumPy
    ``backend_jit`` calls straight through.
    """
    distances = squared_distances(points, centers)
    labels = jnp.argmin(distances, axis=1)
    selected = distances[jnp.arange(points.shape[0]), labels]
    objective = jnp.sum(weights * selected)
    statistics = scatter_bin_statistics(labels, weights, points, n_bins)
    has_empty = jnp.asarray(jnp.any(statistics.weights == 0))
    return labels, objective, statistics.weights, statistics.means, selected, has_empty


def _lloyd_scan(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    centers0: jnp.ndarray,
    n_bins: int,
    max_iter: int,
    tolerance: jnp.ndarray | float,
) -> tuple[
    jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray, jnp.ndarray
]:
    """Run one shared eager Lloyd schedule for either array namespace.

    Returns
    -------
    tuple
        ``(centers_history, objective_history, occupancy_history,
        converged_flags, final_centers, final_objective,
        final_occupancies)``. The first four are stacked along a leading
        ``max_iter`` axis and hold, for step ``i``, the centers entering that
        step (matching ``center_history.append(centers)`` before the
        update), that step's objective and occupancies, and whether
        convergence was first detected at that step. The last three describe
        the true state after the loop exits, mirroring the eager function's
        trailing recomputation on the post-loop ``centers``.
    """
    n_rows = int(points.shape[0])
    centers = centers0
    previous_objective = float("nan")
    centers_history: list[jnp.ndarray] = []
    objective_history: list[jnp.ndarray] = []
    occupancy_history: list[jnp.ndarray] = []
    converged_flags: list[bool] = []
    for _ in range(max_iter):
        _, objective, occupancies, proposed, selected, has_empty = _lloyd_step(
            points, weights, centers, n_bins
        )
        if bool(np.asarray(has_empty)):
            proposed = _repair_empty_bins(proposed, occupancies, weights * selected, points)
        objective_value = float(np.asarray(objective))
        this_converged = bool(
            np.isfinite(previous_objective)
            and abs(previous_objective - objective_value)
            <= float(np.asarray(tolerance)) * max(abs(previous_objective), 1.0)
        )
        centers_history.append(centers)
        objective_history.append(objective)
        occupancy_history.append(occupancies)
        converged_flags.append(this_converged)
        # The convergence step still applies its own update before stopping.
        # Freezing at the pre-update centers instead would shift the reported
        # objective at the 1e-6 level against the committed baselines.
        centers = proposed
        if this_converged:
            break
        previous_objective = objective_value

    final_centers = centers
    final_distances = squared_distances(points, final_centers)
    final_labels = jnp.argmin(final_distances, axis=1)
    final_objective = jnp.sum(weights * final_distances[jnp.arange(n_rows), final_labels])
    final_occupancies = _bin_weights(final_labels, weights, n_bins)
    return (
        jnp.stack(centers_history),
        jnp.asarray(objective_history),
        jnp.stack(occupancy_history),
        jnp.asarray(converged_flags),
        final_centers,
        final_objective,
        final_occupancies,
    )


def _single_kmeans(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    config: KMeansConfig,
    seed: RandomSeed,
) -> QuantizerRun:
    centers0 = _weighted_kmeans_plus_plus(points, weights, n_bins, seed)
    (
        centers_history,
        objective_history,
        occupancy_history,
        converged_flags,
        final_centers,
        final_objective,
        final_occupancies,
    ) = _lloyd_scan(points, weights, centers0, n_bins, config.max_iter, config.tolerance)

    # One host sync for the whole restart: pull the entire per-iteration
    # schedule at once instead of checking the objective and empty-bin
    # conditions on every iteration.
    converged_np = np.asarray(converged_flags)
    objective_np = np.asarray(objective_history)
    convergence_indices = np.flatnonzero(converged_np)
    last_iteration = (
        int(convergence_indices[0]) if convergence_indices.size else config.max_iter - 1
    )

    steps: list[int] = []
    center_history: list[jnp.ndarray] = []
    recorded_objectives: list[float] = []
    bin_weight_history: list[jnp.ndarray] = []
    for iteration in range(last_iteration + 1):
        should_record = iteration % config.record_every == 0
        converged = bool(converged_np[iteration])
        if should_record or converged or iteration == last_iteration:
            steps.append(iteration)
            center_history.append(centers_history[iteration])
            recorded_objectives.append(float(objective_np[iteration]))
            bin_weight_history.append(occupancy_history[iteration])

    # Record the updated final centers if they differ from the last recorded state.
    final_objective_value = float(np.asarray(final_objective))
    if not recorded_objectives or not np.isclose(final_objective_value, recorded_objectives[-1]):
        steps.append(steps[-1] + 1 if steps else 0)
        center_history.append(final_centers)
        recorded_objectives.append(final_objective_value)
        bin_weight_history.append(final_occupancies)
    return QuantizerRun(
        centers=final_centers,
        steps=steps,
        center_history=center_history,
        objective_history=recorded_objectives,
        bin_weight_history=bin_weight_history,
        objective_label="whitened_sse",
    )


def weighted_kmeans(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    config: KMeansConfig,
) -> QuantizerRun:
    """Run seeded weighted k-means restarts and return the lowest-SSE run."""
    norms = np.asarray(jnp.sum(points**2, axis=1))
    order = np.lexsort((np.asarray(weights), norms))
    ordered_points = points[jnp.asarray(order)]
    ordered_weights = weights[jnp.asarray(order)]
    seeds = split_seeds(config.seed, config.solver_restarts)
    runs = [_single_kmeans(ordered_points, ordered_weights, n_bins, config, seed) for seed in seeds]
    return min(runs, key=lambda run: run.objective_history[-1])
