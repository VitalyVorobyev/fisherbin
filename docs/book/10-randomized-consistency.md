# 10. Randomized quantizers, purification, and consistency

A randomized quantizer assigns responsibilities \(r_b(s)\ge0\) with \(\sum_br_b(s)=1\). Its cell
moments are

$$W_b=E[r_b(S)],\qquad m_b=E[r_b(S)S],$$

and its information uses the same \(\sum_bm_bm_b^\top/W_b\) algebra.

For differentiable \(F\), the finite-sample responsibility derivative is

$$
\frac{\partial F}{\partial r_{ib}}
=w_i\left(2s_i^\top G\mu_b-\mu_b^\top G\mu_b\right).
$$

Softmax responsibilities make boundary parameters differentiable and allow annealed optimization.
The final hard rule can have a lower objective; this hardening gap is an empirical diagnostic, not
an optimizer implementation detail.

**Theorem (purification, informal form).** Under appropriate atomlessness and finite-dimensional
moment conditions, randomized cell moments can be matched by a deterministic partition. Atomic
empirical laws do not satisfy this assumption automatically.

Thus a soft optimum on a fixed table need not correspond exactly to any hard assignment of that
same table. Conversely, a hard empirical optimum need not define a stable future-event rule.

**Proposition (fixed-rule consistency).** For a fixed bounded quantizer and integrable score moments,
empirical cell weights and moments converge to their population values by the law of large numbers.

Uniform consistency over a learned nonconvex family requires additional capacity, continuity, and
identifiability assumptions. Validation data estimates generalization but must not select
checkpoints if it is promised to be diagnostic only.

**Open problem.** Obtain finite-sample excess-information bounds for learned common-metric
quantizers under weak tail assumptions and possible near-empty cells.
