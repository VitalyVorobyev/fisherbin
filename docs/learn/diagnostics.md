# Diagnostics

A single accuracy number cannot validate an information-preserving partition.
Use three separate layers of evidence.

## 1. Compression variance

Compare (F_\text{binned}) with (F_\text{unbinned}) for the same supplied
scores and weights. Inspect retained eigenvalues, D-efficiency, numerical rank,
and weighted bin occupancy. The matrix inequality
(F_\text{binned}\preceq F_\text{unbinned}) must hold within tolerance.

Validation samples are diagnostic only. They do not affect gradients, stopping,
checkpoint selection, or final centers.

## 2. Model and estimator bias

When scores come from an approximation, test them independently. For classifier
ratios, use group-aware out-of-fold predictions, record priors and calibration,
and verify ratio-normalization residuals on reference data. Do not call such a
baseline an oracle or information upper bound.

Bias is the mean estimation error,

\[
\operatorname{bias}(\hat\theta)=\mathbb E[\hat\theta]-\theta.
\]

High Fisher retention cannot make this bias vanish.

## 3. Downstream error

Root mean squared error combines variance and bias:

\[
\operatorname{RMSE}^2=\operatorname{variance}+\operatorname{bias}^2
\]

for a scalar estimator under the usual decomposition. Evaluate it on untouched
data using the complete downstream likelihood. Report per-parameter errors,
convergence, empty bins, and boundary cases—not only a macro average.

## High-dimensional partitions

A rank-five partition has no faithful two-dimensional picture. `plot_partition`
therefore stops at effective rank two. For higher rank, `plot_summary` shows the
retained-eigenvalue spectrum and information matrix, while
`plot_optimization` shows median and maximum center-displacement norms across
all coordinates.

Projection-free application summaries can be more informative. In a mixture,
for example, show each bin's reference composition

\[
P(k\mid B_j,\theta_0)=
\frac{P(B_j\mid k)\theta_{0k}}
{\sum_lP(B_j\mid l)\theta_{0l}}.
\]

This explains the statistical role of each gate without pretending to display
all geometric boundaries.

Next: [limitations and alternatives](limitations.md).
