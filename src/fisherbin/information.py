"""Fisher information calculations and invariant-rich diagnostics."""

from __future__ import annotations

from typing import Any

import jax.numpy as jnp
import numpy as np

from ._validation import validate_scores_weights
from .result import InformationReport
from .transforms import fisher_transform


def fisher_information(scores: Any, weights: Any | None = None) -> jnp.ndarray:
    """Estimate unbinned Fisher information ``sum_i w_i s_i s_i.T``."""

    score_array, weight_array = validate_scores_weights(scores, weights)
    return jnp.einsum("n,np,nq->pq", weight_array, score_array, score_array)


def _raw_weight_mask(scores: Any, weights: Any | None) -> jnp.ndarray:
    n = jnp.asarray(scores).shape[0]
    return jnp.ones(n, dtype=bool) if weights is None else jnp.asarray(weights) > 0


def binned_fisher_information(
    scores: Any,
    assignments: Any,
    weights: Any | None = None,
    *,
    n_bins: int | None = None,
) -> jnp.ndarray:
    """Estimate Fisher information retained by hard bin counts."""

    raw_scores = jnp.asarray(scores)
    mask = _raw_weight_mask(raw_scores, weights)
    score_array, weight_array = validate_scores_weights(raw_scores, weights)
    labels = jnp.asarray(assignments)
    if labels.shape != (raw_scores.shape[0],):
        raise ValueError(f"assignments must have shape [{raw_scores.shape[0]}], got {labels.shape}")
    labels = labels[mask]
    if not jnp.issubdtype(labels.dtype, jnp.integer):
        raise TypeError("assignments must contain integer bin labels")
    if n_bins is None:
        n_bins = int(np.asarray(jnp.max(labels))) + 1
    if n_bins < 1:
        raise ValueError("n_bins must be at least one")
    if bool(np.asarray(jnp.any((labels < 0) | (labels >= n_bins)))):
        raise ValueError("assignments contain a label outside [0, n_bins)")
    weighted_scores = weight_array[:, None] * score_array
    bin_weights = jnp.zeros(n_bins, dtype=score_array.dtype).at[labels].add(weight_array)
    bin_score_sums = jnp.zeros((n_bins, score_array.shape[1]), dtype=score_array.dtype)
    bin_score_sums = bin_score_sums.at[labels].add(weighted_scores)
    safe_weights = jnp.where(bin_weights > 0, bin_weights, 1)
    means = bin_score_sums / safe_weights[:, None]
    return jnp.einsum("b,bp,bq->pq", bin_weights, means, means)


def fractional_fisher_information(
    scores: Any,
    responsibilities: Any,
    weights: Any | None = None,
) -> jnp.ndarray:
    """Estimate Fisher information retained by fractional bin assignments."""

    raw_scores = jnp.asarray(scores)
    mask = _raw_weight_mask(raw_scores, weights)
    score_array, weight_array = validate_scores_weights(raw_scores, weights)
    resp = jnp.asarray(responsibilities, dtype=score_array.dtype)
    if resp.ndim != 2 or resp.shape[0] != raw_scores.shape[0] or resp.shape[1] == 0:
        raise ValueError("responsibilities must have shape [N, B] with B >= 1")
    resp = resp[mask]
    if not bool(np.asarray(jnp.all(jnp.isfinite(resp)))) or bool(np.asarray(jnp.any(resp < 0))):
        raise ValueError("responsibilities must be finite and nonnegative")
    if not bool(np.asarray(jnp.allclose(jnp.sum(resp, axis=1), 1, rtol=1e-5, atol=1e-7))):
        raise ValueError("responsibility rows must sum to one")
    weighted_resp = weight_array[:, None] * resp
    bin_weights = jnp.sum(weighted_resp, axis=0)
    bin_score_sums = weighted_resp.T @ score_array
    safe_weights = jnp.where(bin_weights > 0, bin_weights, 1)
    means = bin_score_sums / safe_weights[:, None]
    return jnp.einsum("b,bp,bq->pq", bin_weights, means, means)


def _report_from_fishers(
    fisher_unbinned: jnp.ndarray,
    fisher_binned: jnp.ndarray,
    bin_weights: jnp.ndarray,
    bin_counts: jnp.ndarray,
    bin_effective_sample_sizes: jnp.ndarray,
    *,
    rank_rtol: float | None,
) -> InformationReport:
    transform = fisher_transform(fisher_unbinned, whiten=True, rank_rtol=rank_rtol)
    retained = transform.matrix.T @ fisher_binned @ transform.matrix
    retained = 0.5 * (retained + retained.T)
    eigenvalues = jnp.linalg.eigvalsh(retained)
    arithmetic = float(np.asarray(jnp.mean(eigenvalues)))
    if bool(np.asarray(jnp.any(eigenvalues <= 0))):
        geometric = 0.0
        logdet = float("-inf")
    else:
        logdet = float(np.asarray(jnp.sum(jnp.log(eigenvalues))))
        geometric = float(np.exp(logdet / transform.rank))
    residual = 0.5 * (fisher_unbinned - fisher_binned + (fisher_unbinned - fisher_binned).T)
    residual_min = float(np.asarray(jnp.min(jnp.linalg.eigvalsh(residual))))
    return InformationReport(
        fisher_unbinned=fisher_unbinned,
        fisher_binned=fisher_binned,
        retained_matrix=retained,
        retained_eigenvalues=eigenvalues,
        arithmetic_mean_retention=arithmetic,
        geometric_mean_retention=geometric,
        logdet_retention=logdet,
        bin_weights=bin_weights,
        bin_counts=bin_counts,
        bin_effective_sample_sizes=bin_effective_sample_sizes,
        effective_rank=transform.rank,
        rank_threshold=transform.threshold,
        psd_residual_min_eigenvalue=residual_min,
    )


def information_report(
    scores: Any,
    assignments: Any,
    weights: Any | None = None,
    *,
    n_bins: int | None = None,
    rank_rtol: float | None = None,
) -> InformationReport:
    """Build retained-information and occupancy diagnostics for hard bins."""

    raw_scores = jnp.asarray(scores)
    mask = _raw_weight_mask(raw_scores, weights)
    score_array, weight_array = validate_scores_weights(raw_scores, weights)
    labels = jnp.asarray(assignments)
    if labels.shape != (raw_scores.shape[0],):
        raise ValueError(f"assignments must have shape [{raw_scores.shape[0]}], got {labels.shape}")
    labels = labels[mask]
    if not jnp.issubdtype(labels.dtype, jnp.integer):
        raise TypeError("assignments must contain integer bin labels")
    if n_bins is None:
        n_bins = int(np.asarray(jnp.max(labels))) + 1
    if bool(np.asarray(jnp.any((labels < 0) | (labels >= n_bins)))):
        raise ValueError("assignments contain a label outside [0, n_bins)")
    fisher_unbinned = jnp.einsum("n,np,nq->pq", weight_array, score_array, score_array)
    fisher_binned = binned_fisher_information(raw_scores, assignments, weights, n_bins=n_bins)
    bin_weights = jnp.zeros(n_bins, dtype=score_array.dtype).at[labels].add(weight_array)
    bin_counts = jnp.zeros(n_bins, dtype=jnp.int32).at[labels].add(1)
    squared_weights = jnp.zeros(n_bins, dtype=score_array.dtype).at[labels].add(weight_array**2)
    effective = jnp.where(squared_weights > 0, bin_weights**2 / squared_weights, 0)
    return _report_from_fishers(
        fisher_unbinned,
        fisher_binned,
        bin_weights,
        bin_counts,
        effective,
        rank_rtol=rank_rtol,
    )
