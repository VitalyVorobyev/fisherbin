# 9. E-optimality: multiplicity and supergradients

E-optimality maximizes the weakest retained direction:

$$F_E(I)=\lambda_{\min}(I).$$

If the minimum eigenvalue is simple with unit eigenvector \(v\), a gradient is \(vv^\top\), and the
population first variation suggests a rank-one distance along \(v\).

At multiplicity, the function is nonsmooth.

**Theorem (minimum-eigenspace supergradients).** If \(V\) spans the minimum eigenspace, the valid
supergradients are

$$G=VHV^\top,\qquad H\succeq0,\quad\operatorname{tr}H=1.$$

Therefore no unique E geometry exists at eigenvalue multiplicity.

Even a simple eigenvalue does not give an exact finite bridge.

**Numerical evidence (exhaustive fixture).** Exhaustive enumeration of a fixed eight-point, two-dimensional,
three-cell instance finds a global finite E optimum with a simple minimum eigenvalue whose row 7 is
not assigned to its nearest cell under \(vv^\top\). The violation exceeds \(0.06\). The fixed
decimal instance and exhaustive search are deterministic regression evidence for the counterexample;
the general conclusion follows from the existence of that verified instance.

Exact finite E exchange can still recompute eigenvalues after each candidate move. Supergradients
are useful for screening, not for silently compiling arbitrary labels to a predictor.

**Open problem.** Find an inductive E quantizer parameterization and optimization method that handles
eigenvalue crossings without unstable arbitrary eigenvector choices.
