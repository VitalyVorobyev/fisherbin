# Diagnostics

A single accuracy number cannot validate an information-preserving partition.
Use three separate layers of evidence.

## 1. Compression information

Compare \(F_\text{binned}\) with \(F_\text{unbinned}\) for the same supplied
scores and weights. Inspect retained eigenvalues, D-efficiency, numerical rank,
and weighted bin occupancy. The matrix inequality
\(F_\text{binned}\preceq F_\text{unbinned}\) must hold within tolerance.

Validation samples are diagnostic only. They do not affect gradients, stopping,
checkpoint selection, or final centers.

Match the diagnostic to the downstream likelihood. Poisson counts can use the
total event rate. Counts conditioned on a fixed total have only \(B-1\)
independent frequencies and use score covariance instead of an uncentered
second moment. Report both quantities when the supplied score model and the
downstream likelihood make different count assumptions.

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

## 3. Downstream error and identifiability

Root mean squared error combines variance and bias:

\[
\operatorname{RMSE}^2=\operatorname{variance}+\operatorname{bias}^2
\]

for a scalar estimator under the usual decomposition. Evaluate it on a frozen
held-out cohort using the complete downstream likelihood. Report per-parameter
errors, template rank, convergence, empty bins, and boundary cases—not only a
macro average.

For a fixed-total mixture, inspect the singular values of the template
contrasts \(A_{:a}-A_{:\mathrm{ref}}\). Full rank is required before a covariance
or an optimizer convergence flag can be interpreted as evidence that every
fraction is identified.

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
