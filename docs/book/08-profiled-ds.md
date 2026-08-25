# 8. Profiled \(D_s\): efficient scores, bounds, and a counterexample

Partition parameters into interest \(\psi\) and nuisance \(\lambda\):

$$I=\begin{pmatrix}A&B\\B^\top&C\end{pmatrix},\qquad
S=A-BC^{-1}B^\top.$$

Profiled D-optimality maximizes \(\log\det S\). Define
\(L=[I,-BC^{-1}]\). The binned efficient score is \(Ls\), and the population gradient metric is

$$G_s=L^\top S^{-1}L.$$

**Proposition (population efficient geometry).** At a differentiable stationary population
solution, cells are nearest-centroid regions in the semimetric \(G_s\).

The finite problem differs. A point relocation changes nuisance profiling as well as cell moments.

**Theorem (exact counterexample).** There exists an eight-atom, two-coordinate, three-cell uniform
law whose unique globally optimal finite profiled-\(D_s\) assignment violates its own
\(G_s\)-nearest-centroid rule.

The repository verifies this with rational arithmetic. The optimum has Schur value
\(20449/1920\), a gap \(2929/21120\) to the second assignment, and a rule violation \(8/195\).
No floating-point search is needed to establish the signs.

**Proposition (stable finite gap bound).** At one-point exchange stability, the positive efficient
geometry violation for moving row \(i\) from \(a\) to \(b\) is bounded by a term proportional to

$$w_i q_{aa}\left(W_a^{-1}+W_b^{-1}\right).$$

For balanced uniform cells this is typically \(O(K/N)\), explaining why population geometry can be
a good approximation without becoming an exact finite theorem.

The full-information efficient score supplies a lower-dimensional D upper problem when nuisance
information is external or fixed. It is not automatically identical to profiling nuisance from the
same binned labels.

**Open problem.** Design an inductive profiled-\(D_s\) solver with a useful certified geometry gap
and robust behavior near singular nuisance blocks.
