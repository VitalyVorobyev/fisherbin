# 4. Full D-optimality

> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and
> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.
> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.

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

**Claims:** D-EXCHANGE-IMPLIES-VORONOI, D-EXCHANGE-SCALAR-CORE, D-EXCHANGE-VIOLATION-LOWER-BOUND

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

The real-arithmetic implication from the relocation coefficients, the
nearest-centroid premise, and the leverage bound to this strengthened
inequality is machine-checked as `D-EXCHANGE-SCALAR-CORE` in
`formal/ScoreQuantFormal/ScalarExchange.lean`. This is deliberately a partial
formalization: the matrix determinant reduction and the remaining strict
Voronoi argument are still certified by the informal proof and independent
audit below, not yet by Lean.

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
