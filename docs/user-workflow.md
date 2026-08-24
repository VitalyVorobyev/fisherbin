# User workflow: variables to component values to scores to bins

## 1. Start from an integration sample

The fitting sample is normally Monte Carlo, quadrature, or another reference sample used to approximate Fisher integrals. It is not necessarily observed experimental data.

```python
X_mc = np.column_stack([energy_mc, cos_theta_mc])  # shape [N, K]
mc_weights = ...  # optional shape [N]
```

Variable names are metadata rather than algorithm objects. Use plain strings when they help component validation and plots.

## 2. Define the linear intensity

For

$$
\lambda(x;\theta)=\sum_{\alpha=1}^{M}\theta_\alpha\phi_\alpha(x),
$$

define one vectorized callable per component:

```python
def signal(X: np.ndarray) -> np.ndarray:
    energy, cos_theta = X.T
    return signal_energy_shape(energy) * signal_angle_shape(cos_theta)


model = fb.LinearComponents(
    components={
        "signal": signal,
        "background_1": background_1,
        "background_2": background_2,
    },
    coefficients={
        "signal": 1.0,
        "background_1": 0.4,
        "background_2": 0.2,
    },
    variables=["energy", "cos_theta"],
)
```

The callable contract is exactly `[N, K] -> [N]`. Names determine a stable component order and coefficient mappings must have exactly the same keys.

The functions are intensity components, not necessarily normalized PDFs. Only the total reference intensity must be positive. Signed basis terms and signed coefficients are allowed when their sum remains a valid intensity.

## 3. Fit and inspect the partition

```python
result = fb.fit(
    X_mc,
    model=model,
    weights=mc_weights,
    n_bins=16,
    config=fb.SoftVoronoiConfig(seed=7),
)

print(result.report())
training_bins = result.labels
figure = result.plot_summary(X_mc, mc_weights)
```

Internally, this performs:

```python
problem = model.evaluate(X_mc, weights=mc_weights)
Phi = problem.components
density = Phi @ problem.coefficients
scores = Phi / density[:, None]
```

Only the final score matrix enters the optimizer.

## 4. Freeze the binning and apply it to data

```python
X_data = np.column_stack([energy_data, cos_theta_data])
data_bins = result.predict(X_data)
counts = np.bincount(data_bins, minlength=result.n_bins)
```

The result retains the component model and reference coefficients used during fitting. Asking for the model again during prediction would permit accidental component reordering, so `predict` accepts only `X_data`.

FisherBin stops at labels, counts, and information diagnostics. A likelihood or template-fitting package should consume the resulting bins downstream.

## 5. Use a lower-level entry point when appropriate

If component values already exist:

```python
result = fb.fit_components(
    Phi,
    coefficients=theta0,
    weights=mc_weights,
    n_bins=16,
)

new_bins = result.predict(Phi_new)
```

An evaluated problem is equally valid:

```python
problem = fb.LinearProblem(Phi, theta0, weights=mc_weights)
result = fb.fit_components(problem, n_bins=16)
```

If scores come from another analytic, automatic-differentiation, simulator, or learned workflow:

```python
result = fb.fit_scores(scores, weights=weights, n_bins=16)
new_bins = result.predict(scores_new)
```

The result type makes the prediction representation explicit: variable-level results accept `X`, component-level results accept `Phi`, and score-level results accept scores.
