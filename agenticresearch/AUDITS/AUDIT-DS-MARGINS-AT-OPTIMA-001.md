# Publication-grade audit of the DS15 margins dichotomy

**Claim:** `OPEN-DS-MARGINS-AT-OPTIMA`
**Audit:** `AUDIT-DS-MARGINS-AT-OPTIMA`
**Date:** 30 August 2026
**Result:** theorem verified for \(d_\psi=d_\lambda=1\) after refuting the
registered \(d_\lambda\)-generality (exact rank-vacuity boundary
counterexample), hardening Proposition 6 from a sketch to a proof, correcting
a misattributed Glivenko–Cantelli import in conclusion (3), and supplying the
missing Proposition 5 derivation.

## 1. Target statement

Let \(S=(S_\psi,S_\lambda)\sim P\) on \(\mathbb R^2\) (\(d_\psi=d_\lambda=1\)),
\(ES=0\), \(E\|S\|^2<\infty\), \(I=E[SS^\top]\succ0\), efficient score
\(\hat s=S_\psi-B^*S_\lambda\). Assume

- **(L)** \(E[S_\lambda\mid\hat s]=0\) a.s.;
- **(S)** \(\operatorname{law}(\hat s)\) atomless with positive density near
  the optimal cell boundaries and a unique optimal scalar \(K\)-quantizer
  under squared error;
- **(R)** two-sided conditional nuisance-sign richness near the optimal
  boundaries.

Let \(z^{(N)}\) be exact global maximizers of the in-bin profiled \(D_s\)
value \(\hat\Phi_s\) over feasible \(K\)-cell labelings of i.i.d. samples
(\(K\ge3\), equal weights, exact empirical centering, nonsingular binned
nuisance block). Then almost surely: (i)
\(\hat\Phi_s(z^{(N)})\to v_K=\sup_q S_\psi^+(I_q)\) over all measurable
\(K\)-cell quantizers, attained only at the optimal \(\hat s\)-interval
quantizer \(J^*\), which is fully nuisance-degenerate and in-bin infeasible;
(ii) cell masses converge to the positive population masses of \(J^*\) —
the (M2) mass margin is automatic and singletons die out; (iii)
\(\hat I_{\lambda\lambda},\hat I_{\psi\lambda}\to0\), so
\(\lambda_{\min}(\hat I_N)\to0\) — the (M3) conditioning margin fails for
every \(\kappa>0\) and every law in the class; (iv)
\(v^*(\kappa)=\sup\{\Phi(q):\lambda_{\min}(I_q)\ge\kappa\}<v_K\) for every
\(\kappa>0\); (v) the DS11(a) efficient-score domination gap at \(z^{(N)}\)
tends to \(0\).

The registered statement had \(S\in\mathbb R^{1+d_\lambda}\) with only
\(K\ge3\); that generality is refuted (§6, §7) and the claim is hardened to
\(d_\lambda=1\).

## 2. Criterion and problem level

- Criterion: in-bin profiled \(D_s\) (Schur complement of the binned
  information), with the DS11 pseudo-inverse extension at singular nuisance
  blocks for population suprema.
- Level: `empirical_to_population`.
- Decision variable: hard labelings of finite i.i.d. score samples; the
  population objects (\(v_K\), \(J^*\)) enter only as limits.
- Score oracle: direct/exact scores; estimated scores are excluded (P2).

## 3. Status before the audit

`OPEN-DS-MARGINS-AT-OPTIMA` was `project_proved` (packet
`WORK/completed/DS-MARGINS-AT-OPTIMA.md`, 29 Aug 2026) with
`warning: "Not yet independently audited."`, no `audit` field, no
counterexamples, `literature_search_status: search_gap` from the researcher's
own 29 Aug triangulation.

## 4. Dependencies rechecked

Every dependency was re-derived or re-verified in this session, not taken
from the researcher's summaries.

1. `DS-PROFILED-VARIATIONAL` (DS11): the variational identity and its
   completion-of-squares proof were re-derived; the exact empirical form
   (Proposition 4's engine) was verified in exact rationals on 8 adversarial
   datasets over their full partition lattices (§6). The prior audit
   (`AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md`) already traces the core
   identity to Krein/Anderson/Li–Mathias.
2. `DS-EFFICIENT-SCORE-DOMINATION` (DS7): re-derived in one line from DS11
   at \(B=B^*\); its empirical form is the middle sandwich inequality,
   verified exactly on every instance of §6.
3. `DS-SCALAR-EFFICIENT-DP` (DS8, 1-D contiguity): verified against the full
   lattice — on all 28 instances of §6 the between-value optimum over *all*
   partitions equals the best contiguous grouping of the sorted
   \(\hat s\)-values, including datasets with exact duplicate \(\hat s\)
   values and unequal weights.
4. `DS-GLOBAL-TIE-DEGENERACY` / `CE-DS-DEGENERATE-GLOBAL-TIE-001`: retained
   as the atomic-law boundary witness; its CI pin was not touched. DS15's
   "the 31-fold tie was an atomic-grid artifact" is consistent with the
   fixture (the tie lives on the 1/8 grid, which violates (S)); zero exact
   ties occur on any of this audit's 20 fine-grid full-lattice scans.
5. `DS-FULL-PROFILE-K-LE-D-SINGULAR` / `FI-RANK-CEILING` (DS9): the rank
   ceiling \(\operatorname{rank}(I_z)\le K-1\) under exact centering was
   re-derived and is the engine of the new boundary counterexample (§7).

**Graph defects found and repaired.** The claim's `dependencies` listed
`DS-PROFILED-VARIATIONAL`, `OPEN-DS-DOMINATION-EQUALITY`,
`DS-GLOBAL-TIE-DEGENERACY` — omitting DS7, DS8, and the DS9 rank nodes, all
load-bearing in the proof; and `OPEN-DS-DOMINATION-EQUALITY` was listed as a
*dependency* although its own statement asserts DS15's conclusion (v) — a
circular edge. The patch adds `DS-EFFICIENT-SCORE-DOMINATION`,
`DS-SCALAR-EFFICIENT-DP`, `DS-FULL-PROFILE-K-LE-D-SINGULAR` and removes
`OPEN-DS-DOMINATION-EQUALITY` (the arrow runs the other way, via `implies`).
DS14 (`OPEN-DS-FINITE-POP-BRIDGE`) is *not* added: the audited proof uses
none of DS14's machinery — the misattributed "audit §8" import is replaced by
a self-contained lemma (§8) — and DS14 already lists DS15 in its `implies`.

## 5. Nearest literature and transfer boundary

Independent targeted search, 30 Aug 2026 (query log and per-source
triangulation in
`LITERATURE/audits/AUDIT-DS-MARGINS-AT-OPTIMA-30-August-2026.md`).

<!-- FILLED-FROM-SEARCH -->

## 6. Counterexample search

Independent suite `py/audit_ds_margins_at_optima.py` — pure stdlib, exact
`fractions.Fraction` on every claim-relevant quantity, own CLT-rational law
emulation (exact correlation \(3/5\) via the rational rotation
\((3/5,4/5)\)) and integer-LCG seeds, no code shared with the researcher's
scripts. Committed run artifacts with seeds, git revision, script hash, and
environment: `AUDITS/artifacts/AUDIT-DS-MARGINS-AT-OPTIMA-001/`.

- **identities** (8 datasets × full lattice; duplicate atoms, unequal
  positive weights, a nuisance-symmetric sample with exact duplicate
  \(\hat s\) values, LCG instances): the Proposition 4 identity
  \(\hat\Phi_s=\mathrm{btw}-\hat c^2/\hat I_{\lambda\lambda}\), the sandwich
  \(\mathrm{btw}\le\hat v_K\), full-lattice 1-D contiguity, and the
  singular-nuisance boundary (\(\hat c=0\), pseudo-inverse value
  \(=\mathrm{btw}\) exactly) hold on every labeling — 0 violations.
- **vacuity**: the \(K=d_\lambda+1\) boundary. Minimized witness
  `CE-DS-MARGINS-RANK-VACUITY-001` (\(N=4\), integer scores with zero column
  sums, \(d_\lambda=2\), \(K=3\)): all 6 feasible labelings have profiled
  value exactly \(0\); efficient-score interval optimum \(81/50>0\);
  \(K=4=d_\lambda+2\) restores value \(9/5>0\) on the same atoms. Random
  \(N=6,7,8\) instances confirm (1,354 labelings, all feasible values 0).
  **This refutes conclusion (i) of the registered statement for
  \(d_\lambda\ge2\), \(K=d_\lambda+1\).**
- **exhaustive** (20 instances: 2 laws × 2 reps × \(N=12..16\); all
  \(S(N,3)\) canonical partitions per instance, up to 7,141,686; ≈42.6M
  exact profiled evaluations total): sandwich and tax identity exact on
  20/20 optima; **zero exact ties over the full lattice on every instance**;
  no singleton on the conditionally centered law, one singleton on the
  non-centered control (\(N=15\)); the centered law's optimum nuisance block
  stays small while the non-centered control's stays macroscopic — the (L)
  class boundary reproduced independently.
- **screen probe** (inside the same passes): the researcher's float top-64
  labeled screen, re-implemented with its \(10^{-9}\) nuisance guard, ranks
  the exact optimum **first** with **zero guard casualties** on 20/20
  instances at \(N=12\)–\(16\) — validating the screen mechanism in the
  \(N\ge14\) range where the original N-DS-MARGINS-TREND optima are
  screen-selected. The original \(N\ge14\) instances themselves remain
  uncertified (their committed outputs do not exist in the repo); the trend
  row now carries that caveat.
- **scalar anchor**: exact-rational interval DP at \(N=1000\), \(K=3\):
  the library's float `scalar_interval_dp` reproduces the exact optimum
  (SSE agreement \(10^{-9}\), identical min cell mass \(49/200=0.245\) vs
  population \(0.2703\)) — the float-only (M2) evidence row
  N-DS-SCALAR-MASS gains an exact anchor.

## 7. Algebraic reduction

Two pieces of finite algebra carry the audit.

**(a) The projection-tax identity (Proposition 4).** With
\(\hat s_N=s_\psi-\hat B^*_Ns_\lambda\) from the full-sample normal equations
(\(\sum_iw\hat s_{N,i}s_{\lambda,i}=0\)) and, for a labeling \(z\),
\(x_b=m_{\hat s,b}/\hat W_b^{1/2}\), \(y_b=m_{\lambda,b}/\hat W_b^{1/2}\):
expanding the DS11 variational form at \(B=\hat B^*_N+t\) and minimizing the
quadratic in \(t\),

\[
\hat\Phi_s(z)=|x|^2-\frac{\langle x,y\rangle^2}{|y|^2}
=\mathrm{btw}(\hat s_N;z)-\hat c(z)^2/\hat I^z_{\lambda\lambda}.
\]

The subtracted tax is nonnegative; on singular labelings PSD-ness forces
\(\hat c=0\) and the pseudo-inverse value equals \(\mathrm{btw}\) exactly (so
the sandwich also covers the singular boundary). \(\mathrm{btw}\le\hat v_K\)
by 1-D contiguity of the scalar optimum (DS8), which the audit verified
against full lattices rather than assuming.

**(b) The rank-vacuity boundary.** Exact centering gives \(\sum_bm_b=0\),
hence \(\operatorname{rank}(I_z)=\operatorname{rank}(VV^\top)\le K-1\) for
\(V=[m_b/\sqrt{W_b}]_b\) (the columns satisfy one nontrivial linear
relation with positive coefficients \(\sqrt{W_b}\)). Generalized Schur rank
additivity,
\(\operatorname{rank}(I_z)=\operatorname{rank}(I_{z,\lambda\lambda})
+\operatorname{rank}(S_\psi^+(I_z))\), then forces \(S_\psi^+(I_z)=0\)
whenever \(I_{z,\lambda\lambda}\succ0\) with \(d_\lambda=K-1\): at
\(K=d_\lambda+1\) *every feasible labeling of every sample* has profiled
value exactly zero, while \(v_K>0\) is attained by the (infeasible)
pseudo-inverse extension at \(J^*\). At \(d_\lambda=1\) the same argument
shows \(K=2\) is vacuous — the theorem's \(K\ge3\) is exactly
\(K\ge d_\lambda+2\), which is the correct general cardinality condition.

## 8. Proof / conditional result

The audited proof re-derivation, item by item. Lemmas 1–2 and conclusions
(1), (4), (5) were re-derived and stand as written (Lemma 1 is DS11 at
\(B=B^*\) plus the SSE reassignment step; Lemma 2 uses (L) to kill the
nuisance moments of \(\hat s\)-measurable partitions and (S)-uniqueness for
the attainment set; (5) is Proposition 4's tax squeezed by (1)). Three parts
required repair or completion:

1. **Proposition 5** claimed a "uniform-in-labelings Lipschitz bound in the
   tilt" with no derivation. Supplied: for any labeling,
   \(\mathrm{btw}(s_\psi-\beta s_\lambda;z)=A_z-2\beta B_z+\beta^2C_z\) with
   \(0\le C_z\le\sum_iws_{\lambda,i}^2\) and \(|B_z|\le\sqrt{A_zC_z}\)
   (between-values dominated by total second moments; per-cell
   Cauchy–Schwarz), so all between-values are equi-Lipschitz in \(\beta\) on
   a compact neighborhood of \(B^*\) with an SLLN-bounded constant; the max
   \(\hat v_K(\beta)\) inherits it, and \(\hat B^*_N\to B^*\) a.s. plus the
   uniform centering shift \(-\bar{\hat s}_N^2\to0\) finish the bracket.
   Pollard-1981-style value convergence at the fixed tilt needs no
   uniqueness; only the argmin-continuity use in (2)–(3) needs (S).
2. **Proposition 6** was a labeled proof sketch — the sole lower-bound
   mechanism — with two recorded failed predecessors. The audit closed it at
   \(d_\lambda=1\) with four ingredients now recorded in the chapter:
   boundary/mass consistency of the empirical DP from (S)-uniqueness
   (placing the swap slabs where (R) applies and keeping the two increment
   directions uniformly non-collinear); an availability count — mean
   \(\asymp N^{3/4}\) points per sign window in the width-\(2N^{-1/4}\)
   slabs, fluctuations \(O(\sqrt{N\log\log N})\) uniformly over the fixed VC
   class, tilt shifts \(O(\sqrt{\log\log N/N})\ll N^{-1/4}\) by the LIL;
   drift accounting (cumulative \(\tilde O(N^{-1/2})\) motion of \(x\),
   centroids, and midpoints is second-order); and the steering distance
   \(|y(z_0)-y^*|=O(\sqrt{\log\log N/N})\), giving the honest rate
   \(\tilde O(N^{-3/4})\) (the original \(O(N^{-3/4})\) holds in
   probability; almost-sure statements carry the \(\sqrt{\log\log N}\)).
   The target's existence needs \(x\ne0\) (automatic:
   \(\mathrm{btw}(z_0)=\hat v_K>0\)) and \(K\ge3\) — for
   \(d_\lambda\ge2\) the constraint-plane target requires
   \(K\ge d_\lambda+2\) *and* a vector form of (R); that branch is open.
3. **Conclusion (3)** cited "the fixed-slab Glivenko–Cantelli class of audit
   §8" — a misattribution: in `AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md` §8
   that step's population bound comes from DS14's (M4) slab margin and its
   scale from (M5)'s \(\gamma\), neither assumed by DS15. The correct and
   weaker statement, now in the chapter: a GC law over the *fixed* VC class
   of half-planes \(\{s:s_\psi-\beta s_\lambda\le c\}\) with \((\beta,c)\)
   in a compact neighborhood of \((B^*,\cdot)\), with the population side
   needing only (S)-atomlessness at the \(K-1\) fixed optimal boundaries
   (the empirical slope converges, so no uniform-over-normals margin is
   needed). Lemma 3's constants were also tidied: the mass lower bound
   \(\eta(\delta)\) converges to \(\min_bw^*_b\) along \(\delta\to0\), which
   is what conclusion (4)'s contradiction actually consumes.

Verdict: **verified with hardened assumptions** — \(d_\psi=d_\lambda=1\),
(L)+(S)+(R), \(K\ge3\), equal weights, exact centering, feasibility as
nonsingular binned nuisance block. The registered \(d_\lambda\)-generality is
refuted by the §7(b) boundary; \(d_\lambda\ge2\) with \(K\ge d_\lambda+2\)
and the vector-(R) steering is explicitly open (OP29).

## 9. Adversarial audit and boundary conditions

- **Ties/atoms:** (S) excludes atoms; on the atomic 1/8 grid the known
  31-fold global tie (`CE-DS-DEGENERATE-GLOBAL-TIE-001`) shows what breaks.
  On fine grids this audit found zero exact ties over 20 full lattices.
- **Duplicates:** measure-zero under (S); the finite algebra survives them
  (identities mode; pinned test).
- **Singletons:** permitted at finite \(N\); conclusion (2) makes them
  vanish asymptotically on-class. The only singleton in this audit's scans
  sits on the non-centered control — consistent, not probative.
- **Singular information:** full \(I\succ0\) is assumed; singular *binned*
  nuisance blocks are exactly the feasibility boundary, and the limit
  \(J^*\) lives on it — the theorem's content, not a gap. The pseudo-inverse
  extension is verified to coincide with \(\mathrm{btw}\) there.
- **Nuisance dimension:** \(K=d_\lambda+1\) is a hard boundary (fixture);
  \(K\ge d_\lambda+2,d_\lambda\ge2\) open.
- **Weights:** the theorem assumes i.i.d. equal weights; Proposition 4's
  algebra is weight-agnostic (verified with unequal weights) but nothing
  asymptotic is claimed off equal weights.
- **Hidden compactness:** Lemma 3(iv)'s centroid-escape argument and the
  empirical effective-cell truncation were re-derived; no unstated
  compactness remains.
- **First-order-to-finite:** not applicable — the claim is about exact
  global optima, and asserts nothing about exchange-stable non-global
  states (explicitly out of scope, OP29(c)).
- **Empirical-to-population:** the load-bearing jump; carried by
  Propositions 4–6 plus the corrected GC lemma, all now derived rather than
  imported.
- **Score estimation:** excluded (P2); the slope \(\hat B^*_N\) estimated
  from the *same* sample is internal to the theorem and handled by the
  Lipschitz/LIL absorptions.
- **New events:** prediction is by the compiled scalar interval rule on
  \(\hat s\); observation-to-score conversion stays explicit (library
  invariant).

## 10. Algorithmic consequence

The free in-bin \(D_s\) optimizer is asymptotically self-defeating on
conditionally centered laws: it spends its freedom shedding binned nuisance
information. An exact solver chasing the free optimum therefore converges to
labelings that no (M3)-margin certificate can ever pass — margin
certification and free optimization are *incompatible objectives*, not a
solver-quality issue. The float top-64 screen behind the researcher's trend
suite is validated at \(N\le16\) (rank-1, no guard casualties on 20/20
independent instances), but its \(10^{-9}\) nuisance guard discards exactly
the near-degenerate labelings the theorem predicts optima to become, so at
larger \(N\) a guard-aware exact re-ranking (or the compile path below)
should replace it.

## 11. Deployability consequence

Unchanged from DS15's deployability section, now on audited footing for
\(d_\psi=d_\lambda=1\): the compile target for profiled criteria is the
scalar efficient-score interval rule (full-sample \(\hat B^*_N\), exact DP
on \(\hat s\), 1-D mass/boundary certificates plus slope stability) — not a
DS14 (M3) certificate, which provably cannot hold at free global optima. A
margin-certified in-bin quantizer remains legitimate at the quantified price
\(\delta(\kappa)=v_K-v^*(\kappa)>0\). The binned model at the compile target
carries no nuisance information by design; nuisance estimation must stay
full-sample, and the report to users must say so.

## 12. Information-loss consequence

Conclusion (1) pins the asymptotic \(\eta_{D_s}\) numerator at free optima to
\(v_K\), the unrestricted supremum: free optima asymptotically waste nothing
relative to unbinned *profiled* inference beyond the quantization loss
\(\sigma_s^2-v_K=W_K\) itself. Conclusion (4) prices any (M3) certificate at
\(\delta(\kappa)>0\) of profiled information. The theorem supplies no finite-N
retention bound and no rates for \(\eta_{D_s}\); measured retention against
unbinned inference must still be reported per invariant 7.

## 13. Updated status

- `OPEN-DS-MARGINS-AT-OPTIMA`: remains `project_proved` on the hardened
  \(d_\lambda=1\) statement; gains `audit`, `boundary_counterexamples`,
  repaired `dependencies`, and a rewritten `warning` (audited; screen-caveat
  on the original \(N\ge14\) trend instances; \(d_\lambda\ge2\) open).
- `AUDIT-DS-MARGINS-AT-OPTIMA`: new node, `project_proved`.
- `CE-DS-MARGINS-RANK-VACUITY-001`: new exact boundary fixture, pinned in CI.
- `OPEN-DS-MARGINS-NONCENTERED` (OP29): scope extended with the
  \(d_\lambda\ge2\), \(K\ge d_\lambda+2\) vector-steering branch.
- `OPEN-DS-DOMINATION-EQUALITY`: circular dependency edge removed.

## 14. Registry patch

`claims/OPEN-DS-MARGINS-AT-OPTIMA.json` points here via `audit:`, hardens
`assumptions` (explicit \(d_\lambda=1\); \(K\ge3=d_\lambda+2\) noted as the
general cardinality condition), cites the boundary fixture, and repairs the
dependency edges (§4). `claims/AUDIT-DS-MARGINS-AT-OPTIMA.json` records this
audit. `claims/OPEN-DS-MARGINS-NONCENTERED.json` gains branch (d).
`KNOWN_RESULTS/05b-ds-bridge.md` DS15 carries the hardened statement, the
completed Propositions 5–6, the corrected GC lemma, and the audit-side
measured paragraph; `05a-ds-core.md` DS10 and 05b DS11(a) lose their stale
"OP28 open" text. Six N-DS-AUDIT15 rows enter `NUMERICAL_EVIDENCE.md` with
seeds, revision, and environment recorded in the committed artifacts.

## 15. Regression artifacts

- `py/audit_ds_margins_at_optima.py` — independent exact suite
  (identities / vacuity / exhaustive+screen / scalar), pure stdlib
  rationals, own seeds.
- `AUDITS/artifacts/AUDIT-DS-MARGINS-AT-OPTIMA-001/*.json` — committed run
  records (seeds, git revision, script sha256, environment, wall times).
- `COUNTEREXAMPLES/CE-DS-MARGINS-RANK-VACUITY-001.json` — minimized exact
  boundary fixture.
- `tests/test_research_claims.py::test_ds15_rank_deficiency_zeroes_every_feasible_profiled_value`
  and `::test_ds15_projection_tax_identity_survives_ties_duplicates_and_unequal_weights`
  — deterministic CI pins (< 2 s each); the researcher's sandwich pin is
  untouched.

## 16. Next dependency-blocking question

OP29's deployment-relevant half, sharpened by this audit: **do one-point
exchange-stable non-global \(D_s\) labelings — what the library's optimizer
actually returns — retain the DS14 margins on conditionally centered laws,
and at what information cost relative to \(v_K\)?** DS15 says free *global*
optima shed (M3); nothing yet says the solver's terminal states do. Behind
it, same node: the \(d_\lambda\ge2\), \(K\ge d_\lambda+2\) dichotomy via a
vector-(R) steering construction.
