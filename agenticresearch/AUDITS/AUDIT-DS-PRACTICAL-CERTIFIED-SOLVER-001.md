# Publication-grade audit of the DS19 tilt-DP certificate complex

**Claims:** `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`, `DS-TILT-DUAL-CERTIFICATE`, `DS-TILT-DUAL-STRONG-DUALITY-FAILS`, `DS-STRIP-DP-DELTA-CONSISTENCY`, `DS-MATRIX-TILT-NONQUASICONVEX`, `DS-PROFILED-COMPILE-CERTIFICATE` (DS19 clauses)
**Audit:** `AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER`
**Date:** 2 September 2026
**Source frozen:** `research-ds-practical-certified-solver` at `2c9cb77` (theorem source), packet handoff `0564f03`
**Result:** the DS19 complex is **verified with hardened assumptions**; the umbrella
stays **reduced** with a narrower open remainder. Two exact boundary
counterexamples were found and serialized (`CE-DS-TILT-DUAL-GAP-002`,
`CE-DS-TILT-DUAL-TIE-MASK-001`), one proof gap was closed (the tie lemma), one
computation claim was widened (exact polynomial-bit minimisation at
\(d_\lambda=1\) for every \(K\); fixed \(d_\lambda\), variable \(K\) in
arithmetic complexity by prior art), one bound was tightened (\(O(KN)\)
fixed-tilt evaluation after sorting), and one minimality statement was
corrected (\(N=3,K=2\) is the true support minimum).

---

## 1. Target statement

Tier A of DS19 concerns a finite weighted score table \((s_i,w_i)_{i=1}^N\)
with \(s_i=(s_{\psi i},s_{\lambda i})\in\mathbb R\times\mathbb R^{d_\lambda}\),
positive rational weights, and labelings \(z\) with exactly \(K\) nonempty
cells. Every second moment is about the score-space origin; nothing is
sample-centered. With \(I_z=\sum_bW_b\mu_b\mu_b^\top\),

\[
V_z(\beta)=\sum_b\frac{\bigl(\sum_{i\in b}w_i(s_{\psi i}-\beta\!\cdot\! s_{\lambda i})\bigr)^2}{W_b}
=[1,-\beta]\,I_z\,[1,-\beta]^\top,\qquad
v_K(\beta)=\max_zV_z(\beta),\qquad
\Phi^+(z)=I_{\psi\psi}-I_{\psi\lambda}I_{\lambda\lambda}^+I_{\lambda\psi}.
\]

Let \(\mathcal D(\beta)\) be the set of labelings attaining \(v_K(\beta)\),
\(g^+=\max_z\Phi^+(z)\), \(g_{\rm reg}=\max\{\Phi(z):I_{\lambda\lambda}(z)\succ0\}\),
\(d=\min_\beta v_K(\beta)\), \(p^+=\max\{\Phi^+(z):z\in\mathcal D(\beta)\text{ for some }\beta\}\),
and \(p_{\rm reg}\) the same maximum over regular DP-active labelings.

The frozen compound claim is:

**(T1) Bracket, both domains.** \(p^+\le g^+\le d\) and
\(p_{\rm reg}\le g_{\rm reg}\le g^+\le d\); the same dual ceiling covers the
DS11 pseudo-inverse class and a fortiori the DS9 regular subclass; a singular
DP state is never an in-bin lower bound.

**(T2) Saddle closure gate.** \(p^+=g^+=d\) iff some \((\beta^*,z^*)\)
satisfies \(z^*\in\mathcal D(\beta^*)\) and
\(\beta^*I_{\lambda\lambda}(z^*)=I_{\psi\lambda}(z^*)\); if in addition
\(I_{\lambda\lambda}(z^*)\succ0\), \(z^*\) is an ordinary in-bin global
optimum.

**(T3) Computation.** (a) Fixed rational \(\beta\): \(v_K(\beta)\), an active
labeling, its exact gradient and the primal values in \(O(KN^2)\) rational
operations, ties tolerated. (b) Certified rational \(\varepsilon\)-bracket on
\(d\) in time polynomial in the input bits and \(\log(1/\varepsilon)\), with
an observable coercivity radius after quotienting common nuisance-null
directions. (c) Exact algebraic minimisation for fixed \((K,d_\lambda)\) via
the \(O(N^{2d_\lambda})\) tilt-order arrangement; the variable-\((K,d_\lambda)\)
exact bit complexity is `OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY`.

**(T4) Order-one gap.** `CE-DS-TILT-DUAL-GAP-001` (\(N=4,K=3\), equal weights)
has \(g=116805/11816\) and a rational lower certificate
\(d\ge61717893/5839400\), hence \(d-g\ge105329256/154014175>0.68\); the
witness is support-minimal; a positive-weight bounded augmentation family with
added mass \(1/r\) keeps the gap bounded below as \(r\to\infty\).

**(T5) DS18 \(\Delta\)-consistency.** On the DS18 law, the raw \(\beta=0\)
three-interval DP labeling \(\tilde z_N\) is eventually regular a.s. and
\(0\le\Delta_N=\hat v_{3,N}-\hat\Phi_{D_s}(\tilde z_N)=\hat I_{\psi\lambda}^2/\hat I_{\lambda\lambda}\to0\),
so the audited DS18 disagreement inequality applies to it; nothing about
exchange stability, basin selection or compilation is claimed.

**(T6) Tier B.** For \(d_\psi=d_\lambda=2\), `CE-DS-MATRIX-TILT-NONQUASICONVEX-001`
(\(\{\pm2e_j\}\), \(K=N=8\)) has \(V(B)=I_2+BB^\top\) and determinants
\(17,17,25\) at \(B_0,B_1,(B_0+B_1)/2\): the outer log-determinant map is not
quasiconvex; weak matrix-tilt duality survives.

**(T7) Observable compile table** (`DS-PROFILED-COMPILE-CERTIFICATE`): a
regular exhibited saddle certifies finite globality; an open bracket reports
an interval; the projected efficient-score route stays the unconditional
projected compiler; a DS14 companion needs all audited hypotheses; otherwise
refuse.

## 2. Criterion and problem level

- Criterion: in-bin profiled \(D_s\) at \(d_\psi=1\) — the scalar Schur
  complement \(S_\psi(I)=I_{\psi\psi}-I_{\psi\lambda}I_{\lambda\lambda}^{-1}I_{\lambda\psi}\),
  reported as a *value*, never as \(\log\) of it; on the generalized domain
  the DS11 Moore–Penrose value \(\Phi^+\). Tier B uses \(\log\det\) of the
  \(2\times2\) generalized Schur complement.
- Level: `finite_assignment` for T1–T4, T6 (labelings of a finite table);
  `empirical_to_population` for T5; the umbrella and the compile table are
  registered at `empirical_inductive_quantizer` because a closed saddle
  induces a strip rule \(s\mapsto\) interval index of
  \(s_\psi-\beta^*\!\cdot s_\lambda\) (§11).
- Decision variable: a hard labeling with exactly \(K\) nonempty cells; the
  tilt \(\beta\in\mathbb R^{d_\lambda}\) is a multiplier, not a decision.
- Score oracle: direct exact scores. Estimated scores, held-out and
  population statements are outside every component except T5's named law.

## 3. Status before the audit

All six nodes were `publication_status: internal`, unaudited, with warnings
forbidding any `src/` use. `DS-TILT-DUAL-CERTIFICATE`, `DS-STRIP-DP-DELTA-CONSISTENCY`,
`DS-PROFILED-COMPILE-CERTIFICATE` and the umbrella were `project_proved`;
`DS-TILT-DUAL-STRONG-DUALITY-FAILS` and `DS-MATRIX-TILT-NONQUASICONVEX` were
`counterexample`; `OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY` was `open` (OP31, P7).
P1 had been closed and removed from `registry.json` on the strength of DS19.

## 4. Dependencies rechecked

The closure returned by `registry.py show --deps` has 27 nodes. The audit
re-derived nothing that is registered `project_proved` and audited; it checked
that DS19 uses each dependency inside its registered hypotheses.

1. **`DS-PROFILED-VARIATIONAL` (DS11; audited).** DS19 uses only the
   *matrix* identity \(S^+_\psi(I)=\min_B V(B)\) with attainment set
   \(\{B:BI_{\lambda\lambda}=I_{\psi\lambda}\}\), valid for every PSD block
   matrix. DS11's registered assumption "centered scores" concerns the
   \(\operatorname{Var}(E[\cdot\mid Z])\) *reading*, not the identity, and
   \(I_z=\sum_bW_b\mu_b\mu_b^\top\) is PSD whether or not the rows are
   centered. Use is in scope. The audit re-verified the identity, the
   completion-of-squares form \(V_z(\beta)-\Phi^+(z)=(\beta-\beta_z)I_{\lambda\lambda}(\beta-\beta_z)^\top\),
   and invariance along null directions on every one of 125,491 canonical
   partitions (§6), including singular blocks (0 violations).
2. **`DS-SCALAR-EFFICIENT-DP` (DS8) / Fisher contiguity.** DS19 needs
   contiguity of an optimal partition of a *weighted* scalar table with
   possible *exact ties*. The registered node is for atomless laws or finite
   samples without a tie statement; the audit supplies the missing tie lemma
   (§7.2) and verified DP-versus-brute-force agreement on all 125,491
   partitions at 7 probe tilts plus every exact minimizer, and over all 184
   tie orders of six deliberately tied tables (0 disagreements).
3. **`DS-NONCENTERED-GLOBAL-BASIN-TRANSFER` + `AUDIT-…` (DS18; audited).**
   DS19.4 imports (i) the scalar squeeze \(\hat\Phi\le\operatorname{btw}_N(X;z)\le\hat v_{3,N}(X)\)
   for arbitrary finite \(z\), (ii) the selection-independent event
   \(\Omega_0\) on which \(\hat D_{3,N}\to1/27\) uniformly over codebooks and
   the fixed-cell SLLN holds, and (iii) the finite-\(N\) disagreement bound.
   All three are stated in DS18.2 for *arbitrary* labelings or without
   reference to a labeling; none requires \(z\) to be a profiled optimum. The
   bound (iii) is stated there for labelings with
   \(\hat\Phi(z)\ge\hat\Phi(z_N^*)\); §8.5 shows \(\tilde z_N\) satisfies the
   only property actually used (own-codebook distortion excess \(\le\Delta_N\)).
   Use is in scope.
4. **`DS-EFFICIENT-SCORE-GLOBAL-UPPER`, `DS-EXACT-MOVE-ORACLE`.** Cited by
   the umbrella for context; DS19's proofs do not consume them.
5. **`DS-SCHUR`, `FI-QUANT-IDENTITY`, `D-RANK2-MOVE`, `D-LOGDET-GAIN`,
   `FI-RANK-CEILING`.** Structural; unaffected.
6. **Registry and quantifier audit (packet attack 1).** Statuses, levels and
   edges are consistent; `implies`/`dependencies` are symmetric; the umbrella
   is `project_proved` without a programme (correct, it is not `open`); OP31
   is the only open node and carries P7. No measured scan was promoted to
   theorem authority: `N-DS-PRACTICAL-*` rows are labelled measured, and the
   P1 closeout cites DS19.1–DS19.4, all of which are derivations. Two
   quantifier defects were found and are repaired in §13: "support-minimal"
   in `DS-TILT-DUAL-STRONG-DUALITY-FAILS` is true only for \(K=3\), and
   "computable in \(O(KN^2)\) … tolerates ties" was asserted without a proof.

## 5. Nearest literature

Independent triangulation per `protocols/literature.md`, recorded in
`LITERATURE/audits/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-2-September-2026.md`
(six fields per source; graph round 8). The researcher's four comparison
sources were re-read only afterwards.

- **Pukelsheim & Titterington (1983)** and **Silvey & Titterington (1973)**:
  design-side \(D_s\)/Lagrangian duality on the *convex* set of design
  measures. Transfers the certificate viewpoint; strong duality does not,
  because the hard-partition feasible set is finite and nonconvex — and the
  audit's \(N=3\) witnesses make the interchange failure explicit.
- **Li & Mathias (2000)**: the DS11 identity; classical, already registered.
- **Wang & Song (2011), Grønlund et al. (2017; primary text)**: the fixed-tilt
  interval DP is the classical 1-D \(k\)-means DP, \(O(KN^2)\), and \(O(KN)\)
  after sorting by monotone-matrix search; weighted points covered; exact ties
  not treated.
- **Megiddo (1983), Toledo (1993; primary text)**: parametric search. With
  \(F=-v_K\) and the interval DP as an evaluator whose comparisons are signs of
  degree-\(\le2\) polynomials in \(\beta\), Toledo's theorem gives exact
  minimisation for **fixed \(d_\lambda\) and variable \(K\)** in time
  polynomial in the DP's arithmetic operations — strictly wider than DS19.2's
  fixed-\((K,d_\lambda)\) scope. Neither source bounds bit complexity.
- **Carstensen (1983; secondary), Gajjar & Radhakrishnan (2019)**: the
  superpolynomial parametric-envelope warning that justifies refusing
  crossings-plus-midpoints as an exact method.

Direct antecedents exist for five ingredients separately; no source states
the combined theorem on hard partitions. Claim-level status stays
`search_gap` (never novelty). Two attribution repairs follow: the
exact-computation scope of `DS-TILT-DUAL-CERTIFICATE` is widened, and the
fixed-tilt bound is \(O(KN)\) after sorting.

## 6. Counterexample search

Instrument: `py/audit_ds_practical_certified_solver.py` (pure stdlib,
`fractions.Fraction`, quadratic irrationals exact in \(\mathbb Q(\sqrt D)\);
no import of the researcher's harness or of `scorequant`; LCG seeds
\(20260902+1000n+\text{rep}\)). Artifacts under
`AUDITS/artifacts/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001/` carry git revision,
script SHA-256, platform, arithmetic mode and counts.

| Stage | Scope | Outcome |
|---|---|---|
| `witness` | fixture 001 rebuilt from raw rows; exact envelope minimum; \(N=3,K=2\) grid | all registered rationals reproduced; **exact** \(d=44729/4232\) at rational \(\beta^*=-8/23\), exact gap \(534361/781333\approx0.6839\) (certificate \(0.68389\)); 884 of 2,300 \(N=3,K=2\) tables have a gap |
| `ceiling` | 106 table/\(K\) pairs, \(N\le10\), \(K\in\{2,3,4\}\), \(d_\lambda\in\{1,2\}\), 125,491 canonical partitions, 7–8 probe tilts each, exact \(d\) on 56 | 0 weak-duality, DS11, completion-of-squares, null-direction, contiguity or refinement violations; 0 failures of \(g^+\le d\); 5 tables with \(g^+>g_{\rm reg}\), 5 with an empty regular class, 5 singular DP-active labelings (never counted in \(p_{\rm reg}\)); 2 tables with \(p^+<g^+\) |
| `saddle` | 54 \(d_\lambda=1\) pairs with exact \(d\); 6,688 exhaustive integer grid tables | closure \(\Leftrightarrow\) saddle on 54/54 (34 closed, 20 open, 14 algebraic minimizers, 1 singular-only closure); **362 tie-masked closures** on the grid, 184 with a regular closing labeling |
| `ties` | 6 tied tables, 184 tie orders | DP value order-independent and equal to brute force in all 184; one-sided derivative rules exact; convexity lemma 280/280 |
| `compute` | 54 radius/bit-model checks; 7 \(d_\lambda=2\) brackets; 1 quotient table; 4 arrangement counts | minimizer inside the radius 54/54; measured heights and breakpoint separations inside the a-priori bounds; worst-case bisection depth \(\le592\) bits, actual probes \(\le6\); 6/7 brackets closed to \(\varepsilon=1/20\), all valid; quotient exact; arrangement counts within \(1+m+\binom m2\) |
| `family` | \(r=2..6\) (\(N=6..10\), up to 9,330 partitions), exact \(d_r\) | gaps \(0.028,0.113,0.189,0.251,0.302\), all positive and increasing; all base-induced partitions regular; \(r\cdot\)drift bounded (\(\le12.6\) for \(d\), \(\le10.3\) for \(g^+\)); \(p_2^+=3.17<g_2^+=4.92\) |
| `ds18` | 12 exact samples, \(N\in\{64,256,1024,4096\}\times3\); 10 exhaustive tables, 14,805 partitions | all \(\tilde z_N\) regular; \(\Delta_N=\hat I_{\psi\lambda}^2/\hat I_{\lambda\lambda}\) exact 12/12; \(\Delta\) from \(0.016\)–\(0.071\) (\(N=64\)) to \(1.5\cdot10^{-4}\)–\(6\cdot10^{-4}\) (\(N=4096\)); cuts \(\to\pm1/3\); disagreement inequality holds at \(\eta\in\{1/10,1/20,1/40\}\) 12/12; 0 tax or centering violations |
| `tierb` | fixture rebuilt from raw rows; 680 weak-duality checks on a 6-row \(d_\psi=d_\lambda=2\) table; smaller-support search | \(I_z=I_4\), \(V(B)=I_2+BB^\top\) by direct evaluation, determinants \(17,17,25\); 0 weak-duality violations; a **4-row, \(K=4\)** uncentered midpoint violation (\(115/16,347/16\to369/16\)) exists |
| `invariances` | protocol-G battery | all invariances hold (§9) |

Boundary failures found and serialized (§15): `CE-DS-TILT-DUAL-GAP-002`
(support-minimal gap at \(N=3,K=2\)) and `CE-DS-TILT-DUAL-TIE-MASK-001`
(closed bracket reported open by a deterministic tie policy).

## 7. Algebraic reduction

### 7.1 Weak duality, both domains, and attainment

For any PSD block matrix \(I_z\) the DS11 identity gives
\(\Phi^+(z)=\min_\gamma V_z(\gamma)\le V_z(\beta)\le v_K(\beta)\) for every
\(\beta\); taking \(\max_z\) then \(\min_\beta\) gives \(g^+\le d\), and
\(p^+\le g^+\), \(p_{\rm reg}\le g_{\rm reg}\le g^+\) are inclusions of the
maximised sets. Nothing here needs centering or regularity, so the ceiling
covers the whole DS11 class and hence DS9. \(d\) is attained: writing
\(L=\operatorname{span}\{s_{\lambda i}\}\), for \(u\perp L\) every cell mean
satisfies \(u\cdot\mu_{b\lambda}=0\), so every \(V_z\) is constant along \(u\);
on \(L\) the singleton-versus-rest bound \(v_K(\beta)\ge w_i(s_{\psi i}-\beta\cdot s_{\lambda i})^2\)
(§7.4) is coercive, so a minimizer exists. \(p^+\) is a maximum over the
finite set of envelope-active labelings, hence attained.

### 7.2 The tie lemma (closes the proof gap in DS19.1/DS19.2)

**Lemma.** Fix \(\beta\) and let \(G\) be a group of rows with equal tilted
value \(t\). Among the labelings attaining \(v_K(\beta)\) there is one in
which \(G\) is either contained in a single cell or distributed only among
cells consisting solely of tied rows of value \(t\). Consequently the interval
DP returns \(v_K(\beta)\) in **every** total order consistent with the sorted
weak order, and the labeling active on \((\beta,\beta+\varepsilon)\)
(resp. \((\beta-\varepsilon,\beta)\)) is contiguous in the order that breaks
ties by decreasing (resp. increasing) \(s_\lambda\).

*Proof.* Let cell \(A\) contain non-tied rows with moment \(M_A\), mass
\(W_A\), and a tied sub-mass \(g_A\ge0\) from \(G\). Its contribution is
\(f_A(g_A)=(M_A+tg_A)^2/(W_A+g_A)\). With \(u=W_A+g_A\) and \(c=M_A-tW_A\),
\(f_A=c^2/u+2ct+t^2u\), so \(f_A''(g)=2c^2/(W_A+g)^3\ge0\): each such term is
convex in the tied mass it receives, and a cell made only of tied rows
contributes \(t^2\) times its mass, which is linear. The total objective is
therefore a convex function of the vector of tied masses received by the
mixed cells, over the polytope of achievable allocations, and a convex
function attains its maximum at an extreme allocation. If no pure-tied cell
exists, the extreme allocations put all of \(G\) into one mixed cell. If a
pure-tied cell exists, moving tied mass from a mixed cell into it changes the
objective by \(f_A(0)+t^2g_A-f_A(g_A)=g_A\,(M_A-tW_A)^2/(W_A(W_A+g_A))\ge0\),
so all of \(G\) may be moved into pure-tied cells. In both cases the resulting
labeling is contiguous in every tie order (a pure-tied cell is a sub-interval
of \(G\) in any order, and its value \(t^2\times\)mass does not depend on
which rows it holds). The one-sided statements follow because for
\(\beta'=\beta\pm\varepsilon\) the tilted values are \(t-\pm\varepsilon s_{\lambda i}\),
whose strict order among tied rows is by \(\mp s_\lambda\), and the labeling
optimal at \(\beta'\) for all small \(\varepsilon\) is active at \(\beta\) with
the extreme derivative (and, among equal derivatives, the largest curvature
\(\sum_bL_b^2/W_b\)). ∎

The instrument checks the lemma's convexity step (280 random chords), the
order-independence on 184 tie orders, and the one-sided rules by exact finite
differences (§6). Duplicate full-score rows are tied at every \(\beta\), so
the lemma also settles the collapsed-atom question for the *dual*: the
row-level and atom-level \(v_K\) coincide whenever \(K\le\) the number of
atoms (§9).

### 7.3 Saddle closure, both directions, without minimax interchange

(\(\Leftarrow\)) If \(z^*\in\mathcal D(\beta^*)\) and
\(\beta^*I_{\lambda\lambda}(z^*)=I_{\psi\lambda}(z^*)\), the DS11 attainment
set gives \(\Phi^+(z^*)=V_{z^*}(\beta^*)=v_K(\beta^*)\ge d\ge g^+\ge\Phi^+(z^*)\),
so \(p^+=g^+=d\) (\(z^*\) is DP-active). (\(\Rightarrow\)) If \(g^+=d\),
take **any** \(\Phi^+\)-maximiser \(z^*\) and **any** dual minimiser
\(\beta^*\) (both exist, §7.1): \(d=\Phi^+(z^*)=\min_\gamma V_{z^*}(\gamma)\le V_{z^*}(\beta^*)\le v_K(\beta^*)=d\),
so \(z^*\in\mathcal D(\beta^*)\) and \(\beta^*\) minimises \(V_{z^*}\), i.e.
solves the normal equation by completion of squares. Nonunique dual minimisers
and nonunique DP states are harmless for the iff: every maximiser–minimiser
pair is a saddle. The regular refinement: \(g_{\rm reg}=d\) forces
\(g^+=d\) and a regular \(\Phi^+\)-maximiser, hence a regular saddle; and a
regular saddle certifies \(\Phi(z^*)=\Phi^+(z^*)=g^+\ge g_{\rm reg}\ge\Phi(z^*)\).

**Hardening.** The iff is a statement about the *sets* \(\mathcal D(\beta^*)\).
A deterministic implementation holds one member of \(\mathcal D(\beta^*)\);
that member need not be the saddle even when the bracket closes.
`CE-DS-TILT-DUAL-TIE-MASK-001` (§15) exhibits this at \(N=3,K=2\) with
pairwise-distinct tilted values at \(\beta^*\): a DP *value* tie, not a
tilted-value tie, between the zero-derivative saddle labeling and a crossing
labeling. The frozen text's "that only weakens its lower bound" is correct
and is now made explicit: a reported open interval \([\Phi^+(z_{\rm DP}),d]\)
is **not** evidence of a duality gap.

### 7.4 Coercivity radius and the certified bracket (bit model)

For every row \(i\) the partition placing \(i\) alone and filling \(K-1\)
cells with the other \(N-1\ge K-1\) rows gives
\(v_K(\beta)\ge w_i(s_{\psi i}-\beta\cdot s_{\lambda i})^2\). Any minimiser
has \(v_K(\beta^*)\le v_K(0)\), so it lies in every slab
\(|\beta\cdot s_{\lambda i}-s_{\psi i}|\le\sqrt{v_K(0)/w_i}\). After
quotienting \(L^\perp\) the rows \(s_{\lambda i}\) span, and Cramer's rule on
\(d_\lambda\) independent slabs gives a rational box radius \(R\) of
polynomial bit size (the instrument uses the \(d_\lambda=1\) slab bound and,
at \(d_\lambda=2\), the parallelogram of two independent slabs). \(v_K\) is a
maximum of finitely many convex quadratics, hence convex and Lipschitz on the
box with polynomial-bit constant. Each oracle call returns \(v_K(\beta)\) and a
subgradient (the gradient of an active quadratic) in \(O(KN^2)\) — in fact
\(O(KN)\) after sorting (Grønlund et al.) — rational operations on
polynomial-bit numbers.

*Certificate mechanism (not named in the frozen proof).* Every oracle call at
\(\beta_k\) yields the global affine minorant
\(v_K(\beta)\ge v_K(\beta_k)+g_k\cdot(\beta-\beta_k)\). The exact minimum over
the box of the cutting-plane model \(\max_k(\cdot)\) is a linear program in
\(d_\lambda+1\) variables with polynomially many constraints — solvable
exactly in polynomial time — and is a valid rational lower bound because the
box contains a minimiser. The best oracle value is a rational upper bound.
The ellipsoid method with the standard rounding discipline (Grötschel–Lovász–
Schrijver) needs \(O(d_\lambda^2\log(RL/\varepsilon))\) oracle calls to bring
the upper bound within \(\varepsilon\) of \(d\), and the model minimum is then
within \(\varepsilon\) as well; all iterates stay polynomial-bit. This is the
polynomial certified-\(\varepsilon\) claim, with the bit model explicit. The
instrument demonstrates the certificate with a Kelley loop whose query points
are rounded to a \(2^{-16}\) grid (unrounded iterates blew up past 4,300
digits in the first attempt — the rounding discipline is load-bearing).

### 7.5 Exact minimisation at \(d_\lambda=1\) for every \(K\) (audit-supplied)

Let \(q_z(\beta)=A_z\beta^2+B_z\beta+C_z\). The coefficients are sums of
\(K\) cell terms \(M_b^2/W_b\); with score denominator lcm \(d_s\) and weight
denominator lcm \(d_w\), each \(q_z\) has denominator dividing
\(d_s^2d_w\prod_bn_b\le d_s^2d_w^{K+1}\) (\(n_b\le d_w\) the integer mass
numerators) and \(|A_z|\le\max s_\lambda^2\), \(|B_z|\le2\max|s_\psi s_\lambda|\),
\(|C_z|\le\max s_\psi^2\). Hence every difference \(q_z-q_{z'}\), cleared to
integers, has height \(H\le2\max(\cdot)\,(d_s^2d_w^{K+1})^2\) — polynomial
bits. Breakpoints of \(v_K\) are real roots of such differences. Two distinct
roots of two integer polynomials of degree \(\le2\) and height \(\le H\) are
separated by at least \(\delta=1/(H^4(2(1+H))^3)\): if the polynomials share
no root the resultant is a nonzero integer bounded by \(H^4\prod|r_i-r'_j|\)
with all roots bounded by \(1+H\); if they share a root the two remaining
roots differ by a rational with denominator \(\le H^2\); within one
polynomial the roots differ by \(\sqrt{\mathrm{disc}}/|a|\ge1/H\).

*Algorithm.* Bracket \([-R-1,R+1]\). At a rational probe \(x\) the interval DP
in the two perturbation orders (§7.2) returns the exact one-sided derivatives
\(D^-(x)\le D^+(x)\) of the convex \(v_K\). If \(D^-(x)\le0\le D^+(x)\), \(x\)
is a minimiser (certificate). Otherwise the sign tells the side; bisect.
After the bracket width falls below \(\delta\) it contains at most one
breakpoint, so \(v_K\) equals the right-active quadratic at the left end on
\((\mathrm{lo},r)\) and the left-active quadratic at the right end on
\((r,\mathrm{hi})\); the minimiser is the vertex of one of them (rational) or
their crossing \(r\) (a root of a rational quadratic, exact in
\(\mathbb Q(\sqrt D)\)), and the certificate is re-evaluated exactly in that
field. Depth \(\le\log_2(2(R+1)/\delta)=O(K\log d_w+\log d_s+\log H)\) probes,
each \(O(KN^2)\): **polynomial bit complexity, \(K\) part of the input**.
Probing the vertices and the crossing root at every step (as the instrument
does) only accelerates. Measured: worst-case depth \(\le592\) bits on the
catalogue, actual probes \(\le6\); 14 of 54 minimisers are algebraic of
degree 2 (e.g. \(\beta^*=19-\tfrac1{12}\sqrt{51840}\) on the duplicate
table).

*Fixed \(d_\lambda\ge2\).* The DP is an evaluator in Toledo's sense with
comparison degree 2, so the exact minimum is computable in polynomially many
arithmetic operations for fixed \(d_\lambda\) and variable \(K\) (prior art,
§5); a polynomial *bit* bound is not supplied by that source, and the
one-dimensional root-separation argument does not lift directly (breakpoints
become conic arrangements). This is the corrected remainder of OP31.

### 7.6 Order-one family

Base table with masses \((1-1/r)/4\), plus \(r\) distinct rows
\((j/(r+1)^2,j/(r+1)^3)\) of mass \(1/r^2\). For a labeling \(z\) of the
augmented table let \(z|_{\rm base}\) be its restriction (cells without base
atoms dropped). A cell with only added atoms contributes
\(M_b^2/W_b\le\sum_{i\in b}w_it_i^2\le(1/r)\max_jt_j^2=O(1/r^3)\)
uniformly on compact \(\beta\) sets (Cauchy–Schwarz). A cell with base atoms
has mass \(\ge(1-1/r)/4\ge1/8\), receives added mass \(\le1/r\) and added
moment \(O(1/r^2)\), so \(M_b^2/W_b\) changes by \(O(1/r)\) uniformly on
compacts. Hence \(|v_{K,r}(\beta)-\max_{K'\le3}v_{K'}^{\rm base}(\beta)|=O(1/r)\)
on compacts, and the coarser maxima equal \(v_3^{\rm base}\) by refinement
monotonicity of the between value. All base-induced partitions are regular
(no subset of \(\{39,-65,31,-49\}/8\) sums to zero; verified), so each
\(V_{z|_{\rm base}}\) is coercive with a uniform constant and the singleton
bound keeps every \(\beta^*_r\) in one compact interval (measured:
\(\beta^*_r\in[-0.369,-0.366]\)). Therefore \(d_r\to d\). Likewise
\(\Phi^+_r(z)=\min_\beta V_{z,r}\to\Phi^+(z|_{\rm base})\) uniformly, and
\(\max\) over coarser base partitions is \(g^+\) by DS11(b) refinement
monotonicity, so \(g_r^+\to g^+\) and \(d_r-g_r^+\to d-g>0.68\).

**Hardening.** The family proves the *global-versus-dual* gap only;
\(p_r^+\le g_r^+\) makes the primal gap at least as large, but no convergence
of \(p_r^+\) is claimed or needed (\(p_2^+=3.17\) versus \(g_2^+=4.92\)). The
constants are large: measured \(r\cdot|d_r-d|\le12.6\), so the finite gaps
\(0.03\)–\(0.30\) at \(r\le6\) are far from the limit \(0.68\); the statement
is asymptotic, as registered.

### 7.7 DS18 strip DP

Uncentered between value and centered between value differ by the
labeling-independent \(\bar X_N^2\): \(\sum_bW_b\mu_b^2=\sum_bW_b(\mu_b-\bar X)^2+\bar X^2\).
So \(\tilde z_N\) is exactly the empirical 3-means labeling of the \(X_i\)
(verified on 12 samples and 14,805 partitions). The rest is §8.5.

### 7.8 Tier B

With \(I_z=I_4\), \(V(B)=I_{\psi\psi}-BI_{\lambda\psi}-I_{\psi\lambda}B^\top+BI_{\lambda\lambda}B^\top=I_2+BB^\top\)
(verified by direct evaluation at four \(B\)); \(\det(I_2+BB^\top)\) equals
\(17,17,25\) at the three named points, so the sublevel set
\(\{\log\det V\le\log17\}\) is not convex. Weak duality:
\(S^+_\psi(I_z)\preceq V_z(B)\) (DS11) and \(\det\) is Loewner-monotone on
PSD matrices, so \(\max_z\log\det S^+_\psi(I_z)\le\min_B\max_z\log\det V_z(B)\).

## 8. Proof, counterexample, or conditional result

### 8.1 T1 — verified

§7.1 proves \(p^+\le g^+\le d\) and \(p_{\rm reg}\le g_{\rm reg}\le g^+\le d\)
on the DS11 class, hence on DS9, with attainment. The regular filter is
load-bearing: on `centered_symmetric` (\(K=2\)) the bracket closes at
\(g^+=d=9/4\) through a *singular* DP state while \(g_{\rm reg}=0\); on
`all_nuisance_zero…` the regular class is empty and every DP state is
singular. The instrument never reports a singular DP state as a DS9 bound
(§6). **Hardening:** the statement now names zero-weight rows as excluded (a
cell of zero mass makes \(V_z\) undefined; a zero-weight row sharing a cell
is inert — verified), and names the comparison domain (collapsed atoms versus
unrestricted rows) because \(\mathcal D(\beta)\) and \(g^+\) are
domain-dependent objects (§9).

### 8.2 T2 — verified with hardened assumptions

§7.3 proves both directions without interchanging \(\max\) and \(\min\).
Exhaustive check: closure \(\Leftrightarrow\) saddle on 54/54 exact-\(d\)
tables; on the 34 closed ones every \(\Phi^+\)-maximiser was active at
\(\beta^*\) with zero derivative, and on the 20 open ones no regular labeling
was DP-active at its own normal-equation solution and no singular labeling
reached \(d\). **Hardening (H2):** the gate is set-valued; a deterministic
implementation must exhibit the concrete labeling it certifies, and an open
reported interval is not a gap certificate (`CE-DS-TILT-DUAL-TIE-MASK-001`:
362 such tables among 6,688 exhaustive integer tables at \(N\le4\)).

### 8.3 T3 — verified with hardened assumptions and widened scope

(a) Fixed tilt: the classical contiguous DP; §7.2 supplies the missing tie
lemma, so \(O(KN^2)\) rational operations hold *with* exact ties in every tie
order — the researcher's harness enumerated all tie orders, which was
unnecessary; the bound is \(O(KN)\) after sorting (prior art). The exact
gradient of the active labeling is a subgradient of \(v_K\); the two
perturbation orders give the exact one-sided derivatives. (b) Certified
\(\varepsilon\)-bracket: §7.4 makes the radius, the separation oracle, the
lower-certificate LP and the rounding discipline explicit; the claim holds in
the bit model. (c) Exact computation: the fixed-\((K,d_\lambda)\) arrangement
argument is correct as far as it goes (arrangement counts verified within
\(1+m+\binom m2\)); it is **superseded** by §7.5 — exact polynomial-bit
minimisation at \(d_\lambda=1\) for every \(K\) — and by Toledo (1993) for
fixed \(d_\lambda\ge2\), variable \(K\), in arithmetic complexity. The frozen
reduction question (EXACT-PARAMETRIC-DP) therefore narrows to: polynomial
*bit* complexity for fixed \(d_\lambda\ge2\) with variable \(K\), and any
statement for variable \(d_\lambda\). No approximate solve is called exact
anywhere in DS19; the instrument's Kelley loop is labelled a mechanism check.

### 8.4 T4 — verified with a corrected minimality statement

All registered rationals of `CE-DS-TILT-DUAL-GAP-001` reproduce from raw rows
(§6). The exact dual minimum is \(d=44729/4232\) at the rational crossing
\(\beta^*=-8/23\) of the two named quadratics (subgradient interval
\([-145/23,\,731/92]\ni0\)), so the exact gap is \(534361/781333\approx0.68391\),
marginally above the certificate \(0.68389\); the certificate is a lower
bound, as registered, not the minimum. The \(\Theta(1)\) family survives
(§7.6) as an asymptotic statement about \(d_r-g_r^+\). **Hardening (H4):**
"support-minimal" is true for \(K=3\) only. `CE-DS-TILT-DUAL-GAP-002` —
rows \((-1,0),(0,-1),(1,0)\), equal weights, \(K=2\) — has \(g^+=1/3\),
\(d=1/2\) exactly (\(\beta^*=0\), active \(\{(0,0,1),(0,1,1)\}\), mixture
\(\alpha=1/2\) gives the exact value), gap \(1/6\); it is support-minimal over
all \(K\) because \(N=3,K=2\) is the smallest exact-\(K\) problem with more
than one labeling. 884 of the 2,300 equal-weight integer tables in
\([-2,2]^2\) have a gap.

### 8.5 T5 — verified

By §7.7, \(\tilde z_N\) is the empirical 3-means labeling of the \(X_i\).
On DS18's selection-independent event \(\Omega_1\) (uniform convergence of
the empirical distortion over codebooks in \([-1,1]^3\)) every sequence of
empirical optimal codebooks converges to the unique population codebook
\((-2/3,0,2/3)\) (uniqueness: DS18.1, audited, with exact Hessian
\(\lambda_{\min}=1/6\)); an optimal empirical labeling assigns each point to
a nearest empirical centroid up to ties (else moving it improves), so the DP
cells are Voronoi intervals whose cuts, the centroid midpoints, converge to
\(\pm1/3\). On \(\Omega_2\cap\Omega_3\) the fixed-cell SLLN and bounded
scores transfer all cell masses and moments of \(\tilde z_N\) to those of
\(q^*\): \(\hat I_{\psi\lambda}(\tilde z_N)\to0\),
\(\hat I_{\lambda\lambda}(\tilde z_N)\to32/81\). The identity
\(\Delta_N=\hat I_{\psi\lambda}^2/\hat I_{\lambda\lambda}\) is the scalar
Schur formula at \(V_{\tilde z_N}(0)=\hat v_{3,N}\) (DP optimality at
\(\beta=0\)); regularity is then eventual, and \(\Delta_N\to0\). Which DS18
inequality applies: DS18.2's finite-\(N\) bound
\(P_N(z\ne q^*)\le3\Delta_N/\eta+P_N(\text{bands})\) is derived for any
labeling whose own-codebook distortion excess is at most
\(\hat v_{3,N}-\hat\Phi(z)\); for \(\tilde z_N\) that excess is \(0\le\Delta_N\),
so the bound applies verbatim with the labeling's own \(\Delta_N\). Measured:
\(\Delta_N\) from \(1.6\)–\(7.1\times10^{-2}\) at \(N=64\) to
\(1.5\)–\(6.0\times10^{-4}\) at \(N=4096\); cuts within \(0.02\) of \(\pm1/3\)
at \(N=4096\); the bound held on all 36 \((N,\text{rep},\eta)\) checks. Ties
are null (dyadic draws never equal \(\pm1/3\)). Nothing beyond the value
statement is claimed; `CE-DS-INTERVAL-SEED-UNSTABLE-001` and
`CE-DS-NONCENTERED-POPULATION-CUT-UNSTABLE-001` remain the boundary.

### 8.6 T6 — verified

§7.8, rebuilt from the raw rows. The audit adds that a **smaller** witness
exists: an uncentered 4-row, \(K=4\), \(d_\psi=d_\lambda=2\) integer table
with \(f(B_0)=115/16\), \(f(B_1)=347/16\), \(f((B_0+B_1)/2)=369/16\)
(`tierb.json`); the registered fixture remains the canonical centered,
isotropic one. Weak matrix-tilt duality held on all 680 partition/probe
checks of a 6-row table (\(\max_z\det S^+=23/108\le11/9\)).

### 8.7 T7 — verified as a decision table, with the tie-mask caveat

Every row of the table follows from T1–T6 with the hardenings above. Row (2)
must read: a nonclosed *reported* bracket reports the interval and does not
authorise "optimal"; it also does not certify a gap. Row (1) is unchanged: a
regular exhibited saddle certifies finite globality of the exhibited
labeling, and (new observation, §11) induces a deployable strip rule that
reproduces the labels away from its cut points.

## 9. Adversarial audit (`protocols/theorem.md` §G, each attack with outcome)

- **Strictness and ties.** Tilted-value ties: tie lemma (§7.2), 184 orders,
  0 dependence. DP-value ties at the dual minimiser: real and serialized
  (tie-mask fixture); the iff is unaffected, the implementation contract is
  hardened.
- **Singleton and empty cells.** Exact-\(K\) nonempty cells throughout;
  \(K=N\) has one labeling and closes (fixture 001 at \(K=4\):
  \(d=g^+=103061/9108\)); the singleton-versus-rest partition is what makes
  the radius observable. Empty cells never arise; a zero-mass cell is
  undefined and excluded.
- **Duplicate scores.** Duplicates are tied at every \(\beta\). Row-level and
  atom-level \(v_K(\beta)\) agree at all probes on the doubled fixture
  (\(K=3\le4\) atoms); \(g^+\) agrees too (\(116805/11816\)). At
  \(K=5>4\) atoms only the row level is feasible. On the 3-atom/5-row
  duplicate table, \(g^+\) and \(d\) agree at \(K=2,3\). The frozen "name the
  domain separately" stands; no exact instance of a row-level \(g^+\)
  exceeding the atom-level one was found, and none is claimed.
- **Singular information / nuisance singularity.** Handled through the DS11
  pseudo-inverse value; the audit verified the normal-equation solution set,
  null-direction invariance and the completion-of-squares identity on all
  singular partitions; 5 tables with \(g^+>g_{\rm reg}\) and one
  singular-only closure show the DS9/DS11 split is real.
- **Atomic laws.** T1–T4, T6 are finite by design. T5's law is atomless and
  its dyadic samples are tie-free.
- **Hidden compactness.** Made explicit: the coercivity radius (54/54
  minimisers inside), the quotient of \(L^\perp\) (verified: \(v_K\) constant
  along the null direction and equal to the quotient's exact \(d\)), and the
  common compact interval of the family's minimisers.
- **First-order to finite jumps.** None: the closure gate is exact, and the
  one-sided derivatives are computed, not approximated.
- **Empirical to population.** Only T5 crosses, and only on the named law
  with DS18's audited event; no held-out or population claim elsewhere.
- **Score-estimation error.** Outside every component; the umbrella's
  assumptions say so.
- **New-event extension.** §11.
- **Reparameterisation.** \(\lambda\mapsto a\lambda\): \(\Phi^+\) and \(d\)
  invariant, \(\beta^*\mapsto\beta^*/a\); \(\lambda\mapsto A\lambda\) at
  \(d_\lambda=2\): \(v'_K(\beta')=v_K(\beta'A)\) at all probes, \(\Phi^+\)
  invariant. **Bin relabeling, row ordering:** invariant. **Uniform weight
  scaling:** \(\Phi^+,V,d\) scale linearly, closure invariant.
  **Split-weight duplication:** invariant after atom collapse (above).
  **Exact-\(K\) versus \(\le K\):** \(v_K\) and \(g^+\) monotone in \(K\)
  (verified), so the exact-\(K\) convention loses nothing when \(N\ge K\).

## 10. Algorithmic consequence

- The fixed-tilt DP is the classical weighted 1-D \(k\)-means DP; ties need
  no enumeration; \(O(KN)\) after sorting.
- At \(d_\lambda=1\) the exact dual minimum and an exact certificate are
  computable in polynomial bit complexity for every \(K\) (§7.5); the
  instrument's implementation certifies with \(\le6\) probes on every
  catalogue table.
- For fixed \(d_\lambda\ge2\) the exact minimum is arithmetic-polynomial
  (Toledo); the certified \(\varepsilon\)-bracket is bit-polynomial
  (§7.4); bit-exactness stays open.
- A certified solver must return the concrete labeling it certifies and must
  not read an open interval as a gap; a second DP pass in the opposite
  perturbation order, or a check of the normal equation on every member of a
  DP tie, removes the tie mask in the cases observed.
- Nothing here selects a good primal: \(p^+<g^+\) occurs (2 catalogue tables,
  the family at \(r=2\)), and the primal side of the bracket can be far below
  the global value.

## 11. Deployability consequence

A regular exhibited saddle \((\beta^*,z^*)\) certifies \(z^*\) as a finite
global in-bin optimum, and \(z^*\) is an interval labeling of
\(T_{\beta^*}=s_\psi-\beta^*\!\cdot s_\lambda\): the strip rule
\(s\mapsto\) interval index of \(T_{\beta^*}(s)\) is an explicit score-space
quantizer that reproduces the certified labels except at exact cut ties. This
is a deployable *description* of the certified labeling, not a new theorem
about unseen events: it carries no held-out or population guarantee, and no
`src/` compile path is authorised by this audit. The compile table stands
with the tie-mask caveat; the projected efficient-score rule remains the only
unconditional compiler for its distinct problem; DS14 companions still need
every audited hypothesis; otherwise refuse.

## 12. Information-loss consequence

On the finite training table the bracket \([p_{\rm reg},d]\) (or
\([p^+,d]\)) is an exact interval for the profiled \(D_s\) value, hence an
exact interval for the train-sample retention
\(\eta_{D_s}=\Phi/\Phi_{\rm full}\); at closure it is a point. It bounds no
held-out or population retention and no direction-resolved quantity. The
exact witnesses show the interval may stay macroscopically open (relative
gap \(0.069\) on fixture 001, \(0.5\) on fixture 002), and the tie-mask
fixture shows a reported open interval may be a point in disguise. T5 adds a
population value statement for one law only.

## 13. Updated status

- `DS-TILT-DUAL-CERTIFICATE`: remains `project_proved`, **verified with
  hardened assumptions** — H1 tie lemma supplied; H2 set-valued gate and
  exhibited-labeling contract; H3 bit model of the certified bracket made
  explicit (radius, LP certificate, rounding); H5 zero-weight rows excluded
  and comparison domain named; scope **widened**: exact polynomial-bit
  minimisation at \(d_\lambda=1\) for every \(K\), fixed-\(d_\lambda\)
  variable-\(K\) arithmetic-polynomial by prior art; fixed-tilt bound
  \(O(KN)\) after sorting. New boundary fixture linked. `audit` pointer added;
  "unaudited" warning removed.
- `DS-TILT-DUAL-STRONG-DUALITY-FAILS`: remains `counterexample`, **verified
  with hardened wording** — H4: support minimality is for \(K=3\); the
  overall-minimal witness is `CE-DS-TILT-DUAL-GAP-002` (\(N=3,K=2\), gap
  \(1/6\)); exact \(d\) of fixture 001 recorded; the family is a
  global-versus-dual asymptotic statement.
- `DS-STRIP-DP-DELTA-CONSISTENCY`: remains `project_proved`, **verified**;
  assumptions gain the centering identity and the exact statement of which
  DS18 inequality applies.
- `DS-MATRIX-TILT-NONQUASICONVEX`: remains `counterexample`, **verified**; a
  smaller uncentered witness is recorded in the artifact, the fixture is
  unchanged.
- `DS-PROFILED-COMPILE-CERTIFICATE`: remains `project_proved`; DS19 clauses
  **verified** with the row-(2) tie-mask caveat; warning updated (DS19 now
  audited; still no compile authorisation).
- `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`: remains `project_proved` and
  **reduced**, with the reduction narrowed: the only unresolved assumption is
  exact polynomial-*bit* minimisation for fixed \(d_\lambda\ge2\) with
  variable \(K\), and any exact statement for variable \(d_\lambda\).
- `OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY`: remains `open`, statement narrowed
  accordingly; `Toledo-1993`, `Megiddo-1983`, `Carstensen-1983` linked.
- `AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER`: new node, `project_proved`.
- No inherited node is downgraded. DS11's and DS18's registered scopes were
  found sufficient for DS19's uses.

**Verdict: verified with hardened assumptions (Tier A), verified (Tier B and
T5), umbrella reduced to the narrowed OP31 remainder.**

## 14. Registry patch

`claims/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER.json` is new with this report as
`proof_location`, the instrument as `artifact`, and all six audited nodes plus
`OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY` among its dependencies. The six audited
nodes gain `audit` pointers, the hardened `assumptions` of §13, rewritten
`warning`s, the two new fixtures in `boundary_counterexamples`/`counterexamples`,
and the new literature keys. `KNOWN_RESULTS/05b-ds-bridge.md` §DS19 carries an
audit banner, the tie lemma, the exact-computation widening, the corrected
minimality, and the tie-mask caveat. `OPEN_PROBLEMS.md` (P1 block, OP31),
`manuscripts/README.md`, `COUNTEREXAMPLES/README.md`, `NUMERICAL_EVIDENCE.md`
and `LITERATURE/` are synchronised.

## 15. Counterexample and regression artifacts

**`CE-DS-TILT-DUAL-GAP-002` — support-minimal tilt-dual gap.**
Rows \((-1,0),(0,-1),(1,0)\), weights \(1/3\), \(K=2\). Labelings and values:
\((0,0,1)\!:\Phi=1/3\), \((0,1,1)\!:\Phi=1/3\), \((0,1,0)\!:\Phi=0\), all
regular; quadratics \(\tfrac16\beta^2\mp\tfrac13\beta+\tfrac12\) and
\(\tfrac13\beta^2\). At \(\beta^*=0\): \(v_2(0)=1/2\) (split \(\{-1\},\{0,1\}\)),
active set \(\{(0,0,1),(0,1,1)\}\) with derivatives \(\mp1/3\), so
\(0\in\partial v_2(0)\) and \(d=1/2\) exactly; the mixture \(\alpha=1/2\) is
\(\tfrac16\beta^2+\tfrac12\ge\tfrac12\), a fully rational proof. Gap
\(d-g^+=1/6\). Minimal: \(N=2\) or \(K=N\) admits a single labeling.

**`CE-DS-TILT-DUAL-TIE-MASK-001` — closed bracket hidden by a DP tie.**
Rows \((-1,-1),(0,-2),(0,0)\), weights \(1/3\), \(K=2\), all three
labelings regular. \(g^+=2/9=d\) at \(\beta^*=1/3\), where the tilted values
\((-2/3,2/3,0)\) are pairwise distinct; \(\mathcal D(\beta^*)=\{(0,1,0),(0,1,1)\}\)
with derivatives \(2/3\) and \(0\). Only \((0,1,1)\) (\(\Phi=2/9\)) closes;
\((0,1,0)\) has \(\Phi=4/27\). The right-perturbation DP returns \((0,1,0)\)
and would report the open interval \([4/27,2/9]\); the left-perturbation DP
returns the saddle. A singular-only sibling \((-1,-1),(0,0),(0,1)\) with
\(g^+=d=1/6\) at \(\beta^*=2/3\) is recorded in the fixture's search block.

**Independent instrument and artifacts.** `py/audit_ds_practical_certified_solver.py`
(stages `witness`, `ceiling`, `saddle`, `ties`, `compute`, `family`, `ds18`,
`tierb`, `invariances`, `fixtures`) and the ten provenance-stamped JSON files
under `AUDITS/artifacts/AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER-001/`.

**Regressions in `tests/test_research_claims.py`** (all recompute from raw
data, never from copied constants):
`test_ds19_audit_exact_dual_minimum_of_gap_witness`,
`test_ds19_audit_support_minimal_gap_fixture_002`,
`test_ds19_audit_tie_masked_closure_fixture`,
`test_ds19_audit_weak_ceiling_and_domain_split_on_adversarial_tables`,
`test_ds19_audit_saddle_closure_iff_on_small_tables`,
`test_ds19_audit_tie_order_independence_and_one_sided_derivatives`,
`test_ds19_audit_ds18_strip_dp_delta_chain_on_seeded_sample`,
`test_ds19_audit_matrix_tilt_midpoint_violation_by_direct_evaluation`.

## 16. Next dependency-blocking question

DS19 is verified and hardened, so the packet's first branch applies: does
`OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY` admit an exact **polynomial-bit**
algorithm for fixed \(d_\lambda\ge2\) with variable \(K\) — for instance by
carrying a root-separation bound for the conic breakpoint arrangement through
Toledo's fixed-dimension parametric search — and is the variable-\(d_\lambda\)
problem hard, or does the same machinery extend? Independently of that
academic question, the deployment-facing blocker is unchanged from DS18/DS19:
a *selection* theorem (which certified or \(\Delta\)-consistent labeling does
a practical solver return, and when does it inherit exchange stability), since
the audit confirms that the primal side of the bracket can sit far below the
global value and that an open reported bracket carries no information about
the gap.
