"""End-to-end FlowCyt population-quantification experiment."""

from __future__ import annotations

import resource
import sys
from dataclasses import dataclass
from time import perf_counter

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

import fisherbin as fb

from .data import CLASS_NAMES, REFERENCE_PATIENTS, TEST_PATIENTS, FlowCytData
from .likelihood import estimate_bin_templates, fit_binned_mixture, fit_unbinned_mixture
from .scores import (
    fit_score_model,
    integration_weights,
    mixture_scores,
    reference_composition,
)


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    """Machine-readable metrics and arrays needed for documentation figures."""

    metrics: dict[str, object]
    true_fractions: np.ndarray
    predicted_fractions: dict[str, np.ndarray]
    bin_counts: tuple[int, ...]
    score_projection: np.ndarray
    projection_labels: np.ndarray
    projection_classes: np.ndarray
    predicted_standard_errors: np.ndarray
    bootstrap_standard_errors: np.ndarray
    patient_ids: np.ndarray


def _role_masks(data: FlowCytData) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    keys = data.source_rows + 17 * data.patients + 101 * data.labels
    roles = np.mod(keys, 4)
    return roles <= 1, roles == 2, roles == 3


def _cap_group_mask(
    data: FlowCytData,
    base_mask: np.ndarray,
    *,
    max_per_patient_class: int,
    seed: int,
) -> np.ndarray:
    """Cap computation rows without changing patient/class integration mass."""
    rng = np.random.default_rng(seed)
    selected = np.zeros(len(data.labels), dtype=bool)
    for patient in np.unique(data.patients):
        for label in range(len(CLASS_NAMES)):
            indices = np.flatnonzero(
                base_mask & (data.patients == patient) & (data.labels == label)
            )
            if len(indices) > max_per_patient_class:
                indices = np.sort(rng.choice(indices, size=max_per_patient_class, replace=False))
            selected[indices] = True
    return selected


def _calibration_metrics(
    probabilities: np.ndarray,
    labels: np.ndarray,
    patients: np.ndarray,
) -> dict[str, object]:
    """Summarize out-of-fold calibration with equal patient/class influence."""
    uniform = np.full(len(CLASS_NAMES), 1.0 / len(CLASS_NAMES))
    weights = integration_weights(labels, patients, uniform)
    confidence = np.max(probabilities, axis=1)
    predicted = np.argmax(probabilities, axis=1)
    correct = predicted == labels
    chosen = np.clip(probabilities[np.arange(len(labels)), labels], 1e-12, 1.0)
    one_hot = np.eye(len(CLASS_NAMES))[labels]
    edges = np.linspace(0.0, 1.0, 11)
    bins: list[dict[str, object]] = []
    calibration_error = 0.0
    for index, (lower, upper) in enumerate(zip(edges[:-1], edges[1:], strict=True)):
        mask = (confidence >= lower) & (
            (confidence <= upper) if index == len(edges) - 2 else (confidence < upper)
        )
        mass = float(np.sum(weights[mask]))
        if mass == 0:
            bins.append(
                {
                    "lower": float(lower),
                    "upper": float(upper),
                    "weight": 0.0,
                    "mean_confidence": None,
                    "accuracy": None,
                }
            )
            continue
        mean_confidence = float(np.average(confidence[mask], weights=weights[mask]))
        accuracy = float(np.average(correct[mask], weights=weights[mask]))
        calibration_error += mass * abs(accuracy - mean_confidence)
        bins.append(
            {
                "lower": float(lower),
                "upper": float(upper),
                "weight": mass,
                "mean_confidence": mean_confidence,
                "accuracy": accuracy,
            }
        )
    return {
        "balanced_log_loss": float(np.sum(weights * -np.log(chosen))),
        "balanced_brier_score": float(np.sum(weights[:, None] * (probabilities - one_hot) ** 2)),
        "balanced_accuracy": float(np.sum(weights * correct)),
        "expected_calibration_error": calibration_error,
        "reliability_bins": bins,
    }


def _peak_rss_megabytes() -> float:
    """Return process peak resident memory using platform-native units."""
    value = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value / (1024.0**2 if sys.platform == "darwin" else 1024.0)


def _nearest(points: np.ndarray, centers: np.ndarray) -> np.ndarray:
    distances = np.sum((points[:, None, :] - centers[None, :, :]) ** 2, axis=2)
    return np.argmin(distances, axis=1)


def predict_score_bins(
    result: fb.FitResult,
    scores: np.ndarray,
    *,
    chunk_size: int = 50_000,
) -> np.ndarray:
    """Predict a large score matrix without materializing all distances at once."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    labels = [
        np.asarray(result.predict(scores[start : start + chunk_size]))
        for start in range(0, len(scores), chunk_size)
    ]
    return np.concatenate(labels) if labels else np.empty(0, dtype=np.int64)


def _factor_pair(n_bins: int) -> tuple[int, int]:
    for first in range(int(np.sqrt(n_bins)), 0, -1):
        if n_bins % first == 0:
            return first, n_bins // first
    raise AssertionError("every positive integer has a factor pair")


def _grid_edges(values: np.ndarray, n_parts: int) -> np.ndarray:
    if n_parts == 1:
        return np.empty(0)
    return np.quantile(values, np.linspace(0, 1, n_parts + 1)[1:-1])


def _grid_labels(
    points: np.ndarray, first_edges: np.ndarray, second_edges: np.ndarray
) -> np.ndarray:
    first = np.digitize(points[:, 0], first_edges)
    second = np.digitize(points[:, 1], second_edges)
    return first * (len(second_edges) + 1) + second


def _true_patient_fractions(test: FlowCytData) -> tuple[np.ndarray, np.ndarray]:
    patients = np.unique(test.patients)
    fractions = []
    for patient in patients:
        counts = np.bincount(test.labels[test.patients == patient], minlength=len(CLASS_NAMES))
        fractions.append(counts / np.sum(counts))
    return patients, np.asarray(fractions)


def _fit_patient_fractions(
    test: FlowCytData,
    test_labels: np.ndarray,
    templates: np.ndarray,
    patients: np.ndarray,
) -> tuple[np.ndarray, dict[str, int]]:
    estimates = []
    for patient in patients:
        mask = test.patients == patient
        counts = np.bincount(test_labels[mask], minlength=templates.shape[0])
        estimates.append(fit_binned_mixture(counts, templates))
    return np.asarray([estimate.fractions for estimate in estimates]), {
        "converged_patients": sum(estimate.converged for estimate in estimates),
        "total_patients": len(estimates),
        "maximum_iterations": max(estimate.iterations for estimate in estimates),
    }


def _fit_unbinned_patient_fractions(
    test: FlowCytData,
    ratios: np.ndarray,
    patients: np.ndarray,
) -> tuple[np.ndarray, dict[str, int]]:
    estimates = [fit_unbinned_mixture(ratios[test.patients == patient]) for patient in patients]
    return np.asarray([estimate.fractions for estimate in estimates]), {
        "converged_patients": sum(estimate.converged for estimate in estimates),
        "total_patients": len(estimates),
        "maximum_iterations": max(estimate.iterations for estimate in estimates),
    }


def _bootstrap_uncertainty(
    test: FlowCytData,
    test_labels: np.ndarray,
    templates: np.ndarray,
    patients: np.ndarray,
    *,
    repeats: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    predicted_errors: list[np.ndarray] = []
    bootstrap_errors: list[np.ndarray] = []
    for patient in patients:
        labels = test_labels[test.patients == patient]
        counts = np.bincount(labels, minlength=templates.shape[0])
        fitted = fit_binned_mixture(counts, templates)
        draws = [
            fit_binned_mixture(
                rng.multinomial(len(labels), counts / np.sum(counts)), templates
            ).fractions
            for _ in range(repeats)
        ]
        predicted_errors.append(fitted.standard_errors)
        bootstrap_errors.append(np.std(draws, axis=0, ddof=1))
    return np.asarray(predicted_errors), np.asarray(bootstrap_errors)


def _summary_metrics(
    true_fractions: np.ndarray,
    predicted: np.ndarray,
    test_scores: np.ndarray,
    test_labels: np.ndarray,
    n_bins: int,
) -> dict[str, object]:
    errors = predicted - true_fractions
    per_class = np.sqrt(np.mean(errors**2, axis=0))
    report = fb.information_report(test_scores, test_labels, n_bins=n_bins)
    return {
        "target_macro_rmse": float(np.mean(per_class[:5])),
        "per_class_rmse": per_class.tolist(),
        "held_out_d_efficiency": report.geometric_mean_retention,
        "minimum_bin_count": int(np.min(np.bincount(test_labels, minlength=n_bins))),
    }


def _evaluate_partition(
    *,
    name: str,
    n_bins: int,
    reference: FlowCytData,
    template_mask: np.ndarray,
    template_labels: np.ndarray,
    test: FlowCytData,
    test_labels: np.ndarray,
    patients: np.ndarray,
    true_fractions: np.ndarray,
    test_scores: np.ndarray,
) -> tuple[str, dict[str, object], np.ndarray]:
    templates = estimate_bin_templates(
        reference.labels[template_mask],
        template_labels,
        reference.patients[template_mask],
        n_bins=n_bins,
    )
    predicted, convergence = _fit_patient_fractions(test, test_labels, templates, patients)
    metrics = _summary_metrics(true_fractions, predicted, test_scores, test_labels, n_bins)
    metrics["likelihood_convergence"] = convergence
    return name, metrics, predicted


def run_experiment(
    data: FlowCytData,
    *,
    bin_counts: tuple[int, ...] = (5, 8, 10, 15, 20, 30),
    quick: bool = False,
    seed: int = 2026,
) -> ExperimentResult:
    """Run the complete labels-blind held-out population experiment."""
    reference = data.patients_in(REFERENCE_PATIENTS)
    test = data.patients_in(TEST_PATIENTS)
    if len(reference.labels) == 0 or len(test.labels) == 0:
        raise ValueError("data must contain both declared reference and test patients")

    started = perf_counter()
    timings: dict[str, float] = {}
    score_started = perf_counter()
    score_fit = fit_score_model(
        reference,
        max_per_patient_class=256 if quick else 2_000,
        max_iter=35 if quick else 120,
        seed=seed,
    )
    theta0 = reference_composition(reference.labels, reference.patients)
    reference_scores = mixture_scores(
        score_fit.out_of_fold_probabilities,
        theta0,
        training_prior=score_fit.model.training_prior,
    )
    test_probabilities = score_fit.model.predict_proba(test.features)
    test_ratios = test_probabilities / score_fit.model.training_prior[None, :]
    test_scores = mixture_scores(
        test_probabilities,
        theta0,
        training_prior=score_fit.model.training_prior,
    )
    timings["score_model_and_scores"] = perf_counter() - score_started
    patients, true_fractions = _true_patient_fractions(test)
    unbinned, unbinned_convergence = _fit_unbinned_patient_fractions(test, test_ratios, patients)
    raw_partition_mask, raw_validation_mask, template_mask = _role_masks(reference)
    partition_mask = _cap_group_mask(
        reference,
        raw_partition_mask,
        max_per_patient_class=256 if quick else 512,
        seed=seed + 101,
    )
    validation_mask = _cap_group_mask(
        reference,
        raw_validation_mask,
        max_per_patient_class=128 if quick else 256,
        seed=seed + 102,
    )
    weights = integration_weights(
        reference.labels[partition_mask], reference.patients[partition_mask], theta0
    )

    transformed_markers = score_fit.model.transform.apply(reference.features)
    transformed_test_markers = score_fit.model.transform.apply(test.features)
    metrics_by_method: dict[str, object] = {
        "dataset": {
            "patient_compositions": [
                {
                    "patient": int(patient),
                    "split": "reference" if patient in REFERENCE_PATIENTS else "test",
                    "fractions": (
                        np.bincount(
                            data.labels[data.patients == patient], minlength=len(CLASS_NAMES)
                        )
                        / np.count_nonzero(data.patients == patient)
                    ).tolist(),
                }
                for patient in np.unique(data.patients)
            ],
            "class_names": list(CLASS_NAMES),
        },
        "unbinned": {
            "target_macro_rmse": float(
                np.mean(np.sqrt(np.mean((unbinned - true_fractions) ** 2, axis=0))[:5])
            ),
            "per_class_rmse": np.sqrt(np.mean((unbinned - true_fractions) ** 2, axis=0)).tolist(),
            "likelihood_convergence": unbinned_convergence,
        },
    }
    predicted_by_method: dict[str, np.ndarray] = {"unbinned": unbinned}
    final_projection = np.empty((0, 2))
    final_labels = np.empty(0, dtype=np.int64)
    predicted_standard_errors = np.empty((0, len(CLASS_NAMES)))
    bootstrap_standard_errors = np.empty((0, len(CLASS_NAMES)))

    for n_bins in bin_counts:
        bin_started = perf_counter()
        common = {
            "weights": weights,
            "n_bins": n_bins,
            "validation_scores": reference_scores[validation_mask],
            "validation_weights": integration_weights(
                reference.labels[validation_mask], reference.patients[validation_mask], theta0
            ),
        }
        kmeans_result = fb.fit_scores(
            reference_scores[partition_mask],
            config=fb.KMeansConfig(seed=seed, n_init=3 if quick else 8),
            **common,
        )
        soft_result = fb.fit_scores(
            reference_scores[partition_mask],
            config=fb.SoftVoronoiConfig(
                seed=seed,
                n_init=3 if quick else 4,
                max_steps=50 if quick else 160,
                record_every=10,
            ),
            **common,
        )

        for method, result in (("score_kmeans", kmeans_result), ("soft_voronoi", soft_result)):
            template_labels = np.asarray(result.predict(reference_scores[template_mask]))
            test_bin_labels = predict_score_bins(result, test_scores)
            key, values, predicted = _evaluate_partition(
                name=f"{method}:{n_bins}",
                n_bins=n_bins,
                reference=reference,
                template_mask=template_mask,
                template_labels=template_labels,
                test=test,
                test_labels=test_bin_labels,
                patients=patients,
                true_fractions=true_fractions,
                test_scores=test_scores,
            )
            values["validation_d_efficiency"] = result.validation_report.geometric_mean_retention
            metrics_by_method[key] = values
            predicted_by_method[key] = predicted

        marker_model = KMeans(n_clusters=n_bins, n_init=5, random_state=seed).fit(
            transformed_markers[partition_mask], sample_weight=weights
        )
        key, values, predicted = _evaluate_partition(
            name=f"marker_kmeans:{n_bins}",
            n_bins=n_bins,
            reference=reference,
            template_mask=template_mask,
            template_labels=marker_model.predict(transformed_markers[template_mask]),
            test=test,
            test_labels=marker_model.predict(transformed_test_markers),
            patients=patients,
            true_fractions=true_fractions,
            test_scores=test_scores,
        )
        metrics_by_method[key] = values
        predicted_by_method[key] = predicted

        fisher_matrix = (reference_scores[partition_mask] * weights[:, None]).T @ reference_scores[
            partition_mask
        ]
        eigenvalues, eigenvectors = np.linalg.eigh((fisher_matrix + fisher_matrix.T) / 2.0)
        direction = eigenvectors[:, np.argmax(eigenvalues)]
        projected_reference = reference_scores @ direction
        projected_test = test_scores @ direction
        edges = np.quantile(
            projected_reference[partition_mask], np.linspace(0, 1, n_bins + 1)[1:-1]
        )
        key, values, predicted = _evaluate_partition(
            name=f"one_dimensional_score:{n_bins}",
            n_bins=n_bins,
            reference=reference,
            template_mask=template_mask,
            template_labels=np.digitize(projected_reference[template_mask], edges),
            test=test,
            test_labels=np.digitize(projected_test, edges),
            patients=patients,
            true_fractions=true_fractions,
            test_scores=test_scores,
        )
        metrics_by_method[key] = values
        predicted_by_method[key] = predicted

        pca = PCA(n_components=2, random_state=seed).fit(transformed_markers[partition_mask])
        pca_reference = pca.transform(transformed_markers)
        pca_test = pca.transform(transformed_test_markers)
        first_parts, second_parts = _factor_pair(n_bins)
        first_edges = _grid_edges(pca_reference[partition_mask, 0], first_parts)
        second_edges = _grid_edges(pca_reference[partition_mask, 1], second_parts)
        key, values, predicted = _evaluate_partition(
            name=f"two_dimensional_grid:{n_bins}",
            n_bins=n_bins,
            reference=reference,
            template_mask=template_mask,
            template_labels=_grid_labels(pca_reference[template_mask], first_edges, second_edges),
            test=test,
            test_labels=_grid_labels(pca_test, first_edges, second_edges),
            patients=patients,
            true_fractions=true_fractions,
            test_scores=test_scores,
        )
        metrics_by_method[key] = values
        predicted_by_method[key] = predicted

        random_metrics: list[dict[str, object]] = []
        rng = np.random.default_rng(seed + n_bins)
        coordinates_reference = np.asarray(kmeans_result.transform.apply(reference_scores))
        coordinates_test = np.asarray(kmeans_result.transform.apply(test_scores))
        repeats = 5 if quick else 20
        for repeat in range(repeats):
            centers = coordinates_reference[
                rng.choice(np.flatnonzero(partition_mask), size=n_bins, replace=False)
            ]
            _, random_values, _ = _evaluate_partition(
                name=f"random:{n_bins}:{repeat}",
                n_bins=n_bins,
                reference=reference,
                template_mask=template_mask,
                template_labels=_nearest(coordinates_reference[template_mask], centers),
                test=test,
                test_labels=_nearest(coordinates_test, centers),
                patients=patients,
                true_fractions=true_fractions,
                test_scores=test_scores,
            )
            random_metrics.append(random_values)
        metrics_by_method[f"random_score_voronoi:{n_bins}"] = {
            "target_macro_rmse_median": float(
                np.median([float(values["target_macro_rmse"]) for values in random_metrics])
            ),
            "held_out_d_efficiency_median": float(
                np.median([float(values["held_out_d_efficiency"]) for values in random_metrics])
            ),
            "repeats": repeats,
        }

        if n_bins == bin_counts[-1]:
            coordinates = np.asarray(soft_result.transform.apply(test_scores))
            final_projection = coordinates[:, :2]
            final_labels = predict_score_bins(soft_result, test_scores)
            final_template_labels = np.asarray(soft_result.predict(reference_scores[template_mask]))
            final_templates = estimate_bin_templates(
                reference.labels[template_mask],
                final_template_labels,
                reference.patients[template_mask],
                n_bins=n_bins,
            )
            predicted_standard_errors, bootstrap_standard_errors = _bootstrap_uncertainty(
                test,
                final_labels,
                final_templates,
                patients,
                repeats=30 if quick else 200,
                seed=seed,
            )
        timings[f"partitions_and_baselines_{n_bins}_bins"] = perf_counter() - bin_started

    acceptance_rows = []
    for n_bins in bin_counts:
        learned = metrics_by_method[f"soft_voronoi:{n_bins}"]
        random = metrics_by_method[f"random_score_voronoi:{n_bins}"]
        marker = metrics_by_method[f"marker_kmeans:{n_bins}"]
        acceptance_rows.append(
            {
                "n_bins": n_bins,
                "beats_random_d_efficiency": float(learned["held_out_d_efficiency"])
                > float(random["held_out_d_efficiency_median"]),
                "no_worse_than_marker_rmse": float(learned["target_macro_rmse"])
                <= float(marker["target_macro_rmse"]),
            }
        )

    calibration = _calibration_metrics(
        score_fit.out_of_fold_probabilities,
        reference.labels,
        reference.patients,
    )
    reference_marker_median = np.median(transformed_markers, axis=0)
    test_marker_median = np.median(transformed_test_markers, axis=0)
    metrics_by_method["calibration"] = calibration
    metrics_by_method["shift"] = {
        "median_absolute_standardized_marker_shift": float(
            np.median(np.abs(test_marker_median - reference_marker_median))
        ),
        "maximum_absolute_standardized_marker_shift": float(
            np.max(np.abs(test_marker_median - reference_marker_median))
        ),
        "score_mean_shift_norm": float(
            np.linalg.norm(np.mean(test_scores, axis=0) - np.mean(reference_scores, axis=0))
        ),
    }
    final_key = f"soft_voronoi:{bin_counts[-1]}"
    final_predictions = predicted_by_method[final_key]
    metrics_by_method["patients"] = [
        {
            "patient": int(patient),
            "true_fractions": truth.tolist(),
            "soft_voronoi_fractions": learned.tolist(),
            "unbinned_fractions": unbinned_row.tolist(),
        }
        for patient, truth, learned, unbinned_row in zip(
            patients, true_fractions, final_predictions, unbinned, strict=True
        )
    ]
    metrics_by_method["acceptance"] = {
        "rows": acceptance_rows,
        "random_d_efficiency_wins": sum(
            bool(row["beats_random_d_efficiency"]) for row in acceptance_rows
        ),
        "marker_rmse_noninferiority_wins": sum(
            bool(row["no_worse_than_marker_rmse"]) for row in acceptance_rows
        ),
        "required_random_wins": 5,
        "required_marker_wins": 4,
    }

    metrics_by_method["run"] = {
        "reference_patients": list(REFERENCE_PATIENTS),
        "test_patients": list(TEST_PATIENTS),
        "reference_composition": theta0.tolist(),
        "score_temperature": score_fit.model.temperature,
        "elapsed_seconds": perf_counter() - started,
        "peak_rss_megabytes": _peak_rss_megabytes(),
        "quick": quick,
        "rows": {
            "reference": len(reference.labels),
            "test": len(test.labels),
            "partition": int(np.count_nonzero(partition_mask)),
            "validation": int(np.count_nonzero(validation_mask)),
            "templates": int(np.count_nonzero(template_mask)),
        },
        "settings": {
            "score_max_per_patient_class": 256 if quick else 2_000,
            "score_max_iter": 35 if quick else 120,
            "partition_max_per_patient_class": 256 if quick else 512,
            "validation_max_per_patient_class": 128 if quick else 256,
            "soft_n_init": 3 if quick else 4,
            "soft_max_steps": 50 if quick else 160,
            "random_repeats": 5 if quick else 20,
            "bootstrap_repeats": 30 if quick else 200,
        },
        "timings_seconds": timings,
    }
    metrics_by_method["uncertainty"] = {
        "n_bins": bin_counts[-1],
        "predicted_standard_errors": predicted_standard_errors.tolist(),
        "bootstrap_standard_errors": bootstrap_standard_errors.tolist(),
        "median_ratio_by_class": np.median(
            predicted_standard_errors / np.maximum(bootstrap_standard_errors, 1e-12), axis=0
        ).tolist(),
    }
    return ExperimentResult(
        metrics=metrics_by_method,
        true_fractions=true_fractions,
        predicted_fractions=predicted_by_method,
        bin_counts=bin_counts,
        score_projection=final_projection,
        projection_labels=final_labels,
        projection_classes=test.labels,
        predicted_standard_errors=predicted_standard_errors,
        bootstrap_standard_errors=bootstrap_standard_errors,
        patient_ids=patients,
    )
