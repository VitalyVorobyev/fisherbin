# 9. Empirical-to-population theory

> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and
> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.
> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.

## C1. Restricted affine-class consistency — [PROJECT-PROVED / STANDARD EMPIRICAL-PROCESS ROUTE]

**Claims:** CONSISTENCY-RESTRICTED-AFFINE

Let \(\mathcal Q\) be a compact parameterized class of \(K\)-cell affine-max quantizers. Assume bounded scores or suitable uniform integrability, cell masses uniformly bounded below, and the required information matrices uniformly bounded away from singularity.

Then empirical \(W_b\) and \(m_b\) converge uniformly over \(\mathcal Q\). Consequently D, regular \(D_s\), and E objective values converge uniformly on that regular subset. Approximate empirical maximizers are value-consistent; with an isolated population optimum, standard argmax theory gives parameter/decision consistency up to label permutations.

The proof uses finite capacity of multiclass affine decision regions + ULLN + continuity.

## C2. Unrestricted/global consistency — [OPEN]

Still open in the desired generality:

- unrestricted empirical global D optimum \(\to\) population global optimum;
- exchange-stable D solution set \(\to\) population stationary set;
- unrestricted finite \(D_s\)/E optima \(\to\) deployable population geometric optima.

For D, finite geometric realizability makes this program unusually plausible; for \(D_s\)/E the finite non-geometric counterexamples prevent the same direct reduction.

---
