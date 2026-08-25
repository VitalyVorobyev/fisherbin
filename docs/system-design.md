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

| Task | Criterion | Configuration | Meaning |
| --- | --- | --- | --- |
| finite assignment | `DOptimality` | `DExchangeConfig` | exact positive-gain relocation |
| reusable quantizer | `DOptimality` | `DExchangeConfig` | finite D assignment followed by explicit verified compilation |
| reusable quantizer | `DOptimality` | `SoftVoronoiConfig` | direct differentiable soft-D fit and hardening |
| reusable quantizer | `NormalizedTrace` | `KMeansConfig` | Fisher-whitened weighted k-means baseline |

Unsupported criterion/configuration pairs fail before optimization. There is no generic criterion
plugin until multiple implementations demonstrate a stable common contract.

## Module ownership

- `information.py`: Fisher and retained-information algebra.
- `transforms.py`: informative subspace and whitening.
- `partition.py`: exact D finite relocation, its standalone stability certificate, and geometry
  diagnostics.
- `certify.py`: explicit bounded branch-and-bound global certification of D partitions. Its tree
  search is sequential NumPy in float64: per-node JAX dispatch would dominate a search whose nodes
  are one small log determinant each.
- `quantizers.py`: private weighted k-means and soft-D numerical kernels.
- `sources.py`: empirical and quadrature measures plus provenance.
- `providers.py`: framework-neutral observation-to-score adapters.
- `components.py`: linear models and pure posterior-to-score algebra.
- `criteria.py`, `config.py`, `result.py`, `api.py`: public contracts and orchestration.
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

| Need | Incorrect shortcut | Chosen contract |
| --- | --- | --- |
| same-label nuisance profiling | compile finite labels with an efficient metric | explicit `ProfiledDOptimality`; finite and inductive solvers remain separate |
| Monte Carlo population law | pass an unrecorded callback as a score table | deterministic score/observation sampler source |
| analytic cell integrals | pretend an oracle contains rows | moment-oracle evaluation of an existing rule |
| global guarantee | imply exchange stability is global | explicit bounded branch-and-bound certificate |
| large transported data | call minibatch fitting exact | streaming aggregation for a frozen rule |
| reuse across processes | treat `to_dict()` as a schema | versioned non-pickle quantizer artifact |

The revision deliberately does not add `predict`, a generic criterion plugin, classifier training,
or a universal streaming optimizer. See
[ADR 0013](adr/0013-complete-pre-1-api-boundaries.md) for the complete decision.
