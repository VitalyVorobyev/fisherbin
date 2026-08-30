# API guide

## Top-level tasks

### `optimize_partition`

<!-- snippet: skip -->
```python
optimize_partition(
    scores,                       # ScoreSample, or a raw score array
    *,
    weights=None,
    n_bins,
    criterion=None,
    config=None,
    provenance=None,
    initial_labels=None,
) -> PartitionResult
```

This is fixed-sample assignment. `scores` is either a `ScoreSample` — the same weighted score law
`fit_quantizer` takes, carrying its own weights, schema and provenance — or a raw score array with
`weights` and `provenance` supplied separately. Passing a sample together with either keyword is
rejected rather than silently resolved. An observation source is deliberately not accepted:
converting observations to scores stays an explicit `provider.score(X)`, so the fixed-sample
boundary remains visible. It accepts `DOptimality` or `ProfiledDOptimality` with either
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

<!-- snippet: skip -->
```python
fit_quantizer(
    source,
    *,
    provider=None,
    validation=None,
    n_bins,
    criterion=None,
    config=None,
    diagnostics="endpoints",
) -> QuantizerResult
```

Supported pairs are D exchange, guarded Mahalanobis-Lloyd, soft D, normalized-trace k-means, and
exact scalar interval dynamic programming. The two finite D solvers take the same route: optimize
the labels, then compile the verified rule. `ScoreSample` forbids a provider; observation and
integration sources require one. Validation must use the same score dimension — and, when both
sides declare a `ScoreSchema`, the same parameter names, since a reordering is invisible to a
column count — and remains diagnostic.

`diagnostics` controls how many recorded center snapshots are re-scored into
`trace.train_hard_retention` and `trace.validation_hard_retention`: `"final"` scores only the
terminal snapshot, `"endpoints"` (the default) scores the first and terminal snapshots, and
`"full"` scores every snapshot, matching the historical behavior. Unscored snapshots hold `nan` so
the returned history stays aligned with `trace.steps`; `centers`, `labels`, and both reports are
unaffected.

`ScalarDPConfig` pairs with `DOptimality` only and requires the effective score space to be rank
one after `rank_rtol` projection; a higher rank is rejected by name. On that rank the D-optimal
partition has ordered interval cells, so the weighted interval dynamic program returns the global
optimum rather than a local one, and `max_rows` bounds its exact quadratic work.

## Naming the score coordinates

A score matrix is a table of partial derivatives, one column per model parameter. The order is
meaningful but invisible, which is bearable in a two-parameter toy and dangerous in a real problem
with dozens of components. `ScoreSchema` declares the names:

<!-- snippet: skip -->
```python
schema = sq.ScoreSchema(("T cells", "B cells", "monocytes", "mast cells", "HSPCs"))

sample = sq.ScoreSample(scores, weights, schema=schema)

criterion = sq.ProfiledDOptimality(interest=("HSPCs",))
```

Names are resolved to score columns exactly once, at the public task boundary, so every solver,
report and certificate downstream still works in indices. `ProfiledDOptimality` accepts either
form and refuses a mixture of the two; declaring names against a sample that carries no schema
fails by name rather than guessing. Reports then print `interest: HSPCs` instead of `(4,)`.

A schema answers only *what each coordinate means*. Where the numbers came from and at which
reference point stays with `ScoreProvenance`, and the two are validated against each other rather
than each carrying a reference point that can drift.

Providers may supply the schema for the observation-space routes. `LinearComponentScore` derives
it from the component names the model already declares; `ScoreFunction`, `DensityRatioScore` and
`CentralLogRatioScore` accept `schema=` explicitly. It then reaches `PartitionResult.schema` and
`QuantizerResult.schema`.

## The score-provider contract

`ScoreProvider` is a runtime-checkable protocol, not a closed union. Any object with a
`provenance` and a `score` method is a provider:

<!-- snippet: skip -->
```python
class MyExternalScore:
    provenance = sq.ScoreProvenance(kind="estimated_ratio")

    def score(self, observations):
        return my_package.evaluate(observations)
```

`score` takes observations alone; the execution backend is ambient context established by the
public task, so an external implementation needs no knowledge of `ExecutionConfig`. A provider may
also expose `schema`, which is used when present and is not part of the required contract. The
four built-in providers are convenience implementations of this protocol.

## Sources, providers, and density ratios

Sources carry the measure (`ScoreSample`, `ObservationSample`, `IntegrationSource`); providers
carry the observation-to-score map (`ScoreFunction`, `LinearComponentScore`, `DensityRatioScore`,
`CentralLogRatioScore`). Importance ratios for a sample drawn from a proposal distribution belong
in the source weights, never in a provider.

`DensityRatioScore(ratio, parameterization, *, provenance=None)` pairs a model density-ratio
callback `[N, D] -> [N, K]` with a declared ratio-to-score map: `MixtureParameterization` for a
normalized mixture with one simplex-dependent component (`K - 1` score columns) or
`IntensityParameterization` for an extended linear-intensity model (all `K` columns).
`DensityRatioScore.from_classifier(predict, class_priors, parameterization, ...)` builds the ratio
callback from calibrated posteriors as `ratios_from_posteriors(predict(X), class_priors)` and
always records estimated provenance. `CentralLogRatioScore(predict, deltas, class_priors)` turns
paired minus/plus probabilities from classifiers trained at \(\theta_0\pm\delta\) into central
finite-difference scores.

The underlying array algebra is public: `ratios_from_posteriors(posteriors, class_priors)`,
`mixture_scores_from_ratios(ratios, reference_fractions, reference_component=-1)`, and
`scores_from_components(components, coefficients)` — the latter doubles as the intensity
ratio-to-score map because it is invariant under a common event-wise rescaling of a row.
`ratio_closure_report(ratios, weights)` checks that each ratio column integrates to one under the
declared measure and returns the per-component normalizers with their largest absolute residual.

`ScoreProvenance(kind, ...)` accepts `"unknown"`, `"exact"`, `"autodiff"`, `"estimated_ratio"`,
and `"custom_estimated"`; `exact_fisher` is derived from `kind` and cannot be set independently.
Ratio-derived scores carry a structured `ScoreProvenance.ratio` record (`RatioProvenance`) naming
the estimator, parameterization, reference fractions or coefficients, reference component,
training priors, calibration method, and finite-difference offsets.

## The efficient-score upper bound

<!-- snippet: skip -->
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

## Certificates

<!-- snippet: skip -->
```python
exchange_stability_report(
    scores,
    labels,
    *,
    weights=None,
    criterion=None,
    rank_rtol=None,
    gain_tolerance=1e-10,
) -> StabilityReport

certify_partition(
    scores,
    *,
    weights=None,
    n_bins,
    incumbent=None,
    criterion=None,
    rank_rtol=None,
    config=None,
) -> PartitionCertificate
```

`exchange_stability_report` runs exactly one complete exact scan of a supplied labeling and
nothing else, so labels from any source — a `guard="reject"` batch result, an external tool, a
hand edit — can be checked before they are trusted. It reports the exact objective, the best
remaining gain, and the improving `(row, destination)` move when one exists. The cell count comes
from the labels, and every declared cell must hold positive weight. Stability is always a verdict
at a tolerance: match `gain_tolerance` to the configuration that produced the labels, and read it
back from `StabilityReport.gain_tolerance`. Pass `gain_tolerance=0.0` to ask the strict question
instead.

`certify_partition` decides global optimality by branch and bound with the singleton-completion
upper bound: unassigned atoms are left as singleton cells, so refinement monotonicity of the log
determinant bounds every completion of a partial assignment. It starts from an incumbent — normally
`PartitionResult.labels`, otherwise one default exchange — and returns `status="optimal"` only when
the tree was exhausted; a spent node budget returns `status="budget_exhausted"` with the best
outstanding bound and the remaining `gap`. The search is exponential, so `CertificationConfig`
guards both the node count and the number of distinct score atoms, refusing an oversized instance
by name. Certification is `DOptimality` only: the refinement bound uses Loewner monotonicity of
`logdet`, which the profiled Schur objective does not inherit, and a profiled criterion is rejected
rather than approximated. Neither entry point ever runs implicitly during fitting.

## Result semantics

`PartitionResult` has labels, cell statistics, information matrices, `rank`, `accepted_moves`,
`scans`, `lloyd_iterations`, `accepted_lloyd_steps`, `exchange_stable`, and `best_remaining_gain`,
but no prediction method. One scan is one complete evaluation of every admissible relocation; with
the default `batch_moves` a single scan may relocate many rows, so `accepted_moves` normally
exceeds `scans`. The two Lloyd counters stay zero unless the guarded batch solver ran, and
`objective_history` records every accepted step of every phase in order. Its `compile_quantizer()`
rejects an unstable or geometrically degenerate result.

Geometry diagnostics are criterion-specific and never shared. A `DOptimality` result carries
`geometry`, a `GeometryReport` measuring the largest Mahalanobis-Voronoi violation of the terminal
metric, the guaranteed log-determinant gain such a violation would leave on the table, the largest
exact gain it actually leaves, and the cell-separation residual against the leverage bound; a
`ProfiledDOptimality` result carries `profiled_geometry` instead and leaves `geometry` as `None`.
The two describe different objects — a strict Voronoi rule that exchange stability forces, and an
efficient semimetric whose Voronoi rule a stable profiled partition may violate — so one shared
name would claim an implication that does not hold.

`GeometryReport` is a certificate at a tolerance, recorded as `gain_tolerance` and taken from the
configuration that produced the labels. `voronoi_consistent` means `maximum_violation_gain <=
gain_tolerance`: no Voronoi violation is worth more than the threshold the solver stopped at. It is
not a claim at tolerance zero, and on a large sample it must not be — the Theorem-3 guaranteed gain
falls like \(1/N^2\), so past roughly a million rows a few rows legitimately sit a hair past a cell
boundary inside the default \(10^{-10}\). `compile_quantizer()` reads that certificate rather than
demanding bit-exact label reproduction, so on such a partition `predict_scores` on the training
scores differs from `PartitionResult.labels` on those boundary rows and nowhere else; the
partition's labels stay authoritative for the fixed sample. Assignment itself is unchanged —
`argmin` decides, resolving a tie toward the lowest cell index.

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
- Model density ratios: finite nonnegative `[N, K]`, defined up to a common event-wise factor.
- Integration bounds: finite `[D, 2]` with strictly ordered endpoints and an explicit density.

Numerical null directions are projected out. Scores are never centered. `to_dict()` returns
JSON-ready diagnostic state but is not a durable artifact format.
