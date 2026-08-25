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

This is fixed-sample assignment. It accepts `DOptimality` or `ProfiledDOptimality` with either
`DExchangeConfig` (exact positive-gain relocation) or `MahalanobisLloydConfig` (guarded
nearest-centroid batches). A batch is adopted only when the exactly rebuilt objective strictly
improves, because the frozen-metric batch step is not monotone on its own; with the default
`guard="exchange"` the labels are then finished by the exchange engine, so the terminal state is
exchange-stable.

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

Supported pairs are D exchange, guarded Mahalanobis-Lloyd, soft D, and normalized-trace k-means.
The two finite D solvers take the same route: optimize the labels, then compile the verified rule.
`ScoreSample` forbids a provider; observation and integration sources require one. Validation must
use the same score dimension and remains diagnostic.

## Result semantics

`PartitionResult` has labels, cell statistics, information matrices, `rank`, `accepted_moves`,
`scans`, `lloyd_iterations`, `accepted_lloyd_steps`, `exchange_stable`, and `best_remaining_gain`,
but no prediction method. One scan is one complete evaluation of every admissible relocation; with
the default `batch_moves` a single scan may relocate many rows, so `accepted_moves` normally
exceeds `scans`. The two Lloyd counters stay zero unless the guarded batch solver ran, and
`objective_history` records every accepted step of every phase in order. Its `compile_quantizer()`
rejects an unstable or geometrically degenerate result.

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
