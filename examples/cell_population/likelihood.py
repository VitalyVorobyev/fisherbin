"""Downstream mixture likelihoods consuming frozen hard labels."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .data import CLASS_NAMES


@dataclass(frozen=True, slots=True)
class MixtureEstimate:
    """Population fractions and local covariance from a frozen likelihood."""

    fractions: np.ndarray
    covariance: np.ndarray
    log_likelihood: float
    iterations: int
    converged: bool

    @property
    def standard_errors(self) -> np.ndarray:
        """Return marginal standard errors for all six fractions."""
        return np.sqrt(np.maximum(np.diag(self.covariance), 0.0))


def estimate_bin_templates(
    labels: np.ndarray,
    bins: np.ndarray,
    patients: np.ndarray,
    *,
    n_bins: int,
    alpha: float = 0.5,
) -> np.ndarray:
    """Estimate ``P(bin | class)`` by equal-patient averaging."""
    if n_bins < 1 or not np.isfinite(alpha) or alpha <= 0:
        raise ValueError("n_bins and alpha must be positive")
    labels_array = np.asarray(labels, dtype=np.int64)
    bins_array = np.asarray(bins, dtype=np.int64)
    patients_array = np.asarray(patients, dtype=np.int64)
    if labels_array.shape != bins_array.shape or labels_array.shape != patients_array.shape:
        raise ValueError("labels, bins, and patients must have matching shapes")
    if np.any((bins_array < 0) | (bins_array >= n_bins)):
        raise ValueError("bin labels are outside the declared range")

    templates = np.zeros((n_bins, len(CLASS_NAMES)), dtype=np.float64)
    for label in range(len(CLASS_NAMES)):
        patient_probabilities: list[np.ndarray] = []
        for patient in np.unique(patients_array):
            mask = (patients_array == patient) & (labels_array == label)
            if not np.any(mask):
                continue
            counts = np.bincount(bins_array[mask], minlength=n_bins).astype(np.float64)
            patient_probabilities.append((counts + alpha) / (np.sum(counts) + alpha * n_bins))
        if not patient_probabilities:
            raise ValueError(f"class {label} has no template rows")
        templates[:, label] = np.mean(patient_probabilities, axis=0)
    templates /= np.sum(templates, axis=0, keepdims=True)
    return templates


def _initial_fractions(initial: np.ndarray | None, n_classes: int) -> np.ndarray:
    if initial is None:
        return np.full(n_classes, 1.0 / n_classes, dtype=np.float64)
    fractions = np.asarray(initial, dtype=np.float64)
    if (
        fractions.shape != (n_classes,)
        or np.any(fractions <= 0)
        or not np.isfinite(fractions).all()
    ):
        raise ValueError("initial fractions must be finite, positive, and have shape [K]")
    return fractions / np.sum(fractions)


def _full_covariance(information: np.ndarray) -> np.ndarray:
    covariance_free = np.linalg.pinv(information, rtol=1e-10, hermitian=True)
    n_free = information.shape[0]
    jacobian = np.vstack([np.eye(n_free), -np.ones((1, n_free))])
    covariance = jacobian @ covariance_free @ jacobian.T
    return (covariance + covariance.T) / 2.0


def fit_binned_mixture(
    counts: np.ndarray,
    templates: np.ndarray,
    *,
    initial: np.ndarray | None = None,
    tolerance: float = 1e-8,
    max_iter: int = 10_000,
) -> MixtureEstimate:
    """Fit six population fractions from hard-bin counts with deterministic EM."""
    observed = np.asarray(counts, dtype=np.float64)
    matrix = np.asarray(templates, dtype=np.float64)
    if observed.ndim != 1 or matrix.shape != (len(observed), len(CLASS_NAMES)):
        raise ValueError("templates must have shape [n_bins, 6]")
    if np.any(observed < 0) or not np.isfinite(observed).all() or np.sum(observed) <= 0:
        raise ValueError("counts must be finite, nonnegative, and have positive total")
    if np.any(matrix <= 0) or not np.isfinite(matrix).all():
        raise ValueError("smoothed templates must be finite and strictly positive")

    fractions = _initial_fractions(initial, matrix.shape[1])
    converged = False
    for _completed_iterations in range(1, max_iter + 1):
        probabilities = matrix @ fractions
        expected_class_counts = np.sum(
            observed[:, None] * matrix * fractions[None, :] / probabilities[:, None], axis=0
        )
        updated = expected_class_counts / np.sum(observed)
        if np.max(np.abs(updated - fractions)) <= tolerance:
            fractions = updated
            converged = True
            break
        fractions = updated

    probabilities = matrix @ fractions
    log_likelihood = float(np.sum(observed * np.log(probabilities)))
    contrast = matrix[:, :-1] - matrix[:, [-1]]
    information = np.sum(observed) * (contrast.T @ (contrast / probabilities[:, None]))
    return MixtureEstimate(
        fractions=fractions,
        covariance=_full_covariance(information),
        log_likelihood=log_likelihood,
        iterations=_completed_iterations,
        converged=converged,
    )


def fit_unbinned_mixture(
    likelihood_ratios: np.ndarray,
    *,
    initial: np.ndarray | None = None,
    tolerance: float = 1e-8,
    max_iter: int = 10_000,
) -> MixtureEstimate:
    """Fit fractions from unbinned component density ratios with deterministic EM."""
    ratios = np.asarray(likelihood_ratios, dtype=np.float64)
    if ratios.ndim != 2 or ratios.shape[1] != len(CLASS_NAMES):
        raise ValueError("likelihood_ratios must have shape [N, 6]")
    if np.any(ratios <= 0) or not np.isfinite(ratios).all() or len(ratios) == 0:
        raise ValueError("likelihood ratios must be finite, positive, and nonempty")

    fractions = _initial_fractions(initial, ratios.shape[1])
    converged = False
    for _completed_iterations in range(1, max_iter + 1):
        densities = ratios @ fractions
        responsibilities = ratios * fractions[None, :] / densities[:, None]
        updated = np.mean(responsibilities, axis=0)
        if np.max(np.abs(updated - fractions)) <= tolerance:
            fractions = updated
            converged = True
            break
        fractions = updated

    densities = ratios @ fractions
    contrast = ratios[:, :-1] - ratios[:, [-1]]
    scaled = contrast / densities[:, None]
    information = scaled.T @ scaled
    return MixtureEstimate(
        fractions=fractions,
        covariance=_full_covariance(information),
        log_likelihood=float(np.sum(np.log(densities))),
        iterations=_completed_iterations,
        converged=converged,
    )
