# Publication-grade audit of DS16 stable margins and the compile verdict

**Claims:** `DS-STABLE-MARGINS-PRICE`,
`DS-PROFILED-COMPILE-CERTIFICATE`, `DS-STABLE-STATE-SELECTION`  
**Audit:** `AUDIT-DS-STABLE-MARGINS-COMPILE`  
**Date:** 30 August 2026  
**Source frozen:** branch `research-ds-stable-margins-compile`, commit
`1b58518`  
**Result:** all three claims **hardened**. The DS16 PRICE/FUNNEL/FLOOR
mathematical core survives after a necessary uniform-law repair and sharper
centering/quantifier conventions. The compile conclusion survives only as an
inventory of currently established paths and as a DS14 theorem for certified
sequences, not as mathematical uniqueness or a population guarantee from one
finite certificate. The measured selection claim survives after two reporting
corrections.

## 1. Target statement

For i.i.d. exact scores (S=(S_\psi,S_\lambda)\in\mathbb R^2), equal
weights, (ES=0), finite positive-definite second moment, (K\ge3), law
class (L)+(S), and empirical information computed after exact sample
centering, DS16 asserts:

1. **PRICE.** For every (\kappa>0), all finite labelings retaining
   (\hat I_{\lambda\lambda}\ge\kappa) have asymptotic profiled value at
   most (v_K-\delta(\kappa)) for some population constant
   (\delta(\kappa)>0). This must be pathwise and uniform over labeling
   sequences; stability and seeding are irrelevant.
2. **FUNNEL.** Every feasible sequence whose profiled value converges to
   (v_K) converges in sample measure, up to relabeling, to the unique
   efficient-score interval partition (J^*). Its cells retain positive
   limiting masses while its nuisance and cross blocks vanish.
3. **FLOOR.** Fixed population quantizers with
   (I_{q,\lambda\lambda}>\kappa) induce empirical labelings approaching
   their population profiled value, giving a lower envelope
   (v^{*+}(\kappa)) for the constrained empirical supremum.
4. **Compile.** The projected efficient-score interval rule is the
   unconditional deployment route; a companion profiled rule is available
   only conditionally through DS14 and must report its information price.
5. **Selection evidence.** Exact small-(N) censuses and public-library
   runs exhibit nuisance/value anti-correlation, stable states in both margin
   regimes, centered-law seed instability, and large-(N) funnel behavior.

The audit treats the three registered nodes separately. A measured statement
cannot provide theorem authority, and a theorem about sequences cannot be
promoted to a finite population certificate.

## 2. Criterion and problem level

- **Criterion:** profiled (D_s), scalar POI and scalar nuisance. For a
  labeling (z), (\hat\Phi_s) is the Schur value of its binned second-moment
  information when the nuisance block is positive.
- **Levels:** `empirical_to_population` for PRICE/FUNNEL/FLOOR;
  `empirical_inductive_quantizer` for compilation; `finite_assignment` for
  the selection measurements.
- **Decision variables:** arbitrary finite hard labelings for PRICE/FUNNEL;
  fixed measurable raw-score quantizers for FLOOR; one-point exchange
  terminals only for the measured and DS14 companion-rule parts.
- **Oracle:** exact score rows. Estimated scores remain P2.
- **Runtime boundary:** no library behavior is changed in this audit and no
  file under `src/` is edited.

## 3. Status before the audit

At `1b58518` both mathematical nodes were `project_proved`, the selection node
was `measured`, and none had an independent audit pointer. The source proof
presented Lemma DS16.1 as a uniform arbitrary-grouping rigidity result, then
used it with the Proposition-4 sandwich. It described the projected rule as
the "only unconditional theorem-backed compile path" and described a finite
measured DS14 triple plus stability as a certificate-gated conditional path.

The source measurements reported 18--944 stable states per census instance
and a 0.004--0.046 library gap. Both figures required checking against the
committed raw summary rather than trusting the prose.

## 4. Dependencies rechecked

The upstream DS11--DS15 results were not re-proved. Their exact registered
statements, imported hypotheses, and audited hardenings were checked against
the uses made by DS16.

1. **DS11 / `DS-PROFILED-VARIATIONAL`.** The scalar specialization gives
   the exact identity
   
   \[
   \hat\Phi_s(z)=\operatorname{btw}(\hat s_N;z)
   -\hat c(z)^2/\hat I_{\lambda\lambda}(z)
   \le \operatorname{btw}(\hat s_N;z).
   \]
   
   DS16 uses only feasible positive nuisance blocks. The audit's Fraction
   suite recomputed the identity/sandwich on all adversarial labelings and
   found zero failures.
2. **DS8 / `DS-SCALAR-EFFICIENT-DP`.** One-dimensional SSE optima may be
   taken as sorted interval partitions, giving
   (\operatorname{btw}\le\hat v_K). Duplicate efficient scores do not
   invalidate the value statement; the independent lattice search included
   exact ties.
3. **DS15 / `OPEN-DS-MARGINS-AT-OPTIMA`.** DS16 legitimately imports the
   audited scalar scope (d_\psi=d_\lambda=1), the unique population
   (K)-quantizer under (S), empirical scalar-value convergence, boundary and
   mass consistency, and the Proposition-4 sandwich. It does **not** need
   DS15's swap-richness (R) for PRICE, FUNNEL, or FLOOR. (R) is needed only
   for DS15's separate finite-feasible-global-optimum achievability result.
4. **DS14 / `OPEN-DS-FINITE-POP-BRIDGE`.** Its hypotheses are on an entire
   exchange-stable sequence: (M1)/(M4) on the law and eventual uniform
   (M2)/(M3)/(M5), or its audited merged variant. DS13 bounds violations at a
   stable state; it is not a substitute for exact stability and does not turn
   one finite diagnostic into the DS14 asymptotic conclusion.
5. **Rank nodes.** For centered rows, the cell-moment columns satisfy a
   positive linear relation, so (\operatorname{rank}(I_z)\le K-1). A
   positive nuisance block and positive scalar Schur complement require full
   rank two; hence (K\ge3=d_\psi+d_\lambda+1). The source aside that
   (K\ge d) can suffice for an off-centered moment matrix is algebraically
   true but not an alternative score/Fisher semantic and has been removed
   from the compile claim.

No upstream claim looked false under its audited scope, so no separate
upstream audit task was opened. The defect was in DS16's use/exposition of a
uniform law and in the compile claim's interpretation of DS14.

## 5. Nearest literature

The audit ran an independent primary-source pass, logged in
`LITERATURE/audits/AUDIT-DS-STABLE-MARGINS-COMPILE-30-August-2026.md`.
Only after reaching its conclusions was it compared with the researcher-side
triangulation.

- **Rakhlin--Caponnetto 2006** (`Rakhlin-Caponnetto-2006`) directly precedes
  the compact-codebook almost-minimizer rigidity ingredient: under uniqueness,
  population near-minimizers shrink, and a covering-number uniform law
  transfers the result empirically. It does not cover arbitrary index
  groupings, unbounded finite-second-moment laws, signed nuisance moments, or
  a profiled-information price.
- **Telgarsky--Vattani 2010** (`Telgarsky-Vattani-2010`) is the nearest
  primary reference for finite Hartigan one-point terminal geometry. It also
  warns that exchange terminals are not interchangeable with Voronoi states.
- **Blanchard--Jaffe--Zhivotovskiy 2025/2026** is the nearest balanced-
  clustering comparison. Its minimum-size constraint repairs a weak-moment
  consistency pathology, not the profiled objective's nuisance degeneracy.
- **Silvey 1978** gives the singular-(D_s)-design background, with a convex
  design-weight feasible set rather than hard sample partitions.
- **Alsing--Wandelt 2019** is direct continuous nuisance-hardened compression
  precedent, but has no finite alphabet or profiled hard-quantizer compiler.

The codebook-rigidity ingredient is therefore prior art and is now attributed.
No primary source found proves the combined all-groupings nuisance price,
value funnel, or compiler consequence. Each target keeps
`literature_search_status: search_gap`; this is not a novelty claim.

## 6. Counterexample search

The independent harness is
`py/audit_ds_stable_margins_compile.py`. It imports no code from
`py/ds_stable_margins.py`. Its exact path uses only the standard library and
`Fraction`; every candidate move is evaluated by rebuilding the destination
partition and its moments, not by reusing the researcher's rank-update or
classification logic. Script SHA-256:
`2c98971ae01d42749c87bce5ee7c0b21d0e08e4dcf8990aa21526b8ae81c4fea`.

**Fixtures from raw scores.** For `CE-DS-STABLE-MARGIN-RETAINING-001`, all
966 canonical partitions were enumerated. The declared labeling has exact
value
(3416482747129/14376887844864), nuisance block
(219373899/419430400), minimum mass (1/4), and all 16 admissible gains are
nonpositive; the largest is
(-329181847579541084791/107530695533215013142528). It is stable and
non-global. For `CE-DS-INTERVAL-SEED-UNSTABLE-001`, the independent
classifier reproduces the improving gain
(2335473863255583/5219865952157696\approx0.4474), with nuisance information
rising from (1742559/419430400) to (46347881/419430400).

**Census sample.** Four full lattices, centered06/mix3 at (N=10,12), give
stable counts 25, 58, 5, 134 and non-global stable counts 24, 57, 4, 133.
The gap/nuisance correlations are respectively -0.627, -0.574, -0.825,
-0.413; interval stability and every checked exact source field match. This
also exposes the prose error: the committed ten-instance census range is
**5--944**, not 18--944.

**Adversarial rational sweep.** Five datasets cover split duplicates,
unequal weights, exact ties, a near-singular nuisance block, and tiny-cell
pressure ((N\le8)); 0 sandwich failures were found. Exact-tie data produced
12 global optima without breaking the value inequalities. At the centered
(d=3) boundary every feasible (K=3) profiled value is zero, while (K=4)
restores exact value (9/5), confirming the cardinality restriction. A
scalar (d=1) control separates positive between-value rank from an
inapplicable profiled criterion.

**Public library run.** At (N=100), both gauss06 and mix3 were run from
efficient-score, k-means++, and random seeds. All six terminals pass an
independently recomputed move-stability check. Centered-law
(N\hat I_{11}=2.998,2.372,0.481), with log gaps 0.0349, 0.00962, and
0.0751. The random gap exceeds 0.046, showing the registered interval was not
a run-wise bound. Mix3 has (\lambda_{\min}=1.704\)--1.705 and gap
(6.84\times10^{-5}) for every seed.

No new theorem counterexample was found. The exact artifacts are under
`AUDITS/artifacts/AUDIT-DS-STABLE-MARGINS-COMPILE-001/`.

## 7. Algebraic reduction

Let (x_i=\hat s_{N,i}). For any grouping (z), with its own scalar cell
centroids,

\[
P_Nx^2=\operatorname{btw}(x;z)+\operatorname{WSSE}(x;z),\qquad
\hat\Phi_s(z)\le\operatorname{btw}(x;z)\le\hat v_K.
\]

Thus every profiled-value near-maximizer is an SSE near-minimizer, regardless
of exchange stability. The remaining problem is purely a uniform rigidity
statement for **arbitrary groupings**, followed by recovery of nuisance
moments.

For a grouping's centroid set (C(z)), reassigning each point to a nearest
centroid can only decrease SSE:

\[
P_N\min_{c\in C(z)}(x-c)^2\le\operatorname{WSSE}(x;z).
\]

This remains true when equal observations are split between cells. The
necessary stochastic bridge is not a pointwise SLLN at a subsequential random
codebook. It is

\[
\sup_{\beta\in\mathcal B,C\in[-R,R]^K}
|(P_N-P)\min_{c\in C}(S_\psi-\beta S_\lambda-c)^2|\to0\quad a.s.
\]

for compact (\mathcal B) and finite (R). Truncation plus finite parameter
nets proves it: the class is finite-dimensional and continuous, with envelope
(A_R(1+\|S\|^2)). This is the load-bearing repair.

Nuisance recovery uses the signed class
(S_\lambda1\{S_\psi-\beta S_\lambda\le c\}). Split positive and negative
parts; half-planes are finite VC, (E|S_\lambda|<\infty), and the class
already ranges over all ((\beta,c)), so compact tilt uniformity is not an
extra data-dependent step. Atomlessness makes limiting boundary slabs null;
(L) makes every limiting interval nuisance moment zero.

## 8. Proof / conditional result

**Lemma DS16.1, repaired.** Fix (\varepsilon>0). Uniform integrability of
the empirical second moments makes cells of mass below (\eta) contribute
at most (\rho(\eta)+o(1)), with (\rho(\eta)\downarrow0). If such a cell
existed in a sufficiently near-optimal (K)-grouping, merge it into a bounded
active cell. The result has at most (K-1) cells and adds at most
(\rho(\eta)+o(1)) SSE, contradicting the positive limiting distortion gap
(W_{K-1}-W_K). Empty cells are included as mass zero. Therefore all cells
have a uniform positive mass and all centroids lie in a compact interval.

Nearest-centroid reassignment plus the compact tilt--codebook uniform law
forces every subsequential codebook limit to minimize the population
(K)-means risk. Assumption (S) makes that codebook (C^*) unique. For
codebooks close to (C^*), every point assigned across a midpoint and outside
a width-(t) slab pays a fixed excess proportional to (t) times the minimum
centroid gap. Near-optimality bounds the off-slab misassignment mass; the
empirical slab mass tends uniformly to its population value and then to zero
as (t\downarrow0). This proves symmetric-difference convergence to (J^*),
including split duplicates and sample-dependent groupings.

**PRICE.** Define the supremum of an empty constrained labeling class as
(-\infty). At fixed (N), the supremum is a maximum over finitely many
measurable labeling functionals. Intersect the uniform-law events over
rational tolerances and integer compact radii. On the resulting single
probability-one event, Lemma DS16.1 holds simultaneously for all labelings and
all large (N). If constrained between-values approached (v_K), cell
symmetric differences would be small; Cauchy--Schwarz and the signed weighted
VC law would make every nuisance cell moment small while the cell masses stay
bounded below, contradicting (\hat I_{\lambda\lambda}\ge\kappa). This gives
a positive (\delta(\kappa)). Because the event is pathwise, every labeling
sequence, even a data-dependent selection, obeys the cap without its own
exceptional null set.

**FUNNEL.** If (\hat\Phi_s(z_N)\to v_K), the sandwich and
(\hat v_K\to v_K) force the between-values to (v_K). Apply rigidity at a
sequence of shrinking tolerances. Cell masses converge to (w_b^*>0), all
nuisance moments vanish, and the cross block vanishes by bounded second
moments and the positive mass floor. Therefore
(\lambda_{\min}(\hat I_N)\le\hat I_{\lambda\lambda}\to0).

**FLOOR, corrected convention.** Label observation (i) by the fixed rule
(q(S_i)), then use centered rows in the empirical moment. For cell (b),

\[
\hat m_b=P_N[S1_{q(S)=b}]-\bar S_NP_N(q(S)=b)\to m_b.
\]

The ordinary LLN gives masses and moments, hence Schur-value convergence when
(I_{q,\lambda\lambda}>\kappa). Applying an arbitrary discontinuous (q) to
the sample-centered row would be a different, sample-dependent rule and is
not needed. The result gives the strict-constraint supremal floor
(v^{*+}(\kappa)); it proves neither attainment nor one-sided continuity.
The closed constraint
(v^*(\kappa)=\sup\{\Phi(q):\lambda_{\min}(I_q)\ge\kappa\}) is a different
quantity and only satisfies (v^*(\kappa)\le v^{*+}(\kappa)) here.

## 9. Adversarial audit

- **Strictness and ties:** exact-tie data with 12 global partitions preserve
  the sandwich. Strict positivity of (\delta) comes from rigidity plus the
  nuisance contradiction, not a finite optimum gap. Constrained-value
  attainment/continuity is removed.
- **Singleton/empty cells:** the deletion comparison uses the positive
  (K)-versus-(K-1) population distortion gap. Empty cells are the zero-mass
  case; singleton mass cannot persist in the funnel.
- **Duplicate scores:** split duplicates are allowed in arbitrary groupings.
  Nearest-centroid reassignment is a value comparison, not an assertion that
  the original grouping is Voronoi. Boundary duplicates are confined to
  shrinking slabs; (S) excludes a population atom there.
- **Singular information:** PRICE admits full-information singularity;
  zero profiled values satisfy the cap trivially. Its constrained class
  requires a positive nuisance block. The centered (K=2) rank boundary is
  excluded by (K\ge3).
- **Nuisance singularity:** the theorem explicitly distinguishes
  (I_{\lambda\lambda}\ge\kappa) from
  (\lambda_{\min}(I)\ge\kappa). The latter implies the former by a diagonal
  bound, not conversely.
- **Atomic laws:** the exact grid censuses are evidence only. The theorem
  retains (S), including atomlessness/positive density near optimal
  boundaries and uniqueness.
- **Hidden compactness:** active masses plus second-moment bounds compactify
  centroids. The random-codebook SLLN is replaced by an explicit uniform law
  over each compact parameter set.
- **First-order-to-finite jumps:** PRICE/FUNNEL do not use first-order or
  exchange arguments. The compile branch keeps exact exchange stability as a
  premise of DS14; DS13 alone is not promoted to a certificate.
- **Empirical-to-population jumps:** every such jump is now either the compact
  uniform codebook law, the signed weighted-VC law, the fixed-rule LLN, or the
  already-audited DS15 scalar convergence. A one-(N) diagnostic is not
  called a DS14 population guarantee.
- **Score-estimation error:** excluded. Exact score provenance remains an
  explicit assumption.
- **New-event extension:** arbitrary training labels do not themselves define
  a rule for new events. Only the projected rule is unconditional in the
  current registry; DS14 companion rules are sequence-conditional and OP30
  governs their inhabitation.

The prover-declared weak points (i)--(vii) are all covered above. The only
proof-invalid step found was repairable; the only deployment overclaims were
terminological/logical and are now narrowed.

## 10. Algorithmic consequence

Free profiled exchange optimization remains valid as a finite assignment
solver, but a high objective value cannot simultaneously certify a fixed
nuisance margin on the DS16 class. Exchange stability is not a route around
the price theorem. A practical margin-retaining solver would need an explicit
constraint or penalty, and its existence, convergence, and relation to
(v^*(\kappa)) remain open.

The projected scalar interval DP remains the exact upper-bound computation
for this scalar class. The finite quantity that can be reported is
(\hat v_K-\hat\Phi_s). The audit does not authorize a library compiler
change.

## 11. Deployability consequence

The projected efficient-score interval rule is the **only currently
established unconditional route in the registered theory**. This wording does
not prove that every conceivable alternative compiler is impossible. It also
uses a different statistical formulation: nuisance information is supplied
externally/unbinned rather than required from the hard bins.

A finite exchange-stable state passing measured mass, conditioning, and
separation thresholds may be used to construct and inspect a candidate DS14
companion rule. It does not, by itself, prove eventual margins, the law's slab
condition, population stationarity, or held-out performance. Those conclusions
belong to sequences satisfying all DS14 hypotheses. Certificate-branch
inhabitation is still OP30.

## 12. Information-loss consequence

For the scalar DS16 class, a labeling with
(\hat I_{\lambda\lambda}\ge\kappa), and therefore any labeling with
(\lambda_{\min}(\hat I)\ge\kappa), has asymptotic profiled value at most
(v_K-\delta(\kappa)). If (v_K>0), its population-ceiling retention is at
most (1-\delta(\kappa)/v_K). This is additional to the quantization loss
from unbinned efficient-score variance to (v_K).

The theorem is existential: it gives no numeric (\delta(\kappa)) from one
dataset. The observable diagnostic is the finite DP gap
(\hat v_K-\hat\Phi_s), not an estimate of the theorem's lower bound. It
does not bound held-out performance or estimated-score error.

## 13. Updated status

- `DS-STABLE-MARGINS-PRICE`: **hardened** (`project_proved` retained). Core
  PRICE/FUNNEL/FLOOR conclusions verified under the corrected uniform law,
  common-event quantifier, centered-moment convention, and non-attainment
  warning.
- `DS-PROFILED-COMPILE-CERTIFICATE`: **hardened** (`project_proved`
  retained). “Only” is registry-relative; DS14 is sequence-conditional; a
  finite diagnostic is not a population certificate; OP30 stays open.
- `DS-STABLE-STATE-SELECTION`: **hardened** (`measured` retained). Qualitative
  conclusions reproduced. Stable-count range corrected to 5--944, and the
  0.004--0.046 gap is no longer presented as a per-run bound.

No target is refuted after hardening. No new boundary counterexample is
required.

## 14. Registry patch under `claims/`

The audit adds `audit: AUDITS/AUDIT-DS-STABLE-MARGINS-COMPILE-001.md` to all
three target nodes and creates
`claims/AUDIT-DS-STABLE-MARGINS-COMPILE.json`. The patches:

- state exact score, equal-weight, scalar POI/nuisance, raw-label and centered-
  moment conventions;
- define the empty constrained supremum and the common pathwise event;
- separate (v^{*+}(\kappa)) from (v^*(\kappa)), with no attainment or
  continuity claim;
- remove the off-centered score-semantics implication;
- distinguish a DS14-certified sequence from one finite diagnostic;
- keep certificate inhabitation and constrained-solver existence in
  `OPEN-DS-STABLE-BASINS`;
- add Rakhlin--Caponnetto and Telgarsky--Vattani attribution while retaining
  the three independent `search_gap` decisions;
- correct the measured range and qualify the library gap summary.

Generated indexes are rebuilt only through `py/registry.py reindex`.

## 15. Counterexample/regression artifact

No new exact fixture is needed because no hardened theorem is false. Both
existing boundary fixtures were independently recomputed from their raw score
arrays and remain CI-pinned by
`tests/test_research_claims.py::test_ds16_exchange_stable_state_can_retain_macroscopic_margins`
and
`tests/test_research_claims.py::test_ds16_efficient_score_interval_seed_is_not_exchange_stable`.

The audit adds four ledger rows:

- `N-DS-AUDIT16-FIXTURES`;
- `N-DS-AUDIT16-CENSUS`;
- `N-DS-AUDIT16-ADVERSARIAL`;
- `N-DS-AUDIT16-LIBRARY`.

Their executable source and complete provenance are stored in
`AUDITS/artifacts/AUDIT-DS-STABLE-MARGINS-COMPILE-001/exact.json` and
`library.json`. The census and library reporting corrections are not theorem
counterexamples and therefore do not create misleading counterexample-bank
entries.

## 16. Next dependency-blocking question

**OP30 / `OPEN-DS-STABLE-BASINS`:** for some fixed (\kappa>0), do there
exist almost-sure sequences of margin-compatible one-point exchange-stable
states satisfying DS14's eventual hypotheses, and can a concrete constrained
solver reach them with a proved gap to a correctly defined, attained
constrained population value?

Until that is answered, the companion-rule branch is a valid conditional
theorem but not an inhabited deployment path. The immediate mathematical
subproblem is existence/attainment for (v^{*+}(\kappa)) or
(v^*(\kappa)) under a compact rule class together with an exchange-stable
empirical approximation theorem.
