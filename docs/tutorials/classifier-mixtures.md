# Classifier posteriors for mixtures

Train, cross-fit, and calibrate a multiclass classifier in application code. Record its feature
transform, group split, class priors, calibration selection, seed, and model hash. ScoreQuant
starts from the ready probability callback.

```python
transform = sq.MixturePosteriorTransform(
    class_priors=training_priors,
    reference_fractions=theta0,
)
provider = sq.ClassifierScore(
    model.predict_proba,
    transform,
    description="cross-fitted calibrated component classifier",
)
quantizer = sq.fit_quantizer(
    sq.ObservationSample(X_reference, integration_weights),
    score=provider,
    n_bins=8,
    criterion=sq.DOptimality(),
    config=sq.SoftVoronoiConfig(seed=2026),
)
```

For new observations:

```python
test_scores = provider.score(X_test)
test_bins = quantizer.predict_scores(test_scores)
```

The reported information is information in the estimated score coordinates. To measure true
retained Fisher information, evaluate exact scores under labels produced from the estimated ones.
