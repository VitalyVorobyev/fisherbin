# S05 — Manuscript v9 draft

**Workstream:** W1 · **Needs:** S2 · **Parallel with:** S4 · **Status:** done

## Goal

Write manuscript v9 from the novelty ledger, folding in every finding since v8 and fixing every
item on the v8 staleness list: Theorem 3's hypotheses, the fig-02 caption that still says
"Theorem 6", the section 10 D_s table row (contradicted by
`CE-DS-INTERVAL-SEED-UNSTABLE-001`), and the open problem in section 12.4. Done means every row in
`NOVELTY_LEDGER.md` is placed in v9 or explicitly marked "deliberately omitted" with a reason, and
`registry.py validate` passes; this session does not decide novelty or attribution, S2 already
did.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S02-manuscript-reconciliation.md`: S2 closing report; the ledger this session
  drafts from.
- `agenticresearch/manuscripts/NOVELTY_LEDGER.md`: the row-by-row source of truth for what goes
  into v9 and how it is labelled.
- `agenticresearch/manuscripts/score_space_quantization_article_v8.md`: the document being
  revised; subagents work section by section, the orchestrator never opens the whole body.
- `agenticresearch/manuscripts/README.md`: numbering crosswalk and figures convention (figures by
  path, never inlined as `data:` URIs).
- `agenticresearch/KNOWN_RESULTS/index.md`: DS16-DS19 entries this draft must fold in.
- `agenticresearch/py/registry.py`: `show <ID> --deps --proof` per-claim evidence for each writer.
- `agenticresearch/WORK/TEMPLATE.md`: section shape for the companion research packet.

Companion research packet: `agenticresearch/WORK/completed/MANUSCRIPT-V9-DRAFT.md` (drafted from
`agenticresearch/WORK/TEMPLATE.md` at session start, closed at session end). This programme packet
points at it and does not duplicate its content.

## Deliverables

- `agenticresearch/manuscripts/score_space_quantization_article_v9.md` and the regenerated
  `.html` sibling, figures referenced by path per the README's `data:` URI ban.
- `agenticresearch/manuscripts/README.md`: numbering crosswalk extended to v9; staleness list
  reset (empty, or listing only genuinely new staleness).
- `agenticresearch/WORK/completed/MANUSCRIPT-V9-DRAFT.md`: the closed companion packet.
- Required edits, from the plan: Theorem 3 hypotheses corrected; fig-02 caption corrected; section
  10 D_s table row corrected; section 12.4 open problem answered.
- New sections: the population bridge (attributed per the ledger's DS11 note); the margins
  dichotomy (scoped to scalar-nuisance, stated with its `O~` rate); the off-(L) transfer result;
  the certified bracket, stated as "not generically exact"; A-optimality; information-efficiency
  outputs.
- Every central statement in v9 tagged with its ledger novelty label.

## Done criteria

- Every row in `agenticresearch/manuscripts/NOVELTY_LEDGER.md` is placed in v9 or marked
  "deliberately omitted" with a stated reason.
- `python agenticresearch/py/registry.py validate` is green.
- The four required corrections (Theorem 3, fig-02 caption, section 10 row, section 12.4) are each
  verifiable by grep or by reading the specific paragraph, not by trusting the writer.
- `agenticresearch/manuscripts/README.md` crosswalk includes v9 and its staleness list no longer
  names any of the four corrected items.
- roadmap M12 table shows S05 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Write each new section (population bridge, margins dichotomy, off-(L) transfer, certified bracket, A-optimality, information-efficiency) | fable, one writer per section | section drafts, each writer given only its ledger rows and registry dumps, never researcher derivation prose |
| Apply the four required corrections (Theorem 3, fig-02, section 10, section 12.4) | fable | corrected paragraphs |
| Assemble sections into the full v9 document, regenerate the `.html`, update the crosswalk | haiku | `article_v9.md`, `.html`, updated README |
| Draft and close the companion research packet | haiku | `WORK/completed/MANUSCRIPT-V9-DRAFT.md` |
| Run `registry.py validate`, check every ledger row is placed or marked omitted | haiku | validation output and coverage check |

## Verification

```bash
python agenticresearch/py/registry.py validate
```

This session does not touch `src/`, `docs/`, or `examples/`, so the library/docs handoff gate
does not apply.

## Open decisions

- Section ordering: the plan lists the new sections but not their position relative to the
  existing v8 structure; the session decides and records the placement.
- Whether the `.html` regeneration is a tracked script in the repo or a manual step this session
  performs once; if no such script exists yet, the session must say so and either add one or
  document the manual procedure in the closing report.

## Design decisions (written 3 September 2026, before drafting)

**Section order.** v9 keeps the v8 skeleton for sections 1–6 and appends the new material as
top-level sections placed where the argument needs them, so the profiled-\(D_s\) story is told
in one run before E-optimality. Numbering of v9 (v8 number in brackets):

| v9 | Title | Source |
|---|---|---|
| 1–6 | unchanged titles [1–6] | v8 revised from ledger section 1 rows; four required corrections |
| 7 | Profiled \(D_s\): the finite-to-population bridge | new; ledger DS11–DS15 rows |
| 8 | Margins, stable basins, and transfer under a scalar nuisance | new; 8.1–8.2 ledger DS16–DS17 rows (margins dichotomy, scalar-nuisance scope, \(\tilde O\) rate), 8.3 DS18 rows (off-\(L\) transfer) |
| 9 | Certified brackets for profiled \(D_s\) | new; ledger DS19 rows; stated as "not generically exact" |
| 10 | E-optimality [7] | v8 revised |
| 11 | A-optimality | new; ledger A1–A4 rows |
| 12 | Direct geometric and differentiable quantizer optimization [8] | v8 revised |
| 13 | From finite training to population quantization [9] | v8 revised |
| 14 | Computational formulations and reference implementation [10] | v8 revised; section 10 \(D_s\) table row corrected; new 14.x "Information-efficiency outputs" from ledger I1–I3 rows |
| 15 | Numerical verification and falsification [11] | v8 revised |
| 16 | Discussion [12] | v8 revised; 16.4 open problem answered |
| 17 | Conclusion [13] | v8 revised |
| App. A | Ledger placement | new; one row per `NOVELTY_LEDGER.md` row |

Labelled results are renumbered consecutively in v9 (Proposition, Lemma, Theorem share one
counter as in v8); the README crosswalk records v8 → v9 numbers.

**Novelty tags.** Every central statement (each labelled result, each abstract/contribution
claim that has a ledger row) carries an inline tag immediately after its statement, in the form
`[novelty: <label>; ledger <Row id>]`, e.g. `[novelty: apparently new; ledger V8-11]`. Labels
are the ledger's five words and are copied, never re-decided. Attribution text comes from the
ledger's Attribution column; a `known` or `direct corollary` tag must be accompanied by the
citation the ledger names.

**Placement appendix.** Appendix A of v9 is a table `| Ledger row | v9 location | Note |` with
one line per ledger row (103). Location is a section number or the literal `deliberately
omitted`, in which case Note states the reason. The coverage check greps this appendix against
`NOVELTY_LEDGER.md` row ids.

**Writers.** One fable writer per new section (7, 8.1–8.2, 8.3, 9, 11, 14.x) receives only its
ledger rows, the registry dumps of the claim ids in those rows, the v8 section it must match in
style (section 6), and the tag convention. One fable writer revises v8 sections 1–6, 10, 12–17
from ledger section 1 and applies the four required corrections. A haiku assembler concatenates,
numbers, builds Appendix A, regenerates the HTML, and updates the README crosswalk.

**HTML.** `v8.html` was hand-built (custom CSS, MathJax 3 from CDN, no generator tag); pandoc
is not installed, python `markdown` 3.10 is available in the environment. Decision: when
drafting resumes, add a small tracked script `agenticresearch/py/render_manuscript.py` (python
`markdown` + the v8 stylesheet lifted verbatim from `v8.html`) so the `.html` sibling is
reproducible; record it in the manuscripts README.

**Pause (3 September 2026).** The owner held S5 at the setup stage to conserve the session
budget. Done so far on branch `consolidation-s5-manuscript-v9-draft`: roadmap row `active`,
this design section, the companion packet (then under `WORK/active/`, Outcome unfilled). No v9 text exists yet. Resume by running the two writers named above
(new sections; v8 revision with the four corrections) and then the inline assembly; the v8
section splits and per-ledger-section row files must be regenerated in scratch (they lived in
a session-local scratchpad).

## Revision spec (written 3 September 2026, after the owner rejected the first draft)

The first v9 draft (21,000 words, 17 sections, 23 results in one counter, 93 inline tags, 20 raw
fixture ids in prose) was rejected as unreadable: significant and minor results carried equal
weight in one long technical text. This spec supersedes the section order and result numbering
in "Design decisions" above; the tag convention and the placement appendix survive with the
changes stated here. The manuscript keeps the name v9: nothing had merged.

**Shape.** A main text of at most 9,000 words (Abstract through §10, references excluded) that a
reader can follow without the appendices, and eight appendices holding every auxiliary result,
proof, fixture and interface detail, each reachable from a pointer in the main text.

| Main § | Title | Built from first draft |
|---|---|---|
| Abstract | ≤ 250 words, no tags, no citations, no fixture ids | Abstract |
| 1 | Introduction | §1, §3.3 (the three-problem distinction is the organizing idea; five contributions; paper map) |
| 2 | Prior work | §2.1–2.4 rewritten as one review of 900–1,200 words by theme; `known` rows cited, never claimed |
| 3 | Setting | §3.1, §3.2, §3.7, §4, criterion definitions from §5, §6.1, §10, §11 lead-ins; one paragraph on score-law access pointing to Appendix A |
| 4 | D-optimality: exchange stability closes the bridge | §5.1–5.3; Theorem 2 with proof sketch; fig-02 to fig-06 |
| 5 | Profiled \(D_s\): the bridge fails, then what survives | §6.2, §6.3, §7.1 (statement of the variational form only), §7.2–7.4, §7.5 (Theorem 8 only), §8.1 (Theorem 9), §8.2 (Theorem 10), §8.3 (Theorem 11) |
| 6 | Certified brackets | §9.1, §9.2 as a remark, §9.5 |
| 7 | Other criteria and learned quantizers | §6.4, §10, §11, §12 in ≤ 700 words with pointers |
| 8 | Implementation and verification | §14, §15 in ≤ 500 words with pointers |
| 9 | Discussion and open problems | §16; open problems ≤ 400 words |
| 10 | Conclusion | §17, ≤ 200 words |

| Appendix | Title | Built from first draft |
|---|---|---|
| A | Computational access to the score law | §3.4–3.6, §14 interface catalogue, §14.1 |
| B | D-optimality: auxiliary results | Lemma B.1 (first-draft Lemma 2), exact enumeration and hit-rate details, boundary fixtures for Theorem 2 |
| C | Profiled \(D_s\): proofs and auxiliary results | proofs of Theorems 5–11; Propositions C.1–C.3, Lemma C.4, Proposition C.5; tie-witness, wasted-cells, rank-vacuity, sign-split and singular-destination remarks |
| D | Certified brackets: consistency and complexity | §9.3, §9.4 |
| E | E- and A-optimality | §10.1–10.2, §11 |
| F | Differentiable quantizers and consistency | §12.1–12.4 details, §13 |
| G | Fixture catalogue | table: fixture, what it witnesses, registry claim id, where cited; absorbs the §15 table |
| H | Ledger placement | the placement table with every location rewritten |

**Result numbering.** Main-text results share one counter; appendix results are lettered.
First draft → revision: Prop 1 → Prop 1; Lemma 2 → Lemma B.1; Thm 3 → Thm 2; Prop 4 → Prop 3;
Lemma 5 → Lemma 4; Prop 6 → Prop C.1; Thm 7 → Thm 5; Prop 8 → Prop 6; Thm 9 → Thm 7;
Thm 10 → Thm 8; Prop 11 → Prop C.2; Prop 12 → Prop C.3; Thm 13 → Thm 9; Lemma 14 → Lemma C.4;
Thm 15 → Thm 10; Prop 16 → Prop C.5; Thm 17 → Thm 11; Thm 18 → Thm 12; Prop 19 → Prop D.1;
Prop 20 → Prop D.2; Prop 21 → Prop E.1; Prop 22 → Prop E.2; Prop 23 → Prop F.1. Equations are
numbered per section or appendix and only when referenced; appendices restate any main-text
equation they need under their own number.

**Fixtures.** The main text never prints a `CE-*` id. Fixtures are cited as "fixture G\(n\)" with
the fixed numbering G1 `CE-D-LLOYD-001`, G2 `CE-D-VORONOI-CONVERSE-001`,
G3 `CE-D-UNMERGED-DUPLICATES-001`, G4 `CE-DS-GLOBAL-GEOMETRY-001`, G5 `CE-DS-GLOBAL-GEOMETRY-002`,
G6 `CE-DS-DEGENERATE-GLOBAL-TIE-001`, G7 `CE-DS-POP-WASTED-CELLS-001`,
G8 `CE-DS-MARGINS-RANK-VACUITY-001`, G9 `CE-DS-STABLE-MARGIN-RETAINING-001`,
G10 `CE-DS-INTERVAL-SEED-UNSTABLE-001`, G11 `CE-DS-LCM-SIGNSPLIT-MARGIN-001`,
G12 `CE-DS-LCM-SIGNSPLIT-MINIMAL-001`, G13 `CE-DS-NONCENTERED-POPULATION-CUT-UNSTABLE-001`,
G14 `CE-DS-NONCENTERED-SINGULAR-DESTINATION-001`, G15 `CE-DS-TILT-DUAL-GAP-001`,
G16 `CE-DS-TILT-DUAL-GAP-002`, G17 `CE-DS-TILT-DUAL-TIE-MASK-001`,
G18 `CE-DS-MATRIX-TILT-NONQUASICONVEX-001`, G19 `CE-E-GEOMETRY-001`, G20 `CE-A-DSTYLE-001`.

**Novelty tags.** Unchanged in the source (S9 audits per tagged statement), moved with their
sentences; a dropped passage hands its tag to the surviving statement of the same claim; the
abstract carries none. The renderer shows them as superscript provenance marks hidden behind a
"Show provenance" toggle, so the default view is clean prose. Result boxes use the class of
their environment (`theorem`, `proposition`, `lemma`, `remark`, `warning`); main-text remarks are
limited to what the reader needs.

**Writers.** Two fable writers in parallel from the first draft split by section: M writes the
main text, X writes Appendices A–G; the orchestrator assembles, regenerates Appendix H from the
tags, rewrites the README crosswalk, changes the renderer, and runs one fable reader on the
rendered main text alone before closing. Acceptance is the owner reading the main text.

## Closing report

Session S5 ran on 3 September 2026 on branch `consolidation-s5-manuscript-v9-draft` (worktree
`../scorequant-s5`, PR #37), in three sittings: a setup sitting paused at the owner's request,
a drafting sitting that produced a 21,000-word first draft the owner rejected as unreadable, and
a restructuring sitting that produced the manuscript described here. The first draft and its
design are recorded above under "Design decisions"; the revision spec above supersedes them.

**Delivered.** `agenticresearch/manuscripts/score_space_quantization_article_v9.md` and its
rendered `.html`, now a focused main text plus appendices. The main text (Abstract, §1
Introduction, §2 Prior work, §3 Setting, §4 D-optimality, §5 Profiled \(D_s\), §6 Certified
brackets, §7 Other criteria and learned quantizers, §8 Implementation and verification, §9
Discussion and open problems, §10 Conclusion) runs about 8,750 (9,000 by `wc -w` including markup) words after the abstract and
carries twelve numbered results in one counter: Proposition 1, Theorem 2 (the D exchange
theorem), Proposition 3, Lemma 4, Theorem 5, Proposition 6, Theorems 7–11 (the profiled
\(D_s\) arc: conditional bridge, dichotomy, margin price, centering obstruction, off-class
transfer) and Theorem 12 (brackets). Appendices A–G hold the score-law access material, the D
auxiliaries, the \(D_s\) proofs and auxiliary results (Propositions C.1–C.3, Lemma C.4,
Proposition C.5), the bracket consistency and complexity results, E- and A-optimality,
differentiable quantizers and consistency, and a fixture catalogue G1–G20 that absorbs the
verification table; Appendix H places every ledger row and is generated by the assembler from
the tags. The main text never prints a fixture or registry id. The renderer
(`agenticresearch/py/render_manuscript.py`) now shows novelty tags as superscript provenance
marks hidden behind a sidebar "Show provenance" button, lists appendices under their own
sidebar divider, and styles `lemma` and `remark` boxes. The manuscripts README crosswalk maps
v9 ↔ v8 ↔ first draft ↔ location ↔ ledger row for all 23 results; its staleness list names
the two bibliographic loose ends and the missing human read-through. The companion packet
under `WORK/completed/` carries a revision note. The four required corrections survive:
Theorem 2 states merged distinct atoms, exactly \(K\) nonempty cells and zero tolerance with a
remark on fixture G3; the fig-02 caption cites Theorem 2; §8 says the profiled \(D_s\) route
ships no compiled rule because the interval seed is not exchange-stable (fixture G10); §9
answers the \(D_s\) bridge question through Theorem 8 and leaves OP29–OP31 and the E items
open.

**Verified.** `uv run python agenticresearch/py/registry.py validate` → clean. The assembler
(scratch, not tracked) checked on the final document: all 103 ledger row ids tagged in the body
and each with one label; Appendix H has one row per id; the abstract carries no tags; the
twelve main and eleven appendix result labels are each defined exactly once and every
reference to a result, appendix subsection, section number or fixture number resolves; zero
`CE-` strings in the main text and all twenty fixture ids in Appendix G; zero `$` math, `data:`
URIs, placeholders or "Theorem 6"; every figure path exists; Theorem 2's hardened wording and
the G10 pointer present. Ruff check and format clean on the renderer. One opus reader with fresh context read the rendered main text alone and reported: the central quantity \(v_K\) was named in §5.2 but defined only in §5.6, five dual symbols in §6 arrived without motivation and the dual value \(d\) collided with the dimension letter, six process sentences of the form "An audit …" survived from the ledger notes, equation (5.6) was missing, the off-class law used \(\Phi_{D_s}\) for a raw Schur-complement value, one sentence in §5.9 had lost its subject, §8 restated the fixtures of §4–§7, and \(E_\lambda\), "regular", the between-value and the bare \(\Phi(q)\) were used before definition. All of these were fixed inline (definitions added in §3.3, §5.2, §5.6 and §6; audit sentences reworded as re-derivation statements with their tags kept; equations renumbered; \(\Phi_s\) on the scalar law; §8 shortened) and the checks rerun. Not acted on: the reader's suggestion to demote Propositions 1 and 3 from boxes to inline remarks (they are ledger-tagged results in the crosswalk and stay boxed), the density of §2's citation strings, and one-sentence motivations for Theorems 9 and 12 beyond what §5.7 and the §6 preamble now carry. This session
touched no `src/`, `docs/` outside `docs/programme/`, `docs/roadmap.md` and `CLAUDE.md`, or
`examples/`, so the library gate does not apply.

**Cut or left open.** The first draft's section structure and single result counter were
discarded, not kept as an alternative. The owner's reading of the rendered main text is the
acceptance step; it has not happened at the time of writing. The eight `apparently new` tags
still rest on search gaps and P8 decides them. Haynsworth 1968 (DS15-4) has no ledger key and
the Jakubowski 2021 volume is unverified. Agent budget: the two fable writers of the
restructuring sitting hit the owner's session limit as they finished, after which the owner
ruled out fable subagents for good (`CLAUDE.md`, programme README); the trim and the
read-through ran on opus.

**The one thing the next session must know.** Edit only the `.md` and rerun
`uv run agenticresearch/py/render_manuscript.py <file>.md`; the `.html` is generated. A new
finding adds a ledger row, a statement with its tag in the main text or the right appendix, and
a line in Appendix H (regenerated from the tags, so the tag is what matters). S9 should read
Appendix H, Appendix G and the README crosswalk, not the article body. Never spawn fable
subagents in this project.
