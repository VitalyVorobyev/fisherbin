# ADR 0013: complete the pre-1.0 API with capability-specific boundaries

**Status:** Accepted.

## Context

The first task-explicit API separates fixed assignments from reusable score rules, but the
remaining roadmap exercises five contracts that were not represented yet: profiled
\(D_s\), population sampling, direct cell-moment evaluation, finite global certification,
streaming evaluation, and durable quantizer artifacts. Treating all of these as new `Source`
variants would be misleading. In particular, a moment oracle does not provide event rows, a
certificate is an exponential post-fit operation, and a stream cannot in general reproduce a
batch optimizer.

The API is still pre-1.0. We prefer one deliberate revision now over compatibility aliases or
generic plugin machinery whose semantics would be weaker than the mathematics.

## Decision

Keep the two top-level optimization tasks:

```text
optimize_partition(...) -> PartitionResult
fit_quantizer(...)       -> QuantizerResult
```

Extend them only where the solver contract is established:

- `ProfiledDOptimality(interest=...)` means nuisance information is estimated from the same hard
  labels. Exact finite exchange is supported but never implicitly compiled. Direct soft fitting
  produces an explicit inductive score rule and reports its hardening gap.
- The full-information efficient-score upper problem remains an explicit transformation followed
  by ordinary `DOptimality`; it is not another spelling of same-label profiled \(D_s\).
- Deterministic `ScoreSampler` and `ObservationSampler` sources materialize a declared Monte Carlo
  design. They record seed, requested size, and provenance. They do not hide cross-fitting,
  calibration, or adaptive stopping.
- A `MomentOracle` evaluates cell masses, score first moments, and full second moments for an
  already specified quantizer. It supports population diagnostics but is not accepted by a solver
  that requires event rows or differentiable responsibilities.
- Global certification is an explicit bounded-size operation returning a
  `PartitionCertificate`. It uses a branch-and-bound upper bound obtained by leaving unassigned
  atoms as singleton cells. It never runs silently during ordinary fitting.
- Streaming support first means exact aggregation of diagnostics for a frozen quantizer over an
  iterable of weighted score batches. Batch optimization is not renamed “streaming”.
- `save_quantizer` and `load_quantizer` use a versioned, non-pickle artifact containing a JSON
  manifest and typed arrays. Diagnostic `to_dict()` output remains an in-memory interchange view,
  not a persistence promise.

Criterion-specific diagnostics are first-class. Ordinary information reports continue to show
the complete supplied-score retention spectrum; profiled reports additionally expose the Schur
information, nuisance rank, profiled objective, and efficient-score geometry diagnostics.

## Public-surface quality rules

1. Observation-to-score conversion stays visible; no generic `predict` is introduced.
2. Samplers define measures, providers define maps, and moment oracles define integrals. None is
   accepted in place of another merely because all use callbacks.
3. Public configuration describes user choices. Candidate chunks, cached inverses, factorization
   fallbacks, branch order, and JAX compilation details remain private.
4. A result exposes only operations justified by its criterion. A profiled finite partition has no
   compilation method that can succeed accidentally.
5. Persistence stores reusable score rules, never application classifiers or data-access
   callbacks.
6. New criteria still require their own mathematical and regression gate. This ADR does not create
   a generic criterion plugin and does not add E-optimality.

## Rejected alternatives

- A protocol-only `Source` accepted by every solver: it makes runtime capabilities implicit and
  gives moment-only objects fictitious row semantics.
- `predict(X)` on a quantizer: it hides the provider and encourages applying a rule to the wrong
  representation.
- Compiling finite \(D_s\) labels with the self-induced efficient metric: the exact rational
  counterexample disproves that implication.
- Pickling result objects: it is unsafe, backend-coupled, and cannot support explicit schema
  migration.
- Streaming exact exchange over transient batches: a relocation objective depends on global cell
  state and rescanning candidates; calling a one-pass heuristic exact would be false.

## Consequences

The API grows by a small number of reusable domain concepts while solver internals remain private.
Some result fields may change before 1.0 so D-only geometry is not presented as universal. Every
new capability needs two independent examples or one example plus an analytic laboratory, typed
documentation, invalid-combination tests, and a roadmap gate before it is exported.
