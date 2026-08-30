# Method overview

Every ScoreQuant run follows the same five stages.

```text
score  ->  informative subspace  ->  criterion  ->  solver  ->  certificate
```

This page walks that pipeline once. The [book](book/index.md) develops the same material as theory,
independently of the package API; the [API guide](api.md) states the contracts and errors.

The pipeline sits inside a larger conceptual stack:

```text
observation/source layer      samples or an integration measure (weights carry the measure,
                              including any importance ratios)
statistical representation    exact densities | density ratios | exact or estimated scores
optimization layer            finite-sample partitioning and score-space quantizer fitting
deployment layer              x -> score(x) -> q(score)
```

Score vectors are the interface the optimizers consume; density ratios are often the more natural
interface the statistical model exposes, and converting one into the other is an explicit,
provenance-tracked step, never a hidden one.

## 1. Score

The input to every optimizer is a weighted table of score rows \((s_i, w_i)\) with
\(s_i\in\mathbb R^P\), one coordinate per parameter, evaluated at a reference point \(\theta_0\).
Weights are finite and nonnegative with at least one positive value; a zero-weight row remains
predictable but contributes no measure.

Absolute densities are never required to build the rows. The score is the gradient of a log
density ratio,

$$
s(x)=\nabla_\theta\log\frac{p(x\mid\theta)}{p(x\mid\theta_0)}\bigg|_{\theta=\theta_0},
$$

so any oracle for model density ratios determines it, and for component models the relative
densities \(\phi_k/\phi_{\rm ref}\) suffice. Where the rows come from — precomputed, an analytic
component model, or estimated density ratios — is the subject of
[Three doors](three-doors.md).

For labels \(b(i)\) the relevant quantities are the unbinned information, the cell masses and score
sums, and the between-cell information:

$$
I_\infty=\sum_i w_i s_i s_i^\top,
\quad W_b=\!\!\sum_{i:b(i)=b}\!\!w_i,
\quad m_b=\!\!\sum_{i:b(i)=b}\!\!w_i s_i,
\quad I_B=\sum_b \frac{m_b m_b^\top}{W_b}.
$$

The loss identity

$$
I_\infty-I_B=\sum_b\sum_{i:b(i)=b} w_i\,(s_i-\mu_b)(s_i-\mu_b)^\top\;\succeq\;0,
\qquad \mu_b=m_b/W_b,
$$

is what makes the whole problem well posed: hard labels can only lose information, refinement can
only help, and the loss is exactly the within-cell scatter of the score.

The algebra also fixes the invariances the library is required to preserve. Zero-weight rows do not
contribute. Scaling all weights uniformly and splitting one row into duplicates with the same total
weight leave normalized results unchanged. Identical positive-weight score rows are coalesced into
one weighted atom before optimization and their common label is expanded afterwards, so duplicating
an atom cannot smuggle in a randomized extra degree of freedom.

## 2. Informative subspace

Scores are eigendecomposed through \(I_\infty\) and projected onto the directions that carry
numerically meaningful information, using a relative eigenvalue threshold (`rank_rtol`, with a
dtype-aware default). Directions below the threshold are dropped, not repaired: adding a ridge
would invent information the sample does not contain. The retained rank appears on every result as
`rank`, and the full spectrum on `FisherTransform`.

Solvers optionally whiten the retained directions so that the unbinned information is the identity
there, which is what makes the trace criterion coincide with ordinary squared distance. Scores are
projected and rescaled but **never translated**: \(I_B\) is a second moment about the origin, and
\(s=0\) is the direction of no sensitivity, so centering would change the statistical object.

## 3. Criterion

Three criteria are implemented, and each has a fixed set of solvers it is allowed to pair with.

**`DOptimality`** maximizes \(\log\det I_B\) in the informative subspace. It balances every
information direction at once and corresponds to the volume of the local confidence ellipsoid.
Because the objective is a determinant, its geometry is metric-dependent: the effective distance
uses the currently retained information, which upweights directions where little information has
survived so far.

**`ProfiledDOptimality(interest=...)`** maximizes the log determinant of the Schur complement for a
declared block of interest columns, with nuisance information estimated from the *same* labels.
Writing \(\theta=(\psi,\lambda)\) for parameters of interest and nuisance parameters, and
partitioning the retained information

$$
I_B=
\begin{pmatrix}
I_{\psi\psi} & I_{\psi\lambda}\\
I_{\lambda\psi} & I_{\lambda\lambda}
\end{pmatrix},
$$

profiling the nuisance parameters leaves

$$
I_{\rm eff}
=
I_{\psi\psi}
-
I_{\psi\lambda}
I_{\lambda\lambda}^{-1}
I_{\lambda\psi},
$$

and the criterion maximizes \(\log\det I_{\rm eff}\). At least one nuisance column must remain.

This is not a better \(D\). It answers a different question — *if only these parameters will be
reported and the rest are allowed to float, how should the bins be spent?* — and can deliberately
sacrifice a great deal of nuisance information to do it. Use it when some parameters are genuinely
of interest and the rest are being profiled away.

**`NormalizedTrace`** maximizes the retained trace after whitening. By the loss identity this is
identical to minimizing weighted within-cell squared distance, so its solver is weighted k-means.
It is a deterministic, well-understood baseline rather than a competitor to the determinant
objectives.

## 4. Solver

Solvers are selected by passing a configuration object. The pairing of configuration and criterion
is a closed table, validated before any optimization runs; an unsupported pair raises rather than
silently substituting something else.

| Configuration | `optimize_partition` | `fit_quantizer` |
| --- | --- | --- |
| `DExchangeConfig` | `DOptimality`, `ProfiledDOptimality` | `DOptimality` |
| `MahalanobisLloydConfig` | `DOptimality`, `ProfiledDOptimality` | `DOptimality` |
| `SoftVoronoiConfig` | — | `DOptimality`, `ProfiledDOptimality` |
| `KMeansConfig` | — | `NormalizedTrace` |
| `ScalarDPConfig` | — | `DOptimality` |

### Exact finite exchange

Moving row \(i\) from cell \(a\) to cell \(b\) changes the between-cell information by a rank-two
update,

$$
\Delta I=\alpha\,u_au_a^\top-\beta\,u_bu_b^\top,
\qquad
\alpha=\frac{w_iW_a}{W_a-w_i},\qquad
\beta=\frac{w_iW_b}{W_b+w_i},
$$

so the matrix determinant lemma reduces the exact log-determinant gain to a \(2\times2\)
determinant. The solver evaluates every admissible relocation in a scan, accepts only gains above a
strict tolerance, and rebuilds cell state after every accepted move. The objective is therefore
monotone, termination is guaranteed, and the terminal state is exchange-stable by construction.
With `batch_moves` a single scan may relocate many rows, so `accepted_moves` normally exceeds
`scans`; a batch is truncated before it displaces too much of any cell's weight and adopted only
when the exactly rebuilt objective improves, halving and finally falling back to the single best
move otherwise.

### Guarded Mahalanobis-Lloyd

An iteration freezes the current criterion metric, proposes the complete nearest-centroid
relabeling in that metric, and accepts it only when the exactly rebuilt objective strictly improves.
The guard is part of the contract, not a safety net: the tangent of the concave log determinant is
an upper bound rather than a minorizer, so an unguarded batch step is not monotone and a committed
eight-row fixture loses 0.136521 nat in one such step. With the default `guard="exchange"` the
labels are finished by the exact exchange engine, so the reported state is exchange-stable and a
nonsingular D result stays compilable; `guard="reject"` stops at the last accepted batch and
reports whatever stability it actually reached.

### Soft Voronoi

Soft responsibilities turn cell moments into differentiable functions of the centers, giving a
differentiable surrogate for the D or profiled-D objective. Adam optimizes the centers while the
temperature anneals, and the returned rule is the hardened nearest-center assignment. The reports
keep the soft objective, the hard train and validation information, and the gap between them
separate, because the last of those is the honest quantity. This is a nonconvex empirical solver
with no optimality certificate.

### Weighted k-means

After projection and whitening, weighted Lloyd iterations from deterministic k-means++ restarts
minimize within-cell squared distance, which is the normalized-trace objective. The resulting rule
is an ordinary Euclidean Voronoi quantizer in whitened score space.

### Exact scalar dynamic program

When the effective score space is rank one after projection, the D-optimal partition has ordered
interval cells, so a weighted interval dynamic program returns the **global** optimum rather than a
local one. `ScalarDPConfig` rejects a higher-rank score space by name rather than approximating it,
and `max_rows` bounds the exact quadratic recursion.

## 5. Certificate

Nothing below runs implicitly during fitting; each is an explicit call on results you already have.

**Exchange stability.** `exchange_stability_report(scores, labels, ...)` runs exactly one complete
exact scan of a supplied labeling and nothing else, so labels from any origin — a rejected batch, an
external tool, a hand edit — can be checked before they are trusted. It reports the exact objective,
the best remaining gain, and the improving move when one exists. Every `PartitionResult` already
carries the same verdict as `exchange_stable` and `best_remaining_gain`.

**Geometry.** A `DOptimality` result carries a `GeometryReport` measuring the largest
Mahalanobis-Voronoi violation of the terminal metric, the log-determinant gain such a violation
guarantees is being left on the table, the largest exact gain it actually leaves, and the
cell-separation residual against the leverage bound. A `ProfiledDOptimality` result carries a
`ProfiledGeometryReport` instead. The two are never merged under one name, because they describe
different objects: a strict Voronoi rule that exchange stability forces, and an efficient
semimetric whose Voronoi rule a stable profiled partition may legitimately violate.

Both stability and geometry are certified *at a tolerance*, and both reports record it as
`gain_tolerance`. A finite solver stops when no relocation gains more than that threshold, so
`voronoi_consistent` means no Voronoi violation is worth more than it — never a claim at tolerance
zero. The distinction only bites at scale: the Theorem-3 guaranteed gain shrinks like \(1/N^2\), so
past roughly a million rows a handful of rows may legitimately sit a hair past a cell boundary
inside the default \(10^{-10}\). Verifying such a state at zero would reject a partition the solver
converged on. Pass
`gain_tolerance=0.0` to `exchange_stability_report` when the stricter question is the one you want
answered.

**Compilation.** `PartitionResult.compile_quantizer()` is the D-specific bridge from the finite task
to the inductive one. It applies only to `DOptimality`, requires exchange stability and nonsingular
geometry, and verifies that the compiled Mahalanobis rule reproduces every positive-weight training
label — except where the `geometry` certificate has priced the disagreement at or below its
`gain_tolerance`, which is the same tolerance the solver stopped at.

**Profiled ceiling.** `efficient_score_bound(scores, interest=..., n_bins=...)` bounds the profiled
information of *every* rule with that cell budget by the between-cell information of the full-data
efficient score \(\hat s=s_\psi-B^\ast s_\lambda\). For one parameter of interest the maximizing
rule has ordered interval cells and is found exactly, so `upper_bound` is a certificate rather than
an estimate, and `gap_to(result)` is the remaining slack. Its labels double as the `initial_labels`
initializer for profiled exchange. More than one interest column raises `NotImplementedError`: a
multivariate efficient score would need a multivariate solver, and the answer would no longer be
certified.

**Global optimality.** `certify_partition(scores, n_bins=..., incumbent=...)` decides global
optimality by depth-first branch and bound with the singleton-completion upper bound — unassigned
atoms are left as singleton cells, so refinement monotonicity of the log determinant bounds every
completion of a partial assignment. It returns `status="optimal"` only when the tree was exhausted;
a spent node budget returns `status="budget_exhausted"` with the outstanding bound and gap. The
search is exponential, so `CertificationConfig` guards both the node count and the number of
distinct score atoms and refuses an oversized instance by name. Certification is `DOptimality` only:
the refinement bound uses Loewner monotonicity of \(\log\det\), which the profiled Schur objective
does not inherit.

## Reading the numbers

Retention is reported as the spectrum of \(I_B\) relative to \(I_\infty\) in the informative
subspace, summarized by `arithmetic_mean_retention`, `geometric_mean_retention` (the D-efficiency),
and `logdet_retention`. Optimizer traces carry an explicit `objective_label`, because solvers do
not share one convention: `"whitened_sse"` is a minimized within-cell squared error in whitened
coordinates, while `"logdet_retained"` and `"profiled_logdet"` are maximized log determinants. Two
traces are comparable only under the same label.

Validation sources are diagnostic. They never influence gradients, stopping, initialization
selection, or checkpoints — and the optimizer is judged by the final hardened partition, not by a
soft objective it passed through on the way.
