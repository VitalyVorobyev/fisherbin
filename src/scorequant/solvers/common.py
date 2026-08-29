"""Shared geometric-quantizer state and assignment kernels."""

from __future__ import annotations

from dataclasses import dataclass

from scorequant._chunking import assignment_chunk_rows
from scorequant._execution import scatter_add
from scorequant._execution import xp as jnp


@dataclass(slots=True)
class QuantizerRun:
    """Aggregate state returned by a private quantizer implementation.

    ``objective_label`` names the units of ``objective_history`` so that a
    reported trace is never read in the wrong convention: a within-segment
    squared error and a log determinant are both scalars but not comparable.
    """

    centers: jnp.ndarray
    steps: list[int]
    center_history: list[jnp.ndarray]
    objective_history: list[float]
    bin_weight_history: list[jnp.ndarray]
    objective_label: str = "whitened_sse"
    soft_retention_history: list[float] | None = None
    temperature_history: list[float] | None = None
    gradient_norm_history: list[float] | None = None


def squared_distances(points: jnp.ndarray, centers: jnp.ndarray) -> jnp.ndarray:
    """Return the dense ``[N, B]`` squared Euclidean distance matrix."""
    return jnp.sum((points[:, None, :] - centers[None, :, :]) ** 2, axis=2)


def hard_assign(points: jnp.ndarray, centers: jnp.ndarray) -> jnp.ndarray:
    """Assign each point to its nearest center.

    Materializes the dense ``[n_rows, n_bins, rank]`` distance tensor at
    once, so this stays the right choice inside ``jax.jit``- or
    ``jax.grad``-traced code (XLA fuses the reduction and never keeps the
    full tensor resident). For eager, inference-scale row counts, use
    ``chunked_hard_assign`` instead.
    """
    return jnp.argmin(squared_distances(points, centers), axis=1)


def chunked_hard_assign(points: jnp.ndarray, centers: jnp.ndarray) -> jnp.ndarray:
    """Assign each point to its nearest center in memory-bounded row chunks.

    Eager counterpart to ``hard_assign`` for inference- and diagnostic-scale
    row counts, where nothing traces or fuses the computation so the naive
    form would materialize the full ``[n_rows, n_bins, rank]`` tensor. Do not
    use this inside ``jax.jit`` or ``jax.grad``-traced code: the Python-level
    chunk loop would just unroll into an equivalent, larger traced graph.
    Chunking rows is bit-identical to the unchunked assignment because each
    row's distance and argmin are independent of every other row.
    """
    n_rows = int(points.shape[0])
    chunk_rows = assignment_chunk_rows(points.dtype, n_rows, int(centers.shape[0]), points.shape[1])
    if chunk_rows >= n_rows:
        return hard_assign(points, centers)
    chunks = [
        hard_assign(points[start : start + chunk_rows], centers)
        for start in range(0, n_rows, chunk_rows)
    ]
    return jnp.concatenate(chunks)


def _bin_weights(labels: jnp.ndarray, weights: jnp.ndarray, n_bins: int) -> jnp.ndarray:
    return scatter_add(jnp.zeros(n_bins, dtype=weights.dtype), labels, weights)
