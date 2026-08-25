# ScoreQuant

**Compress events into a few hard labels while preserving information for parameter estimation.**

[![CI](https://github.com/VitalyVorobyev/scorequant/actions/workflows/ci.yml/badge.svg)](https://github.com/VitalyVorobyev/scorequant/actions/workflows/ci.yml)
[![Documentation](https://github.com/VitalyVorobyev/scorequant/actions/workflows/docs.yml/badge.svg)](https://vitalyvorobyev.github.io/scorequant/)

ScoreQuant works in statistical score space. It keeps two tasks deliberately different:

```text
fixed score table              -> optimize_partition() -> labels for those rows
empirical/integrated score law -> fit_quantizer()      -> reusable score -> bin rule
```

A finite assignment does not normally define unseen-event behavior. An exchange-stable,
nonsingular D-optimal assignment is the one exception currently implemented:
`PartitionResult.compile_quantizer()` constructs its theorem-backed Mahalanobis rule explicitly.

## Install

```bash
uv add "scorequant @ git+https://github.com/VitalyVorobyev/scorequant.git"
```

## Fit a reusable score quantizer

For a Gaussian location model, \(x\sim\mathcal N(\mu,1)\), the score at \(\mu_0=0\) is
\(s(x)=x\).

<!-- quickstart-test:start -->
```python
import numpy as np
import scorequant as sq

rng = np.random.default_rng(7)
reference_scores = rng.normal(size=(20_000, 1))

quantizer = sq.fit_quantizer(
    sq.ScoreSample(
        reference_scores,
        provenance=sq.ScoreProvenance(kind="exact", reference_point=(0.0,)),
    ),
    n_bins=4,
    criterion=sq.NormalizedTrace(),
    config=sq.KMeansConfig(seed=7, n_init=8),
)

observed_scores = rng.normal(loc=0.3, size=(2_000, 1))
bins = quantizer.predict_scores(observed_scores)
counts = np.bincount(np.asarray(bins), minlength=quantizer.n_bins)
```
<!-- quickstart-test:end -->

`predict_scores` is intentionally explicit: an observation-to-score model is never hidden inside
prediction.

## Optimize one fixed table

```python
partition = sq.optimize_partition(
    reference_scores,
    n_bins=4,
    criterion=sq.DOptimality(),
    config=sq.DExchangeConfig(seed=7),
)

assert not hasattr(partition, "predict")
if partition.exchange_stable:
    d_quantizer = partition.compile_quantizer()
```

`PartitionResult` records labels, cell moments, information matrices, exact accepted moves,
terminal gain, and provenance. `QuantizerResult` records the score-space rule, train and
validation reports, hardening gap, geometry, criterion, configuration, and provenance.

## Sources and score providers

The reference measure and the observation-to-score map are separate contracts:

| Input | Construction |
| --- | --- |
| Ready weighted scores | `ScoreSample(scores, weights)` |
| Weighted observations and callback | `ObservationSample(X, weights)` + `ScoreFunction` |
| Linear intensity components | `ObservationSample` + `LinearComponentScore` |
| Bounded low-dimensional model | `IntegrationSource(bounds, density=...)` + provider |
| Ready classifier output | `ClassifierScore(callback, transform)` |

Classifier training, calibration, and cross-fitting belong to the application. ScoreQuant
provides pure prior-corrected transformations for calibrated central likelihood ratios and
multiclass mixture posteriors. Information computed from estimated scores is marked as surrogate
information; it is exact Fisher information only when score provenance permits that
interpretation.

## Numerical contract

- Scores and weights are finite; weights are nonnegative and not all zero.
- Scores are never centered automatically: the origin has statistical meaning.
- Numerically singular Fisher directions are projected out, never repaired with a ridge.
- Validation data is diagnostic only and cannot affect gradients, stopping, or checkpoints.
- Optimizers are judged by the final hardened labels.

## Documentation and evidence

The [book](https://vitalyvorobyev.github.io/scorequant/book/) develops the statistical theory
independently of the package API. The
[workflow guide](https://vitalyvorobyev.github.io/scorequant/user-workflow/),
[API guide](https://vitalyvorobyev.github.io/scorequant/api/), and
[reference](https://vitalyvorobyev.github.io/scorequant/reference/) describe released interfaces.

The reproducible [FlowCyt study](https://vitalyvorobyev.github.io/scorequant/usecases/cellpopulation/)
uses a frozen patient split and separates classifier-score error, compression loss,
identifiability, patient shift, and downstream fraction-estimation error. Raw data is not
committed; manifests, hashes, aggregates, tables, and figures are.

ScoreQuant is available under the [MIT license](LICENSE).
