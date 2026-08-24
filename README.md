# FisherBin

**Information-preserving binning for statistical inference.**

[![CI](https://github.com/VitalyVorobyev/fisherbin/actions/workflows/ci.yml/badge.svg)](https://github.com/VitalyVorobyev/fisherbin/actions/workflows/ci.yml)
[![Documentation](https://github.com/VitalyVorobyev/fisherbin/actions/workflows/docs.yml/badge.svg)](https://vitalyvorobyev.github.io/fisherbin/)

FisherBin learns a finite hard partition of continuous or high-dimensional events while retaining information about parameters of a statistical model.

## Installation

FisherBin requires Python 3.12 or newer. From a source checkout:

```bash
uv sync --all-extras --all-groups --locked
```

## User workflow

Suppose an event is described by `energy` and `cos_theta`, and

```text
lambda(x; theta) = theta_signal * signal(x)
                 + theta_bkg1   * background_1(x)
                 + theta_bkg2   * background_2(x).
```

Define vectorized component functions and fit the partition on a Monte Carlo or integration sample:

```python
import numpy as np
import fisherbin as fb

X_mc = np.column_stack([energy_mc, cos_theta_mc])

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

result = fb.fit(
    X_mc,
    model=model,
    weights=mc_weights,
    n_bins=16,
)

print(result.report())
print(result.labels)  # labels for X_mc

data_bins = result.predict(X_data)
counts = np.bincount(data_bins, minlength=result.n_bins)
```

Each component receives the entire `X` matrix with shape `[N, K]` and returns shape `[N]`. Components need not be normalized PDFs and may be signed; FisherBin only requires finite values and a strictly positive reference intensity `components @ coefficients` at every supplied point. Integration weights must be finite and nonnegative.

The fitted result stores the model and its component ordering, so prediction does not ask the caller to provide the model again. FisherBin produces bins and diagnostics; the downstream statistical fit remains the user's responsibility.

## Three explicit representations

The public entry points mirror the mathematical pipeline:

```text
physical variables X
    -- LinearComponents --> component values Phi
    -- reference theta0 --> scores Phi / (Phi @ theta0)
    -- FisherBin --> hard bin labels
```

- `fit(X, model=...)` is the ergonomic physical-variable workflow.
- `fit_components(Phi, coefficients=...)` is the main statistical matrix API and also accepts `LinearProblem`.
- `fit_scores(scores, ...)` is the mathematical core for callers that already have scores.

All three return a result whose `predict(...)` method expects the same representation used during fitting.

## Evidence

The reproducible [synthetic gallery](docs/gallery/index.md) covers an analytic Gaussian score, non-monotonic spectral templates, and an importance-weighted spatial intensity model.

The realistic end-to-end case learns information-aware multidimensional gates
for [cell-population quantification in the FlowCyt benchmark](docs/usecases/cellpopulation.md),
then estimates six population fractions from frozen bin counts on held-out patients.

## Documents

- [Published documentation](https://vitalyvorobyev.github.io/fisherbin/)
- [Python API](docs/api.md)
- [FlowCyt cell-population use case](docs/usecases/cellpopulation.md)
- [Generated reference](docs/reference/index.md)

FisherBin is available under the [MIT license](LICENSE).
