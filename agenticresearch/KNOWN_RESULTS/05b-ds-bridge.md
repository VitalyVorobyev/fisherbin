# 5. \(D_s\)-optimality — finite-to-population bridge

> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and
> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.
> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.

**Notation** (from DS0 in `05a-ds-core.md`, repeated so this file reads standalone).

Let \(\theta=(\psi,\lambda)\) and

\[
F_s(I)
=\log\det S_\psi(I)
=\log\det I-\log\det I_{\lambda\lambda}
\]

in the nonsingular block regime.

## DS11. Variational form of the profiled objective and \(\Phi\)-neutral splits — [BRIDGE core + PROJECT-PROVED consequences; audited]

**Claims:** DS-GLOBAL-TIE-DEGENERACY, DS-PROFILED-VARIATIONAL, OPEN-DS-DOMINATION-EQUALITY

**Audit (28 Aug 2026, `AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md`):** the boxed
identity is classical — it is the extremal characterization of the generalized
Schur complement (Krein 1947; Anderson's shorted operator 1971; Li–Mathias,
SIAM Review 42(2), 2000, Thm 2.2, including the Loewner order, the
pseudo-inverse, and the exact attainment set). The statistical reading
\(V(B)=\operatorname{Var}(E[S_\psi-BS_\lambda\mid Z])\) additionally requires
**centered scores** (\(E[S]=0\)). The binned transfer and consequences (a)–(d)
are project-level.

For any partition with binned information blocks
\(I_{\psi\psi},I_{\psi\lambda},I_{\lambda\lambda}\) define the **generalized
profiled information**
\(S_\psi^+(I)=I_{\psi\psi}-I_{\psi\lambda}I_{\lambda\lambda}^+I_{\lambda\psi}\)
(Moore–Penrose pseudo-inverse; the ordinary Schur complement when
\(I_{\lambda\lambda}\succ0\)). Then

\[
\boxed{
S_\psi^+(I_q)
=\min_B\operatorname{Var}\!\bigl(E[S_\psi-BS_\lambda\mid Z]\bigr)
=\min_B\sum_bW_b(\mu_{b\psi}-B\mu_{b\lambda})(\mu_{b\psi}-B\mu_{b\lambda})^\top,
}
\]

a Loewner minimum over \(d_\psi\times d_\lambda\) matrices \(B\), attained at
every solution of \(BI_{\lambda\lambda}=I_{\psi\lambda}\) (in particular
\(B_q^*=I_{\psi\lambda}I_{\lambda\lambda}^+\); solutions exist because
\(\operatorname{range}(I_{\lambda\psi})\subseteq\operatorname{range}(I_{\lambda\lambda})\)
for a PSD block matrix).

*Proof.* \(V(B)=I_{\psi\psi}-BI_{\lambda\psi}-I_{\psi\lambda}B^\top
+BI_{\lambda\lambda}B^\top\); for any normal-equation solution \(B_0\),
completion of squares gives
\(V(B)=V(B_0)+(B-B_0)I_{\lambda\lambda}(B-B_0)^\top\succeq V(B_0)\), and
\(V(B_0)=S_\psi^+(I)\). ∎

Consequences.

**(a) Efficient-score domination, singular extension, and the exact equality
condition (OP6, fixed \(q\)).** Evaluating at \(B=B^*_{\rm full}\)
re-derives DS7 in one line, extends it to singular binned nuisance blocks, and
gives the exact gap

\[
\boxed{
\operatorname{Var}(E[\widehat S\mid q])-S_\psi^+(I_q)
=(B^*_{\rm full}-B^*_q)\,I^q_{\lambda\lambda}\,(B^*_{\rm full}-B^*_q)^\top
\succeq0 .
}
\]

Equality for a fixed \(q\) holds **iff**
\((B^*_{\rm full}-B^*_q)I^q_{\lambda\lambda}=0\): the full-data nuisance
projection is already optimal for the binned centroids. The finite-\(K\) gap is
therefore exactly the cost of estimating the nuisance projection from bins.
Along any refining sequence of partitions generating the Borel
\(\sigma\)-field, \(E[S\mid Z_K]\to S\) in \(L^2\) (Lévy upward martingale
convergence), so \(I_{q_K}\to I_{\rm full}\); **provided
\(I^{\rm full}_{\lambda\lambda}\succ0\)** (implicit in defining \(\widehat S\)),
the binned nuisance blocks are eventually nonsingular, where
\(B\mapsto I_{\psi\lambda}I_{\lambda\lambda}^{-1}\) is continuous, so
\(B^*_{q_K}\to B^*_{\rm full}\) and the gap vanishes — the \(K\to\infty\) part
of OP6. (The pseudo-inverse map is discontinuous at rank drops — witness
\(I_{\lambda\lambda}^{(k)}=\mathrm{diag}(1,1/k)\), \(I_{\psi\lambda}=[1,1]\),
\(B^*_k=[1,k]\) — so the nonsingular-limit hypothesis is load-bearing; audit
§8.) The behavior at global optima was OP28 and is now settled by DS15 for
conditionally centered laws at \(d_\psi=d_\lambda=1\): the gap is the
projection tax and vanishes a.s. along free global optima (DS15 conclusion 5);
beyond that class it is OP29.

**(b) Refinement monotonicity with exact equality characterization
(\(d_\psi=1\)).** Splitting cell \(M\) into \((x,y)\): for every slope \(c\),
with \(e_b(c)=\mu_{b\psi}-c\,\mu_{b\lambda}\),

\[
V(c;\text{split})=V(c;\text{merged})
+\frac{W_xW_y}{W_M}\bigl(e_x(c)-e_y(c)\bigr)^2 .
\]

Hence \(S_\psi^+\) never decreases under refinement, and the split is
**profiled-information-neutral iff some \(c\) simultaneously minimizes
\(V(\cdot;\text{merged}) \) and equalizes \(e_x(c)=e_y(c)\)**. (Audit: the
identity is the exact between-group variance decomposition; the "iff" holds by
evaluating at a minimizer of the split problem, which exists by the
normal-equation argument. **The same statement and proof hold for every
\(d_\psi\ge1\)** with the rank-one PSD gap
\(\frac{W_xW_y}{W_M}(e_x(B)-e_y(B))(e_x(B)-e_y(B))^\top\) and Loewner
sandwiching — the form DS14's merged variant consumes; audit §8.)

**(c) Wasted cells and exact global ties.** If the merged **configuration** is
entirely nuisance-degenerate (all cells have \(\mu_{b\lambda}=0\), so
\(V(\cdot;\text{merged})\) is constant and every slope minimizes it), every
split whose sub-cells have distinct nuisance means is exactly neutral, while a
split with equal (hence zero) nuisance means and distinct POI means strictly
increases \(S_\psi^+\) but keeps the nuisance block singular — it leaves the
in-bin formulation (DS9). (Audit hardening: the neutrality argument needs the
minimizer set of \(V(\cdot;\text{merged})\) to meet the equalizing slopes;
full nuisance degeneracy supplies that, a partially degenerate configuration
need not.) Exact witnesses:

- `COUNTEREXAMPLES/CE-DS-DEGENERATE-GLOBAL-TIE-001.json`: a centered
  equal-weight \(N=8,d=2,d_\psi=1,K=3\) sample whose exact global in-bin
  optimum \(1083/4096\) is attained by **31 distinct labelings** — exactly the
  feasible refinements of one reduced bipartition — every one of which has two
  exactly coincident projected centroids; the unique nuisance-mean-equal
  refinement is infeasible (singular nuisance block) with generalized value
  \(1191/4096>1083/4096\).
- `COUNTEREXAMPLES/CE-DS-POP-WASTED-CELLS-001.json`: the population/quadrature
  wasted-cell construction of DS12.

**(d) Identifiability up to neutral splits.** The profiled objective is
invariant under \(\Phi\)-neutral splits, so a finite global optimum is in
general identified only up to the reduced configuration of projected centroids
\(\{(W_b,e_b(B^*_q))\}\); deployable content lives at the reduced level.

## DS12. Population stationary geometry for profiled \(D_s\) — [PROJECT-PROVED]

**Claims:** DS-POP-WASTED-CELLS, OPEN-DS-POP-COMMON-METRIC

Let \(P\) be atomless with \(E[S]=0\), \(E\|S\|^2<\infty\), and let \(q\) have
\(W_b>0\) for all \(b\) and \(I_q\succ0\). Call \(q\) **bounded-packet
stationary** if for every \(a\ne b\) and every \(R>0\),

\[
\limsup_{\substack{E\subseteq A_a\cap B(0,R)\\ P(E)\to0}}
\frac{\Phi_{D_s}(q_{E\to b})-\Phi_{D_s}(q)}{P(E)}\le0,
\]

where \(q_{E\to b}\) relabels the measurable set \(E\) to cell \(b\). (Any
local maximizer over small-mass bounded relocations is bounded-packet
stationary.)

**Packet dictionary.** \(I_q\) depends on the partition only through
\((W_b,m_b)\), so relabeling a set \(E\) with mass \(\varepsilon=P(E)\) and
barycenter \(\bar s=\frac1\varepsilon\int_ES\,dP\) changes \(I_q\) **exactly**
as the finite rank-two relocation D2 of the weighted point
\((\bar s,\varepsilon)\):
\(\Delta I=\alpha u_au_a^\top-\beta u_bu_b^\top\), \(u_x=\bar s-\mu_x\),
\(\alpha=\varepsilon W_a/(W_a-\varepsilon)\),
\(\beta=\varepsilon W_b/(W_b+\varepsilon)\). All finite relocation algebra
transfers verbatim to population packets.

**Theorem.** \(q\) is bounded-packet stationary **iff** for every \(a\),
\(P\)-a.e. \(s\in A_a\) and every \(b\):

\[
\boxed{
(s-\mu_a)^\top G_s(s-\mu_a)\le(s-\mu_b)^\top G_s(s-\mu_b),
\qquad
G_s=I_q^{-1}-E_\lambda(I_q)_{\lambda\lambda}^{-1}E_\lambda^\top .
}
\]

Moreover \(G_s=C^\top S_\psi(I_q)^{-1}C\) with \(C=[\,\mathrm{Id}_{d_\psi},
-B^*_q\,]\), so the rule reads: assign a.e. to the nearest projected centroid
\(e_b=C\mu_b\) of the efficient projection \(e(s)=Cs\) in the
\(S_\psi(I_q)^{-1}\) metric,

\[
q(s)\in\arg\min_b\,(e(s)-e_b)^\top S_\psi(I_q)^{-1}(e(s)-e_b)
\quad\text{a.e.}
\]

*Proof.* The pairwise first-variation function
\(\delta_{ab}(s)=(s-\mu_a)^\top G_s(s-\mu_a)-(s-\mu_b)^\top G_s(s-\mu_b)
=2(\mu_b-\mu_a)^\top G_ss+\mu_a^\top G_s\mu_a-\mu_b^\top G_s\mu_b\)
is **affine** in \(s\) (the quadratic terms cancel; this is G1's common-\(G\)
affinity). \(\Phi_{D_s}=F(I)\) with \(F=\log\det S_\psi\) is \(C^2\) on a
neighborhood of \(I_q\succ0\) with \(\nabla F(I_q)=G_s\) (DS2), so for a
packet with bounded barycenter the exact update gives
\(\Phi(q_{E\to b})-\Phi(q)=P(E)\,\delta_{ab}(\bar s)+O(P(E)^2)\), with the
remainder uniform over \(\bar s\in B(0,R)\).

(⟹) If \(V=\{s\in A_a:\delta_{ab}(s)\ge c\}\cap B(0,R)\) had \(P(V)>0\) for
some \(c>0\), atomlessness supplies packets \(E_n\subseteq V\) with
\(P(E_n)\to0\); affinity gives \(\delta_{ab}(\bar s_n)\ge c\) (the barycenter
average of an affine function), so the gain per unit mass is at least
\(c-O(P(E_n))>0\), contradicting stationarity.

(⟸) For any packet \(E\subseteq A_a\cap B(0,R)\), affinity gives
\(\delta_{ab}(\bar s_E)=\frac1{P(E)}\int_E\delta_{ab}\,dP\le0\), so the gain is
\(\le O(P(E)^2)\) and the limsup is \(\le0\). ∎

The factorization \(G_s=C^\top S_\psi^{-1}C\) follows from the block inverse:
\((I^{-1})_{\psi\psi}=S_\psi^{-1}\), \((I^{-1})_{\psi\lambda}=-S_\psi^{-1}B^*_q\),
\((I^{-1})_{\lambda\lambda}=I_{\lambda\lambda}^{-1}+B_q^{*\top}S_\psi^{-1}B^*_q\).

**Deployability characterization (OP5).** The nearest-projected-centroid
**correspondence** is \(P\)-a.e. single-valued and reproduces \(q\) up to null
sets **iff** (i) the projected centroids \(e_b\) are pairwise distinct and
(ii) \(P\) charges no pairwise tie hyperplane (each tie set is affine in
\(e(s)\); both conditions hold e.g. when \(P\) is absolutely continuous and
(i) holds). (Audit hardening: the selection-independent reading is the correct
one — a tie-breaking *selection* could reproduce \(q\) even when (ii) fails,
so the characterization is about the rule being determined by the geometry
alone; audit §8. Note also the asymmetry: sufficiency (⟸) of the stationarity
theorem above holds for every \(P\), while necessity (⟹) genuinely needs
atomlessness — for a finitely atomic law bounded-packet stationarity is
vacuous and `CE-DS-GLOBAL-GEOMETRY-001` violates the rule.) Stationarity
does **not** force (i): `CE-DS-POP-WASTED-CELLS-001` is a stationary partition
(zero violations, ties allowed) whose coincident-centroid cell pairs no
efficient-semimetric rule can separate — in sharp contrast to finite D, where
exchange stability forces distinct centroids (D5). Without (i), stationarity
constrains exactly the **reduced** partition obtained by merging
coincident-\(e_b\) groups (cf. DS11(d)).

## DS13. Exact profiled leverage stability bound — [PROJECT-PROVED]

**Claims:** DS-EXCHANGE-LEVERAGE-BOUND

Finite level, positive weights, nonsingular \(I\) and \(I_{\lambda\lambda}\)
at the current state. (Audit: merged atoms are **not** needed — the proof never
uses row distinctness, confirmed exhaustively on unmerged-duplicate configs;
the operative hypotheses are positive weights and a non-singleton source with
positive co-weight, \(W_a>w_i\).) At any one-point exchange-stable
profiled-\(D_s\) state, for every point \((s_i,w_i)\) in a non-singleton cell
\(a\) and every \(b\ne a\):

\[
\boxed{
s_{aa}-s_{bb}\le\beta_i\,q_{aa}q_{bb}\le w_i\,q_{aa}q_{bb},
\qquad
\beta_i=\frac{w_iW_b}{W_b+w_i},
}
\]

with \(s_{xx}=u_x^\top G_su_x\), \(q_{xx}=u_x^\top I^{-1}u_x\),
\(u_x=s_i-\mu_x\).

*Proof.* By the exact rank-two determinant ratios (D3 applied to \(I\) and to
\(I_{\lambda\lambda}\)), the exact profiled gain of the move satisfies
\(\Delta F_s\le0\) iff

\[
(1+\alpha q_{aa})(1-\beta q_{bb})+\alpha\beta q_{ab}^2
\le
(1+\alpha r_{aa})(1-\beta r_{bb})+\alpha\beta r_{ab}^2,
\]

where \(r_{xy}=u_{x\lambda}^\top I_{\lambda\lambda}^{-1}u_{y\lambda}\).
Expanding and using \(s_{xx}=q_{xx}-r_{xx}\):

\[
\alpha s_{aa}-\beta s_{bb}
\le\alpha\beta\bigl[(q_{aa}q_{bb}-q_{ab}^2)-(r_{aa}r_{bb}-r_{ab}^2)\bigr]
\le\alpha\beta\,q_{aa}q_{bb},
\]

dropping \(q_{ab}^2\ge0\) and the Cauchy–Schwarz-nonnegative
\(r_{aa}r_{bb}-r_{ab}^2\). Since \(\beta\le w_i\le\alpha\) and
\(s_{bb}\ge0\) (\(G_s\succeq0\)), divide by \(\alpha\) and use
\(\beta/\alpha\le1\). Degenerate post-move states: if \(I'_{\lambda\lambda}\)
is singular then so is \(I'\) (Fischer,
\(\det I'\le\det I'_{\psi\psi}\det I'_{\lambda\lambda}\)); in either singular
case both determinant-ratio formulas take their true values with the left one
zero, the displayed inequality holds **without any stability input**, and the
expansion proceeds unchanged — so the bound also covers moves whose
destination state is infeasible. ∎

Complements DS6: the leverage form needs **no balancedness or mass margin**;
tiny or ill-conditioned cells surface through the leverage factors
\(q_{aa}q_{bb}\) instead. It is the finite half of the DS14 bridge.
Exact-arithmetic regressions: 2,706 admissible moves at 110 float-screened,
exactly re-ranked global optima plus 32 moves on both canonical fixtures, zero
violations (`NUMERICAL_EVIDENCE.md` row N-DS-LEVERAGE); independently, the
audit's exhaustive enumeration checked 1,748 admissible moves at all 171
exchange-stable states of five adversarial datasets — vector nuisance, vector
POI, unmerged duplicates, unequal weights, 230 singular-destination moves —
with zero violations (row N-DS-AUDIT-LEVERAGE,
`tests/test_research_claims.py::test_ds13_leverage_bound_at_every_stable_state_with_vector_nuisance`).

## DS14. Conditional finite\(\to\)population \(D_s\) bridge — [PROJECT-PROVED, CONDITIONAL]

**Claims:** OPEN-DS-FINITE-POP-BRIDGE

Let \(S_1,\dots,S_N\) be i.i.d. from \(P\) with equal weights, and let
\(z^{(N)}\) be one-point exchange-stable finite \(D_s\) labelings into \(K\)
cells. Write \(\hat I_N\), \(\hat\mu_b\), \(\hat G_s\), \(\hat e_b\) for the
labeling's own binned quantities and let the **companion rule** \(\rho_N\) be
the efficient-semimetric nearest-cell rule built from them
(\(\rho_N(s)=\arg\min_b(\hat e(s)-\hat e_b)^\top S_\psi(\hat
I_N)^{-1}(\hat e(s)-\hat e_b)\)).

**Assumptions.**

- (M1) \(P\) atomless, \(E[S]=0\), \(E\|S\|^2<\infty\);
- (M2) mass margin: \(\min_b\hat W_b\ge c_0>0\);
- (M3) conditioning margin: \(\lambda_{\min}(\hat I_N)\ge\kappa>0\);
- (M4) slab margin: \(\sup_{\|v\|=1,c}P(|v^\top S-c|\le t)\le\varphi(t)\),
  \(\varphi(t)\downarrow0\);
- (M5) projected-centroid separation:
  \(\min_{b\ne b'}\|\hat e_b-\hat e_{b'}\|\ge\gamma>0\);

(M2)/(M3)/(M5) along the sequence, almost surely eventually.

**Theorem.** Almost surely:

1. **(Geometrization.)** \(P_N(z^{(N)}\ne\rho_N)\to0\): the labeling
   disagrees with its own companion rule on a vanishing fraction of the
   sample.
2. **(Subsequential population stationarity.)** Along any subsequence with
   converging rule parameters, \(\rho_N\to q^*\) \(P\)-a.e., where \(q^*\) is
   a **self-consistent** population efficient-Voronoi quantizer — by DS12
   exactly a bounded-packet stationary population quantizer — and
   \(\hat I_N(z^{(N)})\to I_{q^*}\),
   \(\hat\Phi_s(z^{(N)})\to\Phi_s^{\rm pop}(q^*)\).
3. **(Global variant.)** If each \(z^{(N)}\) is a global finite \(D_s\)
   optimum, then \(\hat\Phi_s(z^{(N)})\to v^*=\sup\{\Phi_s^{\rm pop}(\rho)\}\)
   over the compact class of efficient-Voronoi rules compatible with the
   margins \((c_0,\kappa,\gamma)\), and every subsequential limit \(q^*\)
   attains \(v^*\).

*Proof.*

**Step 1 (finite near-geometry).** By DS13, every misassigned point (positive
rule violation \(g_i=s_{aa}-s_{b^*b^*}>0\)) satisfies
\(g_i\le\frac1N q_{aa}q_{b^*b^*}\). Under (M2)–(M3),
\(\|\hat\mu_b\|^2\le M_N/c_0\) with \(M_N=P_N\|S\|^2\to M=E\|S\|^2\), so
\(q_{xx}\le\frac2\kappa(\|s_i\|^2+M_N/c_0)=:Q_i\) and \(g_i\le Q_i^2/N\).
Hence for any \(t>0\), a misassigned point has either violation gap
\(\le t\) or \(\|s_i\|^2\ge\sqrt{tN}\,\kappa/2-M_N/c_0\); Markov's inequality
gives

\[
P_N(z^{(N)}\ne\rho_N)
\le P_N(0<\mathrm{gap}\le t)+
\frac{M_N}{\sqrt{tN}\,\kappa/2-M_N/c_0}.
\]

**Step 2 (band mass).** Pairwise decision functions
\(h_{bb'}(s)\) are affine in \(s\) with normals
\(v_{bb'}=2C_N^\top S_\psi(\hat I_N)^{-1}(\hat e_b-\hat e_{b'})\); since
\(\|C_N^\top w\|\ge\|w\|\) and \(\kappa\preceq S_\psi(\hat I_N)\preceq\Lambda\)
— where \(\Lambda:=2M\) is **derived**, not assumed:
\(\lambda_{\max}(S_\psi(\hat I_N))\le\operatorname{tr}\hat I_N
=\sum_b\hat W_b\|\hat\mu_b\|^2\le M_N\to M\) a.s., and the lower bound is
\(S_\psi=((\hat I_N^{-1})_{\psi\psi})^{-1}\succeq\lambda_{\min}(\hat I_N)\)
(audit §8) — (M5) gives \(\|v_{bb'}\|\ge2\gamma/\Lambda\). The empirical
gap-\(t\) band, whatever its data-dependent normals, lies in \(\binom K2\)
members of the **fixed** family \(\mathcal S=\{\{s:|v^\top s-c|\le r\}\}\) of
all slabs of half-width \(r=t\Lambda/(2\gamma)\); \(\mathcal S\) is a VC class
(intersections of two half-spaces), so
\(\sup_{\mathcal S}|P_N-P|\to0\) a.s. (VC Glivenko–Cantelli; van der
Vaart–Wellner Thm 2.4.3 / Pollard 1984), and (M4) — already uniform over all
\((v,c)\) — bounds every population slab mass, giving
\(\limsup_NP_N(0<\mathrm{gap}\le t)\le\binom K2\varphi(t\Lambda/(2\gamma))\).
Sending \(N\to\infty\) then \(t\downarrow0\) in Step 1 proves conclusion 1.
(Audit: the uniform law must run over the fixed class, never the
data-dependent slabs; this is the repair recorded in §8 of the audit.)

**Step 3 (moment identification).** \(|\hat W_b(z^{(N)})-\hat W_b(\rho_N)|\le
P_N(z\ne\rho)\to0\) and \(\|\hat m_b(z^{(N)})-\hat m_b(\rho_N)\|\le
M_N^{1/2}P_N(z\ne\rho)^{1/2}\to0\) (Cauchy–Schwarz). The companion rules lie
in the compact affine-max class with parameters bounded by
\((c_0,\kappa,\gamma,M)\); by the C1 uniform moment convergence over that
class, \(\sup_\rho\|\hat m_b(\rho)-m_b^P(\rho)\|\to0\) and likewise for
masses. Along a subsequence with converging parameters, dominated convergence
(tie sets are \(P\)-null by (M4)–(M5)) gives \(\rho_N\to q^*\) a.e. and
population moments converge; chaining the three approximations identifies
\(\lim\hat W_b(z^{(N)})=W_b^P(q^*)\), \(\lim\hat\mu_b(z^{(N)})=\mu_b^P(q^*)\),
\(\lim\hat I_N=I_{q^*}\succeq\kappa\).

**Step 4 (self-consistency and stationarity).** The rule \(q^*\) is built
from the limit centroids and the limit metric, which Step 3 identifies as the
population centroids and metric **of \(q^*\) itself**; hence \(q^*\) is a
self-consistent efficient-Voronoi quantizer, and by the DS12 equivalence it is
bounded-packet stationary. Continuity of \(F\) at \(I_{q^*}\succ0\) gives
\(\hat\Phi_s(z^{(N)})=F(\hat I_N)\to F(I_{q^*})\) — conclusion 2.

**Step 5 (global sandwich).** For any fixed margin-compatible rule \(\rho\),
the sample labeling induced by \(\rho\) is feasible (nonempty cells a.s.
eventually), so \(\hat\Phi_s(z^{(N)})\ge\hat\Phi_s(\rho\text{-labels})\to
\Phi_s^{\rm pop}(\rho)\); hence \(\liminf\hat\Phi_s(z^{(N)})\ge v^*\). Along
any parameter-convergent subsequence, Step 4 gives
\(\hat\Phi_s(z^{(N)})\to\Phi_s^{\rm pop}(q^*)\le v^*\) because \(q^*\)
inherits the margins. Both bounds force
\(\lim\hat\Phi_s(z^{(N)})=v^*=\Phi_s^{\rm pop}(q^*)\). ∎

**Merged-rule variant (dropping (M5)).** Without a separation margin, pass to
a subsequence along which every pairwise separation converges; merge
cell pairs whose separation vanishes (a genuine equivalence relation by the
triangle inequality). Steps 1–2 apply verbatim to the
**merged** companion rule (a group-level misassignment is in particular a
cross-group cell-level one, so DS13 supplies the same gap bound; only
inter-group boundaries carry slabs, and their normals are bounded below along
the subsequence), and Steps 3–5 deliver a population-stationary **reduced**
rule (DS11(d), DS12). The value identification uses the general-\(d_\psi\)
form of DS11(b): within a group the fine rule's own \(B^*(\hat I_N)\)
equalizes projected centroids in the limit, so the limit fine and merged
configurations have exactly equal profiled information (audit §8). This is
sharp:
`CE-DS-DEGENERATE-GLOBAL-TIE-001` shows exact finite global optima whose
label-level structure is not identified (31-fold exact tie), while the reduced
configuration is unique.

**Audit (28 Aug 2026).** The theorem passed the publication-grade audit
(`AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md`) as a conditional result: all five
steps were independently re-derived, with the fixed-class slab
Glivenko–Cantelli argument, the derived \(\Lambda\), the explicit compact
parameter set for Steps 3/5, the two-sided Step-4 fixed-point identification,
and the merged-variant value argument supplied. The audit also notes a free
strengthening: in conclusion 3 the comparison class may be broadened to all
geometric rules with positive masses, distinct centroids, and nonsingular
information — the margins bind only through the hypotheses on \(z^{(N)}\).

**What is deliberately not claimed.** (i) The margins (M2)/(M3)/(M5) are
**not** automatic at finite optima — and DS15 (29 Aug 2026) settles how, for
conditionally centered laws at \(d_\psi=1\): (M2) *is* automatic
asymptotically (the \(N\le18\) singleton evidence is pre-asymptotic), but
(M3) provably **fails** at free global optima, whose limits are
nuisance-degenerate efficient-score interval quantizers. On that class DS14
therefore governs margin-certified solutions — necessarily suboptimal by
\(\delta(\kappa)=v_K-v^*(\kappa)>0\) — never free global optima; beyond the
class the margins remain open (OP29). (ii) \(v^*\) is the optimum over the
margin-compatible geometric class; DS15 shows it sits *strictly below* the
unrestricted population supremum \(v_K\) on the conditionally centered class,
where \(v_K\) is attained only degenerately; the general attainment question
remains C2. (iii) Everything is for exact scores; estimated-score robustness
is the P2 programme.

---
## DS15. Margins dichotomy at global finite \(D_s\) optima — [PROJECT-PROVED for conditionally centered laws, \(d_\lambda=1\); audited]

**Claims:** OPEN-DS-MARGINS-AT-OPTIMA

**Audit (30 Aug 2026, `AUDITS/AUDIT-DS-MARGINS-AT-OPTIMA-001.md`):** verified
with hardened assumptions. The originally registered generality — arbitrary
\(d_\lambda\) under the bare cardinality assumption \(K\ge3\) — is **false**:
for \(K=d_\lambda+1\) exact centering forces
\(\operatorname{rank}(I_z)\le K-1\), so every feasible labeling has profiled
value exactly \(0\) while \(v_K>0\)
(`COUNTEREXAMPLES/CE-DS-MARGINS-RANK-VACUITY-001.json`). The theorem below is
therefore stated for \(d_\lambda=1\), where \(K\ge3\) is exactly
\(K\ge d_\lambda+2\); the \(d_\lambda\ge2\), \(K\ge d_\lambda+2\) branch is
open (Proposition 6's steering is one-dimensional in the nuisance). The audit
supplied the previously missing pieces of Propositions 5–6 and replaced the
misattributed Glivenko–Cantelli import in the proof of conclusion (3); see
the audit report §8.

Setting: \(S=(S_\psi,S_\lambda)\sim P\) on \(\mathbb R^{2}\)
(\(d_\psi=d_\lambda=1\); general \(d_\psi\) and general \(d_\lambda\) are
discussed at the end), \(E S=0\),
\(E\|S\|^2<\infty\), full information \(I=E[SS^\top]\succ0\). Efficient score
\(\hat s=S_\psi-B^*S_\lambda\), \(B^*=I_{\psi\lambda}I_{\lambda\lambda}^{-1}\),
\(\sigma_s^2=E[\hat s^2]=S_\psi(I)\). All second moments are uncentered about
the origin (empirical scores exactly centered, as everywhere in this chapter).

**Law class.**

- **(L) conditional centering:** \(E[S_\lambda\mid\hat s]=0\) a.s. Since
  \(\operatorname{Cov}(\hat s,S_\lambda)=0\) always, (L) upgrades
  uncorrelatedness to mean-independence. It holds for jointly Gaussian scores,
  for every elliptical law with finite second moments (conditional means are
  linear), and more generally whenever the regression of the nuisance score on
  the efficient score vanishes.
- **(S) scalar regularity:** \(\operatorname{law}(\hat s)\) is atomless with a
  positive density near the optimal cell boundaries, and the optimal \(K\)-point
  quantizer of \(\operatorname{law}(\hat s)\) under squared error is unique
  (strict log-concavity suffices — Gaussian in particular; see the OP28
  literature audit for the uniqueness citations).
- **(R) swap richness:** for some \(0<\ell<L\),
  \(P(S_\lambda\in[\ell,L]\mid \hat s)\) and \(P(S_\lambda\in[-L,-\ell]\mid\hat s)\)
  are bounded below near the optimal boundaries (automatic for Gaussian, where
  \(S_\lambda\perp\hat s\)).

Scalar quantities: \(W_K\) = optimal \(K\)-cell SSE of
\(\operatorname{law}(\hat s)\), \(v_K=\sigma_s^2-W_K\), \(J^*\) its optimal
interval partition, with masses \(w_b^*>0\) and distinct centroids \(c_b^*\).

For a quantizer \(q\) (or finite labeling \(z\)): \(W_b\), moments
\(m_b=E[S1_{q=b}]\), \(I_q=\sum_b m_bm_b^\top/W_b\), profiled value
\(\Phi(q)=S_\psi^+(I_q)\) in the DS11 pseudo-inverse extension
(\(=\) the in-bin Schur value whenever \(I_{q,\lambda\lambda}\succ0\)).

### Theorem (dichotomy)

Let \(z^{(N)}\) be exact global finite \(D_s\) optima of i.i.d. samples from
\(P\) satisfying (L)+(S)+(R), over feasible \(K\)-cell labelings
(\(K\ge3=d_\lambda+2\) — load-bearing: at \(K=2=d_\lambda+1\) the rank
boundary above makes every feasible value exactly \(0\); equal weights;
nonsingular binned nuisance block). Then, almost surely:

1. **(Value; unrestricted supremum.)**
   \(\hat\Phi_s(z^{(N)})\to v_K=\sup_q S_\psi^+(I_q)\), the supremum over
   *all* measurable \(K\)-cell quantizers. The supremum is attained exactly at
   the optimal \(\hat s\)-interval quantizer \(J^*\) — and at nothing else —
   and \(J^*\) is fully nuisance-degenerate: \(m_\lambda(J^*_b)=0\) for every
   \(b\), so \(I_{J^*}\) has zero nuisance row and block,
   \(\lambda_{\min}(I_{J^*})=0\), and \(J^*\) is DS9-infeasible (the binned
   model carries no nuisance information).
2. **((M2) holds.)** \(\min_b\hat W_b(z^{(N)})\to\min_b w_b^*>0\): the
   cell-mass margin is automatic asymptotically; singleton cells die out. The
   \(N\le18\) singleton evidence is pre-asymptotic.
3. **((M3) fails.)** \(\hat I_{\lambda\lambda}(z^{(N)})\to0\),
   \(\hat I_{\psi\lambda}(z^{(N)})\to0\), hence
   \(\lambda_{\min}(\hat I_N(z^{(N)}))\to0\): for every \(\kappa>0\) the
   conditioning margin fails eventually, for **every** law in the class. The
   optimizer sheds binned nuisance information by design.
4. **(Margin-compatible optimum is strictly suboptimal.)** For every
   \(\kappa>0\), \(v^*(\kappa):=\sup\{\Phi(q):\lambda_{\min}(I_q)\ge\kappa\}
   <v_K\). DS14's margin hypothesis set is empty along free global-optimum
   sequences: the conditional bridge governs margin-*certified* (necessarily
   \(\delta(\kappa)\)-suboptimal) solutions, never free global optima, on this
   law class.
5. **(Domination equality at optima.)** The DS11(a) gap at \(z^{(N)}\) —
   \((\hat B^*_N-\hat B_{z})\hat I^z_{\lambda\lambda}(\cdot)^\top\) — tends to
   \(0\): efficient-score domination becomes an equality along global optima
   (answering the fourth OP28 sub-question).

### Proof

**Lemma 1 (scalar reduction; any \(P\) with finite second moments).** For every
measurable \(K\)-cell \(q\): \(\Phi(q)\le\sum_bW_bE[\hat s\mid b]^2\le v_K\).
*Proof.* The DS11 variational form gives
\(\Phi(q)=\min_B\sum_bW_b(\mu_{\psi,b}-B\mu_{\lambda,b})^2
\le\sum_bW_bE[\hat s\mid b]^2\) at \(B=B^*\). For the second inequality,
\(\sum_bW_bE[\hat s\mid b]^2=E\hat s^2-\sum_bE[(\hat s-E[\hat s\mid b])^21_b]\),
and reassigning every point to the nearest of the \(K\) conditional means
decreases the SSE term while producing an \(\hat s\)-measurable partition, so
the SSE is at least \(W_K\). ∎

**Lemma 2 (attainment iff degenerate; (L)).** Under (L), every
\(\hat s\)-measurable partition has
\(m_{\lambda,b}=E[E[S_\lambda\mid\hat s]1_{\hat s\in J_b}]=0\); its variational
form is \(B\)-independent and equals \(\sum_bW_bE[\hat s\mid b]^2\) (as
\(\mu_{\psi,b}=E[\hat s\mid b]\)). At \(J^*\) this is \(v_K\), matching
Lemma 1's bound: \(\sup_q\Phi=v_K\). Equality analysis: equality in Lemma 1's
SSE step forces the cells to be nearest-centroid in \(\hat s\) up to null sets
with an optimal centroid set; under (S) the optimum is unique, so any attainer
is \(J^*\) a.e. ∎

**Lemma 3 (rigidity).** Under (L)+(S), for every \(\varepsilon>0\) there is
\(\delta>0\): any \(K\)-cell \(q\) with
\(\sum_bW_bE[\hat s\mid b]^2\ge v_K-\delta\) has (after relabeling)
\(\max_bP(A_b\,\Delta\,\{\hat s\in J^*_b\})\le\varepsilon\), and all masses
\(\ge\eta(\delta)>0\). Consequently \(|m_{\lambda,b}|\le
\|S_\lambda\|_2\sqrt\varepsilon\) (Cauchy–Schwarz over the symmetric
difference, using \(E[S_\lambda1_{J^*_b}]=0\)) and
\(\|I_{q,\lambda\lambda}\|\le C\varepsilon\). In particular
\(v^*(\kappa)<v_K\) for every \(\kappa>0\).
*Proof.* (i) *Effective cells.* For \(\eta>0\) call \(b\) active if
\(W_b\ge\eta\); inactive cells contribute at most
\(\sup_{P(B)\le K\eta}E[\hat s^21_B]=:\tau(K\eta)\to0\) to the between-value
(Cauchy–Schwarz then uniform integrability). (ii) *Deletion comparison.*
Assigning inactive mass to the active centroid closest to the origin (bounded
by \(\sigma_s\sqrt{K/(1-K\eta)}\)) shows the active centroid set \(C_a\)
satisfies \(E[\min_{c\in C_a}(\hat s-c)^2]\le W_K+\delta+\rho(\eta)\) with
\(\rho(\eta)\to0\). (iii) *Full support.* Strict monotonicity
\(W_{K-1}>W_K\) (atomless law, infinite support) forces all \(K\) cells active
once \(\delta+\rho(\eta)<W_{K-1}-W_K\): the mass bound. (iv) *Centroid
convergence.* Compactify: a centroid escaping to infinity has vanishing
Voronoi mass, contradicting (iii)'s budget via \(W_{K-1}>W_K\); so along any
sequence of \(\delta_m\)-near-optimal partitions the centroid sets converge to
the unique optimal \(C^*\) (continuity + uniqueness). (v) *Partition
convergence.* The excess of \(q\) over its own centroids' nearest-point rule
bounds the misassigned mass at distance \(\ge t\) from the \(C^*\)-midpoints;
boundary \(t\)-slabs have small mass (atomlessness); diagonalize. ∎

**Proposition 4 (exact empirical sandwich; finite algebra).** For every sample
and every feasible labeling \(z\): with \(\hat s_N\) built from the
*full-sample* empirical regression \(\hat B^*_N\) (normal equations:
\(\sum_iw\hat s_{N,i}s_{\lambda,i}=0\)),
\[
\hat\Phi_s(z)\;=\;\mathrm{btw}(\hat s_N;z)-
\hat c(z)^\top\hat I^{z\,-1}_{\lambda\lambda}\hat c(z)
\;\le\;\mathrm{btw}(\hat s_N;z)\;\le\;\hat v_K,
\]
where \(\mathrm{btw}(x;z)=\sum_b(\sum_{i\in b}wx_i)^2/\hat W_b\),
\(\hat c(z)=\) the binned \((\hat s,\lambda)\) cross-moment vector, and
\(\hat v_K\) is the exact optimal \(K\)-grouping value of the \(\hat s_N\)
sample — attained by intervals of sorted \(\hat s_N\) (1-D contiguity), hence
computable exactly by enumeration/DP. Both inequalities are verified in exact
rational arithmetic for every optimum in the N-DS-MARGINS-TREND suite.

**Proposition 5 (bracket limits).** A.s. \(\hat v_K(\hat s_N)\to v_K\):
value convergence of empirical scalar quantization (uniform SLLN over interval
classes; Pollard 1981 — value convergence needs no uniqueness), plus a
uniform-in-labelings Lipschitz bound in the tilt to absorb
\(\hat B^*_N\to B^*\) and the exact centering.
*Proof of the Lipschitz bound (audit-supplied).* For any labeling \(z\),
\(\mathrm{btw}(s_\psi-\beta s_\lambda;z)=A_z-2\beta B_z+\beta^2C_z\) with
\(A_z,B_z,C_z\) the binned between-moments; \(0\le C_z\le\sum_iw s_{\lambda,i}^2\)
and \(|B_z|\le\sqrt{A_zC_z}\le\sqrt{\sum_iws_{\psi,i}^2\sum_iws_{\lambda,i}^2}\)
(between-values are dominated by total second moments; per-cell
Cauchy–Schwarz for the cross term). Hence on \(|\beta-B^*|\le1\) every
\(z\mapsto\mathrm{btw}\) is \(\hat L\)-Lipschitz in \(\beta\) with one
SLLN-bounded \(\hat L\), so their maximum \(\hat v_K(\beta)\) is too, and
\(|\hat v_K(\hat B^*_N)-\hat v_K(B^*)|\le\hat L|\hat B^*_N-B^*|\to0\). The
exact centering shifts every between-value by the same
\(-\bar{\hat s}_N^2\to0\). ∎

**Proposition 6 (achievability by steering).** Under (L)+(S)+(R), a.s. there
are feasible labelings \(z'_N\) with
\(\hat\Phi_s(z'_N)\ge\hat v_K-O(N^{-3/4}\sqrt{\log\log N})\).
*Proof (the tax obstruction and its resolution; the audit hardened the
original sketch — the four supplied ingredients follow the construction).*
Write
\(x_b=m_{\hat s,b}/\hat W_b^{1/2}\), \(y_b=m_{\lambda,b}/\hat W_b^{1/2}\)
(\(d_\lambda=1\)); Proposition 4 reads
\(\hat\Phi_s(z)=|x|^2-\langle x,y\rangle^2/|y|^2\): the profiled value pays the
squared *projection* of \(x\) onto the direction of \(y\). At the DP-optimal
interval labeling \(z_0\) of \(\hat s_N\), both \(\langle x,y\rangle\)
(\(=-\)within-cell cross-moment, mean zero under (L)) and \(|y|\) fluctuate at
the \(N^{-1/2}\) scale, so the tax is a \(\Theta_p(1)\) random *ratio* — the
plain interval labeling does **not** prove achievability, and one-dimensional
cancellations (tilting the slope; greedily shrinking \(|\langle x,y\rangle|\))
leave the ratio \(\Theta_p(1)\). The resolution is to steer the vector \(y\)
itself: single-point swaps between \(\hat s\)-adjacent cells, using points
inside boundary slabs of width \(N^{-1/4}\) with \(\lambda\)-magnitude in
\([\ell,L]\) and chosen sign (available in ample number by (R) and the LLN),
move \(y\) in two independent directions of its constraint plane
\(\{\sum_b\hat W_b^{1/2}y_b=0\}\) with increments \(\Theta([\ell,L]/N)\) and
individual between-cost \(\le2\Delta t/N+O(N^{-2})\). Steer \(y\) to within
\(O(L/N)\) of a target \(y^*\) with \(\langle x,y^*\rangle=0\) and
\(|y^*|=N^{-1/2}\) (the intersection of the constraint plane with
\(x^\perp\) is nonempty for \(K\ge3\), and \(x\ne0\) since
\(\mathrm{btw}(z_0)=\hat v_K>0\)): then \(|\langle x,y\rangle|=O(1/N)\)
while \(\hat I^z_{\lambda\lambda}=|y|^2=N^{-1}(1+o(1))\) is *constructed*, not
random — no small-ball event needed — so the tax is \(\tilde O(1/N)\), the
between-value loss from \(\tilde O(N^{1/2})\) swaps is
\(\tilde O(N^{-3/4})\), and feasibility \(\hat I_{\lambda\lambda}>0\) holds by
construction.

The four ingredients the audit supplied to close the sketch:

- *(Boundary and mass consistency.)* The empirical DP boundaries and masses
  of \(z_0\) converge a.s. to those of \(J^*\) — from (S)-uniqueness and
  Pollard's argmin consistency for the empirical scalar problem; this both
  places the swap slabs at the population boundaries where (R) applies and
  keeps the \(\sqrt{\hat W_b}\) scalings bounded, so the two adjacent-swap
  increment directions \(v_{b,b+1}=e_{b+1}/\sqrt{\hat W_{b+1}}
  -e_b/\sqrt{\hat W_b}\) stay uniformly non-collinear (greedy two-direction
  steering then reaches any plane target to within one increment).
- *(Availability count.)* The number of sample points in a data-dependent
  slab of width \(2N^{-1/4}\) around an empirical boundary carrying each
  nuisance-sign window is \(\ge cN^{3/4}\) eventually a.s.: mean
  \(\asymp N^{3/4}\) by (S) positive density and (R), fluctuation
  \(O(\sqrt{N\log\log N})\) uniformly over the fixed VC class of intervals
  \(\times\) sign windows, and the data-dependent tilt
  \(\hat B^*_N\) shifts memberships by \(L|\hat B^*_N-B^*|
  =O(\sqrt{\log\log N/N})\ll N^{-1/4}\) (LIL). The pools
  (\(\asymp N^{3/4}\)) dominate the \(\tilde O(N^{1/2})\) swaps, each point
  used once, sources never emptied (masses stay near \(w^*>0\)).
- *(Drift accounting.)* Each swap moves \(x\), the centroids, and the
  midpoints by \(O(1/N)\); over \(\tilde O(N^{1/2})\) swaps the cumulative
  \(\tilde O(N^{-1/2})\) drift changes \(\langle x,y\rangle\) by
  \(O(|\Delta x||y|)=\tilde O(N^{-1})\) and each swap's between-cost bound by
  a factor \(1+o(1)\) — absorbed.
- *(Steering distance.)* \(|y(z_0)-y^*|=O(\sqrt{\log\log N/N})\) a.s. (LIL
  over the fixed interval class under (L)), whence the
  \(\tilde O(N^{1/2})\) swap count and the stated
  \(\tilde O(N^{-3/4})\) rate; the theorem consumes only \(o(1)\). ∎

**Proof of the theorem.** (1) Upper: Propositions 4–5. Lower: global
optimality against Proposition 6. Attainment/uniqueness: Lemma 2.
(2)–(3): the sandwich squeezes
\(\mathrm{btw}(\hat s_N;z^{(N)})\to v_K\); Lemma 3 applied along the empirical
scalar problem (Pollard's argmin-continuity carries the uniqueness/compactness
argument to \(\hat\mu_N(\hat s_N)\Rightarrow\operatorname{law}(\hat s)\))
forces the optimum's cells to converge in sample measure to \(J^*\): masses
converge to \(w^*\) (conclusion 2), and the empirical cell nuisance moments
converge to \(E[S_\lambda1_{J^*_b}]=0\) (empirical Cauchy–Schwarz over the
symmetric differences plus the LLN on the fixed sets \(J^*_b\)). The
data-dependent slope is absorbed by a Glivenko–Cantelli law over the **fixed**
VC class of half-planes \(\{s:s_\psi-\beta s_\lambda\le c\}\), \((\beta,c)\)
in a compact neighborhood of \((B^*,\cdot)\), with the population side needing
only (S)-atomlessness of \(\operatorname{law}(\hat s)\) at the \(K-1\) fixed
optimal boundaries — *not* the (M4) slab margin or the (M5) scale that power
the superficially similar step in audit §8 of
`AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md` (the earlier citation of that step
here was a misattribution; the audit report §8 records the corrected lemma):
\(\hat I_{\lambda\lambda},\hat I_{\psi\lambda}\to0\), and
\(\lambda_{\min}\le\hat I_{\lambda\lambda}\) (conclusion 3).
(4): if \(\Phi(q_m)\to v_K\) with \(\lambda_{\min}(I_{q_m})\ge\kappa\), Lemma 1
gives \(\mathrm{btw}\to v_K\), Lemma 3 gives
\(I_{q_m,\lambda\lambda}\to0<\kappa\) — contradiction.
(5): the gap equals the tax \(\hat c^\top\hat I_{\lambda\lambda}^{-1}\hat c=
\mathrm{btw}-\hat\Phi_s\to v_K-v_K=0\). ∎

### Interpretation: the in-bin optimum escapes to the projected formulation

The theorem says the free \(D_s\) optimizer *sheds the in-bin formulation's own
feasibility margin*: its limit \(J^*\) is exactly the optimal binning of the
**projected full-data efficient score** (the external-projection problem,
DS-PROJECTED-K-REQUIREMENT), which is infeasible as an in-bin profiled model
in the sense of DS9's feasibility *split* — its binned nuisance block is
exactly singular, so the in-bin formulation cannot estimate the nuisance from
the bins. (Audit note: DS9's recorded statement is the \(K\le d\) rank
ceiling; \(J^*\)'s infeasibility is the zero-nuisance-block face of the same
split at any \(K\), not the cardinality face.) The two formulations, kept deliberately separate by invariant 3, merge
at the optimum — and that merger is *why* the margins fail. This is the
asymptotic form of the tie fixture's finite phenomenon (pseudo-inverse value
\(1191/4096\) above the feasible optimum \(1083/4096\)), and the partition-side
analogue of the design-theory fact that \(D_s\)-optimal designs can carry
singular information matrices (Silvey 1978).

### Deployability

For conditionally centered (in particular Gaussian/elliptical — the linear
template fit) score laws with \(d_\psi=1\):

- The correct compile target for the profiled criterion is the **scalar
  efficient-score interval rule**: estimate \(\hat B^*_N\) from the full
  sample, bin \(\hat s\) by the exact DP. Certify (a) slope stability and
  (b) the scalar quantizer's own 1-D margins (mass, boundary separation) —
  all easy — instead of the DS14 (M3) certificate, which this theorem proves
  can never hold at free global optima.
- A margin-certified in-bin quantizer (audit §11 flow) is legitimate but costs
  at least \(\delta(\kappa)=v_K-v^*(\kappa)>0\) of profiled information — the
  certificate has a quantified price (information-loss implication:
  \(\eta_{D_s}\)-retention strictly below the unrestricted optimum).
- The binned model at the compile target deliberately carries no nuisance
  information (DS9): the report must state that nuisance estimation stays
  unbinned/full-sample — matching the CMS-2025 use pattern (profile at the
  full-likelihood level, bin for the POI).

### What is deliberately not claimed

(i) Nothing beyond class (L): if \(E[S_\lambda\mid\hat s]\ne0\), the tax has a
\(\Theta(1)\) population component on \(\hat s\)-intervals and the supremum may
be attained at nondegenerate quantizers — the margins may then hold; this is
OP29 (`OPEN-DS-MARGINS-NONCENTERED`). (ii) \(d_\psi>1\): Lemma 2's reduction
(via the Loewner form of DS11(a)) identifies the degenerate attainers, but the
uniqueness/rigidity theory of the vector between-matrix problem is open —
the dichotomy transfers exactly when that theory does. (ii′) \(d_\lambda\ge2\):
at \(K=d_\lambda+1\) the claim is **false** (rank vacuity,
`CE-DS-MARGINS-RANK-VACUITY-001`); at \(K\ge d_\lambda+2\) it is open —
Proposition 6's steering uses a scalar nuisance sign and (R) as stated is
one-dimensional (a vector version needs sign-rich swap directions spanning
\(\mathbb R^{d_\lambda}\) and \(K\ge d_\lambda+2\) for the constraint-plane
target to exist); tracked in OP29. (iii) Local/
exchange-stable non-global sequences: DS14 continues to govern them under
certified margins; nothing here says local optima degenerate. (iv) Estimated
scores: P2. (v) (M5): at optima the projected-centroid *object*
\(\hat e_b=\hat\mu_{\psi,b}-\hat B_z\hat\mu_{\lambda,b}\) rides on
\(\hat B_z=\hat I_{\psi\lambda}/\hat I_{\lambda\lambda}\to0/0\); the
meaningful reduced geometry is the scalar \(J^*\) geometry (distinct
centroids). Measured: the optimum's own regression slope keeps an
\(O(1)\)-scale distance from the full-sample slope with no decline through
\(N=20\) (median per-law gaps \(0.01\)–\(0.6\)) — the (M5) object is indeed
unstable at optima.

**Measured (N-DS-MARGINS-TREND, N-DS-SCALAR-MASS, N-DS-MARGINS-EXACT-ANCHOR).**
Fine-grid (\(1/2^{16}\), atomless-emulating) exact-optimum suite, 6 laws,
\(N=8\)–\(18\), 3 reps (+ \(N=20\) extension): the sandwich and tax identity
verified exactly on every instance (112/112, including four at \(N=20\)); **zero** exact ties (the
31-fold tie was an atomic-grid artifact); the optimum is always within 0–3
points of the best efficient-score interval labeling, with relative value gap
medians 0.3–6%; gauss06's binned nuisance block declines (median 0.23 at
\(N=8\) to 0.02 at \(N=18\), the predicted \(K/N\) scale) while the
non-centered mix3's stays macroscopic (median 0.30–0.68 through \(N=16\)) —
the class boundary is visible. Singletons still occur at these tiny \(N\) but
thin out for the Gaussian laws; the scalar suite settles their fate: exact
optimal \(K\)-interval partitions of Gaussian/Laplace/uniform samples at
\(N=100\)–\(20{,}000\) (12 reps each) have min cell mass rising to the
population values (Gaussian \(K=3\): 0.259–0.268 at \(N=20{,}000\) vs 0.2703;
\(K=6\): 0.063–0.071 vs 0.0740) with no singleton beyond \(N=100\).
The float screen is anchored by fully exact enumeration (all 86,526 canonical
partitions per instance) at \(N=12\): 6/6 optima match exactly.

**Audit-side measured (30 Aug 2026, N-DS-AUDIT15 rows).** An independent
pure-stdlib exact suite (`py/audit_ds_margins_at_optima.py`, own CLT-rational
law emulation and LCG seeds, no float screen) exhaustively certified 20 exact
global optima at \(N=12\)–\(16\) (up to all 7,141,686 canonical partitions per
instance): the sandwich and tax identity hold on 20/20; **zero exact ties over
the full lattice on every instance**; the researcher's float top-64 screen,
re-implemented with its \(10^{-9}\) guard, ranks the true optimum first with
zero guard casualties on 20/20 — validating the screen mechanism in the
\(N\ge14\) territory where the original suite is screen-selected (the original
\(N\ge14\) instances themselves remain uncertified); the centered law's
nuisance block stays small while the non-centered control's stays macroscopic
(class boundary reproduced); the single observed singleton sits on the
non-centered control (\(N=15\)). The float-only scalar (M2) sweep is anchored
by an exact-rational interval DP at \(N=1000\): the library DP reproduces the
exact optimum (SSE agreement \(10^{-9}\), identical min cell mass \(49/200\)).

---
## DS16. Margin price at arbitrary labelings, the value funnel, and the profiled compile verdict — [PROJECT-PROVED theorem + MEASURED selection; conditionally centered laws, \(d_\psi=d_\lambda=1\)]

**Claims:** DS-STABLE-MARGINS-PRICE, DS-STABLE-STATE-SELECTION, DS-PROFILED-COMPILE-CERTIFICATE

**Audit (30 Aug 2026,
`AUDITS/AUDIT-DS-STABLE-MARGINS-COMPILE-001.md`):** all three claims are
**hardened**. The PRICE/FUNNEL/FLOOR theorem is verified after replacing a
pointwise SLLN at a data-dependent centroid limit by a uniform strong law on
compact tilt--codebook sets, making the all-labelings event explicit, and
fixing the raw-label/exact-centering convention in the FLOOR. The compile
claim now says *only currently established in the registered theory*, not
mathematical uniqueness: DS14 is a theorem for certified **sequences**, and
a single finite certificate supplies diagnostics but no population guarantee.
The measured census range is corrected from 18--944 to 5--944, and its
reported library gap interval is identified as an aggregate summary rather
than a run-wise bound.

Setting: exactly DS15's — \(S=(S_\psi,S_\lambda)\sim P\) on \(\mathbb R^2\),
\(ES=0\), \(E\|S\|^2<\infty\), \(I\succ0\), class **(L)** (conditional
centering) + **(S)** (scalar regularity of \(\operatorname{law}(\hat s)\));
**(R)** is *not* needed here except where DS15's conclusion (1) is imported
for a comparison. Equal weights, centered score rows
\(\tilde S_i=S_i-\bar S_N\) in every empirical information calculation,
\(K\ge3\)
(\(=d_\psi+d_\lambda+1\); see the cardinality restatement below), feasible
labelings = nonsingular binned nuisance block \(\hat I_{\lambda\lambda}>0\).
\(v_K\), \(J^*\), \(w^*_b\), \(\hat v_K\), \(\mathrm{btw}(\hat s_N;z)\) as in
DS15.

**Cardinality, restated (library commit `891bbf3`, 30 Aug 2026).** The
registered condition \(K\ge d_\lambda+2\) is a \(d_\psi=1\) coincidence. The
mechanism is \(\sum_b m_b=\hat\mu\) (with \(m_b=\sum_{i\in b}w_is_i\)): the
binned moment vectors of an exactly centered sample satisfy one linear
relation, so
\(\operatorname{rank}(I_z)\le K-1\), and a nonvacuous profiled value needs
\(K-1\ge d=d_\psi+d_\lambda\), i.e. **\(K\ge d_\psi+d_\lambda+1\)** on a
centered sample. At \(d_\psi=1\) this is exactly \(K\ge d_\lambda+2\), which
is why `CE-DS-MARGINS-RANK-VACUITY-001` (a \(d_\psi=1\) witness) suggested
the narrower formula; its `consequences[0]` line carries that \(d_\psi=1\)
restriction implicitly.

The algebraic rank bound can be one larger for a matrix built from rows with
nonzero empirical mean. That is not an alternative Fisher-score regime:
scores have mean zero, and ScoreQuant's empirical information uses exact
centering. No off-centered compile claim is inferred from that matrix fact.

### The question

DS15 shows free *global* finite \(D_s\) optima converge to the
nuisance-degenerate efficient-score interval quantizer: (M2) holds, (M3)
fails. The library's optimizer returns one-point **exchange-stable,
generally non-global** states (`DS-EXCHANGE-TERMINATES`), and DS15 asserts
nothing about them. OP29's deployment half asks: do *those* states retain
the DS14 margins, at what information cost \(v_K-\hat\Phi_s\), and does a
theorem-backed inductive compile rule for profiled criteria exist beyond the
projected efficient-score interval rule?

The first observation is that the question is not a universal quantification:
global optima are themselves exchange-stable, so DS15 already exhibits stable
sequences along which (M3) fails. What decides the compile question is (i)
whether the margins are *priced* — whether any labeling carrying them must sit
a definite distance below the supremum — and (ii) which regime the optimizer's
terminal states actually occupy.

### Theorem (margin price and the value funnel)

Under (L)+(S), \(d_\psi=d_\lambda=1\), \(K\ge3\), equal weights, almost
surely:

1. **(Price.)** For every \(\kappa>0\) there is \(\delta(\kappa)>0\),
   depending only on \((P,K,\kappa)\), with
   \[
   \limsup_N\;
   \sup\bigl\{\hat\Phi_s(z)\;:\;z\ \text{feasible},\
   \hat I_{\lambda\lambda}(z)\ge\kappa\bigr\}
   \;\le\;
   \limsup_N\;
   \sup\bigl\{\mathrm{btw}(\hat s_N;z)\;:\;
   \hat I_{\lambda\lambda}(z)\ge\kappa\bigr\}
   \;\le\; v_K-\delta(\kappa).
   \]
   Since \(\lambda_{\min}(\hat I_N)\le\hat I_{\lambda\lambda}\), the same cap
   holds under the DS14 conditioning margin (M3) at level \(\kappa\). The
   hypothesis is a margin, not stability or optimality: **every**
   margin-carrying labeling — exchange-stable or not, optimizer-produced or
   not — pays at least \(\delta(\kappa)\) of profiled information relative to
   the unrestricted supremum \(v_K\) that free global optima attain under
   (L)+(S)+(R) (DS15 conclusion 1).
2. **(Funnel.)** Any sequence of feasible labelings with
   \(\hat\Phi_s(z^{(N)})\to v_K\) — in particular any asymptotically
   value-optimal solver output, from any seed, stable or not, global or not —
   satisfies: cells converge in sample measure to \(J^*\), min cell mass
   \(\to\min_b w^*_b>0\) ((M2) holds; singletons die out),
   \(\hat I_{\lambda\lambda},\hat I_{\psi\lambda}\to0\), hence
   \(\lambda_{\min}(\hat I_N)\to0\) ((M3) fails), and the (M5) object
   \(\hat B_z=\hat I_{\psi\lambda}/\hat I_{\lambda\lambda}\) rides the same
   \(0/0\) as in DS15. DS15's conclusions (2)–(3) are therefore
   value-topological, not properties of exact global optimality.
3. **(Floor.)** For every fixed measurable \(K\)-cell quantizer \(q\) on the
   raw score \(S\), with \(W_b>0\) and
   \(I_{q,\lambda\lambda}>\kappa\), label row \(i\) by \(q(S_i)\) and compute
   its empirical information from the centered rows \(\tilde S_i\). Those
   labelings are eventually feasible with
   \(\hat I_{\lambda\lambda}\ge\kappa\) and
   \(\hat\Phi_s\to\Phi(q)\). Hence the supremum in (1) is asymptotically at
   least \(v^{*+}(\kappa):=\sup\{\Phi(q):I_{q,\lambda\lambda}>\kappa\}\), and
   \(v^{*+}(\kappa)\le v_K-\delta(\kappa)\); DS15's margin-compatible optimum
   \(v^*(\kappa)\) (over \(\lambda_{\min}(I_q)\ge\kappa\), a subclass) obeys
   \(v^*(\kappa)\le v^{*+}(\kappa)\). This is a supremal lower bound: it
   asserts neither attainment nor one-sided continuity of either constrained
   value in \(\kappa\).

### Proof

Throughout, work on one probability-one event where:
\(\hat v_K(\hat s_N)\to v_K\)
and the tilt-Lipschitz bound of DS15 Proposition 5 holds (its proof needs
only (M1)-type moments and (S); the same argument gives
\(\hat v_{K-1}\to v_{K-1}\)); \(\hat B^*_N\to B^*\) and the SLLN holds for
\(\|S\|^2\), \(S_\lambda^2\), and the fixed cells \(1_{J^*_b}\) weighted by
\(S_\lambda\); the Glivenko–Cantelli law holds over the fixed VC class of
tilted half-planes \(\{s:s_\psi-\beta s_\lambda\le c\}\), \((\beta,c)\) in a
compact neighborhood of \((B^*,\cdot)\), both unweighted and with integrable
envelope \(|S_\lambda|\). For the signed weight, apply the VC theorem to
\(S_\lambda^+1_H\) and \(S_\lambda^-1_H\) separately; compact tilt control is
already included because all \((\beta,c)\) half-planes form one fixed
finite-VC class, and \(E|S_\lambda|<\infty\) follows from the second moment.
Also include the uniform strong law
\[
 \sup_{\beta\in\mathcal B,\ C\in[-R,R]^K}
 \left|(P_N-P)\min_{c\in C}(S_\psi-\beta S_\lambda-c)^2\right|\to0
\]
for every compact \(\mathcal B\) containing \(B^*\) and finite \(R\). This
follows by truncation and finite parameter nets: the class is continuous in
the finite-dimensional parameter \((\beta,C)\), and on each compact set has
an integrable envelope \(A_R(1+\|S\|^2)\). Finally include the empirical DP
boundaries and masses of
\(\hat J^*_N\) converge to \(J^*\)'s (the audit-hardened boundary/mass
consistency ingredient of DS15 Proposition 6, which needs only (S)).

**Lemma DS16.1 (empirical grouping rigidity, uniform).** For every
\(\varepsilon>0\) there are \(\delta_0>0\) and an a.s. finite \(N_0\) such
that for all \(N\ge N_0\) and **every** \(K\)-grouping \(z\) of the sample
indices with
\(\mathrm{btw}(\hat s_N;z)\ge \hat v_K-\delta_0\):
after relabeling, \(\hat P_N(z\text{-cell}_b\,\Delta\,\{\hat s_N\in
J^*_b\})\le\varepsilon\) for every \(b\), and
\(\hat W_b(z)\ge w^*_b-2\varepsilon\).

*Proof.* This is DS15 Lemma 3's five-step architecture run on the empirical
scalar sample, with groupings in place of measurable partitions — the one
genuine gap between the two settings, closed as follows. Write
\(x_i=\hat s_{N,i}\), \(\hat P_N\hat s^2=\mathrm{btw}(z)+\mathrm{WSSE}(z)\),
so the hypothesis reads \(\mathrm{WSSE}(z)\le\hat W_K+\delta_0\) with
\(\hat W_K=\hat P_N\hat s^2-\hat v_K\) the optimal empirical \(K\)-grouping
SSE (attained by sorted intervals — the 1-D contiguity fact of DS15
Proposition 4, verified on the full lattice in the identity suites).

(i) *Inactive-cell budget.* For \(\eta>0\) call \(b\) active when
\(\hat W_b\ge\eta\). Uniform integrability transfers: for any \(T\),
\(\sup_{\hat P_N(B)\le m}\hat P_N[\hat s^21_B]\le
2\bigl(\hat P_N[s_\psi^21_{s_\psi^2>T}]+\hat B_N^{*2}\hat
P_N[s_\lambda^21_{s_\lambda^2>T}]\bigr)+2(1+B^{*2})Tm+o(1)\), and the tail
terms converge to their population values by the SLLN on fixed functions; so
inactive cells contribute \(\tau(K\eta)+o(1)\) to the between value with
\(\tau(m)\downarrow0\).

(ii) *Deletion comparison and* (iii) *full support.* If one cell has mass
below \(\eta\), merge it into a bounded active cell. The increment in SSE is
bounded by the inactive cell's second-moment contribution plus its mass times
an active-centroid bound, hence by \(\rho(\eta)+o(1)\), where
\(\rho(\eta)\downarrow0\) by (i). The resulting grouping uses at most
\(K-1\) cells, so its SSE is at least \(\hat W_{K-1}\). Therefore
\(\hat W_{K-1}-\hat W_K\le\delta_0+\rho(\eta)+o(1)\). But
\(\hat W_{K-1}-\hat W_K\to W_{K-1}-W_K>0\) (value convergence at both
budgets; strict positivity from (S), whose positive density near the optimal
boundaries in particular rules out a finite-support collapse). Choose
\(\eta\), then \(\delta_0\), below this gap: every cell is active. This also
closes the apparent \(K\)-versus-\(K-1\) loophole; an empty cell is simply the
\(\eta=0\) case.

(iv) *Centroid convergence, uniform over groupings.* This is the standard
almost-minimizer rigidity principle for k-means codebooks
(Rakhlin--Caponnetto 2006 supplies direct bounded-source prior art), with the
grouping-to-nearest-center reduction made explicit here. Suppose groupings
\(z^{(N_j)}\) with \(\mathrm{WSSE}\le\hat W_K+\delta_j\), \(\delta_j\to0\),
had active-centroid sets escaping a neighborhood of \(C^*\). Active centroids
are bounded (moment bound), so a subsequential limit set \(C'\ne C^*\)
exists. The nearest-point SSE is grouping-independent:
\(\mathrm{SSE}_{\hat P_N}(c(z))\le\mathrm{WSSE}(z)\): reassigning every
observation to a nearest centroid cannot increase SSE, even when duplicate
atoms were split among cells. By the compact-set uniform law displayed
above, simultaneously for the data-dependent \(\hat B_N^*\) and all bounded
codebooks,
\(
\mathrm{SSE}_{P}(c(z^{(N_j)}))
\le \hat W_K+\delta_j+o(1).
\)
Continuity in the codebook then gives
\(\mathrm{SSE}_P(C')\le W_K\), contradicting (S)-uniqueness when
\(C'\ne C^*\). This uniform law is essential: a pointwise SLLN for the
random subsequential limit \(C'\) would be invalid. Thus near-optimal
groupings have centroid sets uniformly convergent to \(C^*\).

(v) *Misassignment slabs.* For a grouping \(z\) with centroids
\(\gamma\)-close to \(C^*\): a point on cell \(a\)'s side at distance
\(\ge t\) from the midpoint of \((c_a,c_b)\) but assigned to \(b\) pays
excess \((x-c_b)^2-(x-c_a)^2\ge 2t\,g/2\) with \(g=\) the minimal \(C^*\)
centroid gap, once \(\gamma<g/4\); so the \(\hat P_N\)-mass misassigned
beyond the \(t\)-slabs is \(\le(\delta_0+o(1))/(tg/2)\), while the slabs
themselves lie inside fixed \((t+\gamma)\)-slabs around the \(C^*\) midpoints
whose empirical mass converges to the population slab mass, small by
(S)-atomlessness. Choosing \(t\) then \(\delta_0\) gives the symmetric
difference bound against the empirical Voronoi cells of \(C^*\); replacing
them by \(\hat J^*_N\)'s cells (boundary/mass consistency) and by the fixed
sets \(\{\hat s_N\in J^*_b\}\) costs empirical slab masses that vanish by the
same GC-plus-atomlessness argument. Masses follow:
\(\hat W_b\ge \hat P_N(\hat s_N\in J^*_b)-\varepsilon\to w^*_b-\varepsilon\).
∎

**Proof of (1).** Define a supremum over an empty feasible set as \(-\infty\).
For each \(N\), both suprema are maxima of finitely many extended-real
measurable functions of the sample, so they are measurable. Intersecting the
probability-one uniform-law events above over integer compact radii and
rational tolerances produces one measurable event on which the argument is
pathwise and simultaneous over **all** labelings at every \(N\). Consequently
the conclusion holds for every labeling sequence selected on that event,
including a data-dependent selection; no separate exceptional set is chosen
per sequence. When the constrained set is nonempty, let \(z^{(N)}\) attain the
\(\mathrm{btw}\)-maximum subject to \(\hat I_{\lambda\lambda}\ge\kappa\). The
first inequality is DS15 Proposition 4 (exact, every sample, every feasible
labeling). Fix \(\kappa\); suppose along a subsequence
\(\mathrm{btw}(\hat s_N;z^{(N)})> v_K-\delta\). Since \(\hat v_K\to v_K\),
for large \(N\) the hypothesis of Lemma DS16.1 holds with
\(\delta_0=2\delta\). Take \(\varepsilon=\varepsilon(\kappa)\) to be fixed
below and \(\delta=\delta_0(\varepsilon)/2\). The lemma gives, per cell,
\[
\bigl|\hat m_{\lambda,b}(z^{(N)})-\hat P_N[S_\lambda1_{\hat s_N\in J^*_b}]
\bigr|
\le\bigl(\hat P_NS_\lambda^2\bigr)^{1/2}\varepsilon^{1/2}
\]
(Cauchy–Schwarz over the symmetric difference), while
\(\hat P_N[S_\lambda1_{\hat s_N\in J^*_b}]\to
E[S_\lambda1_{\hat s\in J^*_b}]=0\) — the weighted GC law over the tilted
half-plane class absorbs \(\hat B^*_N\to B^*\), dominated convergence plus
(S)-atomless boundaries give continuity in the tilt, and (L) makes the limit
zero. With \(\hat W_b\ge w^*_b-2\varepsilon\ge w^*_{\min}/2\) for
\(\varepsilon\) small,
\[
\hat I_{\lambda\lambda}(z^{(N)})
=\sum_b\frac{\hat m_{\lambda,b}^2}{\hat W_b}
\le\frac{2K}{w^*_{\min}}\bigl(C\varepsilon^{1/2}+o(1)\bigr)^2,
\]
with \(C^2=2ES_\lambda^2\), say. Choose \(\varepsilon(\kappa)\) so the right
side is eventually \(<\kappa\): contradiction with
\(\hat I_{\lambda\lambda}\ge\kappa\). Hence
\(\limsup\sup\{\mathrm{btw}\}\le v_K-\delta(\kappa)\) with
\(\delta(\kappa)=\delta_0(\varepsilon(\kappa))/2\). The (M3) transfer is the
diagonal bound \(\lambda_{\min}(\hat I_N)\le e_\lambda^\top\hat I_Ne_\lambda
=\hat I_{\lambda\lambda}\). ∎

**Proof of (2).** \(\hat\Phi_s(z^{(N)})\to v_K\) forces
\(\mathrm{btw}(\hat s_N;z^{(N)})\to v_K\) (Proposition 4 sandwich with
\(\hat v_K\to v_K\)). Apply Lemma DS16.1 with \(\varepsilon_m\downarrow0\)
along \(\delta_m\downarrow0\) and diagonalize: symmetric differences to
\(J^*\)-cells vanish, so masses converge to \(w^*_b\) (min mass positive,
singletons die), and the Step-3 display above with \(\varepsilon\to0\) gives
\(\hat m_{\lambda,b}\to0\), hence \(\hat I_{\lambda\lambda}\to0\); the cross
block \(\hat I_{\psi\lambda}=\sum_b\hat m_{\psi,b}\hat m_{\lambda,b}/\hat
W_b\to0\) since \(\hat m_{\psi,b}\) is bounded and masses are bounded below;
\(\lambda_{\min}\le\hat I_{\lambda\lambda}\to0\). ∎

**Proof of (3).** For a fixed \(q\), label by \(q(S_i)\), not by applying an
arbitrary discontinuous rule to the sample-centered row. Masses and raw
moments are sample means of fixed integrable functions. Exact centering only
changes the empirical cell moment by
\[
 \hat m_b=P_N[S1_{\{q(S)=b\}}]-\bar S_NP_N(q(S)=b),
\]
which converges to \(m_b\) because \(\bar S_N\to ES=0\). Thus the LLN gives
\(\hat W_b\to W_b>0\), \(\hat m_b\to m_b\), so \(\hat
I_{\lambda\lambda}\to I_{q,\lambda\lambda}>\kappa\) (eventually
\(\ge\kappa\)), feasibility eventually, and \(\hat\Phi_s\to\Phi(q)\) by
continuity of the Schur value at a nonsingular scalar nuisance block. Taking
\(q\) near the sup gives the floor; the cap of (1) applied to these labelings
gives \(v^{*+}(\kappa)\le v_K-\delta(\kappa)\). Neither this approximation nor
the price proof supplies an optimizer at the strict boundary or continuity in
\(\kappa\). ∎

**Self-adversarial notes (protocol G).** Duplicate atoms and split duplicates
are inside the grouping formulation by construction; singleton cells are
handled by the mass step, not excluded; \(\hat I_{\lambda\lambda}\ge\kappa\)
excludes singular nuisance blocks but not \(\det\hat I_N=0\) (such states
have \(\hat\Phi_s=0\), inside the cap trivially); the statement is for exact
scores and equal weights — estimated scores are P2, unequal weights were
probed adversarially at finite \(N\) (census suite) but are not claimed; the
law class needs (S) (atomless, unique scalar optimum) — the census grid laws
are atomic emulations, evidence only; nothing here claims margin-carrying
*exchange-stable* sequences exist asymptotically (that inhabitation question
is OP30). Applying \(q\) to centered rows instead of raw \(S_i\) is a
different, sample-dependent labeling convention and needs boundary/translation
continuity not assumed here. The PRICE statement is nevertheless pathwise
uniform over all labelings, so it covers either convention whenever the
margin is observed.

### Measured: which regime the optimizer actually occupies

(`N-DS-STABLE-CENSUS`, `N-DS-STABLE-ASCENT`, `N-DS-STABLE-LIBRARY`;
`py/ds_stable_margins.py`, integer-exact full-lattice census selftested
against the audit stack's from-scratch oracle on 782 states.)

- **Census (exact, \(N=10\)–\(14\), \(K=3\), centered06 + mix3, 2 reps).**
  Exchange-stable states are plentiful (5–944 per instance) and
  overwhelmingly non-global. On the centered law they span both regimes:
  \(\hat I_{\lambda\lambda}\) from \(10^{-5}\) to \(0.57\), with gap and
  nuisance block **anti-correlated** (per-instance correlation \(-0.27\) to
  \(-0.83\)) — the finite shadow of conclusion (1). Whenever
  \(\hat I_{\lambda\lambda}>0.2\), the relative gap exceeded \(1.2\%\)–\(8.4\%\);
  margin-retaining non-global stable states existed in **every** instance
  (witness fixture `CE-DS-STABLE-MARGIN-RETAINING-001`, \(N=8\):
  \(\hat I_{\lambda\lambda}\approx0.523\), \(\lambda_{\min}\ge0.1397\), min
  mass \(1/4\), separation \(0.325\), price \(7.7\%\)). The DS13 leverage
  bound held at every spot-checked stable state; the exact sandwich held at
  all 3,155 stable states censused. (M5) caution: stable states with nearly
  coincident projected centroids occur (min separation \(5.5\times10^{-4}\)),
  so separation must be *checked*, never assumed (cf. DS12 wasted cells).
- **The documented initializer is not a terminal state.** The efficient-score
  DP interval labeling is exchange-unstable in 7/10 centered-law census
  instances (and already at \(N=8\): fixture
  `CE-DS-INTERVAL-SEED-UNSTABLE-001`, exact gain \(0.447\)); the improving
  move grows the nuisance block 27-fold — near the seed, the profiled
  objective climbs by buying back nuisance information, the finite face of
  DS15 Proposition 6's steering. On mix3 the same labeling was stable in
  9/10 instances.
- **Exact ascent (\(N\le14\)).** Terminal states from the interval seed and
  20 random seeds per instance are strongly seed-dependent on the centered
  law (terminal \(\hat I_{\lambda\lambda}\) spanning \(0.0002\)–\(0.57\));
  margin-retaining terminals are reached with sizable probability at these
  tiny \(N\).
- **Library scale (\(N=100/300/1000\), gauss06 vs mix3; efficient-score vs
  k-means++ vs random seeding; `optimize_partition` +
  `ProfiledDOptimality` + `DExchangeConfig`, exchange-stable terminals
  verified).** On the centered law, **every** seeding's terminal state
  collapses the nuisance block at the predicted \(K/N\) scale
  (\(N\cdot\hat I_{\lambda\lambda}\) median \(0.5\)–\(3.0\) across all seeds
  and sizes) with near-optimal values (the research run's reported aggregate
  log-gap summaries to the certified DP ceiling are \(0.004\)–\(0.046\); this
  is not a bound on every seed/run), masses approaching the population values and healthy
  separations — exactly conclusion (2) in action: the terminals are in the
  funnel because they are near-optimal in value, seed-independently. On mix3
  every seeding lands at \(\lambda_{\min}\approx1.7=\Theta(1)\) with log-gaps
  \(\le2\times10^{-4}\): the non-centered regime keeps its margins at the
  optimum, as OP29's first branch conjectures.

### Verdict: the compile rule (DS-PROFILED-COMPILE-CERTIFICATE)

On the conditionally centered class, for what the free optimizer returns:

- **The projected efficient-score interval rule remains the only currently
  established unconditional compile path in the registered theory.** This is
  an inventory of proved routes, not a mathematical uniqueness theorem about
  every possible compiler. Free profiled optimization is
  value-driven; conclusion (2) makes every value-successful run — global or
  not, however seeded — nuisance-degenerate in the limit, with the companion
  rule's slope \(\hat B_z\) unstable (0/0). Nothing about the terminal state
  is stably compilable, and `compile_quantizer`'s refusal for profiled
  criteria is the correct default, now backed by a theorem about the
  optimizer's actual output rather than only about global optima.
- **DS14 supplies a sequence-conditional companion rule, not a population
  guarantee from one finite certificate.** If an exchange-stable sequence
  satisfies DS14's full hypotheses — (M1)/(M4) on the law and, eventually,
  uniform (M2)/(M3)/(M5), or the audited merged-rule variant — then the
  companion efficient-Voronoi rules \(\rho_N\) built from the states' own
  projected centroids and profiled metrics geometrize and have
  population-stationary subsequential limits. At one finite \(N\), exact
  exchange stability plus measured mass, conditioning, and separation checks
  are useful diagnostics and define a candidate companion rule, but do not by
  themselves certify those asymptotics; DS13 is a consequence of stability,
  not a replacement for it. DS16 prices any state with measured
  \(\lambda_{\min}(\hat I_N)\ge\kappa\) pathwise: report the observable finite
  gap \(\hat v_K-\hat\Phi_s\) (the `efficient_score_bound` DP ceiling minus
  the terminal value). The population \(\delta(\kappa)\) is existential and
  may not be reported numerically without a law-specific lower bound.
  Measured: on the centered class the free optimizer does
  **not** return such states at realistic \(N\) (the funnel), so the
  candidate path operationally appears to require margin-*constrained*
  optimization — a solver-design question (OP7), whose asymptotic non-vacuity (do
  margin-compatible stable sequences exist? is \(v^*(\kappa)\) attained?) is
  the explicit open remainder OP30 (`OPEN-DS-STABLE-BASINS`).
- **Information-loss implication.** A margin-certified compile retains at
  most \(v_K-\delta(\kappa)\) of profiled information against the \(K\)-cell
  ceiling \(v_K\) (relative retention \(\le1-\delta(\kappa)/v_K\)), on top of
  the binning loss \(v_K<\sigma_s^2\) against unbinned inference; the
  projected rule attains the ceiling only in the distinct projected-score
  formulation where nuisance information is supplied externally/unbinned
  (DS9/DS15 deployability). The theorem gives no positive computable lower
  bound on \(\delta(\kappa)\) from a single finite dataset.

Both packet stop conditions that could close the deployment question are thus
hit: **proved** (price + funnel on the stated class) and **reduced** (the
inhabitation/selection remainder is OP30), with the falsification half
serialized (`CE-DS-STABLE-MARGIN-RETAINING-001`,
`CE-DS-INTERVAL-SEED-UNSTABLE-001`).

## DS17. Inhabitation of the margin-certified branch: the conditional-centering obstruction and the fixed-point gate — [PROJECT-PROVED theorem + MEASURED gate scans; \(d_\psi=d_\lambda=1\)]

**Claims:** DS-STABLE-BASINS-CENTERED-OBSTRUCTION, DS-STABLE-BASINS-LCM-CLASSIFICATION, DS-STABLE-BASINS-FIXED-POINT-GATE, DS-STABLE-BASINS-GATE-SCANS

**Independent audit (31 Aug 2026,
`AUDITS/AUDIT-DS-STABLE-BASINS-001.md`).** All four nodes are hardened. The
obstruction and eventual-emptiness theorem survive. The audit separates the
root equation, which remains meaningful at a singular binned nuisance block,
from regular tilt consistency \(B_q^*=\beta\), which does not; restricts the
LCM conclusions and Gaussian sign-split construction to their exact scopes;
and demotes every finite root scan to windowed measured evidence. A numerical
scan cannot decide the gate for a law, and a root is necessary, never
sufficient, for empirical inhabitation.

**Normalization (protocol A).** Criterion: in-bin profiled \(D_s\). Levels:
`population_quantizer` (existence/non-existence of self-consistent rules) and
`empirical_to_population` (the inhabitation consequence). Decision variables:
ordinary one-point exchange-stable finite labelings (DS14's hypotheses — never
stability-under-constraint) and population strip rules. Setting as in DS14/DS15:
\(d_\psi=d_\lambda=1\), \(K\ge3\), \(ES=0\), \(E\|S\|^2<\infty\),
\(I=E[SS^\top]\succ0\), efficient score \(\hat s=S_\psi-B^*S_\lambda\),
\(B^*=I_{\psi\lambda}/I_{\lambda\lambda}\). For \(\beta\in\mathbb R\) write
\(T_\beta=S_\psi-\beta S_\lambda\); a **strip rule** at tilt \(\beta\) is a
\(K\)-cell interval partition of \(T_\beta\) with positive masses. Neither (S)
nor (R) is assumed anywhere in DS17.1–DS17.2; (L) is the DS15 conditional
centering \(E[S_\lambda\mid\hat s]=0\) a.s. Deployability question decided: is
OP30(a) — almost-sure sequences of margin-certified exchange-stable labelings —
inhabited on the DS15/DS16 class? Information-loss implication: on that class
the certified branch retains nothing because it is empty; off the class the
gate identity below is only a necessary population test. Conditional centering
is a property of the population score law; it is not, and does not authorize,
sample centering or recentering of score rows.

### Lemma DS17.1a (tilt-residual identity; any law, any partition)

For any \(K\)-cell partition \(q\) with masses \(W_b>0\), centroids
\((\mu_{\psi,b},\mu_{\lambda,b})\), and any \(\beta\), set
\(t_b=\mu_{\psi,b}-\beta\mu_{\lambda,b}\). Then
\(\sum_bW_bt_b\mu_{\lambda,b}=I_{\psi\lambda}(q)-\beta I_{\lambda\lambda}(q)\),
so whenever \(I_{\lambda\lambda}(q)>0\),

\[
B^*(I_q)-\beta=\frac{\sum_bW_bt_b\mu_{\lambda,b}}{I_{\lambda\lambda}(q)} .
\]

For a strip rule at tilt \(\beta\), \(t_b=E[T_\beta\mid A_b]\) and the numerator
is \(E[h(T_\beta)S_\lambda]\), where \(h=\sum_bt_b1_{A_b}\) is the
**non-decreasing step function** sending each \(T_\beta\)-interval to its
conditional mean (strictly increasing values across cells, for an atomless law
with positive masses). *Proof:* expand the definitions; for the strip form use
the tower property \(\sum_bW_bt_b\mu_{\lambda,b}
=E[\,E[T\mid\sigma(q)]\,E[S_\lambda\mid\sigma(q)]\,]=E[h(T)S_\lambda]\), since
\(h(T)=E[T\mid\sigma(q)]\) is \(\sigma(q)\)-measurable and bounded
(\(|h|\le\max_b|t_b|<\infty\)). ∎

Two immediate readings. (i) Call the numerator condition
\(E[h(T_\beta)S_\lambda]=0\) **root consistency**. When
\(I_{q,\lambda\lambda}>0\), it is equivalent to the regular notion of
**tilt consistency** \(B^*(I_q)=\beta\). When
\(I_{q,\lambda\lambda}=0\), \(B^*(I_q)\) is undefined and only the root
equation may be stated. A self-consistent efficient-Voronoi rule with a
positive nuisance block is regularly tilt-consistent at \(\beta=B^*_q\) by
construction. (ii) At any regular tilt-consistent pair the projected centroids satisfy
\(e_b=\mu_{\psi,b}-\beta\mu_{\lambda,b}=t_b\) **identically** — projection
linearity, no law hypothesis — so the nearest-centroid cuts are exactly the
Lloyd midpoints of \(\operatorname{law}(T_\beta)\): self-consistency decomposes
into "cuts are Lloyd-stationary for \(T_\beta\)" plus the scalar root equation
\(E[h(T_\beta)S_\lambda]=0\). This is the gate every later scan tests.

### Theorem DS17.1 (conditional-centering obstruction; population)

Let \(P\) be atomless, in class (L), with \(ES=0\), \(E\|S\|^2<\infty\),
\(I\succ0\). Then every root-consistent strip rule has
\(I_{q,\lambda\lambda}=0\), at every tilt \(\beta\) and every \(K\ge2\).
Equivalently, **no regular tilt-consistent strip rule exists**. In particular,
there is no full-rank bounded-packet stationary rule with pairwise-distinct
projected centroids. No LCM, ellipticity, independence, or log-concavity is
assumed: (L) alone.

*Proof.* Write \(\delta=\beta-B^*\), so \(T_\beta=\hat s-\delta S_\lambda\).

**Case \(\delta=0\).** Cells are \(\hat s\)-measurable, so
\(W_b\mu_{\lambda,b}=E[S_\lambda1_{A_b}]=E[\,E[S_\lambda\mid\hat s]1_{A_b}]=0\)
by (L): \(I_{\lambda\lambda}(q)=\sum_bW_b\mu_{\lambda,b}^2=0\) directly.

**Case \(\delta>0\).** Condition on \(\hat s\): the map
\(x\mapsto h(\hat s-\delta x)\) is non-increasing (\(h\) non-decreasing). The
Chebyshev association inequality for a non-increasing transform — for an
i.i.d. conditional copy \(X'\) of \(X=S_\lambda\) given \(\hat s\),
\(2\,\mathrm{Cov}(h(\hat s-\delta X),X\mid\hat s)
=E[(h(\hat s-\delta X)-h(\hat s-\delta X'))(X-X')\mid\hat s]\le0\)
termwise — gives, with (L) killing the product of conditional means,

\[
E[h(T_\beta)S_\lambda\mid\hat s]
\le E[h(T_\beta)\mid\hat s]\,E[S_\lambda\mid\hat s]=0
\quad\text{a.s.}
\]

Integrating, \(E[h(T_\beta)S_\lambda]\le0\). Now suppose
\(I_{\lambda\lambda}(q)>0\) and root consistency. By DS17.1a the numerator is
exactly \(0\), so the conditional inequality is an equality a.s. Equality in
the termwise-nonpositive covariance forces, for \(P_{\hat s}\)-a.e. value of
\(\hat s\): \((h(\hat s-\delta X)-h(\hat s-\delta X'))(X-X')=0\) a.s., i.e.
\(h(\hat s-\delta S_\lambda)\) is a.s. constant given \(\hat s\) (if
\(S_\lambda\) is conditionally degenerate the same constancy holds trivially).
Since \(h\) takes distinct values on distinct cells, every cell indicator
\(1_{A_b}(T_\beta)\) is then a.s. \(\hat s\)-measurable, and the Case-\(\delta=0\)
computation applies verbatim: \(\mu_{\lambda,b}=0\) for all \(b\), so
\(I_{\lambda\lambda}(q)=0\) — contradiction.

**Case \(\delta<0\).** \(x\mapsto h(\hat s-\delta x)\) is non-decreasing; the
inequality reverses (\(E[h(T)S_\lambda]\ge0\)) and the same equality analysis
applies. Finally, if \(I_{\lambda\lambda}(q)=0\), the asserted conclusion
already holds (and PSD also forces \(I_{\psi\lambda}(q)=0\)); no quotient or
value of \(B_q^*\) is used in this singular case. ∎

*Consequences.* Under (L) a bounded-packet stationary rule with
\(I_q\succ0\) (full rank) **cannot have pairwise-distinct projected
centroids**: distinctness plus tie-nullity (below) would make it a genuine
tilt-consistent strip rule, forcing \(I_{\lambda\lambda}=0\) and, by
\(I_{\psi\lambda}^2\le I_{\psi\psi}I_{\lambda\lambda}\) (PSD), rank
\(\le1\). Margin-compatible stationary configurations on class (L) are
therefore all wasted-cell structures in the DS12 sense — the merged branch of
DS17.3.

### Lemma DS17.0 (pathwise DS14′)

Fix \(K\) and rational \(\kappa,c_0,\gamma>0\), and let \(P\) satisfy (M1) and
(M4). There is one probability-one event \(\Omega_0\) — the intersection,
over the countable family of rational constants and integer truncation radii,
of: the SLLN events for \(P_N\|S\|^2\) and \(P_NS\); the DS14 Step-2
Glivenko–Cantelli event over the **fixed** slab family; and the C1 uniform
moment law over the compact affine-max class with parameters bounded by
\((c_0,\kappa,\gamma,M)\) — such that on \(\Omega_0\) the following holds for
**every** (arbitrarily data-dependent, merely \(\omega\)-wise) choice of
one-point exchange-stable \(K\)-cell labelings \(z^{(N)}\), \(N\in\mathcal N\),
\(|\mathcal N|=\infty\), whose margins (M2)+(M3)+(M5) hold at
\((c_0,\kappa,\gamma)\) for every \(N\in\mathcal N\): along a sub-subsequence
of \(\mathcal N\) the companion parameters converge, and the limit \(q^*\) is a
self-consistent efficient-Voronoi quantizer with
\(\lambda_{\min}(I_{q^*})\ge\kappa\), cell masses \(\ge c_0\), and
pairwise-distinct projected centroids separated by \(\ge\gamma\).

*Proof.* DS14's five steps consume only: the margins at the indices actually
used; the uniform laws — all over fixed function classes after the audit's
repair (`AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md` §8), hence valid
simultaneously for every candidate sequence on \(\Omega_0\); and compactness
of the explicit parameter set, which supplies the convergent sub-subsequence.
Restricting the index set to \(\mathcal N\) leaves every step intact (the
sample is the same; limits along \(\mathcal N\) use the same events). No step
selects a null set depending on the sequence, so the conclusion is pathwise on
\(\Omega_0\); measurable selection is not needed because the argument runs at
fixed \(\omega\). \(\lambda_{\min}\) passes to the limit by its 1-Lipschitz
continuity in operator norm; separation and masses pass by DS14 Step 3. This
is the DS16 §"proof of (1)" quantifier idiom applied to DS14. ∎

### Theorem DS17.2 (inhabitation disproved on the whole class; eventual emptiness)

Let \(P\) be in class (L) with (M1) and (M4) and \(I\succ0\) — the DS15/DS16
law class satisfies this, and neither (S) nor (R) is needed. Then almost
surely, for every rational \(\kappa,c_0,\gamma>0\) there is
\(N_0(\omega)<\infty\) such that for all \(N\ge N_0\) **no one-point
exchange-stable \(K\)-cell labeling of the sample satisfies
(M2)+(M3)+(M5) at \((c_0,\kappa,\gamma)\) at all.** In particular OP30(a) is
**disproved**: on the entire conditionally centered class there is no
almost-sure margin-certified exchange-stable sequence, for any margins;
DS14's hypothesis set is asymptotically empty, and real margins at real
constants are covered by shrinking them to rationals.

*Proof.* Work on \(\Omega_0\). If some \((c_0,\kappa,\gamma)\)-margin-
compatible stable labeling existed for infinitely many \(N\), choose one per
such \(N\) (\(\omega\)-wise) and apply DS17.0: a limit \(q^*\) exists —
bounded-packet stationary with \(\lambda_{\min}(I_{q^*})\ge\kappa>0\) and
pairwise-distinct projected centroids. By DS14 Step 4 the limit **is** the
nearest-projected-centroid rule of its own centroids and metric (the audited
identification — not bare DS12, whose stationarity alone would tolerate
coincident centroids); for \(d_\psi=1\) the scalar metric \(S_\psi(I_{q^*})^{-1}>0\)
cancels, so \(q^*\) is a strip rule at tilt \(\beta^*=B^*_{q^*}\), genuinely
tilt-consistent, with tie sets \(P\)-null by (M4). Theorem DS17.1 gives
\(I_{q^*,\lambda\lambda}=0<\kappa\le\lambda_{\min}(I_{q^*})\le
I_{q^*,\lambda\lambda}\) — contradiction. Union over the countable rational
constants. ∎

*Corollaries (instances).* Jointly Gaussian and atomless elliptical laws with
\(\Sigma\succ0\) are in (L) (linear conditional means) and satisfy (M4)
(below), so the canonical law is covered. Product laws
\(S_\psi\perp S_\lambda\), \(ES_\lambda=0\), are in (L) via independence
(\(B^*=0\), \(\hat s=S_\psi\)) — every bimodal-nuisance product law scanned
below is an instance. For centered LCM laws with nonsingular covariance
(linear conditional means along every nondegenerate tilt, e.g. elliptical),
(L) follows by applying LCM to \(\hat s\), since
\(\operatorname{Cov}(S_\lambda,\hat s)=0\). There is also an independent
one-line second proof: cell means of a strip rule are collinear,
\(\mu_b=\theta\,t_b\) with
\(\theta=\mathrm{Cov}(S,T_\beta)/\mathrm{Var}(T_\beta)\) and
\(\mathrm{Var}(T_\beta)\ge\lambda_{\min}(I)(1+\beta^2)>0\), so
\(I_q=(\sum_bW_bt_b^2)\,\theta\theta^\top\) has rank \(\le1\) and
\(\lambda_{\min}(I_q)=0\); moreover the tilt-consistency equation on a
Gaussian is the Möbius fixed point \(\beta=(a-\beta c)/(c-\beta d)\), i.e.
\(\beta^2d-2\beta c+a=0\Longleftrightarrow\mathrm{Var}(T_\beta)=0\), with
discriminant \(4(c^2-ad)<0\): no real solution at any correlation.

*(M4) for atomless elliptical laws (\(d=2\), \(\Sigma\succ0\)).* Writing
\(S=R\Lambda U\) with \(U\) uniform on the circle: for unit \(v\),
\(P(|v^\top S-c|\le t)\le P(R\le\sqrt t\,k_1)+\sup_{r>\sqrt t k_1}
P_U(|v^\top\Lambda U-c/r|\le t/r)\le P(R\le\sqrt tk_1)+k_2t^{1/4}\) — the
angular arc a slab cuts from an ellipse of radius \(r\) has measure
\(O(\sqrt{t/r})\) even at tangency — and \(P(R\le\varepsilon)\downarrow0\) by
atomlessness at the origin: a uniform \(\varphi(t)\downarrow0\).

### Theorem DS17.3 (LCM merged-branch classification: margins survive only in wasted cells, and are never compilable)

Let \(P\) be atomless with (M4)-tie-nullity and LCM on the relevant tilt
range, and let \(q\) be bounded-packet stationary with \(W_b>0\) and
\(I_q\succ0\) (the merged branch: (M5) dropped). Then:

1. the projected centroids are **not** pairwise distinct (else DS12
   deployability (i)+(ii) reproduces \(q\) as a strip rule and the LCM rank
   bound — or Theorem DS17.1, since LCM\(\Rightarrow\)(L) — contradicts
   \(I_q\succ0\));
2. the reduced rule \(\rho'\) (merge coincident-\(e\) groups; DS12) is a
   genuine \(T_{B^*_q}\)-interval rule with \(K'\le K-1\) cells and
   \(\operatorname{rank}(I_{\rho'})\le1\), so
   \(\lambda_{\min}(I_{\rho'})=0\): **the compilable reduction never carries a
   nuisance margin**;
3. value identity: \(\Phi(q)=\sum_{\text{groups }g}W_gE[e_q(S)\mid G_g]^2\)
   with \(e_q(s)=s_\psi-B^*_qs_\lambda\) — the between-value of
   \(\operatorname{law}(e_q(S))\) on at most \(K-1\) intervals (proof:
   \(\Phi(q)=\min_B\sum_bW_b(\mu_{\psi,b}-B\mu_{\lambda,b})^2\) attained at
   \(B=B^*_q\) by the normal equation, \(e_b\) constant on groups, and
   \(\sum_{b\in g}W_be_b=E[e_q1_{G_g}]\)); always \(\Phi(q)\le v_K\) (DS15
   Lemma 1);
4. nonemptiness: on \(N(0,I_2)\) the **sign-split family** — the threshold
   cell \(\{S_\psi\ge0\}\) plus any nontrivial measurable split of the left
   half determined by \(S_\lambda\) (e.g. \(\{S_\lambda>v\}\) versus
   \(\{S_\lambda\le v\}\))
   — is bounded-packet stationary with \(B^*_q=0\), coincident left projected
   centroids, \(I_q=\operatorname{diag}(2/\pi,\,I_{\lambda\lambda}(\text{split}))\succ0\),
   \(\lambda_{\min}\) up to \(1/\pi\) (at \(v=0\)), and profiled value exactly
   \(v_2=2/\pi\) for **every** member. The population constraint class
   \(\{\lambda_{\min}(I_q)\ge\kappa\}\) of DS16's \(v^*(\kappa)\) is therefore
   **nonempty** for \(\kappa\le1/\pi\) on the canonical law — the audit's
   attainment subproblem has a nonvacuous feasible set. This proves neither
   attainment/continuity of \(v^*(\kappa)\) nor existence of empirical stable
   sequences. For this explicit family, the loss against the scalar Gaussian
   three-bin optimum is the measured quantity
   \(v_3-v_2\approx0.1732\) (\(=0.809826-2/\pi\)); it is not a lower bound for
   every stationary inhabitant.

Exact-rational verification: the \(K=3\) sign-split sibling of
`CE-DS-POP-WASTED-CELLS-001` on the same 8-atom law has
\(I_q=\operatorname{diag}(4,9/8)\), \(\Phi=4\) equal to the \(K'=2\) group
between-value, projected centroids \((-2,-2,2)\), zero first-order violations,
and singular reduced nuisance block — serialized as
`CE-DS-LCM-SIGNSPLIT-MARGIN-001` and CI-pinned. Under bare (L), conclusion 1
still holds (via Theorem DS17.1), while conclusion 2's rank collapse of the
reduced rule is LCM-scoped: a non-LCM (L)-law may leave its reduced strips
with a nonzero nuisance block, and only the fine configuration's coincidence
is forced.

The audit also records the support-minimal atomic boundary at \(N=K=3\) as
`CE-DS-LCM-SIGNSPLIT-MINIMAL-001`. It has the same coincident-centroid and
singular-reduction mechanism, but bounded-packet stationarity is vacuous on
its singleton atoms. The eight-atom fixture remains the structured symmetric
exact control; it is not globally support-minimal.

### Corollary DS17.4 (the fixed-point gate, and what it costs off the class)

For any atomless law with (M4): if OP30(a) full-triple inhabitation holds at
\((\kappa,c_0,\gamma)\), then there exist \(|\beta|\le2M/\kappa\) and a
Lloyd-**stationary** \(K\)-interval quantizer of \(\operatorname{law}(T_\beta)\)
(any centroid-midpoint fixed point, not only the optimum) whose strip rule
\(q\) satisfies the root equation \(E[h(T_\beta)S_\lambda]=0\) with
\(\lambda_{\min}(I_q)\ge\kappa\), masses \(\ge c_0\), and \(t\)-mean
separation \(\ge\gamma\). DS17.1 proves the gate empty on all of class (L).
Numerical root searches can probe but cannot decide this gate for a law. Off
the class, the mix3 scan finds a root at \(\beta=0\), cuts \(\pm1.00476\),
with measured \(I_{\lambda\lambda}=\lambda_{\min}=1.7364\) and value equal to
the efficient interval optimum to the reported tolerance. This is per-law
evidence that a margin may have negligible price; it is not a general theorem
and does not establish the empirical transfer required by OP29(a).

### Self-adversarial notes (protocol G)

- **Strictness and ties.** Finite labelings may carry exact ties and
  duplicates; nothing in DS17.2 constrains them — stability is a hypothesis.
  Population tie sets are (M4)-null; the equality analysis in DS17.1 handles
  conditionally degenerate \(S_\lambda\) explicitly.
- **Singleton/empty cells.** Excluded at the population limit by (M2); finite
  singletons are allowed and irrelevant.
- **Duplicate scores.** Allowed; DS14's Steps 1–3 already cover split atoms.
- **Singular information.** \(I\succ0\) is a hypothesis on the law;
  post-move singular states never enter (DS13 covers them upstream in DS14).
- **Nuisance singularity.** The conclusion *is* nuisance singularity; the
  margin hypothesis (M3) uses \(\lambda_{\min}\le I_{\lambda\lambda}\), so the
  contradiction is against the weaker block bound — no gap.
- **Atomic laws.** DS17.1 needs atomlessness through the strict
  increase of interval means and DS12/DS14's own hypotheses; the 8-atom
  fixture verifies algebra, never the population statement (DS12 necessity is
  vacuous on atoms — wasted-cells precedent). The audit's support-minimal
  three-atom fixture makes that boundary explicit.
- **Hidden compactness.** Only DS14's audited explicit compact class is used.
- **First-order-to-finite jumps.** None: the finite half is DS14 verbatim;
  DS17 adds population algebra plus the pathwise quantifier.
- **Empirical-to-population jumps.** Only DS17.0's fixed-class events — the
  audit-repaired uniform laws; no new uniform law is introduced.
- **Score-estimation error.** Excluded; exact scores (P2 unchanged).
- **New-event extension.** DS17 strengthens the refusal: on class (L) there
  is asymptotically nothing to compile in the certified branch; no new
  inductive claim is made.
- **Why the census witnesses don't contradict DS17.2.** The margin-retaining
  stable states at \(N\le14\) (`CE-DS-STABLE-MARGIN-RETAINING-001`) are
  pre-asymptotic: DS17.2's \(N_0(\omega)\) is finite but not uniform, and the
  grid laws are atomic emulations. The theorem predicts their margins die as
  \(N\) grows — exactly the DS16 library measurement (funnel at
  \(N=100\)–\(1000\)) and the geometry scan below.

### Measured (gate scans; falsification evidence that failed to falsify)

Instrument `py/ds_stable_basins.py` (closed-form Gaussian-mixture strip
moments, validated in selftest against the public
`scorequant.IntegrationSource` tensor Gauss–Legendre quadrature at
\(10^{-9}\) and the exact 8-atom rationals; artifacts with full provenance
under `WORK/artifacts/DS-STABLE-BASINS/`):

- **Gaussian laws** (\(\rho\in\{0,0.6,0.9\}\) and an anisotropic case): at
  every tilt on a 241-point grid, \(\lambda_{\min}(I_q(\beta))\le2.4\times10^{-16}\)
  (exact rank one); the tilt-residual is zero-free (discriminant \(<0\));
  the Möbius iteration never converges (elliptic orbit) — row
  N-DS-BASINS-GAUSS.
- **Product bimodal (L)-laws** (\(m\in\{0.75,1,1.5,2,3\}\), \(s=0.4\)): the
  branch-tracked root scan over \(\beta\in[-2.5,2.5]\), tracking up to 3
  Lloyd-stationary branches per tilt (asymmetric mode-splitting branches
  included), found **zero** self-consistent roots in that finite window and
  branch set. The window is not the full compact gate range for an unstated
  \(\kappa\), and the branch cap cannot exclude isolated roots.
- **Dependent (L)-laws** `xcorr(c)` (equal mixtures of \(\pm c\)-correlated
  standard Gaussians, \(c\in\{0.5,0.8,0.95\}\); (L) by branch symmetry, LCM
  fails off \(\beta=0\)): zero roots — both scans in row
  N-DS-BASINS-CLASS-L-ROOTS. Eight
  (L)-laws, three structural families, zero gate inhabitants: the theorem's
  prediction, tested before its proof was trusted.
- **Sign-split family** on \(N(0,I_2)\): \(\Phi-2/\pi=0\) to machine
  precision across the split parameter \(v\in[-1,1]\), \(I_{\psi\lambda}=0\),
  \(\lambda_{\min}\) maximal \(=1/\pi\) at \(v=0\); \(v_3-v_2=0.173206\) —
  row N-DS-BASINS-SIGNSPLIT.
- **mix3 (off-class control):** one root found — \(\beta=0\), cuts
  \(\pm1.00476\), \(\lambda_{\min}=1.7364\), value \(2.68936=v_3\) to
  \(10^{-6}\) (price \(\approx0\)), zero Monte-Carlo rule violations; the
  finite-difference family Hessian at the root has gradient \(0\) and
  eigenvalues \((-2.146,-0.258,-0.186)\): a **strict local maximum** of the
  population value in the rule family, the second-order input any off-class
  transfer theorem (OP29(a)) would consume — row N-DS-BASINS-MIX3.
- **Seeded library ascent at scale** (public API, \(N\in\{300,1000,3000\}\),
  3 reps): all 63 terminals exchange-stable. gauss06:
  \(\lambda_{\min}\in[5\times10^{-5},0.012]\) with \(N\hat I_{11}\approx0.3\)–\(7\)
  at every seed — the disproof's finite face. mix3: the
  population-fixed-point seeding terminates at the **same** terminal as the
  efficient and k-means seeds in 9/9 runs, with \(\lambda_{\min}=1.73\)–\(1.83\)
  and log-gap \(\le10^{-5}\) at \(N\ge1000\); one random-seed run stranded at
  a degenerate *inferior* terminal (\(\lambda_{\min}=5\times10^{-4}\), gap
  \(0.21\)) — off-class margins are free at the good optimum, but bad local
  terminals still exist — row N-DS-BASINS-LIBRARY.
- **Geometry of the DS16 terminals** (420 recorded ascent terminals plus the
  margin-retaining witness): the witness agrees **exactly** with its own
  companion rule at \(N=8\) (\(\hat B^*=0.497\), separation \(0.325\)); on
  centered06 only \(2\%\) of stable terminals are companion-exact (median
  disagreement \(18\%\), median \(\lambda_{\min}=0.034\)), on mix3 \(61\%\)
  are exact (median \(\lambda_{\min}=1.06\)) — the class boundary of DS17.1
  visible in the finite states — row N-DS-BASINS-GEOMETRY.

### Verdict: OP30(a) and the compile consequence

- **Disproved, on the whole class.** On every (L)+(M1)+(M4) law — all of
  DS15/DS16's class, jointly Gaussian and elliptical laws in particular — the
  margin-certified branch is almost surely **eventually empty**: not merely
  uninhabited by sequences, but devoid of any single margin-compatible
  exchange-stable labeling for all large \(N\). The DS14 companion path on
  this class is vacuous asymptotically; `compile_quantizer`'s refusal needs no
  certificate carve-out there, and a margin-*constrained* solver (OP7/OP30(c))
  cannot terminate at ordinary-stable margin states eventually — any terminal
  it certifies is stable only under the constraint.
- **The merged branch survives but compiles to nothing.** Dropping (M5),
  margin-compatible stationary configurations exist on the canonical law
  (sign-split family, \(\lambda_{\min}\) up to \(1/\pi\)), all wasted-cell
  structures whose compilable reduction has \(\lambda_{\min}=0\) and whose
  value is pinned at \(v_2\) in every scanned instance — retention is bought
  only by spending cells on profiled-information-free splits.
- **Off the class the population gate can be inhabited and may be cheap.** mix3's gate
  inhabitant is the efficient optimum itself (\(\lambda_{\min}=1.74\), price
  \(\approx0\)) in the measured family. This one law does not support a
  general claim that certification is free. The deployment-relevant remainder
  moves to OP29 branch (a)
  (non-centered laws) with the DS17.4 gate identity as its population test,
  and to the DS16 attainment question, whose feasible class DS17.3(4) proves
  nonempty.
- **Deployment statement (required by the packet).** An *inhabited DS14
  sequence*: impossible on class (L) (this theorem). A *finite diagnostic*:
  still legitimate as a diagnostic (the \(N=8\) witness is even
  companion-exact) but now known to be transient on the class — it certifies
  nothing asymptotic. A *constrained terminal*: the only object a
  margin-constrained solver can deliver on the class, and it is **not**
  ordinary-exchange-stable eventually; any future `ProfiledMarginPolicy`
  surface must present it as constrained, priced (\(\hat v_K-\hat\Phi_s\)),
  and non-inductive on this class.

Stop condition **2 (disproved)** of the packet is hit on the packet's own
class, with the obstruction's boundary serialized
(`CE-DS-LCM-SIGNSPLIT-MARGIN-001`: (M5) is load-bearing) and the off-class
escape measured (mix3 root). The isolated remainder is OP29(a)'s non-centered
inhabitation/transfer, gated by DS17.4, plus DS16's constrained-value
attainment — recorded in the OP30 rescope.

## DS18. Exact off-class global basin and empirical stable transfer — [PROJECT-PROVED; (d_\psi=d_\lambda=1), (K=3)]

**Claims:** DS-NONCENTERED-GLOBAL-BASIN-TRANSFER

DS17 left two logically separate gaps off class (L): exhibit a regular root
with fixed margins, and show that an empirical sequence can inhabit it despite
boundary-scale one-point gains. Both gaps are resolved here for one explicit
bounded score law. The transfer is through **finite global profiled optima**;
it is not a theorem that raw population labels are finite terminals, nor a
selection theorem for exchange ascent.

### The named law and exact population rule

Let \(X,Z\stackrel{\mathrm{iid}}\sim\operatorname{Unif}[-1,1]\) and define

\[
S_\psi=X,\qquad S_\lambda=3X^2-1+Z.
\]

Then \(ES=0\), \(E\|S\|^2<\infty\), and

\[
I_{\rm full}=E[SS^\top]
=\begin{pmatrix}1/3&0\\0&17/15\end{pmatrix}\succ0.
\]

The full-data regression slope is \(B^*=0\), hence the efficient score is
\(\hat s=X\). The law is strictly outside (L), because

\[
E[S_\lambda\mid\hat s=X]=3X^2-1\ne0\quad\text{a.s.}
\]

It is atomless and satisfies (M4). Indeed its density is (1/4) on

\[
\{(x,y):|x|\le1,\ |y-(3x^2-1)|\le1\}
\subset[-1,1]\times[-2,3].
\]

For every unit \(v\), a width-\(2t\) slab intersects the bounding rectangle in
area at most \(2t\sqrt{29}\); therefore one may take
\(\varphi(t)=\min(1,\sqrt{29}t/2)\downarrow0\).

Let \(q^*\) be the three-cell \(X\)-interval rule with cuts
\((-1/3,1/3)\). Direct integration gives

\[
W_b=1/3,\qquad
\mu_{\psi,b}=(-2/3,0,2/3),\qquad
\mu_{\lambda,b}=(4/9,-8/9,4/9),
\]

and hence

\[
I_{q^*}
=\begin{pmatrix}8/27&0\\0&32/81\end{pmatrix},\qquad
\Phi_{D_s}(q^*)=8/27.
\]

At \(\beta=0\), the projected cell means are
\((-2/3,0,2/3)\), whose midpoints are exactly the declared cuts. Thus \(q^*\)
is Lloyd-stationary for \(T_0=X\), and the DS17.4 residual is

\[
E[h(X)S_\lambda]=I_{\psi\lambda}(q^*)=0.
\]

Since \(I_{\lambda\lambda}(q^*)=32/81>0\), this is a **regular** root with
\(B^*_{q^*}=0\), not a singular numerator root. Its exact gate margins are

\[
\min_bW_b=1/3,\qquad
\lambda_{\min}(I_{q^*})=8/27,\qquad
\min_{b\ne b'}|t_b-t_{b'}|=2/3.
\]

In particular the fixed constants
\((c_0,\kappa,\gamma)=(1/4,1/4,1/2)\) have strict slack. The root also obeys
the DS17 compact tilt bound trivially because \(\beta=0\). Relative to the
unbinned profiled information \(1/3\), its scalar \(D_s\) retention is

\[
\eta_{D_s}=\frac{8/27}{1/3}=\frac89.
\]

### Theorem DS18.1 (unique strict population attainer)

Among every measurable regular three-cell quantizer of \(S\), \(q^*\) is the
unique population \(D_s\) maximizer up to cell relabeling. Moreover it is
strictly isolated in decision distance: for every \(\varepsilon>0\) there is
\(\delta(\varepsilon)>0\) such that

\[
\min_{\pi}\sum_bP(A_b\mathbin\triangle A^*_{\pi(b)})\ge\varepsilon
\quad\Longrightarrow\quad
\Phi_{D_s}(q)\le 8/27-\delta(\varepsilon).
\]

*Proof.* DS11's variational form, evaluated at \(B=0\), and the scalar
nearest-centroid reduction from DS15 Lemma 1 give, for every \(q\),

\[
\Phi_{D_s}(q)
\le \sum_bW_bE[X\mid q=b]^2
\le v_3(\operatorname{Unif}[-1,1]).
\]

For a uniform interval of length \(\ell\), the within-cell squared-error
contribution (including density \(1/2\)) is \(\ell^3/24\). The three interval
lengths sum to \(2\), so strict convexity gives the unique minimum at
\(\ell_1=\ell_2=\ell_3=2/3\). Its total error is \(1/27\), and therefore

\[
v_3=E[X^2]-1/27=1/3-1/27=8/27.
\]

The exact calculation above shows \(q^*\) attains both bounds with a regular
nuisance block. Equality in the nearest-centroid reduction forces assignment
to a nearest member of the attaining scalar codebook; the uniform law charges
neither midpoint, and the scalar codebook is unique, so \(q=q^*\) a.s. up to
labels. The quantitative isolation is the scalar grouping-rigidity argument
of DS15 Lemma 3, specialized to bounded \(X\): otherwise a sequence a fixed
decision distance away with values tending to \(8/27\) would have centroid
subsequences converging to the unique scalar optimum and its cells would
converge to the equal intervals, a contradiction. ∎

### Theorem DS18.2 (almost-sure exact empirical inhabitation)

Let \(S_1,S_2,\ldots\) be i.i.d. from the named law, with equal weights
\(1/N\) and **without sample centering**. For every sufficiently large \(N\),
let \(z^{(N)}\) be any exact global maximizer of ordinary in-bin profiled
\(D_s\) over the finite labelings with three nonempty cells and
\(\hat I^z_{\lambda\lambda}>0\). Then, on one probability-one event, after
relabeling,

\[
P_N(z^{(N)}\ne q^*)\to0,\qquad
\hat I_N(z^{(N)})\to I_{q^*},\qquad
\hat\Phi_{D_s}(z^{(N)})\to8/27.
\]

Consequently all sufficiently large \(z^{(N)}\) are exact ordinary
one-point exchange-stable and satisfy (M2)+(M3)+(M5) at the fixed constants
\((1/4,1/4,1/2)\). Their companion slopes tend to \(0\), their projected
centroids tend to \((-2/3,0,2/3)\), and their companion rules converge to the
deployable population rule \(q^*\).

*Proof.* Label the sample by the fixed cuts of \(q^*\), writing the result as
\(z_N^*\). The SLLN on these three fixed cells gives
\(\hat I_N(z_N^*)\to I_{q^*}\), so \(z_N^*\) is feasible eventually and
\(\hat\Phi_{D_s}(z_N^*)\to8/27\).

For any finite labeling \(z\), the same variational evaluation at \(B=0\)
and scalar reassignment used above are exact sample algebra:

\[
\hat\Phi_{D_s}(z)
\le \operatorname{btw}_N(X;z)
\le \hat v_{3,N}(X),
\]

where \(\hat v_{3,N}(X)\) is the best three-group scalar between-value and is
attained by intervals of the sorted \(X_i\). Bounded scalar quantization
consistency (the scalar part of DS15 Proposition 5) gives
\(\hat v_{3,N}(X)\to8/27\) a.s. Global optimality therefore squeezes

\[
8/27\leftarrow\hat\Phi_{D_s}(z_N^*)
\le\hat\Phi_{D_s}(z^{(N)})
\le\operatorname{btw}_N(X;z^{(N)})
\le\hat v_{3,N}(X)\to8/27.
\]

The empirical form of DS15's scalar grouping rigidity, now simpler because
\(|S|\) is bounded and the uniform optimum is unique, yields
\(P_N(z^{(N)}\ne q^*)\to0\) after relabeling. The fixed-rule SLLN plus this
vanishing disagreement gives convergence of every cell mass and score moment,
hence of the information, slope, projected centroids, and objective. The
strict limiting margins admit the displayed rational lower constants.

Finally, an exact global feasible labeling has no admissible improving
one-point relocation, so it is exact ordinary exchange-stable. This last step
does not compare stochastic boundary distances with \(1/N\): globality signs
every exact move at once. ∎

### Boundary, scope, and deployment consequence

The stronger finite assertion is false. On the support-minimal movable sample
`CE-DS-NONCENTERED-POPULATION-CUT-UNSTABLE-001`, the raw \(q^*\) labels have
an exact improving gain \(37/14608\). Thus \(O(1/N)\)-scale boundary effects
are real; DS18.2 bypasses them through finite global selection rather than
pretending they vanish pointwise.

The theorem proves that the DS14 margin-certified branch is genuinely
inhabited off (L), and gives a law-specific theorem-backed limiting companion
rule. It does **not** prove that exchange ascent finds the basin, that every
isolated DS17 root persists, that mix3 has a unique root, or that the result is
robust to law/score estimation. No library compile surface follows before a
fresh independent audit and a practical selection theorem.

Self-adversarial checks: population ties are null; empirical empty cells are
excluded by feasibility and disappear under mass convergence; the limiting
nuisance block is regular; bounded support supplies uniform integrability and
(M4); duplicate full scores occur with probability zero; no first-order move
approximation is used; exact scores and equal weights are load-bearing; no
sample centering is performed. The exact root, exhaustive \(N\le10\)
falsification, unequal-weight/duplicate/tie/tiny-cell/singular controls, and
the boundary fixture are reproduced by
`py/ds_noncentered_global_basin.py`.

**Stop-condition verdict.** **PROVED for an explicit off-(L) law.** A regular
DS17 root with fixed positive margins is the unique strict population global
basin, and every sequence of finite global profiled optima transfers almost
surely to exact exchange-stable empirical inhabitants of that basin.
