# 7. D-optimality: relocation, exchange, and compilation

D-optimality maximizes \(F_D(I)=\log\det I\) on the informative subspace. It balances all retained
directions multiplicatively and is invariant to nonsingular parameter reparameterization.

For a finite move of row \((s_i,w_i)\) from cell \(a\) to \(b\), let
\(u_a=s_i-\mu_a\), \(u_b=s_i-\mu_b\),
\(\alpha=w_iW_a/(W_a-w_i)\), and \(\beta=w_iW_b/(W_b+w_i)\).

**Theorem (exact relocation identity).** Provided the source cell remains nonempty,

$$I'=I+\alpha u_au_a^\top-\beta u_bu_b^\top.$$

**Proposition (determinant gain).** With \(G=I^{-1}\),

$$
\frac{\det I'}{\det I}=
(1+\alpha q_{aa})(1-\beta q_{bb})+\alpha\beta q_{ab}^2,
$$

where \(q_{aa}=u_a^\top Gu_a\), \(q_{bb}=u_b^\top Gu_b\), and
\(q_{ab}=u_a^\top Gu_b\).

This yields exact positive-gain exchange without a ridge.

**Theorem (finite monotonicity).** If only strictly positive exact gains are accepted, every move
increases \(\log\det I\). Because finitely many labelings exist, exact arithmetic would terminate;
floating-point implementations add a fixed gain tolerance and terminal rescan.

**Numerical evidence (adaptive-Lloyd counterexample).** Recomputing \(I^{-1}\), then moving every
row simultaneously to its nearest current Mahalanobis centroid, is not the exact exchange
algorithm. A committed eight-row, two-coordinate, three-cell fixture lowers \(\log\det I\) from
\(-3.810643\) to \(-3.947164\) in one such batch step, a decrease of 0.136521 nat. The regression
test reconstructs the metric, reassignment, and both information matrices from the rounded rows;
the exploratory search that found the fixture remains only in `research/`.

**Theorem (D gain lower bound).** Let
\(q_\Delta=(\mu_b-\mu_a)^\top G(\mu_b-\mu_a)\). If the current label violates the nearest-centroid
rule, so \(q_{aa}\ge q_{bb}\), then the determinant-ratio increment obeys

$$
\frac{\det I'}{\det I}-1
\ge \frac{\alpha\beta}{4}q_\Delta^2.
$$

Away from coincident centers this is strictly positive. A deterministic regression test checks the
inequality directly across every qualifying move of a fixed weighted configuration.

**Theorem (finite-to-inductive D bridge).** Every positive-definite one-exchange-stable D partition
is reproduced, away from ties, by assigning each training score to its nearest cell mean under the
final metric \(I^{-1}\).

This theorem justifies explicit compilation to a reusable rule. Compilation must verify label
reproduction rather than assume it.

**Proposition (cell-separation bound).** For cells \(a,b\),

$$
(\mu_a-\mu_b)^\top I^{-1}(\mu_a-\mu_b)\le W_a^{-1}+W_b^{-1}.
$$

Exact update, gain, monotonicity, separation, exhaustive small optima, and compiled-label
reproduction form the D regression laboratory.
