# Publication-grade audit of the exact off-(L) global basin and empirical transfer

**Claim:** `DS-NONCENTERED-GLOBAL-BASIN-TRANSFER` (DS18)
**Audit:** `AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`
**Date:** 31 August 2026
**Source frozen:** `research-open-ds-margins-noncentered` at `b1855c1`, handoff `7864348`
**Result:** theorem verified, with hardened assumptions, a self-contained
replacement for two off-hypothesis lemma imports, a quantitative finite-\(N\)
form of the transfer, one new exact boundary counterexample fixing the
feasibility convention, and two prior-art attribution repairs

---

## 1. Target statement

Let \(X,Z\stackrel{\mathrm{iid}}\sim\operatorname{Unif}[-1,1]\) and

\[
S=(S_\psi,S_\lambda),\qquad S_\psi=X,\qquad S_\lambda=3X^2-1+Z,\qquad K=3 .
\]

The frozen compound claim is:

**(T1) Population.** Among measurable three-cell quantizers of \(S\), the
\(X\)-interval rule \(q^*\) with cuts \(\pm1/3\) is the unique global
maximizer of the in-bin profiled objective
\(\Phi_{D_s}(q)=S_\psi(I_q)\), up to cell relabeling, with

\[
I_{\rm full}=\operatorname{diag}(1/3,\,17/15),\qquad
I_{q^*}=\operatorname{diag}(8/27,\,32/81),\qquad
\beta=0,\qquad
\eta_{D_s}=8/9 .
\]

**(T2) Strict isolation.** For every \(\varepsilon>0\) there is
\(\delta(\varepsilon)>0\) such that
\(\min_\pi\sum_bP(A_b\,\triangle\,A^*_{\pi(b)})\ge\varepsilon\) implies
\(\Phi_{D_s}(q)\le8/27-\delta(\varepsilon)\).

**(T3) Empirical transfer.** For i.i.d. equal-weight samples with exact,
**uncentered** scores: on one probability-one event, **every** sequence
\(z^{(N)}\) of exact global maximizers over finite labelings with three
nonempty cells and \(\hat I^z_{\lambda\lambda}>0\) satisfies, after
relabeling, \(P_N(z^{(N)}\ne q^*)\to0\), \(\hat I_N(z^{(N)})\to I_{q^*}\),
and \(\hat\Phi_{D_s}(z^{(N)})\to8/27\).

**(T4) Finite stability and margins.** Those \(z^{(N)}\) are exact ordinary
one-point exchange-stable and eventually satisfy (M2)+(M3)+(M5) at the fixed
rational constants \((c_0,\kappa,\gamma)=(1/4,1/4,1/2)\).

The node explicitly does **not** claim finite stability of the raw
population-cut labels, nor basin selection by local exchange ascent.

## 2. Criterion and problem level

- Criterion: in-bin profiled \(D_s\), the Schur complement
  \(S_\psi(I)=I_{\psi\psi}-I_{\psi\lambda}I_{\lambda\lambda}^{-1}I_{\lambda\psi}\)
  at \(d_\psi=d_\lambda=1\), so a scalar. **Convention check:** DS18 reports and
  compares the Schur *value*, never \(\log\det\) of it. Since \(s=1\) and every
  compared value is positive on the regular class, \(v\mapsto\log v\) is
  strictly increasing, so "global optimizer" is the same set under either
  convention and the argmax statements transfer verbatim. The audit confirmed
  no place where the two are mixed inside one inequality.
- Levels: `population_quantizer` for (T1)–(T2); `empirical_to_population` for
  (T3); `finite_assignment` for (T4). The node's registered level
  `empirical_to_population` is the coarsest of the three and is correct for the
  compound statement.
- Decision variable: a hard partition of \(\mathbb R^2\) score space (population)
  and a labeling of the sample (finite). Cells are **not** assumed to be
  \(X\)-measurable anywhere.
- Score oracle: exact scores. Estimated scores are outside the claim.

## 3. Status before the audit

`DS-NONCENTERED-GLOBAL-BASIN-TRANSFER` was `project_proved`,
`publication_status: internal`, `literature_search_status: search_gap`, with a
`warning` stating it was unaudited and authorised no `src/` compile surface.
Three downstream nodes already carried DS18 clauses:
`OPEN-DS-MARGINS-NONCENTERED` (OP29), `DS-PROFILED-COMPILE-CERTIFICATE`, and
`OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`. No audit node existed.

## 4. Dependencies rechecked

Every node returned by `registry.py show DS-NONCENTERED-GLOBAL-BASIN-TRANSFER
--deps` was re-read against what DS18 actually uses. Previously audited
`project_proved` nodes were not re-proved; they were checked for *hypothesis
match*, which is where the two defects are.

| Dependency | Status | What DS18 uses | Verdict |
|---|---|---|---|
| `DS-PROFILED-VARIATIONAL` (DS11) | `project_proved`, audited | the variational form at \(B=0\), and the pseudo-inverse extension at a singular nuisance block | **sound.** DS11's statistical reading needs \(E[S]=0\), which holds for the *population* law. At \(d_\lambda=1\) the population inequality DS18 needs is the one-line \(\Phi\le I_{\psi\psi}\); DS11 is only required for the singular extension. The audit re-derived both. |
| `DS-EFFICIENT-SCORE-GLOBAL-UPPER` | `project_proved` | the projected-\(D_s\) upper certificate | **not load-bearing.** DS18 proves its own scalar upper bound; the audit re-derived it without this node. Retained as context, not as a premise. |
| `OPEN-DS-MARGINS-AT-OPTIMA` (DS15) | `project_proved` for class (L), audited 30 Aug | Lemma 1 (scalar reduction), **Lemma 3 (rigidity)**, **Proposition 5 (scalar consistency)** | **hypothesis mismatch — repaired here.** See below. |
| `DS-STABLE-BASINS-FIXED-POINT-GATE` (DS17.4) | `project_proved`, audited 31 Aug | the root equation \(E[h(T_\beta)S_\lambda]=0\) and the margin triple | **sound, and used in the right direction.** DS17.4 is a *necessary* population test. DS18 exhibits an admissible root and then proves inhabitation directly; it never treats the gate as sufficient. Confirmed exactly: the residual is \(0\), \(B^*(I_{q^*})=0=\beta\), and the block \(32/81>0\) makes the root regular rather than a singular-numerator root. |
| `DS-SCHUR`, `FI-QUANT-IDENTITY`, `FI-RANK-CEILING` | foundational | \(I_q=\sum_bW_b\mu_b\mu_b^\top\), the Schur definition, \(\operatorname{rank}I_q\le K-1\) | inherited, not re-audited (recorded as a separate future task, per the packet's independence contract). |

**The DS15 hypothesis mismatch.** DS15 is registered *for conditionally
centered laws* — class (L), \(E[S_\lambda\mid\hat s]=0\) — and its chapter
carries the standing convention "*all second moments are uncentered about the
origin (empirical scores exactly centered, as everywhere in this chapter)*".
DS18's law is **off (L) by construction** (\(E[S_\lambda\mid X]=3X^2-1\)) and
DS18.2 runs explicitly **without sample centering**. So DS18 cites two DS15
results outside their registered hypothesis set:

- **Lemma 3 (rigidity)** is stated "*under (L)+(S)*". Reading its proof, (L)
  enters only in the *consequence* clause \(|m_{\lambda,b}|\le\|S_\lambda\|_2\sqrt\varepsilon\)
  (which uses \(E[S_\lambda1_{J^*_b}]=0\)); the partition-convergence core uses
  only (S) and boundedness. DS18 consumes only the core. **The content
  survives; the citation does not.**
- **Proposition 5 (bracket limits)** is proved for \(\hat v_K\) built from the
  *estimated* tilt \(\hat B^*_N\) and includes a term absorbing the exact
  empirical centering shift \(-\bar{\hat s}_N^2\). DS18 has no estimated tilt
  (\(\beta=0\) is fixed) and no centering, so neither the Lipschitz-in-\(\beta\)
  argument nor the shift term applies — the statement DS18 needs is the simpler
  unshifted one. **The content survives; the citation does not.**

**Hardening H1 (applied).** §7–§8 below replace both citations with
self-contained lemmas proved for this law from scratch. DS18 no longer depends
on any (L)-conditioned result. This is a repair to DS18's *proof text*, not a
downgrade of DS15: DS15 itself is untouched and its scope is correct.

## 5. Nearest literature

Full six-field triangulation and the nine search rounds are in
`LITERATURE/audits/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-31-August-2026.md`.
The audit ran an independent query path and only afterwards compared with the
research session's round 6.

- **Kieffer (1983)** — uniqueness of the locally optimal scalar quantizer for
  a **log-concave** density. Covers \(\operatorname{Unif}[-1,1]\) and is the
  correct antecedent for DS18's scalar uniqueness.
- **Mease & Nair (2006)** — a second uniqueness route under log-concavity of
  the density, with the standing warning that Eubank-type weakenings are
  known-broken.
- **Pollard (1981)** — strong consistency of empirical optimal quantizers, on a
  **selection-independent** almost-sure event. This is precisely the structure
  that carries DS18's "*every* sequence of global optimizers" quantifier.
- **Rakhlin & Caponnetto (2006)** — almost-minimizer rigidity for bounded
  sources: the published template for (T2) and for the empirical rigidity in
  (T3), stated in codebook space rather than in decision distance.
- **Telgarsky & Vattani (2010)** — Hartigan one-point relocation: terminals
  need not be Voronoi. Explains why DS18 must derive stability from *global*
  finite optimality, and is the mechanism behind the \(N=4\) boundary fixture.
- **de Castro & Dorigo (2019), INFERNO** — closest *applied* statement of the
  objective (an Asimov inverse Hessian, i.e. a profiled-Fisher surrogate) but
  over soft differentiable histograms and with no optimality theorem. Newly
  key-registered by this audit.

**Two attribution defects found and repaired.**

1. **Under-attribution.** Six direct antecedents were already in this project's
   own bibliography and unlinked to DS18: `Kieffer-1983`, `Mease-Nair-2006`,
   `Pollard-1981`, `Rakhlin-Caponnetto-2006`, `Fisher-1958` (one-dimensional
   contiguity, which the scalar upper problem uses), `Graf-Luschgy-2000`.
2. **Mis-scoped uniqueness citation.** The node cites `Liu-Pages-2020` for the
   scalar uniqueness/conditioning it needs, but that route's conditioning
   statement (Prop 11: positive-definite distortion Hessian) assumes
   **strictly** log-concave densities, as does Fleischer (1964)'s uniqueness.
   \(\operatorname{Unif}[-1,1]\) is log-concave but **not strictly** so.
   Kieffer and Mease–Nair do cover it; for the conditioning fact the audit
   supplies the missing statement itself — the exact distortion Hessian at
   \((-2/3,0,2/3)\) is

   \[
   H=\begin{pmatrix}1/2&-1/6&0\\-1/6&1/3&-1/6\\0&-1/6&1/2\end{pmatrix},
   \qquad \lambda_{\min}(H)=\tfrac16>0,
   \]

   with \(\det(H-\tfrac16 I)=0\) and \(H-\tfrac16 I\succeq0\) verified in exact
   rational arithmetic.

The **combined** statement — non-centered score law, Schur-complement objective
over hard partitions, unique strict attainer with quantitative isolation,
almost-sure transfer of *every* global optimizer sequence, exact finite
one-point stability — was not located. Recorded as `search_gap`, never novelty.

## 6. Counterexample search

Instrument: `py/audit_ds_noncentered_global_basin_transfer.py`, pure standard
library, written from the law definition, importing neither the library nor
`py/ds_noncentered_global_basin.py`. Artifacts with full provenance (git
revision, script SHA-256 `acdba34c…`, interpreter, platform, exact counts,
seed formula \(\mathrm{seed}(n,\mathrm{rep})=20260831+1000n+\mathrm{rep}\)) are
under `AUDITS/artifacts/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001/`.

**Exhaustive sweep (`search.json`).** 39 tables, **65,924** canonical
partitions enumerated exactly, split as: midpoint grid \(N=3\ldots10\) —
**13,744** partitions (independently reproducing the count the research row
declares); product grid \(N=6,8,10\) — **10,386** (likewise reproduced);
seeded LCG samples \(N=4\ldots10\), three reps — 41,229; seven adversarial
tables — 565. On every partition the audit checked
\(\hat\Phi_{D_s}\le\mathrm{btw}\le\hat v_3\), the agreement of the Schur value
with an independently minimised variational form, and label-permutation
invariance.

- **0** sandwich violations.
- **0** disagreements between the Schur and variational routes.
- **0** disagreements between the contiguous dynamic program for \(\hat v_3\)
  and brute force over all canonical partitions (all tables with \(N\le8\)).
- **1** exactly singular labeling found, on the hand-built
  `singular_nuisance_pairs` table — and its pseudo-inverse value \(19/48\)
  strictly exceeds the best regular value \(17/48\). This is the seed of the
  new boundary fixture (§15).

**Adversarial classes exercised:** unequal positive weights; a zero-weight row;
duplicate score atoms; exact ties at \(X=\pm1/3\); an exactly singular binned
nuisance block; singleton and tiny cells; near-singular information; and — by
construction, since canonical partitions of the sample are arbitrary — cells
that depend on \(Z\) and are not \(X\)-measurable.

**Boundary fixture reproduced (`exact.json`).** The registered
`CE-DS-NONCENTERED-POPULATION-CUT-UNSTABLE-001` was rebuilt from its
construction data \(X=(-3/4,-1/4,1/4,3/4)\), \(Z=(-1,-3/4,1,1)\) through the
law, **not** copied from the fixture's `scores` field. Every stored quantity
reproduces: the score rows, \(I\) before and after, \(363/2656\), \(49/352\),
the exact gain \(37/14608\), the four admissible moves, and the fact that the
post-move labeling is the exact global optimum and is itself exchange-stable
(best move \(-37/14608<0\)). Support-minimality confirmed independently:
\(N=3\) has one canonical partition and **zero** admissible relocations, so no
\(N<4\) instance of the phenomenon exists at \(K=3\).

**Boundary minimality search (`boundary.json`).** Over the 40 support points
\(\{-1,-\tfrac12,0,\tfrac12,1\}\times\{-1,-\tfrac34,-\tfrac12,0,\tfrac14,\tfrac12,\tfrac34,1\}\),
all **91,390** four-row tables were enumerated exactly: 84 host a singular
labeling, and in **42** of them *every* global regular optimum has an
admissible one-point relocation into a singular state with strictly positive
pseudo-inverse gain; 14 of those are exactly centered.

**Transfer probe (`transfer.json`).** Exact global optimisation over all
canonical partitions for \(N=4\ldots11\), three seeded reps each: **24**
optimisations, **126,732** partitions evaluated, 316 admissible moves checked
at the optima. All 24 global optima are exact one-point exchange-stable;
**zero** singular labelings occurred in any sampled table. The finite-\(N\)
certificate \(\Delta_N\) (§7) at \(N=64,256,1024,4096\), three reps each,
falls from \(\sim2.6\times10^{-2}\) to \(\sim3\times10^{-5}\) while
\(|\hat B_z|\) falls from \(0.20\) to \(0.03\)–\(0.05\); the margin triple
holds 0/3 times at \(N=64\), 1/3 at \(N=256\) (separation is the binding one),
and 3/3 at both \(N=1024\) and \(N=4096\).

No counterexample to (T1)–(T4) was found.

## 7. Algebraic reduction

Throughout, \(P_N\) is the empirical measure of the equal-weight sample,
\(\hat W_b,\hat\mu_b,\hat I_N\) are the labeling's own binned quantities, and
**all second moments are about the origin** — the sample is never centered, so
\(\hat I_N=\sum_b\hat W_b\hat\mu_b\hat\mu_b^\top\) is a raw second-moment
matrix, not a covariance. This is load-bearing and is stated explicitly
because DS15's chapter convention assumes the opposite.

**Reduction 0 (the exact law).** In pre-shear coordinates \((X,Z)\) the joint
density is \(1/4\) on \([-1,1]^2\) and the map \((x,z)\mapsto(x,3x^2-1+z)\) has
unit Jacobian. Every population quantity below is therefore an exact
polynomial integral over the square; the audit computes them that way and
never inverts the shear. Independently, the shear image is the strip
\(\{|x|\le1,\ |y-(3x^2-1)|\le1\}\subset[-1,1]\times[-2,3]\) of area \(4\).

\[
E[S_\psi^2]=\tfrac13,\quad E[S_\psi S_\lambda]=0,\quad E[S_\lambda^2]=\tfrac{17}{15},
\quad B^*=0,\quad \hat s=X,\quad E[S_\lambda\mid X]=3X^2-1 .
\]

The last identity was verified by orthogonality: \(E[(S_\lambda-(3X^2-1))X^k]=0\)
for \(k=0,\dots,5\). Since \(3X^2-1\ne0\) off a null set, the law is strictly
outside (L).

**Reduction 1 (profiled \(\le\) uncentered scalar between-value).** For any
measurable three-cell \(q\) with positive masses,

\[
\Phi_{D_s}(q)=I_{\psi\psi}(q)-\frac{I_{\psi\lambda}(q)^2}{I_{\lambda\lambda}(q)}
\;\le\;I_{\psi\psi}(q)=\sum_bW_b\,E[X\mid q=b]^2 .
\tag{R1}
\]

At \(d_\lambda=1\) this needs no variational machinery. If
\(I_{\lambda\lambda}(q)=0\), then \(I_{\psi\lambda}(q)=0\) too (Cauchy–Schwarz)
and the DS11 pseudo-inverse extension gives \(S_\psi^+(I_q)=I_{\psi\psi}(q)\),
so **(R1) holds with the pseudo-inverse convention as well**. The same algebra
holds verbatim for the sample.

**Reduction 2 (nearest-codepoint bound; arbitrary cells).** Put
\(m_b=E[X\mid q=b]\). Then

\[
\sum_bW_bm_b^2=E[X^2]-E\bigl[(X-m_{q(S)})^2\bigr]
\;\le\;E[X^2]-E\bigl[\min_b(X-m_b)^2\bigr]
\;\le\;E[X^2]-D_3 ,
\tag{R2}
\]

where \(D_3=\inf_{c\in\mathbb R^3}E[\min_b(X-c_b)^2]\). **This is where the
"arbitrary cells depending on \(Z\)" attack is answered:** the only fact used
is the pointwise inequality \((X-m_{q(S)})^2\ge\min_b(X-m_b)^2\), which holds
for *any* measurable partition of \(\mathbb R^2\), interval or not,
\(X\)-measurable or not. No contiguity, no interval structure, no assumption on
how cells depend on \(Z\).

**Reduction 3 (the scalar upper problem, exactly).** For a codebook
\(c_1<c_2<c_3\) the nearest-point cells are the intervals cut at the
midpoints. With density \(1/2\), an interval of length \(\ell\) contributes at
least \(\ell^3/24\), with equality iff its codepoint is its midpoint. Since
\(\ell_1+\ell_2+\ell_3=2\) and \(\ell\mapsto\ell^3\) is strictly convex,

\[
D_3=\min_{\sum\ell_b=2}\sum_b\frac{\ell_b^3}{24}=\frac1{27},
\qquad\text{uniquely at }\ell_b=\tfrac23,\ c^*=(-\tfrac23,0,\tfrac23).
\tag{R3}
\]

Hence \(v_3:=E[X^2]-D_3=\tfrac13-\tfrac1{27}=\tfrac8{27}\), and
\(v_2=\tfrac13-\tfrac1{12}=\tfrac14<v_3\), so a quantizer with an empty cell
cannot attain \(v_3\). An exact lattice scan of all **35,990** sorted
codebooks on the \(1/30\)-lattice found none below \(1/27\) and a best rival
\(67/1800\); the local face is the exact Hessian with
\(\lambda_{\min}=1/6\) (§5).

**Reduction 4 (the computable finite-\(N\) certificate).** For a sample, let
\(\hat D_{3,N}=\min_{c}P_N\min_b(X-c_b)^2\) and
\(\hat v_{3,N}=P_N[X^2]-\hat D_{3,N}\). Let \(z^*_N\) be the fixed
population-cut labeling and

\[
\boxed{\;\Delta_N:=\hat v_{3,N}-\hat\Phi_{D_s}(z^*_N)\;\ge\;0\;}
\]

Then for **every** labeling \(z\) with \(\hat\Phi_{D_s}(z)\ge\hat\Phi_{D_s}(z^*_N)\)
— in particular every global optimum, once \(z^*_N\) is feasible — writing
\(\hat m\) for \(z\)'s own \(X\)-centroids:

\[
\underbrace{P_N\bigl[(X-\hat m_{z})^2\bigr]-P_N\bigl[\min_b(X-\hat m_b)^2\bigr]}_{\text{own-codebook excess}}\le\Delta_N,
\qquad
P_N\bigl[\min_b(X-\hat m_b)^2\bigr]-\hat D_{3,N}\le\Delta_N .
\tag{R4}
\]

Both follow from (R1)–(R2) applied to the sample:
\(P_N[(X-\hat m_z)^2]=P_N[X^2]-\mathrm{btw}_N(z)\le P_N[X^2]-\hat\Phi(z)
\le P_N[X^2]-\hat\Phi(z^*_N)=\hat D_{3,N}+\Delta_N\).
\(\Delta_N\) is computable from the sample alone, with **no combinatorial
search over labelings** — this is the audit's quantitative contribution and
what makes (T3) checkable at \(N=4096\).

**Reduction 5 (regularity is a.s. vacuous).** At \(d_\lambda=1\),
\(\hat I^z_{\lambda\lambda}=\sum_b\hat W_b\hat\mu_{\lambda,b}^2=0\) iff every
cell \(\lambda\)-sum vanishes, which forces \(\sum_iS_{\lambda,i}=0\). Under
the named law \(\sum_iS_{\lambda,i}\) has an absolutely continuous
distribution (condition on the \(X_i\); \(\sum_iZ_i\) is independent and
atomless), so \(P(\sum_iS_{\lambda,i}=0)=0\) for each \(N\), and the countable
union over \(N\) is still null. **Almost surely every labeling with three
nonempty cells is regular**, so DS18's restriction to regular labelings is
a.s. no restriction at all, and the ordinary one-point comparison domain
contains no singular destination.

## 8. Proof

### 8.1 (T1): unique population attainer

\(q^*\) attains \(8/27\): direct integration gives \(W_b=1/3\),
\(\mu_{\psi}=(-\tfrac23,0,\tfrac23)\), \(\mu_\lambda=(\tfrac49,-\tfrac89,\tfrac49)\),
so \(I_{q^*}=\operatorname{diag}(8/27,32/81)\), \(I_{\psi\lambda}=0\) and
\(\Phi_{D_s}(q^*)=8/27\). Chaining (R1)–(R3), every measurable three-cell
quantizer satisfies \(\Phi_{D_s}(q)\le v_3=8/27\). Hence \(q^*\) is a global
maximizer.

*Uniqueness.* Suppose \(\Phi_{D_s}(q)=8/27\). Then both inequalities in
(R2) are equalities. The second forces \(\{m_b\}\) to be an optimal codebook,
which by (R3) is \(\{-\tfrac23,0,\tfrac23\}\) — in particular the three
centroids are distinct. The first forces
\(m_{q(S)}\in\arg\min_b(X-m_b)^2\) a.s.; the midpoints of that codebook are
\(\pm1/3\), and \(P(X=\pm1/3)=0\), so a.s. the nearest codepoint is unique and
\(q=q^*\) a.s. up to relabeling. \(\square\)

Three hardenings fall out. **(a)** The argument never uses regularity: with the
pseudo-inverse convention the bound and the equality analysis are unchanged,
and the unique attainer \(q^*\) is regular, so no singular quantizer attains
the optimum either. **(b)** Cells with \(W_b=0\) are excluded by \(v_2<v_3\).
**(c)** Uniqueness is "a.s. up to labels *and null sets*" — the frozen
statement omits the null-set qualifier, which the registry patch restores.

### 8.2 (T2): strict isolation, in decision distance

Define \(d(q,q^*)=\min_\pi\sum_bP(A_b\triangle A^*_{\pi(b)})\). **This distance
is defined nowhere else in the workspace; the audit pins it here.** Note
\(d(q,q^*)=2\min_\pi P(q\ne\pi\circ q^*)\).

Let \(G(c)=E[\min_b(X-c_b)^2]-\tfrac1{27}\ge0\) on \([-1,1]^3\). \(G\) is
continuous, and by (R3) vanishes only at \(c^*\); projecting any codebook onto
\([-1,1]\) does not increase the distortion, so the infimum over
\(\mathbb R^3\) is attained on the cube. By compactness,

\[
g(\rho):=\inf\{G(c):c\in[-1,1]^3,\ \|c-c^*\|_\infty\ge\rho\}>0
\quad\text{for every }\rho>0 .
\tag{8.1}
\]

Now let \(q\) satisfy \(\Phi_{D_s}(q)\ge8/27-\delta\). By (R1)–(R2),
\(E[(X-m_q)^2]\le\tfrac1{27}+\delta\) and \(G(m)\le\delta\), so
\(\|m-c^*\|_\infty<\rho\) as soon as \(\delta<g(\rho)\). Fix \(\eta\in(0,1/3)\)
and take \(\rho=\eta/8\). For \(x\) with \(|x\mp1/3|>\eta\) the margin between
the correct codepoint of \(c^*\) and its nearest rival is
\(\tfrac43|x\mp\tfrac13|>\tfrac43\eta\); perturbing each codepoint by at most
\(\rho\) changes each squared distance by at most \(4\rho\), so the margin
stays \(>\tfrac43\eta-8\rho=\tfrac13\eta\). Therefore

\[
P\bigl(q\ne q^*,\ |X\mp\tfrac13|>\eta\bigr)\cdot\tfrac{\eta}{3}
\;\le\;E\bigl[(X-m_q)^2-\min_b(X-m_b)^2\bigr]\;\le\;\delta ,
\]

and \(P(|X-\tfrac13|\le\eta)+P(|X+\tfrac13|\le\eta)=2\eta\). Hence

\[
d(q,q^*)\;\le\;2\Bigl(\frac{3\delta}{\eta}+2\eta\Bigr)
\qquad\text{whenever }\delta<g(\eta/8).
\tag{8.2}
\]

Given \(\varepsilon>0\), choose \(\eta=\varepsilon/8\) and
\(\delta(\varepsilon)=\min\{g(\eta/8),\ \varepsilon\eta/24\}\); then
\(\Phi_{D_s}(q)>8/27-\delta(\varepsilon)\) forces \(d(q,q^*)<\varepsilon\),
which is (T2) in contrapositive. \(\square\)

This is a genuine compactness/rigidity argument with an explicit modulus, not
a restatement of uniqueness; and it is self-contained — DS15 Lemma 3 is not
invoked. The role DS15 Lemma 3 *could* play is exactly (8.1), and the audit
notes that its registered form would have to be re-scoped off (L) first.

### 8.3 (T3): empirical transfer, on one selection-independent event

Define \(\Omega_0=\Omega_1\cap\Omega_2\cap\Omega_3\cap\Omega_4\):

- \(\Omega_1\): \(\sup_{c\in[-1,1]^3}\bigl|P_Nf_c-Pf_c\bigr|\to0\), where
  \(f_c(x)=\min_b(x-c_b)^2\). *Proof:* the class is bounded by \(4\) and
  \(4\)-Lipschitz in \(c\) on the cube (\(|\min_ba_b-\min_bb_b|\le\max_b|a_b-b_b|\)
  and \(|(x-c)^2-(x-c')^2|\le4|c-c'|\)); a finite \(\epsilon\)-net plus the SLLN
  at each net point gives the uniform law.
- \(\Omega_2\): the SLLN on the finitely many fixed functionals
  \(1_{A^*_b},\,X1_{A^*_b},\,S_\lambda1_{A^*_b},\,X^2\) (\(b=1,2,3\)).
- \(\Omega_3\): \(P_N(|X\mp\tfrac13|\le\eta)\to\eta\) for every rational
  \(\eta\in(0,\tfrac13)\) (Glivenko–Cantelli; countably many).
- \(\Omega_4\): \(\sum_{i\le N}S_{\lambda,i}\ne0\) for every \(N\)
  (Reduction 5).

Each has probability one, so \(P(\Omega_0)=1\); **and none of the four
mentions a labeling**, so \(\Omega_0\) is selection-independent. Fix
\(\omega\in\Omega_0\) and let \((z^{(N)})\) be *any* sequence of exact global
optima — measurable or not, and possibly a different selection for each \(N\).

*Feasibility and existence.* On \(\Omega_2\), \(\hat W_b(z^*_N)\to1/3>0\) and
\(\hat I_N(z^*_N)\to I_{q^*}\), so eventually \(z^*_N\) has three nonempty
cells and \(\hat I^{z^*}_{\lambda\lambda}>0\); on \(\Omega_4\) every
three-nonempty-cell labeling is regular. The feasible set is finite and
eventually nonempty, so a global maximum exists, and by continuity of
\(v\mapsto v_{11}-v_{12}^2/v_{22}\) at \(I_{q^*}\) (where \(32/81>0\)),
\(\hat\Phi_{D_s}(z^*_N)\to8/27\).

*The squeeze.* On \(\Omega_1\), \(\hat D_{3,N}\to D_3=\tfrac1{27}\) and
\(P_N[X^2]\to\tfrac13\), so \(\hat v_{3,N}\to\tfrac8{27}\). With (R1)–(R2)
applied to the sample,

\[
\tfrac8{27}\leftarrow\hat\Phi_{D_s}(z^*_N)
\le\hat\Phi_{D_s}(z^{(N)})
\le\mathrm{btw}_N(X;z^{(N)})
\le\hat v_{3,N}\to\tfrac8{27},
\]

hence \(\hat\Phi_{D_s}(z^{(N)})\to8/27\) and \(\Delta_N\to0\).

*Rigidity.* Let \(\hat m^{(N)}\) be \(z^{(N)}\)'s \(X\)-centroids, all in
\([-1,1]\). By (R4), \(P_Nf_{\hat m^{(N)}}\le\hat D_{3,N}+\Delta_N\); by
\(\Omega_1\), \(G(\hat m^{(N)})\le\Delta_N+2\sup_c|P_Nf_c-Pf_c|+|\hat D_{3,N}-D_3|\to0\),
so by (8.1) \(\|\hat m^{(N)}-c^*\|_\infty\to0\). Repeating the margin argument
of §8.2 with \(P_N\) in place of \(P\), for every rational \(\eta\in(0,1/3)\)
and all large \(N\),

\[
P_N\bigl(z^{(N)}\ne q^*\bigr)
\;\le\;\frac{3\Delta_N}{\eta}\;+\;P_N\bigl(|X-\tfrac13|\le\eta\bigr)+P_N\bigl(|X+\tfrac13|\le\eta\bigr).
\tag{8.3}
\]

Letting \(N\to\infty\) (using \(\Omega_3\)) then \(\eta\downarrow0\) gives
\(P_N(z^{(N)}\ne q^*)\to0\) after relabeling. **(8.3) is checkable at finite
\(N\)**; it is the certificate the transfer artifact reports.

*Moments.* Scores are bounded (\(|S_\psi|\le1\), \(|S_\lambda|\le3\)), so
uniform integrability is free and, for each \(b\),
\(\bigl|P_N[S1_{z^{(N)}=b}]-P_N[S1_{q^*=b}]\bigr|\le3\,P_N(z^{(N)}\ne q^*)\to0\)
while \(P_N[S1_{q^*=b}]\to E[S1_{A^*_b}]\) on \(\Omega_2\). Hence every cell
mass and score moment converges, so \(\hat I_N(z^{(N)})\to I_{q^*}\), the
companion slope \(\hat B_z=\hat I_{\psi\lambda}/\hat I_{\lambda\lambda}\to0\),
the projected centroids \(\hat e_b\to(-\tfrac23,0,\tfrac23)\), and the
companion rule converges in \(P\)-measure to \(q^*\). \(\square\)

**No step centers the sample.** Every displayed empirical quantity is a raw
second moment about the origin; \(\hat v_{3,N}=P_N[X^2]-\hat D_{3,N}\) is *not*
a between-variance about \(\bar X_N\). The audit checked this line by line
because DS15's chapter convention is the opposite one.

### 8.4 (T4): finite ordinary exchange stability, and the feasibility convention

**The convention, stated exactly.** Following the audited D exemplar
(`AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md` §9), an ordinary one-point
relocation is admissible iff its **source cell remains nonempty**; there is no
capacity, balance, or minimum-mass restriction. The comparison domain is the
set of labelings reachable by such moves, evaluated with the same in-bin
profiled objective.

Two families of moves need separate treatment.

1. **Moves into a singular destination.** A move whose destination has
   \(\hat I_{\lambda\lambda}=0\) leaves the DS9-feasible in-bin class; under the
   DS11 pseudo-inverse convention it is nonetheless *evaluable*, and its value
   is \(\hat I_{\psi\psi}\), which has no projection tax subtracted. Such a move
   can therefore strictly beat a global optimum over regular labelings — see
   the new exact fixture in §15, where the gain is \(+1/96\). **On the named
   law this family is empty almost surely** (Reduction 5), so on \(\Omega_4\)
   the two conventions agree and global optimality over regular labelings *is*
   ordinary exchange stability. Off \(\Omega_4\) — atomic emulations, grid
   laws, hand-built tables — the conventions genuinely differ, and DS18 must
   name the in-bin convention. This is hardening **H2**.
2. **Moves that empty the source.** These are inadmissible by the convention.
   Even if they were admitted, they cannot improve: emptying cell \(a=\{i\}\)
   into \(b\) produces a configuration that is a *coarsening* of the current
   one, and DS11(b) refinement monotonicity gives
   \(S_\psi^+(\text{coarsening})\le S_\psi^+(\text{refinement})\). So the
   conclusion does not depend on this half of the convention.

With (1) and (2) settled, the step is immediate and holds at **every** \(N\) on
\(\Omega_4\), not merely eventually: every admissible relocation from
\(z^{(N)}\) lands in the feasible set, over which \(z^{(N)}\) is a global
maximum, so no admissible move has positive exact gain. The "eventually" in
the registered statement is needed only for the margins.

**Margins.** \(\hat W_b\to1/3>1/4=c_0\);
\(\lambda_{\min}(\hat I_N)\to\lambda_{\min}(\operatorname{diag}(8/27,32/81))=8/27>1/4=\kappa\)
— the audit confirmed that DS14's (M3) is \(\lambda_{\min}(\hat I_N)\ge\kappa\)
and **not** a \(\det/\operatorname{tr}\) conditioning number; had it been the
latter, \(\det/\operatorname{tr}=(256/2187)/(56/81)=32/189\approx0.169<1/4\)
would have failed. Separation \(\to2/3>1/2=\gamma\). All three limits have
strict slack, so convergence gives eventual satisfaction at the fixed rational
constants. (M1) holds for the law; (M4) is verified next.

### 8.5 (M4) and the boundary tube

The law is atomless with density \(1/4\) on a set of area \(4\). For a unit
\(v\) and half-width \(t\), \(\{|v^\top S-c|\le t\}\cap\mathrm{supp}\) lies in
a \(2t\times\mathrm{diam}\) rectangle, so its mass is at most
\(t\cdot\mathrm{diam}/2\). With the bounding rectangle
\([-1,1]\times[-2,3]\), \(\mathrm{diam}=\sqrt{29}\), so
\(\varphi(t)=\min(1,\sqrt{29}\,t/2)\) as registered is **valid**.

The support's own diameter is smaller, but the audit records a correction
worth stating because it is an easy slip: it is **not** \(\sqrt{26}\). The
farthest pair is not \((\mp1,3)\) against \((0,-2)\); it is a corner
\((1,3)\) against a point of the lower arc \(y=3x^2-2\) at the root of
\(18x^3-29x-1=0\) near \(x=-0.03451\), giving
\(\mathrm{diam}^2=26.03450\ldots>26\). Any diameter-based modulus for this law
is therefore bounded below by \(2.5512\,t\); the registered \(2.6926\,t\) is
within \(5.5\%\) of the best this route can give.

The bound was tested, not merely derived. An exact rational slab sweep — the
\(z\)-section is an interval of constant half-width \(\tau/|q|\) whose centre is
a parabola in \(x\), so its clipped length has an exactly computable range on
each \(x\)-cell — covered **480** slabs over 12 rational directions, 10
offsets and 4 half-widths, with enclosure widths \(\le2.5\times10^{-4}\):
**zero** violations of the registered constant, and zero even against the
tighter \(\mathrm{diam}^2\le2609/100\) constant \(2.5539\,t\). Worst observed
\(\mathrm{mass}/t=1.99858\) (direction \((3,-1)\), offset \(1\),
\(\tau=1/40\)). A seeded Monte-Carlo cross-check at 200,000 draws agrees with
the exact bounds to sampling error. So the registered constant holds with
roughly \(35\%\) slack, and the sweep suggests the sharp constant is near
\(2\) — below what any diameter argument can reach.

### 8.6 Two-route confirmation of the population algebra

Every population quantity was computed twice: exact bivariate polynomial
integration over the pre-shear square (route A), and a rigorous
`Decimal` interval route with directed rounding and an exact second-order
Taylor cell form (route B, no antiderivatives). Route B's enclosures contain
route A's exact values in **12/12** cases, with widths from \(10^{-48}\) to
\(1.5\times10^{-6}\). A third, independent Monte-Carlo route at 200,000 draws
gives \(\hat\Phi=0.29660\) against \(8/27=0.296296\) and
\(\hat\eta=0.888805\) against \(8/9=0.888889\).

## 9. Adversarial audit (`protocols/theorem.md` §G, each attack with outcome)

- **Strictness and ties.** Population ties are null: \(P(X=\pm1/3)=0\), so the
  equality analysis in §8.1 is not vacuous. Sample ties are permitted and were
  exercised (`exact_ties_at_cuts`, rows exactly at \(X=\pm1/3\)) — the sandwich
  survives; only the *raw population-cut labeling* becomes ambiguous, which the
  theorem never uses as a terminal. **Outcome: no defect; the tie-breaking rule
  for \(z^*_N\) is now stated explicitly (H3).**
- **Singleton and empty cells.** Empty cells are excluded at the population by
  \(v_2=1/4<8/27\) and at the sample by feasibility. Singletons are allowed and
  occur at small \(N\); they are irrelevant because the argument uses only cell
  means. Exercised in `tiny_and_singleton_cells`. **Outcome: no defect.**
- **Duplicate scores.** Duplicate rows occur with probability zero under the
  law and are harmless when present: unlike the D exchange theorem, DS18 never
  claims a strict nearest-centroid geometry for the finite labels, so split
  duplicates cost nothing. Exercised in `duplicate_atoms`. **Outcome: no
  defect; noted that DS18 is *not* subject to the
  `CE-D-UNMERGED-DUPLICATES-001` failure mode.**
- **Singular information / nuisance singularity.** The one genuine finding.
  See §8.4(1) and §15. **Outcome: assumption hardened, new boundary fixture.**
- **Atomic laws.** DS18 is a statement about one atomless law; every finite
  computation here is on an atomic emulation, and the audit is explicit that
  the a.s. arguments (Reduction 5, \(\Omega_4\)) are exactly what fails on
  atoms. **Outcome: boundary made explicit.**
- **Hidden compactness.** Located and made explicit: the only compactness is
  over the codebook cube \([-1,1]^3\), justified because \(X\) is bounded and
  projecting a codebook onto the cube cannot increase distortion. No compactness
  is assumed on the space of partitions. **Outcome: no defect.**
- **First-order-to-finite jumps.** None. No first-order/derivative
  approximation of a move appears anywhere; every finite comparison is an exact
  rational evaluation. **Outcome: no defect.**
- **Empirical-to-population jumps.** The load-bearing one. It is carried by the
  explicit four-event \(\Omega_0\) of §8.3, all of whose members are
  selection-independent — which is what licenses the "**every** sequence"
  quantifier. **Outcome: verified, and the event is now listed.**
- **Score-estimation error.** Excluded by hypothesis. If \(\hat s\ne s\), the
  retained information is \(\operatorname{Var}(E[s\mid q(\hat s)])\) and nothing
  here applies. **Outcome: scope restated in the node's assumptions.**
- **New-event extension.** The theorem's finite output is a *labeling*. What
  extends to unseen events is the limiting rule \(q^*\) and the companion rules
  converging to it — not the finite labels. **Outcome: transductive/inductive
  split kept explicit.**
- **Unequal and zero weights (packet extra).** Equal weights are load-bearing
  for the SLLN steps as stated. Exercised adversarially; the *sandwich* (R1)–(R2)
  survives arbitrary positive weights (it is pure algebra), but the limit
  identification does not, and DS18 claims nothing there. A zero-weight row is
  invisible to the objective and may carry any label. **Outcome: assumption
  restated as load-bearing for the transfer, not for the algebra.**
- **Cells depending on \(Z\) (packet extra).** Answered structurally by (R2):
  the reduction never assumes cells are \(X\)-measurable. Exercised by the
  exhaustive enumeration, which ranges over all canonical partitions of the
  sample. **Outcome: no defect; the mechanism is now stated.**
- **Label relabeling (packet extra).** All finite enumeration uses
  restricted-growth canonical forms, so labelings are quotiented by permutation
  by construction; the audit also verified permutation-invariance of the
  profiled value directly. **Outcome: no defect.**
- **Supports below \(N=4\) (packet extra).** \(N=3\) has a single canonical
  partition (three singletons) and **zero** admissible relocations; \(N<3\) is
  infeasible at \(K=3\). The \(N=4\) fixture is therefore support-minimal, as
  claimed. **Outcome: confirmed independently.**
- **Objective convention (packet extra).** Schur value versus its logarithm:
  §2. Monotone equivalence is sufficient everywhere "global optimizer" appears.
  **Outcome: no defect.**

## 10. Algorithmic consequence

The theorem is a **global-oracle** statement and stays one. It says that if an
exact global finite profiled-\(D_s\) optimizer is available, then for this law
its output converges to a deployable full-rank rule and is exactly
exchange-stable. It does **not** say that one-point exchange ascent, Lloyd-type
iteration, or the library's seeded solver finds that basin: the audit's own
transfer probe shows the exact optima at \(N=4\ldots11\) still disagree with
the population rule on 0–4 rows, and the \(N=4\) fixture shows the raw
population labels are not a terminal.

What *is* newly usable is (R4)/(8.3): \(\Delta_N=\hat v_{3,N}-\hat\Phi(z^*_N)\)
is computable from a sample with no combinatorial search, and bounds the
disagreement of every global optimum with the population rule. That is a
diagnostic an implementation could report — but it certifies a *global*
optimizer's behaviour, not the terminal a local solver returns, so it is not
yet a solver certificate.

## 11. Deployability consequence

**Unchanged: no `src/` or public API change is authorized by this audit.** The
verdict is verification, not promotion. Specifically:

- `compile_quantizer` remains D-only. DS18 supplies no finite \(D_s\) compile
  theorem; it supplies a *limiting* rule for one named law.
- The projected efficient-score interval rule remains the only established
  unconditional \(D_s\) compile path in the registered theory.
- Any future profiled-margin surface must still present a finite margin triple
  as a diagnostic, and must state the in-bin (DS9) feasibility convention
  explicitly — the new fixture in §15 shows that the choice of convention
  changes which labelings count as exchange-stable, and it is not a
  hypothetical: it is realised on the named law's own support at \(N=4\).
- Nothing here transfers to another law, to estimated scores, or to
  \(d_\psi>1\) or \(d_\lambda\ge2\).

## 12. Information-loss consequence

Exact and audited by two routes: \(\eta_{D_s}=(8/27)/(1/3)=8/9\), so the
optimal three-cell hard partition of this law's score space retains
\(88.9\%\) of the profiled Fisher information and loses \(L_{D_s}=1/9\). The
direction-resolved picture is the full \(D\) retention
\(R=I_{\rm full}^{-1/2}I_{q^*}I_{\rm full}^{-1/2}
=\operatorname{diag}(8/9,\ 160/459)\): the parameter of interest keeps
\(8/9\), while the nuisance direction keeps only \(160/459\approx0.349\) — the
binned model is deliberately nuisance-poor, and the profiled retention is high
*because* \(\beta=0\) makes the nuisance loss free at this optimum. That
coincidence is a property of this law, not a general phenomenon, and must not
be quoted as a generic \(D_s\) retention figure.

The empirical retention is the theorem's own limit: on \(\Omega_0\),
\(\hat\eta_{D_s}(z^{(N)})\to8/9\) for every sequence of global optimizers.
At finite \(N\) the gap is bounded above by \(\Delta_N/(1/3)=3\Delta_N\), which
the transfer artifact measures at \(\sim10^{-4}\) by \(N=4096\).

## 13. Updated status

- `DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`: remains **`project_proved`**, now
  audited, with an `audit` pointer, fully explicit assumptions, a hardened
  warning, and the corrected literature list. `publication_status` stays
  `internal` and `literature_search_status` stays `search_gap`.
- `AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`: new node, `project_proved`.
- `CE-DS-NONCENTERED-SINGULAR-DESTINATION-001`: new exact boundary
  counterexample, linked from the target's `boundary_counterexamples`.
- `OPEN-DS-MARGINS-NONCENTERED`, `DS-PROFILED-COMPILE-CERTIFICATE`,
  `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`: DS18 clauses re-worded to carry the
  audited scope (in-bin feasibility convention named; global-oracle boundary
  retained).
- DS15 (`OPEN-DS-MARGINS-AT-OPTIMA`) is **not** downgraded. Its scope is
  correct; the defect was DS18 citing it outside that scope, and DS18's proof
  text is now self-contained.

**Verdict: verified with hardened assumptions.** The complete registered
statement follows, with these hardenings now explicit:

- **H1** — the proof no longer imports (L)-conditioned DS15 lemmas; the scalar
  uniqueness, rigidity, and consistency steps are proved here for this law.
- **H2** — the in-bin (DS9) feasibility convention is named, and regularity is
  shown a.s. vacuous under the law (so the theorem is unaffected) while being
  load-bearing off that null set (so the convention must be stated).
- **H3** — uniqueness is "a.s., up to labels and null sets"; the reference
  labeling \(z^*_N\) is defined with the half-open convention
  \(\{X<-1/3\},\{-1/3\le X<1/3\},\{X\ge1/3\}\).
- **H4** — the probability-one event is exhibited as the explicit
  selection-independent intersection \(\Omega_0\), and the transfer is given
  the quantitative finite-\(N\) form (8.3).
- **H5** — (M3) is \(\lambda_{\min}(\hat I_N)\ge\kappa\); the margin triple is
  verified against that reading, with the \(\det/\operatorname{tr}\) reading
  explicitly excluded.

## 14. Registry patch

`claims/DS-NONCENTERED-GLOBAL-BASIN-TRANSFER.json` gains
`audit: "AUDITS/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001.md"`, the five
hardenings as explicit `assumptions`, the new
`boundary_counterexamples` entry, and the corrected `literature` list
(`Kieffer-1983`, `Mease-Nair-2006`, `Pollard-1981`,
`Rakhlin-Caponnetto-2006`, `Fisher-1958`, `Graf-Luschgy-2000`,
`deCastro-Dorigo-2019` added). `claims/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER.json`
is new, with this report as `proof_location`, the independent script as
`artifact`, and the audited target among its dependencies. The three downstream
nodes are re-worded. `KNOWN_RESULTS/05b-ds-bridge.md` DS18 carries an audit
banner and the hardened proof steps; `OPEN_PROBLEMS.md` OP29 and
`manuscripts/README.md` are synchronised.

## 15. Counterexample and regression artifacts

**New exact boundary counterexample —
`CE-DS-NONCENTERED-SINGULAR-DESTINATION-001`.** Support-minimal at \(N=4\),
exactly centered, every row on the named law's support
(\(X=(-1,0,\tfrac12,\tfrac12)\), \(Z=(-1,1,-\tfrac34,\tfrac14)\)):

\[
S=\bigl[(-1,1),\ (0,0),\ (\tfrac12,-1),\ (\tfrac12,0)\bigr],\qquad w_i=\tfrac14 .
\]

The exact global optimum over **regular** labelings is \(1/12\), attained by
exactly two labelings, \((0,0,1,2)\) and \((0,1,1,2)\). The single labeling with
an exactly singular binned nuisance block, \((0,1,0,2)\), has
\(\hat I=\bigl[\begin{smallmatrix}3/32&0\\0&0\end{smallmatrix}\bigr]\) and DS11
pseudo-inverse value \(3/32\). And **both** global regular optima reach it by
one admissible relocation with exact gain

\[
\tfrac3{32}-\tfrac1{12}=\tfrac1{96}>0 ,
\]

while every other admissible move is non-improving. So: *if the ordinary
comparison domain admits a singular destination evaluated by the pseudo-inverse
extension, then every exact global optimum over regular labelings of this table
fails one-point exchange stability.* This does not refute DS18 — such tables are
null under the law (Reduction 5), and the project's in-bin convention makes the
move inadmissible — but it shows the convention is load-bearing rather than
cosmetic, at the smallest support where a relocation exists at all. It is
distinct from `CE-DS-DEGENERATE-GLOBAL-TIE-001`, which compares *values* at
\(N=8\) on a Gaussian-derived table; this one exhibits the gap as an
**admissible one-point move from every global optimum**, on the DS18 law's own
support, at \(N=4\).

**Independent instrument.** `py/audit_ds_noncentered_global_basin_transfer.py`
(stages `population`, `exact`, `search`, `boundary`, `transfer`) with the five
provenance-stamped artifacts under
`AUDITS/artifacts/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001/`.

**Regressions in `tests/test_research_claims.py`** — all recompute from raw
data, never from copied constants:

- `test_ds18_population_law_integrates_to_the_registered_optimum` — integrates
  \(I_{\rm full}\), the cell moments, \(I_{q^*}\), \(v_3\) and \(v_2\) from the
  law definition with an inlined exact polynomial integrator.
- `test_ds18_profiled_scalar_sandwich_holds_on_every_small_partition` — the
  full (R1)–(R3) chain on every canonical partition of seeded tables.
- `test_ds18_singular_destination_beats_the_regular_optimum` — the new fixture,
  rebuilt from its \((X,Z)\) construction.
- the pre-existing `test_ds18_population_cut_labels_need_not_be_exchange_stable`
  and `test_ds18_named_off_class_root_and_margins_are_exact` were re-run
  unchanged and pass against the audited statement.

## 16. Next dependency-blocking question

DS18 is verified, so the packet's first branch applies:

> Can a practical profiled solver be proved to select this full-rank basin
> **without** global combinatorial optimization, while retaining computable
> margins and value guarantees under perturbations of the law?

The audit sharpens it into the next concretely attackable step. The quantity
\(\Delta_N=\hat v_{3,N}-\hat\Phi(z^*_N)\) is computable in \(O(N\log N)\) and,
by (8.3), converts *any* labeling's value gap into a bound on its disagreement
with the population rule. So the blocking question is now:

**Is there a labeling rule computable in polynomial time — exchange ascent from
the scalar interval seed being the candidate — whose output \(\tilde z_N\)
satisfies \(\hat v_{3,N}-\hat\Phi(\tilde z_N)\to0\) almost surely on this law?**
Any such rule inherits (8.3) verbatim and therefore inherits the whole
transfer, converting DS18 from a global-oracle theorem into a solver
certificate. The finite obstruction to attack first is the one this audit
measured: at \(N\le11\) the exact optimum still disagrees with the population
rule on up to four rows, and the raw population labels are not a terminal, so
the seed cannot be the population cuts.
