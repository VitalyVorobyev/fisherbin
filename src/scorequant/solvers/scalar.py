"""Exact scalar interval dynamic programming."""

from __future__ import annotations

import numpy as np

from scorequant._binstats import scatter_bin_statistics
from scorequant._execution import xp as jnp
from scorequant.config import ScalarDPConfig

from .common import QuantizerRun

# One dynamic-programming stripe materializes this many [stripe, n_states]
# temporaries, and the whole stripe set is held inside the byte budget.
_DYNAMIC_STRIPE_TEMPORARIES = 8
_DYNAMIC_WORKING_SET_BYTES = 64 * 1024 * 1024


def _dynamic_stripe_rows(n_states: int, item_size: int) -> int:
    """Return how many dynamic-programming stops one memory-bounded stripe holds.

    One stripe materializes a handful of ``[stripe, n_states]`` prefix-difference
    blocks, so the budget is divided by that temporary count rather than by one.
    """
    per_row = item_size * n_states * _DYNAMIC_STRIPE_TEMPORARIES
    return max(1, min(n_states, _DYNAMIC_WORKING_SET_BYTES // max(per_row, 1)))


def scalar_interval_dp(
    values: np.ndarray, weights: np.ndarray, n_bins: int
) -> tuple[np.ndarray, float]:
    """Solve exact one-dimensional weighted interval k-means by dynamic programming.

    On a scalar score law an optimal hard partition has ordered interval cells,
    so the global optimum is the minimal total weighted within-segment squared
    error over ``n_bins`` consecutive segments of the sorted values. Prefix sums
    turn every segment cost into a constant-time expression, and each dynamic
    stage evaluates whole blocks of stop/split pairs at once, so the quadratic
    recursion runs in a handful of memory-bounded stripes instead of one Python
    iteration per stop.

    Parameters
    ----------
    values
        Finite scalar coordinates with shape ``[N]``.
    weights
        Finite nonnegative weights with shape ``[N]``.
    n_bins
        Number of requested interval cells.

    Returns
    -------
    tuple
        Integer labels aligned with ``values`` and the minimal weighted
        within-segment squared error.
    """
    n_rows = int(values.shape[0])
    if n_bins > n_rows:
        raise ValueError("scalar dynamic programming requires n_bins <= the number of atoms")
    order = np.argsort(values, kind="stable")
    ordered_values = values[order]
    ordered_weights = weights[order]
    prefix_weight = np.r_[0.0, np.cumsum(ordered_weights)]
    prefix_sum = np.r_[0.0, np.cumsum(ordered_weights * ordered_values)]
    prefix_square = np.r_[0.0, np.cumsum(ordered_weights * ordered_values**2)]
    # ``previous`` is the completed stage of the recursion; only one stage and
    # the predecessor table are retained, so storage stays O(n_bins * n_rows).
    previous = np.full(n_rows + 1, np.inf)
    previous[0] = 0.0
    predecessor = np.zeros((n_bins + 1, n_rows + 1), dtype=np.int32)
    stripe = _dynamic_stripe_rows(n_rows + 1, prefix_weight.dtype.itemsize)
    for bin_count in range(1, n_bins + 1):
        current = np.full(n_rows + 1, np.inf)
        first_start = bin_count - 1
        for begin in range(bin_count, n_rows + 1, stripe):
            end = min(begin + stripe, n_rows + 1)
            stops = np.arange(begin, end)
            # A stop of ``end - 1`` admits no split point beyond ``end - 2``, so
            # the block is cut to the columns this stripe can actually use.
            columns = np.arange(first_start, end - 1)
            admissible = columns[None, :] < stops[:, None]
            segment_weight = prefix_weight[stops, None] - prefix_weight[None, columns]
            segment_sum = prefix_sum[stops, None] - prefix_sum[None, columns]
            segment_square = prefix_square[stops, None] - prefix_square[None, columns]
            # A zero-weight segment carries no measure, so its exact cost is
            # zero; the substituted denominator only avoids a spurious divide.
            safe_weight = np.where(segment_weight > 0, segment_weight, 1.0)
            costs = segment_square - segment_sum**2 / safe_weight
            candidates = np.where(admissible, previous[None, columns] + costs, np.inf)
            selected = np.argmin(candidates, axis=1)
            current[begin:end] = candidates[np.arange(end - begin), selected]
            predecessor[bin_count, begin:end] = first_start + selected
        previous = current
    objective = float(previous[n_rows])
    if not np.isfinite(objective):
        raise ValueError("scalar dynamic programming found no feasible interval partition")
    ordered_labels = np.empty(n_rows, dtype=np.int32)
    stop = n_rows
    for label in range(n_bins - 1, -1, -1):
        start = int(predecessor[label + 1, stop])
        ordered_labels[start:stop] = label
        stop = start
    labels = np.empty(n_rows, dtype=np.int32)
    labels[order] = ordered_labels
    return labels, objective


def scalar_weighted_kmeans_dp(
    points: jnp.ndarray,
    weights: jnp.ndarray,
    n_bins: int,
    config: ScalarDPConfig,
) -> QuantizerRun:
    """Solve one-dimensional weighted interval k-means exactly by dynamic programming."""
    rank = int(points.shape[1]) if points.ndim == 2 else 0
    if rank != 1:
        raise ValueError(
            "scalar dynamic programming requires an effective score rank of one, got "
            f"rank {rank}; reduce the score dimension or choose another solver"
        )
    n_rows = int(points.shape[0])
    if n_rows > config.max_rows:
        raise ValueError(
            f"scalar dynamic programming received {n_rows} distinct rows, "
            f"exceeding max_rows={config.max_rows}"
        )
    labels, objective = scalar_interval_dp(
        np.asarray(points[:, 0], dtype=np.float64),
        np.asarray(weights, dtype=np.float64),
        n_bins,
    )
    label_array = jnp.asarray(labels)
    statistics = scatter_bin_statistics(label_array, weights, points, n_bins)
    centers = statistics.means
    return QuantizerRun(
        centers=centers,
        steps=[0],
        center_history=[centers],
        objective_history=[objective],
        bin_weight_history=[statistics.weights],
        objective_label="whitened_sse",
    )
