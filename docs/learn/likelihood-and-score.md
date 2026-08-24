# Likelihood and score

## Likelihood

**Definition.** For observed data (x), the likelihood is the model density
viewed as a function of the parameter:

\[
L(\theta;x)=p(x\mid\theta).
\]

**Intuition.** The data are fixed; (	heta) moves. Values of (	heta) that make
the observation more plausible receive larger likelihood.

For independent events (x_1,\ldots,x_N), log likelihoods add:

\[
\ell(\theta)=\log L(\theta)=\sum_i\log p(x_i\mid\theta).
\]

**Limitation.** A likelihood is only as correct as its model. An exact optimizer
cannot remove misspecification in (p(x\mid\theta)).

## Score

**Definition.** The score is the gradient of log likelihood at a chosen
reference point (	heta_0):

\[
s(x;\theta_0)=
\left.\nabla_\theta\log p(x\mid\theta)\right|_{\theta_0}.
\]

It has one coordinate per free parameter.

**Intuition.** The score is a local arrow. Its direction says how this event
wants to move the parameters; its magnitude says how strongly. Events with
similar arrows have similar local inferential roles.

**Example.** For a Gaussian location model (x\sim\mathcal N(\mu,\sigma^2))
with known (sigma),

\[
s(x;\mu_0)=\frac{x-\mu_0}{\sigma^2}.
\]

Events below (mu_0) have negative scores, events above it have positive
scores, and distant events carry stronger local leverage.

**Limitation.** The score is local to (	heta_0). A partition optimized there
need not remain best far away. The origin also has statistical meaning: a zero
score means locally neutral evidence, so scores must not be mean-centered.

## Why the score is a compression coordinate

Near (	heta_0), a first-order expansion gives

\[
\log p(x\mid\theta)
\approx
\log p(x\mid\theta_0)
+s(x;\theta_0)^T(\theta-\theta_0).
\]

To first order, the dependence on (	heta) enters through the score. This is
the basis of **score compression**: replacing a complicated observation by a
low-dimensional vector that retains local parameter sensitivity. It does not
say that an estimated score is exact, or that local compression solves global
inference.

The statistical literature develops this idea as generalized optimal
compression and as a target for simulation-assisted learning; see the
[bibliography](../bibliography.md).

Next: [Fisher information](fisher-information.md).
