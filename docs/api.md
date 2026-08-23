# Python API

## Fitting

`fisherbin.fit(scores, *, weights=None, n_bins, config=None, validation_scores=None, validation_weights=None)` is the only fitting entry point. Omitting `config` selects `KMeansConfig()`. Passing `SoftVoronoiConfig()` selects differentiable D-optimal fitting. Validation inputs are optional diagnostics and cannot affect the returned centers.

Both configuration types are frozen dataclasses with `to_dict()` methods. Common fields control whitening, numerical rank tolerance, seed, convergence, restarts, and trace frequency. Soft fitting additionally controls Adam, annealing, and k-means initialization.

## Fitted result

`FitResult` exposes:

- `predict(scores)` — nearest-center hard labels for every input row;
- `evaluate(scores, weights=None)` — a fresh `InformationReport` using the fixed partition;
- `to_dict()` — JSON-compatible config, transform, centers, reports, and trace;
- `plot_summary(scores, weights=None)` — optional Matplotlib summary;
- `train_report` and optional `validation_report` from fitting;
- `transform`, `centers`, `config`, and `trace` for structured inspection.

`to_dict()` is intended for inspection and future service integration. It is not a versioned persistence format and has no matching `from_dict()` in v0.1.

## Information calculations

- `fisher_information(scores, weights=None)` computes unbinned Fisher information.
- `binned_fisher_information(scores, assignments, weights=None, n_bins=None)` computes hard-bin information.
- `fractional_fisher_information(scores, responsibilities, weights=None)` computes differentiable soft-bin information.
- `information_report(scores, assignments, weights=None, n_bins=None, rank_rtol=None)` returns normalized retention and occupancy diagnostics.

Assignments are zero-based integers. Fractional responsibility rows must be finite, nonnegative, and sum to one.

## Components and visualization

`scores_from_components(components, coefficients)` evaluates the relative-component score for a nonnegative linear intensity model with strictly positive total intensity.

The optional plotting functions `plot_optimization`, `plot_partition`, `plot_information`, and `plot_summary` consume structured result objects. Install the `viz` extra to use them. Higher-rank partitions are explicitly labeled as two-dimensional projections.
