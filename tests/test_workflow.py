from __future__ import annotations

import json

import jax.numpy as jnp
import numpy as np
import pytest

import fisherbin as fb


def _model() -> fb.LinearComponents:
    def signal(X: np.ndarray) -> np.ndarray:
        energy, angle = X.T
        return 0.1 + np.exp(-0.5 * ((energy - 0.4) / 0.2) ** 2) * (1 + 0.3 * angle)

    def background(X: np.ndarray) -> np.ndarray:
        energy, angle = X.T
        return 0.2 + (1 - energy) ** 2 * (1 - 0.2 * angle)

    return fb.LinearComponents(
        components={"signal": signal, "background": background},
        # Coefficient mapping order is deliberately different from component order.
        coefficients={"background": 0.4, "signal": 1.0},
        variables=("energy", "cos_theta"),
    )


def _observations(seed: int, size: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.column_stack([rng.uniform(0, 1, size), rng.uniform(-1, 1, size)])


def _same_partition(left: np.ndarray, right: np.ndarray) -> None:
    np.testing.assert_array_equal(left[:, None] == left[None, :], right[:, None] == right[None, :])


def test_named_model_evaluation_preserves_explicit_metadata() -> None:
    X = _observations(1, 50)
    weights = np.linspace(0.5, 1.5, len(X))
    model = _model()
    problem = model.evaluate(X, weights=weights)
    assert problem.components.shape == (50, 2)
    assert problem.component_names == ("signal", "background")
    assert tuple(np.asarray(problem.coefficients)) == (1.0, 0.4)
    assert problem.variables == ("energy", "cos_theta")
    np.testing.assert_allclose(problem.scores, problem.components / problem.density[:, None])
    json.dumps(problem.to_dict(), allow_nan=False)


def test_all_three_entry_points_are_equivalent() -> None:
    X = _observations(2, 300)
    weights = np.linspace(0.2, 1.8, len(X))
    model = _model()
    problem = model.evaluate(X, weights=weights)
    config = fb.KMeansConfig(seed=9, n_init=3)

    score_result = fb.fit_scores(problem.scores, weights=weights, n_bins=5, config=config)
    component_result = fb.fit_components(problem, n_bins=5, config=config)
    model_result = fb.fit(X, model=model, weights=weights, n_bins=5, config=config)

    _same_partition(np.asarray(score_result.labels), np.asarray(component_result.labels))
    _same_partition(np.asarray(score_result.labels), np.asarray(model_result.labels))
    np.testing.assert_allclose(score_result.centers, component_result.centers)
    np.testing.assert_allclose(score_result.centers, model_result.centers)
    assert model_result.report() is model_result.train_report
    assert "D-efficiency" in str(model_result.report())


def test_result_views_delegate_common_fitted_state() -> None:
    model_result = fb.fit(_observations(11, 120), model=_model(), n_bins=4)
    component_result = model_result.component_result
    score_result = component_result.score_result

    assert model_result.config is score_result.config
    assert model_result.trace is score_result.trace
    assert model_result.train_report is score_result.train_report
    assert component_result.config is score_result.config
    assert component_result.labels is score_result.labels
    assert component_result.report() is score_result.train_report


def test_frozen_model_predicts_new_physical_observations() -> None:
    train = _observations(3, 250)
    data = _observations(4, 80)
    model = _model()
    result = fb.fit(train, model=model, n_bins=6)
    data_labels = result.predict(data)
    direct_labels = result.component_result.score_result.predict(model.evaluate(data).scores)
    np.testing.assert_array_equal(data_labels, direct_labels)
    counts = np.bincount(np.asarray(data_labels), minlength=result.n_bins)
    assert counts.sum() == len(data)
    assert len(counts) == result.n_bins
    payload = result.to_dict()
    assert "components" not in payload["model"]
    json.dumps(payload, allow_nan=False)


def test_validation_is_diagnostic_through_every_representation() -> None:
    train = _observations(5, 240)
    validation = _observations(6, 120)
    model = _model()
    problem = model.evaluate(train)
    validation_problem = model.evaluate(validation)

    component_result = fb.fit_components(
        problem,
        n_bins=5,
        validation_components=validation_problem,
    )
    model_result = fb.fit(
        train,
        model=model,
        n_bins=5,
        validation_X=validation,
    )
    assert component_result.validation_report is not None
    assert model_result.validation_report is not None
    np.testing.assert_allclose(component_result.centers, model_result.centers)


def test_sequence_model_uses_stable_generated_names() -> None:
    model = fb.LinearComponents(
        components=[lambda X: np.ones(len(X)), lambda X: 1 + X[:, 0]],
        coefficients=[1.0, 0.5],
    )
    problem = model.evaluate(_observations(7, 20))
    assert problem.component_names == ("component_0", "component_1")


def test_component_and_model_failures_are_explicit() -> None:
    X = _observations(8, 20)
    with pytest.raises(ValueError, match="keys must match"):
        fb.LinearComponents(
            components={"a": lambda X: np.ones(len(X))},
            coefficients={"b": 1.0},
        )
    with pytest.raises(ValueError, match="must return shape"):
        fb.LinearComponents(
            components=[lambda X: np.ones((len(X), 1))], coefficients=[1.0]
        ).evaluate(X)
    with pytest.raises(ValueError, match="variables"):
        fb.LinearComponents(
            components=[lambda X: np.ones(len(X))],
            coefficients=[1.0],
            variables=["only_one"],
        ).evaluate(X)
    with pytest.raises(ValueError, match="strictly positive"):
        fb.LinearProblem(components=-np.ones((20, 1)), coefficients=[1.0])
    problem = _model().evaluate(X)
    with pytest.raises(ValueError, match="must be omitted"):
        fb.fit_components(problem, coefficients=[1.0, 0.4], n_bins=3)
    with pytest.raises(TypeError, match="LinearComponents"):
        fb.fit(X, model=object(), n_bins=3)


def test_component_result_accepts_raw_matrix_and_predicts_components() -> None:
    model = _model()
    train = model.evaluate(_observations(9, 180))
    data = model.evaluate(_observations(10, 60))
    result = fb.fit_components(
        train.components,
        coefficients=train.coefficients,
        component_names=train.component_names,
        n_bins=4,
    )
    labels = result.predict(data.components)
    assert labels.shape == (60,)
    assert result.evaluate(data.components).effective_rank == 2


def test_linear_problem_arrays_are_jax_compatible() -> None:
    problem = fb.LinearProblem(
        components=jnp.asarray([[1.0, 0.2], [0.5, 1.0]]),
        coefficients=jnp.asarray([1.0, 0.3]),
    )
    assert isinstance(problem.scores, jnp.ndarray)
