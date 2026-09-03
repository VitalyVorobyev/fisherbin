# S09 — Closure: independent v9 audit, exit gate, teardown

**Workstream:** all · **Needs:** S5, S8 · **Parallel with:** — · **Status:** queued

## Goal

Close the programme. Perform a fresh-context audit read of manuscript v9 against the novelty
ledger, following `agenticresearch/protocols/audit.md`'s independence requirement, and record a
verdict per statement; this read is publication-critical and is not optional, per the plan's own
risk note that attribution is publication-critical. Then verify all four workstream gates hold,
flip every session row in the M12 table to `done` or `cut`, retire the session prompt in
`docs/programme/README.md`, and consolidate the CHANGELOG for M11. Done means M12 reads `done` in
`docs/roadmap.md` and the full handoff gate plus `pnpm validate` are green on `main`.

## Inputs

- `docs/programme/README.md`: orchestrator contract; the session prompt this session retires.
- `docs/programme/S08-portal-user-path.md`: S8 closing report; confirms the portal gate.
- `docs/programme/S05-manuscript-v9-draft.md`: S5 closing report; confirms v9 exists and what it
  covers.
- `agenticresearch/manuscripts/score_space_quantization_article_v9.md`: the document being
  audited.
- `agenticresearch/manuscripts/NOVELTY_LEDGER.md`: the ledger the audit checks v9 against.
- `agenticresearch/protocols/audit.md`: the independence and verdict-per-statement procedure this
  session must follow.
- `docs/roadmap.md`: M12 table and exit gate; this session flips the table and evaluates the gate.
- `CHANGELOG.md`: consolidated for M11 at session end.
- `agenticresearch/py/registry.py`: `validate` for the final registry check.

Companion research packet: `agenticresearch/WORK/active/MANUSCRIPT-V9-AUDIT.md`. It does not exist
yet; this session drafts it from `agenticresearch/WORK/TEMPLATE.md` at session start. This
programme packet points at it and does not duplicate its content.

## Deliverables

- A fresh-context audit read of v9 against `NOVELTY_LEDGER.md`, per `protocols/audit.md`, with a
  verdict recorded per statement (confirmed, needs revision, or disputed, per the protocol's own
  vocabulary).
- `agenticresearch/WORK/completed/MANUSCRIPT-V9-AUDIT.md`: the closed companion packet, carrying
  the audit verdicts.
- `docs/roadmap.md`: M12 exit gate evaluated; every session row (S1-S9) flipped to `done` or
  `cut`; M12 status line changed to `done`.
- `docs/programme/README.md`: the copy-paste session prompt retired (marked no longer active, or
  removed per the session's judgment, with the reason recorded).
- `CHANGELOG.md`: consolidated entry for the M11 release, summarizing the programme's changes.

## Done criteria

- Every statement in v9 that the ledger tags has a recorded audit verdict.
- All four M12 workstream gates (W1-W4) hold, verified against their stated gate text in
  `docs/roadmap.md`, not assumed from session closing reports alone.
- Every session row S1-S9 in the M12 table reads `done` or `cut`.
- `docs/roadmap.md` M12 status line reads `done`.
- The full handoff gate, `pnpm validate`, and `python agenticresearch/py/registry.py validate` are
  all green on `main`.
- roadmap M12 table shows S09 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Perform the independent audit read of v9 against the ledger, verdict per statement | opus/fable, must not have drafted v9 in S5 | verdict table |
| Check every S1-S8 packet for a written closing report and its done criteria met | haiku | coverage checklist |
| Draft and close the companion audit packet | haiku | `WORK/completed/MANUSCRIPT-V9-AUDIT.md` |
| Run the full handoff gate, `pnpm validate`, and `registry.py validate` | haiku | gate output |
| Update `docs/roadmap.md` (session rows, M12 status, exit gate), retire the README session prompt, consolidate CHANGELOG | orchestrator | roadmap, README, CHANGELOG diff |

## Verification

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
cd website && pnpm validate
python agenticresearch/py/registry.py validate
```

## Open decisions

- How to guarantee the audit reader is genuinely independent of the S5 drafting session (a new
  session with no shared context is the plan's intent; the exact mechanism, e.g. a fresh Claude
  Code session with no memory of S5, is left to whoever runs S9).
- Whether any session row ends up `cut` rather than `done` (for example if S7's HEP path was
  unreachable and only the fallback shipped, that is still `done`, not `cut`; `cut` is reserved
  for a session whose deliverable was dropped entirely). The plan does not name a `cut` candidate,
  so this session should not manufacture one.

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
