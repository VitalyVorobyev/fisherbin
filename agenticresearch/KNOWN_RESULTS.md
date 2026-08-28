# Known results and current project theory

**Version:** 2.0 · 26 August 2026  
**Purpose:** canonical theorem/result ledger. Read `PROBLEM.md` first.

Status vocabulary (mirrors `CLAIMS.json` `status_definitions`):

- **[LIT]** established literature.
- **[BRIDGE]** direct synthesis/translation of known results into ScoreQuant notation.
- **[PROJECT-PROVED]** derived in this project and currently treated as proved internally; still subject to publication-grade audit.
- **[COUNTEREXAMPLE]** explicit falsification in the project setting.
- **[MEASURED]** numerical evidence/regression test, not a theorem.
- **[CONJECTURE]** precise unproved conjecture.
- **[SEARCH-GAP]** no direct precedent located in targeted search; not a novelty proof.
- **[OPEN]** unresolved.

---

# 1. Universal information structure

## U1. Quantized Fisher-information identity — [LIT]

**Claims:** FI-QUANT-IDENTITY

For \(Z=q(S)\),

\[
\nabla_\theta\log P_\theta(Z=b)|_{\theta_0}
=E[S\mid Z=b]=\mu_b,
\]

hence

\[
\boxed{
I_q
=\operatorname{Var}(E[S\mid Z])
=\sum_bW_b\mu_b\mu_b^\top
=\sum_b\frac{m_bm_b^\top}{W_b}.
}
\]

Closest direct literature: score-function quantization; Barnes–Han–Özgür.

## U2. Exact information-loss decomposition — [LIT/BRIDGE]

**Claims:** FI-LOSS-DECOMPOSITION

\[
\boxed{
I_{\rm full}-I_q=E[\operatorname{Cov}(S\mid Z)]\succeq0.
}
\]

Consequences:

- hard quantization cannot increase Fisher information;
- all retained-information criteria here depend on a quantizer only through \((W_b,m_b)\).

## U3. Local Fisher-losslessness criterion — [BRIDGE]

**Claims:** FI-LOSSLESS-IFF-SCORE-MEASURABLE

\[
\boxed{
I_q=I_{\rm full}
\iff
S=h(Z)\quad\text{a.s.}
}
\]

Equivalently \(\operatorname{Cov}(S\mid Z)=0\) a.s. Generic smooth score laws cannot be exactly lossless for finite \(K\).

## U4. Rank ceiling — [BRIDGE]

**Claims:** FI-RANK-CEILING

Since \(\sum_bm_b=0\),

\[
\operatorname{rank}(I_q)\le\min(d,K-1).
\]

Therefore \(K\ge d+1\) is necessary for nonsingular full-D information.

## U5. Refinement monotonicity — [BRIDGE]

**Claims:** FI-REFINEMENT-MONOTONICITY, GENERAL-REFINEMENT-BB

If \(\mathcal P'\) refines \(\mathcal P\), then

\[
I_{\mathcal P'}\succeq I_{\mathcal P}.
\]

This powers branch-and-bound upper bounds for every Loewner-monotone criterion.

## U6. Reparameterization invariance of D — [BRIDGE]

**Claims:** D-REPARAM-INVARIANCE

Under an invertible local parameter transformation, \(I_q\) transforms by congruence and \(\log\det I_q\) changes only by a quantizer-independent constant. D-optimal partitions are therefore invariant under invertible reparameterization.

## U7. Normalized retained-information spectrum — [BRIDGE]

**Claims:** INFO-RETENTION-SPECTRUM

\[
R=I_{\rm full}^{-1/2}I_qI_{\rm full}^{-1/2},
\qquad 0\preceq R\preceq I.
\]

Thus every retention eigenvalue lies in \([0,1]\). Natural summaries are

\[
\frac1d\operatorname{tr}R,
\qquad
(\det R)^{1/d},
\qquad
\lambda_{\min}(R).
\]

The middle quantity is D-efficiency.

---

# 2. Trace control case

## T1. Fisher-whitened normalized trace equals weighted k-means — [BRIDGE; essentially known]

**Claims:** TRACE-WHITENED-KMEANS

With

\[
z=I_{\rm full}^{-1/2}s,
\]

\[
\boxed{
d-\operatorname{tr}(I_{\rm full}^{-1}I_q)
=E\|z-E[z\mid Z]\|^2.
}
\]

Therefore maximizing normalized retained trace is exactly squared-error vector quantization / weighted k-means in whitened score space.

This is useful as a baseline, not a headline novelty claim.

---

# 3. Generic first-order and finite screening results

## G1. Infinitesimal cell-transfer identity — [PROJECT-PROVED/BRIDGE]

**Claims:** GENERAL-FIRST-VARIATION

Move infinitesimal probability mass \(d\varepsilon\) at score \(s\) from cell \(a\) to \(b\). Then

\[
\boxed{
dI_q=
[(s-\mu_a)(s-\mu_a)^\top-(s-\mu_b)(s-\mu_b)^\top]d\varepsilon.
}
\]

For differentiable \(F(I)\) with symmetric \(G=\nabla F(I)\),

\[
\boxed{
\frac{dF}{d\varepsilon}
=(s-\mu_a)^\top G(s-\mu_a)
-(s-\mu_b)^\top G(s-\mu_b).
}
\]

A shared \(G\) makes pairwise boundaries affine because the common \(s^\top Gs\) term cancels.

## G2. General concavity/supergradient screening — [PROJECT-PROVED]

**Claims:** D-TANGENT-SCREENING, DS-TANGENT-SCREENING, GENERAL-SUPERGRADIENT-SCREENING, GENERAL-WEIGHTED-TANGENT-STABILITY

For a concave criterion \(F\), let \(G\) be any supergradient at the current information matrix. For an exact finite relocation

\[
\Delta I=\alpha u_au_a^\top-\beta u_bu_b^\top,
\]

concavity gives

\[
\boxed{
\Delta F
\le
\operatorname{tr}(G\Delta I)
=
\alpha u_a^\top Gu_a-
\beta u_b^\top Gu_b.
}
\]

Therefore:

- if the weighted tangent gain is \(\le0\), the exact move cannot improve;
- weighted-tangent stability is a sufficient certificate of one-point exchange stability;
- expensive exact move evaluation can be restricted to screened-in candidates.

This applies to D, \(D_s\), A, and E (using a supergradient for E).

**Measured audit:** zero screening-direction violations in the reported randomized suites (including 4,886 D/A/\(D_s\) moves and the E suite).

---

# 4. Full D-optimality

\[
F_D(I)=\log\det I,
\qquad G_D=I^{-1}.
\]

## D1. Population stationary geometry — [PROJECT-PROVED/BRIDGE]

**Claims:** D-POP-VORONOI

A regular atomless stationary D quantizer satisfies

\[
\boxed{
q(s)\in\arg\min_b
(s-\mu_b)^\top I_q^{-1}(s-\mu_b)
\quad\text{a.e.}
}
\]

Thus cells form a self-consistent common-metric Mahalanobis Voronoi / affine-max partition.

This is a first-order stationarity result, not a global-optimality theorem.

## D2. Exact weighted rank-two relocation — [PROJECT-PROVED]

**Claims:** D-RANK2-MOVE

Move weighted point \((s,w)\) from a non-singleton source \(a\) to destination \(b\). Let

\[
u_a=s-\mu_a,\quad u_b=s-\mu_b,
\]

\[
\alpha=\frac{wW_a}{W_a-w},\qquad
\beta=\frac{wW_b}{W_b+w}.
\]

Then

\[
\boxed{
\Delta I
=\alpha u_au_a^\top-
\beta u_bu_b^\top.
}
\]

## D3. Exact log-det relocation gain — [PROJECT-PROVED]

**Claims:** D-LOGDET-GAIN

With \(H=I^{-1}\) and

\[
q_{aa}=u_a^\top Hu_a,\quad
q_{bb}=u_b^\top Hu_b,\quad
q_{ab}=u_a^\top Hu_b,
\]

\[
\boxed{
\Delta F_D
=\log\!
[(1+\alpha q_{aa})(1-\beta q_{bb})+\alpha\beta q_{ab}^2].
}
\]

This supports exact \(O(d^2)\)-type candidate evaluation with cached factorizations.

## D4. Leverage inequality — [STANDARD/BRIDGE]

**Claims:** D-LEVERAGE

For every cell centroid,

\[
\mu_c^\top I^{-1}\mu_c\le 1/W_c,
\]

and for centroid difference \(\delta=\mu_a-\mu_b\),

\[
\boxed{
\delta^\top I^{-1}\delta
\le
1/W_a+1/W_b.
}
\]

This is a standard projection/leverage inequality; its role here is to bridge infinitesimal D geometry to exact finite gains.

Explicitly, with

\[
A=[\sqrt{W_1}\mu_1,\ldots,\sqrt{W_K}\mu_K],
\qquad I=AA^\top,
\]

the matrix \(P=A^\top(AA^\top)^{-1}A\) is an orthogonal projector. Taking
\(v_a=1/\sqrt{W_a}\), \(v_b=-1/\sqrt{W_b}\), and all other coordinates zero
gives \(Av=\mu_a-\mu_b\), hence

\[
(\mu_a-\mu_b)^\top I^{-1}(\mu_a-\mu_b)
=v^\top Pv\le v^\top v=1/W_a+1/W_b.
\]

## D5. Exchange stability implies strict D-Voronoi geometry — [PROJECT-PROVED; audited]

**Claims:** D-EXCHANGE-IMPLIES-VORONOI, D-EXCHANGE-VIOLATION-LOWER-BOUND

Let coincident score rows be merged into distinct atoms with positive weights,
and partition those atoms into exactly \(K\) nonempty cells. Assume \(I\succ0\),
that the only relocation constraint is preservation of nonempty cells, and that
exchange stability means no **exact positive-gain** relocation (zero gain
tolerance). Then a point in a non-singleton source that is tied with or farther
from its own centroid than a competing centroid under \(I^{-1}\) has

\[
\boxed{
\Delta F_D
\ge
\log\left(1+\frac{\alpha\beta}{4}q_\delta^2\right)>0
}
\]

when the two centroids are distinct. Here
\(q_\delta=(\mu_a-\mu_b)^\top I^{-1}(\mu_a-\mu_b)\).

The exact algebra is

\[
\frac{\det(I+\Delta I)}{\det I}=1+E,
\qquad
E\ge\frac{\alpha\beta}{4}
\left[q_\delta^2+(q_{aa}-q_{bb})^2\right].
\]

Distinct centroids follow from stability rather than needing a separate
assumption. If \(\mu_a=\mu_b\) and either cell is non-singleton, moving a
non-centroid atom between them gives determinant ratio
\(1+(\alpha-\beta)q_{aa}>1\). If both are singletons, equality would mean the
two score atoms are duplicates, excluded by merging. A singleton atom is then
strictly nearest to its own centroid because its own distance is zero and every
other centroid is distinct.

Hence

\[
\boxed{
\text{one-point exchange stable}
\Rightarrow
\text{strict self-consistent D-Voronoi}.
}
\]

The converse fails.

Exact ties between distinct centroids are therefore ruled out, not left as an
unresolved degeneracy. Split duplicate atoms are a genuine boundary failure:
see `COUNTEREXAMPLES/CE-D-UNMERGED-DUPLICATES-001.json`. Zero-weight rows,
singular/pseudodeterminant objectives, extra capacity or mass constraints, and
nonzero solver gain tolerances are outside the theorem. At tolerance
\(\varepsilon>0\), the implementation certifies only that no geometric
disagreement has exact gain exceeding \(\varepsilon\); strict training-label
reproduction need not hold.

Publication-grade audit and proof: `AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md`.
Exact-rational regression: `py/audit_d_exchange_voronoi.py`.

## D6. Exact finite inductive closure / compiler — [PROJECT-PROVED]

**Claims:** D-FINITE-INDUCTIVE-CLOSURE

Every one-point-exchange-stable positive-definite finite D solution can be compiled to

\[
\boxed{
\hat q_D(s)=
\arg\min_b(s-\mu_b)^\top\widehat I^{-1}(s-\mu_b).
}
\]

For merged distinct positive-weight score atoms at exact zero-tolerance
stability, this predictor reproduces **all training labels exactly**, without a
tie breaker. Original duplicate rows inherit the merged atom's label. Therefore
an exact terminal D exchange solution is not merely transductive: it has a
canonical deployable extension. A finite numerical solver using a positive gain
tolerance has the weaker, explicitly tolerance-stamped compiler guarantee
documented by `GeometryReport`.

## D7. Every finite global D optimum is geometrically realizable — [PROJECT-PROVED COROLLARY]

**Claims:** D-GLOBAL-GEOMETRIC-REALIZABILITY

A finite global optimum is exchange stable, hence strict D-Voronoi. Therefore unrestricted finite D assignment optimization and global optimization over the corresponding realizable D-Voronoi/affine-max labelings have the same optimum value.

This does **not** say every D-Voronoi fixed point is globally optimal.

## D8. Monotone exact one-point exchange — [PROJECT-PROVED]

**Claims:** D-EXCHANGE-TERMINATES

Accepting only exact positive D gains gives:

- strict objective ascent;
- no cycles;
- finite termination because the labeling set is finite;
- a terminal one-point exchange-stable solution;
- by D5/D6, a canonical deployable D quantizer.

## D9. Adaptive Mahalanobis Lloyd is not monotone — [COUNTEREXAMPLE]

**Claims:** D-GUARDED-LLOYD, D-LLOYD-NONMONOTONE

The batch iteration “compute \(I^{-1}\) → nearest-centroid reassignment → recompute \(I\)” can decrease \(\log\det I\).

Reason:

\[
\log\det J
\le
\log\det I+\operatorname{tr}(I^{-1}(J-I)),
\]

so the fixed-metric tangent is an **upper** bound, not a minorizer.

Measured suite: decreasing steps occurred in 57/300 instances; one explicit example loses about 0.137 nat.

## D10. Voronoi fixed point does not imply exchange stability — [COUNTEREXAMPLE]

**Claims:** D-VORONOI-NOT-EXCHANGE

Measured suite: 35/100 Lloyd/Voronoi fixed points still admitted an exact improving one-point move, with improvements up to about 1.033 nat.

## D11. Exact global enumeration for fixed \((d,K)\) — [PROJECT-PROVED]

**Claims:** D-GLOBAL-XP

D7 restricts candidate global labelings to affine-max-realizable partitions. Arrangement enumeration gives an exact XP algorithm of form

\[
\boxed{N^{O(Kd)}}
\]

for fixed \((d,K)\), with an effective affine parameter count of order \((K-1)(d+1)\).

This is an application of a known computational-geometry template; hardness/FPT status remains open.

## D12. Singleton-refinement branch-and-bound bound — [PROJECT-PROVED]

**Claims:** D-BB-SINGLETON-BOUND

For a partial assignment and unassigned point set \(U\), singleton refinement yields

\[
\boxed{
I_{\rm completion}
\preceq
I_{\rm partial}+
\sum_{i\in U}w_is_is_i^\top.
}
\]

Thus

\[
\log\det\left(
I_{\rm partial}+\sum_{i\in U}w_is_is_i^\top
\right)
\]

is a valid D upper bound for every completion.

Measured implementation: exact agreement with exhaustive search on small instances and certificates through \(N=40\) for reported \(d=2,K=3\) tests. The hardest reported \(N=40\) instance visited 131,799 nodes in 8.3 s; this is instance-dependent evidence, not a worst-case claim.

---

# 5. \(D_s\)-optimality

## DS0. Profiled objective and Schur notation — [LIT]

**Claims:** DS-SCHUR

Let \(\theta=(\psi,\lambda)\) and

\[
F_s(I)
=\log\det S_\psi(I)
=\log\det I-\log\det I_{\lambda\lambda}
\]

in the nonsingular block regime.

## DS1. Classical \(D_s\) design theory — [LIT]

**Claims:** DS-CLASSICAL-DESIGN-THEORY

Wynn, Whittle, Näther–Reinsch, Kiefer/general equivalence theory provide classical subset/nuisance-parameter optimal design, sensitivity, and singular-case tools. They do not directly solve the quantizer feasible set.

## DS2. Gradient / efficient semimetric — [PROJECT-PROVED/BRIDGE]

**Claims:** DS-GRADIENT-EFFICIENT-SEMIMETRIC

For regular nonsingular blocks,

\[
\boxed{
G_s
=
I^{-1}
-E_\lambda I_{\lambda\lambda}^{-1}E_\lambda^\top
\succeq0,
}
\]

of rank \(d_\psi\). Population first-order stationarity therefore induces an efficient-score semi-metric / affine-max geometry.

## DS3. Exact finite one-point objective oracle — [PROJECT-PROVED]

**Claims:** DS-EXACT-MOVE-ORACLE, DS-EXCHANGE-TERMINATES

The same rank-two full-information update applies. The exact profiled gain is

\[
\boxed{
\Delta F_s
=
\Delta\log\det I
-
\Delta\log\det I_{\lambda\lambda},
}
\]

with each term evaluable by low-rank determinant algebra when blocks remain nonsingular. Exact positive-gain \(D_s\) exchange is therefore monotone and finitely terminating on a finite sample.

## DS4. D-style finite geometry theorem fails — [COUNTEREXAMPLE]

**Claims:** DS-FINITE-GEOMETRY-FAILS

A positive first-order efficient-Voronoi margin need not imply positive exact finite \(D_s\) gain. Therefore

\[
\text{exchange stable}\not\Rightarrow\text{exact }G_s\text{-Voronoi}
\]

in general.

## DS5. A global finite \(D_s\) optimum can be non-geometric — [EXACT COUNTEREXAMPLE]

**Claims:** DS-GLOBAL-NONGEOMETRIC

There is a centered equal-weight \(N=8,d=2,d_\psi=1,K=3\) example for which exhaustive enumeration of all 966 unlabeled nonempty partitions gives a unique global \(D_s\) optimum that violates its own efficient-semi-metric nearest-cell rule.

Canonical fixture is stored in `COUNTEREXAMPLES/CE-DS-GLOBAL-GEOMETRY-001.json`.

This proves that unrestricted finite \(D_s\) assignment and deployable self-consistent geometric \(D_s\) fitting are genuinely different finite problems.

## DS6. Approximate finite efficient-Voronoi bound — [PROJECT-PROVED]

**Claims:** DS-OKN-BOUND

At a \(D_s\) one-point exchange-stable state, the relative first-order violation obeys a bound of the form

\[
\boxed{
\frac{s_{aa}-s_{bb}}{q_{aa}}
\le
w_i\left(\frac1{W_a}+\frac1{W_b}\right).
}
\]

For equal weights and balanced cells this is \(O(K/N)\).

Measured suite: the observed maximum violation shrank from roughly 0.18 to 0.029 as \(N\) increased from 8 to 64 in the reported experiment.

## DS7. Full-data efficient-score domination — [PROJECT-PROVED; see also DS11(a)]

**Claims:** DS-EFFICIENT-SCORE-DOMINATION, DS-EFFICIENT-SCORE-GLOBAL-UPPER

Let

\[
\widehat S=S_\psi-B^*S_\lambda,
\qquad
B^*=I^{\rm full}_{\psi\lambda}(I^{\rm full}_{\lambda\lambda})^{-1}.
\]

For **every** quantizer \(q\),

\[
\boxed{
S_\psi(I_q)
\preceq
\operatorname{Var}(E[\widehat S\mid q(S)]).
}
\]

Interpretation: profiling nuisance information from the bins cannot beat first projecting to the full-data efficient score and then measuring the retained between-cell information of that projection.

Taking log-determinants and suprema gives

\[
\boxed{
\sup_q F_s(q)
\le
\text{best D-optimal K-bin value for the }d_\psi\text{-dimensional efficient score}.
}
\]

For the last equality to deterministic quantization of \(\widehat S\), atomlessness is required for the **efficient-score law itself**.

## DS8. Scalar efficient-score upper problem is exactly solvable by DP — [PROJECT-PROVED/BRIDGE]

**Claims:** DS-SCALAR-EFFICIENT-DP

For \(d_\psi=1\), deterministic D-optimal quantization of a scalar atomless efficient score has ordered interval cells. On a finite sample the optimal interval partition can be solved exactly by dynamic programming.

Consequences:

- cheap globally optimal upper bound for in-bin \(D_s\);
- strong initializer;
- explicit optimality-gap certificate for a found \(D_s\) solution.

Measured certificate gaps were 0.003–0.118 nat on reported \(d=3,d_\psi=1,K=4,N=60\) tests and 0.011–0.19 nat on reported \(d=4,d_\psi=2,K=5,N=80\) tests using the corresponding projected D upper problems.

## DS9. The \(K\le d\) feasibility split — [PROJECT-PROVED/STRUCTURAL]

**Claims:** DS-FULL-PROFILE-K-LE-D-SINGULAR, DS-PROJECTED-K-REQUIREMENT

For the **full in-bin profiled formulation**, \(I_q\) is singular when \(K\le d\), so ordinary full-block \(D_s\) profiling is not identifiable.

The projected efficient-score problem only needs enough categories to identify the \(d_\psi\)-dimensional efficient score, i.e. structurally \(K\ge d_\psi+1\), if nuisance information is supplied externally.

These are different statistical problems and must be exposed separately.

## DS10. Finite-to-population bridge: resolution map — [SUMMARY]

The bridge programme (OP4/OP5, packet `WORK/completed/DS-POPULATION-BRIDGE.md`,
28 Aug 2026) is resolved as follows:

- DS11 — variational form of the profiled objective, \(\Phi\)-neutral splits,
  and the exact equality condition for efficient-score domination (OP6, fixed
  \(q\));
- DS12 — rigorous population stationary \(D_s\) geometry and its deployability
  characterization (OP5);
- DS13 — exact finite leverage stability bound (the finite half of the bridge);
- DS14 — conditional finite\(\to\)population bridge theorem (OP4).

Residual open conditions live in `OPEN_PROBLEMS.md` OP28 (whether the margin
assumptions hold automatically at finite optima) and C2 (unrestricted
population attainment).

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

# 6. E-optimality control theory

\[
F_E(I)=\lambda_{\min}(I).
\]

## E1. Supergradient structure — [LIT]

**Claims:** E-SUPERGRADIENT

If the minimum eigenvalue is simple with unit eigenvector \(v\), one gradient is \(vv^\top\). At multiplicity \(r\) with basis \(V\),

\[
\partial^+\lambda_{\min}(I)
=\{VHV^\top:H\succeq0,\ \operatorname{tr}H=1\}.
\]

## E2. Repeated-eigenvalue one-transfer degeneracy — [PROJECT-PROVED]

**Claims:** E-REPEATED-EIGEN-DEGENERACY

For one infinitesimal transfer \(\Delta I=aa^\top-bb^\top\),

\[
d\lambda_{\min}(I;\Delta I)
=\lambda_{\min}(V^\top\Delta I V)\le0
\]

whenever the minimum eigenspace dimension is \(r\ge2\). Thus one-point first-order stability can become automatic/non-identifying exactly where E tends to equalize weak directions.

## E3. Finite global E geometry fails even with simple minimum eigenvalue — [COUNTEREXAMPLE]

**Claims:** E-GLOBAL-GEOMETRY-FAILS

Exhaustive \(N=8,d=2,K=3\) search produced a global E optimum whose own rank-one \(vv^\top\) nearest-cell rule disagrees with a training label; reported margin \(\approx0.06796\).

## E4. Positive first-order E margin need not imply exact improvement — [COUNTEREXAMPLE]

**Claims:** E-FIRSTORDER-NOT-FINITE

Reported suite: 2,167/8,965 subgradient-rule-improving moves had strictly negative exact E gain; one example had margin 2.27 and exact change \(-0.240\).

## E5. Safe E screening and B&B — [PROJECT-PROVED]

**Claims:** E-BB-APPLIES, E-TANGENT-SCREENING

G2 gives a sound rejection rule. Exact post-move \(\lambda_{\min}\) evaluation can be reserved for screened-in candidates. Refinement B&B applies because \(\lambda_{\min}\) is Loewner-monotone.

## E6. Common-supergradient population geometry — [OPEN]

**Claims:** OPEN-E-COMMON-SUPERGRADIENT

It remains open whether every suitable population E optimum admits one common supergradient that supports all cell-assignment inequalities almost everywhere.

---

# 7. A-optimality control theory

\[
F_A(I)=-\operatorname{tr}(I^{-1}),
\qquad
G_A=I^{-2}.
\]

## A1. Exact finite move oracle — [PROJECT-PROVED]

**Claims:** A-EXACT-MOVE-ORACLE, A-EXCHANGE-TERMINATES

The universal rank-two \(\Delta I\) plus Woodbury gives an exact \(O(d^2)\)-type A move oracle; exact positive-gain exchange is monotone and finitely terminating.

## A2. D-style finite geometry theorem fails — [COUNTEREXAMPLE]

**Claims:** A-FINITE-GEOMETRY-FAILS

The reported search found 443 A moves violating the would-be D-style implication. Therefore finite exchange stability does not generally collapse to the first-order \(I^{-2}\) Voronoi rule.

## A3. Concavity screening remains valid — [PROJECT-PROVED]

**Claims:** A-TANGENT-SCREENING

G2 supplies a sound tangent rejection rule for A.

## A4. Quantitative A necessity bound — [OPEN]

No analogue of the \(D_s\) Prop.-17-style \(O(w)\) violation bound has yet been derived.

---

# 8. Randomized/soft quantizers and empirical geometric optimization

## S1. Soft assignments are an actual randomized quantizer — [PROJECT-PROVED/BRIDGE]

**Claims:** SOFT-RANDOMIZED-FIM

For \(r_{ib}\ge0\), \(\sum_br_{ib}=1\),

\[
W_b=\sum_iw_ir_{ib},\qquad
m_b=\sum_iw_ir_{ib}s_i,
\]

\[
\boxed{
I_{\rm soft}=\sum_b\frac{m_bm_b^\top}{W_b}.
}
\]

This is exactly the Fisher information of the corresponding randomized categorical observation at the reference point, provided the randomization rule is held fixed with respect to \(\theta\).

## S2. Exact soft-assignment gradient — [PROJECT-PROVED]

**Claims:** SOFT-ASSIGNMENT-GRADIENT

For differentiable \(F\), \(G=\nabla F(I_{\rm soft})\),

\[
\boxed{
\frac{\partial F}{\partial r_{ib}}
=w_i(2s_i^\top G\mu_b-\mu_b^\top G\mu_b).
}
\]

Up to a bin-independent term this is negative squared \(G\)-distance to the centroid.

## S3. Hard empirical geometric objective is piecewise constant — [PROJECT-PROVED/OBSERVATION]

**Claims:** HARD-GEOMETRIC-EMPIRICAL-PIECEWISE-CONSTANT

For a hard affine/Voronoi quantizer parameterized by continuous generators/hyperplanes, the finite empirical objective is piecewise constant in those parameters: until a training row crosses a boundary, labels and cell moments do not change.

Therefore ordinary gradient descent on the **hard finite** objective is zero almost everywhere and is not a useful generic solver.

## S4. Fixed-temperature soft optimization has ordinary stationary-point guarantees — [BRIDGE]

**Claims:** SOFT-FIXED-TEMP-STATIONARY

A positive-temperature softmax affine-max family is smooth away from empty cells/singular information. Line-search gradient ascent or quasi-Newton optimization can be made monotone in the soft objective; standard nonconvex theory gives stationary-point/gradient-norm guarantees, not hard local/global optimality.

## S5. Atomless purification — [LIT + PROJECT APPLICATION]

**Claims:** DWW-PURIFICATION-MOMENTS, SOFT-HARD-ATOMLESS-EQUIVALENCE

For an atomless score law, Dvoretzky–Wald–Wolfowitz purification preserves all \((W_b,m_b)\) of a randomized finite-action quantizer. Hence randomized and deterministic quantizers have the **same population optimum value for every criterion depending only on these moments**.

This is a classical theorem applied to the present Fisher-score moment representation.

## S6. Atomic randomization gap — [OPEN]

Finite empirical score laws are atomic. Whether splitting atoms can strictly improve D/\(D_s\)/E over every deterministic hard score quantizer remains unresolved in general.

---

# 9. Empirical-to-population theory

## C1. Restricted affine-class consistency — [PROJECT-PROVED / STANDARD EMPIRICAL-PROCESS ROUTE]

**Claims:** CONSISTENCY-RESTRICTED-AFFINE

Let \(\mathcal Q\) be a compact parameterized class of \(K\)-cell affine-max quantizers. Assume bounded scores or suitable uniform integrability, cell masses uniformly bounded below, and the required information matrices uniformly bounded away from singularity.

Then empirical \(W_b\) and \(m_b\) converge uniformly over \(\mathcal Q\). Consequently D, regular \(D_s\), and E objective values converge uniformly on that regular subset. Approximate empirical maximizers are value-consistent; with an isolated population optimum, standard argmax theory gives parameter/decision consistency up to label permutations.

The proof uses finite capacity of multiclass affine decision regions + ULLN + continuity.

## C2. Unrestricted/global consistency — [OPEN]

Still open in the desired generality:

- unrestricted empirical global D optimum \(\to\) population global optimum;
- exchange-stable D solution set \(\to\) population stationary set;
- unrestricted finite \(D_s\)/E optima \(\to\) deployable population geometric optima.

For D, finite geometric realizability makes this program unusually plausible; for \(D_s\)/E the finite non-geometric counterexamples prevent the same direct reduction.

---

# 10. Score/density-ratio/classifier access

## O1. Density ratios suffice for local scores — [BRIDGE]

**Claims:** RATIO-LOCAL-SCORE

\[
s(x)=\left.\nabla_\theta\log\frac{p(x\mid\theta)}{p(x\mid\theta_0)}\right|_{\theta_0}.
\]

Full absolute densities are not required if the relevant local density ratio is available.

## O2. Linear-mixture component ratios suffice — [BRIDGE]

**Claims:** MIXTURE-RATIO-SCORE

For

\[
p(x\mid\theta)=\sum_\alpha\theta_\alpha\phi_\alpha(x),
\]

score coordinates depend on \(\phi_\alpha(x)/\sum_\beta\theta_{0\beta}\phi_\beta(x)\). Ratios to one reference component therefore suffice exactly after algebraic reconstruction.

## O3. Calibrated classifier posteriors provide ratios — [LIT/BRIDGE]

**Claims:** CLASSIFIER-MIXTURE-SCORE-FORMULA, CLASSIFIER-RATIO-ORACLE

With class priors \(\pi_\alpha\), posterior odds recover component density ratios. In the mixture parameterization,

\[
\boxed{
s_\alpha(x)=
\frac{\eta_\alpha(x)/\pi_\alpha}
{\sum_\beta\theta_{0\beta}\eta_\beta(x)/\pi_\beta}.
}
\]

Estimated classifiers solve the exact score problem only to the extent that they recover calibrated ratios.

## O4. True retained FI under an estimated score — [BRIDGE]

**Claims:** PROXY-TRUE-RETAINED-FI

If the quantizer uses \(\hat s\), the actual retained Fisher information is

\[
\boxed{
\operatorname{Var}(E[s\mid q(\hat s)]),
}
\]

not \(\operatorname{Var}(E[\hat s\mid q(\hat s)])\) unless \(\hat s=s\) in the relevant sense.

## O5. Representation loss and quantization loss separate — [BRIDGE]

**Claims:** REPRESENTATION-QUANTIZATION-LOSS

For a representation \(R(X)\),

\[
I_R=\operatorname{Var}(E[s\mid R]),
\qquad
I_q\preceq I_R\preceq I_{\rm full}.
\]

This separates oracle/representation loss from hard-quantization loss whenever truth scores are available for validation.

---

# 11. Information-efficiency outputs

## I1. D-efficiency — [BRIDGE]

**Claims:** INFO-D-EFFICIENCY

\[
\eta_D=(\det I_q/\det I_{\rm full})^{1/d}.
\]

## I2. \(D_s\)-efficiency — [BRIDGE]

**Claims:** INFO-DS-EFFICIENCY

\[
\eta_{D_s}=
(\det S_\psi(I_q)/\det S_\psi(I_{\rm full}))^{1/s}.
\]

## I3. Directional diagnostics — [BRIDGE]

**Claims:** INFO-DIRECTIONAL-DIAGNOSTICS

Report normalized retention eigenvalues, their geometric mean, arithmetic mean, and minimum. D optimization does not guarantee every direction is equally preserved.

---

# 12. Numerical evidence as regression tests — [MEASURED]

The measured ledger lives in `NUMERICAL_EVIDENCE.md` — one row per evidence
item (`N-*` id), with the CLAIMS.json node(s) it supports and the executable
source that produces it. It is not duplicated here; nothing in it is a proof.

Keep exact seeds/scripts or minimized fixtures beside any claim used in publication.

---

# 13. Guarantee hierarchy

Use this hierarchy precisely:

\[
\text{finite global optimum}
\subseteq
\text{one-point exchange stable}
\]

for any criterion where all admissible positive one-point moves are checked.

For full D, project theory strengthens this to

\[
\boxed{
\text{finite global}
\subseteq
\text{exchange stable}
\subsetneq
\text{strict self-consistent D-Voronoi}.
}
\]

For \(D_s\), A, and E the second inclusion fails in general.

Restricted-family local optima, population stationarity, and statistical consistency are separate notions and must not be placed in this finite inclusion chain.

---

# 14. Conservative novelty boundary

### Clearly known / inherited

- Fisher-optimal finite quantization and score-function quantization;
- scalar FI-loss/score-distortion theory;
- multivariate conditional-score representation of quantized FIM;
- trace-optimal polyhedral quantizers in sufficient-statistic space;
- D/\(D_s\)/A/E optimal-design theory and equivalence/sensitivity tools;
- determinant clustering and one-point exchange;
- vector quantization/CVT/Lloyd theory;
- differentiable inference-aware categorization;
- density-ratio estimation and classifier-ratio identities;
- DWW purification itself.

### Project synthesis/results that require publication-grade prior-art audit

- exact centroid-coupled rank-two relocation and closed D gain in this retained-between-score setting;
- D exchange-stability \(\Rightarrow\) strict self-consistent \(I_q^{-1}\)-Voronoi with quantitative finite gain;
- exact finite D inductive closure and geometric realizability of global optima;
- fixed-\((d,K)\) exact enumeration application and singleton-refinement B&B;
- \(D_s\) approximate finite geometry, efficient-score domination, and resulting upper certificates;
- criterion-separation counterexamples for \(D_s\), A, and E.

These are not to be labeled “first” solely because no direct precedent has yet been found.
