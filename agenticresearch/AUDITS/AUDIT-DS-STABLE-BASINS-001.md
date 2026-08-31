# Publication-grade audit of DS17 stable basins

**Claims:** `DS-STABLE-BASINS-CENTERED-OBSTRUCTION`,
`DS-STABLE-BASINS-LCM-CLASSIFICATION`,
`DS-STABLE-BASINS-FIXED-POINT-GATE`, `DS-STABLE-BASINS-GATE-SCANS`, and
clause (c) of `DS-PROFILED-COMPILE-CERTIFICATE`  
**Audit:** `AUDIT-DS-STABLE-BASINS`  
**Date:** 31 August 2026  
**Source frozen:** branch `research-ds-stable-basins`, commit `ce8d59d`
(merged by PR #27 as `7e20983`)  
**Result:** all four DS17 nodes **hardened**. The conditional-centering
obstruction, LCM reduced-rule classification, and necessary fixed-point gate
survive. Their statements needed a singular-nuisance definition repair,
narrower LCM/deployment language, and a strict separation of theorem from
finite root-search evidence. The measured scan node remains `measured`; its
no-root and unique-root wording is replaced by windowed “found” language.

## 1. Target statement

At scalar interest and nuisance dimensions, DS17 asserted four linked results.

1. On an atomless conditionally centered law,
   \(E[S_\lambda\mid\hat s]=0\), every self-consistent strip rule collapses
   its binned nuisance information. Chaining this population obstruction
   through DS14 was claimed to show that, almost surely, every sufficiently
   large sample has no ordinary one-point exchange-stable labeling satisfying
   fixed mass, conditioning, and projected-centroid-separation margins.
2. Under linear conditional means (LCM), any full-rank stationary escape after
   dropping separation consists of coincident projected-centroid splits; its
   merged deployable rule is rank at most one. A Gaussian sign-split family
   was offered as a nonempty population example.
3. Off the centered class, inhabitation was reduced necessarily to a scalar
   equation \(E[h(T_\beta)S_\lambda]=0\) along Lloyd-stationary strip rules,
   with \(|\beta|\le2M/\kappa\).
4. Finite scans reported no admissible roots on centered examples and a cheap
   root on mix3, then fed clause (c) of the compile refusal and three open-
   problem reroutes.

The audit tests each node separately. It does not treat a numerical failure to
find a root as a proof, or a population root as a finite-sample certificate.

## 2. Criterion and problem level

- **Criterion:** scalar in-bin profiled \(D_s\), with
  \(\Phi(q)=I_{q,\psi\psi}-I_{q,\psi\lambda}^2/
  I_{q,\lambda\lambda}\) in the regular nuisance-block regime.
- **Levels:** population quantizers for the obstruction, LCM classification,
  and gate; empirical-to-population for eventual emptiness; finite assignment
  and population computation for the measured controls.
- **Decision variables:** population interval partitions of
  \(T_\beta=S_\psi-\beta S_\lambda\), DS12 bounded-packet stationary rules,
  and ordinary one-point exchange-stable empirical labelings. Stability only
  under a margin constraint is never substituted.
- **Oracle:** i.i.d. equal-weight exact scores. Estimated scores remain P2.
- **Centering boundary:** (L) is a conditional expectation under the
  population score law. It is not sample centering and does not authorize
  recentering score rows.

No public library API or file under `src/` is changed.

## 3. Status before attempt

At `ce8d59d`, the obstruction, LCM classification, and gate were
`project_proved`; the scans were `measured`. None had an audit pointer. Three
theorem nodes carried researcher-assigned `search_gap`; the scan node carried
`not_searched`.

The registered obstruction said every “tilt-consistent” rule has a singular
nuisance block although tilt consistency had just been defined by
\(B_q^*=\beta\), which requires the block to be positive. The gate said a
finite branch scan “decides” a law. The scan node implied the proved
obstruction, and the compile claim cited DS17 without depending on it.

## 4. Dependencies rechecked

The audited DS11--DS16 nodes were not re-proved, but their exact hypotheses
and the statements consumed here were checked.

1. **DS11 / `DS-PROFILED-VARIATIONAL`.** The scalar normal equation and
   profiled-value identity are valid. They justify \(B_q^*\) only when the
   nuisance block is positive (or with a separately declared generalized
   inverse); DS17 uses the ordinary regular form.
2. **DS12 / `OPEN-DS-POP-COMMON-METRIC`.** With full-rank information,
   positive masses, distinct projected centroids, and null tie hyperplanes,
   bounded-packet stationarity reproduces the rule by its own projected
   nearest-centroid correspondence. Coincident centroids require the audited
   merged construction and do not themselves compile fine labels.
3. **DS14 / `OPEN-DS-FINITE-POP-BRIDGE`.** Step 4, not bare DS12, identifies
   a parameter-limit rule from its own population moments. Its audit repaired
   the data-dependent-slab error with fixed VC/uniform-moment classes and made
   the compact parameter set explicit. Those events are independent of a
   later pathwise selection of labelings.
4. **DS16 / `DS-STABLE-MARGINS-PRICE`.** Its value funnel is not needed to
   prove DS17.2. Its distinction between \(v^{*+}(\kappa)\) and
   \(v^*(\kappa)\) is load-bearing when interpreting the sign-split family.
5. **Rank/Schur foundations.** The elementary diagonal bound
   \(\lambda_{\min}(I_q)\le I_{q,\lambda\lambda}\) supplies the final
   contradiction. The packet excludes re-auditing `DS-SCHUR`,
   `FI-QUANT-IDENTITY`, and `FI-RANK-CEILING`; their publication/bridge
   authority is flagged as a separate audit task.

One inherited structural weakness remains outside scope:
`DS-PROFILED-COMPILE-CERTIFICATE` directly depends on measured
`DS-STABLE-STATE-SELECTION`. This audit does not use that measured node as
theorem authority and records the edge for a separate compile-claim audit.

## 5. Nearest literature

The independent search is recorded in
`LITERATURE/audits/AUDIT-DS-STABLE-BASINS-31-August-2026.md`. The closest
sources have different feasible sets and do not prove the combined theorem.

- **Bickel--Klaassen--Ritov--Wellner:** efficient scores are residuals after
  nuisance-tangent projection. This is prior art for the orthogonality and
  normal-equation background, not for binned self-generated tilts or hard
  partitions.
- **Jakubowski (2021):** equality in Chebyshev's monotone covariance
  inequality gives the closest published equality mechanism. The conditional
  application and its conversion into measurable cells and zero binned
  nuisance moments remain part of the project proof.
- **Tarpey--Li--Flury (1995):** principal/self-consistent points of elliptical
  laws supply the closest eigenspace restriction. They optimize Euclidean
  squared error and do not contain profiled Fisher information or DS17's
  endogenous tilt.
- **Tarpey--Flury (1996):** supplies the general self-consistency/LCM
  framework, while credit for the term itself traces to Hastie--Stuetzle. It
  does not give the finite margin or compile consequence.
- **Tarpey--Loperfido (2015):** extends principal-subspace results beyond the
  simplest elliptical setting. It is a closer missed lead, but still lacks
  the Schur objective, root gate, and empirical exchange-stability bridge.

The efficient-score projection and Chebyshev inequality/equality ingredients
are therefore re-attributed to classical literature. No searched source proves
the combined conditionally centered strip obstruction or eventual empirical
emptiness. The obstruction and gate retain `search_gap`; the compound LCM node
is set to `prior_art_found` because its first structural conclusion directly
overlaps the published self-consistency-to-eigenspace theorem, while its
profiled rank/value conclusions remain project-level.

## 6. Counterexample search

The independent harness is `py/audit_ds_stable_basins.py`. It imports none of
the researcher's DS17 instrument. Exact paths rebuild cells, information, and
moves from raw arrays with `Fraction`; population paths use independently
derived conditional Gaussian-mixture moments and adaptive one-dimensional
quadrature.

**Exact identities and fixtures.** At \(\beta=1/2\), the eight-atom sign-split
fixture gives cell means
\((-11/4,-5/4,2)\), numerator \(-9/16\), nuisance block \(9/8\), and quotient
\(-1/2=B_q^*-\beta\). Its information is exactly
\(\operatorname{diag}(4,9/8)\), its projected centroids are
\((-2,-2,2)\), and its merged nuisance block is zero. The DS16 stable witness
again has 966 canonical partitions, 16 admissible moves, and maximum gain
\(-329181847579541084791/107530695533215013142528\).

**Minimization.** The eight-atom sign-split control is not globally
support-minimal. The exact \(N=K=3\) boundary
\([(-1,1),\;(-1,-1),\;(2,0)]\)
with equal weights has \(I_q=\operatorname{diag}(2,2/3)\), projected
centroids \((-1,-1,2)\), and a singular merged nuisance block. Since full rank
needs \(K\ge3\) and nonempty labels need \(N\ge K\), it is support-minimal.
It is atomic with singleton cells, so bounded-packet stationarity is vacuous;
it delimits the assumptions and does not refute DS17.

**Quadrature.** For the bimodal control at \(\beta=0.7\), cuts
\((-0.9,0.8)\), adaptive quadrature and the independent conditional-mixture
formula agree below \(10^{-12}\); public `IntegrationSource` at order 120 and
truncation 12 agrees below \(10^{-13}\). This is independent of the original
strip-moment evaluator.

**Root search.** The audit searches the simultaneous two Lloyd equations and
the undivided numerator equation over the full \(|\beta|\le2M/\kappa\) window
at declared \((\kappa,c_0,\gamma)=(1,0.05,0.1)\), using grid refinement and
Sobol multistarts. Across 13 laws and 6,578 starts it finds no gate-admissible
root on any (L) law and one on mix3. It also finds singular numerator roots on
every centered control. These are expected: at \(I_{q,\lambda\lambda}=0\),
the numerator can vanish although the quotient and regular tilt consistency
are undefined. This directly forces the terminology repair.

The mix3 root is
\((\beta,c_1,c_2)\approx(0,-1.00476341197,1.00476341197)\), with
\(\lambda_{\min}\approx1.73639480105\). Its audited compact bound is
\(2M/\kappa=31/3\), so the researcher's \([-2.5,2.5]\) scan was sufficient to
see the near-zero root but not justified as a complete gate window.

No theorem counterexample was found. Numerical absence and apparent
uniqueness remain measured, not interval-certified facts.

## 7. Algebraic reduction

For cell means \(\mu_b=(\mu_{\psi b},\mu_{\lambda b})\), define
\(t_b=\mu_{\psi b}-\beta\mu_{\lambda b}\). Direct expansion gives
\[
\sum_bW_bt_b\mu_{\lambda b}
=I_{q,\psi\lambda}-\beta I_{q,\lambda\lambda}.
\]
For a strip rule, \(h(T_\beta)=t_b\) on cell \(b\), so the left side is
\(E[h(T_\beta)S_\lambda]\). This undivided identity is universal. Only when
\(I_{q,\lambda\lambda}>0\) may it be divided to obtain
\[
B_q^*-\beta
=\frac{E[h(T_\beta)S_\lambda]}{I_{q,\lambda\lambda}}.
\]

The audit therefore uses two terms:

- **root consistency:** \(E[h(T_\beta)S_\lambda]=0\), meaningful even at a
  singular nuisance block;
- **regular tilt consistency:** \(B_q^*=\beta\), defined only when the block
  is positive and then equivalent to root consistency.

At a regular self-consistent pair, projected cell centroids equal the
\(T_\beta\)-cell means, so the remaining fixed-point equations are precisely
the Lloyd midpoint equations plus root consistency.

## 8. Proof / conditional result

Let \(\delta=\beta-B^*_{\rm full}\), so
\(T_\beta=\hat s-\delta S_\lambda\), and suppose (L).

For \(\delta>0\), conditional on \(\hat s\), the function
\(x\mapsto h(\hat s-\delta x)\) is non-increasing. A regular conditional law
exists because the variables are real-valued on standard Borel spaces. On a
product extension take conditionally i.i.d. (X,X'). The finite-valued step
function \(h\) is bounded and \(S_\lambda\in L^2\), so the covariance product
is integrable, and
\[
2\operatorname{Cov}(h(\hat s-\delta X),X\mid\hat s)
=E[(h(\hat s-\delta X)-h(\hat s-\delta X'))(X-X')\mid\hat s]\le0.
\]
Conditional centering kills the product of conditional means. Root
consistency makes the integrated inequality an equality. The integrand has a
fixed sign, so it is zero almost surely. Thus \(h(T_\beta)\) is conditionally
constant; conditional degeneracy of \(S_\lambda\) gives the same conclusion
trivially. Atomlessness and positive interval masses make the distinct-cell
values of (h) strictly ordered, hence every cell indicator is
\(\hat s\)-measurable. Conditional centering then makes every nuisance cell
moment zero. The argument reverses signs for \(\delta<0\), and for
\(\delta=0\) the cells are already \(\hat s\)-measurable. Therefore every
root-consistent strip rule has \(I_{q,\lambda\lambda}=0\); no regular
tilt-consistent strip rule exists.

For DS17.2, fix \(K\). Intersect the audited DS14 fixed-class strong-law events
over rational \((\kappa,c_0,\gamma)\) and integer compact radii. On this one
event, assume margin-compatible ordinary-stable labelings exist for infinitely
many (N), choose one pathwise at each such (N), and apply compactness.
DS14 Step 4 identifies a full-rank, distinct-centroid, self-consistent limit.
In scalar POI dimension the positive Schur metric cancels from nearest-cell
comparisons, so the limit is a regular tilt-consistent strip rule. The
population obstruction gives
\(I_{q,\lambda\lambda}=0\), contradicting
\(\kappa\le\lambda_{\min}(I_q)\le I_{q,\lambda\lambda}\). Thus only finitely
many \(N\) can admit any such labeling. Shrinking positive real margins to
positive rationals covers arbitrary fixed margins. No pointwise SLLN is
evaluated at a data-dependent limit.

For centered nonsingular LCM laws,
\(E[S\mid T_\beta]\) is linear and strip-cell means are collinear, so every
reduced strip information matrix is rank at most one. The Gaussian sign-split
family independently establishes nonemptiness of the closed population class
for \(\kappa\le1/\pi\), but supplies no empirical sequence or constrained-
value attainment theorem.

## 9. Adversarial audit

- **Strictness and ties:** population interval means are distinct only under
  atomlessness and positive masses. Fine sign-split cells deliberately tie;
  they are handled by merging, not by arbitrary deterministic tie breaking.
- **Singleton/empty cells:** population masses are positive and DS14 (M2)
  excludes vanishing cells in the limit. The minimized atomic witness shows
  exactly why singleton packet stationarity proves nothing.
- **Duplicate scores:** permitted in finite samples; fixed-class uniform laws
  and the pathwise selection argument do not assume distinct rows.
- **Singular information:** full-rank information is needed for DS12/DS14 and
  for regular (B_q^*). The numerator identity is recorded separately at
  singularity; no (0/0) quotient is used.
- **Nuisance singularity:** it is the population conclusion, not an input to
  the regular contradiction. PSD forces the cross block to zero with it.
- **Atomic laws:** excluded from the theorem and isolated by the minimized
  fixture. Exact atomic calculations validate algebra only.
- **Hidden compactness:** the only compactness is DS14's audited explicit
  parameter class. The beta bound follows from
  \(|I_{\psi\lambda}^q|\le\operatorname{tr}(I_q)\le2M\) and
  \(I_{\lambda\lambda}^q\ge\lambda_{\min}(I_q)\ge\kappa\).
- **First-order-to-finite jumps:** the population statement is stationary;
  the finite statement imports DS14's exact exchange bound and does not infer
  finite stability directly from a root.
- **Empirical-to-population jumps:** one common fixed-class event covers every
  pathwise selection and rational margin triple. The converse root-to-
  empirical direction remains open.
- **Score-estimation error:** excluded; all theorems and computations use
  exact scores.
- **New-event extension:** distinct-centroid stationary limits define strip
  rules for new scores; coincident fine labels do not. On (L), the certified
  distinct branch is empty rather than deployable.

The equality argument also handles conditionally degenerate nuisance laws:
conditional constancy is then immediate. Pairwise duplicate (t_b) values are
not allowed in the strict strip theorem; they belong to the merged branch.

## 10. Algorithmic consequence

On the audited (L) class, an unconstrained exchange solver cannot eventually
terminate at an ordinary-stable state carrying fixed (M2)+(M3)+(M5). A
margin-constrained solver may terminate, but its state is stable only under
the constraint and must report the finite upper-bound gap.

Off (L), the root equation can screen population candidates, but a solver must
enumerate all Lloyd-stationary branches within the \(\kappa\)-dependent compact
tilt range. A found root is not a convergence or stability certificate. Dense
multistart searches are diagnostics, not proof of completeness.

## 11. Deployability consequence

The compile refusal survives only on the explicitly stated scalar,
population-conditionally-centered class. There the full-triple DS14 companion
branch is asymptotically empty, while the LCM merged reduction loses its
nuisance/full-rank margin. A finite diagnostic remains useful for inspection
but does not establish a population guarantee.

Nothing here licenses refusing compilation for general template mixtures,
HEP fits, or cytometry laws: membership in (L) must be proved for the actual
score law. The mix3 root is per-law measured evidence and does not establish
that certification is generally free. No `src/` change is authorized.

## 12. Information-loss consequence

The empty certified branch has no retained-information guarantee because it
has no asymptotic inhabitants. For the explicit Gaussian sign-split family,
the scalar profiled information is \(2/\pi\) against full efficient-score
variance one, i.e. retention \(2/\pi\approx0.63662\); its measured loss to the
three-bin scalar optimum is about (0.173206). This number belongs to that
family, not every stationary merged configuration.

For mix3, the audited population root has measured value equal to the
efficient interval optimum within numerical tolerance and
\(\lambda_{\min}\approx1.7364\). This is not a held-out, finite-sample, or
estimated-score guarantee.

## 13. Updated status

- `DS-STABLE-BASINS-CENTERED-OBSTRUCTION`: **hardened**;
  `project_proved` retained. The core obstruction and eventual-emptiness
  quantifiers are verified after separating root from regular consistency.
- `DS-STABLE-BASINS-LCM-CLASSIFICATION`: **hardened**;
  `project_proved` retained. Rank collapse is LCM-scoped, sign-split
  nonemptiness concerns the closed population class only, and the numerical
  (v_3-v_2) value is not universal.
- `DS-STABLE-BASINS-FIXED-POINT-GATE`: **hardened**;
  `project_proved` retained. It is necessity only, with a margin-dependent
  compact range and no numerical decision claim.
- `DS-STABLE-BASINS-GATE-SCANS`: **hardened**; `measured` retained. The
  independent results reproduce the qualitative boundary but replace “zero
  roots” by “zero gate-admissible roots found” and “unique” by “one found.”

Clause (c) of `DS-PROFILED-COMPILE-CERTIFICATE` is hardened consistently. No
target is refuted or reduced to an unresolved proof assumption.

## 14. Registry patch under `claims/`

The four DS17 nodes gain this audit pointer and fully explicit assumptions.
The patches:

- distinguish numerator/root consistency from regular \(B_q^*=\beta\);
- state fixed (K), exact scores, equal weights, population (L), and the
  precise use of (M4);
- restrict LCM rank collapse and Gaussian sign-split claims;
- remove the measured scan's implication into the proved obstruction;
- add the DS17 theorem dependencies to the compile claim and rerouted open
  nodes without making measured evidence theorem authority;
- record the minimized atomic boundary and audit-owned literature status;
- make every programme entry's status visible in the generated index.

The new node `AUDIT-DS-STABLE-BASINS` points to this report and the independent
harness. Generated indexes are rebuilt only through `registry.py reindex`.

## 15. Counterexample/regression artifact

No theorem counterexample was found. The new exact boundary fixture
`CE-DS-LCM-SIGNSPLIT-MINIMAL-001` is support-minimal and CI-pinned by
`test_ds17_minimal_atomic_signsplit_is_only_a_boundary_witness`. Its metadata
explicitly says it falsifies no DS17 claim because atomlessness, (M4), and
non-vacuous packet transfers fail.

The existing eight-atom fixture remains pinned as the structured symmetric
sign-split construction. The audit reports honestly that this test confirms
the boundary mechanism, not the population theorem; the proof above carries
the theorem authority.

Four provenance-complete run records live under
`AUDITS/artifacts/AUDIT-DS-STABLE-BASINS-001/`, and the evidence ledger adds
`N-DS-AUDIT17-EXACT`, `N-DS-AUDIT17-QUADRATURE`,
`N-DS-AUDIT17-ROOTS`, and `N-DS-AUDIT17-LIBRARY`.

## 16. Next dependency-blocking question

**OP29(a) / `OPEN-DS-MARGINS-NONCENTERED`:** on a stated non-centered law
class, does the necessary `DS-STABLE-BASINS-FIXED-POINT-GATE` admit a
nondegenerate root with a strict population basin, and can that basin be
transferred to ordinary empirical one-point exchange stability despite
(O(1/N))-scale boundary-noise move gains?

Separately, future audits must address the direct measured dependency in
`DS-PROFILED-COMPILE-CERTIFICATE` and the foundational `DS-SCHUR`,
`FI-QUANT-IDENTITY`, and `FI-RANK-CEILING` nodes. They are not prerequisites
for closing this scoped audit.
