# 6. Population first variation and geometry

Consider moving an infinitesimal mass at score \(s\) into cell \(b\). For a differentiable matrix
criterion \(F(I)\) with gradient \(G=\nabla_I F\), the first-order cell utility is

$$h_b(s)=2s^\top G\mu_b-\mu_b^\top G\mu_b.$$

**Proposition (first variation).** At a stationary population partition, almost every score is
assigned to a cell maximizing \(h_b(s)\).

The utility is affine in \(s\). Pairwise boundaries are hyperplanes. If \(G\succeq0\), maximizing
utility is equivalent to minimizing

$$d_b(s)=(s-\mu_b)^\top G(s-\mu_b),$$

up to the common term \(s^\top Gs\). Singular \(G\) gives a semimetric: differences in its null
space do not affect assignment.

**Theorem (common-metric geometry).** For a differentiable monotone information criterion with a
fixed positive-semidefinite gradient at a stationary solution, its cells form a common-metric
Mahalanobis Voronoi diagram, modulo ties and null directions.

This is a population first-order statement. Finite relocation changes both affected centroids and
the metric by a noninfinitesimal amount. Treating the population rule as an exact finite rule is a
category error unless a criterion-specific theorem supplies the bridge.

For D, \(G=I^{-1}\) and such a finite bridge exists at exchange stability. For profiled \(D_s\),
the gradient is an efficient-score semimetric but exact finite optima can violate it. For E,
nondifferentiability at eigenvalue multiplicity makes the geometry nonunique even at population
level.

**Open problem.** Establish useful finite-sample geometry-gap rates for broad weighted atomic laws,
not only balanced small-weight regimes.
