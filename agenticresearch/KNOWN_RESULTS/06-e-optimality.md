# 6. E-optimality control theory

> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and
> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.
> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.

\[
F_E(I)=\lambda_{\min}(I).
\]

## E1. Supergradient structure — [LIT]

**Claims:** E-SUPERGRADIENT

If the minimum eigenvalue is simple with unit eigenvector \(v\), one gradient is \(vv^\top\). At multiplicity \(r\) with basis \(V\),

\[
\partial^+\lambda_{\min}(I)
=\{VHV^\top:H\succeq0,\ \operatorname{tr}H=1\}.
\]

## E2. Repeated-eigenvalue one-transfer degeneracy — [PROJECT-PROVED]

**Claims:** E-REPEATED-EIGEN-DEGENERACY

For one infinitesimal transfer \(\Delta I=aa^\top-bb^\top\),

\[
d\lambda_{\min}(I;\Delta I)
=\lambda_{\min}(V^\top\Delta I V)\le0
\]

whenever the minimum eigenspace dimension is \(r\ge2\). Thus one-point first-order stability can become automatic/non-identifying exactly where E tends to equalize weak directions.

## E3. Finite global E geometry fails even with simple minimum eigenvalue — [COUNTEREXAMPLE]

**Claims:** E-GLOBAL-GEOMETRY-FAILS

Exhaustive \(N=8,d=2,K=3\) search produced a global E optimum whose own rank-one \(vv^\top\) nearest-cell rule disagrees with a training label; reported margin \(\approx0.06796\).

## E4. Positive first-order E margin need not imply exact improvement — [COUNTEREXAMPLE]

**Claims:** E-FIRSTORDER-NOT-FINITE

Reported suite: 2,167/8,965 subgradient-rule-improving moves had strictly negative exact E gain; one example had margin 2.27 and exact change \(-0.240\).

## E5. Safe E screening and B&B — [PROJECT-PROVED]

**Claims:** E-BB-APPLIES, E-TANGENT-SCREENING

G2 gives a sound rejection rule. Exact post-move \(\lambda_{\min}\) evaluation can be reserved for screened-in candidates. Refinement B&B applies because \(\lambda_{\min}\) is Loewner-monotone.

## E6. Common-supergradient population geometry — [OPEN]

**Claims:** OPEN-E-COMMON-SUPERGRADIENT

It remains open whether every suitable population E optimum admits one common supergradient that supports all cell-assignment inequalities almost everywhere.

---
