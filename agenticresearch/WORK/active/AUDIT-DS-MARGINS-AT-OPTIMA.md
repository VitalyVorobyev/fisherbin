# AUDIT-DS-MARGINS-AT-OPTIMA — publication-grade adversarial audit of DS15

**Programme:** P1 · **Opened:** 30 August 2026 · **Status:** active

## Goal

Independently verify, refute, or reduce `OPEN-DS-MARGINS-AT-OPTIMA` (DS15,
`KNOWN_RESULTS/05b-ds-bridge.md`): the margins dichotomy at exact global finite
\(D_s\) optima for conditionally centered laws. The auditor did not produce the
proof; the session follows `protocols/audit.md` (16-item output contract) with
its own counterexample search and its own prior-art search.

## Why it matters

DS15 resolves OP28 and redirects the profiled-criterion compile target to the
projected efficient-score interval rule — a guarantee the library is expected
to ship. It is the definition of load-bearing.

## Relevant claims

`OPEN-DS-MARGINS-AT-OPTIMA` (target), its recorded dependencies
(`DS-PROFILED-VARIATIONAL`, `OPEN-DS-DOMINATION-EQUALITY`,
`DS-GLOBAL-TIE-DEGENERACY`) and the unrecorded ones its proof uses
(`DS-EFFICIENT-SCORE-DOMINATION`, `DS-SCALAR-EFFICIENT-DP`,
`DS-FULL-PROFILE-K-LE-D-SINGULAR`, `OPEN-DS-FINITE-POP-BRIDGE`), plus
`OPEN-DS-MARGINS-NONCENTERED` (scope boundary).

## Known blockers

- Proposition 6 (achievability by steering) is a labeled proof sketch and the
  sole lower-bound mechanism; the research packet records two failed
  predecessor constructions.
- Conclusion (3) imports "the fixed-slab Glivenko–Cantelli class of audit §8",
  a step powered there by DS14's (M4)/(M5) margins, which DS15 does not assume.
- The theorem is stated on \(\mathbb R^{1+d_\lambda}\) with only \(K\ge3\);
  the rank ceiling makes every feasible labeling's profiled value exactly zero
  when \(K=d_\lambda+1\).
- The researcher's exact optima at \(N\ge14\) are float-screen-selected
  (top-64 labelings, `FLOAT_GUARD=1e-9`), exhaustively anchored only at
  \(N=12\).

## Recommended starting points

`python py/registry.py show OPEN-DS-MARGINS-AT-OPTIMA --deps --proof`;
`AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md` (contract exemplar);
`py/audit_ds_population_bridge.py` (independent-code-path style);
`LITERATURE/audits/OPEN-DS-MARGINS-AT-OPTIMA-29-August-2026.md` (the
researcher-side triangulation, to be redone independently).

## Required deliverables

`AUDITS/AUDIT-DS-MARGINS-AT-OPTIMA-001.md`; registry patch (audit pointer,
hardened assumptions, dependency repairs); boundary counterexample fixtures
with pinned tests; independent exact audit script + committed run artifacts;
independent literature audit with the protocol's six-field triangulation;
green library gate.

## Stop conditions

Verdict recorded as one of: verified with hardened assumptions; refuted with a
serialized counterexample; reduced to explicitly listed unresolved
assumptions — encoded in the claim node and the audit report.

## Next dependency-blocking question

Filled at close (required by `protocols/theorem.md`).
