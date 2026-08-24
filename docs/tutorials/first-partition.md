# First analytic partition

This tutorial starts with a model whose score is known exactly. That makes the
unbinned/binned information ordering an oracle check rather than a comparison
between estimators.

## 1. Generate Gaussian location scores

For \(x\sim\mathcal N(\mu,1)\) at \(\mu_0=0\), the score is \(s(x)=x\).

```python
import jax.numpy as jnp
import numpy as np
import fisherbin as fb

rng = np.random.default_rng(7)
x_reference = rng.normal(size=20_000)
scores = jnp.asarray(x_reference[:, None])
```

## 2. Fit four hard bins

```python
result = fb.fit_scores(
    scores,
    n_bins=4,
    config=fb.KMeansConfig(seed=7, n_init=8),
)

print(result.report())
```

The result predicts in the same representation used for fitting:

```python
x_observed = rng.normal(loc=0.2, size=1_000)
observed_bins = result.predict(jnp.asarray(x_observed[:, None]))
counts = np.bincount(np.asarray(observed_bins), minlength=result.n_bins)
```

## 3. Check the information inequality

```python
full = np.asarray(result.train_report.unbinned_fisher)
binned = np.asarray(result.train_report.binned_fisher)
loss_eigenvalues = np.linalg.eigvalsh((full - binned + (full - binned).T) / 2)

assert loss_eigenvalues.min() >= -1e-10
```

Here both matrices use the same exact score model. The binned matrix cannot
exceed the unbinned one. Any small negative eigenvalue within tolerance comes
from floating-point arithmetic.

## 4. Inspect the geometry

```python
figure = fb.plot_partition(result, scores)
```

Rank one has a faithful geometric view: the horizontal axis is the informative
score coordinate and the vertical axis is the hard-bin label. Higher-dimensional
results should be judged with information and occupancy diagnostics rather than
an unlabeled two-coordinate projection.

Next: [linear components](linear-components.md).
