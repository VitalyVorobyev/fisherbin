# DS-MARGINS-AT-OPTIMA — are the DS14 margins automatic at finite \(D_s\) optima?

**Programme:** P1 (OPEN_PROBLEMS.md OP28) · **Opened:** 28 Aug 2026 · **Status:** active
**Target claim:** `OPEN-DS-MARGINS-AT-OPTIMA`
**Descends from:** `WORK/completed/DS-POPULATION-BRIDGE.md` and
`WORK/completed/AUDIT-DS-POPULATION-BRIDGE.md`, which independently named this
as their next dependency-blocking question.

## Goal

Decide whether global (or exchange-stable) finite \(D_s\) optima under
light-tailed atomless laws asymptotically satisfy the three DS14 margins —
cell mass (M2), conditioning (M3), projected-centroid separation (M5) — almost
surely along the sequence. "Done" is decidable: a proof for a stated law class,
a counterexample law under which a margin fails infinitely often, or a
reduction to an explicitly stated conjecture node.

## Why it matters

DS14 is the project's headline \(D_s\) result and it is **conditional** on
assumptions the ledger explicitly records as *not* automatic. The audit's
verdict: this is *"the sole obstacle between the conditional bridge and an
unconditional compile guarantee for profiled criteria."* The library today
hard-refuses `compile_quantizer` for profiled criteria; a positive resolution
is what lifts that refusal with a theorem behind it, which is the largest
math-gated library feature in the queue.

It also comes before P2 for a mathematical reason, not just a queue reason:
`WORK/active/SCORE-ORACLE-ROBUSTNESS.md` records that any perturbation bound
"needs a boundary-margin condition, and margins are data-dependent". DS14's
(M4) slab margin is exactly such a condition. Settling margin behaviour here
makes P2 cheaper rather than later.

## Relevant claims

`OPEN-DS-MARGINS-AT-OPTIMA` (target), `OPEN-DS-FINITE-POP-BRIDGE` (DS14),
`DS-GLOBAL-TIE-DEGENERACY`, `DS-EXCHANGE-LEVERAGE-BOUND` (DS13),
`OPEN-DS-POP-COMMON-METRIC` (DS12), `DS-PROFILED-VARIATIONAL` (DS11),
`DS-OKN-BOUND` (DS6), `OPEN-DS-DOMINATION-EQUALITY`,
`OPEN-DS-E-UNRESTRICTED-CONSISTENCY` (C2, for the attainment sub-question).

Pull the branch with:

```bash
python py/registry.py show OPEN-DS-MARGINS-AT-OPTIMA --deps --proof
```

## Known blockers

- **The standing evidence points the wrong way.** Exact enumeration through
  \(N=18\) shows singleton cells persisting at global optima and a worst
  relative semimetric violation of 0.42 at \(N=10\), with no shrinkage yet
  (`N-DS-BRIDGE-TREND`); the independent audit scan reproduced a singleton at
  one of three exact \(N=10\) optima (`N-DS-AUDIT-MARGINS`). The
  \(\sim2\log N/N\) extreme-cell heuristic predicts the opposite for
  Gaussian tails. Either the heuristic is wrong or \(N\le18\) is pre-asymptotic;
  deciding which is the first real question.
- **(M5) provably fails somewhere.** `CE-DS-DEGENERATE-GLOBAL-TIE-001` is an
  exact global optimum with coincident projected centroids. So the honest target
  is not "(M5) always holds" but a characterization of the failure set, plus
  whether DS14's merged-rule variant is best possible there.
- **Two margins are about the optimizer, not the law.** (M2) and (M5) constrain
  the *solution sequence*; a law-level hypothesis alone cannot give them without
  an argument about what optima look like.

## Recommended starting points

Suggestions, not a decomposition — create whatever internal subproblems you need.

- Falsify before proving (`protocols/numerical.md`). `py/ds_population_bridge.py`
  already has the machinery: `trend` (exhaustive global optima vs \(N\), 5 laws,
  deterministic md5 seeds), `analyze`, `leverage`, and the degenerate-tie
  construction. Push \(N\) as far as exhaustive enumeration allows before
  believing either side of the heuristic; run it detached and report only the
  summary line plus the serialized artifact.
- The extreme-cell heuristic is a statement about the smallest cell of an
  optimal \(K\)-partition of a light-tailed sample. Attack it directly for
  \(d_\psi=1\) where the scalar DP gives exact ground truth.
- For (M5), the tie fixture suggests looking at symmetry: characterize the
  laws whose profiled geometry has an exact symmetry forcing coincident
  projected centroids, and check whether those are non-generic in a stateable
  sense.
- (M3) may be the easy one: conditioning is a full-information property and
  DS13 already needs no mass margin.

## Required deliverables

- Patch `claims/OPEN-DS-MARGINS-AT-OPTIMA.json` (and DS14's node if its
  conditionality changes), then `py/registry.py reindex` and `validate`.
- Any counterexample minimized and serialized to `COUNTEREXAMPLES/`, cited from
  its claim, and pinned in `tests/test_research_claims.py` if publication-critical.
- A `NUMERICAL_EVIDENCE.md` row for any new sweep, citing a claim id and an
  executable source.
- If DS14 becomes unconditional for a law class, say explicitly what the library
  may then compile and under which check — the deployability consequence is the
  point of the packet.
- Note the manuscript impact in `manuscripts/README.md` (completion item 7).

## Stop conditions

Proved for a stated law class; refuted by a law under which a margin fails
infinitely often; or reduced to explicitly listed unresolved assumptions
recorded as a conjecture node. A genuine scientific branch (for example, the
C2 attainment sub-question) becomes its own packet rather than expanding this one.

## Next dependency-blocking question

To be filled in when the packet closes.
