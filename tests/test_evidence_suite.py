from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import scorequant as sq
from examples.baselines import rectangular_observation_bins
from examples.nuisance_profiled_ds import (
    build_problem,
    finite_partitions,
    interval_study,
    partition_agreement,
    unbinned_profiled_information,
)
from examples.soft_purification import (
    center_separation,
    fractional_retention,
    hard_retention,
    softmax_responsibilities,
)
from examples.solver_shootout import (
    compare_methods,
    retention,
    scale_sensitivity,
    whitening_probe,
)
from examples.synthetic_problems import two_parameter_gaussian_mixture
from tests._fit import fit_test_quantizer

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS = REPO_ROOT / "docs" / "examples" / "assets"
SHOOTOUT_METRICS = ASSETS / "solver_shootout.json"
NUISANCE_METRICS = ASSETS / "nuisance-profiled-ds.json"
SOFT_METRICS = ASSETS / "soft-purification.json"

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


def _load(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as stream:
        loaded = json.load(stream)
    assert isinstance(loaded, dict)
    return loaded


def _listing(metrics: dict[str, object], key: str) -> list[dict[str, object]]:
    value = metrics[key]
    assert isinstance(value, list)
    return [row for row in value if isinstance(row, dict)]


def _mapping(metrics: dict[str, object], key: str) -> dict[str, object]:
    value = metrics[key]
    assert isinstance(value, dict)
    return value


# --- docs/examples/nuisance-profiled-ds.md ---------------------------------

# The retention table: full-matrix and profiled retention of each labeling,
# at the precision the page prints.
PAGE_NUISANCE_PARTITIONS: dict[str, tuple[float, float]] = {
    "d_partition": (0.94952, 0.94855),
    "ds_partition_seeded": (0.90115, 0.97903),
    "ds_partition_initialized": (0.90115, 0.97903),
}

# The held-out rows of the same table, plus the training number the prose
# quotes for the soft profiled rule.
PAGE_NUISANCE_RULES: dict[str, tuple[float, float, float]] = {
    "d_rule": (0.95158, 0.95005, 0.94855),
    "ds_rule": (0.93238, 0.97358, 0.97255),
}

# The ceiling sweep: bins, plain D, D_s from generic seeding, D_s from the
# ceiling's labels, and the certified ceiling itself.
PAGE_NUISANCE_SWEEP = [
    (3, 0.92454, 0.95294, 0.95294, 0.95364),
    (4, 0.94855, 0.97903, 0.97903, 0.97972),
    (5, 0.97517, 0.98504, 0.98620, 0.98706),
    (6, 0.98047, 0.98591, 0.99146, 0.99153),
    (8, 0.98940, 0.99322, 0.99509, 0.99518),
]

# The initializer table: bins, both certified gaps, both relocation counts.
PAGE_NUISANCE_INITIALIZER = [
    (3, 0.000735, 0.000735, 315, 5),
    (4, 0.000710, 0.000710, 1715, 17),
    (5, 0.002041, 0.000867, 672, 23),
    (6, 0.005682, 0.000071, 631, 24),
    (8, 0.001971, 0.000096, 870, 51),
]

# The downstream interval table: half-widths in signal-fraction units.
PAGE_NUISANCE_INTERVALS = {
    "unbinned": 0.011258,
    "d_partition": 0.011558,
    "ds_partition_initialized": 0.011376,
}


def test_nuisance_json_matches_the_published_retention_table() -> None:
    metrics = _load(NUISANCE_METRICS)
    assert metrics["n_bins"] == 4
    assert metrics["interest"] == [0]
    assert metrics["nuisance"] == [1, 2]
    # "at four bins on 4000 training and 15000 held-out events".
    assert metrics["n_train"] == 4_000
    assert metrics["n_test"] == 15_000

    partitions = {str(row["key"]): row for row in _listing(metrics, "partitions")}
    assert set(partitions) == set(PAGE_NUISANCE_PARTITIONS)
    for key, (full, profiled) in PAGE_NUISANCE_PARTITIONS.items():
        assert round(float(partitions[key]["full_retention"]), 5) == pytest.approx(full)  # type: ignore[arg-type]
        assert round(float(partitions[key]["profiled_retention"]), 5) == pytest.approx(profiled)  # type: ignore[arg-type]

    rules = {str(row["key"]): row for row in _listing(metrics, "rules")}
    assert set(rules) == set(PAGE_NUISANCE_RULES)
    for key, (full, profiled, train_profiled) in PAGE_NUISANCE_RULES.items():
        row = rules[key]
        assert round(float(row["test_full_retention"]), 5) == pytest.approx(full)  # type: ignore[arg-type]
        assert round(float(row["test_profiled_retention"]), 5) == pytest.approx(profiled)  # type: ignore[arg-type]
        assert round(float(row["train_profiled_retention"]), 5) == pytest.approx(train_profiled)  # type: ignore[arg-type]


def test_nuisance_json_matches_the_published_criterion_trade() -> None:
    """Each criterion wins on its own objective, by the amounts the page states."""
    partitions = {str(row["key"]): row for row in _listing(_load(NUISANCE_METRICS), "partitions")}
    plain = partitions["d_partition"]
    profiled = partitions["ds_partition_initialized"]
    given_up = float(plain["full_retention"]) - float(profiled["full_retention"])  # type: ignore[arg-type]
    gained = float(profiled["profiled_retention"]) - float(plain["profiled_retention"])  # type: ignore[arg-type]
    assert given_up == pytest.approx(0.0484, abs=5e-4)
    assert gained == pytest.approx(0.0305, abs=5e-4)

    agreement = _mapping(_load(NUISANCE_METRICS), "agreement")
    assert round(float(agreement["adjusted_rand_index"]), 3) == pytest.approx(0.629)  # type: ignore[arg-type]
    assert int(agreement["d_interval_runs"]) == 5  # type: ignore[call-overload]
    assert int(agreement["ds_interval_runs"]) == 6  # type: ignore[call-overload]


def test_nuisance_json_matches_the_published_ceiling_sweep() -> None:
    sweep = _listing(_load(NUISANCE_METRICS), "ceiling_sweep")
    assert len(sweep) == len(PAGE_NUISANCE_SWEEP)
    for row, published in zip(sweep, PAGE_NUISANCE_SWEEP, strict=True):
        n_bins, plain, seeded, initialized, ceiling = published
        assert int(float(row["n_bins"])) == n_bins  # type: ignore[arg-type]
        assert round(float(row["d_profiled_retention"]), 5) == pytest.approx(plain)  # type: ignore[arg-type]
        assert round(float(row["ds_seeded_retention"]), 5) == pytest.approx(seeded)  # type: ignore[arg-type]
        assert round(float(row["ds_initialized_retention"]), 5) == pytest.approx(initialized)  # type: ignore[arg-type]
        assert round(float(row["ceiling_retention"]), 5) == pytest.approx(ceiling)  # type: ignore[arg-type]
        # The ceiling is a ceiling: no labeling at this budget may exceed it.
        assert float(row["ds_initialized_retention"]) <= float(row["ceiling_retention"]) + 1e-9  # type: ignore[arg-type]
        assert float(row["d_profiled_retention"]) <= float(row["ceiling_retention"]) + 1e-9  # type: ignore[arg-type]


def test_nuisance_json_matches_the_published_initializer_table() -> None:
    sweep = _listing(_load(NUISANCE_METRICS), "ceiling_sweep")
    for row, published in zip(sweep, PAGE_NUISANCE_INITIALIZER, strict=True):
        n_bins, seeded_gap, initialized_gap, seeded_moves, initialized_moves = published
        assert int(float(row["n_bins"])) == n_bins  # type: ignore[arg-type]
        assert round(float(row["seeded_gap"]), 6) == pytest.approx(seeded_gap)  # type: ignore[arg-type]
        assert round(float(row["initialized_gap"]), 6) == pytest.approx(initialized_gap)  # type: ignore[arg-type]
        assert int(float(row["seeded_moves"])) == seeded_moves  # type: ignore[arg-type]
        assert int(float(row["initialized_moves"])) == initialized_moves  # type: ignore[arg-type]
        # The initializer is never worse on either axis.
        assert float(row["initialized_gap"]) <= float(row["seeded_gap"]) + 1e-12  # type: ignore[arg-type]
        assert float(row["initialized_moves"]) < float(row["seeded_moves"])  # type: ignore[arg-type]

    headline = _mapping(_load(NUISANCE_METRICS), "bound")
    assert int(headline["seeded_scans"]) == 26  # type: ignore[call-overload]
    assert int(headline["initialized_scans"]) == 5  # type: ignore[call-overload]
    assert int(headline["seeded_moves"]) == 1715  # type: ignore[call-overload]
    assert int(headline["initialized_moves"]) == 17  # type: ignore[call-overload]
    # "within 0.0007 nat", which is 0.07 percent in ratio terms.
    gap = float(headline["initialized_gap"])  # type: ignore[arg-type]
    assert gap == pytest.approx(0.00071, abs=5e-6)
    assert 100.0 * (1.0 - np.exp(-gap)) == pytest.approx(0.071, abs=5e-3)
    # "at six bins it closes the certified gap by a factor of 80".
    six = next(row for row in sweep if int(float(row["n_bins"])) == 6)  # type: ignore[arg-type]
    assert float(six["seeded_gap"]) / float(six["initialized_gap"]) == pytest.approx(80.0, abs=2.0)  # type: ignore[arg-type]


def test_nuisance_json_matches_the_published_interval_table() -> None:
    intervals = _mapping(_load(NUISANCE_METRICS), "intervals")
    unbinned = float(intervals["unbinned_half_width"])  # type: ignore[arg-type]
    assert round(unbinned, 6) == pytest.approx(PAGE_NUISANCE_INTERVALS["unbinned"])

    rows = {str(row["key"]): row for row in _listing(intervals, "rows")}
    excess = {}
    for key in ("d_partition", "ds_partition_initialized"):
        half_width = float(rows[key]["half_width"])  # type: ignore[arg-type]
        assert round(half_width, 6) == pytest.approx(PAGE_NUISANCE_INTERVALS[key])
        # The scan is a check on the library, not an illustration beside it.
        fisher = float(rows[key]["fisher_half_width"])  # type: ignore[arg-type]
        assert half_width == pytest.approx(fisher, rel=1e-3)
        excess[key] = 100.0 * (half_width / unbinned - 1.0)

    assert excess["d_partition"] == pytest.approx(2.67, abs=5e-3)
    assert excess["ds_partition_initialized"] == pytest.approx(1.04, abs=5e-3)
    narrowing = 1.0 - (
        float(rows["ds_partition_initialized"]["half_width"])  # type: ignore[arg-type]
        / float(rows["d_partition"]["half_width"])  # type: ignore[arg-type]
    )
    assert 100.0 * narrowing == pytest.approx(1.6, abs=0.05)
    # "about three fifths of the price of binning".
    assert 1.0 - excess["ds_partition_initialized"] / excess["d_partition"] == pytest.approx(
        0.61, abs=0.02
    )

    # "at eight bins the same two profiled retentions imply a narrowing of 0.29%".
    sweep = _listing(_load(NUISANCE_METRICS), "ceiling_sweep")
    eight = next(row for row in sweep if int(float(row["n_bins"])) == 8)  # type: ignore[arg-type]
    narrowing_at_eight = 1.0 - np.sqrt(
        float(eight["d_profiled_retention"]) / float(eight["ds_initialized_retention"])  # type: ignore[arg-type]
    )
    assert 100.0 * narrowing_at_eight == pytest.approx(0.29, abs=0.01)


def test_fast_rerun_reproduces_the_criterion_crossover_and_the_certified_ceiling() -> None:
    problem = build_problem(n_bins=4, sizes=FAST_SIZES)
    train = problem.train
    bound = sq.efficient_score_bound(
        train.scores, interest=problem.interest, weights=train.weights, n_bins=4
    )
    partitions = finite_partitions(problem, n_bins=4, bound=bound)
    rows = {row.key: row for row in partitions.rows}

    # Each criterion wins on its own objective and loses on the other one.
    plain = rows["d_partition"]
    profiled = rows["ds_partition_initialized"]
    assert plain.full_retention > profiled.full_retention
    assert profiled.profiled_retention > plain.profiled_retention

    # The certified ceiling dominates every labeling of this budget, whatever
    # criterion produced it.
    reference = unbinned_profiled_information(
        train.scores, train.weights, interest=problem.interest
    )
    ceiling = float(np.exp(bound.upper_bound - np.log(reference)))
    assert plain.profiled_retention <= ceiling + 1e-9
    assert profiled.profiled_retention <= ceiling + 1e-9

    # The initializer is never worse and always cheaper.
    seeded = rows["ds_partition_seeded"]
    assert profiled.objective >= seeded.objective - 1e-12
    assert profiled.accepted_moves < seeded.accepted_moves

    # The two partitions are genuinely different objects.
    assert 0.2 < partition_agreement(partitions.d_labels, partitions.warm_labels, 4) < 0.95


def test_fast_rerun_reproduces_the_narrower_profiled_interval() -> None:
    problem = build_problem(n_bins=4, sizes=FAST_SIZES)
    train = problem.train
    bound = sq.efficient_score_bound(
        train.scores, interest=problem.interest, weights=train.weights, n_bins=4
    )
    partitions = finite_partitions(problem, n_bins=4, bound=bound)
    study = interval_study(
        problem,
        {
            "d_partition": ("Plain D", partitions.d_labels),
            "ds_partition_initialized": ("Profiled D_s", partitions.warm_labels),
        },
        n_bins=4,
    )
    rows = {row.key: row for row in study.rows}
    for row in study.rows:
        assert row.half_width == pytest.approx(row.fisher_half_width, rel=1e-3)
    assert rows["ds_partition_initialized"].half_width < rows["d_partition"].half_width


def test_profiled_partition_refuses_to_compile() -> None:
    """The page's honest caveat, as an executable statement."""
    problem = build_problem(n_bins=4, sizes=FAST_SIZES)
    train = problem.train
    profiled = sq.optimize_partition(
        train.scores,
        weights=train.weights,
        n_bins=4,
        criterion=sq.ProfiledDOptimality(problem.interest),
        config=sq.DExchangeConfig(seed=11),
    )
    with pytest.raises(ValueError, match="no canonical inductive compilation"):
        profiled.compile_quantizer()


# --- docs/examples/soft-purification.md ------------------------------------

# The annealing table: the randomized rule and the hard rule it implies, at the
# first and last recorded snapshot of the traced fit.
PAGE_SOFT_SCHEDULE = {
    "first_soft_retention": 0.70076,
    "final_soft_retention": 0.97552,
    "first_hard_retention": 0.97557,
    "final_hard_retention": 0.97552,
}

# The hardening-gap ladder, at the one significant digit the page prints.
PAGE_SOFT_HARDENING: dict[str, tuple[float, ...]] = {
    "gaussian_location": (-9.2e-02, -3.5e-02, -4.3e-03, -2.9e-05, -1.4e-08),
    "spectral_templates": (-1.0e-02, -1.8e-03, -1.6e-04, -6.2e-07, -4.2e-09),
    "two_parameter_gaussian_mixture": (-1.3e-02, -2.2e-03, -1.4e-04, -4.9e-07, -1.2e-12),
    "signal_background_shape": (-2.1e-02, -2.7e-03, -2.3e-04, -3.4e-06, 8.1e-15),
}
PAGE_SOFT_RATIOS = (0.8, 0.4, 0.2, 0.05, 0.01)

# The purification table, for the traced problem.
PAGE_SOFT_PURIFICATION = [
    (1.0, 0.33641, 0.97552, 0.639),
    (0.5, 0.86238, 0.97552, 0.113),
    (0.25, 0.96805, 0.97552, 0.00747),
    (0.1, 0.97535, 0.97552, 0.000174),
    (0.05, 0.97550, 0.97552, 0.0000204),
]

# The solver table: soft, exact exchange, exchange started from soft labels.
PAGE_SOFT_SOLVERS = {
    "gaussian_location": (0.8851049, 0.8851055, 0.8851055),
    "spectral_templates": (0.9968710, 0.9969338, 0.9969318),
    "two_parameter_gaussian_mixture": (0.9964000, 0.9964524, 0.9964008),
    "signal_background_shape": (0.9755215, 0.9755675, 0.9755675),
}


def test_soft_json_matches_the_published_annealing_table() -> None:
    metrics = _load(SOFT_METRICS)
    schedule = _mapping(metrics, "schedule")
    # "the signal-plus-backgrounds problem at six cells, 300 Adam steps,
    # cooling to one fiftieth of the starting temperature", on 4000 events.
    assert schedule["problem"] == "signal_background_shape"
    assert schedule["n_bins"] == 6
    assert metrics["n_train"] == 4_000
    assert metrics["schedule_steps"] == 300
    assert float(schedule["temperature_ratio"]) == pytest.approx(0.02)  # type: ignore[arg-type]
    for key, published in PAGE_SOFT_SCHEDULE.items():
        assert round(float(schedule[key]), 5) == pytest.approx(published)  # type: ignore[arg-type]

    # "the soft objective climbs 27 D-efficiency points".
    climb = float(schedule["final_soft_retention"]) - float(schedule["first_soft_retention"])  # type: ignore[arg-type]
    assert 100.0 * climb == pytest.approx(27.5, abs=0.5)
    # "the rule that will be deployed falls by 0.000046".
    change = float(schedule["final_hard_retention"]) - float(schedule["first_hard_retention"])  # type: ignore[arg-type]
    assert change == pytest.approx(-4.6e-5, abs=5e-7)


def test_soft_json_matches_the_published_hardening_ladder() -> None:
    rows = _listing(_load(SOFT_METRICS), "hardening")
    assert len(rows) == len(PAGE_SOFT_HARDENING) * len(PAGE_SOFT_RATIOS)
    for problem, published in PAGE_SOFT_HARDENING.items():
        for ratio, value in zip(PAGE_SOFT_RATIOS, published, strict=True):
            row = next(
                entry
                for entry in rows
                if entry["problem"] == problem
                and float(entry["temperature_ratio"]) == pytest.approx(ratio)  # type: ignore[arg-type]
            )
            gap = float(row["hardening_gap"])  # type: ignore[arg-type]
            assert float(f"{gap:.1e}") == pytest.approx(value)
    # "the gap closes by six or more orders of magnitude" over the ladder, and
    # is negative wherever it is above floating-point noise.
    for problem, published in PAGE_SOFT_HARDENING.items():
        assert abs(published[0]) / abs(published[-1]) > 1e6, problem
        assert all(value < 0.0 for value in published[:-1]), problem


def test_soft_json_matches_the_published_purification_table() -> None:
    rows = [
        row
        for row in _listing(_load(SOFT_METRICS), "purification")
        if row["problem"] == "signal_background_shape"
    ]
    assert len(rows) == len(PAGE_SOFT_PURIFICATION)
    for row, published in zip(rows, PAGE_SOFT_PURIFICATION, strict=True):
        ratio, randomized, purified, gain = published
        assert float(row["temperature_ratio"]) == pytest.approx(ratio)  # type: ignore[arg-type]
        assert round(float(row["randomized_retention"]), 5) == pytest.approx(randomized)  # type: ignore[arg-type]
        assert round(float(row["purified_retention"]), 5) == pytest.approx(purified)  # type: ignore[arg-type]
        assert float(f"{float(row['purification_gain']):.3g}") == pytest.approx(gain, rel=1e-2)  # type: ignore[arg-type]

    # "positive at every temperature and every problem, ranging from 0.64 down
    # to 1.2e-6", and "retains a third of the information".
    every = [
        float(row["purification_gain"]) for row in _listing(_load(SOFT_METRICS), "purification")
    ]  # type: ignore[arg-type]
    assert min(every) > 0.0
    assert max(every) == pytest.approx(0.639, abs=5e-3)
    assert min(every) == pytest.approx(1.2e-6, abs=1e-7)
    warmest = rows[0]
    ratio = float(warmest["randomized_retention"]) / float(warmest["purified_retention"])  # type: ignore[arg-type]
    assert ratio == pytest.approx(1 / 3, abs=0.03)


def test_soft_json_matches_the_published_solver_table() -> None:
    rows = {str(row["problem"]): row for row in _listing(_load(SOFT_METRICS), "solvers")}
    assert set(rows) == set(PAGE_SOFT_SOLVERS)
    deficits = []
    for problem, (soft, exchange, from_soft) in PAGE_SOFT_SOLVERS.items():
        row = rows[problem]
        assert round(float(row["soft_retention"]), 7) == pytest.approx(soft)  # type: ignore[arg-type]
        assert round(float(row["exchange_retention"]), 7) == pytest.approx(exchange)  # type: ignore[arg-type]
        assert round(float(row["exchange_from_soft_retention"]), 7) == pytest.approx(from_soft)  # type: ignore[arg-type]
        # "exact exchange wins on all four".
        assert float(row["exchange_retention"]) >= float(row["soft_retention"])  # type: ignore[arg-type]
        deficits.append(1e6 * (float(row["exchange_retention"]) - float(row["soft_retention"])))  # type: ignore[arg-type]
    # "by between 0.6 and 63 parts per million".
    assert min(deficits) == pytest.approx(0.6, abs=0.1)
    assert max(deficits) == pytest.approx(63.0, abs=1.0)


def test_fractional_retention_agrees_with_the_public_hard_report() -> None:
    """The soft page's grounding check, on a table the page never sees."""
    rng = np.random.default_rng(77)
    scores = rng.normal(size=(500, 3)) @ np.array(
        [[1.0, 0.4, -0.2], [0.0, 1.2, 0.3], [0.0, 0.0, 0.8]]
    )
    weights = rng.uniform(0.3, 1.7, size=500)
    labels = rng.integers(0, 5, size=500)
    one_hot = np.eye(5)[labels]
    assert fractional_retention(scores, one_hot, weights) == pytest.approx(
        hard_retention(scores, labels, weights, 5), abs=1e-12
    )


def test_fast_rerun_reproduces_the_hardening_and_purification_signs() -> None:
    problem = build_problem(n_bins=6, sizes=FAST_SIZES)
    train = problem.train
    source = sq.ScoreSample(train.scores, train.weights)

    gaps = []
    for ratio in (0.5, 0.2, 0.05):
        rule = sq.fit_quantizer(
            source,
            n_bins=6,
            criterion=sq.DOptimality(),
            config=sq.SoftVoronoiConfig(
                seed=3, n_init=4, max_steps=80, record_every=80, temperature_end_ratio=ratio
            ),
        )
        gaps.append(float(rule.hardening_gap or 0.0))
    assert all(gap < 0.0 for gap in gaps)
    assert all(abs(later) < abs(earlier) for earlier, later in zip(gaps, gaps[1:], strict=False))

    fitted = sq.fit_quantizer(
        source,
        n_bins=6,
        criterion=sq.DOptimality(),
        config=sq.SoftVoronoiConfig(seed=3, n_init=4, max_steps=80, record_every=80),
    )
    coordinates = np.asarray(fitted.transform.apply(train.scores))
    centers = np.asarray(fitted.centers)
    separation = center_separation(centers)
    gains = []
    for ratio in (1.0, 0.25):
        responsibilities = softmax_responsibilities(coordinates, centers, ratio * separation)
        gains.append(
            hard_retention(train.scores, np.argmax(responsibilities, axis=1), train.weights, 6)
            - fractional_retention(train.scores, responsibilities, train.weights)
        )
    assert all(gain > 0.0 for gain in gains)
    assert gains[0] > gains[1]

    # The soft fit is a competitor, not a winner: exchange is at least as good.
    exchange = sq.optimize_partition(
        train.scores, weights=train.weights, n_bins=6, config=sq.DExchangeConfig(seed=3)
    )
    assert (
        exchange.train_report.geometric_mean_retention
        >= float(fitted.train_report.geometric_mean_retention) - 1e-9
    )
