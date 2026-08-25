# Motivation

ScoreQuant reduces continuous or high-dimensional events to hard labels while preserving
information about a local parameter vector. Its canonical pipeline is

```text
Source + ScoreProvider -> score law -> partition or quantizer
```

The source supplies a measure. The provider supplies the observation-to-score map. Neither
capability substitutes for the other.

## Statistical object

At a reference point \(\theta_0\), a probability model has score

$$
s(x)=\nabla_\theta\log p(x\mid\theta)\vert_{\theta_0}.
$$

An intensity model uses the corresponding event score
\(\nabla_\theta\log\lambda(x;\theta)\). A hard rule \(q\) retains the between-cell information

$$
I_q=\sum_b W_b\mu_b\mu_b^\top,
\qquad W_b=E[1_{q(s)=b}],\quad \mu_b=E[s\mid q(s)=b].
$$

ScoreQuant optimizes a matrix criterion of this supplied-score information. It never centers
scores: the score-space origin has statistical meaning.

## Three different optimization problems

1. **Population design** optimizes a measurable rule under a specified score law.
2. **Empirical quantizer fitting** learns a reusable rule in a chosen function family from a
   finite or quadrature approximation to that law.
3. **Finite assignment** chooses labels for one fixed weighted score table.

The first two are inductive; the third is transductive. A finite labeling underdetermines what
happens to a future score. D-optimal exchange has a theorem-backed compilation at a nonsingular,
one-point-stable state. Profiled \(D_s\) and E-optimality do not have that implication in general.

## Exact, supplied, and surrogate information

If supplied vectors are the true model score, their second moment is Fisher information. If they
are estimated classifier scores \(\hat s\), the same algebra is exact for the supplied vectors but
is only a surrogate for the original model:

$$
\widehat I_q=\operatorname{Var}(E[\hat s\mid q(\hat s)]),\qquad
I_q^{\mathrm{true}}=\operatorname{Var}(E[s\mid q(\hat s)]).
$$

Results therefore carry score provenance. Classifier calibration, cross-fitting, and training are
application responsibilities; their error must not be reported as quantization loss.

## Intended use and non-goals

ScoreQuant is useful when downstream inference requires hard gates, categories, or template
counts and local parameter sensitivity matters more than proximity in observation space. It is
not a general compressor, classifier trainer, complete likelihood framework, or proof that an
upstream simulator or learned ratio is unbiased.
