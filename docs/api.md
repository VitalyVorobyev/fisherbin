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
    initial_labels=None,
) -> PartitionResult
```

This is fixed-sample assignment. It accepts `DOptimality` or `ProfiledDOptimality` with either
`DExchangeConfig` (exact positive-gain relocation) or `MahalanobisLloydConfig` (guarded
nearest-centroid batches). A batch is adopted only when the exactly rebuilt objective strictly
improves, because the frozen-metric batch step is not monotone on its own; with the default
`guard="exchange"` the labels are then finished by the exchange engine, so the terminal state is
exchange-stable.

`initial_labels` starts the solver from a supplied `[N]` labeling instead of its own seeding, which
is how `efficient_score_bound(...).labels` is used as an initializer. Zero-weight rows carry no
measure and their labels are ignored, identical score rows are merged before the solver runs and
must therefore already agree on their bin, and every requested cell must remain nonempty
afterwards. Supplied labels replace the seeding of the first exchange restart only, so `init` and
`n_init` still govern any further restart and one call can compare both starts; the guarded
Mahalanobis-Lloyd solver starts from them directly.

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

Supported pairs are D exchange, guarded Mahalanobis-Lloyd, soft D, normalized-trace k-means, and
exact scalar interval dynamic programming. The two finite D solvers take the same route: optimize
the labels, then compile the verified rule. `ScoreSample` forbids a provider; observation and
integration sources require one. Validation must use the same score dimension and remains
diagnostic.

`ScalarDPConfig` pairs with `DOptimality` only and requires the effective score space to be rank
one after `rank_rtol` projection; a higher rank is rejected by name. On that rank the D-optimal
partition has ordered interval cells, so the weighted interval dynamic program returns the global
optimum rather than a local one, and `max_rows` bounds its exact quadratic work.

## The efficient-score upper bound

```python
efficient_score_bound(
    scores,
    *,
    interest,
    weights=None,
    n_bins,
    config=None,
) -> EfficientScoreBound
```

Efficient-score domination bounds the profiled information of every `n_bins`-cell rule of the full
score space by the between-cell information of the full-data efficient score under that rule. For
one parameter of interest the maximizing rule has ordered interval cells and is found exactly, so
`upper_bound` is a certificate rather than an estimate, reported in the same log-determinant
convention as `PartitionResult.objective` under `ProfiledDOptimality`. `gap_to(partition_result)`
returns the remaining slack and is nonnegative up to floating-point error; `labels` doubles as the
`initial_labels` initializer for profiled exchange. More than one interest column raises
`NotImplementedError`, because a multivariate efficient score would need a multivariate solver and
the result would no longer be certified.

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
`OptimizationTrace.objective_label` names the units of the recorded objective, because solvers do
not share one convention: `"whitened_sse"` is a minimized weighted within-cell squared error in
Fisher-whitened coordinates, while `"logdet_retained"` and `"profiled_logdet"` are maximized log
determinants. Two traces are comparable only under the same label.
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
