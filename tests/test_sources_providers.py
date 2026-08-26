import numpy as np
import pytest

import scorequant as sq
from examples.synthetic_problems import signal_background_shape


def test_score_callback_requires_a_reference_measure() -> None:
    provider = sq.ScoreFunction(lambda values: values)
    with pytest.raises(TypeError, match="source"):
        sq.fit_quantizer(provider, n_bins=2)  # type: ignore[arg-type]


def test_observation_and_score_sources_are_equivalent() -> None:
    observations = np.linspace(-1, 1, 60)[:, None]
    weights = np.linspace(1, 2, 60)
    provenance = sq.ScoreProvenance(kind="exact", reference_point=(0.0,))
    provider = sq.ScoreFunction(lambda values: np.asarray(values), provenance=provenance)
    config = sq.KMeansConfig(seed=3, n_init=3)
    direct = sq.fit_quantizer(
        sq.ScoreSample(observations, weights, provenance=provenance),
        n_bins=3,
        criterion=sq.NormalizedTrace(),
        config=config,
    )
    composed = sq.fit_quantizer(
        sq.ObservationSample(observations, weights),
        score=provider,
        n_bins=3,
        criterion=sq.NormalizedTrace(),
        config=config,
    )
    assert np.array_equal(
        np.asarray(direct.predict_scores(observations)),
        np.asarray(composed.predict_scores(observations)),
    )
    assert composed.provenance.exact_fisher
    assert composed.information_kind == "exact_fisher"


def test_precomputed_score_validation_accepts_observation_training() -> None:
    observations = np.linspace(-1, 1, 60)[:, None]
    provider = sq.ScoreFunction(lambda values: np.asarray(values))
    result = sq.fit_quantizer(
        sq.ObservationSample(observations),
        score=provider,
        validation=sq.ScoreSample(observations[::3]),
        n_bins=3,
        criterion=sq.NormalizedTrace(),
        config=sq.KMeansConfig(seed=3, n_init=3),
    )
    assert result.validation_report is not None


def test_bounded_quadrature_matches_symmetric_reference_law() -> None:
    source = sq.IntegrationSource(
        [[-1.0, 1.0]],
        density=lambda values: np.full(len(values), 0.5),
        quadrature=sq.GaussLegendreConfig(order=20),
    )
    provider = sq.ScoreFunction(
        lambda values: np.asarray(values),
        provenance=sq.ScoreProvenance(kind="exact"),
    )
    materialized = source.materialize()
    total_weight = float(np.sum(np.asarray(materialized.weights)))
    second_moment = float(
        np.sum(
            np.asarray(materialized.weights)
            * np.square(np.asarray(materialized.observations[:, 0]))
        )
        / total_weight
    )
    assert total_weight == pytest.approx(1.0, abs=1e-12)
    assert second_moment == pytest.approx(1 / 3, abs=1e-12)
    result = sq.fit_quantizer(
        source,
        score=provider,
        n_bins=2,
        config=sq.DExchangeConfig(seed=2, n_init=3, max_scans=200),
    )
    labels = np.asarray(result.predict_scores([[-0.5], [0.5]]))
    assert labels[0] != labels[1]
    assert result.source_kind == "integration_source"


def test_quadrature_rejects_implicit_measure_and_capacity_explosion() -> None:
    with pytest.raises(TypeError):
        sq.IntegrationSource([[-1.0, 1.0]])  # type: ignore[call-arg]
    source = sq.IntegrationSource(
        np.tile([[-1.0, 1.0]], (5, 1)),
        density=lambda values: np.ones(len(values)),
        quadrature=sq.GaussLegendreConfig(order=20, max_points=1000),
    )
    with pytest.raises(ValueError, match="exceeding max_points"):
        source.materialize()


def test_central_classifier_transform_corrects_training_priors() -> None:
    deltas = [0.2]
    priors = [0.25, 0.75]
    target_score = np.array([[-1.5], [0.4]])
    prior_odds = priors[1] / priors[0]
    odds = prior_odds * np.exp(2 * deltas[0] * target_score[:, 0])
    probabilities = np.column_stack([1 / (1 + odds), odds / (1 + odds)])
    transform = sq.CentralLogRatioTransform(deltas, priors)
    assert np.allclose(np.asarray(transform.transform(probabilities)), target_score)


def test_classifier_provider_is_always_estimated() -> None:
    transform = sq.CentralLogRatioTransform([0.1], [0.5, 0.5])

    def predict(values: object) -> np.ndarray:
        observations = np.asarray(values)[:, 0]
        plus = 1 / (1 + np.exp(-0.2 * observations))
        return np.column_stack([1 - plus, plus])

    provider = sq.ClassifierScore(
        predict,
        transform,
        description="ready calibrated model",
    )
    assert provider.provenance.kind == "estimated_classifier"
    assert not provider.provenance.exact_fisher
    assert provider.provenance.metadata["transform"] == "central_log_ratio"
    assert provider.provenance.metadata["deltas"] == [0.1]
    result = sq.fit_quantizer(
        sq.ObservationSample(np.arange(12, dtype=float)[:, None]),
        score=provider,
        n_bins=2,
        criterion=sq.NormalizedTrace(),
        config=sq.KMeansConfig(n_init=2),
    )
    assert result.information_kind == "supplied_score_surrogate"


def test_integration_source_end_to_end_with_two_score_columns() -> None:
    """`fit_quantizer(IntegrationSource(...), score=...)` with a multi-parameter score.

    The existing quadrature test above covers only a single score column from an
    identity provider. Two score directions (a signal fraction and one
    background-shape nuisance) exercise the bounded-quadrature path the way a real
    linear-component model would use it, closing that coverage gap.
    """
    problem = signal_background_shape(background_rates=(2.5,), n_bins=4)

    def signal_component(x: np.ndarray) -> np.ndarray:
        return problem.signal_density(np.asarray(x)[:, 0])

    def background_component(x: np.ndarray) -> np.ndarray:
        return problem.background_densities[0](np.asarray(x)[:, 0])

    model = sq.LinearComponents(
        components={"signal": signal_component, "background": background_component},
        coefficients={
            "signal": float(problem.coefficients[0]),
            "background": float(problem.coefficients[1]),
        },
        variables=["x"],
    )
    provider = sq.LinearComponentScore(model)

    source = sq.IntegrationSource(
        problem.bounds, density=problem.intensity, quadrature=sq.GaussLegendreConfig(order=48)
    )
    result = sq.fit_quantizer(
        source,
        score=provider,
        n_bins=problem.n_bins,
        criterion=sq.DOptimality(),
        config=sq.DExchangeConfig(seed=50, n_init=4),
    )
    assert result.source_kind == "integration_source"
    assert result.transform.rank == 2

    test = problem.test
    report = result.evaluate_scores(test.scores, test.weights)
    assert report.geometric_mean_retention > 0.9

    profiled = sq.profiled_information_report(
        test.scores,
        np.asarray(result.predict_scores(test.scores)),
        interest=problem.interest,
        weights=test.weights,
        n_bins=problem.n_bins,
    )
    assert profiled.geometric_mean_retention > 0.9
