# Consolidation programme (M12) — orchestrator contract

This directory is the standing memory of the M12 consolidation programme. It exists so that a
session started in any harness (Codex, Claude Code, or a person) can pick up the programme cold,
do one session's work, and leave the next session the same footing. Status lives in one place
only: the M12 table in `docs/roadmap.md`. This file explains how to run a session; the packets
`S01`–`S09` say what each session delivers.

## Scope

Four workstreams, gated in `docs/roadmap.md` under "M12 — Consolidation programme":

- **W1 — Manuscript v9.** Novelty ledger, then a full synthesis folding in every finding since
  v8. Not yet submission-formatted.
- **W2 — Library design pass.** Public-surface truth (S1), then internals (S3): error hierarchy,
  one fit pipeline, single-sourced validation, results constructed once. Breaking changes are
  allowed pre-1.0 and are recorded in an ADR and the CHANGELOG.
- **W3 — Portal.** The portal is the public face; MkDocs stays the exhaustive reference.
  Narrative duplicated between the two moves out of MkDocs. The research section is rewritten in
  plain English from the ledger.
- **W4 — Showcases.** One realistic end-to-end example per input route. HEP data: FAIR Universe
  HiggsML Uncertainty Challenge first, verified by actually fetching it, with a defined fallback.

Dependency spine: the public API is frozen (S3) before anything quotes it (S4, S6, S8); the
novelty ledger (S2) is written before anything narrates research (S5, S6). The `Needs` column of
the roadmap table is the merge lock.

## Orchestrator invariants

The session's orchestrator is a lean coordinator, not a reader of the codebase.

1. **Standing reads are three files:** this README, the session packet, and the previous
   session's packet (for its closing report). Everything else is delegated or read as a named
   excerpt.
2. **Never open** a manuscript body (`agenticresearch/manuscripts/*.md`, `*.html`) or a claim file
   (`agenticresearch/claims/*.json`) in the orchestrator context. Research packets delegate those
   reads and receive registry dumps (`python agenticresearch/py/registry.py show <ID> --deps
   --proof`) or one-section extracts.
3. **Delegate every wide read**: inventories, greps, whole-module reads, running gates. The
   orchestrator reads specs, diff summaries, and closing reports.
4. **Design decisions are written down before code.** A strong agent writes the spec into the
   packet (or a scratch file named in the packet); implementation agents work from that spec.
5. **One branch, one PR, one closing report.** Branch `consolidation-s<N>-<slug>`; do not commit
   or push without the owner's go-ahead unless the packet says otherwise.
6. **Status changes happen in `docs/roadmap.md` only** (`queued | active | done | cut`). Flip the
   row to `active` at session start and to `done` only after the packet's done criteria are met
   and the closing report is written.
7. **Close with a plain-English report** in the packet's "Closing report" section: what was
   delivered, what was verified (commands and results), what was cut or left open, and the one
   thing the next session must know. This report is the memory the next session reads.

## Delegation ladder

Pick the model tier by task complexity, not by file count.

| Tier | Use for |
|---|---|
| haiku | inventories, greps, file:line lists, running gates and reporting failures verbatim, index regeneration, materializing files from a written spec |
| sonnet | implementing a written spec (module refactors, tests, TSX against a spec, notebooks), executing examples, wiring Docusaurus |
| opus / fable | API and refactor design decisions, statistical design of examples, novelty labelling, manuscript prose, portal research narrative, independent audits |

Independent tasks run in parallel. An agent that must edit the same file as another waits.

## Research sessions

S2, S5 and S9 are research sessions. The `agenticresearch/` workspace is self-governing
(`protocols/theorem.md` item 7, `protocols/audit.md` independence, `py/registry.py validate`), so
each of these sessions also opens a packet `agenticresearch/WORK/active/MANUSCRIPT-V9-*.md` from
`agenticresearch/WORK/TEMPLATE.md`. The programme packet points at it and duplicates nothing.

## Verification

Any session touching `src/`, `docs/` or `examples/` runs the full handoff gate from
`docs/roadmap.md`:

```bash
uv run ruff check . && uv run ruff format --check . && uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build && uv run mkdocs build --strict
```

Portal sessions add `cd website && pnpm validate`. Research sessions add
`python agenticresearch/py/registry.py validate`. A gate is reported verbatim: green, or the
failing command and its output.

## Session prompt

Start a fresh session in the repo root and paste, filling `<N>` and `<slug>` from the roadmap
table and the packet file name:

```text
You are running ScoreQuant consolidation session S<N> (programme M12).

Read docs/programme/README.md, then docs/programme/S0<N>-<slug>.md, then the
closing report of the previous session's packet. Read nothing else directly:
delegate every inventory, module read and gate run to subagents at the tier
the README's delegation ladder names, and work from their summaries.

Rules of engagement:
- Work on branch consolidation-s<N>-<slug>. Do not commit or push without the
  owner's go-ahead.
- Flip the S<N> row in docs/roadmap.md to `active` first.
- Write design decisions into the packet before any code is written.
- Never open agenticresearch/manuscripts/* bodies or agenticresearch/claims/*.json
  in your own context.
- Before finishing: every done criterion in the packet is checked, the
  verification commands in the packet are green (report failures verbatim),
  the roadmap row reads `done`, and the packet's Closing report is written in
  plain English for a reader who did not watch the session.
- End with the closing report and the one thing the next session must know.
```

## Files

| File | Session |
|---|---|
| `S01-scaffold-and-public-surface.md` | Scaffold + public-surface truth pass |
| `S02-manuscript-reconciliation.md` | Manuscript reconciliation + novelty ledger |
| `S03-library-internals-refactor.md` | Library internals refactor |
| `S04-showcase-foundations.md` | Showcase foundations |
| `S05-manuscript-v9-draft.md` | Manuscript v9 draft |
| `S06-portal-ia-and-research-narrative.md` | Portal information-architecture cut + research narrative |
| `S07-hep-classifier-showcase.md` | HEP classifier showcase |
| `S08-portal-user-path.md` | Portal user path + e2e in CI + deployment |
| `S09-closure.md` | Closure: independent v9 audit, exit gate, teardown |

This directory is excluded from the published MkDocs site (`mkdocs.yml` `exclude_docs`) and from
the front-door prose guard (`tests/test_readme.py`), so it may use planning vocabulary.
