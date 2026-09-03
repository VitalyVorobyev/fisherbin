# S06 — Portal topology, reference cut, research narrative

**Workstream:** W3 · **Needs:** S2, S3 · **Parallel with:** S7 · **Status:** queued

## Goal

Make the portal the site root and MkDocs the reference under it, in one session, so the risky
topology move is designed and verified once instead of twice. Today the portal builds to
`/scorequant/portal/` and is never deployed, MkDocs owns the root, and the URL the published
package advertises as both Homepage and Documentation lands a visitor on the reference index
rather than on any explanation. At the same time this session pays the debts that make the
promotion safe and the later content sessions cheap: a committed redirect manifest for every
pre-cut MkDocs URL, the two Docusaurus docs-plugin instances that S8 and this session's research
pages need, the narrative pages moved out of MkDocs per the W3 gate, one generated
criterion/solver table in place of four hand-copied ones, and the plain-English research section
that replaces `/theory` and `/research`. Done means the assembled tree serves the portal at the
root with every old URL still resolving, `pnpm validate` is green, and no reader of the research
pages meets a sentence that explains neither the problem, the usage, nor a finding.

Deployment stays a CI artifact. Going live is S10's last act, after the front door exists.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S03-library-internals-refactor.md`: S3 closing report; the frozen API any
  snippet on these pages must match.
- `docs/programme/S02-manuscript-reconciliation.md`: S2 closing report; the novelty labels the
  research narrative draws from.
- `agenticresearch/manuscripts/NOVELTY_LEDGER.md`: the only source for what the research pages may
  claim. No page in that section derives a new statement.
- `docs/adr/0019-react-learning-portal.md`: the staged-migration decision this session completes.
  Its stage 2 ("moving React to the root and narrowing MkDocs to `/reference/` requires
  content/link parity and an explicit redirect manifest") is the contract to satisfy, not to
  restate.
- `website/docusaurus.config.ts`: `baseUrl`, and `docs: false` which this session replaces with two
  plugin instances.
- `website/scripts/assemble-preview.mjs`: today copies MkDocs `site/` to the preview root and the
  portal build under `portal/`; this session inverts that and emits the redirect stubs.
- `mkdocs.yml`: `site_url`, `nav`, `exclude_docs`.
- `website/scripts/generate_data.py`: already Griffe-introspects `scorequant.__all__`; extended
  here with the criterion/solver compatibility matrix.
- `src/scorequant/solvers/`: the solver-spec registry that matrix is derived from. S3 deleted
  `_SolverSpec.backends`; read the surviving spec structure before designing the generator.
- `website/src/pages/theory.tsx`, `website/src/pages/research.tsx`: deleted here.
- `website/content/research-public.json`: the public claim allowlist, extended here.
- `docs/related-work.md`: source for the "what was already known" research page.
- `tests/test_readme.py`: `_FRONT_DOOR`, `_UNPUBLISHED` and `_UNPUBLISHED_DIRS` all shift when
  narrative pages are retired; `test_retired_pages_are_gone` is the precedent for pinning the
  retirement.
- `.github/workflows/docs.yml`, `.github/workflows/portal-preview.yml`: the two build pipelines
  whose output paths change.

## Deliverables

**Topology.**

- `website/docusaurus.config.ts`: `baseUrl` `/scorequant/portal/` → `/scorequant/`.
- `mkdocs.yml`: `site_url` → `https://vitalyvorobyev.github.io/scorequant/reference/`.
- `website/scripts/assemble-preview.mjs` renamed `assemble-site.mjs` (with the `package.json`
  script renamed to match): the portal build at the assembled root, MkDocs `site/` under
  `reference/`.
- `website/redirects.json`: a committed manifest mapping every pre-cut MkDocs URL to its
  post-cut location. Generated once from the pre-cut `mkdocs build` output, then committed and
  hand-checked — not regenerated on each build, because its purpose is to remember URLs the new
  build no longer knows about. The pre-cut sitemap listed **52 URLs** on 3 September 2026
  (`site/sitemap.xml` after `uv run mkdocs build`), so that is the number to cover and the number
  the test counts.

  One of those 52 is the site root, and it is deliberately **not** a manifest entry: after the cut
  the root serves the portal home, which is the whole point of the promotion. A visitor holding the
  root URL — the one the published package advertises as Homepage and Documentation — should land
  on the explanation, not be bounced to the reference. The manifest therefore covers the 51 page
  URLs, and the redirect test must expect exactly that rather than demanding a stub at the root.
- Redirect stubs emitted by the assemble script at every manifest key: a `<meta
  http-equiv="refresh">` to the target plus `<link rel="canonical">` and a visible one-line link
  for a reader whose browser blocks the refresh. Static stubs are the only mechanism available —
  GitHub Pages has no server-side rewrite.
- `website/tests/redirects.test.ts` (or the closest existing home): every manifest key exists as a
  stub in the assembled tree, every stub's target resolves to a real file in that same tree, and
  the manifest covers every URL the pre-cut sitemap listed. This test is the parity evidence ADR
  0019 asks for.

**Plugin instances.**

- Two Docusaurus docs-plugin instances, `walkthroughs` (`path: walkthroughs`, `routeBasePath:
  walkthroughs`) and `research` (`path: research`, `routeBasePath: research`), both rendered
  through the existing `AppShell`/theme layout rather than the stock Docusaurus docs theme.
- `website/walkthroughs/index.mdx`: the index page only, listing the four walkthroughs S8 writes,
  each row marked as not yet written. The route must exist before S8 so S8 adds pages, not
  infrastructure.

**Reference cut.**

- `docs/motivation.md`, `docs/three-doors.md` and `docs/user-workflow.md` retired from MkDocs.
  Their content is the source material for the portal home, `/get-started` and the walkthroughs;
  this session moves the material into a scratch file named in the closing report and hands it to
  S8 and S10 rather than writing the portal prose itself.
- `docs/index.md` rewritten as the `/reference/` front matter: what this reference contains, and a
  link back to the root for the explanation.
- `mkdocs.yml` nav updated for the retirements; `docs/examples/index.md` and any page linking a
  retired target updated so `mkdocs build --strict` stays green.
- Kept in MkDocs, because nothing in the portal duplicates them and they are reference or
  evidence: `method.md`, `related-work.md`, `api.md`, `glossary.md`, `bibliography.md`,
  `reference/`, `book/`, `gallery/`, `usecases/`, and the six theory and solver example pages
  (`solver-shootout`, `nuisance-profiled-ds`, `soft-purification`, `lloyd-nonmonotone`,
  `ds-geometry-counterexample`, `global-certification`).
- `docs/examples/door1-score-events.md`, `door2-mixture-densities.md` and `door3-classifier.md`
  are the one genuine overlap with S8's walkthroughs. This session decides their fate and records
  it (see Open decisions); it does not delete them speculatively.
- `tests/test_readme.py` lists updated, with the retirements pinned the way
  `test_retired_pages_are_gone` pins the earlier ones.

**One generated compatibility table.**

- The criterion/solver compatibility matrix derived from the solver-spec registry and emitted
  through `website/scripts/generate_data.py` into `website/src/generated/`, plus a small Python
  helper that renders it as the Markdown table `docs/api.md` includes. Today the same table is
  hand-maintained in `docs/method.md` §4, `docs/user-workflow.md` §4, `README.md` and
  `docs/system-design.md`; after this session there is one derived source and the surviving copies
  read from it.
- A test asserting the generated matrix matches what the library actually accepts — every listed
  pair fits, every unlisted pair raises.

**Research narrative.**

- 6–8 Markdown pages under `website/research/`, in plain English, drawn only from the ledger and
  `docs/related-work.md`: the problem; what was already known; what ScoreQuant adds (exchange
  implies Voronoi, the compile bridge); what cannot be certified (the profiled refusal, margins,
  the DS19 gap); how the API names each theorem and refusal; reading the claim record; the book
  table of contents.
- `website/content/research-public.json` extended with the new page data.
- `website/src/pages/theory.tsx` and `research.tsx` deleted; nav and tests updated.

**Bookkeeping.**

- `docs/roadmap.md`: the retired root-promotion cut already records its reason; this session
  confirms the W3 gate text matches what shipped.
- An ADR recording the completed migration, superseding ADR 0019's staging note.

## Done criteria

- The assembled tree serves the portal at its root and MkDocs under `reference/`.
- `website/redirects.json` exists, and the redirect test passes: each of the 51 pre-cut page URLs
  has a stub, every stub target resolves in the assembled tree, and the root serves the portal
  home rather than a stub.
- Both docs-plugin instances render through `AppShell`; `/walkthroughs` and `/research` resolve.
- `docs/motivation.md`, `docs/three-doors.md` and `docs/user-workflow.md` no longer exist, and
  `tests/test_readme.py` pins their retirement.
- One derived criterion/solver matrix; a `grep` for the hand-copied table finds no second source
  of truth, and the conformance test passes.
- `website/src/pages/theory.tsx` and `research.tsx` no longer exist.
- Every research page opens with a "who this is for" line, and every claim id mentioned has an
  adjacent link to its registry entry (zero unlinked claim ids).
- A haiku "pointless statement" pass has run over the research pages and removed every sentence
  that explains neither the problem, the usage, nor a finding; its before/after diff is in the
  closing report.
- Full handoff gate green, plus `cd website && pnpm validate`.
- roadmap M12 table shows S06 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Design the topology change: baseUrl, site_url, assemble inversion, manifest schema, stub shape, and what the redirect test asserts | orchestrator inline | written spec appended to this packet before any code |
| Design the reference cut: page-by-page keep/retire/reduce verdict, including the three door pages | orchestrator inline | written spec appended to this packet |
| Implement the topology change, assemble script, stubs and redirect test from the spec | sonnet | config, script and test diff |
| Generate the pre-cut URL list and draft `redirects.json` from the pre-cut sitemap | haiku | manifest draft plus coverage count |
| Wire the two docs-plugin instances through `AppShell`; delete `theory.tsx`/`research.tsx`; update nav and tests | sonnet | TSX and config diff |
| Design and implement the generated criterion/solver matrix and its conformance test | sonnet | generator, generated JSON, test diff |
| Retire the three narrative pages, rewrite `docs/index.md` as reference front matter, fix every inbound link, update `tests/test_readme.py` | sonnet | docs diff |
| Write the 6–8 research pages from the ledger and `docs/related-work.md` | opus | Markdown drafts |
| Extend `website/content/research-public.json` | haiku | JSON diff |
| "Pointless statement" audit over the research pages | haiku | list of removed sentences |
| Run gates, report failures verbatim | haiku | gate output |

Never a `fable` subagent (`docs/programme/README.md`, budget rule).

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
```

The handoff gate applies in full: this session edits `docs/`.

## Open decisions

- The three door pages (`docs/examples/door1-score-events.md`, `door2-mixture-densities.md`,
  `door3-classifier.md`). They are code-complete and executed, and S8's `ratios.mdx` and
  `michelson.mdx` will cover the same routes narratively. Three options: keep them as the
  code-complete reference the walkthroughs link into; reduce them to stubs pointing at the
  walkthroughs; delete them and let the walkthroughs carry the code. Whichever is chosen, the
  executed-snippet coverage they provide today must not disappear — if the code moves, the test
  that runs it moves with it.
- Whether the research topic list yields 6, 7 or 8 pages. Seven topics are named; the session
  decides whether to split one.
- How `research-public.json` keys map onto the new page slugs; no schema is prescribed.
- Whether the generated compatibility matrix is emitted as JSON consumed by a Markdown include, or
  as a generated Markdown fragment committed alongside the JSON. The second is easier for
  `mkdocs build --strict` to consume; the first avoids a committed derived Markdown file.

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
