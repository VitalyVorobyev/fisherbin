# Workflow guide

## Fixed score table: optimize its labels

Use this when the rows themselves are the final object.

```python
partition = sq.optimize_partition(
    scores,
    weights=weights,
    n_bins=8,
    criterion=sq.DOptimality(),
    config=sq.DExchangeConfig(seed=11),
)
labels = partition.labels
```

Inspect `exchange_stable`, `best_remaining_gain`, `accepted_moves`, cell statistics, information
matrices, and `train_report`. Do not invent future labels from an ordinary partition.

## Ready scores: learn a reusable rule

```python
quantizer = sq.fit_quantizer(
    sq.ScoreSample(scores, weights, provenance=provenance),
    validation=sq.ScoreSample(validation_scores, validation_weights),
    n_bins=8,
    criterion=sq.DOptimality(),
    config=sq.SoftVoronoiConfig(seed=11),
)
labels_new = quantizer.predict_scores(scores_new)
report_new = quantizer.evaluate_scores(scores_new, weights_new)
```

Validation is diagnostic only. Use `NormalizedTrace` with `KMeansConfig` for the weighted k-means
baseline or `DOptimality` with `DExchangeConfig` for theorem-backed finite-D compilation.

## Physical observations and an exact callback

```python
provider = sq.ScoreFunction(score_fn, provenance=sq.ScoreProvenance(kind="exact"))
quantizer = sq.fit_quantizer(
    sq.ObservationSample(X_train, weights),
    score=provider,
    n_bins=8,
)
labels_new = quantizer.predict_scores(provider.score(X_new))
```

No ambiguous observation-space prediction is hidden inside the result.

## Linear components

```python
model = sq.LinearComponents(
    components={"signal": signal, "background": background},
    coefficients={"signal": 1.0, "background": 0.4},
)
provider = sq.LinearComponentScore(model)
quantizer = sq.fit_quantizer(
    sq.ObservationSample(X_mc, mc_weights),
    score=provider,
    n_bins=8,
)
```

If component values are already evaluated, call `scores_from_components(Phi, coefficients)` and
then choose either fixed assignment or reusable quantizer fitting.

## Bounded model without a sampled table

```python
source = sq.IntegrationSource(
    [[-1.0, 1.0]],
    density=lambda x: 0.5 * np.ones(len(x)),
    quadrature=sq.GaussLegendreConfig(order=24),
)
quantizer = sq.fit_quantizer(source, score=provider, n_bins=4)
```

This path is for low-dimensional bounded domains. Use an empirical source for high-dimensional
observations.

## Ready classifier probabilities

Construct a pure transform, wrap the already trained callback in `ClassifierScore`, and retain all
training/calibration/fold details in application evidence. Evaluate true-score information
separately whenever an exact validation score is available.
