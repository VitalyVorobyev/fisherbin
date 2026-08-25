# 5. Trace criterion and weighted k-means

Take the trace of the loss identity:

$$\operatorname{tr}(I_\infty-I_q)
=\sum_b\int_{q(s)=b}\|s-\mu_b\|^2d\nu(s).$$

Thus Euclidean weighted k-means maximizes retained trace in the chosen coordinates. Parameter units
make raw Euclidean distance arbitrary, so a useful normalized criterion first projects onto the
informative subspace and whitens by \(I_\infty^{-1/2}\).

**Proposition (normalized-trace equivalence).** In whitened coordinates \(u=I_\infty^{-1/2}s\),
minimizing weighted within-cell squared error is equivalent to maximizing
\(\operatorname{tr}(I_\infty^{-1/2}I_qI_\infty^{-1/2})\).

Weighted Lloyd iteration alternates:

1. assign every positive-weight row to its nearest center;
2. replace each center with the weighted mean of its assigned rows.

**Theorem (Lloyd decrease).** With a fixed metric, each assignment step and each centroid step
weakly decreases weighted distortion. With deterministic tie handling and finitely many labelings,
the hard-label sequence reaches a fixed labeling.

*Proof sketch.* Nearest-center assignment minimizes each row term with centers fixed. The weighted
mean uniquely minimizes the sum of squared distances within a nonempty cell. The objective cannot
increase at either step.

This theorem does not apply if the metric is recomputed from the current D-information after every
batch assignment: that is a different adaptive algorithm and can lose monotonicity.

**Numerical evidence.** Deterministic tests verify the fixed-metric Lloyd history, row-order and
weight invariances, and hardened held-out information. Multiple seeded initializations are still
needed because k-means is nonconvex.
