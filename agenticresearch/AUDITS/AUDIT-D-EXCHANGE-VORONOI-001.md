# Publication-grade audit of finite D exchange implies Voronoi

**Claim:** `D-EXCHANGE-IMPLIES-VORONOI`  
**Audit:** `AUDIT-D-EXCHANGE-VORONOI`  
**Date:** 26 August 2026  
**Result:** theorem verified after making its duplicate, feasibility, and tolerance assumptions explicit

## 1. Target statement

Let \(s_1,\ldots,s_N\in\mathbb R^d\) be the distinct atoms obtained after
merging coincident score rows, with weights \(w_i>0\). Partition the atoms into
exactly \(K\) nonempty cells. The only feasibility constraint on a relocation is
that its source cell remain nonempty. Write

\[
W_b=\sum_{i:z_i=b}w_i,\qquad
\mu_b=\frac{1}{W_b}\sum_{i:z_i=b}w_i s_i,\qquad
I=\sum_bW_b\mu_b\mu_b^\top.
\]

If \(I\succ0\) and no admissible one-atom relocation has positive exact
\(\log\det I\) gain, then

\[
(s_i-\mu_{z_i})^\top I^{-1}(s_i-\mu_{z_i})
<
(s_i-\mu_b)^\top I^{-1}(s_i-\mu_b)
\]

for every atom \(i\) and every \(b\ne z_i\). Duplicate original rows inherit
the label of their merged atom. This is an exact, zero-gain-tolerance theorem.

## 2. Criterion and problem level

- Criterion: full D, \(F_D(I)=\log\det I\).
- Level: `finite_assignment`.
- Decision variable: a hard labeling of the finite score atoms.
- Score oracle: direct finite scores; score estimation is not part of the claim.

## 3. Status before the audit

`D-EXCHANGE-IMPLIES-VORONOI` was `project_proved`; the publication-grade audit
node was `open` at priority 0.

## 4. Dependencies rechecked

The audit independently re-derived all three mathematical dependencies:

1. `D-RANK2-MOVE`: exact weighted source/destination moment update.
2. `D-LOGDET-GAIN`: the two-rank determinant ratio.
3. `D-LEVERAGE`: the centroid-difference projection bound.

There was no unresolved dependency in the proof chain. Nearby negative results
only block the converse and extensions to A, E, or \(D_s\).

## 5. Nearest literature and transfer boundary

The targeted search did not locate the finite retained-between-score theorem in
equivalent notation. This is a search gap, not a novelty claim.

- Kiefer--Wolfowitz (1960) proves the D equivalence theorem for approximate
  design measures. Its \(M^{-1}\) sensitivity geometry transfers, but its convex
  design-measure feasible set has neither partition centroids nor finite label
  relocations.
- Venkitasubramaniam--Tong--Swami (2006) quantizes scalar score functions for
  Fisher information. Score-space reduction transfers; the multivariate full-D
  finite exchange theorem does not.
- Barnes--Han--Özgür (2018) gives the conditional-score representation and
  multivariate trace-Fisher geometry. The information identity transfers; its
  objective and finite optimality conditions differ.
- Dülek (2023) proves polytopal sufficient-statistic quantizers for a trace-FIM
  problem in exponential families. It supports geometric precedent but not the
  determinant or one-point-exchange implication.
- Friedman--Rubin (1967) and Späth (1977/1985) establish determinant grouping
  and exchange precedents. The inspected Späth `DETEXM` routine minimizes the
  determinant of pooled within-cluster scatter, not the determinant of retained
  between-cell Fisher information.

## 6. Counterexample search

The exact-rational enumerator
`py/audit_d_exchange_voronoi.py` tested 80 deterministic data sets spanning
\(d=1,2,3\), the smallest rank-feasible cell counts, unequal positive weights,
singletons, tiny cells, and rational near-singular coordinate scaling. It
enumerated 8,727 positive-definite partitions, checked 97,601 admissible moves,
including 30,881 moves satisfying the non-nearest premise, and found 93 stable
partitions. Every exact identity, lower bound, and stable-to-strict-Voronoi
conclusion passed.

The search did find the minimal boundary failure when duplicates are not
merged: scores \((1,1,-1)\), weights \((1/4,1/4,1/2)\), \(K=3\), with each row
in its own cell. Information is the scalar 1 and stability is vacuous, but the
first two atoms have tied coincident centroids. The exact fixture is
`COUNTEREXAMPLES/CE-D-UNMERGED-DUPLICATES-001.json`.

## 7. Algebraic reduction

Move \((s,w)\) from non-singleton cell \(a\) to cell \(b\), and put

\[
u_a=s-\mu_a,\quad u_b=s-\mu_b,\quad
\alpha=\frac{wW_a}{W_a-w},\quad
\beta=\frac{wW_b}{W_b+w}.
\]

Direct expansion of the two affected cell moments gives

\[
W'_a\mu'_a\mu_a'^\top-W_a\mu_a\mu_a^\top
=\alpha u_au_a^\top-wss^\top,
\]

\[
W'_b\mu'_b\mu_b'^\top-W_b\mu_b\mu_b^\top
=wss^\top-\beta u_bu_b^\top,
\]

and therefore

\[
\Delta I=\alpha u_au_a^\top-\beta u_bu_b^\top.
\]

For \(H=I^{-1}\), set

\[
x=u_a^\top Hu_a,\quad y=u_b^\top Hu_b,\quad z=u_a^\top Hu_b.
\]

The matrix determinant lemma in rank two gives the exact determinant ratio

\[
R=\frac{\det(I+\Delta I)}{\det I}
=(1+\alpha x)(1-\beta y)+\alpha\beta z^2.
\]

Also

\[
\frac{\alpha-\beta}{\alpha\beta}
=\frac1{W_a}+\frac1{W_b}=:C.
\]

Let \(A=[\sqrt{W_1}\mu_1,\ldots,\sqrt{W_K}\mu_K]\), so \(I=AA^\top\), and
let \(v_a=1/\sqrt{W_a}\), \(v_b=-1/\sqrt{W_b}\), with all other coordinates
zero. Then \(P=A^\top(AA^\top)^{-1}A\) is an orthogonal projector and, for
\(\delta=\mu_a-\mu_b=Av\),

\[
q_\delta=\delta^\top H\delta=v^\top Pv\le v^\top v=C.
\]

## 8. Proof

Suppose the point is tied or worse against cell \(b\), so \(x\ge y\). Writing
\(R=1+E\),

\[
\begin{aligned}
E
&=\alpha x-\beta y-\alpha\beta(xy-z^2)\\
&=\frac{\alpha+\beta}{2}(x-y)
 +\frac{\alpha-\beta}{2}(x+y)
 -\alpha\beta(xy-z^2)\\
&\ge \alpha\beta\left[\frac{q_\delta}{2}(x+y)-(xy-z^2)\right]\\
&=\frac{\alpha\beta}{4}\left[q_\delta^2+(x-y)^2\right]\\
&\ge\frac{\alpha\beta}{4}q_\delta^2.
\end{aligned}
\]

The penultimate equality uses
\(q_\delta=(u_b-u_a)^\top H(u_b-u_a)=x+y-2z\).
If \(\mu_a\ne\mu_b\), positive definiteness gives \(q_\delta>0\), so

\[
\Delta F_D=\log R
\ge\log\left(1+\frac{\alpha\beta}{4}q_\delta^2\right)>0.
\]

The candidate information matrix is always positive semidefinite by its cell
moment representation, and \(R>1\) gives a positive determinant. It is therefore
positive definite, so the displayed log-determinant gain is well defined.

It remains to show that distinct cell centroids need not be assumed separately.
If \(\mu_a=\mu_b\) and either cell contains more than one distinct atom, that
cell contains an atom \(s\ne\mu_a\). Move such an atom from that non-singleton
cell to the other. Then \(u_a=u_b\), \(x=y=z>0\), and

\[
R=1+(\alpha-\beta)x>1,
\]

because \(\alpha>w>\beta\). If both cells are singletons, their equal centroids
are duplicate score atoms, excluded by merging. Thus exact exchange stability
itself forces distinct centroids.

Finally, an atom in a singleton source has zero distance to its own centroid.
Once centroids are distinct, its distance to every competing centroid is
strictly positive. Every non-singleton tied-or-worse comparison would yield the
strict improvement above. Therefore every atom is strictly nearest to its own
centroid.

## 9. Adversarial audit and boundary conditions

- **Ties:** a tie between distinct centroids is theorem-triggering and cannot
  survive exact stability. It is not an allowed residual degeneracy.
- **Singletons:** no removal is admissible, but strict assignment follows from
  zero own distance and distinct centroids.
- **Duplicates:** coincident atoms must be merged, or their labels must already
  be constant on each duplicate class. Split duplicates give the exact boundary
  counterexample above.
- **Weights:** every retained atom weight must be strictly positive. A zero-weight
  row is invisible to the objective and can have an arbitrary label.
- **Feasibility:** the theorem assumes no capacity, balance, minimum-mass, or
  other move restriction beyond keeping all cells nonempty. Such constraints can
  make a geometric violation inadmissible.
- **Singularity:** current \(I\succ0\) is essential. The proof does not cover
  pseudodeterminants or projected singular directions.
- **Near singularity:** there is no condition-number gap in the exact theorem;
  every positive-definite matrix is covered. Floating implementations still
  require their documented rank and gain tolerances.
- **Tolerance:** `best_gain <= epsilon` does not imply strict Voronoi geometry.
  It only bounds the exact gain of a geometric disagreement by \(\epsilon\).
  The existing boundary regression test exercises this distinction.
- **Atomic law:** the theorem is finite and atomic by design; no atomless or
  population limit is imported.
- **New events:** the conclusion concerns score-space assignment. Observation to
  score conversion remains a separate explicit step.

## 10. Algorithmic consequence

An exact positive-gain one-point D exchange algorithm terminates at a strict
self-consistent common-metric Voronoi labeling. The determinant lower bound is a
valid certificate for every observed nearest-centroid violation. This does not
make batch adaptive-Mahalanobis Lloyd monotone, prove the converse, or establish
global optimality of an exchange terminal state.

## 11. Deployability consequence

For merged positive-weight training atoms at exact stability, the final rule

\[
\widehat q(s)=\arg\min_b(s-\mu_b)^\top I^{-1}(s-\mu_b)
\]

reproduces every training label without a tie breaker and supplies a canonical
extension to unseen scores. At nonzero solver tolerance, compilation is only
tolerance-certified and may relabel boundary rows.

## 12. Information-loss consequence

The theorem is structural only. It supplies no lower bound on D-efficiency, no
bound on the worst normalized retention eigenvalue, and no held-out or
population guarantee. Those quantities must still be reported against full
unbinned Fisher information.

## 13. Updated status

- `D-EXCHANGE-IMPLIES-VORONOI`: remains `project_proved`, now with audited,
  explicit assumptions.
- `AUDIT-D-EXCHANGE-VORONOI`: `open` -> `project_proved`.
- `D-UNMERGED-DUPLICATES-FAIL`: added as `counterexample` to the unqualified
  duplicate-splitting extension.

## 14. Registry patch

`CLAIMS.json` now points the audit node to this report, sharpens the theorem and
compiler assumptions, records the duplicate counterexample, and removes the
completed audit from the priority-open index.

## 15. Regression artifacts

- `py/audit_d_exchange_voronoi.py`: deterministic exact-rational exhaustive
  audit and identity checker.
- `COUNTEREXAMPLES/CE-D-UNMERGED-DUPLICATES-001.json`: minimal exact boundary
  counterexample.
- `tests/test_research_claims.py`: regression verification of the boundary
  fixture.

## 16. Next dependency-blocking question

The next downstream blocker is `OPEN-D-EXCHANGE-CONSISTENCY`: under what margin,
cell-mass, compactness, and conditioning assumptions do empirical exact or
tolerance-stable exchange terminals converge to the population stationary set?
