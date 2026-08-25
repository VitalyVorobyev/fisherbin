from __future__ import annotations

import jax.numpy as jnp
import numpy as np
import pytest

import scorequant as fb


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

    scores = fb.mixture_scores_from_posteriors(posteriors, priors, reference)

    np.testing.assert_allclose(scores, expected, rtol=1e-6, atol=1e-7)
    assert scores.shape == (2, 2)


def test_prior_correction_recovers_the_same_density_ratio_scores() -> None:
    rng = np.random.default_rng(20)
    ratios = np.exp(rng.normal(size=(50, 4)))
    reference = np.asarray([0.16, 0.14, 0.20, 0.50])
    uniform_prior = np.full(4, 0.25)
    skewed_prior = np.asarray([0.45, 0.15, 0.10, 0.30])

    uniform = fb.mixture_scores_from_posteriors(
        _posteriors_from_ratios(ratios, uniform_prior), uniform_prior, reference
    )
    skewed = fb.mixture_scores_from_posteriors(
        _posteriors_from_ratios(ratios, skewed_prior), skewed_prior, reference
    )

    np.testing.assert_allclose(uniform, skewed, rtol=1e-6, atol=1e-6)


def test_reference_component_changes_only_the_score_parameterization() -> None:
    rng = np.random.default_rng(22)
    posteriors = rng.dirichlet(np.ones(4), size=300)
    priors = np.full(4, 0.25)
    reference = np.asarray([0.2, 0.25, 0.15, 0.4])
    last_scores = fb.mixture_scores_from_posteriors(posteriors, priors, reference)
    first_scores = fb.mixture_scores_from_posteriors(
        posteriors, priors, reference, reference_component=0
    )
    config = fb.KMeansConfig(seed=7, n_init=4)

    last_labels = np.asarray(fb.fit_scores(last_scores, n_bins=6, config=config).labels)
    first_labels = np.asarray(fb.fit_scores(first_scores, n_bins=6, config=config).labels)

    np.testing.assert_array_equal(
        last_labels[:, None] == last_labels[None, :],
        first_labels[:, None] == first_labels[None, :],
    )


def test_class_permutation_preserves_scores_up_to_column_order() -> None:
    posteriors = np.asarray([[0.6, 0.3, 0.1], [0.15, 0.35, 0.5]])
    priors = np.asarray([0.5, 0.3, 0.2])
    reference = np.asarray([0.2, 0.3, 0.5])
    permutation = np.asarray([2, 0, 1])

    expected = fb.mixture_scores_from_posteriors(posteriors, priors, reference)
    permuted = fb.mixture_scores_from_posteriors(
        posteriors[:, permutation],
        priors[permutation],
        reference[permutation],
        reference_component=0,
    )

    np.testing.assert_allclose(permuted, expected)


def test_zero_posteriors_are_allowed_without_clipping() -> None:
    scores = fb.mixture_scores_from_posteriors(
        jnp.asarray([[1.0, 0.0, 0.0], [0.0, 0.25, 0.75]], dtype=jnp.float32),
        [0.4, 0.3, 0.3],
        [0.2, 0.3, 0.5],
    )
    assert scores.dtype == jnp.float32
    assert np.isfinite(np.asarray(scores)).all()


@pytest.mark.parametrize(
    ("posteriors", "priors", "reference", "reference_component", "message"),
    [
        ([[0.4, 0.4]], [0.5, 0.5], [0.5, 0.5], -1, "sum to one"),
        ([[1.1, -0.1]], [0.5, 0.5], [0.5, 0.5], -1, "nonnegative"),
        ([[0.5, 0.5]], [1.0, 0.0], [0.5, 0.5], -1, "strictly positive"),
        ([[0.5, 0.5]], [0.5, 0.5], [0.2, 0.2], -1, "sum to one"),
        ([[0.5, 0.5]], [0.5, 0.5], [0.5, 0.5], 2, "outside"),
    ],
)
def test_invalid_mixture_score_inputs_fail(
    posteriors: list[list[float]],
    priors: list[float],
    reference: list[float],
    reference_component: int,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        fb.mixture_scores_from_posteriors(
            posteriors,
            priors,
            reference,
            reference_component=reference_component,
        )


def test_reference_component_rejects_non_integer() -> None:
    with pytest.raises(TypeError, match="integer"):
        fb.mixture_scores_from_posteriors(
            [[0.5, 0.5]], [0.5, 0.5], [0.5, 0.5], reference_component=True
        )
