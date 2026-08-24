# Linear components

Use this workflow when the model is a sum of known intensity components.

## 1. Define the model

Suppose (x) contains energy and angle, and

\[
\lambda(x;\theta)=
\theta_s\phi_s(x)+\theta_1\phi_1(x)+\theta_2\phi_2(x).
\]

Each callable receives the complete `[N, K]` variable matrix and returns one
value per row:

```python
import fisherbin as fb

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

The components need not integrate to one. Their weighted sum at the reference
coefficients must be finite and strictly positive for every supplied event.

## 2. Fit from physical variables

```python
result = fb.fit(
    X_reference,
    model=model,
    weights=integration_weights,
    n_bins=16,
    config=fb.SoftVoronoiConfig(seed=7),
)
```

Internally the model evaluates `Phi`, constructs
`scores = Phi / (Phi @ theta0)[:, None]`, and delegates to `fit_scores`.

## 3. Freeze and apply

```python
data_bins = result.predict(X_observed)
counts = np.bincount(data_bins, minlength=result.n_bins)
```

The fitted result stores the model and component order. Prediction therefore
accepts physical variables again; it does not ask you to repeat coefficients or
component names.

If `Phi` is already available, use `fit_components(Phi,
coefficients=theta0, ...)`. The result then predicts from new component matrices,
not from physical variables.

Next: [classifier posteriors for mixtures](classifier-mixtures.md).
