"""Fisher eigenspace projection and optional whitening."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import jax.numpy as jnp
import numpy as np

from ._json import json_ready


def _default_rank_rtol(dtype: jnp.dtype) -> float:
    return 1e-10 if jnp.dtype(dtype) == jnp.float64 else 1e-5


@dataclass(frozen=True, slots=True)
class FisherTransform:
    """Projection onto informative Fisher directions, optionally whitened.

    Scores are never mean-centered. ``matrix`` maps raw score vectors from
    shape ``[..., P]`` to optimization coordinates ``[..., R]``.
    """

    matrix: jnp.ndarray
    eigenvectors: jnp.ndarray
    eigenvalues: jnp.ndarray
    retained_eigenvalues: jnp.ndarray
    rank_rtol: float
    threshold: float
    whiten: bool

    @property
    def input_dim(self) -> int:
        return int(self.matrix.shape[0])

    @property
    def rank(self) -> int:
        return int(self.matrix.shape[1])

    @property
    def dropped_directions(self) -> int:
        return self.input_dim - self.rank

    def apply(self, scores: Any) -> jnp.ndarray:
        """Map raw scores into the fitted informative coordinate system."""

        array = jnp.asarray(scores, dtype=self.matrix.dtype)
        if array.ndim != 2 or array.shape[1] != self.input_dim:
            raise ValueError(f"scores must have shape [N, {self.input_dim}], got {array.shape}")
        if not bool(np.asarray(jnp.all(jnp.isfinite(array)))):
            raise ValueError("scores must be finite")
        return array @ self.matrix

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible representation."""

        return json_ready(
            {
                "matrix": self.matrix,
                "eigenvectors": self.eigenvectors,
                "eigenvalues": self.eigenvalues,
                "retained_eigenvalues": self.retained_eigenvalues,
                "rank_rtol": self.rank_rtol,
                "threshold": self.threshold,
                "whiten": self.whiten,
                "rank": self.rank,
                "dropped_directions": self.dropped_directions,
            }
        )


def fisher_transform(
    fisher: Any,
    *,
    whiten: bool = True,
    rank_rtol: float | None = None,
) -> FisherTransform:
    """Construct an informative-subspace transform from a Fisher matrix."""

    matrix = jnp.asarray(fisher)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or matrix.shape[0] == 0:
        raise ValueError("fisher must be a non-empty square matrix")
    if not bool(np.asarray(jnp.all(jnp.isfinite(matrix)))):
        raise ValueError("fisher must be finite")
    matrix = 0.5 * (matrix + matrix.T)
    eigenvalues, eigenvectors = jnp.linalg.eigh(matrix)
    maximum = float(np.asarray(jnp.max(eigenvalues)))
    if maximum <= 0:
        raise ValueError("Fisher information has no positive informative direction")
    resolved_rtol = _default_rank_rtol(matrix.dtype) if rank_rtol is None else rank_rtol
    if not np.isfinite(resolved_rtol) or resolved_rtol < 0:
        raise ValueError("rank_rtol must be finite and nonnegative")
    threshold = resolved_rtol * maximum
    keep = np.asarray(eigenvalues > threshold)
    if not np.any(keep):
        raise ValueError("rank threshold removes every Fisher direction")
    basis = eigenvectors[:, keep]
    retained = eigenvalues[keep]
    transform_matrix = basis / jnp.sqrt(retained)[None, :] if whiten else basis
    return FisherTransform(
        matrix=transform_matrix,
        eigenvectors=eigenvectors,
        eigenvalues=eigenvalues,
        retained_eigenvalues=retained,
        rank_rtol=float(resolved_rtol),
        threshold=float(threshold),
        whiten=whiten,
    )
