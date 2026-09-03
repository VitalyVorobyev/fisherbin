"""Private nearest-center prediction kernel shared by results and artifacts.

Leaf module: it depends only on ``_chunking`` and ``_execution``, so both the
deployable :mod:`scorequant.artifact` layer and the fitting
:mod:`scorequant.result` layer can import it without pulling the other in.
"""

from __future__ import annotations

from ._chunking import assignment_chunk_rows
from ._execution import backend_array
from ._execution import xp as jnp


def predict_distances(
    coordinates: jnp.ndarray, centers: jnp.ndarray, metric: jnp.ndarray | None
) -> jnp.ndarray:
    """Return the dense ``[chunk_rows, n_bins]`` assignment-distance table."""
    differences = coordinates[:, None, :] - centers[None, :, :]
    if metric is None:
        return jnp.sum(differences**2, axis=2)
    return jnp.einsum("nbr,rs,nbs->nb", differences, metric, differences)


def predict_labels(
    coordinates: jnp.ndarray, centers: jnp.ndarray, metric: jnp.ndarray | None
) -> jnp.ndarray:
    """Assign one chunk of rows to its nearest center."""
    return jnp.argmin(predict_distances(coordinates, centers, metric), axis=1)


def chunked_predict_labels(
    coordinates: jnp.ndarray, centers: jnp.ndarray, metric: jnp.ndarray | None
) -> jnp.ndarray:
    """Assign every row to its nearest center in memory-bounded chunks.

    Bit-identical to the unchunked assignment: each row's distance and
    argmin are independent of every other row, so partitioning rows into
    chunks never materializes the full ``[n_rows, n_bins, rank]`` tensor and
    changes nothing about the arithmetic.

    Public results store canonical NumPy arrays, so the stored centers and
    metric are placed on the active backend once here. Without it the broadcast
    difference and its square would be evaluated by NumPy on every chunk even
    under the JAX backend, materializing host temporaries that the selected
    runtime is supposed to own.
    """
    coordinates = backend_array(coordinates)
    centers = backend_array(centers)
    if metric is not None:
        metric = backend_array(metric)
    n_rows = int(coordinates.shape[0])
    chunk_rows = assignment_chunk_rows(
        coordinates.dtype, n_rows, int(centers.shape[0]), coordinates.shape[1]
    )
    if chunk_rows >= n_rows:
        return predict_labels(coordinates, centers, metric)
    chunks = [
        predict_labels(coordinates[start : start + chunk_rows], centers, metric)
        for start in range(0, n_rows, chunk_rows)
    ]
    return jnp.concatenate(chunks)
