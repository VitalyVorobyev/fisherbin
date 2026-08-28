# Publication-grade audit of the profiled Ds population bridge

**Claims:** `DS-PROFILED-VARIATIONAL` (DS11), `OPEN-DS-POP-COMMON-METRIC` (DS12),
`DS-EXCHANGE-LEVERAGE-BOUND` (DS13), `OPEN-DS-FINITE-POP-BRIDGE` (DS14)
**Audit:** `AUDIT-DS-POPULATION-BRIDGE`
**Date:** 28 August 2026
**Result:** DS12 and DS13 verified with hardened assumptions; DS11 verified with
hardened assumptions and its core identity re-attributed to classical prior art
(Krein / Anderson / Li–Mathias); DS14 verified as a conditional theorem after
hardening its assumptions and supplying two missing arguments (the fixed-class
slab Glivenko–Cantelli step and the general-\(d_\psi\) neutral-split value
identification for the merged variant). No refutation was found.

## 1. Target statement

Throughout, \(S\) is the \(d\)-dimensional score with parameter split
\(\theta=(\psi,\lambda)\), \(d=d_\psi+d_\lambda\); a labeling/quantizer has cell
masses \(W_b\), moments \(m_b\), centroids \(\mu_b=m_b/W_b\), and binned
information \(I_q=\sum_b m_bm_b^\top/W_b\) (U1). \(S_\psi^+(I)=
I_{\psi\psi}-I_{\psi\lambda}I_{\lambda\lambda}^+I_{\lambda\psi}\) is the
generalized profiled information and \(F_s=\log\det S_\psi\).

- **DS11.** For PSD \(I\), with \(V(B)=I_{\psi\psi}-BI_{\lambda\psi}
  -I_{\psi\lambda}B^\top+BI_{\lambda\lambda}B^\top\):
  \(S_\psi^+(I)=\min_BV(B)\) in the Loewner order, attained exactly at the
  solutions of \(BI_{\lambda\lambda}=I_{\psi\lambda}\). Statistically, for
  **centered** scores \(V(B)=\operatorname{Var}(E[S_\psi-BS_\lambda\mid Z])\).
  Consequences: the exact efficient-score-domination gap, refinement
  monotonicity with a neutrality characterization, wasted-cell/global-tie
  phenomena, identifiability up to neutral splits.
- **DS12.** For atomless \(P\), \(E[S]=0\), \(E\|S\|^2<\infty\), \(W_b>0\),
  \(I_q\succ0\): bounded-packet stationarity of \(\Phi_{D_s}\) is equivalent to
  a.e. assignment to the nearest projected centroid \(e_b=C\mu_b\) of
  \(e(s)=Cs\) in the \(S_\psi(I_q)^{-1}\) metric
  (\(G_s=C^\top S_\psi^{-1}C\), \(C=[\mathrm{Id},-B_q^*]\)), plus the
  deployability characterization.
- **DS13.** Finite level, positive weights, \(I\succ0\),
  \(I_{\lambda\lambda}\succ0\): at any one-point exchange-stable profiled-Ds
  state, every admissible move (non-singleton source) satisfies
  \(s_{aa}-s_{bb}\le\beta_i\,q_{aa}q_{bb}\le w_i\,q_{aa}q_{bb}\).
- **DS14.** Under (A1)–(A5) (i.i.d. atomless centered law with finite second
  moment; mass, conditioning, slab, and separation margins), one-point
  exchange-stable finite Ds labelings are asymptotically geometric; along
  parameter-convergent subsequences their companion rules converge to
  self-consistent, bounded-packet-stationary efficient-Voronoi quantizers with
  convergent values; global finite optima converge in value to the population
  optimum over the margin-compatible geometric class; without (A5) the same
  holds for the reduced (merged) rule.

## 2. Criterion and problem level

- Criterion: profiled \(D_s\), \(F_s(I)=\log\det I-\log\det I_{\lambda\lambda}\).
- Levels: `universal` (DS11), `population_quantizer` (DS12),
  `finite_assignment` (DS13), `empirical_to_population` (DS14).
- Decision variables: a matrix minimization (DS11), a measurable partition
  (DS12), a hard finite labeling (DS13), a sequence of labelings (DS14).
- Score oracle: exact scores throughout; estimated scores are the P2 programme.

## 3. Status before the audit

All four claims were `project_proved` (internal). No audit node existed.
`OPEN-DS-FINITE-POP-BRIDGE` carried the warning "Publication-grade audit
pending: WORK/active/AUDIT-DS-POPULATION-BRIDGE.md" on top of its
conditional-margins caveat.

## 4. Dependencies rechecked

Every dependency was re-derived, not merely cited:

1. `FI-QUANT-IDENTITY` (U1): \(I_q=\sum_bW_b\mu_b\mu_b^\top\) equals
   \(\operatorname{Var}(E[S\mid Z])\) **only for centered scores**; the audit
   pushes this hypothesis explicitly into DS11 (see §8).
2. `RANK-CEILING` (U4): \(\operatorname{rank}(I_q)\le\min(d,K-1)\) for centered
   scores. Exercised concretely: a centered \(d=2,K=2\) probe has **no**
   feasible state at all, so DS13-type claims are vacuous there (consistent
   with DS9).
3. `GENERAL-FIRST-VARIATION` (G1) and `D-RANK2-MOVE` (D2): re-derived. The
   per-cell moment update is \(\Delta_a=\alpha u_au_a^\top-wss^\top\) and
   \(\Delta_b=wss^\top-\beta u_bu_b^\top\); the \(wss^\top\) terms cancel only
   in the sum, giving \(\Delta I=\alpha u_au_a^\top-\beta u_bu_b^\top\). D2
   additionally needs positive weights and \(W_a>w\).
4. `D-LOGDET-GAIN` (D3): re-derived from the \(2\times2\) capacitance
   determinant \(\det(\mathrm{Id}_2+CU^\top I^{-1}U)\); the identity is purely
   algebraic and holds regardless of post-move definiteness.
5. `DS-GRADIENT-EFFICIENT-SEMIMETRIC` (DS2): \(G_s=C^\top S_\psi^{-1}C
   \succeq0\) of rank \(d_\psi\) re-derived from the block inverse.
6. `DS-EXACT-MOVE-ORACLE` (DS3), `DS-OKN-BOUND` (DS6),
   `DS-EFFICIENT-SCORE-DOMINATION` (DS7), `DS-FULL-PROFILE-K-LE-D-SINGULAR`
   (DS9): rechecked as used.
7. `CONSISTENCY-RESTRICTED-AFFINE` (C1): its recorded proof is one sentence.
   The audit does **not** lean on it: the instance DS14 needs — a uniform LLN
   for cell masses and first moments over the compact affine-max class — is
   re-derived directly in §8 (VC-subgraph class, integrable envelope
   \(\|s\|\)), so DS14's chain has no unproved analytic dependency.

No circularity: DS14 uses DS13 (finite), DS12 (population), DS11(b) (values),
and the ULLN; none of these uses DS14.

## 5. Nearest literature and transfer boundary

**DS11's boxed identity is classical prior art, not a project theorem.**
Li & Mathias, *Extremal Characterizations of the Schur Complement and Resulting
Inequalities*, SIAM Review 42(2):233–246 (2000), Theorem 2.2: for positive
semidefinite \(H\),
\([Z\,|\,\mathrm{Id}]\,H\,[Z\,|\,\mathrm{Id}]^*\;\ge\;S(H)
=H_{22}-H_{12}^*H_{11}^\dagger H_{12}\)
in the Loewner order for every \(Z\), with equality **iff**
\((Z+H_{12}^*H_{11}^\dagger)H_{11}=0\). Substituting \(Z=-B\), \(H_{11}
=I_{\lambda\lambda}\), \(H_{22}=I_{\psi\psi}\) yields DS11's identity verbatim
— Moore–Penrose extension, Loewner minimality, and the exact attainment set
\(BI_{\lambda\lambda}=I_{\psi\lambda}\) included. Li–Mathias attribute the
characterization to M. G. Krein (1947) and note Anderson's independent shorted
operator (1971; Anderson–Trapp 1975) and Butler–Morley. The statistical
reading is equally classical: the efficient score
\(\ell_\psi-I_{\psi\lambda}I_{\lambda\lambda}^{-1}\ell_\lambda\) with variance
the Schur complement is standard semiparametric/nuisance theory (e.g. van der
Vaart 1998, §25.4; Bickel–Klaassen–Ritov–Wellner 1993). **What remains
project-level in DS11:** the transfer to binned scores via U1, the
quantizer-level corollaries (a)–(d) (exact domination gap, refinement
neutrality, wasted cells/ties, reduced identifiability), and the observation
that the pseudo-inverse extension leaves the in-bin formulation (DS9).

**For DS12–DS14 the targeted search again found no direct equivalent — a
search gap, not a novelty claim.** Independent queries (adaptive/Mahalanobis
quantizer consistency; determinant-criterion partition consistency; profiled
Fisher binning in HEP) confirmed the packet's triangulation:

- **Pollard (1981, 1982)**, Abaya–Wise, Lember, Linder: the "uniform LLN +
  argmin continuity" skeleton transfers as a template; every result assumes a
  fixed source-independent metric and per-point additive distortion — no
  solution-dependent semimetric, no determinant/Schur functional of aggregated
  cell moments.
- **Graf–Luschgy (2000)**: uniform LLN over Voronoi-type classes for additive
  distortion; nearest published analogue of the ULLN instance re-derived here.
- **Sabin–Gray (1986)**: set convergence of empirical fixed points of the
  generalized Lloyd algorithm — the closest structural precedent for DS14's
  shape; convex additive distortions only, no margins, no Schur
  self-consistency.
- **HEP inference-aware binning** (INFERNO, de Castro–Dorigo 2018; binned
  Poisson-likelihood NN optimization, Wunsch et al. 2020; "Learning to bin",
  2026): optimizes profiled/Asimov Fisher information through soft binning —
  the practice DS14 would certify — but supplies algorithms only, no
  finite-to-population consistency theorems.
- **Margin conditions** (Mammen–Tsybakov; Levrard): conceptual template for
  (A4); fast-rate mechanics rest on a squared-distortion Pythagorean identity
  with no log-det analogue, so no rates transfer.

## 6. Counterexample search

Independent suite `py/audit_ds_population_bridge.py` (pure-stdlib
`fractions.Fraction`; no numpy; no code shared with the researcher's
`py/ds_population_bridge.py`; every claim-deciding quantity exact):

- **DS11 (`ds11` mode):** 400 deterministic pseudo-random PSD instances,
  \(d_\psi,d_\lambda\in\{1,2\}\), 58 with exactly singular nuisance blocks and
  multiple normal-equation solutions. Zero failures of: normal-equation
  consistency (the PSD range condition), agreement of \(V\) across distinct
  solutions, the exact completion-of-squares identity, Loewner minimality, and
  \(V(B_0)=\) Schur complement on nonsingular blocks. The mode also carries the
  pseudo-inverse discontinuity witness
  \(I_{\lambda\lambda}^{(k)}=\mathrm{diag}(1,1/k)\),
  \(I_{\psi\lambda}=[1,1]\Rightarrow B^*_k=[1,k]\), demonstrating why DS11(a)'s
  \(K\to\infty\) claim needs a nonsingular full nuisance block.
- **DS13 (`ds13` mode):** exhaustive exact enumeration of **all** canonical
  surjective labelings, with the leverage bound checked at **every** one-point
  exchange-stable state (the theorem claims all stable states, not just
  optima). Five adversarial datasets: duplicates with unequal weights
  (\(d=2,K=3\)); nuisance-symmetric uncentered (\(K=2\)); nuisance-symmetric
  centered (\(K=3\)); **vector nuisance** \(d=3,d_\psi=1,d_\lambda=2\); and
  **vector POI** \(d=3,d_\psi=2,d_\lambda=1\) — the researcher's own evidence
  never left scalar nuisance. Totals: 1,707 feasible states, 171 stable
  states, 1,748 admissible-move checks, **0 violations**, worst gap/bound
  ratio \(1/2\); 230 checked moves had exactly singular destination nuisance
  blocks (the degenerate edge case is exercised, not just argued). Two
  instructive structural results: the centered \(K=2\) probe is completely
  infeasible (U4), and the uncentered \(\lambda\)-centered \(K=2\) landscape is
  exactly flat (every feasible state has profiled value \(m_{\psi,\rm tot}^2\);
  all 106 states are global optima), a maximal-tie stress case the bound
  survives.
- **Fixtures (`fixtures` mode):** both packet fixtures re-verified from raw
  scores through an independent code path.
  `CE-DS-DEGENERATE-GLOBAL-TIE-001`: 966 partitions, 964 feasible, optimum
  \(1083/4096\), tie multiplicity 31, every tie refines the reduced
  bipartition and has coincident projected centroids, gap to next value
  \(237/16640\), pseudo-inverse value of the infeasible refinement
  \(1191/4096\). `CE-DS-POP-WASTED-CELLS-001`: profiled \(=4\), nuisance block
  \(9/4\) vs singular coarsening, zero first-order violations, projected
  centroids \((-2,-2,2,2)\). All exact quantities match the researcher's.
- **Margins (`margins` mode):** three own \(N=10,K=3\) datasets (integer LCG,
  exactly centered), globally optimized by **full exact enumeration — no float
  screen, no top-\(k\) cut**. One of three exact global optima carries a
  singleton cell, independently reconfirming that (A2) is not automatic
  (OP28); DS13 and DS6 hold at all optima; separations positive.

**Researcher-evidence weaknesses documented (not relied upon).** The
`trend`-mode "exhaustively verified global optima" in
`py/ds_population_bridge.py` are float-screened (top 64 by float objective,
then exact re-rank) with an \(\hat I_{\lambda\lambda}>10^{-9}\) float filter;
given that exact optima occur in 31-fold tie classes, a top-64 screen is not
obviously safe, and `analyze` re-derives scores from numpy RNG streams rather
than stored data. DS13's KNOWN_RESULTS evidence sentence ("2,378 moves at 100
optima") was stale against the ledger (2,706 at 110, plus 32 fixture moves);
fixed in this audit. The N-DS-BRIDGE-TREND suite runs on scores rounded to
multiples of \(1/8\) — an atomic law — which is fine for the finite claims it
supports but is not evidence about atomless-law margins. None of this affects
the theorems; the audit's own exact evidence is independent.

## 7. Algebraic reduction

**DS11.** \(V(B)=[\,\mathrm{Id}\;{-B}\,]\,I\,[\,\mathrm{Id}\;{-B}\,]^\top\).
For PSD \(I\), \(\ker I_{\lambda\lambda}\subseteq\ker I_{\psi\lambda}\)
(if \(I_{\lambda\lambda}x=0\) then \([0;x]^\top I[0;x]=0\), hence
\(I[0;x]=0\)), equivalently \(\operatorname{range}(I_{\lambda\psi})\subseteq
\operatorname{range}(I_{\lambda\lambda})\); so \(B_0=I_{\psi\lambda}
I_{\lambda\lambda}^+\) solves \(B_0I_{\lambda\lambda}=I_{\psi\lambda}\). For
**any** solution \(B_0\), using \(I_{\lambda\lambda}B_0^\top=I_{\lambda\psi}\)
twice, \(V(B)-V(B_0)=(B-B_0)I_{\lambda\lambda}(B-B_0)^\top\succeq0\), and
\(V(B_0)=I_{\psi\psi}-B_0I_{\lambda\psi}
=I_{\psi\psi}-I_{\psi\lambda}I_{\lambda\lambda}^+I_{\lambda\psi}\) because
\(I_{\lambda\psi}=I_{\lambda\lambda}I_{\lambda\lambda}^+I_{\lambda\psi}\).
Equality holds iff \((B-B_0)I_{\lambda\lambda}=0\), i.e. exactly on the
normal-equation solution set — matching Li–Mathias (2.2).

**DS13.** With \(U=[u_a,u_b]\), \(Cq=\mathrm{diag}(\alpha,-\beta)\),
\(\det(I+\Delta I)/\det I=\det(\mathrm{Id}_2+CqU^\top I^{-1}U)
=(1+\alpha q_{aa})(1-\beta q_{bb})+\alpha\beta q_{ab}^2\), and identically for
\(I_{\lambda\lambda}\) with \(r_{xy}\). Expanding the stability inequality and
substituting \(s_{xx}=q_{xx}-r_{xx}\) (from \(G_s=I^{-1}
-E_\lambda I_{\lambda\lambda}^{-1}E_\lambda^\top\)) gives
\(\alpha s_{aa}-\beta s_{bb}\le\alpha\beta[(q_{aa}q_{bb}-q_{ab}^2)
-(r_{aa}r_{bb}-r_{ab}^2)]\); both dropped terms are correctly signed
(\(q_{ab}^2\ge0\); Cauchy–Schwarz in the \(I_{\lambda\lambda}^{-1}\) inner
product). Division by \(\alpha>0\) with \(\beta\le w_i\le\alpha\) and
\(s_{bb}\ge0\) yields the bound. \(\alpha>0\) needs positive weights and
\(W_a>w_i\) (non-singleton source with positive co-weight).

**DS12 packet dictionary.** Relabeling \(E\subseteq A_a\) with
\(\varepsilon=P(E)\), \(\bar s\) its barycenter, maps
\((W_a,m_a)\mapsto(W_a-\varepsilon,m_a-\varepsilon\bar s)\) and
\((W_b,m_b)\mapsto(W_b+\varepsilon,m_b+\varepsilon\bar s)\) — exactly the D2
update of the weighted point \((\bar s,\varepsilon)\); since \(I_q\) is a
function of \((W_b,m_b)\) alone (U1), the finite relocation algebra transfers
exactly, not merely approximately.

## 8. Proof / counterexample / conditional result

**DS11 — verified with hardened assumptions.** The core identity is complete
(§7) and is classical (§5). Hardened/supplied:

- *(Centering.)* \(\operatorname{Var}(E[S_\psi-BS_\lambda\mid Z])=V(B)\)
  requires \(E[S]=0\); the raw claim listed only "binned information PSD". The
  matrix identity needs no centering; the statistical reading does.
- *(a, \(K\to\infty\).)* \(B^*_{q_K}\to B^*_{\rm full}\) crosses the
  Moore–Penrose discontinuity (witness in §6). Repair: \(\widehat S\) is only
  defined when \(I^{\rm full}_{\lambda\lambda}\succ0\) (DS7); then
  \(I_{q_K}\to I_{\rm full}\) (Lévy's upward martingale convergence in
  \(L^2\), refining partitions generating the Borel \(\sigma\)-field, plus
  continuity of second moments) makes
  \(I_{\lambda\lambda}^{q_K}\) eventually nonsingular, where
  \(B\mapsto I_{\psi\lambda}I_{\lambda\lambda}^{-1}\) is continuous. The
  hypothesis \(I^{\rm full}_{\lambda\lambda}\succ0\) is now explicit.
- *(b.)* The split identity is the exact between-group decomposition
  \(W_xe_x^2+W_ye_y^2-W_Me_M^2=\frac{W_xW_y}{W_M}(e_x-e_y)^2\) (with
  \(e_M=(W_xe_x+W_ye_y)/W_M\) by linearity of \(e\) in \(\mu\)). The "iff":
  (⇐) evaluate at the common minimizer; (⇒) the split's minimum is attained at
  some \(B_1\) (PSD quadratic; attainment by the normal-equation argument),
  and \(V(B_1;\text{merged})+\mathrm{gap}(B_1)=\min V(\cdot;\text{merged})
  \le V(B_1;\text{merged})\) forces \(\mathrm{gap}(B_1)=0\) and \(B_1\) to
  minimize the merged problem. **The same argument works for every
  \(d_\psi\ge1\)** (the gap is a PSD rank-one matrix; Loewner sandwich plus
  \(X\preceq Y\preceq X\Rightarrow X=Y\)); the general case is what DS14's
  merged variant actually consumes, so it is now on record.
- *(c.)* Scope precision: "a merged group is nuisance-degenerate" must be read
  as *the merged configuration is entirely nuisance-degenerate* (all cells
  have \(\mu_{b\lambda}=0\)), so that \(V(\cdot;\text{merged})\) is constant
  and every slope is a minimizer; then a split with distinct nuisance means
  admits an equalizing slope and is exactly neutral, and "strictly increases"
  in the equal-nuisance-mean case additionally needs
  \(\mu_{x\psi}\ne\mu_{y\psi}\). The fixture satisfies all of this.

**DS12 — verified with hardened statement.** Independently re-proved:

- *(Uniform remainder, supplied.)* \(F=\log\det S_\psi\) is \(C^\infty\) on
  \(\{I\succ0\}\). For \(\bar s\in B(0,R)\) and \(\varepsilon\le\varepsilon_0
  <\min(W_a/2,\lambda_{\min}(I_q)/(2C_R))\): \(\alpha=\varepsilon
  +O(\varepsilon^2)\), \(\beta=\varepsilon-O(\varepsilon^2)\) with constants
  depending only on \((W_a,W_b,\varepsilon_0)\), \(\|\Delta I\|\le C_R
  \varepsilon\), the segment \([I,I+\Delta I]\) stays in a compact subset of
  \(\{I\succ0\}\), and second-order Taylor gives
  \(\Phi(q_{E\to b})-\Phi(q)=\varepsilon\,\delta_{ab}(\bar s)
  +O(\varepsilon^2)\) uniformly over \(\bar s\in B(0,R)\).
- *(Necessity.)* Atomlessness supplies subsets of arbitrary intermediate
  measure (Sierpiński's theorem); the barycenter of \(E\subseteq V\cap B(0,R)\)
  stays in the convex \(B(0,R)\), and affinity turns the pointwise bound
  \(\delta_{ab}\ge c\) on \(V\) into \(\delta_{ab}(\bar s_n)\ge c\).
  **Atomlessness is load-bearing here and only here:** for a finitely atomic
  law no packets of arbitrarily small positive mass exist, bounded-packet
  stationarity holds vacuously, and the existing fixture
  `CE-DS-GLOBAL-GEOMETRY-001` (an exact global optimum violating its own
  rule) witnesses the failure of (⟹) for atomic \(P\). The sufficiency
  direction (⟸) uses no atomlessness and holds for every \(P\).
- *(Deployability, restated selection-independently.)* The precise
  characterization proved: *the nearest-projected-centroid correspondence is
  \(P\)-a.e. single-valued and reproduces \(q\) up to null sets* **iff** (i)
  the \(e_b\) are pairwise distinct and (ii) \(P\) charges no pairwise tie
  hyperplane. If (i) fails, both coincident cells are minimizers on a set of
  mass \(\ge W_b+W_{b'}\); if (i) holds, ties between distinct centroids are
  genuine affine hyperplanes and (ii) makes the argmin a.e. unique, and
  stationarity then forces the argmin to equal the label a.e. As literally
  worded ("defines a deployable rule reproducing \(q\)") the necessity of (ii)
  could be dodged by a tie-breaking selection that copies \(q\); the hardened
  wording eliminates that reading. The fixture shows stationarity does not
  force (i).

**DS13 — verified; assumptions corrected in both directions.** The four-line
algebra is exact (§7, re-verified exhaustively in §6). Two hardenings:

- *(Degenerate destinations, closed.)* If the post-move nuisance block is
  singular, then the post-move \(I'\) is singular too (Fischer:
  \(\det I'\le\det I'_{\psi\psi}\det I'_{\lambda\lambda}\)), so **both**
  determinant-ratio formulas evaluate to their true (zero) values,
  \(0\le\text{RHS}\) holds **without any stability input**, and the expansion
  argument proceeds unchanged. The one-sentence remark in the proof is
  correct once this case split is made explicit; no convention about
  \(\Delta F_s=\log0-\log0\) is needed, and the bound covers such moves.
- *(Merged atoms, dropped.)* The proof never uses distinctness of score rows;
  the bound holds verbatim at stable states of unmerged-duplicate configs
  (confirmed exhaustively, dataset 1 of §6). The operative assumptions are:
  positive weights, current \(I\succ0\) and \(I_{\lambda\lambda}\succ0\), and
  non-singleton source with positive co-weight (\(W_a>w_i\)).

**DS14 — verified as a conditional theorem with hardened assumptions.** The
five steps were re-derived; the following were supplied or made explicit:

- *(Step 1.)* DS13 applies because (A2) with equal weights gives every cell
  \(\ge c_0N\ge2\) points for \(N\ge2/c_0\) and (A3) gives both nonsingular
  blocks; \(\|\hat\mu_b\|^2\le M_N/c_0\) (Jensen), \(q_{xx}\le
  \frac2\kappa(\|s_i\|^2+M_N/c_0)\) (parallelogram), and the Markov bound is
  valid once \(\sqrt{tN}\kappa/2>M_N/c_0\). Disagreement convention:
  \(\rho_N\) breaks exact ties in favor of the current label, so misassignment
  implies a strictly positive gap.
- *(Step 2, the load-bearing repair.)* \(\Lambda\) is not an extra assumption:
  \(\lambda_{\max}(S_\psi(\hat I_N))\le\operatorname{tr}\hat I_N=\sum_b\hat
  W_b\|\hat\mu_b\|^2\le M_N\to M\) a.s., so \(\Lambda:=2M\) works eventually
  a.s.; the sandwich \(\kappa\preceq S_\psi(\hat I_N)\preceq\Lambda\) follows
  with the lower bound from \(S_\psi=((\hat I_N^{-1})_{\psi\psi})^{-1}\succeq
  \lambda_{\min}(\hat I_N)\). The Glivenko–Cantelli step must not be run over
  the data-dependent slabs; instead: the **fixed** class
  \(\mathcal S=\{\,\{s:|v^\top s-c|\le r\}:\|v\|=1,c\in\mathbb R\,\}\) of all
  slabs of half-width \(r\) is a VC class (each slab is an intersection of two
  half-spaces; VC dimension \(\le\) a constant depending only on \(d\)), so
  \(\sup_{\mathcal S}|P_N-P|\to0\) a.s. (Vapnik–Chervonenkis / van der
  Vaart–Wellner Thm 2.4.3, Pollard 1984 II.14), and (A4) — which is already
  uniform over all \((v,c)\) — bounds every population slab mass by
  \(\varphi(r)\). The empirical gap-\(t\) band, whatever its data-dependent
  normals, lies in \(\binom K2\) members of \(\mathcal S\) with
  \(r=t\Lambda/(2\gamma)\); hence \(\limsup_NP_N(0<\text{gap}\le t)\le\binom
  K2\varphi(t\Lambda/(2\gamma))\), and \(N\to\infty\), \(t\downarrow0\) give
  conclusion 1.
- *(Step 3.)* The needed uniform law is re-proved directly (removing the load
  from C1's terse statement): cells of rules in the class are intersections of
  \(\le K-1\) half-spaces (VC-subgraph class); the functions
  \(s\mapsto s\,\mathbf1_{\rm cell}(s)\) have integrable envelope \(\|s\|\)
  (finite second moment suffices amply), so masses and first moments converge
  uniformly over the class a.s. (Pollard 1984, II.24 / Graf–Luschgy-type
  ULLN). **Compactness is explicit:** parameters live in \(\{\hat W\in
  \Delta_{K}:\hat W_b\ge c_0\}\times\{\|\hat e_b\|\le(1+2M/\kappa)
  \sqrt{2M/c_0}\}\times\{\kappa\le S_\psi\le2M\}\times\{\|B^*\|\le2M/\kappa\}\)
  — a compact set, so every subsequence has a parameter-convergent
  sub-subsequence. Along one, dominated convergence (tie sets are \(P\)-null:
  (A4) kills every hyperplane, and limit normals are nonzero by (A5) passing
  to the limit) identifies empirical with population moments of the limit.
- *(Step 4.)* Written as the two-sided argument: the limit rule's parameters
  are continuous images (at \(I\succeq\kappa\)) of the limit moments, which
  Step 3 identifies as the population moments *of the limit rule itself*;
  self-consistency then hands exactly DS12's a.e.-nearest condition, whose
  hypotheses (atomless, masses \(\ge c_0\), \(I_{q^*}\succeq\kappa\)) are
  inherited, so \(q^*\) is bounded-packet stationary.
- *(Step 5.)* The lower bound holds for each fixed margin-compatible \(\rho\)
  by global optimality plus the fixed-rule SLLN (boundaries null); the
  uncountable supremum is handled by a countable value-exhausting sequence.
  The upper bound plus parameter compactness force
  \(\lim\hat\Phi_s=v^*=\Phi_s^{\rm pop}(q^*)\); margins are closed under the
  limits taken, so \(q^*\) is in the class and attains \(v^*\). *Remark
  (strengthening, not needed for the claim):* the same sandwich proves
  convergence to the supremum over the **broader** class of all geometric
  rules with positive masses, distinct centroids, and nonsingular information
  — the margin restriction binds only through the hypotheses on
  \(z^{(N)}\), not on the comparison class. Whether that equals the
  unrestricted supremum over measurable quantizers stays open (C2).
- *(Merged variant.)* Vanishing pairwise separation along the subsequence is
  transitive (triangle inequality), so the merge is by genuine equivalence
  classes; inter-group separations have positive limits, giving a group-level
  (A5) with some \(\gamma'>0\) along the subsequence; Steps 1–2 then run for
  the group rule verbatim (a group-level misassignment is in particular a
  cell-level one across groups, so DS13 supplies the same gap bound, and only
  inter-group slabs are needed). The **value identification** for conclusion
  2–3 needs refinement neutrality beyond the recorded \(d_\psi=1\): within a
  group, the fine rule's own \(B_1=B^*(\hat I)\) equalizes projected
  centroids in the limit, and by the general-\(d_\psi\) DS11(b) above the
  limit fine and merged configurations have equal profiled information; so
  \(\hat\Phi_s(z^{(N)})\) converges to the reduced rule's population value.
  This gap in the written proof ("Steps 3–5 deliver", citing only
  \(d_\psi=1\) machinery) is now closed.

No counterexample to any of the four claims was found; the boundary failures
that exist (`CE-DS-DEGENERATE-GLOBAL-TIE-001`, `CE-DS-POP-WASTED-CELLS-001`,
atomic-law vacuity via `CE-DS-GLOBAL-GEOMETRY-001`) delimit hypotheses the
claims already carry after hardening.

## 9. Adversarial audit and boundary conditions

- **Ties:** DS12/DS14 tolerate exact ties (the rule condition is \(\le\); the
  companion rule breaks ties toward the current label); (A4) makes tie sets
  null in the limit. The 31-fold exact tie fixture shows finite optima can be
  entire tie classes — handled by the merged variant, not excluded.
- **Singletons:** DS13 excludes singleton *sources* only; the audit's margin
  scan reconfirms singleton cells occur at exact global optima, which is
  precisely why (A2) is an assumption, not a fact (OP28).
- **Duplicates:** irrelevant to DS13 (assumption dropped, verified
  exhaustively); population claims are unaffected (atomless).
- **Singular information:** DS12/DS13 require \(I\succ0\),
  \(I_{\lambda\lambda}\succ0\) at the *current* state; post-move singularity
  is fully covered (Fischer case split). DS11 is the one claim that lives on
  singular blocks, and its pseudo-inverse value can strictly exceed the
  feasible in-bin optimum (fixture; warning retained).
- **Nuisance singularity:** the wasted-cell fixture keeps
  \(I_{\lambda\lambda}\) singular under the coarsening; DS9's feasibility
  split is respected everywhere; the centered \(K\le d\) probe is structurally
  infeasible (U4).
- **Atomic laws:** DS12's necessity direction fails for atomic laws
  (vacuous stationarity; existing fixture as witness); sufficiency survives.
  DS14 assumes atomless (A1) and never applies DS12 to an atomic law.
- **Hidden compactness:** was the sharpest risk in DS14 Steps 3/5; now an
  explicit compact parameter set (§8), so the subsequence extractions are
  legitimate.
- **First-order-to-finite:** DS13 is exact-finite (no first-order leap); DS12
  is genuinely first-order and says so; DS4 already blocks the naive
  finite-geometry claim, which is why the bridge runs through the leverage
  bound rather than exact Voronoi geometry.
- **Empirical-to-population:** the ULLN runs over fixed VC classes, never over
  data-dependent families; moments and values transfer along
  parameter-convergent subsequences only — exactly what the theorem claims,
  no more.
- **Score-estimation error:** out of scope by declaration (P2); nothing here
  covers estimated scores.
- **New events:** all statements are score-space statements; the companion
  rule extends to unseen scores only under the deployability conditions of
  DS12 (distinct projected centroids, null ties).

## 10. Algorithmic consequence

Exact one-point Ds exchange terminates (DS3) at states whose geometric defect
is quantitatively controlled: every admissible move's efficient-semimetric
violation is bounded by \(w_i\,q_{aa}q_{bb}\) (DS13) with no balance or mass
margin, complementing DS6. Under the DS14 margins, exchange-stable labelings
are asymptotically indistinguishable from their own companion rules, so the
finite solver output converges (in the stated subsequential sense) to
population-stationary efficient-Voronoi quantizers. This does not make any
Lloyd-type iteration monotone, does not identify label-level optima (tie
classes), and says nothing about optimization quality beyond stability.

## 11. Deployability consequence

The deployable object for profiled criteria is the **reduced** configuration
\(\{(W_b,e_b)\}\): DS12's characterization tells exactly when a stationary
partition is reproducible by its own rule, and DS14 (merged variant) shows the
reduced rule is what finite optima determine. A future
`compile_quantizer`-for-Ds must (i) merge coincident projected centroids
before compiling, (ii) certify the margins (A2)/(A3)/(A5) on the training
labeling rather than assume them, and (iii) refuse compilation when the
nuisance block is singular (DS9). The bridge is conditional: margins are
certified inputs, not consequences.

## 12. Information-loss consequence

Nothing here bounds D- or Ds-efficiency against full-data information: the
bridge transports stationarity and values, not retention guarantees. The
efficient-score domination gap (DS11(a)) is the exact price of binned nuisance
projection for a fixed partition, vanishing along refining sequences under
\(I^{\rm full}_{\lambda\lambda}\succ0\); behavior at optima stays open
(OP28), and \(v^*\) is the optimum over the margin-compatible geometric class
only — its relation to the unrestricted supremum is C2.

## 13. Updated status

- `DS-PROFILED-VARIATIONAL`: remains `project_proved` with the core identity
  reclassified as classical prior art (`literature_search_status:
  "prior_art_found"`), assumptions hardened (centering; nonsingular full
  nuisance block for the \(K\to\infty\) part; scope of (c)); the \(d_\psi\ge1\)
  neutrality extension recorded.
- `OPEN-DS-POP-COMMON-METRIC`: remains `project_proved`, deployability
  characterization hardened to the selection-independent reading; atomic-law
  boundary recorded with the existing fixture; `literature_search_status:
  "search_gap"`.
- `DS-EXCHANGE-LEVERAGE-BOUND`: remains `project_proved`; merged-atoms
  assumption dropped, degenerate-destination case closed, positive-co-weight
  made explicit; `literature_search_status: "search_gap"`.
- `OPEN-DS-FINITE-POP-BRIDGE`: remains `project_proved` (conditional); the
  "audit pending" warning is lifted; the conditional-margins warning stays;
  \(\Lambda\) recorded as derived (\(2E\|S\|^2\)), the slab-GC and
  merged-value arguments recorded; `literature_search_status: "search_gap"`.
- `AUDIT-DS-POPULATION-BRIDGE`: added as `project_proved`.

## 14. Registry patch

`CLAIMS.json` gains the audit node pointing at this report; the four audited
nodes gain `audit:` pointers, hardened `assumptions`, and
`literature_search_status`; DS14's warning drops the pending clause; the
DS11 bibliography records Li–Mathias (with the Krein/Anderson attribution);
indexes are regenerated by hand and validated by the registry tests.

## 15. Regression artifacts

- `py/audit_ds_population_bridge.py`: the independent exact-rational suite
  (modes `ds11`, `ds13`, `fixtures`, `margins`, `all`).
- `tests/test_research_claims.py::test_ds13_leverage_bound_at_every_stable_state_with_vector_nuisance`:
  pinned exhaustive regression in a configuration class the original evidence
  never touched (\(d=3\), \(d_\lambda=2\)).
- Reused fixtures: `CE-DS-DEGENERATE-GLOBAL-TIE-001`,
  `CE-DS-POP-WASTED-CELLS-001` (independently re-verified),
  `CE-DS-GLOBAL-GEOMETRY-001` (reinterpreted as the atomic-law boundary
  witness for DS12 necessity).

## 16. Next dependency-blocking question

`OPEN-DS-MARGINS-AT-OPTIMA` (OP28): do exact finite Ds optima under
light-tailed atomless laws satisfy the mass, conditioning, and separation
margins asymptotically — or at least after merging \(\Phi\)-neutral splits?
The audit's own exact scan shows singleton cells at an \(N=10\) global
optimum, so the question is genuinely open and now the sole obstacle between
the conditional bridge and an unconditional compile guarantee for profiled
criteria.
