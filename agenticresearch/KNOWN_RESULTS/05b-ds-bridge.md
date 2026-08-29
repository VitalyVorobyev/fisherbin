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
§8.) The behavior at global optima is tied to OP28 and remains open.

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
**not** automatic at finite optima: exhaustively verified global optima at
\(N\le18\) regularly carry singleton cells (the audit's own fully exact
\(N=10\) scan reproduces this), and the tie fixture has exactly
coincident projected centroids (OP28 records the conjecture that the margins
hold asymptotically for light-tailed atomless laws; the measured suite is
N-DS-BRIDGE-TREND). (ii) \(v^*\) is the optimum over the margin-compatible
geometric class; whether it equals the unrestricted population supremum over
all measurable quantizers (and whether that supremum is attained) remains open
in C2. (iii) Everything is for exact scores; estimated-score robustness is the
P2 programme.

---
