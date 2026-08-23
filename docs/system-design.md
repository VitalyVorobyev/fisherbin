# System Design

## Design goal

Keep the mathematics obvious in code while producing structured diagnostics that can drive both today's Python figures and a future local application.

```text
physical variables X -- LinearComponents --> component matrix Phi
                                                |
                                                v
                                   scores = Phi / (Phi @ theta0)
                                                |
                                                v
                                      score-space optimizer
                                                |
                                                v
                                      frozen hard partition
```

## Boundaries

- `information.py` owns full, hard-binned, and fractionally binned Fisher calculations.
- `transforms.py` owns informative-rank selection, projection, and optional whitening.
- `quantizers.py` privately implements weighted k-means and soft Voronoi optimization.
- `components.py` owns `LinearComponents`, evaluated `LinearProblem`, and score construction.
- `config.py`, `result.py`, and `api.py` define the representation-specific fitting contract.
- `visualization.py` imports Matplotlib lazily and only consumes structured results.
- Dataset-specific generators, baselines, notebooks, and figure layouts live in `examples/`.

JAX is the v0.1 numerical implementation and Optax supplies Adam. The public concepts remain arrays, configs, transforms, reports, traces, and fitted partitions; no backend registry or protocol is introduced yet.

## Public workflows

```python
result = fisherbin.fit(
    X,
    model=model,
    weights=weights,
    n_bins=16,
    config=fisherbin.KMeansConfig(seed=0),
    validation_X=validation_X,
    validation_weights=validation_weights,
)

bins = result.predict(X_new)
report = result.evaluate(X_new, weights_new)
payload = result.to_dict()
```

`fit_components` and `fit_scores` expose the two lower representation layers. Every result predicts in the same representation used to fit. All three paths delegate to one score optimizer; component functions and application variables never enter numerical optimization.

The config type selects the method. Validation is diagnostic only. `to_dict()` is JSON-ready but is not a durable versioned artifact format. High-level model metadata is serialized, but callable functions are not.

## Numerical behavior

- Inputs must be finite; weights must be nonnegative with at least one positive value.
- Fisher matrices are symmetrized before eigendecomposition.
- Directions below a dtype-aware relative eigenvalue threshold are projected out and reported.
- Score coordinates are never centered.
- X64 is enabled by the application or CI, never as an import-time side effect.
- Fitting is full-batch and uses dense `[N, B]` distances/responsibilities, but histories contain only aggregate values and `[B, R]` center snapshots.

## Frontend boundary

Web, Tauri, and Python-service layers are deferred. A future frontend should serialize typed config values and pre-evaluated component matrices into the Python boundary and consume JSON-ready reports/traces rather than reproduce statistical calculations or parse plots.
