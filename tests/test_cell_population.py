from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

import numpy as np

import scorequant as fb
from examples.cell_population.closure import (
    ClosureInputs,
    conditional_binned_fisher_information,
    conditional_fisher_information,
    fixed_total_partition_audit,
    ratio_model_audit,
    template_identifiability_audit,
    uncertainty_coverage_audit,
)
from examples.cell_population.data import (
    CLASS_NAMES,
    REFERENCE_PATIENTS,
    TEST_PATIENTS,
    FlowCytData,
    RobustArcsinhTransform,
    load_fixture,
)
from examples.cell_population.experiment import predict_score_bins, run_experiment
from examples.cell_population.fixture import _proportional_counts, _stratified_patient_ranges
from examples.cell_population.likelihood import (
    estimate_bin_templates,
    fit_binned_mixture,
    fit_unbinned_mixture,
)
from examples.cell_population.scores import (
    fit_score_model,
    integration_weights,
    reference_composition,
)

FIXTURE = Path("examples/data/flowcyt_fixture.npz")
FULL_EVIDENCE = Path("docs/usecases/assets/cell_population.json")


def _synthetic_flowcyt(seed: int = 10, per_class: int = 10) -> FlowCytData:
    rng = np.random.default_rng(seed)
    features: list[np.ndarray] = []
    labels: list[np.ndarray] = []
    patients: list[np.ndarray] = []
    rows: list[np.ndarray] = []
    centers = rng.normal(0, 2, size=(len(CLASS_NAMES), 12))
    for patient in (*REFERENCE_PATIENTS, *TEST_PATIENTS):
        shift = rng.normal(0, 0.08, size=12)
        for label in range(len(CLASS_NAMES)):
            block = centers[label] + shift + rng.normal(0, 0.35, size=(per_class, 12))
            features.append(150 * np.sinh(block))
            labels.append(np.full(per_class, label))
            patients.append(np.full(per_class, patient))
            rows.append(np.arange(per_class))
    return FlowCytData(
        np.concatenate(features),
        np.concatenate(labels),
        np.concatenate(patients),
        np.concatenate(rows),
    )


def test_robust_transform_is_frozen_and_finite() -> None:
    data = _synthetic_flowcyt(per_class=3)
    reference = data.patients_in(REFERENCE_PATIENTS)
    transform = RobustArcsinhTransform.fit(reference.features)
    transformed = transform.apply(data.features)
    assert transformed.shape == data.features.shape
    assert np.isfinite(transformed).all()


def test_posterior_prior_correction_recovers_same_simplex_scores() -> None:
    rng = np.random.default_rng(20)
    ratios = np.exp(rng.normal(size=(50, 6)))
    theta0 = np.asarray([0.16, 0.14, 0.20, 0.08, 0.07, 0.35])
    uniform_prior = np.full(6, 1 / 6)
    skewed_prior = np.asarray([0.35, 0.15, 0.10, 0.05, 0.05, 0.30])
    uniform_posterior = ratios * uniform_prior
    uniform_posterior /= np.sum(uniform_posterior, axis=1, keepdims=True)
    skewed_posterior = ratios * skewed_prior
    skewed_posterior /= np.sum(skewed_posterior, axis=1, keepdims=True)
    np.testing.assert_allclose(
        fb.mixture_scores_from_posteriors(uniform_posterior, uniform_prior, theta0),
        fb.mixture_scores_from_posteriors(skewed_posterior, skewed_prior, theta0),
        rtol=1e-12,
        atol=1e-12,
    )


def test_binned_and_unbinned_mixture_recover_known_fractions() -> None:
    templates = np.asarray(
        [
            [0.70, 0.05, 0.05, 0.05, 0.05, 0.10],
            [0.05, 0.70, 0.05, 0.05, 0.05, 0.10],
            [0.05, 0.05, 0.70, 0.05, 0.05, 0.10],
            [0.05, 0.05, 0.05, 0.70, 0.05, 0.10],
            [0.05, 0.05, 0.05, 0.05, 0.70, 0.10],
            [0.10, 0.10, 0.10, 0.10, 0.10, 0.50],
        ]
    )
    theta = np.asarray([0.10, 0.12, 0.15, 0.08, 0.05, 0.50])
    counts = 2_000_000 * (templates @ theta)
    binned = fit_binned_mixture(counts, templates)
    np.testing.assert_allclose(binned.fractions, theta, atol=2e-6)
    np.testing.assert_allclose(binned.covariance, binned.covariance.T)
    assert np.linalg.eigvalsh(binned.covariance).min() >= -1e-12

    ratios = np.repeat(templates.T, 20_000, axis=0)
    unbinned = fit_unbinned_mixture(ratios)
    assert np.isfinite(unbinned.fractions).all()
    np.testing.assert_allclose(np.sum(unbinned.fractions), 1.0)

    component_values = templates
    uniform_priors = np.full(6, 1 / 6)
    posterior_values = component_values * uniform_priors[None, :]
    posterior_values /= np.sum(posterior_values, axis=1, keepdims=True)
    exact_scores = fb.mixture_scores_from_posteriors(posterior_values, uniform_priors, theta)
    mixture_weights = component_values @ theta
    coarse_bins = np.asarray([0, 0, 1, 1, 2, 2])
    full_fisher = fb.fisher_information(exact_scores, mixture_weights)
    binned_fisher = fb.binned_fisher_information(
        exact_scores, coarse_bins, mixture_weights, n_bins=3
    )
    residual = np.asarray(full_fisher - binned_fisher)
    assert np.linalg.eigvalsh((residual + residual.T) / 2).min() >= -1e-12


def test_fixed_total_information_obeys_psd_ordering_and_bin_rank_bound() -> None:
    rng = np.random.default_rng(101)
    scores = rng.normal(size=(2_000, 5))
    weights = rng.uniform(0.2, 2.0, size=len(scores))
    labels = np.argmax(scores[:, :4], axis=1)
    full = conditional_fisher_information(scores, weights)
    binned = conditional_binned_fisher_information(scores, labels, weights, n_bins=4)
    residual = (full - binned + (full - binned).T) / 2
    assert np.linalg.eigvalsh(residual).min() >= -1e-12
    assert np.linalg.matrix_rank(binned, tol=1e-10) <= 3
    audit = fixed_total_partition_audit(scores, labels, weights, n_bins=4)
    assert audit["retained_rank"] <= audit["rank_bound"] == 3
    assert audit["d_efficiency"] == 0.0


def test_scientific_closure_input_cannot_receive_test_data() -> None:
    names = {field.name for field in fields(ClosureInputs)}
    assert "test" not in names
    assert "test_labels" not in names
    assert "true_fractions" not in names


def test_five_bins_cannot_identify_six_fixed_total_fractions() -> None:
    rng = np.random.default_rng(102)
    templates = rng.dirichlet(np.ones(5), size=6).T
    theta0 = np.asarray([0.10, 0.12, 0.08, 0.05, 0.15, 0.50])
    audit = template_identifiability_audit(templates, theta0)
    assert audit["effective_rank"] <= 4
    assert audit["rank_bound"] == 4
    assert audit["full_rank"] is False
    witness = audit["nonidentifiability_witness"]
    assert isinstance(witness, dict)
    assert witness["fraction_separation_norm"] > 0
    assert witness["maximum_bin_probability_difference"] < 1e-12


def test_six_bins_can_close_a_full_rank_six_class_template() -> None:
    templates = np.full((6, 6), 0.02)
    np.fill_diagonal(templates, 0.9)
    templates /= np.sum(templates, axis=0, keepdims=True)
    theta = np.asarray([0.10, 0.12, 0.08, 0.05, 0.15, 0.50])
    audit = template_identifiability_audit(templates, theta)
    assert audit["full_rank"] is True
    estimate = fit_binned_mixture(200_000 * (templates @ theta), templates)
    np.testing.assert_allclose(estimate.fractions, theta, atol=2e-6)


def test_uncertainty_audit_marks_boundary_dominated_components() -> None:
    templates = np.full((8, 6), 0.01)
    templates[:6] += np.eye(6) * 0.9
    templates /= np.sum(templates, axis=0, keepdims=True)
    theta = np.asarray([0.15, 0.12, 0.10, 1e-12, 0.08, 0.55 - 1e-12])
    audit = uncertainty_coverage_audit(templates, theta, draws=80, event_count=2_000, seed=103)
    reference_mast = audit["scenarios"]["reference_like"]["classes"]["mast cells"]
    assert reference_mast["status"] == "boundary_dominated"
    assert reference_mast["interior_standard_error_ratio"] is None
    assert reference_mast["interior_68_percent_coverage"] is None
    enriched_t = audit["scenarios"]["mast_enriched"]["classes"]["T cells"]
    assert np.isfinite(enriched_t["empirical_standard_deviation"])


def test_template_estimation_is_patient_balanced_and_smoothed() -> None:
    labels = np.tile(np.repeat(np.arange(6), 8), 2)
    patients = np.repeat([1, 2], 48)
    bins = (labels + np.arange(len(labels)) % 2) % 4
    templates = estimate_bin_templates(labels, bins, patients, n_bins=4)
    assert templates.shape == (4, 6)
    assert np.all(templates > 0)
    np.testing.assert_allclose(np.sum(templates, axis=0), 1.0)


def test_cross_fitted_score_model_covers_every_reference_patient() -> None:
    data = _synthetic_flowcyt(per_class=8)
    reference = data.patients_in(REFERENCE_PATIENTS)
    fitted = fit_score_model(reference, max_per_patient_class=8, max_iter=8)
    assert fitted.out_of_fold_probabilities.shape == (len(reference.labels), 6)
    np.testing.assert_allclose(np.sum(fitted.out_of_fold_probabilities, axis=1), 1.0)
    theta0 = reference_composition(reference.labels, reference.patients)
    scores = fb.mixture_scores_from_posteriors(
        fitted.out_of_fold_probabilities,
        fitted.model.class_priors,
        theta0,
    )
    assert scores.shape == (len(reference.labels), 5)
    assert fitted.calibration_selection["selected_strategy"] in {
        "raw_declared_prior",
        "raw_oof_prior",
        "temperature_oof_prior",
    }
    outer_folds = fitted.calibration_selection["outer_folds"]
    assert len(outer_folds) == 5
    held_out_patients = [patient for fold in outer_folds for patient in fold["held_out_patients"]]
    assert sorted(held_out_patients) == sorted(REFERENCE_PATIENTS)
    assert len(held_out_patients) == len(set(held_out_patients))
    assert list(fitted.calibration_selection["candidates"]) == [
        "raw_declared_prior",
        "raw_oof_prior",
        "temperature_oof_prior",
    ]
    final_calibration = fitted.calibration_selection["final_calibration"]
    assert float(final_calibration["maximum_normalization_residual"]) < 0.25
    closure = ratio_model_audit(fitted, reference, theta0)
    strategies = closure["strategies"]
    assert strategies["raw_oof_prior"]["maximum_normalization_residual"] < 1e-12
    assert strategies["temperature_oof_prior"]["maximum_normalization_residual"] < 1e-12
    assert np.isfinite(strategies[closure["selected_strategy"]]["mean_score_norm"])
    weights = integration_weights(reference.labels, reference.patients, theta0)
    np.testing.assert_allclose(np.sum(weights), 1.0)


def test_committed_fixture_has_disjoint_patients_and_declared_schema() -> None:
    data = load_fixture(FIXTURE)
    reference = data.patients_in(REFERENCE_PATIENTS)
    test = data.patients_in(TEST_PATIENTS)
    assert len(reference.labels) > 0
    assert len(test.labels) > 0
    assert set(reference.patients).isdisjoint(set(test.patients))
    assert set(reference.labels) == set(range(6))
    assert data.features.shape[1] == 12


def test_chunked_score_prediction_matches_one_shot() -> None:
    rng = np.random.default_rng(44)
    scores = rng.normal(size=(127, 3))
    result = fb.fit_scores(scores, n_bins=5)
    np.testing.assert_array_equal(
        predict_score_bins(result, scores, chunk_size=13), np.asarray(result.predict(scores))
    )


def test_remote_sample_ranges_are_deterministic_and_bounded() -> None:
    totals = (17, 83, 211, 9, 31, 149)
    first = _stratified_patient_ranges(totals, 137, 12, np.random.default_rng(2026))
    second = _stratified_patient_ranges(totals, 137, 12, np.random.default_rng(2026))
    assert first == second
    assert sum(count for ranges in first for _, count in ranges) == 137
    for total, ranges in zip(totals, first, strict=True):
        assert all(start >= 0 and count > 0 and start + count <= total for start, count in ranges)
        occupied = [set(range(start, start + count)) for start, count in ranges]
        assert sum(len(values) for values in occupied) == len(set().union(*occupied))


def test_remote_sample_allocation_preserves_component_proportions() -> None:
    totals = (66_439, 11_773, 12_768, 66, 3_618, 449_803)
    counts = _proportional_counts(totals, 20_000)
    assert sum(counts) == 20_000
    assert all(0 <= count <= total for count, total in zip(counts, totals, strict=True))
    np.testing.assert_allclose(
        np.asarray(counts) / sum(counts),
        np.asarray(totals) / sum(totals),
        atol=1 / 20_000,
    )


def test_flowcyt_fixture_is_the_standard_end_to_end_use_case() -> None:
    result = run_experiment(
        load_fixture(FIXTURE),
        bin_counts=(5,),
        operating_n_bins=5,
        uncertainty_n_bins=5,
        quick=True,
    )
    soft = result.metrics["soft_voronoi:5"]
    marker = result.metrics["marker_kmeans:5"]
    assert float(soft["target_macro_rmse"]) < float(marker["target_macro_rmse"])
    assert float(soft["held_out_d_efficiency"]) >= 0.20
    assert result.predicted_fractions["soft_voronoi:5"].shape == (len(TEST_PATIENTS), 6)
    assert result.operating_bin_composition.shape == (5, 6)
    np.testing.assert_allclose(np.sum(result.operating_bin_composition, axis=1), 1.0)
    assert "unbinned_classifier_ratio" in result.metrics
    assert "unbinned" not in result.metrics
    closure = result.metrics["scientific_closure"]
    assert closure["reference_only"] is True
    assert closure["template_identifiability"]["soft_voronoi:5"]["full_rank"] is False
    assert closure["fixed_total_information"]["soft_voronoi:5"]["retained_rank"] <= 4
    assert result.metrics["uncertainty"]["protocol"]["source"] == "frozen_reference_templates"


def test_committed_full_patient_evidence_passes_the_frozen_gate() -> None:
    metrics = json.loads(FULL_EVIDENCE.read_text(encoding="utf-8"))
    assert metrics["source"]["sample_rows"] == 600_000
    assert metrics["run"]["quick"] is False
    assert metrics["acceptance"]["random_d_efficiency_wins"] == 6
    assert metrics["acceptance"]["marker_rmse_noninferiority_wins"] == 6
    assert metrics["soft_voronoi:8"]["held_out_d_efficiency"] >= 0.94
    assert metrics["soft_voronoi:8"]["target_macro_rmse"] <= 0.0023
    assert metrics["soft_voronoi:8"]["likelihood_convergence"]["converged_patients"] == 10
    assert metrics["calibration_selection"]["selected_strategy"] == "raw_declared_prior"
    assert metrics["run"]["classifier_test_posterior_evaluations"] == 1
    assert (
        metrics["unbinned_classifier_ratio"]["target_macro_rmse"]
        < metrics["soft_voronoi:8"]["target_macro_rmse"]
    )
    composition = np.asarray(metrics["operating_partition"]["reference_bin_composition"])
    assert composition.shape == (8, 6)
    np.testing.assert_allclose(np.sum(composition, axis=1), 1.0)

    closure = metrics["scientific_closure"]
    assert closure["reference_only"] is True
    assert set(closure) == {
        "reference_only",
        "ratio_model",
        "fixed_total_information",
        "template_identifiability",
        "population_limit",
        "pseudo_patients",
        "seed_stability",
        "uncertainty_coverage",
    }
    ratio_strategies = closure["ratio_model"]["strategies"]
    assert ratio_strategies["raw_declared_prior"]["maximum_normalization_residual"] > 0.20
    assert ratio_strategies["raw_oof_prior"]["maximum_normalization_residual"] < 1e-12
    for method in ("score_kmeans", "soft_voronoi"):
        five = closure["template_identifiability"][f"{method}:5"]
        assert five["effective_rank"] == 4
        assert five["full_rank"] is False
        assert five["nonidentifiability_witness"]["maximum_bin_probability_difference"] < 1e-12
        assert closure["fixed_total_information"][f"{method}:5"]["d_efficiency"] == 0.0
        for n_bins in (6, 8):
            assert closure["template_identifiability"][f"{method}:{n_bins}"]["full_rank"]
            assert closure["fixed_total_information"][f"{method}:{n_bins}"]["retained_rank"] == 5

    pseudo = closure["pseudo_patients"]
    assert pseudo["protocol"]["source"] == "reference_validation_rows_only"
    assert pseudo["protocol"]["repeats_per_composition"] == 20
    assert len(pseudo["by_composition"]) == 11
    assert pseudo["methods"]["soft_voronoi:5"]["converged_pseudo_patients"] == 0
    assert pseudo["methods"]["soft_voronoi:6"]["converged_pseudo_patients"] == 220
    stability = closure["seed_stability"]
    assert stability["seeds"] == list(range(2026, 2036))
    assert stability["summary"]["soft_voronoi:5"]["template_rank_range"] == [4, 4]
    assert stability["summary"]["soft_voronoi:8"]["template_rank_range"] == [5, 5]

    uncertainty = metrics["uncertainty"]
    assert uncertainty["protocol"]["source"] == "frozen_reference_templates"
    reference_mast = uncertainty["scenarios"]["reference_like"]["classes"]["mast cells"]
    assert reference_mast["status"] == "boundary_dominated"
    assert reference_mast["interior_standard_error_ratio"] is None
    assert reference_mast["interior_68_percent_coverage"] is None
    enriched_mast = uncertainty["scenarios"]["mast_enriched"]["classes"]["mast cells"]
    assert enriched_mast["status"] == "interior"
    assert 0.9 <= enriched_mast["interior_standard_error_ratio"] <= 1.1
