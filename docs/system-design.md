# System Design

## Design goal

Keep the first version small enough that the mathematics is obvious in the code.

The library should have one primary workflow:

```text
scores + weights
      |
      v
quantizer.fit(...)
      |
      v
partition
      |
      +--> assign new scores
      +--> information report
```

Everything else is an adapter or optional extension.

## Core modules

```text
fisherbin/
  information.py     Fisher matrices and diagnostics
  quantizers.py      score k-means, later soft Voronoi
  components.py      linear-component -> score adapter
  result.py          fitted partition and report
```

Do not introduce backend abstractions, services, registries, or plugin systems until a concrete need appears.

## Public API

The low-level API should accept NumPy arrays directly:

```python
result = fisherbin.fit(
    scores,
    weights=None,
    n_bins=16,
    method="kmeans",
)

bins = result.predict(scores_new)
report = result.report()
```

A linear-component convenience API can compute scores and call the same core:

```python
scores = fisherbin.scores_from_components(components, coefficients)
result = fisherbin.fit(scores, n_bins=16)
```

The API should remain small until real use cases show what abstractions are actually needed.

## Implementation

### NumPy first

Implement the mathematical reference in NumPy. This keeps the project easy to inspect, test, and use.

### Differentiable optimizer

Add PyTorch only for soft-Voronoi optimization once the NumPy baseline works. PyTorch is an optional dependency, not a requirement for using fitted partitions or the k-means baseline.

### Performance

Do not add Rust/C++, JAX, streaming infrastructure, or custom GPU kernels initially. Profile real workloads first. The core calculations are simple enough that optimized NumPy/SciPy and optional PyTorch may be sufficient for a long time.

## Result object

A fitted result needs only:

- bin centers;
- optional whitening transform;
- method/configuration metadata;
- information diagnostics.

Serialization can start with a simple NumPy/JSON representation. Versioned schemas are only needed once compatibility becomes a real concern.

## Validation

Tests should focus on mathematical invariants:

- $F_B\preceq F_\infty$;
- event order does not matter;
- relabeling bins does not matter;
- identical weighted copies are equivalent to the original event;
- one bin and one-event-per-bin limits are correct;
- k-means reduces trace information loss relative to sensible baselines on synthetic problems.

Optimization metrics must also be evaluated on held-out samples in examples and benchmarks.

## Frontend

A frontend is useful, but it is not part of the initial architecture.

After the core library is stable, a small local application could provide:

- loading score/component datasets;
- 2D projections colored by bin;
- configuration of bin count and optimizer;
- optimization progress;
- comparison of Fisher information before and after binning.

It should call the Python library rather than reimplement the method. The technology choice can wait until the UI is actually started.
