# S08 — Portal user path

**Workstream:** W3 · **Needs:** S6, S7 · **Parallel with:** — · **Status:** queued

## Goal

Turn the portal from a marketing shell into the working entry point for a new user. Today the
home page carries marketing copy and a "proof strip", `/docs` shows three hardcoded snippets (one
of which raises: `website/src/pages/docs.tsx:20`, fixed in S1), and `/examples` does not index the
showcases S4 and S7 build. This session rewrites the home page around the problem statement, one
runnable example, and the two public tasks; replaces `/docs` with `/get-started` built from
`docs/user-workflow.md`; replaces `/examples` with `/showcases` indexing the S4 and S7 pages plus
FlowCyt; wires `pnpm test:e2e` into `portal-preview.yml`; and turns on the `/portal/` deployment
per the owner's site-strategy decision. Done means every route is free of slogans, every snippet
actually executes, e2e is green in CI, and the portal is live.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S06-portal-ia-and-research-narrative.md`: S6 closing report; the research
  section and shell layout this session's navigation must link into.
- `docs/programme/S07-hep-classifier-showcase.md`: S7 closing report; the showcase page(s)
  `/showcases` must index.
- `docs/user-workflow.md`: the best on-ramp today; `/get-started` is built from this document.
- `website/src/pages/docs.tsx`: current `/docs` page, replaced by `/get-started`.
- `website/src/pages/examples.tsx`: current `/examples` page, replaced by `/showcases`.
- `tests/test_portal_snippets.py`: executes portal `code:` strings; extended for the new pages.
- `.github/workflows/portal-preview.yml`: CI workflow this session adds the e2e step to.
- `docs/three-doors.md`: source for the "two public tasks" framing on the home page.
- `website/package.json`: `test:e2e` script (`playwright test`) already defined.

## Deliverables

- Home page rewritten: problem statement, one runnable example, the two tasks
  (`optimize_partition` / `fit_quantizer`), links onward; no proof strip.
- `/docs` replaced by `/get-started`, built from `docs/user-workflow.md`; every snippet on the
  page executed by `tests/test_portal_snippets.py`.
- `/examples` replaced by `/showcases`, indexing the S4 and S7 example pages plus the existing
  FlowCyt teaser.
- `.github/workflows/portal-preview.yml` runs `pnpm test:e2e`.
- Pages deployment of `/portal/` enabled.

## Done criteria

- No route contains a sentence a haiku slogan-auditor flags; the audit's before/after list is
  recorded in the closing report.
- Every snippet on `/get-started` is executed by `tests/test_portal_snippets.py` and asserts a
  result object (not a name check).
- `pnpm test:e2e` runs in `portal-preview.yml` and is green in CI.
- The `/portal/` deployment is live (a reachable URL is recorded in the closing report).
- `cd website && pnpm validate` is green.
- roadmap M12 table shows S08 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Write home page and `/get-started` prose from `docs/user-workflow.md`, no proof strip, plain language | fable | page copy drafts |
| Implement the TSX routes, snippet execution wiring, `/showcases` index | sonnet | TSX diff |
| Wire the e2e step into `portal-preview.yml` and the `/portal/` deployment config | sonnet | workflow diff |
| Run the slogan audit pass over every route | haiku | list of flagged and removed sentences |
| Run `pnpm validate` and `pnpm test:e2e`, confirm CI green, report failures verbatim | haiku | gate output |

## Verification

```bash
cd website && pnpm validate
cd website && pnpm test:e2e
```

This session does not modify `src/scorequant` or `examples/`; it reads but does not rewrite
`docs/user-workflow.md`, so the library handoff gate does not apply. If the session does end up
touching `docs/`, run the full handoff gate as well.

## Open decisions

- Exact mechanics of enabling the `/portal/` Pages deployment (workflow trigger, secrets, target
  branch): the owner has already decided deployment happens; this session decides how.
- Whether `/get-started` fully replaces `docs.tsx` or the file is kept as a redirect stub; the
  plan says "replaced" without specifying redirect handling.

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
