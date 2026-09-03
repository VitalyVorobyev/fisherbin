# MANUSCRIPT-V9-RECONCILIATION — Novelty ledger for manuscript v9

**Programme:** P6 (D-CORE-COMPLETION; manuscript by-product) · **Opened:** 3 September 2026 · **Closed:** 3 September 2026 · **Status:** completed

Companion to the M12 programme packet `docs/programme/S02-manuscript-reconciliation.md`;
that packet owns the session mechanics, this one owns the scientific deliverable.

## Goal

Give every central statement of manuscript v8 (26 Aug 2026) and every registry finding proved
since v8 a novelty label (known / direct corollary / adaptation / apparently new / unresolved), an
attribution, and a `registry.py show <ID> --deps --proof` pointer, so that a v9 draft can be written
without re-deriving or re-attributing anything. Done is decidable: every v8 labelled result and
every in-scope claim id has a row in `manuscripts/NOVELTY_LEDGER.md`, and `registry.py validate`
is green.

## Why it matters

The manuscript is a by-product of the ledger, not a driver (`research-plan-proposal.md`). v8 is
behind the registry by eight `KNOWN_RESULTS` results (DS11–DS19 chain, A1–A4, I1–I3) and a dozen
fixtures, and it carries at least one attribution that an audit has already reversed (DS11's
core identity is classical). A v9 drafted from the ledger cannot repeat that.

## Relevant claims

- v8 crosswalk: GENERAL-FIRST-VARIATION, D-POP-VORONOI, D-LEVERAGE, D-EXCHANGE-IMPLIES-VORONOI,
  D-EXCHANGE-VIOLATION-LOWER-BOUND, D-FINITE-INDUCTIVE-CLOSURE, DS-OKN-BOUND,
  CONSISTENCY-RESTRICTED-AFFINE, plus the D/E/soft/oracle chapters v8 states without labels.
- DS11–DS15: DS-PROFILED-VARIATIONAL, DS-GLOBAL-TIE-DEGENERACY, OPEN-DS-DOMINATION-EQUALITY,
  DS-POP-WASTED-CELLS, OPEN-DS-POP-COMMON-METRIC, DS-EXCHANGE-LEVERAGE-BOUND,
  OPEN-DS-FINITE-POP-BRIDGE, OPEN-DS-MARGINS-AT-OPTIMA.
- DS16–DS19: DS-STABLE-MARGINS-PRICE, DS-STABLE-STATE-SELECTION, DS-PROFILED-COMPILE-CERTIFICATE,
  DS-STABLE-BASINS-*, DS-NONCENTERED-GLOBAL-BASIN-TRANSFER, DS-TILT-DUAL-*,
  DS-STRIP-DP-DELTA-CONSISTENCY, DS-MATRIX-TILT-NONQUASICONVEX, OPEN-DS-PRACTICAL-CERTIFIED-SOLVER.
- A1–A4: A-EXACT-MOVE-ORACLE, A-EXCHANGE-TERMINATES, A-FINITE-GEOMETRY-FAILS, A-TANGENT-SCREENING.
- I1–I3: INFO-D-EFFICIENCY, INFO-DS-EFFICIENCY, INFO-DIRECTIONAL-DIAGNOSTICS.
- Every `COUNTEREXAMPLES/CE-*.json` fixture (20 at opening).

## Known blockers

- No adversarial literature search happens in this session (that is P8); rows whose attribution
  is unchecked are labelled `unresolved` with a reason, never omitted.
- `literature_search_status: search_gap` is not a novelty proof; the ledger says "apparently new"
  and records the gap.
- The orchestrator never loads the v8 body; extraction runs in subagents from
  `manuscripts/README.md`, the registry dumps, and line-range excerpts.

## Recommended starting points

`manuscripts/README.md` (crosswalk and staleness list), `KNOWN_RESULTS/index.md` §14
(conservative novelty boundary), the four DS audits in `AUDITS/`, `LITERATURE/BIBLIOGRAPHY.md`.

## Required deliverables

- `manuscripts/NOVELTY_LEDGER.md` (new).
- `KNOWN_RESULTS/index.md` chapter table extended to DS16–DS19.
- This packet closed and moved to `WORK/completed/`.

## Stop conditions

Every v8 labelled result and every in-scope claim id has a ledger row, or the missing rows are
listed here with the reason they could not be labelled.

## Outcome

Delivered `manuscripts/NOVELTY_LEDGER.md` (103 rows: 42 v8 central statements incl. 7 labelled
results and 5 fixtures; 18 DS11–DS15; 30 DS16–DS19; 13 A1–A4/I1–I3). Every in-scope claim id and
every `COUNTEREXAMPLES/CE-*` fixture has a row; `KNOWN_RESULTS/index.md` lists DS16–DS19;
`registry.py validate` clean. Labels: known 20, direct corollary 34, adaptation 10, apparently new
8, unresolved 31. No `apparently new` row rests on more than a `search_gap`. Nothing was cut; the
adversarial literature search is P8 by design.

## Next dependency-blocking question

`D-EXCHANGE-IMPLIES-VORONOI` (Theorem 3, ledger row V8-11) is the paper's spine and its only
`search_gap` sits on the audit node, with pre-digital determinant-clustering literature
(Späth 1977/1985, between Friedman–Rubin 1967 and Telgarsky–Vattani 2010) unswept
(`LITERATURE/gaps.md`). P8 must answer: does Späth's exchange routine already contain the
centroid-coupled rank-two update (`D-RANK2-MOVE`) and the terminal Voronoi geometry? A "yes"
demotes V8-09 to `known` and V8-11 to `adaptation` before v9 is drafted.
