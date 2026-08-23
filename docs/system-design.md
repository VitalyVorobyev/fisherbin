# System Design

## Design goal

Keep the mathematics obvious in code while producing structured diagnostics that can drive both today's Python figures and a future local application.

```text
array-like scores + nonnegative weights
                 |
                 v
             fit(config)
                 |
                 v
             FitResult
       /-----------|------------\
  predict       evaluate       trace/report
                                  |
                           optional Matplotlib
```

## Boundaries

- `information.py` owns full, hard-binned, and fractionally binned Fisher calculations.
- `transforms.py` owns informative-rank selection, projection, and optional whitening.
- `quantizers.py` privately implements weighted k-means and soft Voronoi optimization.
- `config.py`, `result.py`, and `api.py` define the small public fitting contract.
- `visualization.py` imports Matplotlib lazily and only consumes structured results.
- Dataset-specific generators, baselines, notebooks, and figure layouts live in `examples/`.

JAX is the v0.1 numerical implementation and Optax supplies Adam. The public concepts remain arrays, configs, transforms, reports, traces, and fitted partitions; no backend registry or protocol is introduced yet.

## Public workflow

```python
result = fisherbin.fit(
    scores,
    weights=weights,
    n_bins=16,
    config=fisherbin.KMeansConfig(seed=0),
    validation_scores=validation_scores,
    validation_weights=validation_weights,
)

bins = result.predict(scores_new)
report = result.evaluate(scores_new, weights_new)
payload = result.to_dict()
```

The config type selects the method. Validation is diagnostic only. `to_dict()` is JSON-ready but is not a durable versioned artifact format.

## Numerical behavior

- Inputs must be finite; weights must be nonnegative with at least one positive value.
- Fisher matrices are symmetrized before eigendecomposition.
- Directions below a dtype-aware relative eigenvalue threshold are projected out and reported.
- Score coordinates are never centered.
- X64 is enabled by the application or CI, never as an import-time side effect.
- Fitting is full-batch and uses dense `[N, B]` distances/responsibilities, but histories contain only aggregate values and `[B, R]` center snapshots.

## Frontend boundary

Web, Tauri, and Python-service layers are deferred. A future frontend should serialize typed config values into the Python boundary and consume JSON-ready reports/traces rather than reproduce statistical calculations or parse plots.
