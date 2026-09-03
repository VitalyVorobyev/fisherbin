# S06 — Portal information-architecture cut + research narrative

**Workstream:** W3 · **Needs:** S2, S3 · **Parallel with:** S7 · **Status:** queued

## Goal

Replace the portal's two weakest pages with a research section written in plain English from the
novelty ledger. Today `/theory` is one prose block reused across all 14 book chapters, and
`/research` is a hardcoded timeline plus a five-node graph with fixed coordinates; neither reflects
DS16-DS19 or updates when the claim registry changes. This session deletes both and adds a
Docusaurus docs plugin at `routeBasePath: research` with 6-8 Markdown pages, each stating who it is
for and linking every claim it makes back to the registry. Done means `research.tsx` and
`theory.tsx` are gone, the new pages exist and pass `pnpm validate`, and a haiku audit pass finds
no sentence that fails to explain the problem, the usage, or a finding.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S03-library-internals-refactor.md`: S3 closing report; the frozen API this
  narrative and any linked snippet must match.
- `docs/programme/S02-manuscript-reconciliation.md`: S2 closing report; source of the novelty
  labels this narrative draws from.
- `agenticresearch/manuscripts/NOVELTY_LEDGER.md`: the only source for what the narrative may
  claim; no page in this section derives a new statement.
- `docs/related-work.md`: source for the "what was already known" page.
- `website/src/pages/research.tsx`: current hardcoded timeline and graph, to be deleted.
- `website/src/pages/theory.tsx`: current reused prose block, to be deleted.
- `website/content/research-public.json`: extended with the new page content.
- `mkdocs.yml`: nav for `docs/book/ch01-14`, source for the "book table of contents" page.
- `website/docusaurus.config.*`: currently sets `docs: false`; this session enables a docs plugin
  instance scoped to `path: research`, `routeBasePath: research`.

## Deliverables

- Docusaurus docs plugin instance enabled with `path: research`, `routeBasePath: research`,
  rendered through the existing `AppShell`/theme layout (not a bare Docusaurus docs theme).
- 6-8 Markdown pages in plain English: the problem; what was already known (from
  `docs/related-work.md`); what ScoreQuant adds (exchange implies Voronoi, the compile bridge);
  what cannot be certified (profiled refusal, margins, the DS19 gap); how the API names each
  theorem and refusal; reading the claim record; the book table of contents.
- `website/content/research-public.json` extended with the new page data.
- `website/src/pages/research.tsx` and `website/src/pages/theory.tsx` deleted.
- Navigation updated (portal nav no longer links the deleted pages; links the new research
  section); tests updated to match.

## Done criteria

- `website/src/pages/research.tsx` and `website/src/pages/theory.tsx` no longer exist.
- Every new research page opens with a "who this is for" line.
- `grep` for claim ids in the new pages: every claim id mentioned has an adjacent link to the
  registry entry (zero unlinked claims).
- A haiku "pointless statement" pass has run over the new pages and removed every sentence that
  explains neither the problem, the usage, nor a finding; the pass's before/after diff is recorded
  in the closing report.
- `cd website && pnpm validate` is green.
- roadmap M12 table shows S06 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Write the research narrative pages (draws only from the ledger and `docs/related-work.md`, never raw manuscript derivation prose) | fable | 6-8 Markdown page drafts |
| Wire the Docusaurus docs plugin config, delete `research.tsx`/`theory.tsx`, update nav and tests | sonnet | config and TSX diff |
| Extend `website/content/research-public.json` | sonnet | JSON diff |
| Run the "pointless statement" audit pass over the new pages | haiku | list of removed sentences |
| Run `pnpm validate`, report failures verbatim | haiku | gate output |

## Verification

```bash
cd website && pnpm validate
```

This session does not modify `src/scorequant`, `docs/` (only reads `docs/related-work.md` and
`mkdocs.yml` nav for reference), or `examples/`, so the library handoff gate does not apply.

## Open decisions

- Whether the topic list yields exactly 6 or 8 pages: the plan names 7 topics (problem, prior
  knowledge, what ScoreQuant adds, what cannot be certified, API naming, reading the claim record,
  book table of contents); the session decides whether to split one topic to reach 8 or leave it
  at 7, within the stated 6-8 range.
- How `research-public.json` keys map onto the new page slugs; the plan does not specify a schema.

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
