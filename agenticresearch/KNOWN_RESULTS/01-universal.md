# 1. Universal information structure

> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and
> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.
> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.

## U1. Quantized Fisher-information identity — [LIT]

**Claims:** FI-QUANT-IDENTITY

For \(Z=q(S)\),

\[
\nabla_\theta\log P_\theta(Z=b)|_{\theta_0}
=E[S\mid Z=b]=\mu_b,
\]

hence

\[
\boxed{
I_q
=\operatorname{Var}(E[S\mid Z])
=\sum_bW_b\mu_b\mu_b^\top
=\sum_b\frac{m_bm_b^\top}{W_b}.
}
\]

Closest direct literature: score-function quantization; Barnes–Han–Özgür.

## U2. Exact information-loss decomposition — [LIT/BRIDGE]

**Claims:** FI-LOSS-DECOMPOSITION

\[
\boxed{
I_{\rm full}-I_q=E[\operatorname{Cov}(S\mid Z)]\succeq0.
}
\]

Consequences:

- hard quantization cannot increase Fisher information;
- all retained-information criteria here depend on a quantizer only through \((W_b,m_b)\).

## U3. Local Fisher-losslessness criterion — [BRIDGE]

**Claims:** FI-LOSSLESS-IFF-SCORE-MEASURABLE

\[
\boxed{
I_q=I_{\rm full}
\iff
S=h(Z)\quad\text{a.s.}
}
\]

Equivalently \(\operatorname{Cov}(S\mid Z)=0\) a.s. Generic smooth score laws cannot be exactly lossless for finite \(K\).

## U4. Rank ceiling — [BRIDGE]

**Claims:** FI-RANK-CEILING

Since \(\sum_bm_b=0\),

\[
\operatorname{rank}(I_q)\le\min(d,K-1).
\]

Therefore \(K\ge d+1\) is necessary for nonsingular full-D information.

## U5. Refinement monotonicity — [BRIDGE]

**Claims:** FI-REFINEMENT-MONOTONICITY, GENERAL-REFINEMENT-BB

If \(\mathcal P'\) refines \(\mathcal P\), then

\[
I_{\mathcal P'}\succeq I_{\mathcal P}.
\]

This powers branch-and-bound upper bounds for every Loewner-monotone criterion.

## U6. Reparameterization invariance of D — [BRIDGE]

**Claims:** D-REPARAM-INVARIANCE

Under an invertible local parameter transformation, \(I_q\) transforms by congruence and \(\log\det I_q\) changes only by a quantizer-independent constant. D-optimal partitions are therefore invariant under invertible reparameterization.

## U7. Normalized retained-information spectrum — [BRIDGE]

**Claims:** INFO-RETENTION-SPECTRUM

\[
R=I_{\rm full}^{-1/2}I_qI_{\rm full}^{-1/2},
\qquad 0\preceq R\preceq I.
\]

Thus every retention eigenvalue lies in \([0,1]\). Natural summaries are

\[
\frac1d\operatorname{tr}R,
\qquad
(\det R)^{1/d},
\qquad
\lambda_{\min}(R).
\]

The middle quantity is D-efficiency.

---
