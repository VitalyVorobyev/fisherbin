# Three doors

Everything ScoreQuant optimizes is a weighted table of score rows. There are three ways to arrive
at one, and they differ in which statistical representation you already possess: the scores
themselves, the component densities that generate them, or the component density *ratios* — the
minimal sufficient input, since the score is the gradient of a log density ratio and any common
event-wise factor cancels.

| Door | You have | You supply | Provenance |
| --- | --- | --- | --- |
| **1. Precomputed** | `(event, score)` rows and their weights | `ScoreSample(scores, weights)` | whatever you declare |
| **2. Component or analytic model** | Component densities, an intensity, or a score callback | `ObservationSample` / `IntegrationSource` **+** `LinearComponentScore` or `ScoreFunction` | usually `exact` |
| **3. Density ratios** | A ratio callback — analytic, or estimated by a calibrated classifier or a direct ratio estimator | `ObservationSample` **+** `DensityRatioScore(...)` or `CentralLogRatioScore(...)` | `estimated_ratio` unless analytic |

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
    sq.fit_quantizer(sample, provider=provider, n_bins=3)
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
`DensityRatioScore` maps observations to model density ratios and applies a declared
parameterization; `CentralLogRatioScore` turns paired minus/plus probabilities into central
finite-difference scores. Each one carries a `provenance` and a `.score(X)` method you can call
yourself — which is exactly how doors 2 and 3 feed `optimize_partition`, since that task takes
score rows rather than a source.

One distinction runs through everything downstream. **Model density ratios** — \(\phi_k/\phi_{\rm ref}\)
or \(p(x\mid\theta)/p(x\mid\theta_0)\) — are a statistical representation: they build scores and
enter through a provider. **Importance ratios** — \(p_{\theta_0}(x)/g(x)\) for a sample drawn from
a proposal \(g\) — reweight expectations and enter as source *weights*, never through a provider.
The two kinds never share an argument.

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

`ScoreProvenance(kind=...)` accepts `"exact"`, `"autodiff"`, `"estimated_ratio"`,
`"custom_estimated"`, and the default `"unknown"`. Only the first two let a result report
`information_kind == "exact_fisher"`, so declaring provenance is how you decide whether the
library is allowed to call its output Fisher information. Ratio-derived scores additionally carry
a structured `provenance.ratio` record — estimator, parameterization, training priors,
calibration, finite-difference offsets — sufficient to reconstruct how the representation was
obtained.

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
    provider=component_score,
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
    source, provider=component_score, n_bins=5, config=sq.DExchangeConfig(seed=11)
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
    provider=exact_score,
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

## Door 3: density ratios

The score never needs absolute densities. For a mixture or intensity model it is a function of the
component density ratios alone, and the ratios are defined only up to a common event-wise factor —
any gauge works. Door 3 is therefore the door of the *density-ratio oracle*: an analytic ratio
formula, a calibrated classifier, a direct ratio estimator in the KLIEP/uLSIF family, a calibrated
neural likelihood-ratio estimator, or an externally supplied ratio model. Estimation, feature
preprocessing, cross-fitting, and calibration all stay in your application; ScoreQuant begins at
the ready ratio callback.

One warning applies to every backend: a ranking score or an arbitrary monotone transform of a
likelihood ratio is **not** enough. Score construction needs a quantitatively meaningful ratio or
log-ratio, so calibration or a ratio-estimation loss is required upstream.

### From ratios to scores

`DensityRatioScore` pairs a ratio callback `[N, D] -> [N, K]` with a declared parameterization:
`MixtureParameterization(reference_fractions)` for a normalized mixture (scores
\((r_k-r_{\text{ref}})/\sum_j \theta_j r_j\), one component simplex-dependent) or
`IntensityParameterization(coefficients)` for an extended model (scores
\(r_k/\sum_j \theta_j r_j\), all \(K\) columns kept).

A classifier is one estimator of ratios: calibrated posteriors \(q_k(x)\) estimated under training
priors \(\pi_k\) give \(r_k = q_k/\pi_k\) up to a common factor, which is
`ratios_from_posteriors`. The chain is explicit —

```python
def predict_proba(X):
    x = np.asarray(X)[:, 0]
    signal = np.exp(-0.5 * ((x - 1.0) / 0.5) ** 2) / 0.5
    background = np.exp(-0.5 * (x / 1.5) ** 2) / 1.5
    joint = np.stack([signal, background], axis=1)  # equal training priors
    return joint / joint.sum(axis=1, keepdims=True)


posteriors = predict_proba(np.linspace(-3.0, 3.0, 7)[:, None])
ratios = sq.ratios_from_posteriors(posteriors, [0.5, 0.5])
scores = sq.mixture_scores_from_ratios(ratios, [0.3, 0.7])
```

— and `DensityRatioScore.from_classifier` packages it as a provider with full provenance:

```python
classifier_score = sq.DensityRatioScore.from_classifier(
    predict_proba,
    [0.5, 0.5],
    sq.MixtureParameterization([0.3, 0.7]),
    description="calibrated two-component classifier",
)

is_signal = rng.random(2_000) < 0.3
mixture = np.where(is_signal, rng.normal(1.0, 0.5, 2_000), rng.normal(0.0, 1.5, 2_000))[:, None]
quantizer = sq.fit_quantizer(
    sq.ObservationSample(mixture),
    provider=classifier_score,
    n_bins=4,
    config=sq.DExchangeConfig(seed=5),
)
information_kind = quantizer.information_kind  # "supplied_score_surrogate"
```

Any other ratio backend enters through the same constructor with its own callback:
`sq.DensityRatioScore(my_ratio_model, sq.MixtureParameterization([0.3, 0.7]))`. An *analytic*
ratio may declare `provenance=sq.ScoreProvenance(kind="exact")`; a classifier-derived one cannot.
When the training priors are proportional to the reference fractions, the intensity denominator
\(\sum_j \theta_j q_j/\pi_j\) is identically one and the scores reduce to the prior-corrected
ratios themselves.

Posteriors must be `[N, K]`, nonnegative and row-normalized; ratios must be nonnegative; class
priors and reference fractions must be strictly positive and sum to one. Nothing calibrates,
clips, or renormalizes classifier output — those operations change the implied density ratios and
belong upstream.

### The closure check

Exact ratios relative to the training measure integrate to one under it:
\(\sum_i w_i r_{ik}/\sum_i w_i = 1\) for every component. `ratio_closure_report` measures the
residual before any quantizer is fitted:

```python
closure = sq.ratio_closure_report(classifier_score.ratio(mixture), np.ones(mixture.shape[0]))
closure_residual = closure.max_residual
```

A large residual flags estimator bias, a misdeclared training prior, or a measure mismatch — model
error, not compression loss. The test is necessary but not sufficient: closure never upgrades
estimated provenance to exact.

### Central log-ratio classifiers

When the parameter is not a mixture fraction, a classifier trained to separate samples generated at
\(\theta_0-\delta\) from \(\theta_0+\delta\) estimates the directional log density ratio, and its
central finite difference is a score estimate. Input has shape `[N, P, 2]` in `(minus, plus)` order
(a `[N, 2]` input is accepted for a single direction), and `CentralLogRatioScore` subtracts the
training-prior log odds and divides by \(2\delta\).

```python
delta = 0.1


def central_probabilities(X):
    plus = 1.0 / (1.0 + np.exp(-2.0 * delta * np.asarray(X)[:, 0]))
    return np.stack([1.0 - plus, plus], axis=1)


central_score = sq.CentralLogRatioScore(central_probabilities, [delta], [0.5, 0.5])
recovered = np.asarray(central_score.score(np.linspace(-3.0, 3.0, 7)[:, None])).ravel()
```

Here the classifier is the exact Bayes rule for a Gaussian location model, so `recovered` reproduces
\(s(x)=x\) to floating-point accuracy — a useful sanity check to run against your own callback
before trusting its scores.

### Estimated scores are surrogate information

Classifier-derived providers always record `kind="estimated_ratio"`, so `information_kind` reads
`"supplied_score_surrogate"`. The between-cell algebra is exact for the vectors you supplied, but
the vectors are estimates: what the report measures is \(\operatorname{Var}(E[\hat s\mid q(\hat s)])\),
not \(\operatorname{Var}(E[s\mid q(\hat s)])\). To measure the second, label events with the
estimated scores and then evaluate an exact score under those labels. Estimator error is not
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
- Model density ratios: finite, nonnegative `[N, K]`, defined up to a common event-wise factor.
- Central classifier probabilities: strictly positive `[N, P, 2]`, normalized on the last axis.
- Integration bounds: finite `[D, 2]` with strictly ordered endpoints, plus an explicit density.

Numerically singular directions are projected out. Scores are never centered.
