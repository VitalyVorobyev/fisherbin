# ADR 0018: Use explicit JAX and NumPy execution behind one mathematical core

**Status:** Accepted

**Supersedes:** [ADR 0004](0004-jax-first.md)

## Context

ScoreQuant's first implementation was intentionally JAX-native. That kept the equations singular,
but it also allowed JAX array types, eager imports, random-number generation, scatter operations,
and compilation decisions to spread through domain objects, reports, orchestration, and solvers.
The browser learning lab provides the concrete second-runtime requirement that ADR 0004 required:
Pyodide supports NumPy but does not support JAX or Optax.

Copying each solver into a NumPy tree would be a worse boundary than the current coupling. The two
implementations would drift in the exact places where ScoreQuant's semantics matter: singular
directions, zero-weight rows, uncentred Fisher algebra, exchange gains, schedules, and hardening.

## Decision

Add one public immutable `ExecutionConfig` with explicit backend, precision, and device fields.
`execution=None` preserves the JAX default at public task boundaries and inherits an already active
execution scope inside an operation. Backend and device compatibility is resolved before numerical
work. ScoreQuant never changes JAX's global X64 setting.

The implementation follows this dependency direction:

```text
domain contracts and canonical NumPy results
        -> private execution protocol and adapters
        -> shared mathematical kernels
        -> solver orchestration
        -> public task API
```

JAX and NumPy adapters own conversion, scatter updates, deterministic random initialization,
device placement, compilation, and optimizer updates. Equations and solver flow are shared. The
soft objective has one analytic center gradient: JAX applies it through Optax Adam and NumPy through
a private Adam state with the same schedule, clipping, bias correction, and constants. Runtime
autodiff remains an oracle test, not a second production equation.

All arrays crossing the stable public boundary are `numpy.ndarray` values. Results record their
resolved execution and reuse it for prediction and evaluation unless the caller supplies an
override. There is one private capability table for task, configuration, criterion, and backend
support; there is no public backend registry or backend base class.

JAX and Optax remain normal CPython dependencies, guarded by Emscripten platform markers so a
Pyodide wheel can import and run the NumPy backend without them. PyTorch is not added. A future
runner can be admitted only after a concrete workload, capability mapping, conformance suite, and
benchmark gate justify it.

## Consequences

Backend equivalence means identical mathematics, invariants, and accepted hardened quality within
documented tolerances, not identical random trajectories. One backend-parameterized conformance
suite covers the declared task/configuration/criterion matrix, the certificate path, and the float32
leg; the golden-fixture and invariant suites continue to run on the default backend rather than
being parameterized twice. Import-boundary tests prohibit domain objects from depending
on execution libraries and prohibit solvers from branching on backend names.

This is an intentional pre-1.0 result-type change: arrays become NumPy and execution provenance is
serialized. JAX remains the default production backend, so callers that omit `execution` retain
the current task behavior while gaining a stable path to browser-scale NumPy execution.
