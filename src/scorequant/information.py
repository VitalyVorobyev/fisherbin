"""Fisher information calculations and invariant-rich diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

import jax.numpy as jnp
import numpy as np

from ._typing import ArrayLike
from ._validation import _ValidatedSample, validate_sample
from .result import InformationReport, ProfiledInformationReport
from .transforms import fisher_transform


def fisher_information(scores: ArrayLike, weights: ArrayLike | None = None) -> jnp.ndarray:
    """Estimate unbinned Fisher information.

    Parameters
    ----------
    scores
        Finite score matrix with shape ``[N, P]``.
    weights
        Optional finite, nonnegative weights with shape ``[N]``.

    Returns
    -------
    jax.Array
        Matrix ``sum_i w_i s_i s_i.T`` with shape ``[P, P]``.
    """
    sample = validate_sample(scores, weights)
    return _unbinned_fisher(sample)


def _unbinned_fisher(sample: _ValidatedSample) -> jnp.ndarray:
    return jnp.einsum(
        "n,np,nq->pq",
        sample.effective_weights,
        sample.effective_scores,
        sample.effective_scores,
    )


def _validate_hard_assignments(
    sample: _ValidatedSample,
    assignments: ArrayLike,
    n_bins: int | None,
) -> tuple[jnp.ndarray, int]:
    labels = jnp.asarray(assignments)
    if labels.shape != (sample.scores.shape[0],):
        raise ValueError(
            f"assignments must have shape [{sample.scores.shape[0]}], got {labels.shape}"
        )
    if not jnp.issubdtype(labels.dtype, jnp.integer):
        raise TypeError("assignments must contain integer bin labels")
    labels = labels[sample.positive_weight_mask]
    if n_bins is None:
        resolved_n_bins = int(np.asarray(jnp.max(labels))) + 1
    else:
        if isinstance(n_bins, bool) or not isinstance(n_bins, int):
            raise TypeError("n_bins must be an integer")
        resolved_n_bins = n_bins
    if resolved_n_bins < 1:
        raise ValueError("n_bins must be at least one")
    if bool(np.asarray(jnp.any((labels < 0) | (labels >= resolved_n_bins)))):
        raise ValueError("assignments contain a label outside [0, n_bins)")
    return labels, resolved_n_bins


@dataclass(frozen=True, slots=True)
class _HardBinStatistics:
    fisher: jnp.ndarray
    weights: jnp.ndarray
    counts: jnp.ndarray
    effective_sample_sizes: jnp.ndarray


def _hard_binned_fisher(
    sample: _ValidatedSample,
    labels: jnp.ndarray,
    n_bins: int,
) -> tuple[jnp.ndarray, jnp.ndarray]:
    scores = sample.effective_scores
    weights = sample.effective_weights
    weighted_scores = weights[:, None] * scores
    bin_weights = jnp.zeros(n_bins, dtype=scores.dtype).at[labels].add(weights)
    bin_score_sums = jnp.zeros((n_bins, scores.shape[1]), dtype=scores.dtype)
    bin_score_sums = bin_score_sums.at[labels].add(weighted_scores)
    safe_weights = jnp.where(bin_weights > 0, bin_weights, 1)
    means = bin_score_sums / safe_weights[:, None]
    fisher = jnp.einsum("b,bp,bq->pq", bin_weights, means, means)
    return fisher, bin_weights


def _hard_bin_statistics(
    sample: _ValidatedSample,
    labels: jnp.ndarray,
    n_bins: int,
) -> _HardBinStatistics:
    fisher, bin_weights = _hard_binned_fisher(sample, labels, n_bins)
    weights = sample.effective_weights
    bin_counts = jnp.zeros(n_bins, dtype=jnp.int32).at[labels].add(1)
    squared_weights = jnp.zeros(n_bins, dtype=weights.dtype).at[labels].add(weights**2)
    effective = jnp.where(squared_weights > 0, bin_weights**2 / squared_weights, 0)
    return _HardBinStatistics(
        fisher=fisher,
        weights=bin_weights,
        counts=bin_counts,
        effective_sample_sizes=effective,
    )


def binned_fisher_information(
    scores: ArrayLike,
    assignments: ArrayLike,
    weights: ArrayLike | None = None,
    *,
    n_bins: int | None = None,
) -> jnp.ndarray:
    """Estimate Fisher information retained by hard bin counts.

    Parameters
    ----------
    scores
        Finite score matrix with shape ``[N, P]``.
    assignments
        Integer bin label for every input row, with shape ``[N]``.
    weights
        Optional finite, nonnegative weights with shape ``[N]``.
    n_bins
        Total number of bins. Inferred from the largest effective label when
        omitted; provide it explicitly to preserve trailing empty bins.

    Returns
    -------
    jax.Array
        Hard-binned Fisher matrix with shape ``[P, P]``.
    """
    sample = validate_sample(scores, weights)
    labels, resolved_n_bins = _validate_hard_assignments(sample, assignments, n_bins)
    fisher, _ = _hard_binned_fisher(sample, labels, resolved_n_bins)
    return fisher


def fractional_fisher_information(
    scores: ArrayLike,
    responsibilities: ArrayLike,
    weights: ArrayLike | None = None,
) -> jnp.ndarray:
    """Estimate Fisher information retained by fractional assignments.

    Parameters
    ----------
    scores
        Finite score matrix with shape ``[N, P]``.
    responsibilities
        Finite nonnegative responsibilities with shape ``[N, B]`` whose
        effective rows sum to one.
    weights
        Optional finite, nonnegative weights with shape ``[N]``.

    Returns
    -------
    jax.Array
        Fractionally binned Fisher matrix with shape ``[P, P]``.
    """
    sample = validate_sample(scores, weights)
    resp = jnp.asarray(responsibilities, dtype=sample.scores.dtype)
    if resp.ndim != 2 or resp.shape[0] != sample.scores.shape[0] or resp.shape[1] == 0:
        raise ValueError("responsibilities must have shape [N, B] with B >= 1")
    resp = resp[sample.positive_weight_mask]
    if not bool(np.asarray(jnp.all(jnp.isfinite(resp)))) or bool(np.asarray(jnp.any(resp < 0))):
        raise ValueError("responsibilities must be finite and nonnegative")
    if not bool(np.asarray(jnp.allclose(jnp.sum(resp, axis=1), 1, rtol=1e-5, atol=1e-7))):
        raise ValueError("responsibility rows must sum to one")
    weighted_resp = sample.effective_weights[:, None] * resp
    bin_weights = jnp.sum(weighted_resp, axis=0)
    bin_score_sums = weighted_resp.T @ sample.effective_scores
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
    scores: ArrayLike,
    assignments: ArrayLike,
    weights: ArrayLike | None = None,
    *,
    n_bins: int | None = None,
    rank_rtol: float | None = None,
) -> InformationReport:
    """Build retained-information and occupancy diagnostics for hard bins.

    Parameters
    ----------
    scores
        Finite score matrix with shape ``[N, P]``.
    assignments
        Integer bin label for every input row, with shape ``[N]``.
    weights
        Optional finite, nonnegative weights with shape ``[N]``.
    n_bins
        Total number of bins, including empty bins. Inferred when omitted.
    rank_rtol
        Relative threshold used to select informative Fisher directions.

    Returns
    -------
    InformationReport
        Unregularized Fisher matrices, normalized retention, spectrum, and
        per-bin occupancy diagnostics.
    """
    sample = validate_sample(scores, weights)
    labels, resolved_n_bins = _validate_hard_assignments(sample, assignments, n_bins)
    statistics = _hard_bin_statistics(sample, labels, resolved_n_bins)
    return _report_from_fishers(
        _unbinned_fisher(sample),
        statistics.fisher,
        statistics.weights,
        statistics.counts,
        statistics.effective_sample_sizes,
        rank_rtol=rank_rtol,
    )


def _profiled_blocks(
    information: jnp.ndarray, interest: tuple[int, ...]
) -> tuple[jnp.ndarray, jnp.ndarray, tuple[int, ...]]:
    dimension = information.shape[0]
    if any(index >= dimension for index in interest):
        raise ValueError(f"interest indices must be smaller than score dimension {dimension}")
    nuisance = tuple(index for index in range(dimension) if index not in set(interest))
    if not nuisance:
        raise ValueError("profiled D requires at least one nuisance score column; use DOptimality")
    interest_indices = jnp.asarray(interest)
    nuisance_indices = jnp.asarray(nuisance)
    interest_block = information[jnp.ix_(interest_indices, interest_indices)]
    cross_block = information[jnp.ix_(interest_indices, nuisance_indices)]
    nuisance_block = information[jnp.ix_(nuisance_indices, nuisance_indices)]
    nuisance_sign, _ = jnp.linalg.slogdet(nuisance_block)
    if float(np.asarray(nuisance_sign)) <= 0:
        raise ValueError("profiled D requires nonsingular nuisance information")
    schur = interest_block - cross_block @ jnp.linalg.solve(nuisance_block, cross_block.T)
    return 0.5 * (schur + schur.T), nuisance_block, nuisance


def profiled_information_report(
    scores: ArrayLike,
    assignments: ArrayLike,
    *,
    interest: tuple[int, ...],
    weights: ArrayLike | None = None,
    n_bins: int | None = None,
) -> ProfiledInformationReport:
    r"""Build same-label profiled-\(D_s\) diagnostics without regularization.

    Parameters
    ----------
    scores
        Finite score matrix with shape ``[N, P]`` in the declared parameter order.
    assignments
        Integer bin label for every input row.
    interest
        Unique nonnegative score-column indices for parameters of interest.
    weights
        Optional nonnegative measure weights.
    n_bins
        Total number of bins, including empty bins.

    Returns
    -------
    ProfiledInformationReport
        Full-data and same-label Schur information plus determinant retention.
    """
    if not interest or len(set(interest)) != len(interest) or any(index < 0 for index in interest):
        raise ValueError("interest must contain unique nonnegative indices")
    sample = validate_sample(scores, weights)
    labels, resolved_n_bins = _validate_hard_assignments(sample, assignments, n_bins)
    binned, _ = _hard_binned_fisher(sample, labels, resolved_n_bins)
    unbinned = _unbinned_fisher(sample)
    schur_unbinned, nuisance_unbinned, nuisance = _profiled_blocks(unbinned, interest)
    schur_binned, nuisance_binned, _ = _profiled_blocks(binned, interest)
    binned_sign, binned_logdet = jnp.linalg.slogdet(schur_binned)
    unbinned_sign, unbinned_logdet = jnp.linalg.slogdet(schur_unbinned)
    if float(np.asarray(unbinned_sign)) <= 0:
        raise ValueError("full-data profiled information is singular")
    interest_rank = int(np.linalg.matrix_rank(np.asarray(schur_binned)))
    nuisance_rank = int(np.linalg.matrix_rank(np.asarray(nuisance_binned)))
    if float(np.asarray(binned_sign)) <= 0:
        objective = float("-inf")
        logdet_retention = float("-inf")
        retention = 0.0
    else:
        objective = float(np.asarray(binned_logdet))
        logdet_retention = objective - float(np.asarray(unbinned_logdet))
        retention = float(np.exp(logdet_retention / len(interest)))
    return ProfiledInformationReport(
        interest=interest,
        nuisance=nuisance,
        schur_unbinned=schur_unbinned,
        schur_binned=schur_binned,
        nuisance_unbinned=nuisance_unbinned,
        nuisance_binned=nuisance_binned,
        objective=objective,
        logdet_retention=logdet_retention,
        geometric_mean_retention=retention,
        interest_rank=interest_rank,
        nuisance_rank=nuisance_rank,
    )


def efficient_scores(
    scores: ArrayLike,
    *,
    interest: tuple[int, ...],
    weights: ArrayLike | None = None,
) -> jnp.ndarray:
    """Project scores with the full-information nuisance regression.

    This constructs the explicit lower-dimensional upper problem for profiled
    information. Quantizing the result with ordinary D-optimality is not the
    same finite task as profiling nuisance from the resulting labels.

    Parameters
    ----------
    scores
        Finite score matrix in the declared parameter order.
    interest
        Unique nonnegative score-column indices for parameters of interest.
    weights
        Optional nonnegative reference-measure weights used for the full
        information regression.

    Returns
    -------
    jax.Array
        Full-information efficient scores with shape ``[N, len(interest)]``.
    """
    if not interest or len(set(interest)) != len(interest) or any(index < 0 for index in interest):
        raise ValueError("interest must contain unique nonnegative indices")
    sample = validate_sample(scores, weights)
    dimension = sample.scores.shape[1]
    if any(index >= dimension for index in interest):
        raise ValueError(f"interest indices must be smaller than score dimension {dimension}")
    interest_set = set(interest)
    nuisance = tuple(index for index in range(dimension) if index not in interest_set)
    if not nuisance:
        raise ValueError("efficient-score projection requires at least one nuisance column")
    information = _unbinned_fisher(sample)
    interest_indices = jnp.asarray(interest)
    nuisance_indices = jnp.asarray(nuisance)
    cross = information[jnp.ix_(interest_indices, nuisance_indices)]
    nuisance_information = information[jnp.ix_(nuisance_indices, nuisance_indices)]
    sign, _ = jnp.linalg.slogdet(nuisance_information)
    if float(np.asarray(sign)) <= 0:
        raise ValueError("efficient-score projection requires nonsingular nuisance information")
    nuisance_coefficients = jnp.linalg.solve(nuisance_information, cross.T)
    return (
        sample.scores[:, interest_indices]
        - sample.scores[:, nuisance_indices] @ nuisance_coefficients
    )
