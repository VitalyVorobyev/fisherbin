# 1. Likelihood, score, and score law

Let \(X\) have a model indexed by \(\theta\in\mathbb R^p\), and fix the reference point
\(\theta_0\). The local score is

$$s(x)=\nabla_\theta\log p(x\mid\theta)\vert_{\theta_0}.$$

It is not merely a feature embedding: its origin, units, and linear transformations correspond to
a parameterization. Replacing \(s\) by \(As\) represents a nonsingular local reparameterization;
replacing it by \(s-c\) generally changes the statistical problem.

**Proposition (score-law reduction).** For any quantizer that depends on observations only through
their score, every cell moment and every information criterion considered here depends on the
observation model only through the push-forward law \(P_S=s_\#P_{\theta_0}\).

*Reason.* Integrals of any function \(g(s(x))\) under the observation law equal integrals of
\(g(S)\) under its push-forward law. Cell indicators and cell score moments are such functions.

This gives the basic separation

```text
reference measure on X + map X -> S = induced score law on S.
```

A table of score rows and weights approximates this law empirically. A bounded density plus
quadrature approximates it deterministically. A callback alone supplies the map but no expectation.

**Theorem (probability-score closure).** Under the regularity conditions that permit
differentiation under the integral, a normalized probability model satisfies
\(E_{\theta_0}[s(X)]=0\).

*Proof.* Differentiate \(\int p(x\mid\theta)dx=1\):
\(0=\int \partial_\theta p\,dx=\int p\,\partial_\theta\log p\,dx\).

This theorem is a diagnostic, not an instruction to center an empirical score table. Centering can
hide model, integration, or classifier error and changes intensity-score semantics.

**Open problem.** How should one design a single hard rule over a large reference region rather
than at one \(\theta_0\), while retaining interpretable guarantees and manageable computation?
