# Constructing scores

FisherBin does not require one particular score estimator. It requires finite
score vectors expressed in a stable parameter order.

## Exact likelihood derivatives

If (p(x\mid\theta)) is differentiable and evaluable, compute
(\nabla_\theta\log p) analytically or with automatic differentiation. This is
the cleanest oracle case.

**Limitation.** Many simulators can sample events but cannot evaluate their
likelihood.

## Linear components

For an intensity

\[
\lambda(x;\theta)=\sum_k\theta_k\phi_k(x),
\]

the derivative score is

\[
s_k(x)=\frac{\phi_k(x)}{\lambda(x;\theta_0)}.
\]

The components need not be normalized densities. Individual terms may be
signed, but the total reference intensity must be finite and positive on every
integration row. Use `fit` for callable components or `fit_components` for an
already evaluated component matrix.

## Classifier posteriors and learned ratios

For a (K)-component mixture, train a classifier to distinguish component
samples. If (q_k(x)) is its posterior under class prior (pi_k), Bayes' rule
gives a density ratio up to a common event-wise factor:

\[
r_k(x)=\frac{q_k(x)}{\pi_k}\propto p_k(x).
\]

At an interior reference composition (	heta_0), choosing component (r) as
the simplex reference gives (K-1) scores:

\[
s_a(x)=
\frac{r_a(x)-r_r(x)}{\sum_k r_k(x)\theta_{0k}},
\qquad a\ne r.
\]

`mixture_scores_from_posteriors` implements exactly this transformation. It
accepts any classifier's ready posteriors and adds no classifier protocol or
training dependency.

**Limitation.** Posterior calibration and prior consistency are part of the
application. Clipping, hidden normalization, or evaluating calibration choices
on the final test cohort can conceal model bias. Learned likelihood-ratio and
score methods are powerful, but their output is an estimator rather than an
oracle; see the primary simulation-assisted inference papers in the
[bibliography](../bibliography.md).

## Event-sensitivity regression

When simulations expose how event weights change with parameters, one can
regress those derivatives directly. This provides another route to local
scores without a tractable event density.

**Limitation.** Its validity depends on the simulator derivatives, sampling
measure, and regression generalization.

Next: [partition algorithms](algorithms.md).
