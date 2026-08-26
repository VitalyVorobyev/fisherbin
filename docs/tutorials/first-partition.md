# First fixed D partition

For a Gaussian location score \(s=x\), optimize labels of one fixed table:

```python
import numpy as np
import scorequant as sq

rng = np.random.default_rng(12)
scores = rng.normal(size=(2_000, 1))
partition = sq.optimize_partition(
    scores,
    n_bins=4,
    criterion=sq.DOptimality(),
    config=sq.DExchangeConfig(seed=12),
)
```

`partition.labels` has one label per supplied row. Inspect the exact exchange state:

```python
partition.exchange_stable
partition.best_remaining_gain
partition.train_report.geometric_mean_retention
```

For future scores, compile only after stability:

```python
future_scores = rng.normal(size=(200, 1))
quantizer = partition.compile_quantizer()
future_bins = quantizer.predict_scores(future_scores)
```

Compilation verifies that the final D Mahalanobis rule reproduces all positive-weight training
labels. This explicit transition is part of the statistical contract.
