# SCORE-ORACLE-ROBUSTNESS — perturbation theory for estimated scores

**Programme:** P2 (OPEN_PROBLEMS.md) · **Opened:** 28 Aug 2026 · **Status:** active
**Descends from:** research-plan-proposal.md Session 10 (reprioritized to "Now" by the product-first decision)

## Goal

Bound the error induced in cell moments, \(I_q\), the D/\(D_s\) objective,
efficiency, and geometric boundaries when the score oracle is an estimate
\(\hat s\) with stated error (\(\|\hat s-s\|_{L^2}\le\varepsilon\) or
stronger); identify conditions under which the reported surrogate is
conservative.

## Why it matters

Every real dataset (FlowCyt, HEP classifier-derived scores) hits this gap; the
library book calls it "the largest practical gap in the framework." Even a
one-model result with explicit constants upgrades the empirical error ladder
from suggestive measurement to an instance of a theorem, and yields an honest
error-bar story for shipped retention numbers.

## Relevant claims

OPEN-SCORE-PERTURBATION (target), OPEN-CLASSIFIER-CALIBRATION-FI,
OPEN-REPRESENTATION-LOSS-ESTIMATION, PROXY-TRUE-RETAINED-FI,
REPRESENTATION-QUANTIZATION-LOSS, RATIO-LOCAL-SCORE,
CLASSIFIER-MIXTURE-SCORE-FORMULA, FI-LOSS-DECOMPOSITION.

## Known blockers

- Hard assignment makes every functional non-smooth at cell boundaries; any
  bound needs a boundary-margin condition, and margins are data-dependent.
- The claim must keep representation loss (score estimation) and quantization
  loss separated — the levels are distinct in the registry and in the library.

## Recommended starting points

- Matrix perturbation of the log-det objective composed with stability of
  D-optimal Voronoi boundaries under score perturbation, composed with known
  classifier excess-risk → ratio-error rates.
- The empirical infrastructure (error ladder, closure report, analytic
  laboratory in the library docs) already exists to falsify candidate bounds
  cheaply — use it before polishing constants.
- A one-dimensional exactly solvable model first; the scalar DP solver gives
  ground truth.

## Required deliverables

Registry patches; any counterexample fixtures; a ledger row linking the bound
to a falsification sweep; proposed diagnostic surface for the library (what a
user-facing error bar would report) recorded in the packet, not implemented.

## Stop conditions

A perturbation bound with explicit constants for at least one model class,
a counterexample showing no such bound holds without a margin condition, or
reduction to a stated conjecture node.
