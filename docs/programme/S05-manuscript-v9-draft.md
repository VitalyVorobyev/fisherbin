# S05 — Manuscript v9 draft

**Workstream:** W1 · **Needs:** S2 · **Parallel with:** S4 · **Status:** queued

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

Companion research packet: `agenticresearch/WORK/active/MANUSCRIPT-V9-DRAFT.md`. It does not exist
yet; this session drafts it from `agenticresearch/WORK/TEMPLATE.md` at session start. This
programme packet points at it and does not duplicate its content.

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

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
