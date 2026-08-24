# Roadmap

## v0.1 — JAX end-to-end proof

- JAX Fisher calculations, informative-subspace transforms, and nonnegative-weight validation.
- Deterministic weighted k-means and Optax soft Voronoi optimization.
- Immutable typed configs, result/report/trace objects, prediction, evaluation, and JSON-ready conversion.
- Explicit `fit(X, model=...)`, `fit_components(...)`, and `fit_scores(...)` workflows with representation-specific prediction.
- Optional Matplotlib optimization and final-result views.
- Three deterministic synthetic problems, scripts, notebooks, gallery figures, and held-out baseline comparisons.
- X64 invariant tests, float32 smoke coverage, linting, notebook execution, and a moderate-scale memory smoke benchmark.

**Done when:** the package reproduces the Fisher-loss identity, both optimizers produce trustworthy hard-partition diagnostics, and every gallery result regenerates from a clean environment.

## v0.2 candidates, only after v0.1 evidence

- tune optimizer defaults against a broader deterministic fixture set;
- add a versioned fitted-partition artifact if multiple consumers need persistence;
- profile chunked statistics or minibatched optimization on million-event workloads;
- evaluate nuisance-profiled and multi-reference objectives on concrete applications.

## Later

- backend abstraction beyond JAX;
- signed-weight formulations with explicitly revised guarantees;
- occupancy constraints, power diagrams, and alternative optimality criteria;
- Python service plus React/Tauri applications consuming the library data contract;
- compiled or accelerator-specific deployment work justified by profiles.
