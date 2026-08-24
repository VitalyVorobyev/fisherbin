# Python API

## Representation-specific fitting

### `fit`

```python
fit(
    X,
    *,
    model: LinearComponents,
    weights=None,
    n_bins: int,
    config=None,
    validation_X=None,
    validation_weights=None,
) -> ModelFitResult
```

This is the physical-variable API. `X` has shape `[N, K]`. The model is evaluated once for fitting and stored in the result for later `predict(X_new)` calls.

### `fit_components`

```python
fit_components(
    components_or_problem,
    *,
    coefficients=None,
    weights=None,
    component_names=None,
    n_bins: int,
    config=None,
    validation_components=None,
    validation_weights=None,
) -> ComponentFitResult
```

A matrix input has shape `[N, M]` and requires coefficients with shape `[M]`. Passing `LinearProblem` instead uses its coefficients, weights, and names; conflicting keyword values are rejected.

### `fit_scores`

```python
fit_scores(
    scores,
    *,
    weights=None,
    n_bins: int,
    config=None,
    validation_scores=None,
    validation_weights=None,
) -> FitResult
```

This is the score-space mathematical core. It contains all optimizer implementation; the other fitting functions evaluate their upstream representation and delegate here.

Validation inputs are diagnostic only for every entry point. They cannot affect gradients, stopping, checkpoint selection, or final centers.

The optimizer is selected by constructing `KMeansConfig` or `SoftVoronoiConfig`. The read-only `method` field is derived from the config class and included by `to_dict()`; it is not a constructor argument. All config values are validated immediately.

## Linear models

`LinearComponents(components, coefficients, variables=None)` accepts either:

- an insertion-ordered mapping of names to vectorized callables plus an exactly matching coefficient mapping; or
- a sequence of callables and an equally sized coefficient sequence.

Each callable receives a NumPy array `[N, K]` and returns one finite value per row. `variables` is optional string metadata whose length validates `K`.

`model.evaluate(X, weights=None)` returns an immutable `LinearProblem` containing component values, reference coefficients, optional integration weights, names, density, and scores. Callables are intentionally absent from its JSON representation.

`LinearProblem(components, coefficients, weights=None, component_names=None, variables=None)` is also directly constructible when component values have already been evaluated.

Components and coefficients may be signed and need not be normalized. Their reference intensity must be finite and strictly positive on all supplied rows.

## Result behavior

`FitResult`, `ComponentFitResult`, and `ModelFitResult` share:

- `labels` — final labels for all fitting rows, including predictable zero-weight rows;
- `predict(values)` — values must use the same representation as the fitting entry point;
- `evaluate(values, weights=None)` — held-out `InformationReport`;
- `report()` — final fitting-sample report;
- `n_bins`, `centers`, `transform`, `config`, `trace`, `train_report`, and optional `validation_report`;
- `to_dict()` — JSON-ready arrays and metadata;
- `plot_summary(values, weights=None)` — optional Matplotlib view.

`ModelFitResult` stores its `LinearComponents` object. Its JSON form records names, variables, and coefficients but omits unserializable callables. Durable save/load remains deferred.

## Information and visualization

- `fisher_information(scores, weights=None)` computes unbinned information.
- `binned_fisher_information(scores, assignments, weights=None, n_bins=None)` computes hard-bin information.
- `fractional_fisher_information(scores, responsibilities, weights=None)` computes soft-bin information.
- `information_report(...)` returns normalized retention and occupancy diagnostics.
- `scores_from_components(components, coefficients)` performs the explicit `Phi -> scores` transformation.
- `plot_optimization`, `plot_partition`, `plot_information`, and `plot_summary` consume score-level structured results.

## Migration from the initial prototype

The former `fit(scores, ...)` call is intentionally replaced by `fit_scores(scores, ...)`. This pre-release hard break prevents `fit` from ambiguously interpreting a matrix as physical variables or scores.

The initial configs accepted a redundant `method=` constructor argument even though their class already selected the method. That argument is removed; use the appropriate config class directly.

See the generated [API reference](reference/index.md) for current signatures and field documentation.
