# ScoreQuant

**Information-optimal hard compression for parametric inference.**

ScoreQuant replaces continuous event-level information with a small number of hard bins while
preserving as much Fisher information as possible for the parameters you actually want to measure.

[![CI](https://github.com/VitalyVorobyev/scorequant/actions/workflows/ci.yml/badge.svg)](https://github.com/VitalyVorobyev/scorequant/actions/workflows/ci.yml)
[![Documentation](https://github.com/VitalyVorobyev/scorequant/actions/workflows/docs.yml/badge.svg)](https://vitalyvorobyev.github.io/scorequant/)

Many statistical workflows eventually reduce rich observations to counts in a few named categories:
template and component fits, gated cell populations, binned likelihoods, trigger tiers, tables a
collaborator can reproduce by hand. That compression is usually chosen for convenience — equal
width, equal population, a threshold on one classifier output — even though the goal is parameter
estimation, and it silently discards sensitivity the experiment already paid for.

ScoreQuant chooses the categories from the inference problem instead. For a regular parametric
model $X\sim p(x\mid\theta)$, the local information an event carries at a reference point
$\theta_0$ is summarized by its **score**

$$
s(x) = \nabla_\theta \log p(x\mid\theta)\big|_{\theta_0}.
$$

ScoreQuant partitions score space into a few hard cells and optimizes the Fisher information
retained by their counts. Binning is still lossy; the point is to make the loss a quantity you
choose, measure and report rather than one you inherit from the axis ticks.

The model does **not** have to be a mixture. Mixture fractions, Gaussian means, calibration
parameters, cross sections, rates, shape and nuisance parameters all enter through the same score
representation.

## Three independent choices

Using ScoreQuant means answering three separate questions:

1. **What are you optimizing?** Labels for one finite sample, or a reusable rule for future events?
2. **How do you obtain the score?** Already available, computed from an explicit model, or
   estimated through density ratios?
3. **Which parameter information matters?** All of it through $D$-optimality, or only declared
   parameters of interest after profiling nuisance parameters through $D_s$?

The axes are independent.

```text
                         SCORE ACCESS
                ┌──────────────────────────────┐
                │ precomputed scores           │
TASK            │ exact model / score oracle   │       OBJECTIVE
                │ density ratios / classifier  │
                └──────────────────────────────┘

sample partition ─────────────────────────────── D
space quantizer  ─────────────────────────────── Ds
                                                   normalized trace / baselines
```

The optimizer ultimately sees weighted score vectors. Everything before that is model access;
everything after it is hard compression.

## 1. Choose the task

### A. Sample partitioning — *the best labels for the sample I have*

<!-- snippet: skip -->
```python
partition = sq.optimize_partition(scores, n_bins=8, criterion=sq.DOptimality())
```

This is **transductive**. The decision variables are the labels of the supplied rows, and the
result is a `PartitionResult`. A labeling of one finite table does not by itself say what should
happen to an event you have not seen, so `PartitionResult` deliberately has **no** generic predict
method.

There is one sanctioned crossing, and it is a theorem rather than a convenience: an
exchange-stable, nonsingular $D$-optimal partition already *is* a strict self-consistent Voronoi
partition in the $I_B^{-1}$-Mahalanobis metric. Such a result compiles into exactly that rule, and
refuses when it is unstable or degenerate.

<!-- snippet: skip -->
```python
rule = partition.compile_quantizer()
```

An arbitrary finite $D_s$-optimal partition should **not** be assumed to define a reusable Voronoi
quantizer.

### B. Space quantization — *the rule I apply to future events*

<!-- snippet: skip -->
```python
fit = sq.fit_quantizer(source, provider=provider, n_bins=8, criterion=sq.DOptimality())
bins = fit.quantizer.predict_scores(provider.score(future_events))
```

This is the **inductive** problem. Use it when the bins themselves are the deliverable: a histogram
definition, an event categorizer, a gating rule, or any analysis that must process observations
that were not present during optimization.

## 2. Choose how the score is obtained

The common interface is $x \mapsto s(x)$, and there are three routes to it.

| Score access | You already have | Interface |
| --- | --- | --- |
| **Precomputed scores** | score vectors $s_i$ | `ScoreSample` |
| **Exact model / score oracle** | a likelihood, component model, analytic or autodiff score | `ScoreFunction`, `LinearComponentScore` |
| **Density ratios** | analytic ratios, a direct ratio estimator, a calibrated classifier | `DensityRatioScore`, `CentralLogRatioScore` |

These are alternative upstream routes to the *same* downstream optimization problem. Absolute
densities are never required: the score is the gradient of a log density *ratio*, so a ratio oracle
is enough — but it must be a calibrated one. A ranking score or an arbitrary monotonic classifier
output is not, since the construction needs ratios rather than event ordering. See
[Three doors](https://vitalyvorobyev.github.io/scorequant/three-doors/) for the derivation.

### Sources and providers are different things

Fitting a reusable rule needs both a **reference measure** — which observations occur, with what
weight — and a **score map**.

| Source | Meaning |
| --- | --- |
| `ScoreSample(scores, weights)` | a finite weighted sample already in score space |
| `ObservationSample(X, weights)` | finite weighted observations |
| `IntegrationSource(bounds, density=...)` | deterministic quadrature over a bounded model |

Observation-space sources require a provider; a `ScoreSample` rejects one. **Model density ratios**
construct scores and enter through providers; **importance ratios** modify the reference measure
and enter as source weights. The two never share an argument.

`ScoreProvider` is a public protocol, so an external estimator is a provider without being wrapped:

<!-- snippet: skip -->
```python
class MyExternalScore:
    provenance = sq.ScoreProvenance(kind="estimated_ratio")

    def score(self, observations):
        return my_package.evaluate(observations)
```

## 3. Choose what information to preserve

For a hard rule with cells $b=1,\ldots,K$, let $W_b=P(q(S)=b)$ and $\mu_b=E[S\mid q(S)=b]$. The
information retained by the bin label is $I_B=\sum_b W_b\,\mu_b\mu_b^\top$.

- **`DOptimality()`** maximizes $\log\det I_B$, treating all score directions symmetrically. Use it
  when the complete parameter vector matters.
- **`ProfiledDOptimality(interest=...)`** maximizes the log determinant of the Schur complement
  after profiling nuisance parameters. This is **not** a generally better $D$; it answers a
  different question, and can deliberately sacrifice large amounts of nuisance information to
  answer it.
- **`NormalizedTrace()`** maximizes the Fisher-normalized retained trace. After whitening this is
  weighted $k$-means — an interpretable alternative and a baseline.

Parameters of interest can be named rather than indexed, which matters as soon as a model has more
than a handful of components:

<!-- snippet: skip -->
```python
sample = sq.ScoreSample(
    scores, weights, schema=sq.ScoreSchema(("T", "B", "monocyte", "mast", "HSPC"))
)
criterion = sq.ProfiledDOptimality(interest=("HSPC",))
```

Reports then say `interest: HSPC` and `nuisance: T, B, monocyte, mast`.

Whichever route supplies the scores, `optimize_partition` always takes score rows — so routes 2
and 3 reach it through an explicit `provider.score(X)`. The observation-to-score transformation
never hides inside a fitting call, and prediction never silently recomputes scores.

## Quick start

A Gaussian location model $x\sim\mathcal N(\mu, I_2)$ has $s(x)=x-\mu_0$, so at $\mu_0=0$ the
observations *are* the score vectors.

```python
import numpy as np
import scorequant as sq

rng = np.random.default_rng(7)
sample = sq.ScoreSample(
    rng.normal(size=(4_000, 2)),
    schema=sq.ScoreSchema(("mu_x", "mu_y")),
    provenance=sq.ScoreProvenance(kind="exact", reference_point=(0.0, 0.0)),
)
```

Partition this finite sample:

```python
partition = sq.optimize_partition(
    sample, n_bins=6, criterion=sq.DOptimality(), config=sq.DExchangeConfig(seed=7)
)
assert partition.exchange_stable
print(round(float(partition.train_report.geometric_mean_retention), 3))
```

Six bins retain a $D$-efficiency of about 0.75 — the geometric mean of the retained-information
eigenvalues. `partition.labels` belongs to these rows and nowhere else.

Fit a reusable rule instead, and deploy it:

```python
fit = sq.fit_quantizer(
    sample, n_bins=6, criterion=sq.DOptimality(), config=sq.DExchangeConfig(seed=7)
)
assert fit.information_kind == "exact_fisher"

rule = fit.quantizer
future_bins = rule.predict_scores(rng.normal(loc=0.25, size=(1_000, 2)))
```

`rule` is the deployable object: a transform, centers and a metric, with no training data attached.
It saves to a versioned, non-pickle artifact that loads and predicts in a process with no JAX
installed — fit on the accelerated backend, deploy anywhere.

<!-- snippet: skip -->
```python
rule.save("gaussian-6bins.sqz")
rule = sq.Quantizer.load("gaussian-6bins.sqz")
```

## Real-data showcase: FlowCyt

The [FlowCyt study](https://vitalyvorobyev.github.io/scorequant/usecases/flowcyt/) is the main
end-to-end real-data example. Flow cytometry produces individual cells described by twelve marker
measurements, while the scientific result is a vector of population fractions. The study uses all
30 patients: 20 reference, 10 frozen held-out, 600,000 sampled real cells drawn from 21,254,866
upstream events.

```text
12-dimensional cell measurements → calibrated classifier → density ratios
    → 5-dimensional mixture score → ScoreQuant → 8 frozen hard bins
    → integer bin counts → downstream mixture fit → cell-population fractions
```

At the eight-bin operating point the learned quantizer retains **98.5%** of the supplied-score
surrogate information and reaches a **0.00193** macro RMSE on the ten held-out patients; the
selected unbinned classifier-ratio baseline reaches 0.00173.

The study is useful beyond cytometry because it draws the boundaries explicitly: *the classifier is
not ScoreQuant, and the downstream mixture fitter is not ScoreQuant.* ScoreQuant is the
information-preserving hard-compression layer between them.

It also contains a real profiled-$D_s$ experiment, treating one cell fraction as the parameter of
interest. Interestingly, $D_s$ does **not** materially improve the final measurement there: plain
$D$ already lies close to a certified efficient-score ceiling. That is a useful negative result,
and it illustrates why $D_s$ is a different inferential objective rather than an automatically
superior one.

## Solvers

Unsupported task/criterion combinations are rejected before any optimization runs.

| Configuration | `optimize_partition` | `fit_quantizer` | Contract |
| --- | --- | --- | --- |
| `DExchangeConfig` | `DOptimality`, `ProfiledDOptimality` | `DOptimality` | Exact positive-gain relocations; monotone objective; terminates exchange-stable |
| `MahalanobisLloydConfig` | `DOptimality`, `ProfiledDOptimality` | `DOptimality` | A batch is adopted only if the exactly rebuilt objective improves; optional exact-exchange guard |
| `SoftVoronoiConfig` | — | `DOptimality`, `ProfiledDOptimality` | Differentiable soft optimization then hardening, with the hardening gap reported |
| `KMeansConfig` | — | `NormalizedTrace` | Weighted $k$-means in whitened score space |
| `ScalarDPConfig` | — | `DOptimality` | The exact global interval solution for rank-one score space |

The strong finite-sample bridge *exchange stable $\Rightarrow I_B^{-1}$-Voronoi* is specific to
full $D$-optimality and should not be assumed for profiled $D_s$.

## Certificates and diagnostics

Certificates are explicit operations; none runs silently during fitting.
`exchange_stability_report` scans any supplied labeling exactly and reports the best remaining
gain; `certify_partition` gives a branch-and-bound global certificate for full $D$, or an explicit
outstanding gap when its budget runs out; `efficient_score_bound` gives a certified ceiling on
profiled information for one parameter of interest; and `PartitionResult.geometry` measures the
Voronoi violation a result leaves unclaimed. Validation data is diagnostic only — it never touches
gradients, stopping, or checkpoint selection.

## Score provenance

There is a difference between optimizing supplied vectors exactly and claiming those vectors *are*
the exact statistical score. ScoreQuant records which it has: exact or autodiff provenance lets a
result report `information_kind == "exact_fisher"`, while classifier- or ratio-derived scores
produce `"supplied_score_surrogate"`. The optimization can be exact even when the vectors are
estimates, and the distinction matters when reading a retained-information number.

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

Python 3.12 or newer; JAX and Optax are the required numerical dependencies. ScoreQuant never sets
global JAX configuration at import, so 64-bit precision is your application's call
(`JAX_ENABLE_X64=1`). NumPy is a supported portable runtime, which is what lets a saved rule predict
where JAX is absent.

## Where ScoreQuant sits

```text
data → likelihood, component model, ratio estimator or classifier → SCORE
     → [ ScoreQuant: score → hard label ] → counts → template fit / profile likelihood / report
```

ScoreQuant does not train the classifier and does not perform the final parameter fit. It answers
one question well:

> Given a limited number of hard categories, how should they be chosen so the downstream inference
> loses as little relevant information as possible?

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
reusable one; profiled $D_s$ comes with certified efficient-score upper bounds; and small instances
can be closed with branch-and-bound global certificates. See
[Related work](https://vitalyvorobyev.github.io/scorequant/related-work/) for the full map,
including which pipeline stage each comparable package occupies.

## Documentation

[Why ScoreQuant](https://vitalyvorobyev.github.io/scorequant/motivation/) ·
[Method overview](https://vitalyvorobyev.github.io/scorequant/method/) ·
[Three doors](https://vitalyvorobyev.github.io/scorequant/three-doors/) ·
[Choosing your workflow](https://vitalyvorobyev.github.io/scorequant/user-workflow/) ·
[The book](https://vitalyvorobyev.github.io/scorequant/book/) ·
[Examples](https://vitalyvorobyev.github.io/scorequant/examples/) ·
[API guide](https://vitalyvorobyev.github.io/scorequant/api/) and
[reference](https://vitalyvorobyev.github.io/scorequant/reference/) ·
[FlowCyt study](https://vitalyvorobyev.github.io/scorequant/usecases/flowcyt/) ·
[Related work](https://vitalyvorobyev.github.io/scorequant/related-work/)

The book develops the statistical theory independently of this package's API; the FlowCyt study is
a reproducible end-to-end evaluation on a frozen patient split.

ScoreQuant is available under the [MIT license](LICENSE).
