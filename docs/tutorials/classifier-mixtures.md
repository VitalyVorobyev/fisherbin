# Classifier posteriors for mixtures

This tutorial covers a reusable boundary: a classifier is trained elsewhere,
then FisherBin converts its ready posteriors into mixture scores.

## 1. Statistical model

For (K) component densities,

\[
p(x\mid\theta)=\sum_{k=1}^K\theta_k p_k(x),
\qquad \theta_k>0,
\qquad \sum_k\theta_k=1.
\]

Only (K-1) fractions are free. Choose one component as a reference; the
default is the last one.

## 2. Train and calibrate outside FisherBin

Let `posteriors[n, k]` be (q_k(x_n)), produced under training priors
`class_priors[k]` equal to (pi_k). These values must be probabilities: finite,
nonnegative, and row-normalized.

Use group-aware out-of-fold predictions when events share patients, runs, or
simulations. Fit calibration and prior corrections only on reference groups.
Classifier training and calibration are deliberately not library concerns.

## 3. Convert posteriors to scores

```python
import fisherbin as fb

scores = fb.mixture_scores_from_posteriors(
    posteriors,
    class_priors,
    reference_fractions,
    reference_component=-1,
)
```

The helper computes

\[
r_k=\frac{q_k}{\pi_k},\qquad
d=\sum_k r_k\theta_{0k},\qquad
s_a=\frac{r_a-r_\text{ref}}{d}.
\]

It does not clip zero posterior entries, renormalize rows, infer priors, or fit a
temperature. Invalid simplex inputs raise an error instead of being repaired
silently.

## 4. Fit and apply a partition

```python
partition = fb.fit_scores(
    scores[partition_rows],
    weights=weights[partition_rows],
    validation_scores=scores[validation_rows],
    validation_weights=weights[validation_rows],
    n_bins=8,
    config=fb.SoftVoronoiConfig(seed=7),
)

test_scores = fb.mixture_scores_from_posteriors(
    test_posteriors,
    class_priors,
    reference_fractions,
)
test_bins = partition.predict(test_scores)
```

The downstream mixture likelihood should estimate (P(B_j\mid k)) on
independent labelled reference rows and consume only test bin counts.

## 5. Interpret an unbinned comparison correctly

Ratios (q_k/\pi_k) are exact component density ratios only for a perfectly
specified, perfectly calibrated classifier. Therefore an unbinned likelihood
built from them is named an **unbinned classifier-ratio baseline**, not an
oracle. If it has worse RMSE than the binned pipeline, the likely mechanism is
ratio model bias plus recalibration by independent bin templates. The exact
Fisher inequality is not violated.

See the [FlowCyt study](../usecases/cellpopulation.md) for a nested patient-fold
calibration audit and a real six-component example.
