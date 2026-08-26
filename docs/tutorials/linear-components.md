# Linear-component workflow

For \(\lambda(x;\theta)=\sum_k\theta_k\phi_k(x)\), define the components and reference
coefficients:

<!-- illustrative fragment; signal/background are defined in surrounding prose, not runnable standalone. -->
<!-- snippet: skip -->
```python
model = sq.LinearComponents(
    components={"signal": signal, "background": background},
    coefficients={"signal": 1.0, "background": 0.4},
    variables=["energy", "angle"],
)
provider = sq.LinearComponentScore(model)
```

Pair observations and their measure with the provider:

<!-- illustrative fragment; X_mc/mc_weights are defined in surrounding prose, not runnable standalone. -->
<!-- snippet: skip -->
```python
quantizer = sq.fit_quantizer(
    sq.ObservationSample(X_mc, mc_weights),
    score=provider,
    n_bins=8,
    criterion=sq.NormalizedTrace(),
    config=sq.KMeansConfig(seed=42),
)
```

Prediction keeps score construction visible:

<!-- illustrative fragment; X_data is defined in surrounding prose, not runnable standalone. -->
<!-- snippet: skip -->
```python
data_scores = provider.score(X_data)
data_bins = quantizer.predict_scores(data_scores)
```

Already evaluated components use `scores_from_components(Phi, coefficients)` before the chosen
partition or quantizer task.
