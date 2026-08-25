# 2. Probability-score and intensity-score models

For independent observations from a normalized density, the one-event Fisher information is

$$I(\theta_0)=E[s(X)s(X)^\top],$$

and the score has zero mean under standard regularity assumptions.

Many event analyses instead observe a Poisson point process with intensity
\(\lambda(x;\theta)\). Its log likelihood is

$$\ell(\theta)=\sum_i\log\lambda(x_i;\theta)-\int\lambda(x;\theta)dx.$$

Define the event score \(s(x)=\nabla_\theta\log\lambda(x;\theta_0)\). Then

$$I(\theta_0)=\int \lambda(x;\theta_0)s(x)s(x)^\top dx.$$

The compensator makes the full likelihood score mean zero, but the event-score mean under the
intensity measure is \(\int\partial_\theta\lambda\,dx\), generally nonzero.

**Proposition (do not center intensity scores).** Subtracting the empirical mean event score can
remove the total-rate direction and therefore lower or change the information represented by
Poisson counts.

For a linear intensity

$$\lambda(x;\theta)=\sum_{\alpha=1}^p\theta_\alpha\phi_\alpha(x),$$

the event score is

$$s_\alpha(x)=\frac{\phi_\alpha(x)}{\lambda(x;\theta_0)}.$$

Components need not be normalized densities, and their individual signs need not be constrained;
the reference intensity must be finite and strictly positive on the integration domain.

Normalized finite mixtures have a different parameter geometry because fractions lie on a
simplex. If component \(r\) is dependent, the independent score coordinates are differences of
component density ratios relative to \(r\), divided by the mixture density. Choosing another
dependent component is a reparameterization, not a different physical model.

**Numerical evidence.** In the FlowCyt capstone, closure of mean constrained-mixture scores is
checked by patient and by fold. Residual nonclosure is treated as classifier/integration error,
never repaired by centering.
