# Capability roadmap

This is an internal engineering document. Published user documentation contains
only capabilities that exist in the library.

## Stable score-to-partition core

**Outcome:** numerical invariants, deterministic fitting, and representation-
specific prediction remain reliable while the implementation stays compact.

- Preserve score origin, nonnegative weights, singular-direction projection,
  and validation-only diagnostics.
- Keep `fit_scores` as a short orchestration layer over private preparation,
  transform, quantizer, report, and trace stages.
- Expand deterministic regression fixtures only for distinct failure modes.

**Gate:** X64 and float32 tests, static checks, package build, and strict docs
build pass without unexpected fixed-seed result changes.

## Credible application evidence

**Outcome:** realistic studies distinguish compression information, upstream
model bias, and downstream estimation error.

- Keep the FlowCyt patient split and acceptance rules frozen.
- Select posterior calibration with nested reference-patient folds.
- Evaluate the untouched test cohort once and retain negative results without
  test-driven retuning.
- Record candidate metrics, priors, temperature, normalization closure,
  convergence, runtime, and source provenance.

**Gate:** machine-readable evidence reproduces every table and figure, and test
labels are confined to final metrics.

## Broader default evidence

**Outcome:** optimizer defaults are supported across deficient rank, rare
occupancy, skewed and zero weights, nonlinear score geometry, and controlled
distribution shift.

- Compare final hardened partitions, not only soft objectives.
- Record retention, stability, runtime, memory, and explicit failure modes.
- Change a default only after consistent improvement across several fixtures.

**Gate:** held-out thresholds pass in X64 and float32 invariants remain finite.

## Multidimensional partition visualization

**Outcome:** find honest, useful summaries for informative rank above two before
exposing another visualization API.

- Compare bin-score profile heatmaps.
- Compare pairwise projections with an explicit lost-dimension label.
- Evaluate nearest/second-nearest assignment margins.
- Prototype conditional two-dimensional slices with fixed remaining
  coordinates, including interaction only if static evidence is insufficient.
- Test every candidate on at least one synthetic case and the FlowCyt mixture.

**Gate:** a representation must reveal a decision-relevant property that the
retained spectrum, information matrix, occupancy, and application-specific bin
composition do not already show. Until then, no public API is added.

## Persistence and larger workloads

Design a fitted-partition artifact only when a concrete second process needs
one. Callable component models cannot be serialized generically, so the
consumer representation must be explicit. Profile real workloads before adding
chunked statistics, minibatches, or accelerator-specific paths.

## Deferred statistical extensions

Nuisance-profiled and multi-reference objectives, occupancy constraints, power
diagrams, alternative optimality criteria, signed weights, and additional
numerical backends require separate mathematical contracts and evidence.
