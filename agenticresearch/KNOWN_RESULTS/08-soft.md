# 8. Randomized/soft quantizers and empirical geometric optimization

> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and
> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.
> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.

## S1. Soft assignments are an actual randomized quantizer — [PROJECT-PROVED/BRIDGE]

**Claims:** SOFT-RANDOMIZED-FIM

For \(r_{ib}\ge0\), \(\sum_br_{ib}=1\),

\[
W_b=\sum_iw_ir_{ib},\qquad
m_b=\sum_iw_ir_{ib}s_i,
\]

\[
\boxed{
I_{\rm soft}=\sum_b\frac{m_bm_b^\top}{W_b}.
}
\]

This is exactly the Fisher information of the corresponding randomized categorical observation at the reference point, provided the randomization rule is held fixed with respect to \(\theta\).

## S2. Exact soft-assignment gradient — [PROJECT-PROVED]

**Claims:** SOFT-ASSIGNMENT-GRADIENT

For differentiable \(F\), \(G=\nabla F(I_{\rm soft})\),

\[
\boxed{
\frac{\partial F}{\partial r_{ib}}
=w_i(2s_i^\top G\mu_b-\mu_b^\top G\mu_b).
}
\]

Up to a bin-independent term this is negative squared \(G\)-distance to the centroid.

## S3. Hard empirical geometric objective is piecewise constant — [PROJECT-PROVED/OBSERVATION]

**Claims:** HARD-GEOMETRIC-EMPIRICAL-PIECEWISE-CONSTANT

For a hard affine/Voronoi quantizer parameterized by continuous generators/hyperplanes, the finite empirical objective is piecewise constant in those parameters: until a training row crosses a boundary, labels and cell moments do not change.

Therefore ordinary gradient descent on the **hard finite** objective is zero almost everywhere and is not a useful generic solver.

## S4. Fixed-temperature soft optimization has ordinary stationary-point guarantees — [BRIDGE]

**Claims:** SOFT-FIXED-TEMP-STATIONARY

A positive-temperature softmax affine-max family is smooth away from empty cells/singular information. Line-search gradient ascent or quasi-Newton optimization can be made monotone in the soft objective; standard nonconvex theory gives stationary-point/gradient-norm guarantees, not hard local/global optimality.

## S5. Atomless purification — [LIT + PROJECT APPLICATION]

**Claims:** DWW-PURIFICATION-MOMENTS, SOFT-HARD-ATOMLESS-EQUIVALENCE

For an atomless score law, Dvoretzky–Wald–Wolfowitz purification preserves all \((W_b,m_b)\) of a randomized finite-action quantizer. Hence randomized and deterministic quantizers have the **same population optimum value for every criterion depending only on these moments**.

This is a classical theorem applied to the present Fisher-score moment representation.

## S6. Atomic randomization gap — [OPEN]

Finite empirical score laws are atomic. Whether splitting atoms can strictly improve D/\(D_s\)/E over every deterministic hard score quantizer remains unresolved in general.

---
