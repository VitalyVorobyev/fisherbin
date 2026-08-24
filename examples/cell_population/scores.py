"""Calibrated classifier-to-score bridge for the FlowCyt example."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

from .data import (
    CLASS_NAMES,
    REFERENCE_FOLDS,
    FlowCytData,
    RobustArcsinhTransform,
    deterministic_group_sample,
)


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values, axis=1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / np.sum(exponentials, axis=1, keepdims=True)


def _temperature_scale(probabilities: np.ndarray, temperature: float) -> np.ndarray:
    clipped = np.clip(probabilities, 1e-12, 1.0)
    return _softmax(np.log(clipped) / temperature)


def _balanced_row_weights(labels: np.ndarray, patients: np.ndarray) -> np.ndarray:
    weights = np.zeros(len(labels), dtype=np.float64)
    groups = 0
    for patient in np.unique(patients):
        for label in range(len(CLASS_NAMES)):
            mask = (patients == patient) & (labels == label)
            count = int(np.count_nonzero(mask))
            if count:
                weights[mask] = 1.0 / count
                groups += 1
    if groups == 0:
        raise ValueError("cannot balance an empty labeled sample")
    return weights * (len(weights) / np.sum(weights))


def _balanced_log_loss(
    probabilities: np.ndarray,
    labels: np.ndarray,
    patients: np.ndarray,
    temperature: float,
) -> float:
    calibrated = _temperature_scale(probabilities, temperature)
    weights = _balanced_row_weights(labels, patients)
    losses = -np.log(np.clip(calibrated[np.arange(len(labels)), labels], 1e-12, 1.0))
    return float(np.average(losses, weights=weights))


def _fit_temperature(
    probabilities: np.ndarray,
    labels: np.ndarray,
    patients: np.ndarray,
) -> float:
    """Minimize balanced multiclass log loss with deterministic golden-section search."""
    left, right = np.log(0.25), np.log(4.0)
    golden = (np.sqrt(5.0) - 1.0) / 2.0
    x1 = right - golden * (right - left)
    x2 = left + golden * (right - left)
    f1 = _balanced_log_loss(probabilities, labels, patients, float(np.exp(x1)))
    f2 = _balanced_log_loss(probabilities, labels, patients, float(np.exp(x2)))
    for _ in range(48):
        if f1 <= f2:
            right, x2, f2 = x2, x1, f1
            x1 = right - golden * (right - left)
            f1 = _balanced_log_loss(probabilities, labels, patients, float(np.exp(x1)))
        else:
            left, x1, f1 = x1, x2, f2
            x2 = left + golden * (right - left)
            f2 = _balanced_log_loss(probabilities, labels, patients, float(np.exp(x2)))
    return float(np.exp((left + right) / 2.0))


@dataclass(frozen=True, slots=True)
class ScoreModel:
    """Frozen preprocessing, classifier ensemble, and probability calibration."""

    transform: RobustArcsinhTransform
    classifiers: tuple[HistGradientBoostingClassifier, ...]
    temperature: float
    training_prior: np.ndarray

    def predict_proba(self, features: np.ndarray) -> np.ndarray:
        """Predict calibrated uniform-prior class posteriors."""
        transformed = self.transform.apply(features)
        predictions = [
            _temperature_scale(classifier.predict_proba(transformed), self.temperature)
            for classifier in self.classifiers
        ]
        probabilities = np.mean(predictions, axis=0)
        probabilities /= np.sum(probabilities, axis=1, keepdims=True)
        return probabilities

    def likelihood_ratios(self, features: np.ndarray) -> np.ndarray:
        """Return component density ratios up to a common event-wise factor."""
        probabilities = self.predict_proba(features)
        return probabilities / self.training_prior[None, :]


@dataclass(frozen=True, slots=True)
class ScoreFit:
    """Return the frozen score model and calibrated out-of-fold predictions."""

    model: ScoreModel
    out_of_fold_probabilities: np.ndarray


def fit_score_model(
    reference: FlowCytData,
    *,
    max_per_patient_class: int = 2_000,
    max_iter: int = 120,
    seed: int = 2026,
) -> ScoreFit:
    """Fit a patient-cross-fitted density-ratio model on labeled references."""
    transform = RobustArcsinhTransform.fit(reference.features)
    transformed_all = transform.apply(reference.features)
    out_of_fold = np.full((len(reference.labels), len(CLASS_NAMES)), np.nan)
    classifiers: list[HistGradientBoostingClassifier] = []

    reference_patients = set(int(value) for value in np.unique(reference.patients))
    folds = [
        tuple(patient for patient in fold if patient in reference_patients)
        for fold in REFERENCE_FOLDS
    ]
    folds = [fold for fold in folds if fold]
    if len(folds) < 2:
        raise ValueError("score cross-fitting requires patients from at least two reference folds")

    for fold_index, held_out_patients in enumerate(folds):
        train_mask = ~np.isin(reference.patients, held_out_patients)
        held_out_mask = np.isin(reference.patients, held_out_patients)
        training = deterministic_group_sample(
            reference.select(train_mask),
            max_per_patient_class=max_per_patient_class,
            seed=seed + fold_index,
        )
        classifier = HistGradientBoostingClassifier(
            learning_rate=0.08,
            max_iter=max_iter,
            max_leaf_nodes=31,
            l2_regularization=1e-3,
            early_stopping=False,
            random_state=seed + fold_index,
        )
        classifier.fit(
            transform.apply(training.features),
            training.labels,
            sample_weight=_balanced_row_weights(training.labels, training.patients),
        )
        if tuple(int(value) for value in classifier.classes_) != tuple(range(len(CLASS_NAMES))):
            raise ValueError("every classifier fold must contain all six classes")
        out_of_fold[held_out_mask] = classifier.predict_proba(transformed_all[held_out_mask])
        classifiers.append(classifier)

    if not np.isfinite(out_of_fold).all():
        raise ValueError("every reference patient must receive an out-of-fold prediction")
    temperature = _fit_temperature(out_of_fold, reference.labels, reference.patients)
    calibrated = _temperature_scale(out_of_fold, temperature)
    prior = np.full(len(CLASS_NAMES), 1.0 / len(CLASS_NAMES), dtype=np.float64)
    return ScoreFit(
        model=ScoreModel(transform, tuple(classifiers), temperature, prior),
        out_of_fold_probabilities=calibrated,
    )


def reference_composition(labels: np.ndarray, patients: np.ndarray) -> np.ndarray:
    """Compute the equal-patient mean six-class composition."""
    compositions: list[np.ndarray] = []
    for patient in np.unique(patients):
        counts = np.bincount(labels[patients == patient], minlength=len(CLASS_NAMES))
        compositions.append(counts / np.sum(counts))
    result = np.mean(compositions, axis=0)
    if np.any(result <= 0):
        raise ValueError("every class must occur in the reference composition")
    return result / np.sum(result)


def mixture_scores(
    probabilities: np.ndarray,
    reference: np.ndarray,
    *,
    training_prior: np.ndarray | None = None,
) -> np.ndarray:
    """Convert calibrated class posteriors into five simplex score directions."""
    values = np.asarray(probabilities, dtype=np.float64)
    theta0 = np.asarray(reference, dtype=np.float64)
    if training_prior is None:
        prior = np.full(values.shape[1], 1.0 / values.shape[1])
    else:
        prior = np.asarray(training_prior, dtype=np.float64)
    if values.ndim != 2 or values.shape[1] != len(CLASS_NAMES):
        raise ValueError("probabilities must have shape [N, 6]")
    if theta0.shape != (len(CLASS_NAMES),) or prior.shape != theta0.shape:
        raise ValueError("reference and training_prior must have shape [6]")
    if np.any(values < 0) or np.any(theta0 <= 0) or np.any(prior <= 0):
        raise ValueError("probabilities, reference, and prior must be nonnegative/positive")
    ratios = np.clip(values, 1e-12, 1.0) / prior[None, :]
    density = ratios @ theta0
    scores = (ratios[:, :-1] - ratios[:, [-1]]) / density[:, None]
    if not np.isfinite(scores).all():
        raise ValueError("score construction produced non-finite values")
    return scores


def integration_weights(
    labels: np.ndarray,
    patients: np.ndarray,
    reference: np.ndarray,
) -> np.ndarray:
    """Weight rows so patients are equal within class and class mass is ``reference``."""
    weights = np.zeros(len(labels), dtype=np.float64)
    for label in range(len(CLASS_NAMES)):
        present = [
            patient
            for patient in np.unique(patients)
            if np.any((patients == patient) & (labels == label))
        ]
        if not present:
            raise ValueError(f"class {label} has no integration rows")
        for patient in present:
            mask = (patients == patient) & (labels == label)
            weights[mask] = reference[label] / (len(present) * np.count_nonzero(mask))
    return weights
