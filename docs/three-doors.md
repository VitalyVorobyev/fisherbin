# Three doors

Everything ScoreQuant optimizes is a weighted table of score rows. There are three ways to arrive
at one, and they differ in what you already possess: the scores themselves, a model that generates
them, or a classifier that implies them.

| Door | You have | You supply | Provenance |
| --- | --- | --- | --- |
| **1. Precomputed** | `(event, score)` rows and their weights | `ScoreSample(scores, weights)` | whatever you declare |
| **2. Component or analytic model** | Component densities, an intensity, or a score callback | `ObservationSample` / `IntegrationSource` **+** `LinearComponentScore` or `ScoreFunction` | usually `exact` |
| **3. Trained classifier** | A calibrated probability callback on measurement space | `ObservationSample` **+** `ClassifierScore(...)` with a transform | always `estimated_classifier` |

Every snippet on this page runs. They share one namespace, so the imports below come first.

```python
import numpy as np

import scorequant as sq
```

## Sources and providers are separate contracts

A **source** supplies the reference measure — which events exist and how much each one weighs. A
**score provider** supplies the observation-to-score map. Neither substitutes for the other, and a
score callback on its own is deliberately not enough to fit anything: without a measure there is no
score law to optimize against.

| Source | Meaning | Provider |
| --- | --- | --- |
| `ScoreSample(scores, weights)` | A finite weighted table already in score space | must be omitted |
| `ObservationSample(X, weights)` | A finite weighted table of observations | required |
| `IntegrationSource(bounds, density=...)` | A bounded box with an explicit density and deterministic Gauss-Legendre nodes | required |

`fit_quantizer` enforces the pairing:

```python
sample = sq.ScoreSample(np.random.default_rng(0).normal(size=(64, 2)))
observations = np.asarray(sample.scores)
provider = sq.ScoreFunction(lambda X: np.asarray(X))

try:
    sq.fit_quantizer(sample, score=provider, n_bins=3)
    raise AssertionError("a ScoreSample must reject a provider")
except ValueError as error:
    score_sample_rejects_provider = str(error)

try:
    sq.fit_quantizer(sq.ObservationSample(observations), n_bins=3)
    raise AssertionError("an ObservationSample must require a provider")
except ValueError as error:
    observation_sample_requires_provider = str(error)
```

The providers themselves are framework-neutral. `ScoreFunction` wraps any callable
`[N, D] -> [N, P]`; `LinearComponentScore` evaluates a frozen linear component model;
`ClassifierScore` wraps a ready probability callback together with a pure transform. Each one
carries a `provenance` and a `.score(X)` method you can call yourself — which is exactly how doors 2
and 3 feed `optimize_partition`, since that task takes score rows rather than a source.

## Door 1: precomputed scores

Use this when the scores already exist: an analytic model you evaluated elsewhere, weight
derivatives from a simulator, or a score column shipped with a dataset. `ScoreSample` validates the
table and records where it came from.

```python
rng = np.random.default_rng(7)
scores = rng.normal(size=(2_000, 2))  # N(mu, I2) at mu0 = 0 has s(x) = x
weights = np.ones(scores.shape[0])

door1 = sq.ScoreSample(
    scores,
    weights,
    provenance=sq.ScoreProvenance(kind="exact", reference_point=(0.0, 0.0)),
)

quantizer = sq.fit_quantizer(
    door1, n_bins=6, criterion=sq.DOptimality(), config=sq.DExchangeConfig(seed=7)
)
partition = sq.optimize_partition(
    scores, weights=weights, n_bins=6, config=sq.DExchangeConfig(seed=7)
)
```

The same rows serve either task. `quantizer.predict_scores(new_scores)` labels future events;
`partition.labels` labels these 2000 rows and stops there.

`ScoreProvenance(kind=...)` accepts `"exact"`, `"autodiff"`, `"estimated_classifier"`,
`"custom_estimated"`, and the default `"unknown"`. Only the first two let a result report
`information_kind == "exact_fisher"`, so declaring provenance is how you decide whether the
library is allowed to call its output Fisher information.

## Door 2: a component or analytic model

### Linear component models

For a linear intensity \(\lambda(x;\theta)=\sum_k\theta_k\phi_k(x)\), the event score is
\(s_k=\phi_k/(\phi^\top\theta_0)\). Declare the components and the reference coefficients, and the
provider builds the scores.

```python
def peak(X):
    return np.exp(-0.5 * ((X[:, 0] - 1.0) / 0.4) ** 2)


def flat(X):
    return np.ones(X.shape[0])


model = sq.LinearComponents(
    components={"peak": peak, "flat": flat},
    coefficients={"peak": 1.0, "flat": 0.5},
    variables=["mass"],
)
component_score = sq.LinearComponentScore(model)
```

With Monte Carlo events, the source carries the measure. A uniform draw reweighted by the reference
intensity is one honest way to build it:

```python
events = rng.uniform(-2.0, 3.0, size=(2_000, 1))
intensity = np.asarray(model.evaluate_components(events)) @ np.asarray(model.coefficients)

quantizer = sq.fit_quantizer(
    sq.ObservationSample(events, intensity),
    score=component_score,
    n_bins=5,
    config=sq.DExchangeConfig(seed=11),
)
grid = np.linspace(-2.0, 3.0, 100)[:, None]
data_bins = quantizer.predict_scores(component_score.score(grid))
```

Prediction takes scores, never observations. Converting `X` to scores stays a line you wrote.

### Bounded models without a sample

When the model is low-dimensional and bounded, no sampling is needed: `IntegrationSource`
materializes a deterministic tensor-product Gauss-Legendre grid and weights it by an explicit
density.

```python
source = sq.IntegrationSource(
    [[-2.0, 3.0]],
    density=lambda X: peak(X) + 0.5 * flat(X),
    quadrature=sq.GaussLegendreConfig(order=96),
)
quantizer = sq.fit_quantizer(
    source, score=component_score, n_bins=5, config=sq.DExchangeConfig(seed=11)
)
```

Bounds have shape `[D, 2]` with strictly ordered endpoints, and the density is mandatory — bounds
alone never imply a uniform measure. Point count is `order ** D`, so `max_points` refuses an
accidental high-dimensional explosion. Use an empirical source for anything beyond a few
dimensions.

### An exact score callback

If you can differentiate the log likelihood yourself, wrap the callable directly and declare it.

```python
exact_score = sq.ScoreFunction(
    lambda X: np.asarray(X),  # N(mu, I2) at mu0 = 0
    provenance=sq.ScoreProvenance(kind="exact", reference_point=(0.0, 0.0)),
)
quantizer = sq.fit_quantizer(
    sq.ObservationSample(rng.normal(size=(1_000, 2))),
    score=exact_score,
    n_bins=4,
    config=sq.DExchangeConfig(seed=2),
)
```

### Components you already evaluated

If the component matrix \(\Phi\) is already in memory, `scores_from_components` is the explicit
adapter — it is a conversion, not a fitting task, so you choose the task afterwards.

```python
Phi = np.asarray(model.evaluate_components(events))
component_scores = sq.scores_from_components(Phi, model.coefficients)
partition = sq.optimize_partition(
    component_scores, weights=intensity, n_bins=5, config=sq.DExchangeConfig(seed=11)
)
```

## Door 3: a trained classifier

Training, feature preprocessing, cross-fitting, and calibration all stay in your application.
ScoreQuant begins at the ready probability callback and applies a pure, prior-corrected transform
to reconstruct the relative densities the score is built from. Two transforms are provided.

### Multiclass mixture posteriors

For a \(K\)-component mixture whose fractions are the parameters, calibrated posteriors
\(q_k(x)\) estimated under class priors \(\pi_k\) give component density ratios
\(r_k=q_k/\pi_k\). With one component held dependent by the simplex constraint and \(\theta\) the
mixture fractions at the reference point, the scores are
\((r_k-r_{\text{ref}})/\sum_j \theta_j r_j\), which is what `MixturePosteriorTransform` computes.

```python
def predict_proba(X):
    x = np.asarray(X)[:, 0]
    signal = np.exp(-0.5 * ((x - 1.0) / 0.5) ** 2) / 0.5
    background = np.exp(-0.5 * (x / 1.5) ** 2) / 1.5
    joint = np.stack([signal, background], axis=1)  # equal training priors
    return joint / joint.sum(axis=1, keepdims=True)


classifier_score = sq.ClassifierScore(
    predict_proba,
    sq.MixturePosteriorTransform(class_priors=[0.5, 0.5], reference_fractions=[0.3, 0.7]),
    description="calibrated two-component classifier",
)

is_signal = rng.random(2_000) < 0.3
mixture = np.where(is_signal, rng.normal(1.0, 0.5, 2_000), rng.normal(0.0, 1.5, 2_000))[:, None]
quantizer = sq.fit_quantizer(
    sq.ObservationSample(mixture),
    score=classifier_score,
    n_bins=4,
    config=sq.DExchangeConfig(seed=5),
)
information_kind = quantizer.information_kind  # "supplied_score_surrogate"
```

Posteriors must be `[N, K]`, nonnegative and row-normalized; class priors and reference fractions
must be strictly positive and sum to one. The transform does not calibrate, clip, or renormalize
classifier output — those operations change the implied density ratios and belong upstream.

### Central log-ratio classifiers

When the parameter is not a mixture fraction, a classifier trained to separate samples generated at
\(\theta_0-\delta\) from \(\theta_0+\delta\) estimates a central finite-difference score. Input has
shape `[N, P, 2]` in `(minus, plus)` order (a `[N, 2]` input is accepted for a single direction),
and `CentralLogRatioTransform` subtracts the training-prior log odds and divides by \(2\delta\).

```python
delta = 0.1


def central_probabilities(X):
    plus = 1.0 / (1.0 + np.exp(-2.0 * delta * np.asarray(X)[:, 0]))
    return np.stack([1.0 - plus, plus], axis=1)


central_score = sq.ClassifierScore(
    central_probabilities,
    sq.CentralLogRatioTransform([delta], [0.5, 0.5]),
)
recovered = np.asarray(central_score.score(np.linspace(-3.0, 3.0, 7)[:, None])).ravel()
```

Here the classifier is the exact Bayes rule for a Gaussian location model, so `recovered` reproduces
\(s(x)=x\) to floating-point accuracy — a useful sanity check to run against your own callback
before trusting its scores.

### Estimated scores are surrogate information

`ClassifierScore` always records `kind="estimated_classifier"`, so `information_kind` reads
`"supplied_score_surrogate"`. The between-cell algebra is exact for the vectors you supplied, but
the vectors are estimates: what the report measures is \(\operatorname{Var}(E[\hat s\mid q(\hat s)])\),
not \(\operatorname{Var}(E[s\mid q(\hat s)])\). To measure the second, label events with the
estimated scores and then evaluate an exact score under those labels. Classifier error is not
quantization loss, and the library will not let one be reported as the other.

## Validation samples

Any door can supply a validation source, and the rules are the same everywhere: it must use the
training parameter order and score dimension, a `ScoreSample` validation set never takes a provider
even when the training source has one, and it is **diagnostic only**. It never influences gradients,
stopping, initialization selection, or checkpoint choice.

```python
train_scores = rng.normal(size=(1_500, 2))
holdout_scores = rng.normal(size=(500, 2))

quantizer = sq.fit_quantizer(
    sq.ScoreSample(train_scores),
    validation=sq.ScoreSample(holdout_scores),
    n_bins=5,
    criterion=sq.NormalizedTrace(),
    config=sq.KMeansConfig(seed=4, n_init=4),
)
train_efficiency = float(quantizer.train_report.geometric_mean_retention)
holdout_efficiency = float(quantizer.validation_report.geometric_mean_retention)
```

A frozen rule can also be scored on any later sample without refitting, through
`quantizer.evaluate_scores(scores, weights)`.

## Shape and measure contracts

- Scores: finite `[N, P]` with `N > 0` and `P > 0`.
- Observations: finite `[N, D]`.
- Weights: finite, nonnegative `[N]`, at least one positive. Zero-weight rows stay predictable and
  contribute nothing.
- Multiclass posteriors: nonnegative `[N, K]`, row-normalized, with strictly positive normalized
  priors and reference fractions.
- Central classifier probabilities: strictly positive `[N, P, 2]`, normalized on the last axis.
- Integration bounds: finite `[D, 2]` with strictly ordered endpoints, plus an explicit density.

Numerically singular directions are projected out. Scores are never centered.
