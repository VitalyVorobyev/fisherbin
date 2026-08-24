# Algorithms

## Preparing the score geometry

FisherBin eigendecomposes the unbinned Fisher matrix, discards numerically
singular directions, and optionally whitens the retained subspace. Scores are
never centered. This produces informative coordinates (u_i) whose Euclidean
scales correspond to normalized Fisher directions.

## Weighted score k-means

**Definition.** Weighted k-means minimizes

\[
\sum_i w_i\lVert u_i-z_{b(i)}\rVert^2
\]

over centers (z_b) and nearest-center assignments.

**Intuition.** It directly minimizes the trace of exact Fisher loss in the
chosen coordinates. It is deterministic for a fixed seed and initialization
settings.

**Limitation.** It optimizes a trace objective, can reach a local minimum, and
does not explicitly balance weak versus strong retained directions.

## Soft Voronoi optimization

Soft Voronoi fitting replaces hard assignments during optimization by

\[
\rho_{ib}=\frac{\exp[-\lVert u_i-z_b\rVert^2/(2\sigma^2)]}
{\sum_c\exp[-\lVert u_i-z_c\rVert^2/(2\sigma^2)]}.
\]

The fractional bin statistics are differentiable, so the centers can maximize
a D-optimal objective based on \(\log\det F_\text{soft}\). Temperature is reduced
during fitting; the reported result is always the final hard nearest-center
partition.

**Intuition.** This is **inference-aware optimization**: the training objective
is a proxy for parameter precision rather than reconstruction or classification
accuracy. INFERNO is a related example of optimizing a differentiable inference
objective; FisherBin applies that principle to reusable hard score-space bins.

**Limitation.** A soft objective can improve while the hardened partition does
not. Inspect the hard trace and final report. At least as many bins as retained
Fisher directions are required for a nonsingular D-optimal result.

## Alternatives

- **Geometric binning** is simple and interpretable but follows measurement
  coordinates rather than parameter sensitivity.
- **One-dimensional discriminants** can be effective for one target versus one
  alternative, but collapse multiple parameter directions and may be
  non-monotonic with the full score.
- **Exact unbinned likelihood** is preferred when it is available and
  computationally acceptable; it does not incur binning loss.
- **Learned likelihood ratios or scores** avoid hard bins but introduce model
  and calibration error.
- **End-to-end inference-aware networks** can optimize an application-specific
  inference objective, at the cost of a larger and less reusable training
  boundary.

Next: [diagnostics](diagnostics.md).
