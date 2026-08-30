"""Shared logic and committed figure for the door3-classifier documentation page.

A two-component Gaussian mixture (`signal_pdf`, `background_pdf`) is separated
by a small `sklearn.linear_model.LogisticRegression` classifier whose
calibrated posteriors become component density ratios and then scores through
`scorequant.DensityRatioScore.from_classifier`. `exact_provider` builds the
analytic Bayes-optimal score for the same mixture, which is what makes the
retention ladder in `run_ladder` an honest comparison instead of a guess. This
module backs both the notebook (`examples/notebooks/door3_classifier.ipynb`)
and the committed figure `docs/examples/assets/door3-classifier.png`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from sklearn.linear_model import LogisticRegression

import scorequant as sq

ASSET_PATH = Path("docs/examples/assets/door3-classifier.png")

SIGNAL_MU, SIGNAL_SIGMA = 1.0, 0.5
BACKGROUND_MU, BACKGROUND_SIGMA = 0.0, 1.5
REFERENCE_FRACTIONS = (0.3, 0.7)


def signal_pdf(x: np.ndarray) -> np.ndarray:
    """Evaluate the signal component's normal density."""
    scale = SIGNAL_SIGMA * np.sqrt(2 * np.pi)
    return np.exp(-0.5 * ((x - SIGNAL_MU) / SIGNAL_SIGMA) ** 2) / scale


def background_pdf(x: np.ndarray) -> np.ndarray:
    """Evaluate the background component's normal density."""
    scale = BACKGROUND_SIGMA * np.sqrt(2 * np.pi)
    return np.exp(-0.5 * ((x - BACKGROUND_MU) / BACKGROUND_SIGMA) ** 2) / scale


def exact_posteriors(x: np.ndarray) -> np.ndarray:
    """Return the true Bayes posterior `[N, 2]` under equal training priors."""
    values = np.asarray(x)[:, 0]
    joint = np.stack([signal_pdf(values), background_pdf(values)], axis=1)
    return joint / joint.sum(axis=1, keepdims=True)


def exact_provider() -> sq.ScoreFunction:
    """Build the analytic (non-estimated) score provider for this mixture.

    Returns
    -------
    scorequant.ScoreFunction
        A provider declaring `ScoreProvenance(kind="exact")`, the ceiling
        that `run_ladder`'s classifier-based providers approach as training
        data grows.
    """
    return sq.ScoreFunction(
        lambda x: sq.mixture_scores_from_ratios(
            sq.ratios_from_posteriors(exact_posteriors(x), [0.5, 0.5]),
            list(REFERENCE_FRACTIONS),
        ),
        provenance=sq.ScoreProvenance(kind="exact", description="analytic Bayes posterior"),
    )


def make_features(x: np.ndarray) -> np.ndarray:
    """Build the quadratic feature the classifier needs to separate unequal variances."""
    return np.column_stack([x, x**2])


def draw_reference_mixture(seed: int, n: int) -> np.ndarray:
    """Draw `n` events from the mixture at `REFERENCE_FRACTIONS`.

    Parameters
    ----------
    seed
        Deterministic seed.
    n
        Number of events to draw.

    Returns
    -------
    numpy.ndarray
        Observations with shape ``[n, 1]``.
    """
    rng = np.random.default_rng(seed)
    is_signal = rng.random(n) < REFERENCE_FRACTIONS[0]
    x = np.where(
        is_signal,
        rng.normal(SIGNAL_MU, SIGNAL_SIGMA, n),
        rng.normal(BACKGROUND_MU, BACKGROUND_SIGMA, n),
    )
    return x[:, None]


def train_classifier(seed: int, n_per_class: int) -> LogisticRegression:
    """Train a quadratic-feature logistic regression on balanced component samples.

    Parameters
    ----------
    seed
        Deterministic seed for the labeled training draw.
    n_per_class
        Number of labeled events drawn from each component.

    Returns
    -------
    sklearn.linear_model.LogisticRegression
        A fitted classifier; class 0 is signal, class 1 is background.
    """
    rng = np.random.default_rng(seed)
    x_signal = rng.normal(SIGNAL_MU, SIGNAL_SIGMA, n_per_class)
    x_background = rng.normal(BACKGROUND_MU, BACKGROUND_SIGMA, n_per_class)
    x = np.concatenate([x_signal, x_background])
    y = np.concatenate([np.zeros(n_per_class), np.ones(n_per_class)])
    return LogisticRegression(max_iter=1000).fit(make_features(x), y)


def classifier_provider(model: LogisticRegression, *, description: str) -> sq.DensityRatioScore:
    """Wrap a fitted classifier as a classifier-derived ratio provider.

    Parameters
    ----------
    model
        A classifier exposing `predict_proba` in `[signal, background]` order.
    description
        Human-readable label recorded on the provider's provenance.

    Returns
    -------
    scorequant.DensityRatioScore
        Always carries `kind="estimated_ratio"` provenance with the training
        priors and mixture parameterization recorded.
    """

    def predict(x: np.ndarray) -> np.ndarray:
        return model.predict_proba(make_features(np.asarray(x)[:, 0]))

    return sq.DensityRatioScore.from_classifier(
        predict,
        [0.5, 0.5],
        sq.MixtureParameterization(list(REFERENCE_FRACTIONS)),
        description=description,
    )


@dataclass(frozen=True, slots=True)
class LadderStep:
    """One rung of the classifier-quality retention ladder.

    Attributes
    ----------
    n_per_class
        Labeled training events per component used to fit the classifier.
    surrogate_retention
        `QuantizerResult.evaluate_scores(...)` D-efficiency reported on the
        estimated scores themselves — what the library can honestly claim
        about the vectors it was given.
    true_retention
        D-efficiency of the *exact* score, evaluated at the labels the
        estimated-score quantizer actually produced. This is what the
        surrogate number is a proxy for, and the two can disagree sharply.
    closure_residual
        `ratio_closure_report(...).max_residual` of the classifier-derived
        ratios on the training measure: exact ratios integrate to one, so a
        large residual flags estimator bias before any quantizer is fitted.
    """

    n_per_class: int
    surrogate_retention: float
    true_retention: float
    closure_residual: float


def run_ladder(
    *,
    n_per_class_values: tuple[int, ...],
    n_train: int,
    n_test: int,
    n_bins: int = 4,
) -> list[LadderStep]:
    """Fit a quantizer from an estimated score at each rung of classifier quality.

    Parameters
    ----------
    n_per_class_values
        Labeled training-set sizes (per component) to try, smallest first.
    n_train, n_test
        Reference-mixture sample sizes used to fit and evaluate each quantizer.
    n_bins
        Requested bin budget, shared across every rung.

    Returns
    -------
    list of LadderStep
        One entry per `n_per_class_values` entry, in order.
    """
    oracle = exact_provider()
    test_observations = draw_reference_mixture(999, n_test)
    oracle_test_scores = np.asarray(oracle.score(test_observations))
    train_observations = draw_reference_mixture(2026, n_train)

    steps: list[LadderStep] = []
    for index, n_per_class in enumerate(n_per_class_values):
        model = train_classifier(101 + index, n_per_class)
        provider = classifier_provider(
            model, description=f"logistic regression, {n_per_class} events per class"
        )
        result = sq.fit_quantizer(
            sq.ObservationSample(train_observations),
            provider=provider,
            n_bins=n_bins,
            criterion=sq.DOptimality(),
            config=sq.DExchangeConfig(seed=7),
        )
        surrogate = float(
            result.evaluate_scores(provider.score(test_observations)).geometric_mean_retention
        )
        labels = np.asarray(result.predict_scores(provider.score(test_observations)))
        true_retention = float(
            sq.information_report(
                oracle_test_scores, labels, n_bins=result.n_bins
            ).geometric_mean_retention
        )
        closure = sq.ratio_closure_report(
            provider.ratio(train_observations), np.ones(train_observations.shape[0])
        )
        steps.append(LadderStep(n_per_class, surrogate, true_retention, closure.max_residual))
    return steps


def make_figure(steps: list[LadderStep]) -> Figure:
    """Render the surrogate-versus-true retention ladder.

    Parameters
    ----------
    steps
        Ladder rungs from `run_ladder`, smallest training set first.

    Returns
    -------
    matplotlib.figure.Figure
        A single-panel bar comparison of surrogate and true retention.
    """
    figure, ax = plt.subplots(figsize=(7, 4))
    labels = [f"{step.n_per_class}/class" for step in steps]
    x = np.arange(len(steps))
    width = 0.35
    surrogate_values = [s.surrogate_retention for s in steps]
    true_values = [s.true_retention for s in steps]
    ax.bar(x - width / 2, surrogate_values, width, label="surrogate (self-reported)")
    ax.bar(x + width / 2, true_values, width, label="true (exact scores, estimated labels)")
    ax.set(
        xticks=x,
        xticklabels=labels,
        ylabel="D-efficiency",
        xlabel="classifier training set size",
        title="Door 3: the surrogate-information caveat",
        ylim=(0.0, 1.05),
    )
    ax.legend()
    return figure


def main() -> None:
    """Regenerate and save the committed door3 figure."""
    steps = run_ladder(n_per_class_values=(15, 60, 300), n_train=400, n_test=600)
    figure = make_figure(steps)
    ASSET_PATH.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(ASSET_PATH, dpi=160)
    plt.close(figure)


if __name__ == "__main__":
    main()
