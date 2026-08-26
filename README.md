# ScoreQuant

**Compress events into a handful of hard bins while keeping the Fisher information that downstream
parameter estimation depends on.**

[![CI](https://github.com/VitalyVorobyev/scorequant/actions/workflows/ci.yml/badge.svg)](https://github.com/VitalyVorobyev/scorequant/actions/workflows/ci.yml)
[![Documentation](https://github.com/VitalyVorobyev/scorequant/actions/workflows/docs.yml/badge.svg)](https://vitalyvorobyev.github.io/scorequant/)

## The problem

Many analyses cannot keep every event as a continuous vector. They need counts in a few named
categories: template fits, trigger tiers, gated cell populations, binned likelihoods, tables that a
collaborator can reproduce by hand. The binning is usually chosen for readability — equal width,
equal population, a threshold on one discriminant — and it silently throws away parameter
sensitivity that the experiment already paid for. ScoreQuant chooses the bins instead in *score
space*, where every event is represented by its local log-likelihood gradient
$s(x)=\nabla_\theta\log p(x\mid\theta)\big|_{\theta_0}$, and optimizes a matrix criterion of the
information that survives the labels. Binning is still lossy; the point is to make the loss a
quantity you choose, measure, and report rather than one you inherit from the axis ticks.

## Two tasks, three doors

Two tasks, kept deliberately separate:

- **Sample partitioning** — the best labels for the finite weighted sample you have.
  `optimize_partition(scores, ...) -> PartitionResult`. This is transductive, and
  `PartitionResult` has **no** predict method: a labeling of one table does not determine what
  happens to an event you have not seen.
- **Space quantization** — a reusable rule on score space.
  `fit_quantizer(source, score=...) -> QuantizerResult`, applied through
  `QuantizerResult.predict_scores(scores)`.

The one sanctioned crossing is a theorem, not a convenience: an exchange-stable, nonsingular
D-optimal partition is already a strict self-consistent Voronoi partition in the
$I_B^{-1}$-Mahalanobis metric, so `PartitionResult.compile_quantizer()` can hand back exactly that
rule — and refuses when the result is unstable or degenerate.

Three doors, one per input regime:

| | Sample partitioning (`optimize_partition`) | Space quantization (`fit_quantizer`) |
| --- | --- | --- |
| **Door 1** — you already have `(event, score)` rows | `optimize_partition(scores, weights=w, n_bins=k)` | `fit_quantizer(ScoreSample(scores, w), n_bins=k)` |
| **Door 2** — you have component densities or an analytic score model | `optimize_partition(provider.score(X), weights=w, n_bins=k)` | `fit_quantizer(ObservationSample(X, w) \| IntegrationSource(...), score=provider, n_bins=k)` |
| **Door 3** — you can estimate density ratios (calibrated classifier, direct ratio estimator) or write them analytically | `optimize_partition(provider.score(X), weights=w, n_bins=k)` | `fit_quantizer(ObservationSample(X, w), score=provider, n_bins=k)` |

`optimize_partition` always takes score rows, so doors 2 and 3 reach it through an explicit
`provider.score(X)`. The observation-to-score step never hides inside a fitting call or a
prediction call.

## Capabilities

Solvers, and the criteria each one implements for each task. An unsupported pair is rejected
before any optimization runs.

| Configuration (solver) | `optimize_partition` | `fit_quantizer` | What it guarantees |
| --- | --- | --- | --- |
| `DExchangeConfig` — exact positive-gain relocation | `DOptimality`, `ProfiledDOptimality` | `DOptimality` | Every accepted move has a closed-form positive exact gain, so the objective is monotone and the run ends exchange-stable |
| `MahalanobisLloydConfig` — guarded nearest-centroid batches | `DOptimality`, `ProfiledDOptimality` | `DOptimality` | A batch is adopted only when the exactly rebuilt objective improves; `guard="exchange"` finishes with exact relocations |
| `SoftVoronoiConfig` — annealed differentiable assignment | — | `DOptimality`, `ProfiledDOptimality` | A local optimum plus a measured hardening gap between the soft objective and the final hard labels |
| `KMeansConfig` — weighted Lloyd in whitened score space | — | `NormalizedTrace` | Deterministic multi-restart baseline; equivalent to normalized retained trace |
| `ScalarDPConfig` — exact interval dynamic program | — | `DOptimality` | The global optimum, not a local one, when the score space is rank one |

Certificates and bounds are explicit, separately invoked operations. None of them ever runs
silently during fitting.

| Entry point | What it returns | Criterion |
| --- | --- | --- |
| `exchange_stability_report(scores, labels, ...)` | One complete exact scan of any supplied labeling: stability verdict, exact objective, best remaining gain, and the improving move if one exists | `DOptimality`, `ProfiledDOptimality` |
| `certify_partition(scores, n_bins=..., incumbent=...)` | Branch-and-bound global optimality, or an explicit `status="budget_exhausted"` with the outstanding gap | `DOptimality` only |
| `efficient_score_bound(scores, interest=..., n_bins=...)` | A certified ceiling on the profiled information of *every* rule with that cell budget, plus the labels attaining it | `ProfiledDOptimality`, one interest parameter |
| `PartitionResult.compile_quantizer()` | The theorem-backed Mahalanobis rule of an exchange-stable partition | `DOptimality` only |
| `PartitionResult.geometry` / `.profiled_geometry` | Measured Voronoi violation and the objective gain it leaves unclaimed | Attached only to the matching criterion |

## Install

There is no PyPI release yet. Install from source:

```bash
uv add "scorequant @ git+https://github.com/VitalyVorobyev/scorequant.git"
```

Or to work on a checkout:

```bash
git clone https://github.com/VitalyVorobyev/scorequant.git
cd scorequant
uv sync --all-extras --all-groups
```

Python 3.12 or newer; JAX and Optax are the only required dependencies. ScoreQuant never sets
global JAX configuration at import time, so 64-bit precision is your application's call
(`JAX_ENABLE_X64=1`).

## Fast start — Door 1: you already have scores

A Gaussian location model $x\sim\mathcal N(\mu, I_2)$ has score $s(x)=x-\mu_0$, so at
$\mu_0=0$ the events *are* the scores.

```python
import numpy as np
import scorequant as sq

rng = np.random.default_rng(7)
scores = rng.normal(size=(4_000, 2))

quantizer = sq.fit_quantizer(
    sq.ScoreSample(
        scores,
        provenance=sq.ScoreProvenance(kind="exact", reference_point=(0.0, 0.0)),
    ),
    n_bins=6,
    criterion=sq.DOptimality(),
    config=sq.DExchangeConfig(seed=7),
)

future_scores = rng.normal(loc=0.25, size=(1_000, 2))
future_bins = quantizer.predict_scores(future_scores)
```

Six bins retain a D-efficiency of about 0.75 here — the geometric mean of the retained-information
eigenvalues, reported as `quantizer.train_report.geometric_mean_retention`. Because the provenance
says the scores are exact, `quantizer.information_kind` is `"exact_fisher"` rather than
`"supplied_score_surrogate"`.

## Fast start — Door 2: you have a component model

For a linear intensity $\lambda(x;\theta)=\sum_k\theta_k\phi_k(x)$ the event score is
$s_k = \phi_k/(\phi^\top\theta_0)$. Declare the components, let the library build the scores, and
let the model's own intensity supply the reference measure.

```python
import numpy as np
import scorequant as sq


def peak(X):
    return np.exp(-0.5 * ((X[:, 0] - 1.0) / 0.4) ** 2)


def flat(X):
    return np.ones(X.shape[0])


model = sq.LinearComponents(
    components={"peak": peak, "flat": flat},
    coefficients={"peak": 1.0, "flat": 0.5},
    variables=["mass"],
)
provider = sq.LinearComponentScore(model)
source = sq.IntegrationSource(
    [[-2.0, 3.0]],
    density=lambda X: peak(X) + 0.5 * flat(X),
    quadrature=sq.GaussLegendreConfig(order=96),
)

quantizer = sq.fit_quantizer(source, score=provider, n_bins=5, config=sq.DExchangeConfig(seed=11))
data_bins = quantizer.predict_scores(provider.score(np.linspace(-2.0, 3.0, 200)[:, None]))
```

`IntegrationSource` suits a bounded, low-dimensional model, since its tensor grid grows as
`order ** D`. With Monte Carlo events instead, swap in `ObservationSample(X, weights)` and keep the
same provider.

## Fast start — Door 3: you have density ratios

The score is the gradient of a log density *ratio*, so absolute densities are never required — a
ratio oracle is enough. A calibrated classifier is the most common one: posteriors over training
priors are component density ratios up to a factor that cancels. Training, calibration, and
cross-fitting stay in your code; ScoreQuant starts at the ready callback.

```python
import numpy as np
import scorequant as sq


def predict_proba(X):
    x = np.asarray(X)[:, 0]
    signal = np.exp(-0.5 * ((x - 1.0) / 0.5) ** 2) / 0.5
    background = np.exp(-0.5 * (x / 1.5) ** 2) / 1.5
    joint = np.stack([signal, background], axis=1)  # equal training priors
    return joint / joint.sum(axis=1, keepdims=True)


classifier_score = sq.DensityRatioScore.from_classifier(
    predict_proba,
    [0.5, 0.5],  # training priors
    sq.MixtureParameterization([0.3, 0.7]),  # reference mixture fractions
    description="calibrated two-component classifier",
)

rng = np.random.default_rng(5)
is_signal = rng.random(4_000) < 0.3
events = np.where(is_signal, rng.normal(1.0, 0.5, 4_000), rng.normal(0.0, 1.5, 4_000))[:, None]

closure = sq.ratio_closure_report(classifier_score.ratio(events), np.ones(events.shape[0]))

quantizer = sq.fit_quantizer(
    sq.ObservationSample(events),
    score=classifier_score,
    n_bins=4,
    config=sq.DExchangeConfig(seed=5),
)
assert quantizer.information_kind == "supplied_score_surrogate"
```

Any other ratio backend — a direct density-ratio estimator, a calibrated neural likelihood-ratio
model, an analytic formula — enters through the same `DensityRatioScore` with its own callback. An
estimated ratio is still an estimate: its between-cell matrix is exact for the vectors you supplied
and only a surrogate for the model's own Fisher information. Provenance records how the ratios were
obtained, `ratio_closure_report` bounds visible estimator bias before any fitting, and
`information_kind` refuses to claim exact Fisher semantics.

## What the results carry

`PartitionResult` records the labels, cell weights and score moments, the full and between-cell
information matrices, the informative rank, accepted moves and scans, the terminal
`best_remaining_gain`, `exchange_stable`, criterion-specific geometry diagnostics, and score
provenance. `QuantizerResult` records the frozen score-space rule (transform, centers, optional
common metric), train and validation reports, the hardening gap, the solver contract, an
optimization trace with its explicit `objective_label`, the source kind, and provenance. Validation
data is diagnostic only — it never touches gradients, stopping, or checkpoint selection.

## How it relates to prior work

Choosing a quantizer to preserve Fisher information is established territory, and ScoreQuant does
not claim to have invented it. Venkitasubramaniam, Tong and Swami introduced score-function
quantizers for distributed estimation ([CISS 2006](https://doi.org/10.1109/CISS.2006.286494));
Farias and Brossier developed the scalar high-resolution theory of Fisher-optimal quantization
([arXiv:1310.6945](https://arxiv.org/abs/1310.6945)); Barnes, Han and Özgür characterized quantized
Fisher information geometrically through conditional score means
([Allerton 2018](https://doi.org/10.1109/ALLERTON.2018.8635899)); Dülek proved convex-polytope
optimality for sufficient-statistic quantizers under a trace criterion
([IEEE TPAMI 2023](https://doi.org/10.1109/TPAMI.2022.3172282)). Determinant criteria for
partitions date to Friedman and Rubin (1967) and Scott and Symons (1971), and D-optimality itself
to Kiefer and Wolfowitz (1960). Inference-aware categorization is an active line of its own —
INFERNO, ThickBrick, and the recent GATO/BOBR binning optimizers.

What ScoreQuant contributes is narrower and concrete: the exact finite-sample geometry of
*full-matrix* D-optimal hard quantization. Relocating one weighted row is a rank-two update whose
log-determinant gain is available in closed form, which makes the exchange monotone and its
termination a stability certificate; exchange stability implies a strict self-consistent
$I_B^{-1}$-Mahalanobis-Voronoi rule, which is what licenses compiling a finite partition into a
reusable one; profiled $D_s$ comes with certified efficient-score upper bounds; and small
instances can be closed with branch-and-bound global certificates. All of it sits behind an API
that keeps the two tasks and the three doors visible instead of collapsing them into one `fit`.
See [Related work](https://vitalyvorobyev.github.io/scorequant/related-work/) for the full map,
including which pipeline stage each comparable package occupies.

## Documentation

- [Why ScoreQuant](https://vitalyvorobyev.github.io/scorequant/motivation/) — the problem, and why
  naive binning loses information.
- [Method overview](https://vitalyvorobyev.github.io/scorequant/method/) — score, informative
  subspace, criterion, solver, certificate.
- [Three doors](https://vitalyvorobyev.github.io/scorequant/three-doors/) — the input regimes in
  full, with the sources-versus-providers contract.
- [Choosing your workflow](https://vitalyvorobyev.github.io/scorequant/user-workflow/) — which
  task, which door, which criterion and solver.
- [The book](https://vitalyvorobyev.github.io/scorequant/book/) — the statistical theory developed
  independently of this package's API.
- [Examples](https://vitalyvorobyev.github.io/scorequant/examples/) — ten runnable pages, nine with
  a matching notebook: the three doors, a solver shootout against three baselines, theory
  demonstrations (profiled $D_s$, soft rules, two counterexamples, global certification), and a
  teaser into the FlowCyt study below.
- [API guide](https://vitalyvorobyev.github.io/scorequant/api/) and
  [reference](https://vitalyvorobyev.github.io/scorequant/reference/) — released contracts.
- [FlowCyt study](https://vitalyvorobyev.github.io/scorequant/usecases/flowcyt/) — a
  reproducible end-to-end evaluation on a frozen patient split that separates classifier-score
  error, compression loss, identifiability, patient shift, and downstream fraction-estimation
  error. Raw data is not committed; manifests, hashes, aggregates, tables, and figures are.

ScoreQuant is available under the [MIT license](LICENSE).
