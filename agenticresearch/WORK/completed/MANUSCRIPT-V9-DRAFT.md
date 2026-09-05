# MANUSCRIPT-V9-DRAFT — Manuscript v9 from novelty ledger

**Programme:** P6 (D-CORE-COMPLETION; manuscript by-product) · **Opened:** 3 September 2026 · **Status:** completed 3 September 2026

## Goal

Draft manuscript v9 from the novelty ledger (agenticresearch/manuscripts/NOVELTY_LEDGER.md), folding in DS11–DS19, A1–A4, I1–I3 and the four required corrections (Theorem 3 hypotheses, fig-02 caption "Theorem 6", section 10 D_s table row contradicted by CE-DS-INTERVAL-SEED-UNSTABLE-001, section 12.4 open problem), and deliver v9 in both .md and .html formats. Done is decidable: every ledger row is either placed in the manuscript or marked deliberately omitted with reason, `registry.py validate` is green, and the README crosswalk and ledger placement appendix are complete.

## Why it matters

Manuscript v8 is behind the registry by eight `KNOWN_RESULTS` results (DS11–DS19 chain, A1–A4, I1–I3) and carries unaudited attributions. A v9 drafted from the ledger ensures all results are correctly attributed and all known corrections are incorporated. The resulting manuscript is a faithful record of what the registry proves, ready for publication.

## Relevant claims

From the novelty ledger (v8 and later rows):

**v8 central statements (42 rows):** GENERAL-FIRST-VARIATION, D-POP-VORONOI, D-LEVERAGE, D-EXCHANGE-IMPLIES-VORONOI, D-EXCHANGE-VIOLATION-LOWER-BOUND, D-FINITE-INDUCTIVE-CLOSURE, DS-OKN-BOUND, CONSISTENCY-RESTRICTED-AFFINE, plus the D/E/soft/oracle chapters v8 states without labels.

**DS11–DS15 (18 rows):** DS-PROFILED-VARIATIONAL, DS-GLOBAL-TIE-DEGENERACY, OPEN-DS-DOMINATION-EQUALITY, DS-POP-WASTED-CELLS, OPEN-DS-POP-COMMON-METRIC, DS-EXCHANGE-LEVERAGE-BOUND, OPEN-DS-FINITE-POP-BRIDGE, OPEN-DS-MARGINS-AT-OPTIMA.

**DS16–DS19 (30 rows):** DS-STABLE-MARGINS-PRICE, DS-STABLE-STATE-SELECTION, DS-PROFILED-COMPILE-CERTIFICATE, DS-STABLE-BASINS-*, DS-NONCENTERED-GLOBAL-BASIN-TRANSFER, DS-TILT-DUAL-*, DS-STRIP-DP-DELTA-CONSISTENCY, DS-MATRIX-TILT-NONQUASICONVEX, OPEN-DS-PRACTICAL-CERTIFIED-SOLVER.

**A1–A4 (4 rows):** A-EXACT-MOVE-ORACLE, A-EXCHANGE-TERMINATES, A-FINITE-GEOMETRY-FAILS, A-TANGENT-SCREENING.

**I1–I3 (3 rows):** INFO-D-EFFICIENCY, INFO-DS-EFFICIENCY, INFO-DIRECTIONAL-DIAGNOSTICS.

## Known blockers

- The four required corrections must be integrated: Theorem 3 hypotheses clarification, fig-02 caption "Theorem 6" audit, section 10 D_s table row validation against CE-DS-INTERVAL-SEED-UNSTABLE-001, section 12.4 open problem restatement.
- All 103 ledger rows must be accounted for in the final manuscript or listed as deliberately omitted with reason.
- Ledger rows marked `unresolved` do not block closure if their blocking reason is explicit.

## Recommended starting points

- `manuscripts/NOVELTY_LEDGER.md` (the authoritative row list with claim ids and novelty labels).
- `manuscripts/README.md` (numbering crosswalk, staleness list, figures convention).
- `manuscripts/score_space_quantization_article_v8.md` (source v8 to be updated).
- Registry dumps and `AUDITS/` results for DS11–DS19 validation.
- The four required corrections documented in the agenticresearch session notes.

## Required deliverables

- `manuscripts/score_space_quantization_article_v9.md` (updated manuscript with all corrections and new results).
- `manuscripts/score_space_quantization_article_v9.html` (rendered v9 in HTML format).
- `manuscripts/NOVELTY_LEDGER.md` update if row placement requires clarification.
- `manuscripts/README.md` v9 numbering crosswalk and deprecation note for v8.
- Appendix in v9 showing ledger row placement (which ledger row appears in which section/theorem).

## Stop conditions

- Every ledger row (103 total) is placed in the v9 manuscript or explicitly marked as deliberately omitted with reason documented.
- The four required corrections are integrated and validated.
- `registry.py validate` reports no errors.
- README crosswalk is current for v9.
- Ledger placement appendix is complete.

## Outcome

Manuscript v9 exists: `manuscripts/score_space_quantization_article_v9.md` (1,335 lines) and its
rendered `.html`, produced by the new `py/render_manuscript.py`. Every one of the 103 ledger rows
is placed (none deliberately omitted); Appendix A of the article lists the section per row and
117 inline novelty tags cover all 103 rows. Labelled results run Proposition 1 … Proposition 23
(v8's Proposition 5 is now Proposition 23); sections 7–9 (bridge, margins/basins/transfer,
certified brackets), 11 (A-optimality) and 14.1 (information-efficiency outputs) are new; the
four required corrections are in §5.2, §14 and §16.4 (with §13 carrying the same answer). The
bibliography grew from 22 to 75 entries, all named by the ledger's Attribution column.
`registry.py validate` is clean. The README crosswalk now maps v9 ↔ v8 ↔ ledger rows and the
staleness list is reset for v9.

## Revision (3 September 2026, same day)

The owner rejected the first draft as unreadable: 21,000 words in 17 flat sections, 23 results
in one counter at equal weight, provenance tags in most sentences, fixture ids as narrative
subjects. The manuscript was restructured on the same branch: a main text of §1–§10
(about 8,750 (9,000 by `wc -w` including markup) words after `## Abstract`; twelve numbered results, Proposition 1 … Theorem 12)
and Appendices A–H (score-law access; D auxiliaries; profiled \(D_s\) proofs and auxiliaries;
brackets; E and A; differentiable quantizers and consistency; fixture catalogue G1–G20; ledger
placement). Every ledger row is still placed (Appendix H, generated from the tags), the tags are
unchanged in the source and rendered as hidden provenance marks, and no `CE-*` id appears in
the main text. The renumbering (first draft → revision) is in the README crosswalk. The
revision spec for the M12 manuscript session (recorded in git history) records the design; its
closing report records what was verified and what remains open.

## Next dependency-blocking question

The P8 adversarial literature review: the eight `apparently new` rows and the 31 `unresolved`
rows are tagged in v9 exactly as the ledger labels them, so v9 cannot be submitted until P8
either confirms those labels or re-attributes them (the tags make every such statement
greppable). Two bibliographic loose ends from the writers: Haynsworth 1968 was cited for DS15-4
without a ledger key, and the Jakubowski 2021 volume details are unverified.
