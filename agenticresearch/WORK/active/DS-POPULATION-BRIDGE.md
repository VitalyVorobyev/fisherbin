# DS-POPULATION-BRIDGE — finite→population theory for profiled \(D_s\)

**Programme:** P1 (OPEN_PROBLEMS.md) · **Opened:** 28 Aug 2026 · **Status:** active
**Descends from:** research-plan-proposal.md Session 8 (reprioritized to "Now" by the product-first decision)

## Goal

Determine what statistical guarantee connects finite profiled-\(D_s\)
solutions (exchange-stable or global) to population efficient-score
quantizers: prove a bridge theorem under explicit regularity assumptions, or
reduce the question to precisely stated unresolved conditions.

## Why it matters

This is the single largest math-gated library feature. `result.py` hard-refuses
`compile_quantizer()` for profiled criteria because finite \(D_s\) optima can be
non-geometric (CE-DS-GLOBAL-GEOMETRY-001/-002); the open question is whether
the \(O(K/N)\) violation bound forces global finite profiled optima toward
population efficient-Voronoi solutions. A positive answer (even conditional)
gives the profiled criterion a compile bridge; a negative answer closes the
question and justifies the explicit-quantizer route permanently.

## Relevant claims

OPEN-DS-FINITE-POP-BRIDGE (target), OPEN-DS-POP-COMMON-METRIC,
DS-OKN-BOUND, DS-FINITE-GEOMETRY-FAILS, DS-GLOBAL-NONGEOMETRIC,
DS-GRADIENT-EFFICIENT-SEMIMETRIC, DS-EFFICIENT-SCORE-DOMINATION,
OPEN-DS-DOMINATION-EQUALITY, CONSISTENCY-RESTRICTED-AFFINE, D-POP-VORONOI.

## Known blockers

- The finite geometry fails exactly (two rational counterexamples); any bridge
  must be asymptotic or conditional, never finite-exact.
- Population \(D_s\) first-order geometry (OP5) is itself not fully rigorous;
  the packet may need to settle it first.
- Balancedness and minimum-cell-mass assumptions in DS-OKN-BOUND may not
  survive at optima; check before building on them.

## Recommended starting points

- The \(O(K/N)\) bound (DS-OKN-BOUND) + margin conditions, in the style of
  set-valued M-estimation.
- The restricted affine-max consistency proposition
  (CONSISTENCY-RESTRICTED-AFFINE) as the inductive-family half of a two-step
  bridge: unrestricted finite → near-geometric → restricted-class consistency.
- Falsification first (`protocols/numerical.md`): search for a sequence of
  growing-N exact instances whose global \(D_s\) optima stay boundedly
  non-geometric — that would kill the strongest form of the bridge early.

## Required deliverables

Registry patches for the touched OPEN-* nodes; any counterexample serialized
with fixtures + tests; a ledger row for any systematic search; audit per
`protocols/audit.md` if a bridge theorem is proved (it would be
publication-critical and library-load-bearing).

## Stop conditions

Bridge proved under explicit assumptions, disproved by a persistent-violation
construction, or reduced to a precise unresolved condition (e.g. a population
margin hypothesis) recorded as a new conjecture node.
