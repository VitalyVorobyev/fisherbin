from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import scorequant as sq
from examples.baselines import rectangular_observation_bins
from examples.solver_shootout import (
    compare_methods,
    retention,
    scale_sensitivity,
    whitening_probe,
)
from examples.synthetic_problems import two_parameter_gaussian_mixture
from tests._fit import fit_test_quantizer

REPO_ROOT = Path(__file__).resolve().parents[1]
SHOOTOUT_METRICS = REPO_ROOT / "docs" / "examples" / "assets" / "solver_shootout.json"

# Reduced sizes for the bound checks below: the committed JSON carries the
# full study, and these re-runs only have to reproduce its qualitative claims.
FAST_SIZES = (800, 400, 2_000)


def test_rank_deficient_fixture_projects_duplicate_direction() -> None:
    coordinate = np.linspace(-2, 2, 600)
    scores = np.column_stack([coordinate, 2 * coordinate])
    result = fit_test_quantizer(scores, n_bins=4, config=sq.KMeansConfig(seed=31, n_init=3))
    assert result.transform.rank == 1
    assert result.evaluate_scores(scores).geometric_mean_retention >= 0.90


def test_rare_population_fixture_retains_nonempty_hard_bins() -> None:
    rng = np.random.default_rng(32)
    common = rng.normal(0, 0.35, size=(1_900, 2))
    rare = rng.normal([3.0, -2.0], 0.12, size=(100, 2))
    scores = np.vstack([common, rare])
    result = fit_test_quantizer(scores, n_bins=6, config=sq.KMeansConfig(seed=32, n_init=4))
    assert np.all(np.asarray(result.train_report.bin_counts) > 0)
    assert result.train_report.geometric_mean_retention >= 0.70


def test_skewed_and_zero_weight_fixture_remains_finite() -> None:
    rng = np.random.default_rng(33)
    scores = rng.normal(size=(1_000, 3))
    weights = rng.lognormal(mean=0, sigma=2, size=len(scores))
    weights[::11] = 0
    result = fit_test_quantizer(
        scores,
        weights=weights,
        n_bins=8,
        config=sq.KMeansConfig(seed=33, n_init=4),
    )
    assert np.isfinite(np.asarray(result.centers)).all()
    assert np.isfinite(result.train_report.geometric_mean_retention)


@pytest.mark.parametrize("shift", [0.0, 0.4, 0.8])
def test_controlled_train_test_shift_is_reported_not_optimized(shift: float) -> None:
    rng = np.random.default_rng(34)
    train = rng.normal(size=(1_200, 2))
    test = rng.normal(loc=[shift, -shift / 2], size=(2_000, 2))
    config = sq.KMeansConfig(seed=34, n_init=3)
    without_validation = fit_test_quantizer(train, n_bins=6, config=config)
    with_validation = fit_test_quantizer(
        train,
        n_bins=6,
        config=config,
        validation_scores=test,
    )
    np.testing.assert_allclose(without_validation.centers, with_validation.centers)
    assert with_validation.validation_report is not None
    assert np.isfinite(with_validation.validation_report.geometric_mean_retention)


def _shootout_metrics() -> dict[str, object]:
    with SHOOTOUT_METRICS.open(encoding="utf-8") as stream:
        loaded = json.load(stream)
    assert isinstance(loaded, dict)
    return loaded


def _shootout_methods() -> dict[str, dict[str, float | str | None]]:
    methods = _shootout_metrics()["methods"]
    assert isinstance(methods, list)
    return {str(row["key"]): row for row in methods}


# Every retention number the solver-shootout page prints in its method table,
# transcribed from the committed JSON at the precision the page shows.
PAGE_RETENTION: dict[str, tuple[float, float | None]] = {
    "partition_d_exchange": (0.99916, None),
    "partition_mahalanobis_lloyd": (0.99916, None),
    "quantizer_d_exchange": (0.99916, 0.99910),
    "quantizer_mahalanobis_lloyd": (0.99916, 0.99910),
    "quantizer_whitened_kmeans": (0.99916, 0.99910),
    "quantizer_soft_voronoi": (0.99916, 0.99910),
    "quantizer_scalar_dp": (0.99917, 0.99911),
    "baseline_rectangular_observation_bins": (0.94226, 0.93762),
    "baseline_euclidean_kmeans_scores": (0.99906, 0.99897),
    "baseline_equal_frequency_1d": (0.99793, 0.99788),
}

# The relative-cost column of the same page: the published value and the
# number of decimals the page shows it to.
PAGE_COST_RATIO: dict[str, tuple[float, int]] = {
    "partition_d_exchange": (1.00, 2),
    "partition_mahalanobis_lloyd": (1.01, 2),
    "quantizer_d_exchange": (1.01, 2),
    "quantizer_mahalanobis_lloyd": (1.01, 2),
    "quantizer_whitened_kmeans": (1.03, 2),
    "quantizer_soft_voronoi": (2.21, 2),
    "quantizer_scalar_dp": (2.73, 2),
    "baseline_rectangular_observation_bins": (0.001, 3),
    "baseline_euclidean_kmeans_scores": (0.29, 2),
    "baseline_equal_frequency_1d": (0.001, 3),
}

# The bin-budget sweep table: budget, score space, rectangular grid, gap.
PAGE_BUDGET_SWEEP = [
    (4, 0.98360, 0.89767, 0.08594),
    (9, 0.99708, 0.69843, 0.29865),
    (16, 0.99910, 0.93762, 0.06148),
    (25, 0.99961, 0.90734, 0.09227),
]

# The score-rescaling table: multiplier, whitened fit, Euclidean k-means.
PAGE_SCALE_PROBE = [
    (1.0, 0.98581, 0.98029),
    (5.0, 0.98581, 0.94995),
    (25.0, 0.98581, 0.40206),
    (100.0, 0.98581, 0.39556),
]


def test_shootout_json_matches_the_published_method_table() -> None:
    methods = _shootout_methods()
    assert set(methods) == set(PAGE_RETENTION)
    for key, (train, test) in PAGE_RETENTION.items():
        row = methods[key]
        assert round(float(row["train_retention"]), 5) == pytest.approx(train)  # type: ignore[arg-type]
        if test is None:
            assert row["test_retention"] is None
        else:
            assert round(float(row["test_retention"]), 5) == pytest.approx(test)  # type: ignore[arg-type]


def test_shootout_json_matches_the_published_cost_table() -> None:
    metrics = _shootout_metrics()
    methods = _shootout_methods()
    # The methodology the page states must be the one the study ran.
    assert metrics["timing_repeats"] == 5
    assert "warm-up" in str(metrics["timing_note"])
    assert isinstance(metrics["machine"], dict)
    for key, (ratio, decimals) in PAGE_COST_RATIO.items():
        measured = float(methods[key]["seconds_ratio"])  # type: ignore[arg-type]
        assert round(measured, decimals) == pytest.approx(ratio)
        assert float(methods[key]["seconds"]) > 0.0  # type: ignore[arg-type]
    assert float(metrics["fastest_information_aware_seconds"]) > 0.0  # type: ignore[arg-type]


def test_shootout_json_matches_the_published_sweep_and_scale_tables() -> None:
    metrics = _shootout_metrics()
    sweep = metrics["budget_sweep"]
    assert isinstance(sweep, list)
    assert len(sweep) == len(PAGE_BUDGET_SWEEP)
    for row, (n_bins, score_space, grid, gap) in zip(sweep, PAGE_BUDGET_SWEEP, strict=True):
        assert int(row["n_bins"]) == n_bins
        assert round(float(row["score_space"]), 5) == pytest.approx(score_space)
        assert round(float(row["observation_space"]), 5) == pytest.approx(grid)
        assert round(float(row["gap"]), 5) == pytest.approx(gap)

    probe = metrics["scale_probe"]
    assert isinstance(probe, dict)
    entries = probe["entries"]
    assert isinstance(entries, list)
    for row, (scale, whitened, euclidean) in zip(entries, PAGE_SCALE_PROBE, strict=True):
        assert float(row["scale"]) == pytest.approx(scale)
        assert round(float(row["whitened"]), 5) == pytest.approx(whitened)
        assert round(float(row["euclidean"]), 5) == pytest.approx(euclidean)


def test_shootout_headline_gaps_hold_in_the_committed_study() -> None:
    metrics = _shootout_metrics()
    methods = _shootout_methods()
    held_out = [
        float(row["test_retention"])  # type: ignore[arg-type]
        for row in methods.values()
        if row["family"] == "information_aware" and row["test_retention"] is not None
    ]
    grid = float(methods["baseline_rectangular_observation_bins"]["test_retention"])  # type: ignore[arg-type]

    # Claim 1: score space beats the observation-space grid, by 6.1 points at
    # the headline budget and by at least 6 points at every swept budget.
    assert max(held_out) - grid == pytest.approx(0.0615, abs=5e-4)
    assert (1.0 - grid) / (1.0 - max(held_out)) == pytest.approx(70.0, abs=1.0)
    sweep = metrics["budget_sweep"]
    assert isinstance(sweep, list)
    assert min(float(row["gap"]) for row in sweep) > 0.06
    assert max(float(row["gap"]) for row in sweep) > 0.29

    # Claim 3: the information-aware solvers agree far more closely than they
    # differ in cost.
    assert max(held_out) - min(held_out) < 2e-5
    ratios = [
        float(row["seconds_ratio"])  # type: ignore[arg-type]
        for row in methods.values()
        if row["family"] == "information_aware"
    ]
    assert max(ratios) > 2.0


def test_shootout_whitening_is_inert_on_a_line_and_decisive_off_it() -> None:
    metrics = _shootout_metrics()
    probe = metrics["whitening_probe"]
    assert isinstance(probe, dict)
    # Claim 2, first half: on a two-parameter component score the whole cloud
    # lies on a line, so whitening cannot change the k-means partition.
    assert abs(float(probe["whitened"]) - float(probe["unwhitened"])) < 1e-4

    scale_probe = metrics["scale_probe"]
    assert isinstance(scale_probe, dict)
    entries = scale_probe["entries"]
    assert isinstance(entries, list)
    whitened = [float(row["whitened"]) for row in entries]
    euclidean = [float(row["euclidean"]) for row in entries]
    # Claim 2, second half: off the line, D-efficiency is invariant under a
    # score reparameterization and only the whitened fit reflects that.
    assert max(whitened) - min(whitened) < 1e-9
    assert euclidean[0] > 0.97
    assert min(euclidean) < 0.5
    assert euclidean[0] - min(euclidean) > 0.5


def test_fast_rerun_reproduces_the_score_space_gap_and_solver_agreement() -> None:
    problem = two_parameter_gaussian_mixture(n_bins=16, sizes=FAST_SIZES)
    methods = compare_methods(problem, soft_steps=60, timing_repeats=1)
    by_key = {entry.key: entry for entry in methods}

    held_out = [
        entry.test_retention
        for entry in methods
        if entry.family == "information_aware" and entry.test_retention is not None
    ]
    grid = by_key["baseline_rectangular_observation_bins"].test_retention
    assert grid is not None
    assert max(held_out) - grid > 0.03
    assert max(held_out) - min(held_out) < 2e-4
    assert min(held_out) > 0.99

    equal_frequency = by_key["baseline_equal_frequency_1d"].test_retention
    assert equal_frequency is not None
    assert max(held_out) - equal_frequency > 5e-4

    whitening = whitening_probe(problem)
    assert abs(whitening["whitened"] - whitening["unwhitened"]) < 1e-3


def test_fast_rerun_reproduces_the_score_rescaling_collapse() -> None:
    rows = scale_sensitivity(scales=(1.0, 25.0), n_bins=8, sizes=FAST_SIZES)
    assert rows[0]["whitened"] == pytest.approx(rows[1]["whitened"], abs=1e-9)
    assert rows[0]["euclidean"] > 0.95
    assert rows[1]["euclidean"] < 0.6


def test_rectangular_grid_is_not_monotone_in_the_bin_budget() -> None:
    """The page claims adding grid cells can lose information; measure it."""
    values = []
    for n_bins in (4, 9):
        problem = two_parameter_gaussian_mixture(n_bins=n_bins, sizes=FAST_SIZES)
        labels = rectangular_observation_bins(
            problem.test.observations, total_budget=problem.n_bins
        )
        values.append(
            retention(problem.test.scores, labels, problem.test.weights, int(labels.max()) + 1)
        )
    assert values[1] < values[0]
