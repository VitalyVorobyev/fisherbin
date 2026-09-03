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

## Closing report

Session S5 ran on 3 September 2026 on branch `consolidation-s5-manuscript-v9-draft` (worktree
`../scorequant-s5`), in two sittings: a setup sitting paused at the owner's request to save the
token window, and the drafting sitting (two fable writers in parallel, assembly and rendering
done inline by the orchestrator; no other subagents).

**Delivered.** `agenticresearch/manuscripts/score_space_quantization_article_v9.md` (1,335
lines, 17 sections plus References and Appendix A) and its rendered `.html`, produced by the new
tracked script `agenticresearch/py/render_manuscript.py` (python-markdown declared as an inline
script dependency, v8 stylesheet lifted verbatim, MathJax 3, generated contents sidebar). The
section order is the one recorded in the design section above: v8's sections 1–6 revised, new
sections 7 (bridge, DS11–DS15), 8 (margins, stable basins, off-class transfer, DS16–DS18), 9
(certified brackets, DS19), 11 (A-optimality) and 14.1 (information-efficiency outputs), and
v8's 7–13 revised as 10, 12–17. Labelled results share one counter, Proposition 1 to
Proposition 23; v8's Proposition 5 is now Proposition 23 and the new results are Lemma 5 to
Proposition 22. Equations are numbered per section; the v8→v9 map is (1)→3.1, (2)→3.2,
(3)→4.1, (4)→4.2, (5)→4.3, (6)→5.1, (7)→5.2, (8)→5.3, (9)→5.4, (10)→5.5, (11)→5.6, (12)→5.7,
(13)→5.8, (14)→6.1, (15)→6.2, (16)→6.3, (17)→6.4, (18)→6.5, (19)→6.6, (20)→10.1, (21)→10.2,
(22)→10.3, (23)→10.4, (24)→12.1, (25)→12.2, (26)→12.3. Every central statement carries a
`[novelty: <label>; ledger <row>]` tag copied from the ledger (117 tags, all 103 rows covered,
none deliberately omitted); Appendix A lists the v9 location of each row. The bibliography grew
from 22 to 75 entries, all named by the ledger's Attribution column. The four required
corrections: Theorem 3 (§5.2) now states merged atoms, exactly \(K\) nonempty cells, strictly
positive weights and zero-tolerance stability, with a warning box on
`CE-D-UNMERGED-DUPLICATES-001` and a note on the failed converse; the fig-02 caption and alt text
say Theorem 3; the §14 profiled \(D_s\) table row names `CE-DS-INTERVAL-SEED-UNSTABLE-001` and
routes compilation through the projected efficient-score rule, certificate-gated otherwise; §16.4
answers the \(D_s\) bridge question on conditionally centered scalar-nuisance laws and lists
OP29, OP30, OP31 and the E items as open, and §13 carries the same answer. The manuscripts README
gained a v9 ↔ v8 ↔ ledger crosswalk (the v8 crosswalk kept as historical), a rendering section,
and a reset staleness list; the companion packet is closed under `WORK/completed/`.

**Verified.** `uv run python agenticresearch/py/registry.py validate` → `registry clean`. The
assembler checked: every ledger row id in Appendix A exactly once (103), every placed row tagged
in the body, no placeholder, no unresolved `[@Key]` citation, no `$` math, no `data:` URI, zero
occurrences of "Theorem 6". Greps: `CE-D-UNMERGED-DUPLICATES-001` in §5.2 and §15;
`CE-DS-INTERVAL-SEED-UNSTABLE-001` in the §14 table row; `Proposition 23` in §13 and §16.4. The
render script was tested on a fixture with math, result boxes, tables, figures and citations
before rendering v9. This session touched no `src/`, `docs/` outside `docs/programme/` and
`docs/roadmap.md`, or `examples/`, so the library gate does not apply.

**Cut or left open.** Nothing from the packet was cut. Two bibliographic loose ends from the
writers are recorded in the companion packet (Haynsworth 1968 cited for DS15-4 without a ledger
key; Jakubowski 2021 volume details unverified). Section 7 runs about 2,100 words against the
1,200–1,800 target because it carries 18 ledger rows, eight labelled results and three witness
boxes with mandated hardened wording; nothing was trimmed to meet the target. The v9 draft has
had no independent read-through: the two writers verified their own outputs mechanically, and
the orchestrator spot-read the abstract, Theorem 3 and §16.4 only. The eight `apparently new`
tags rest on search gaps, as the ledger says; P8 decides them.

**The one thing the next session must know.** The `.html` is generated; edit only the `.md`
and rerun `uv run agenticresearch/py/render_manuscript.py <file>.md`. S9 (closure) should read
Appendix A and the README crosswalk, not the article body, to check that later findings reached
the manuscript; a new finding adds a ledger row, a v9 statement with its tag, and an Appendix A
line, in that order.
