# Migration to task-explicit APIs

The previous fitting entry points were removed without aliases. Migrate each call atomically:

| Previous intent | Replacement |
| --- | --- |
| Optimize labels of a fixed score table | `optimize_partition(scores, weights=..., ...)` |
| Learn a reusable rule from scores | `fit_quantizer(ScoreSample(scores, weights), ...)` |
| Fit from evaluated component values | `scores_from_components(Phi, coefficients)`, then choose one task above |
| Fit from physical variables and linear components | `fit_quantizer(ObservationSample(X, weights), score=LinearComponentScore(model), ...)` |
| Assign unseen values | compute scores explicitly, then `quantizer.predict_scores(scores_new)` |

Also choose a criterion/configuration pair explicitly:

<!-- TODO(phase2): illustrative kwarg fragments, not statements; slated for docs rewrite. -->
<!-- snippet: skip -->
```python
criterion=sq.NormalizedTrace(), config=sq.KMeansConfig(...)
criterion=sq.DOptimality(), config=sq.SoftVoronoiConfig(...)
criterion=sq.DOptimality(), config=sq.DExchangeConfig(...)
```

Code that previously predicted through a finite assignment must decide whether it actually needs a
reusable quantizer. Only a verified stable D partition can be compiled.
