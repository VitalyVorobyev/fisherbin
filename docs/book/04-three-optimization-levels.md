# 4. Three optimization levels

The same cell-moment algebra supports three noninterchangeable decision problems.

## Population design

Choose any measurable \(q:\mathbb R^p\to\{1,\ldots,K\}\) to optimize an expectation under a fixed
score law. This is the clean variational problem. It assumes that the law or its cell moments can be
evaluated accurately.

## Empirical quantizer fitting

Choose parameters \(\eta\) in a deployable family \(q_\eta\) using a weighted sample or numerical
integration. Evaluation concerns the rule on future draws, not only its labels on training rows.
Generalization, geometry, hardening, and validation diagnostics belong here.

## Finite assignment

Choose arbitrary labels \(b_1,\ldots,b_N\) for one fixed table. This has \(K^N\) raw assignments
before label symmetry. It may outperform a restricted quantizer family on those same rows while
providing no answer for a new score.

**Proposition (underdetermination).** Any finite assignment of distinct points admits infinitely many
extensions to the rest of score space. Therefore labels alone cannot define a unique predictor.

The tasks are linked only by additional results. For stable nonsingular finite D assignment, a
canonical Mahalanobis extension exists. No analogous generic implication holds for profiled
\(D_s\) or E.

Sources and score providers make the data contract equally explicit:

```text
Source: which rows or integration nodes, with which measure?
ScoreProvider: which tangent vector is assigned to each observation?
```

**Numerical evidence.** Equivalent precomputed-score, observation-callback, and bounded-quadrature
constructions are regression-tested against the same numerical core.

**Open problem.** Which restrictions on a score law guarantee convergence of an empirical
quantizer family to a population optimum rather than merely convergence of objective values?
