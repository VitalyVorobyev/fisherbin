# FisherBin

**Information-preserving binning for statistical inference.**

FisherBin partitions high-dimensional observations into a finite number of bins by clustering their parameter-score vectors. The v0.1 implementation uses JAX throughout, supports weighted k-means and differentiable soft Voronoi fitting, and reports exactly how much Fisher information the final hard partition retains.

## Quickstart

```python
import fisherbin

result = fisherbin.fit(
    scores_train,
    weights=weights_train,
    n_bins=8,
    config=fisherbin.SoftVoronoiConfig(seed=7),
    validation_scores=scores_valid,
    validation_weights=weights_valid,
)

bins = result.predict(scores_test)
report = result.evaluate(scores_test, weights_test)
print(report.retained_eigenvalues)

figure = result.plot_summary(scores_test, weights_test)  # fisherbin[viz]
```

Weights must be finite and nonnegative. Scores are never centered; singular Fisher directions are projected out and reported. Set `JAX_ENABLE_X64=1` before Python for the high-precision reference mode used by the examples and CI.

Install the package with `uv sync`; include visualization and notebook dependencies with `uv sync --all-extras --dev`.

## Evidence

The reproducible [synthetic gallery](docs/gallery/README.md) covers an analytic Gaussian score, non-monotonic spectral templates, and an importance-weighted spatial intensity model. Each example is available as both a script and a notebook and compares score-space methods with observation-space and random baselines.

## Documents

- [Motivation](docs/motivation.md)
- [Method](docs/method.md)
- [System design](docs/system-design.md)
- [Python API](docs/api.md)
- [Roadmap](docs/roadmap.md)
- [Architecture decisions](docs/adr/README.md)
