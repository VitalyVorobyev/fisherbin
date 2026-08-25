# System design

## Public task boundary

```text
scores ---------------------------------> optimize_partition() -> PartitionResult

ScoreSample ----------------------------+
ObservationSample + ScoreProvider ------+-> fit_quantizer() ----> QuantizerResult
IntegrationSource + ScoreProvider ------+
```

`PartitionResult` owns one fixed assignment: labels, cell weights/moments/means, full and retained
information, objective, rank diagnostics, accepted moves, exchange stability, remaining gain, and
provenance. It has no prediction method. `compile_quantizer()` is available only for a stable,
nonsingular D result whose rule reproduces every positive-weight training label.

`QuantizerResult` owns score-space centers and metric, `predict_scores`, train/validation reports,
hardening gap, trace, criterion/configuration, source kind, and provenance. There is deliberately
no ambiguous `predict` method.

## Stable first-wave combinations

`api.py` validates every `(config, criterion)` pair against one declarative table instead of
scattered isinstance chains; this is the complete current matrix.

| Task | Criterion | Configuration | Meaning |
| --- | --- | --- | --- |
| finite assignment | `DOptimality` | `DExchangeConfig` | exact positive-gain relocation |
| finite assignment | `ProfiledDOptimality` | `DExchangeConfig` | exact positive-gain relocation of the same-label profiled objective |
| finite assignment | `DOptimality` | `MahalanobisLloydConfig` | guarded batch Mahalanobis-Lloyd, exact-objective verified per proposal |
| finite assignment | `ProfiledDOptimality` | `MahalanobisLloydConfig` | guarded batch Mahalanobis-Lloyd of the profiled objective |
| reusable quantizer | `DOptimality` | `DExchangeConfig` | finite D assignment followed by explicit verified compilation |
| reusable quantizer | `DOptimality` | `MahalanobisLloydConfig` | guarded batch Lloyd assignment followed by explicit verified compilation |
| reusable quantizer | `DOptimality` | `SoftVoronoiConfig` | direct differentiable soft-D fit and hardening |
| reusable quantizer | `ProfiledDOptimality` | `SoftVoronoiConfig` | direct differentiable soft profiled-D fit and hardening |
| reusable quantizer | `DOptimality` | `ScalarDPConfig` | exact interval dynamic program on one retained score dimension |
| reusable quantizer | `NormalizedTrace` | `KMeansConfig` | Fisher-whitened weighted k-means baseline |

Unsupported criterion/configuration pairs fail before optimization: a config type absent from a
task's own signature raises `TypeError`, and a config/criterion pair the task does not implement
raises `ValueError`. There is no generic criterion plugin until multiple implementations demonstrate
a stable common contract. A profiled finite partition never compiles into a quantizer: no same-label
profiled rule is canonical away from the training rows. See
[ADR 0014](adr/0014-unified-exchange-and-certificates.md).

## Module ownership

- `information.py`: Fisher and retained-information algebra.
- `transforms.py`: informative subspace and whitening.
- `partition.py`: the unified exchange engine (D and profiled-\(D_s\) share one determinant-lemma
  scan through a private `_ExchangeObjective` protocol), the guarded batch Mahalanobis-Lloyd solver,
  the standalone stability certificate, and geometry diagnostics.
- `certify.py`: explicit bounded branch-and-bound global certification of D partitions. Its tree
  search is sequential NumPy in float64: per-node JAX dispatch would dominate a search whose nodes
  are one small log determinant each.
- `quantizers.py`: private weighted k-means and soft-D numerical kernels.
- `sources.py`: empirical and quadrature measures plus provenance.
- `providers.py`: framework-neutral observation-to-score adapters.
- `components.py`: linear models and pure posterior-to-score algebra.
- `reports.py`: diagnostic and certificate dataclasses (`InformationReport`,
  `ProfiledInformationReport`, `GeometryReport`, `ProfiledGeometryReport`, `StabilityReport`,
  `PartitionCertificate`, `EfficientScoreBound`). It depends on nothing that depends back on it,
  which is what lets `result.py` and `information.py` both build on it without importing each other.
- `criteria.py`, `config.py`, `result.py`, `api.py`: public contracts and orchestration. `api.py`
  validates every `(config, criterion, task)` combination against one declarative table instead of
  scattered isinstance chains.
- `_binstats.py`, `_chunking.py`, `_validation.py`: private numerical helpers shared across modules
  (weighted per-bin scatter-add statistics, the shared memory-bounded row-chunking budget used by
  exchange scans and assignment kernels, and input validation including dtype promotion).
- `examples/`, tests, and `research/`: datasets, tuning, counterexample search, and application logic.

JAX is the sole numerical kernel implementation and Optax supplies gradient optimization. Optional
visualization imports remain lazy. Research exploration is provenance and is excluded from the
product Ruff gate; every relied-upon identity or counterexample is copied into a deterministic
regression test.

## Source/provider rules

A score callback without a source has no measure and is rejected. A `ScoreSample` already contains
scores, so supplying a provider with it is also rejected. Observation and integration sources
require a provider. Equivalent source/provider constructions must materialize the same core
result.

`ScoreProvenance.exact_fisher` is derived from provenance kind; an estimated classifier cannot set
it independently. The classifier boundary stores only a ready callback, an explicit pure transform,
and metadata. Training frameworks remain outside dependencies and application splits remain
visible.

## Complexity and durability

The current exact exchange scan is \(O(NKP^2)\) per accepted move and avoids \(O(N^2)\) storage.
Geometric solvers materialize \([N,K]\) distances. Histories store aggregate metrics and center
snapshots, never per-event responsibilities. `to_dict()` is JSON-ready diagnostic state, not a
versioned persistence format.

## Pre-1.0 API audit

The current two-function boundary is sound: it prevents a fixed labeling from masquerading as a
rule and keeps observation-to-score conversion visible. The main weaknesses are capability gaps,
not a need for a generic facade:

| Need | Incorrect shortcut | Chosen contract | Status |
| --- | --- | --- | --- |
| same-label nuisance profiling | compile finite labels with an efficient metric | explicit `ProfiledDOptimality`; finite and inductive solvers remain separate | implemented |
| certified profiled ceiling | trust profiled exchange with no upper bound | `efficient_score_bound`/`EfficientScoreBound`, an exact scalar-DP ceiling on the profiled objective | implemented |
| global guarantee | imply exchange stability is global | explicit bounded branch-and-bound certificate | implemented as `certify_partition`/`PartitionCertificate` (D-only) |
| local stability of any labeling | trust a solver's own termination claim | one exact scan via `exchange_stability_report`/`StabilityReport` | implemented |
| Voronoi self-consistency of a D result | assume exchange stability implies Voronoi geometry | measured `GeometryReport`/`ProfiledGeometryReport` | implemented |
| Monte Carlo population law | pass an unrecorded callback as a score table | deterministic score/observation sampler source | not yet implemented |
| analytic cell integrals | pretend an oracle contains rows | moment-oracle evaluation of an existing rule | not yet implemented |
| large transported data | call minibatch fitting exact | streaming aggregation for a frozen rule | not yet implemented |
| reuse across processes | treat `to_dict()` as a schema | versioned non-pickle quantizer artifact | not yet implemented |

The revision deliberately does not add `predict`, a generic criterion plugin, classifier training,
or a universal streaming optimizer. See [ADR 0013](adr/0013-complete-pre-1-api-boundaries.md) and
[ADR 0014](adr/0014-unified-exchange-and-certificates.md) for the complete decisions.
