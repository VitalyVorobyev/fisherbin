# ADR 0014: one exchange engine with criterion-specific objectives and explicit certificates

**Status:** Accepted; partially supersedes ADR 0011 and ADR 0013.

## Context

D exchange and profiled-\(D_s\) exchange shared no code, so the determinant-lemma algebra, the
batch-move machinery, and the guarded Mahalanobis-Lloyd solver each risked its own drift between
criteria. Separately, ADR 0013 named finite global certification and criterion-specific geometry
diagnostics as remaining pre-1.0 contracts without implementing them; a batch relabeling step also
turned out not to be monotone in general, so an unguarded batch acceptance rule would silently
regress the objective.

## Decision

Drive D and profiled-\(D_s\) exchange from one engine parameterized by a private
`_ExchangeObjective` protocol (`_DObjective`, `_ProfiledDObjective`) that supplies the
determinant-lemma state, chunked gains, move application, and assignment metric for its criterion;
the scan, restart, and batch machinery is written once against the protocol. Batch moves — in
exchange and in the guarded Mahalanobis-Lloyd solver — are proposed by a metric-nearest-centroid
rule but accepted only when the exactly rebuilt objective strictly improves, because that batch
proposal is not monotone by construction: a committed fixture loses log-determinant on one
unguarded step. A rejected batch halves and retries before falling back to the single best move, so
the accepted trajectory is always exact-objective-verified and cell-mass budgeted, never merely
plausible.

Keep two top-level tasks, sample partitioning (`optimize_partition`) and space quantization
(`fit_quantizer`), and validate every `(config, criterion)` pair against one declarative table in
`api.py` instead of per-call isinstance chains:

| Config | `optimize_partition` | `fit_quantizer` |
| --- | --- | --- |
| `DExchangeConfig` | `DOptimality`, `ProfiledDOptimality` | `DOptimality` |
| `MahalanobisLloydConfig` | `DOptimality`, `ProfiledDOptimality` | `DOptimality` |
| `KMeansConfig` | — | `NormalizedTrace` |
| `SoftVoronoiConfig` | — | `DOptimality`, `ProfiledDOptimality` |
| `ScalarDPConfig` | — | `DOptimality` |

A finite profiled-\(D_s\) partition never compiles into a quantizer: `DExchangeConfig` and
`MahalanobisLloydConfig` accept `ProfiledDOptimality` for partitioning but not for fitting, because
no same-label profiled rule is canonical away from the training rows.

Add an explicit certificate family instead of folding correctness claims into the solvers
themselves:

- `exchange_stability_report` runs exactly one exact scan over any supplied labeling — solver
  output, an external tool's result, or a hand edit — and reports whether it is stable.
- `GeometryReport` certifies D-partition Voronoi self-consistency at an exchange-stable state: the
  Theorem-3 violation gain bound and the Lemma-2 leverage separation bound, both measured rather
  than assumed. `ProfiledGeometryReport` reports the analogous finite efficient-semimetric gap for
  profiled partitions.
- `certify_partition` runs a bounded branch-and-bound global search with the singleton-completion
  upper bound, reporting `status="optimal"` only when the tree is exhausted and
  `status="budget_exhausted"` with a genuine outstanding upper bound otherwise. It supports
  `DOptimality` only: the bound relies on Loewner monotonicity of the log determinant under cell
  refinement, which the profiled Schur objective does not inherit, so a profiled criterion is
  refused rather than silently approximated.

No certificate runs implicitly during optimization. A caller who wants a stability, geometry, or
global-optimality claim requests it explicitly and pays its own cost.

## Consequences

The solver-pairing language of ADR 0011 — "D exchange may compile at verified stability" — is
refined by the explicit table above and by `GeometryReport` making that verification measurable
rather than assumed; ADR 0011's criterion-specific-semantics principle stands. The finite global
certification and criterion-specific diagnostics ADR 0013 described as remaining contracts are now
implemented as the certificate family above; ADR 0013's other pending contracts (population
sampling, moment oracles, streaming evaluation, durable artifacts) remain open. One engine means a
determinant-lemma bug fix or performance change applies to both criteria at once, and adding a
future exchange-based criterion means implementing `_ExchangeObjective` rather than a parallel
solver.
