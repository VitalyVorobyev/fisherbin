# Score model and calibration

ScoreQuant never sees a marker. It sees a five-column score matrix. This page is
about how twelve fluorescence channels become those five columns, and about the
audit that decided which of three candidate constructions to trust.

This is [Door 3](../../examples/door3-classifier.md): a trained classifier,
converted to score coordinates by an explicit adapter. Classifier training and
calibration are application code and stay outside the library.

## From class probabilities to mixture scores

Let \(p_k(x)\) be the marker density of population \(k\). A patient is modelled
as

\[
p(x\mid\theta)=\sum_{k=1}^{6}\theta_k p_k(x),
\qquad \theta_k\geq 0,
\qquad \sum_k\theta_k=1.
\]

Only five fractions are independent. Taking `other` as the reference component
gives five score directions at the reference composition \(\theta_0\):

\[
s_a(x)=
\frac{p_a(x)-p_6(x)}
     {\sum_k\theta_{0k}p_k(x)},
\qquad a=1,\ldots,5.
\]

Column \(a\) is therefore the derivative of the log density with respect to the
fraction of population \(a\), with `other` absorbing the sum constraint. That
identification is what makes the [profiled extension](profiled.md) exact rather
than analogical.

The component densities are not known analytically. We estimate their ratios
with a patient-cross-fitted `HistGradientBoostingClassifier`. If \(q_k(x)\) is a
class posterior learned with training prior \(\pi_k\), then

\[
\frac{p_k(x)}{p_{\text{train}}(x)}=\frac{q_k(x)}{\pi_k}.
\]

The common event density cancels in the score formula. This is the key bridge:
we can build the five statistical score coordinates without fitting a general
twelve-dimensional density model. The algebra itself is a public adapter —
`mixture_scores_from_posteriors`, with `MixturePosteriorTransform` and
`ClassifierScore` as the provider-side entry points.

## The nested calibration audit

The audit compares three strategies fixed before the test cohort is evaluated:
raw posteriors with declared uniform training priors, raw posteriors with priors
estimated from inner out-of-fold marginals, and temperature-scaled posteriors
with the same prior-consistency correction. It selects the smallest outer-fold
macro RMSE, preferring the simpler strategy when values differ by at most
\(10^{-6}\). Candidate errors, the selected strategy, priors, temperature, and
ratio-normalization residuals are stored in the JSON evidence.

| Candidate | Nested outer-fold macro RMSE | Maximum normalization residual | Mean score norm at \(\theta_0\) |
| --- | ---: | ---: | ---: |
| Raw posteriors, declared uniform priors | **0.00298** | 0.2169 | 0.1778 |
| Raw posteriors, out-of-fold priors | 0.00308 | \(<10^{-12}\) | 0.1616 |
| Temperature-scaled, out-of-fold priors | 0.01122 | \(<10^{-12}\) | 1.2255 |

After selection, one final classifier is trained on all reference patients and
used by the frozen held-out evaluation. The nested audit selected raw posteriors
with the declared uniform training priors, so the final temperature is 1.0.
Fisher information does not make an upstream score estimator correct.

```python
import json
from pathlib import Path

metrics = json.loads(Path("docs/usecases/assets/cell_population.json").read_text())
selection = metrics["calibration_selection"]

assert selection["selected_strategy"] == "raw_declared_prior"
assert selection["final_calibration"]["temperature"] == 1.0
assert round(selection["candidates"]["raw_declared_prior"]["target_macro_rmse"], 5) == 0.00298
assert round(selection["candidates"]["raw_oof_prior"]["target_macro_rmse"], 5) == 0.00308
assert round(selection["candidates"]["temperature_oof_prior"]["target_macro_rmse"], 5) == 0.01122
assert metrics["run"]["classifier_test_posterior_evaluations"] == 1
```

## What the normalization residual means

For exact density ratios, every component ratio integrates to one under the
declared training mixture. The selected raw-declared strategy misses that
closure by as much as 0.217, and its weighted mean-score norm at \(\theta_0\) is
0.178. This is model bias, not compression loss.

The OOF-prior strategies force the six component integrals to one on the same
reference sample, to numerical precision. That does not make their ratios
correct point by point: the raw OOF-prior candidate still has mean-score norm
0.162 and slightly worse nested RMSE, while temperature scaling increases the
norm to 1.225 and performs much worse. Marginal normalization is therefore a
useful closure check, but not a sufficient calibration criterion.

No ratio is silently renormalized after selection. The evidence records all three
residuals, reference-fold errors, and patient-level dispersion. The test cohort
is not used to choose among them.

```python
strategies = metrics["scientific_closure"]["ratio_model"]["strategies"]

assert strategies["raw_declared_prior"]["maximum_normalization_residual"] > 0.20
assert strategies["raw_oof_prior"]["maximum_normalization_residual"] < 1e-12
assert strategies["temperature_oof_prior"]["maximum_normalization_residual"] < 1e-12
assert round(strategies["temperature_oof_prior"]["mean_score_norm"], 3) == 1.225
```

## The surrogate-information caveat

Everything ScoreQuant reports about these columns is retention of the
*supplied* score law, and the library says so: the result's `information_kind`
is `supplied_score_surrogate`, and its `provenance.kind` is
`estimated_classifier`. That flag is not decoration. It means a retention of
0.985 is a statement about how much of the estimated score matrix's Fisher
information survives binning, and says nothing about how far that estimated
matrix is from the true one.

```python
eight = metrics["soft_voronoi:8"]

assert eight["information_kind"] == "supplied_score_surrogate"
assert eight["score_provenance"]["kind"] == "estimated_classifier"
assert eight["score_provenance"]["metadata"]["calibration_strategy"] == "raw_declared_prior"
```

This is why the study never argues from retention alone. Held-out population
RMSE, template rank, bin occupancy, and the fixed-total identifiability check
are separate quantities, and
[Quantization at scale](quantization.md) reports each of them. The theory behind
the caveat is [Chapter 13](../../book/ch13-estimated-scores.md); the synthetic
version of the same trap is the retention-versus-classifier-quality experiment in
[door3-classifier](../../examples/door3-classifier.md).

Calibration diagnostics for the selected model — balanced log loss, balanced
Brier score, balanced accuracy, expected calibration error, and the full
reliability table — are stored under `calibration` in the committed evidence and
drawn in the right-hand panels of the diagnostics figure on the
[data page](data.md#the-frozen-patient-split).
