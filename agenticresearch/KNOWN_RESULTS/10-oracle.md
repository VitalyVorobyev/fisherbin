# 10. Score/density-ratio/classifier access

> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and
> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.
> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.

## O1. Density ratios suffice for local scores — [BRIDGE]

**Claims:** RATIO-LOCAL-SCORE

\[
s(x)=\left.\nabla_\theta\log\frac{p(x\mid\theta)}{p(x\mid\theta_0)}\right|_{\theta_0}.
\]

Full absolute densities are not required if the relevant local density ratio is available.

## O2. Linear-mixture component ratios suffice — [BRIDGE]

**Claims:** MIXTURE-RATIO-SCORE

For

\[
p(x\mid\theta)=\sum_\alpha\theta_\alpha\phi_\alpha(x),
\]

score coordinates depend on \(\phi_\alpha(x)/\sum_\beta\theta_{0\beta}\phi_\beta(x)\). Ratios to one reference component therefore suffice exactly after algebraic reconstruction.

## O3. Calibrated classifier posteriors provide ratios — [LIT/BRIDGE]

**Claims:** CLASSIFIER-MIXTURE-SCORE-FORMULA, CLASSIFIER-RATIO-ORACLE

With class priors \(\pi_\alpha\), posterior odds recover component density ratios. In the mixture parameterization,

\[
\boxed{
s_\alpha(x)=
\frac{\eta_\alpha(x)/\pi_\alpha}
{\sum_\beta\theta_{0\beta}\eta_\beta(x)/\pi_\beta}.
}
\]

Estimated classifiers solve the exact score problem only to the extent that they recover calibrated ratios.

## O4. True retained FI under an estimated score — [BRIDGE]

**Claims:** PROXY-TRUE-RETAINED-FI

If the quantizer uses \(\hat s\), the actual retained Fisher information is

\[
\boxed{
\operatorname{Var}(E[s\mid q(\hat s)]),
}
\]

not \(\operatorname{Var}(E[\hat s\mid q(\hat s)])\) unless \(\hat s=s\) in the relevant sense.

## O5. Representation loss and quantization loss separate — [BRIDGE]

**Claims:** REPRESENTATION-QUANTIZATION-LOSS

For a representation \(R(X)\),

\[
I_R=\operatorname{Var}(E[s\mid R]),
\qquad
I_q\preceq I_R\preceq I_{\rm full}.
\]

This separates oracle/representation loss from hard-quantization loss whenever truth scores are available for validation.

---
