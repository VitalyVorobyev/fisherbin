from __future__ import annotations

import numpy as np
import pytest

import scorequant as fb


def test_rank_deficient_fixture_projects_duplicate_direction() -> None:
    coordinate = np.linspace(-2, 2, 600)
    scores = np.column_stack([coordinate, 2 * coordinate])
    result = fb.fit_scores(scores, n_bins=4, config=fb.KMeansConfig(seed=31, n_init=3))
    assert result.transform.rank == 1
    assert result.evaluate(scores).geometric_mean_retention >= 0.90


def test_rare_population_fixture_retains_nonempty_hard_bins() -> None:
    rng = np.random.default_rng(32)
    common = rng.normal(0, 0.35, size=(1_900, 2))
    rare = rng.normal([3.0, -2.0], 0.12, size=(100, 2))
    scores = np.vstack([common, rare])
    result = fb.fit_scores(scores, n_bins=6, config=fb.KMeansConfig(seed=32, n_init=4))
    assert np.all(np.asarray(result.train_report.bin_counts) > 0)
    assert result.train_report.geometric_mean_retention >= 0.70


def test_skewed_and_zero_weight_fixture_remains_finite() -> None:
    rng = np.random.default_rng(33)
    scores = rng.normal(size=(1_000, 3))
    weights = rng.lognormal(mean=0, sigma=2, size=len(scores))
    weights[::11] = 0
    result = fb.fit_scores(
        scores,
        weights=weights,
        n_bins=8,
        config=fb.KMeansConfig(seed=33, n_init=4),
    )
    assert np.isfinite(np.asarray(result.centers)).all()
    assert np.isfinite(result.train_report.geometric_mean_retention)


@pytest.mark.parametrize("shift", [0.0, 0.4, 0.8])
def test_controlled_train_test_shift_is_reported_not_optimized(shift: float) -> None:
    rng = np.random.default_rng(34)
    train = rng.normal(size=(1_200, 2))
    test = rng.normal(loc=[shift, -shift / 2], size=(2_000, 2))
    config = fb.KMeansConfig(seed=34, n_init=3)
    without_validation = fb.fit_scores(train, n_bins=6, config=config)
    with_validation = fb.fit_scores(
        train,
        n_bins=6,
        config=config,
        validation_scores=test,
    )
    np.testing.assert_allclose(without_validation.centers, with_validation.centers)
    assert with_validation.validation_report is not None
    assert np.isfinite(with_validation.validation_report.geometric_mean_retention)
