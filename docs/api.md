# API guide

## Top-level tasks

### `optimize_partition`

```python
optimize_partition(
    scores,
    *,
    weights=None,
    n_bins,
    criterion=None,
    config=None,
    provenance=None,
) -> PartitionResult
```

This is fixed-sample assignment. The current implementation accepts only `DOptimality` with
`DExchangeConfig`.

### `fit_quantizer`

```python
fit_quantizer(
    source,
    *,
    score=None,
    validation=None,
    n_bins,
    criterion=None,
    config=None,
) -> QuantizerResult
```

Supported pairs are D exchange, soft D, and normalized-trace k-means. `ScoreSample` forbids a
provider; observation and integration sources require one. Validation must use the same score
dimension and remains diagnostic.

## Result semantics

`PartitionResult` has labels, cell statistics, information matrices, `rank`, accepted moves,
`exchange_stable`, and `best_remaining_gain`, but no prediction method. Its
`compile_quantizer()` rejects an unstable or geometrically degenerate result.

`QuantizerResult.predict_scores(scores)` is the only prediction method. `evaluate_scores` assigns
new scores with the frozen rule and computes supplied-score information. The stored transform,
centers, and optional common metric define its score-space geometry; `rank`, train/validation
reports, hardening gap, solver contract, source kind, and score provenance remain inspectable.
Both result types expose `information_kind`: it is `exact_fisher` only for exact/autodiff
provenance and `supplied_score_surrogate` otherwise.

## Shape and measure contracts

- Scores: finite `[N, P]`, `N > 0`, `P > 0`.
- Observations: finite `[N, D]`.
- Weights: finite nonnegative `[N]` with at least one positive value.
- Classifier central probabilities: positive `[N, P, 2]`, normalized on the final axis.
- Multiclass posteriors: nonnegative `[N, K]`, row-normalized, with positive normalized priors.
- Integration bounds: finite `[D, 2]` with strictly ordered endpoints and an explicit density.

Numerical null directions are projected out. Scores are never centered. `to_dict()` returns
JSON-ready diagnostic state but is not a durable artifact format.
