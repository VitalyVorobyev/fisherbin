# ScoreQuant

ScoreQuant compresses events into a small number of hard bins while preserving the Fisher
information that downstream parameter estimation depends on.

Analyses that need counts in named categories — template fits, trigger tiers, gated populations,
binned likelihoods — usually pick those categories for readability and lose parameter sensitivity
without measuring how much. ScoreQuant works in *score space*, where each event is represented by
its local log-likelihood gradient
\(s(x)=\nabla_\theta\log p(x\mid\theta)\big|_{\theta_0}\), and optimizes a matrix criterion of the
information that survives the labels. The loss becomes a number you choose and report instead of
one you inherit from the axis ticks.

## Two tasks

```text
scores                                  -> optimize_partition() -> PartitionResult
ScoreSample | ObservationSample
           | IntegrationSource  (+ score provider) -> fit_quantizer() -> QuantizerResult
```

**Sample partitioning** answers "what are the best labels for the weighted sample in front of me?"
It is transductive, and `PartitionResult` deliberately has no predict method: a labeling of one
table does not determine what happens to an event you have not seen.

**Space quantization** answers "what reusable rule should I apply to future events?" It is
inductive, and prediction is the explicit `QuantizerResult.predict_scores(scores)`.

The one sanctioned crossing between them is a theorem rather than a convenience: an
exchange-stable, nonsingular D-optimal partition is already a strict self-consistent Voronoi
partition in the \(I_B^{-1}\)-Mahalanobis metric, so `PartitionResult.compile_quantizer()` returns
exactly that rule — and refuses when the partition is unstable or geometrically degenerate.

## Three doors

| | Sample partitioning | Space quantization |
| --- | --- | --- |
| **Door 1** — precomputed `(event, score)` rows | `optimize_partition(scores, weights=w, n_bins=k)` | `fit_quantizer(ScoreSample(scores, w), n_bins=k)` |
| **Door 2** — component densities or an analytic score model | `optimize_partition(provider.score(X), weights=w, n_bins=k)` | `fit_quantizer(source, score=provider, n_bins=k)` with an `ObservationSample` or `IntegrationSource` |
| **Door 3** — a trained classifier on measurement space | `optimize_partition(provider.score(X), weights=w, n_bins=k)` | `fit_quantizer(ObservationSample(X, w), score=provider, n_bins=k)` |

`optimize_partition` always takes score rows, so doors 2 and 3 reach it through an explicit
`provider.score(X)` call. Observation-to-score conversion never hides inside fitting or prediction.
[Three doors](three-doors.md) treats each regime in full.

## Quickstart

A Gaussian location model \(x\sim\mathcal N(\mu, I_2)\) has score \(s(x)=x-\mu_0\), so at
\(\mu_0=0\) the events are already the scores. First, the fixed-sample task:

```python
import numpy as np
import scorequant as sq

rng = np.random.default_rng(3)
scores = rng.normal(size=(2_000, 2))

partition = sq.optimize_partition(
    scores,
    n_bins=5,
    criterion=sq.DOptimality(),
    config=sq.DExchangeConfig(seed=3),
)
stable = bool(partition.exchange_stable)
efficiency = float(partition.train_report.geometric_mean_retention)
```

`partition.labels` belongs to those 2000 rows and nothing else. This run ended exchange-stable
(`stable` is `True`), and only in that case do the same labels also define a reusable rule:

```python
if partition.exchange_stable:
    quantizer = partition.compile_quantizer()
    future_bins = quantizer.predict_scores(rng.normal(loc=0.2, size=(500, 2)))
```

If a reusable rule is what you wanted from the start, fit one directly and let the criterion and
solver be your choice rather than a by-product:

```python
quantizer = sq.fit_quantizer(
    sq.ScoreSample(scores),
    n_bins=5,
    criterion=sq.NormalizedTrace(),
    config=sq.KMeansConfig(seed=3, n_init=4),
)
future_bins = quantizer.predict_scores(rng.normal(loc=0.2, size=(500, 2)))
```

The three fast starts in the [README](https://github.com/VitalyVorobyev/scorequant#readme) do the
same for each door, and [Choosing your workflow](user-workflow.md) walks through the decision.

## Site map

- [Why ScoreQuant](motivation.md) — the problem, why naive binning loses information, why score
  space, and why the two tasks stay apart.
- [Method overview](method.md) — the pipeline from score to certificate, with the criteria and
  solver families named.
- [Three doors](three-doors.md) — the input regimes, the source-versus-provider contract, and the
  validation rules.
- [Choosing your workflow](user-workflow.md) — which task, which door, which criterion and solver.
- [The book](book/index.md) — the statistical theory developed independently of this package's API.
- Examples — [Door 1, precomputed score events](examples/door1-score-events.md),
  [Door 2, mixture densities](examples/door2-mixture-densities.md),
  [Door 3, a trained classifier](examples/door3-classifier.md).
- Evidence — the [synthetic gallery](gallery/index.md) and the reproducible
  [FlowCyt study](usecases/cellpopulation.md).
- [API guide](api.md) and [reference](reference/index.md) — released contracts and errors.
- [Related work](related-work.md) — the four research traditions this sits in, an honest
  known-versus-new table, and a software comparison.
- [Glossary](glossary.md) and [bibliography](bibliography.md).
