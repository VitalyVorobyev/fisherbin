# Roadmap

## Current status: v0.1 release hardening

The v0.1 scientific core is feature-complete:

- JAX Fisher statistics, informative-rank projection, whitening, and nonnegative-weight validation;
- deterministic weighted score k-means and Optax soft Voronoi optimization;
- explicit variable, component, and score workflows with representation-specific prediction;
- immutable configs, reports, traces, held-out diagnostics, and JSON-ready conversion;
- optional Matplotlib views plus three reproducible scripts, notebooks, gallery figures, and baseline comparisons;
- X64 invariant tests, float32 smoke coverage, notebook execution, and a moderate-scale memory benchmark.

The current hardening milestone adds maintainable internals, Python 3.12 support, MIT licensing, generated API documentation, static typing gates, package-build checks, and automatic GitHub Pages deployment.

**Exit gate:** every documented `uv` command passes from a locked environment, pull requests build documentation strictly, the Pages workflow deploys from `main`, and the package is ready for an explicitly authorized v0.1 tag.

## v0.2: broaden empirical evidence

**Outcome:** defaults and acceptance thresholds are supported by more than the three designed proof examples.

- Add a broader deterministic fixture set spanning ranks, occupancies, weight distributions, nonlinear score geometry, and train/test shift.
- Calibrate existing defaults before exposing new optimizer controls.
- Validate at least one realistic external analysis end to end, including how its downstream likelihood consumes frozen labels.
- Compare final hard partitions, runtime, memory, and failure modes; do not make global-optimality claims.

**Exit gate:** documented default choices pass stable held-out thresholds across the expanded suite and one realistic application without dataset-specific library code.

## Persistence and larger workloads

Design a versioned fitted-partition artifact only after a concrete second process or frontend needs it. Callable `LinearComponents` models cannot be serialized generically, so persistence must define whether consumers provide scores, components, or a separately identified model.

Profile before adding chunked statistics, minibatches, or accelerator-specific paths. Adopt them only when measured workloads exceed the current moderate full-batch target.

## Later statistical and application work

- nuisance-profiled and multi-reference objectives evaluated on concrete applications;
- occupancy constraints, power diagrams, and alternative optimality criteria;
- a backend abstraction after a second backend has explicit requirements;
- a Python service and React/Tauri frontends consuming a stable artifact and configuration contract;
- signed-weight formulations with explicitly revised mathematical guarantees.

These items remain outside v0.1 and are not prerequisites for proving the current method.
