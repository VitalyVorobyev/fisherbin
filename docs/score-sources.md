# Score sources and providers

`Source + ScoreProvider` induces the score law used for fitting.

## Sources

`ScoreSample(scores, weights)` is already in score space and takes no provider.

`ObservationSample(X, weights)` carries empirical observations and requires one provider.

`IntegrationSource(bounds, density=..., quadrature=...)` supplies deterministic tensor
Gauss-Legendre integration. Bounds have shape `[D, 2]`; density or intensity is mandatory. An
explicit constant callback represents a uniform measure. Since point count is `order**D`,
`max_points` rejects accidental high-dimensional explosions.

## Providers

```python
provider = sq.ScoreFunction(
    score_fn,
    provenance=sq.ScoreProvenance(kind="exact", reference_point=(0.0,)),
)
```

`LinearComponentScore(model)` evaluates frozen component functions and applies
`scores_from_components`.

`ClassifierScore(callback, transform, description=...)` accepts a ready probability callback.
Training, calibration, feature preprocessing, and cross-fitting remain outside ScoreQuant.

For central finite differences:

```python
transform = sq.CentralLogRatioTransform(deltas, class_priors)
provider = sq.ClassifierScore(classifier_probabilities, transform)
```

Input is `[N, P, 2]` in `(minus, plus)` order. The transform subtracts training-prior log odds and
divides by `2 * delta`.

For multiclass mixtures:

```python
transform = sq.MixturePosteriorTransform(class_priors, reference_fractions)
provider = sq.ClassifierScore(predict_proba, transform)
```

The pure transform corrects class priors and returns constrained mixture-score coordinates.
Classifier provenance is always estimated, so its supplied-score information is a surrogate unless
an external exact-score validation establishes more.
