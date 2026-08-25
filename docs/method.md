# Method

## Information algebra

For weighted rows \((s_i,w_i)\) and labels \(b(i)\),

$$
I_\infty=\sum_i w_i s_i s_i^\top,
\quad W_b=\sum_{i:b(i)=b}w_i,
\quad m_b=\sum_{i:b(i)=b}w_i s_i,
\quad I_B=\sum_b\frac{m_bm_b^\top}{W_b}.
$$

The loss identity

$$
I_\infty-I_B=\sum_b\sum_{i:b(i)=b}
w_i(s_i-\mu_b)(s_i-\mu_b)^\top\succeq0
$$

implies refinement monotonicity and the trace/k-means correspondence. Zero-weight rows do not
contribute. Uniform scaling and split-weight duplication leave normalized results invariant.
Identical positive-weight score rows are coalesced into one score-law atom before optimization and
their common label is expanded afterward; duplicating an atom cannot create a randomized extra
degree of freedom.

Numerically singular directions are projected out with a relative eigenthreshold. No ridge is
used because a ridge would invent information. Scores are projected and optionally whitened but
never translated.

## Implemented criteria and solvers

### Exact finite D exchange

For \(F_D(I)=\log\det I\), moving row \(i\) from cell \(a\) to \(b\) gives

$$
\Delta I=\alpha u_au_a^\top-\beta u_bu_b^\top,
\quad
\alpha=\frac{w_iW_a}{W_a-w_i},\quad
\beta=\frac{w_iW_b}{W_b+w_i}.
$$

The rank-two determinant lemma gives the exact gain. The solver accepts only gains above a fixed
tolerance, recomputes cell state after every accepted move, and terminates at a deterministic
one-point scan or an explicit move limit. For a positive-definite stable state, final labels are
reproduced by the common Mahalanobis metric \(I_B^{-1}\); only then may the result compile to a
quantizer. Zero-weight rows receive that final rule without influencing the fit.

### Normalized-trace k-means

After projection and Fisher whitening, weighted Lloyd steps minimize within-cell squared distance,
equivalently maximize normalized retained trace. This is a deterministic multi-restart baseline
and yields a reusable Euclidean Voronoi quantizer.

### Soft D quantizer fitting

Soft responsibilities define fractional cell moments and a differentiable D objective. Adam
optimizes centers while temperature decreases; the final result is the hardened nearest-center
rule. Reports distinguish soft objective, hard train/validation information, and hardening gap.
This is a nonconvex empirical solver, not a global-optimality certificate.

## Score acquisition

- `ScoreSample` carries precomputed score rows and their measure.
- `ObservationSample` needs a `ScoreFunction`, `LinearComponentScore`, or `ClassifierScore`.
- `IntegrationSource` materializes deterministic tensor Gauss-Legendre quadrature on a finite
  box. Density or intensity is mandatory. Its exponential point growth restricts it to low
  observation dimension.
- `LinearComponentScore` evaluates \(s_\alpha=\phi_\alpha/(\phi^\top\theta_0)\).
- `CentralLogRatioTransform` converts calibrated minus/plus posteriors, with training-prior
  correction, to central finite-difference scores.
- `MixturePosteriorTransform` converts calibrated multiclass posteriors to constrained mixture
  scores after class-prior correction.

Classifier callbacks must already be trained and calibrated. Validation sources remain diagnostic
and cannot affect gradients, stopping, initialization selection, or checkpoints.

## Criterion-specific limits

Profiled \(D_s\) remains a gated future solver and E-optimality is explicitly outside the
development plan. Both remain theory and regression-test subjects. Exact rational and exhaustive
fixtures prove that their globally optimal finite assignments can violate the corresponding
apparent nearest-cell geometries. Any future reconsideration would require separate finite and
inductive contracts before public exposure.
