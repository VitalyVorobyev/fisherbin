# 3. Generic first-order and finite screening results

> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and
> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.
> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.

## G1. Infinitesimal cell-transfer identity — [PROJECT-PROVED/BRIDGE]

**Claims:** GENERAL-FIRST-VARIATION

Move infinitesimal probability mass \(d\varepsilon\) at score \(s\) from cell \(a\) to \(b\). Then

\[
\boxed{
dI_q=
[(s-\mu_a)(s-\mu_a)^\top-(s-\mu_b)(s-\mu_b)^\top]d\varepsilon.
}
\]

For differentiable \(F(I)\) with symmetric \(G=\nabla F(I)\),

\[
\boxed{
\frac{dF}{d\varepsilon}
=(s-\mu_a)^\top G(s-\mu_a)
-(s-\mu_b)^\top G(s-\mu_b).
}
\]

A shared \(G\) makes pairwise boundaries affine because the common \(s^\top Gs\) term cancels.

## G2. General concavity/supergradient screening — [PROJECT-PROVED]

**Claims:** D-TANGENT-SCREENING, DS-TANGENT-SCREENING, GENERAL-SUPERGRADIENT-SCREENING, GENERAL-WEIGHTED-TANGENT-STABILITY

For a concave criterion \(F\), let \(G\) be any supergradient at the current information matrix. For an exact finite relocation

\[
\Delta I=\alpha u_au_a^\top-\beta u_bu_b^\top,
\]

concavity gives

\[
\boxed{
\Delta F
\le
\operatorname{tr}(G\Delta I)
=
\alpha u_a^\top Gu_a-
\beta u_b^\top Gu_b.
}
\]

Therefore:

- if the weighted tangent gain is \(\le0\), the exact move cannot improve;
- weighted-tangent stability is a sufficient certificate of one-point exchange stability;
- expensive exact move evaluation can be restricted to screened-in candidates.

This applies to D, \(D_s\), A, and E (using a supergradient for E).

**Measured audit:** zero screening-direction violations in the reported randomized suites (including 4,886 D/A/\(D_s\) moves and the E suite).

---
