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

\[
\boxed{
I_{\rm full}-I_q=E[\operatorname{Cov}(S\mid Z)]\succeq0.
}
\]

Consequences:

- hard quantization cannot increase Fisher information;
- all retained-information criteria here depend on a quantizer only through \((W_b,m_b)\).

## U3. Local Fisher-losslessness criterion — [BRIDGE]

\[
\boxed{
I_q=I_{\rm full}
\iff
S=h(Z)\quad\text{a.s.}
}
\]

Equivalently \(\operatorname{Cov}(S\mid Z)=0\) a.s. Generic smooth score laws cannot be exactly lossless for finite \(K\).

## U4. Rank ceiling — [BRIDGE]

Since \(\sum_bm_b=0\),

\[
\operatorname{rank}(I_q)\le\min(d,K-1).
\]

Therefore \(K\ge d+1\) is necessary for nonsingular full-D information.

## U5. Refinement monotonicity — [BRIDGE]

If \(\mathcal P'\) refines \(\mathcal P\), then

\[
I_{\mathcal P'}\succeq I_{\mathcal P}.
\]

This powers branch-and-bound upper bounds for every Loewner-monotone criterion.

## U6. Reparameterization invariance of D — [BRIDGE]

Under an invertible local parameter transformation, \(I_q\) transforms by congruence and \(\log\det I_q\) changes only by a quantizer-independent constant. D-optimal partitions are therefore invariant under invertible reparameterization.

## U7. Normalized retained-information spectrum — [BRIDGE]

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

A finite global optimum is exchange stable, hence strict D-Voronoi. Therefore unrestricted finite D assignment optimization and global optimization over the corresponding realizable D-Voronoi/affine-max labelings have the same optimum value.

This does **not** say every D-Voronoi fixed point is globally optimal.

## D8. Monotone exact one-point exchange — [PROJECT-PROVED]

Accepting only exact positive D gains gives:

- strict objective ascent;
- no cycles;
- finite termination because the labeling set is finite;
- a terminal one-point exchange-stable solution;
- by D5/D6, a canonical deployable D quantizer.

## D9. Adaptive Mahalanobis Lloyd is not monotone — [COUNTEREXAMPLE]

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

Measured suite: 35/100 Lloyd/Voronoi fixed points still admitted an exact improving one-point move, with improvements up to about 1.033 nat.

## D11. Exact global enumeration for fixed \((d,K)\) — [PROJECT-PROVED]

D7 restricts candidate global labelings to affine-max-realizable partitions. Arrangement enumeration gives an exact XP algorithm of form

\[
\boxed{N^{O(Kd)}}
\]

for fixed \((d,K)\), with an effective affine parameter count of order \((K-1)(d+1)\).

This is an application of a known computational-geometry template; hardness/FPT status remains open.

## D12. Singleton-refinement branch-and-bound bound — [PROJECT-PROVED]

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

Let \(\theta=(\psi,\lambda)\) and

\[
F_s(I)
=\log\det S_\psi(I)
=\log\det I-\log\det I_{\lambda\lambda}
\]

in the nonsingular block regime.

## DS1. Classical \(D_s\) design theory — [LIT]

Wynn, Whittle, Näther–Reinsch, Kiefer/general equivalence theory provide classical subset/nuisance-parameter optimal design, sensitivity, and singular-case tools. They do not directly solve the quantizer feasible set.

## DS2. Gradient / efficient semimetric — [PROJECT-PROVED/BRIDGE]

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

A positive first-order efficient-Voronoi margin need not imply positive exact finite \(D_s\) gain. Therefore

\[
\text{exchange stable}\not\Rightarrow\text{exact }G_s\text{-Voronoi}
\]

in general.

## DS5. A global finite \(D_s\) optimum can be non-geometric — [EXACT COUNTEREXAMPLE]

There is a centered equal-weight \(N=8,d=2,d_\psi=1,K=3\) example for which exhaustive enumeration of all 966 unlabeled nonempty partitions gives a unique global \(D_s\) optimum that violates its own efficient-semi-metric nearest-cell rule.

Canonical fixture is stored in `COUNTEREXAMPLES/CE-DS-GLOBAL-GEOMETRY-001.json`.

This proves that unrestricted finite \(D_s\) assignment and deployable self-consistent geometric \(D_s\) fitting are genuinely different finite problems.

## DS6. Approximate finite efficient-Voronoi bound — [PROJECT-PROVED]

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

## DS7. Full-data efficient-score domination — [PROJECT-PROVED]

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

For \(d_\psi=1\), deterministic D-optimal quantization of a scalar atomless efficient score has ordered interval cells. On a finite sample the optimal interval partition can be solved exactly by dynamic programming.

Consequences:

- cheap globally optimal upper bound for in-bin \(D_s\);
- strong initializer;
- explicit optimality-gap certificate for a found \(D_s\) solution.

Measured certificate gaps were 0.003–0.118 nat on reported \(d=3,d_\psi=1,K=4,N=60\) tests and 0.011–0.19 nat on reported \(d=4,d_\psi=2,K=5,N=80\) tests using the corresponding projected D upper problems.

## DS9. The \(K\le d\) feasibility split — [PROJECT-PROVED/STRUCTURAL]

For the **full in-bin profiled formulation**, \(I_q\) is singular when \(K\le d\), so ordinary full-block \(D_s\) profiling is not identifiable.

The projected efficient-score problem only needs enough categories to identify the \(d_\psi\)-dimensional efficient score, i.e. structurally \(K\ge d_\psi+1\), if nuisance information is supplied externally.

These are different statistical problems and must be exposed separately.

## DS10. Finite-to-population bridge remains incomplete — [OPEN]

DS6 strongly suggests asymptotic geometric closure for balanced empirical problems, but unrestricted finite \(D_s\) global/exchange-stable solutions have not yet been proved to converge to population stationary deployable quantizers.

---

# 6. E-optimality control theory

\[
F_E(I)=\lambda_{\min}(I).
\]

## E1. Supergradient structure — [LIT]

If the minimum eigenvalue is simple with unit eigenvector \(v\), one gradient is \(vv^\top\). At multiplicity \(r\) with basis \(V\),

\[
\partial^+\lambda_{\min}(I)
=\{VHV^\top:H\succeq0,\ \operatorname{tr}H=1\}.
\]

## E2. Repeated-eigenvalue one-transfer degeneracy — [PROJECT-PROVED]

For one infinitesimal transfer \(\Delta I=aa^\top-bb^\top\),

\[
d\lambda_{\min}(I;\Delta I)
=\lambda_{\min}(V^\top\Delta I V)\le0
\]

whenever the minimum eigenspace dimension is \(r\ge2\). Thus one-point first-order stability can become automatic/non-identifying exactly where E tends to equalize weak directions.

## E3. Finite global E geometry fails even with simple minimum eigenvalue — [COUNTEREXAMPLE]

Exhaustive \(N=8,d=2,K=3\) search produced a global E optimum whose own rank-one \(vv^\top\) nearest-cell rule disagrees with a training label; reported margin \(\approx0.06796\).

## E4. Positive first-order E margin need not imply exact improvement — [COUNTEREXAMPLE]

Reported suite: 2,167/8,965 subgradient-rule-improving moves had strictly negative exact E gain; one example had margin 2.27 and exact change \(-0.240\).

## E5. Safe E screening and B&B — [PROJECT-PROVED]

G2 gives a sound rejection rule. Exact post-move \(\lambda_{\min}\) evaluation can be reserved for screened-in candidates. Refinement B&B applies because \(\lambda_{\min}\) is Loewner-monotone.

## E6. Common-supergradient population geometry — [OPEN]

It remains open whether every suitable population E optimum admits one common supergradient that supports all cell-assignment inequalities almost everywhere.

---

# 7. A-optimality control theory

\[
F_A(I)=-\operatorname{tr}(I^{-1}),
\qquad
G_A=I^{-2}.
\]

## A1. Exact finite move oracle — [PROJECT-PROVED]

The universal rank-two \(\Delta I\) plus Woodbury gives an exact \(O(d^2)\)-type A move oracle; exact positive-gain exchange is monotone and finitely terminating.

## A2. D-style finite geometry theorem fails — [COUNTEREXAMPLE]

The reported search found 443 A moves violating the would-be D-style implication. Therefore finite exchange stability does not generally collapse to the first-order \(I^{-2}\) Voronoi rule.

## A3. Concavity screening remains valid — [PROJECT-PROVED]

G2 supplies a sound tangent rejection rule for A.

## A4. Quantitative A necessity bound — [OPEN]

No analogue of the \(D_s\) Prop.-17-style \(O(w)\) violation bound has yet been derived.

---

# 8. Randomized/soft quantizers and empirical geometric optimization

## S1. Soft assignments are an actual randomized quantizer — [PROJECT-PROVED/BRIDGE]

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

For differentiable \(F\), \(G=\nabla F(I_{\rm soft})\),

\[
\boxed{
\frac{\partial F}{\partial r_{ib}}
=w_i(2s_i^\top G\mu_b-\mu_b^\top G\mu_b).
}
\]

Up to a bin-independent term this is negative squared \(G\)-distance to the centroid.

## S3. Hard empirical geometric objective is piecewise constant — [PROJECT-PROVED/OBSERVATION]

For a hard affine/Voronoi quantizer parameterized by continuous generators/hyperplanes, the finite empirical objective is piecewise constant in those parameters: until a training row crosses a boundary, labels and cell moments do not change.

Therefore ordinary gradient descent on the **hard finite** objective is zero almost everywhere and is not a useful generic solver.

## S4. Fixed-temperature soft optimization has ordinary stationary-point guarantees — [BRIDGE]

A positive-temperature softmax affine-max family is smooth away from empty cells/singular information. Line-search gradient ascent or quasi-Newton optimization can be made monotone in the soft objective; standard nonconvex theory gives stationary-point/gradient-norm guarantees, not hard local/global optimality.

## S5. Atomless purification — [LIT + PROJECT APPLICATION]

For an atomless score law, Dvoretzky–Wald–Wolfowitz purification preserves all \((W_b,m_b)\) of a randomized finite-action quantizer. Hence randomized and deterministic quantizers have the **same population optimum value for every criterion depending only on these moments**.

This is a classical theorem applied to the present Fisher-score moment representation.

## S6. Atomic randomization gap — [OPEN]

Finite empirical score laws are atomic. Whether splitting atoms can strictly improve D/\(D_s\)/E over every deterministic hard score quantizer remains unresolved in general.

---

# 9. Empirical-to-population theory

## C1. Restricted affine-class consistency — [PROJECT-PROVED / STANDARD EMPIRICAL-PROCESS ROUTE]

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

\[
s(x)=\left.\nabla_\theta\log\frac{p(x\mid\theta)}{p(x\mid\theta_0)}\right|_{\theta_0}.
\]

Full absolute densities are not required if the relevant local density ratio is available.

## O2. Linear-mixture component ratios suffice — [BRIDGE]

For

\[
p(x\mid\theta)=\sum_\alpha\theta_\alpha\phi_\alpha(x),
\]

score coordinates depend on \(\phi_\alpha(x)/\sum_\beta\theta_{0\beta}\phi_\beta(x)\). Ratios to one reference component therefore suffice exactly after algebraic reconstruction.

## O3. Calibrated classifier posteriors provide ratios — [LIT/BRIDGE]

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

If the quantizer uses \(\hat s\), the actual retained Fisher information is

\[
\boxed{
\operatorname{Var}(E[s\mid q(\hat s)]),
}
\]

not \(\operatorname{Var}(E[\hat s\mid q(\hat s)])\) unless \(\hat s=s\) in the relevant sense.

## O5. Representation loss and quantization loss separate — [BRIDGE]

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

\[
\eta_D=(\det I_q/\det I_{\rm full})^{1/d}.
\]

## I2. \(D_s\)-efficiency — [BRIDGE]

\[
\eta_{D_s}=
(\det S_\psi(I_q)/\det S_\psi(I_{\rm full}))^{1/s}.
\]

## I3. Directional diagnostics — [BRIDGE]

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
