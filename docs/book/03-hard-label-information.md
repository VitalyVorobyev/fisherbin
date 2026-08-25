# 3. Fisher information after hard labels

Let a hard label \(B=q(S)\) take \(K\) values. With measure \(\nu\), define

$$W_b=\int_{q(s)=b}d\nu(s),\qquad
m_b=\int_{q(s)=b}s\,d\nu(s),\qquad \mu_b=m_b/W_b.$$

The information supplied by the label counts is

$$I_q=\sum_{b=1}^K\frac{m_bm_b^\top}{W_b}=\sum_bW_b\mu_b\mu_b^\top.$$

**Theorem (loss identity).** If \(I_\infty=\int ss^\top d\nu(s)\), then

$$I_\infty-I_q=sum_b\int_{q(s)=b}(s-\mu_b)(s-\mu_b)^\top d\nu(s)\succeq0.$$

*Proof.* Expand the right side cell by cell and use \(m_b=W_b\mu_b\).

Immediate consequences are important.

**Proposition (refinement).** Splitting cells cannot decrease information in the positive-semidefinite
order. It removes within-cell scatter and never adds it.

**Proposition (rank).** \(\operatorname{rank}(I_q)\le\min(p,K)\). For a normalized probability
score, \(\sum_bm_b=0\), so \(\operatorname{rank}(I_q)\le K-1\).

**Proposition (invariances).** Information criteria normalized to \(I_\infty\) are unchanged by
row permutation, bin relabeling, common positive weight scaling, and replacing a row by identical
copies whose weights sum to the original. Under a nonsingular parameter transformation
\(s'=A^{-\top}s\), D-efficiency is unchanged.

Zero-weight rows contribute neither moments nor information. They may still be assigned by a
separately defined future-event rule.

### A two-point laboratory

For scores \(-1,+1\) with equal measure, one cell has mean zero and retains no information; two
singleton cells retain all information. This is both an exact example of refinement and a warning
that occupancy alone says nothing about sensitivity.
