from __future__ import annotations

import jax.numpy as jnp
import numpy as np
import pytest

import scorequant as sq
from tests._fit import fit_test_quantizer


def _posteriors_from_ratios(ratios: np.ndarray, priors: np.ndarray) -> np.ndarray:
    values = ratios * priors[None, :]
    return values / np.sum(values, axis=1, keepdims=True)


def test_mixture_scores_match_simplex_derivative() -> None:
    posteriors = jnp.asarray([[0.6, 0.3, 0.1], [0.15, 0.35, 0.5]])
    priors = jnp.asarray([0.5, 0.3, 0.2])
    reference = jnp.asarray([0.2, 0.3, 0.5])
    ratios = np.asarray(posteriors) / np.asarray(priors)
    density = ratios @ np.asarray(reference)
    expected = (ratios[:, :2] - ratios[:, [2]]) / density[:, None]

    scores = sq.mixture_scores_from_ratios(sq.ratios_from_posteriors(posteriors, priors), reference)

    np.testing.assert_allclose(scores, expected, rtol=1e-6, atol=1e-7)
    assert scores.shape == (2, 2)


def test_ratios_from_posteriors_apply_the_declared_prior_correction() -> None:
    posteriors = np.asarray([[0.6, 0.3, 0.1], [0.15, 0.35, 0.5]])
    priors = np.asarray([0.5, 0.3, 0.2])

    ratios = sq.ratios_from_posteriors(posteriors, priors)

    np.testing.assert_allclose(ratios, posteriors / priors[None, :], rtol=1e-6)


def test_prior_correction_recovers_the_same_density_ratio_scores() -> None:
    rng = np.random.default_rng(20)
    ratios = np.exp(rng.normal(size=(50, 4)))
    reference = np.asarray([0.16, 0.14, 0.20, 0.50])
    uniform_prior = np.full(4, 0.25)
    skewed_prior = np.asarray([0.45, 0.15, 0.10, 0.30])

    uniform = sq.ratios_from_posteriors(
        _posteriors_from_ratios(ratios, uniform_prior), uniform_prior
    )
    skewed = sq.ratios_from_posteriors(_posteriors_from_ratios(ratios, skewed_prior), skewed_prior)

    np.testing.assert_allclose(
        sq.mixture_scores_from_ratios(uniform, reference),
        sq.mixture_scores_from_ratios(skewed, reference),
        rtol=1e-6,
        atol=1e-6,
    )


def test_mixture_scores_are_gauge_invariant() -> None:
    rng = np.random.default_rng(21)
    ratios = np.exp(rng.normal(size=(60, 3)))
    gauge = np.exp(rng.normal(size=(60, 1)))
    reference = np.asarray([0.2, 0.3, 0.5])

    plain = sq.mixture_scores_from_ratios(ratios, reference)
    rescaled = sq.mixture_scores_from_ratios(ratios * gauge, reference)

    np.testing.assert_allclose(plain, rescaled, rtol=1e-6, atol=1e-6)


def test_intensity_scores_are_gauge_invariant() -> None:
    rng = np.random.default_rng(23)
    ratios = np.exp(rng.normal(size=(60, 3)))
    gauge = np.exp(rng.normal(size=(60, 1)))
    coefficients = np.asarray([0.6, 1.4, 0.9])

    plain = sq.scores_from_components(ratios, coefficients)
    rescaled = sq.scores_from_components(ratios * gauge, coefficients)

    np.testing.assert_allclose(plain, rescaled, rtol=1e-6, atol=1e-6)


def test_mixture_scores_are_pairwise_differences_of_intensity_scores() -> None:
    rng = np.random.default_rng(24)
    ratios = np.exp(rng.normal(size=(40, 4)))
    reference = np.asarray([0.16, 0.14, 0.20, 0.50])

    intensity = np.asarray(sq.scores_from_components(ratios, reference))
    mixture = np.asarray(sq.mixture_scores_from_ratios(ratios, reference))

    np.testing.assert_allclose(mixture, intensity[:, :3] - intensity[:, [3]], rtol=1e-6, atol=1e-6)


def test_priors_proportional_to_reference_reduce_to_raw_ratios() -> None:
    rng = np.random.default_rng(25)
    ratios = np.exp(rng.normal(size=(30, 3)))
    reference = np.asarray([0.2, 0.3, 0.5])
    posteriors = _posteriors_from_ratios(ratios, reference)

    corrected = sq.ratios_from_posteriors(posteriors, reference)
    intensity = sq.scores_from_components(corrected, reference)

    np.testing.assert_allclose(intensity, corrected, rtol=1e-6, atol=1e-6)


def test_reference_component_changes_only_the_score_parameterization() -> None:
    rng = np.random.default_rng(22)
    posteriors = rng.dirichlet(np.ones(4), size=300)
    priors = np.full(4, 0.25)
    reference = np.asarray([0.2, 0.25, 0.15, 0.4])
    ratios = sq.ratios_from_posteriors(posteriors, priors)
    last_scores = sq.mixture_scores_from_ratios(ratios, reference)
    first_scores = sq.mixture_scores_from_ratios(ratios, reference, reference_component=0)
    config = sq.KMeansConfig(seed=7, n_init=4)

    last_labels = np.asarray(fit_test_quantizer(last_scores, n_bins=6, config=config).labels)
    first_labels = np.asarray(fit_test_quantizer(first_scores, n_bins=6, config=config).labels)

    np.testing.assert_array_equal(
        last_labels[:, None] == last_labels[None, :],
        first_labels[:, None] == first_labels[None, :],
    )


def test_class_permutation_preserves_scores_up_to_column_order() -> None:
    posteriors = np.asarray([[0.6, 0.3, 0.1], [0.15, 0.35, 0.5]])
    priors = np.asarray([0.5, 0.3, 0.2])
    reference = np.asarray([0.2, 0.3, 0.5])
    permutation = np.asarray([2, 0, 1])

    expected = sq.mixture_scores_from_ratios(
        sq.ratios_from_posteriors(posteriors, priors), reference
    )
    permuted = sq.mixture_scores_from_ratios(
        sq.ratios_from_posteriors(posteriors[:, permutation], priors[permutation]),
        reference[permutation],
        reference_component=0,
    )

    np.testing.assert_allclose(permuted, expected)


def test_zero_posteriors_are_allowed_without_clipping() -> None:
    ratios = sq.ratios_from_posteriors(
        jnp.asarray([[1.0, 0.0, 0.0], [0.0, 0.25, 0.75]], dtype=jnp.float32),
        [0.4, 0.3, 0.3],
    )
    scores = sq.mixture_scores_from_ratios(ratios, [0.2, 0.3, 0.5])
    assert scores.dtype == jnp.float32
    assert np.isfinite(np.asarray(scores)).all()


def test_ratio_closure_report_flags_a_misdeclared_prior() -> None:
    rng = np.random.default_rng(26)
    ratios = np.exp(rng.normal(size=(2_000, 3)))
    ratios /= np.mean(ratios, axis=0, keepdims=True)
    weights = np.ones(ratios.shape[0])

    closed = sq.ratio_closure_report(ratios, weights)
    skew = np.asarray([1.4, 0.8, 0.9])
    biased = sq.ratio_closure_report(ratios * skew[None, :], weights)

    assert closed.max_residual < 1e-6
    assert biased.max_residual > 0.1
    assert closed.normalizers.shape == (3,)
    assert "max_residual" in closed.to_dict()


def test_ratio_closure_report_is_invariant_to_weight_scaling() -> None:
    rng = np.random.default_rng(27)
    ratios = np.exp(rng.normal(size=(100, 3)))
    weights = rng.uniform(0.1, 2.0, size=100)

    base = sq.ratio_closure_report(ratios, weights)
    scaled = sq.ratio_closure_report(ratios, 7.5 * weights)

    np.testing.assert_allclose(base.normalizers, scaled.normalizers, rtol=1e-6)


@pytest.mark.parametrize(
    ("posteriors", "priors", "message"),
    [
        ([[0.4, 0.4]], [0.5, 0.5], "sum to one"),
        ([[1.1, -0.1]], [0.5, 0.5], "nonnegative"),
        ([[0.5, 0.5]], [1.0, 0.0], "strictly positive"),
    ],
)
def test_invalid_posterior_inputs_fail(
    posteriors: list[list[float]],
    priors: list[float],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        sq.ratios_from_posteriors(posteriors, priors)


@pytest.mark.parametrize(
    ("ratios", "reference", "reference_component", "message"),
    [
        ([[1.0, -0.5]], [0.5, 0.5], -1, "nonnegative"),
        ([[1.0, 0.5]], [0.2, 0.2], -1, "sum to one"),
        ([[1.0, 0.5]], [0.5, 0.5], 2, "outside"),
        ([[0.0, 0.0]], [0.5, 0.5], -1, "strictly positive at every row"),
    ],
)
def test_invalid_mixture_score_inputs_fail(
    ratios: list[list[float]],
    reference: list[float],
    reference_component: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        sq.mixture_scores_from_ratios(
            ratios,
            reference,
            reference_component=reference_component,
        )


def test_reference_component_rejects_non_integer() -> None:
    with pytest.raises(TypeError, match="integer"):
        sq.mixture_scores_from_ratios([[1.0, 0.5]], [0.5, 0.5], reference_component=True)
