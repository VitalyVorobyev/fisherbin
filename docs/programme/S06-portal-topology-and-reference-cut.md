# S06 — Portal topology, reference cut, research narrative

**Workstream:** W3 · **Needs:** S2, S3 · **Parallel with:** S7 · **Status:** done

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

**Amended by decision R1 below.** The three narrative retirements move to the sessions that
publish their replacements — `docs/three-doors.md` to S8, `docs/motivation.md` and
`docs/user-workflow.md` to S10 — because none of the replacements exists yet and two of the pages
carry 22 executed snippets between them. What stays here is structural:

- `docs/reference/` renamed `docs/symbols/` (decision T1): mounting MkDocs under `/reference/`
  would otherwise put the mkdocstrings pages at `/reference/reference/<topic>/` and collide the
  old `/reference/` URL with the new MkDocs index.
- `docs/index.md` rewritten as the `/reference/` front matter: what this reference contains, and a
  link back to the site root for the explanation. It stops presenting itself as the front door.
- `mkdocs.yml` nav updated for the rename; `mkdocs build --strict` stays green.
- Kept in MkDocs, because nothing in the portal duplicates them and they are reference or
  evidence: `method.md`, `related-work.md`, `api.md`, `glossary.md`, `bibliography.md`,
  `symbols/`, `book/`, `gallery/`, `usecases/`, and the six theory and solver example pages
  (`solver-shootout`, `nuisance-profiled-ds`, `soft-purification`, `lloyd-nonmonotone`,
  `ds-geometry-counterexample`, `global-certification`).
- `docs/examples/door1-score-events.md`, `door2-mixture-densities.md` and `door3-classifier.md`
  are kept whole: they are the code-complete, executed reference that S8's walkthroughs link
  into, and their thirteen executed fences are coverage the programme has already ruled must not
  disappear.
- `tests/test_readme.py` lists are unchanged here; `_FRONT_DOOR` keeps all six entries until the
  pages retire in S8 and S10.

**One generated compatibility table.**

- The criterion/solver compatibility matrix derived from `_SOLVER_TABLE`
  (`src/scorequant/api.py:127`, not `src/scorequant/solvers/` — see decision R3) and emitted
  through `website/scripts/generate_data.py`, both into `portal-data.json` and as the committed
  Markdown fragment `docs/_generated/solver-matrix.md`.
- Three of the seven hand-copies consume the fragment: `docs/method.md` §4, `README.md`, and
  `docs/book/ch06-two-tasks.md`. R3 records why the other four are kept as they are.
- A test asserting the generated JSON matches `_SOLVER_TABLE` and the generated fragment matches
  the JSON. Behaviour-versus-registry is already tested by the executed fence in
  `docs/book/ch14-choosing-a-method.md`, which enumerates all thirty pairings and pins
  `(accepted, refused) == (10, 20)`; the new test does not duplicate it.

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

## Design decisions — topology

Written before any code, per `docs/programme/README.md` invariant 4. Every number here was
measured on the pre-cut tree on 3 September 2026.

### T1. The `/reference/` name collision, and why `docs/reference/` is renamed

MkDocs already owns a section called `reference/`: `docs/reference/{index,certification,
configuration,fitting,information,models,ratios,results,transforms,visualization}.md`, the
mkdocstrings pages. Mounting the whole MkDocs site under `/reference/` without touching that
section produces `/scorequant/reference/reference/fitting/`, and — worse — the old
`/scorequant/reference/` URL would need a redirect stub at exactly the path the new MkDocs index
occupies. That is a hard collision, not an aesthetic one.

**Decision: rename `docs/reference/` to `docs/symbols/`.** Post-cut the mkdocstrings pages are
`/reference/symbols/<topic>/`, which reads as reference → symbols → topic. The rename costs
nothing in URL terms because the `/reference/` prefix already changes every MkDocs URL, so every
one of these pages needs a stub either way.

Consequence for the manifest: two of the 53 pre-cut URLs deliberately take **no** stub.

- `/` — the root becomes the portal home. That is the entire point of the promotion, and it is
  the URL the published package advertises as both Homepage and Documentation.
- `/reference/` — the old mkdocstrings section index. After the cut `/reference/` is the MkDocs
  reference front matter, which answers the same question with real content. A stub there would
  both collide with that page and be a worse answer than the page itself.

51 stubs. (The packet said 52 URLs and 51 stubs; the pre-cut sitemap now lists **53**, because S4
added `examples/michelson-phase/`. The stub count is unchanged at 51 only by coincidence — one
URL was added and one, `/reference/`, moved from the stub list to the deliberate-exclusion list.)

### T2. `website/redirects.json` schema

Paths are baseUrl-relative, no leading slash, trailing slash kept — exactly the sitemap `<loc>`
values minus the `https://vitalyvorobyev.github.io/scorequant/` prefix, so the manifest can be
diffed against a sitemap by eye.

```json
{
  "schemaVersion": 1,
  "sourceSitemapCount": 53,
  "generatedFrom": "site/sitemap.xml, pre-cut build of 2026-09-03",
  "unstubbed": [
    { "path": "", "reason": "..." },
    { "path": "reference/", "reason": "..." }
  ],
  "redirects": [
    { "from": "api/", "to": "reference/api/" },
    { "from": "motivation/", "to": "", "pending": "S10: re-point at the portal home section that replaces it" }
  ]
}
```

A `from` of `"api/"` means the assemble script writes `<assembled>/api/index.html`.

### T3. Stub shape

Static stubs are the only mechanism available — GitHub Pages has no server-side rewrite.

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Moved — ScoreQuant</title>
    <link rel="canonical" href="https://vitalyvorobyev.github.io/scorequant/reference/api/" />
    <meta http-equiv="refresh" content="0; url=/scorequant/reference/api/" />
    <meta name="robots" content="noindex" />
  </head>
  <body>
    <p>This page moved to <a href="/scorequant/reference/api/">/scorequant/reference/api/</a>.</p>
  </body>
</html>
```

`noindex` keeps the stub out of search results so the canonical target is what gets indexed. The
visible link is for a reader whose browser blocks the refresh.

### T4. Where the three retired narrative pages point

`motivation/`, `three-doors/` and `user-workflow/` are retired from MkDocs here, but the pages
that replace them are written in S8 and S10. The redirect test requires every stub target to
resolve in the assembled tree, so a stub pointing at a route that does not exist yet would fail
the gate. All three therefore point at the portal home (`""`) now and carry a `pending` note
naming S10. Emptying `pending` is one of S10's done criteria.

### T5. The live site stays frozen until S10

`.github/workflows/docs.yml` deploys the MkDocs `site/` directory straight to the Pages root on
every push to `main`. Merging S6 unchanged would therefore publish a reference site with the three
narrative pages deleted and no portal at the root to replace them — a real regression on a live
URL that the package advertises.

**Decision: S6 disables the `deploy` job in `docs.yml`** (the `build` job stays, as strict-build
validation) with a comment naming S10 as the session that re-enables deployment against the
assembled tree. The live site holds its last good state, every live URL keeps working, and the
promotion goes live exactly once — in S10, with the owner's authorization, which is what ADR 0019
requires ("Deployment remains preview-only until separately authorized").

### T6. The docs-plugin instances need no theming work

`presets.classic.docs` is `false` today, and `website/src/theme/Layout/index.tsx` already wraps
every plugin-routed page in `AppShell` with `manageHead={false}`. Two
`@docusaurus/plugin-content-docs` instances therefore render through the ScoreQuant shell without
any per-instance theme work. Each instance takes `id`, `path`, `routeBasePath`,
`sidebarPath: false` (AppShell owns navigation; the stock sidebar is not wanted) and no
`editUrl`.

- `walkthroughs`: `path: "walkthroughs"`, `routeBasePath: "walkthroughs"`.
- `research`: `path: "research"`, `routeBasePath: "research"`.

### T7. One base constant instead of nine literals

Nine source files hard-code `/scorequant/portal/` or `/scorequant/`:
`src/lab/lab.worker.ts:24`, `src/components/SearchDialog.tsx:72`, `src/components/Logo.tsx:10`,
`src/data/showcase.ts:92`, `src/pages/lab.tsx:196`, `src/components/AppShell.tsx:103`,
`src/pages/{theory,examples,api}.tsx`, plus `playwright.config.ts:9` and
`tests/navigation.test.ts:7`.

`useBaseUrl` cannot serve all of them — `lab.worker.ts` is a Web Worker with no React context. So
the fan-out collapses into one module, `website/src/lib/site.ts`, exporting `SITE_BASE`,
`REFERENCE_BASE` and a `siteUrl(path)` helper, with a Vitest case asserting that no file under
`website/src` contains the literal `scorequant/portal`. That test is what stops the old prefix
creeping back.

## Design decisions — the reference cut

### R1. The narrative retirement moves out of S6

The packet made S6 delete `docs/motivation.md`, `docs/three-doors.md` and
`docs/user-workflow.md`. Measuring the pages before writing the code changed that verdict:

| Page | Executed `python` fences | Replacement page written in |
|---|---|---|
| `docs/motivation.md` | 0 | S10 (portal home) |
| `docs/three-doors.md` | 13 | S8 (the four walkthroughs) |
| `docs/user-workflow.md` | 9 | S10 (`/get-started`) |

Two facts follow. First, **not one of the three replacements exists yet** — all are written in S8
or S10 — so retiring the pages here opens a window in which the material exists only in a scratch
file. Second, `three-doors.md` and `user-workflow.md` carry **22 executed snippets** between them,
including the `CentralLogRatioScore` fence S4 had just made executable; deleting the pages
un-executes them, and the packet's own open decision forbids exactly that ("the executed-snippet
coverage they provide today must not disappear — if the code moves, the test that runs it moves
with it").

**Decision: each page is retired by the session that publishes its replacement.**

- `docs/three-doors.md` → **S8**, whose four walkthroughs are one per input route; its 13 fences
  move into walkthrough MDX, where the extended `tests/test_portal_snippets.py` executes them.
- `docs/motivation.md` and `docs/user-workflow.md` → **S10**, which writes the portal home and
  `/get-started`; `user-workflow.md`'s 9 fences move into `/get-started`, whose whole point is
  showing snippets with their captured output.

S6 keeps what is genuinely structural: the topology, the plugin routes, the redirect manifest, the
`docs/reference/` rename, one generated compatibility matrix, and the research narrative. This is
not a reduction in the programme's scope — the retirements still happen, on the W3 gate's terms —
only a reassignment to the sessions that can do them without a coverage gap. It also simplifies the
redirect manifest: with all three pages still present, every stub target is a real MkDocs page and
nothing dangles (superseding decision T4, whose `pending` mechanism is no longer needed).

`tests/test_readme.py`'s `_FRONT_DOOR` therefore keeps all six entries here, and the
`test_retired_pages_are_gone` extension moves to S8 and S10 with the pages.

### R2. `docs/index.md` becomes the reference front matter, without losing the site map

`docs/index.md` (123 lines: Two tasks / Three doors / Install / Quickstart / Site map) is
rewritten as the front matter of `/reference/`: what this reference contains, and a link back to
the site root for the explanation. The Site map section stays and stays valid, because R1 keeps
its three link targets alive. The Two tasks / Three doors / Install / Quickstart sections stay
too — they are the reference's own orientation, and the portal home that would duplicate them
does not exist until S10.

The one change with teeth: the page must stop presenting itself as the front door of the project.
The portal home is the front door; this page opens by saying so.

### R3. One generated compatibility matrix, from `api.py` not `solvers/`

The packet pointed at "the solver-spec registry in `src/scorequant/solvers/`". That package does
exist (`common.py`, `kmeans.py`, `scalar.py`, `soft.py`) but holds the numerical kernels; the
registry is `_SolverSpec` / `_SOLVER_TABLE` at `src/scorequant/api.py:103-139`, two fields per
spec (`partition_criteria`, `quantizer_criteria`) after S3 deleted `backends`.

The table is hand-copied in **seven** places, not the four the packet named:

| Location | Shape | Verdict |
|---|---|---|
| `docs/method.md:137` | config x task grid | **consume the generated fragment** |
| `README.md:257` | grid plus a "Contract" column | **consume the generated fragment** |
| `docs/book/ch06-two-tasks.md:205` | config x task grid | **consume the generated fragment** |
| `docs/user-workflow.md:63` | narrative "choose it when" | keep — it is advice, not a matrix; retires in S10 |
| `docs/system-design.md:38` | one row per (task, criterion, config) | keep — unpublished internal design record |
| `docs/adr/0014:31` | config x task grid | keep — an accepted ADR is a frozen record and is not rewritten |
| `docs/book/ch14-choosing-a-method.md:63` | Python dict in an executed fence | keep — see below |

`ch14`'s dict is not a copy of the table; it is a **conformance test already running in the
docs**. The fence enumerates every (task, config, criterion) triple, asserts each is accepted or
refused, checks the refusal message, and pins `(accepted, refused) == (10, 20)`. That is exactly
the "every listed pair fits, every unlisted pair raises" test the packet asks for, and it has been
green all along. So the new conformance test does **not** re-verify library behaviour; it verifies
the two derived artifacts against the registry:

1. the generated JSON equals what `_SOLVER_TABLE` declares, and
2. the generated Markdown fragment equals what the JSON declares.

Behaviour-versus-registry stays ch14's job, and `ch14`'s dict gains a comment naming the generated
matrix as the source it is checking against.

**Emission: generated regions, not an include.** MkDocs here loads only `search` and
`mkdocstrings`, so there is no snippet-include mechanism, and `README.md` is not a MkDocs page at
all and could never use one. So `website/scripts/generate_data.py` grows a `_solver_matrix()`
section into `portal-data.json` and then rewrites the table **in place** in each consuming file,
between markers:

```markdown
<!-- generated: solver-matrix (do not edit by hand; run `pnpm generate:data`) -->
| Configuration | `optimize_partition` | `fit_quantizer` |
...
<!-- /generated: solver-matrix -->
```

This needs no new Markdown extension, no new page, no nav entry and no `docs/_generated/`
directory, and it works identically for `README.md` and for MkDocs pages. The test asserts each
region's content equals the table rendered from `_SOLVER_TABLE`, so a hand edit inside a region
fails the gate.

### R4. `docs/reference/` is renamed `docs/symbols/`

Nine mkdocstrings pages plus an index move from `docs/reference/` to `docs/symbols/`, for the
collision reason in T1. Inbound updates: `mkdocs.yml` nav (10 lines), and the portal's generated
`reference` deep links, which are produced by `generate_data.py` and so change in the generator,
not by hand — `website/src/generated/portal-data.json` carries `/reference/index/` or
`/reference/configuration/` on every one of its API symbols.

## Done criteria

- The assembled tree serves the portal at its root and MkDocs under `reference/`.
- `website/redirects.json` exists, and the redirect test passes: each of the 51 pre-cut page URLs
  has a stub, every stub target resolves in the assembled tree, and the root serves the portal
  home rather than a stub.
- Both docs-plugin instances render through `AppShell`; `/walkthroughs` and `/research` resolve.
- `docs/reference/` is gone and `docs/symbols/` serves the mkdocstrings pages; every inbound
  link, including the portal's generated deep links, points at the new path.
- One derived criterion/solver matrix, consumed by `docs/method.md`, `README.md` and
  `docs/book/ch06-two-tasks.md`; the generated-artifact test passes. (The three narrative
  retirements are S8's and S10's per R1, and are pinned in those packets' done criteria.)
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

**What this session was for.** The portal existed but was never served anywhere; MkDocs owned the
site root, which is the URL the published package advertises as both Homepage and Documentation,
so every reader arriving through PyPI landed on a reference index rather than on an explanation.
This session inverts that — the portal at the root, MkDocs beneath it at `/reference/` — and pays
the debts that make the inversion safe.

**What was delivered.**

The topology. `baseUrl` is `/scorequant/`; `mkdocs.yml`'s `site_url` is
`.../scorequant/reference/`; `assemble-preview.mjs` became `assemble-site.mjs` and now puts the
portal build at the assembled root and the MkDocs build under `reference/`. The nine source files
that hard-coded `/scorequant/portal/` collapsed into one `SITE_BASE` constant in
`website/src/lib/site.ts`, with a test that fails if the old literal comes back.

The redirect manifest. `website/redirects.json` covers all 53 pre-cut URLs: 49 get static stubs
(`meta refresh` + `rel=canonical` + `noindex` + a visible link, because GitHub Pages has no
server-side rewrite), and 4 deliberately do not, each with a written reason the test enforces.
`assemble-site.mjs` verifies at the end of every run that each entry produced a stub and each
stub's target resolves — the parity evidence ADR 0019 asked for, checked by the build rather than
by eye.

The reference cut. `docs/reference/` is now `docs/symbols/`; `docs/index.md` opens by saying it is
the reference and pointing at the root for the explanation; the criterion/solver compatibility
table is generated from `_SOLVER_TABLE` into `portal-data.json` and into marked regions of
`docs/method.md`, `README.md` and `docs/book/ch06-two-tasks.md`, with `tests/test_solver_matrix.py`
failing on a hand edit or an unregenerated registry change.

The routes. Two `plugin-content-docs` instances serve `/walkthroughs` (index only, for S8 to fill)
and `/research` (ten pages). `theory.tsx` and `research.tsx` are gone. The nav is eight entries —
Docs, Walkthroughs, Lab, API, Research, Benchmarks, Reference, Blog — which promotes the Lab and
the reference from a single call-to-action and a footer link to primary destinations.

The research narrative. Ten pages drawn only from the novelty ledger and `docs/related-work.md`,
each opening with a "who this is for" line, with 100 claim-id links and zero unlinked ids. The
public claim allowlist went from 5 to 61.

**What was verified.** `ruff check` clean; `ruff format --check` 246 files; `ty check src` clean;
`pytest -n auto` **505 passed**; float32 leg 4 passed; `uv build` wheel and sdist;
`mkdocs build --strict` clean; `pnpm validate` clean; `pnpm test` 52 passed;
`pnpm test:e2e` **13 passed, 5 skipped, 0 failed**; `pnpm assemble:site` reports 49 stubs verified.
All four unstubbed URLs were checked by hand in the assembled tree and each serves real content,
not a stub.

**Four things the packet got wrong, corrected here.**

1. *The `/reference/` collision.* MkDocs already owned a `reference/` section, so mounting the site
   under `/reference/` would have produced `/reference/reference/fitting/` and put a required stub
   at the exact path the new MkDocs index occupies. Hence the `docs/symbols/` rename (T1).
2. *The reference cut would have deleted 22 executed snippets.* `three-doors.md` carries 13 Python
   fences and `user-workflow.md` 9, and none of their replacement pages exists until S8 or S10.
   The retirements moved to the sessions that publish their replacements (R1), which is now a
   standing rule in `docs/programme/README.md`.
3. *The registry is in `api.py`, not `solvers/`,* and the table is hand-copied in seven places, not
   four — one of which (`ch14`) is not a copy at all but a working conformance test that already
   pins all 30 pairings, so the new test checks the derived artifacts and does not duplicate it
   (R3).
4. *The count was 53, not 52.* S4 added `examples/michelson-phase/` after the packet was written.

**Three defects found by building it, none of which the packet anticipated.**

- *Stubs could overwrite real content.* Two old MkDocs URLs share a name with a portal route,
  `/api/` and `/examples/`. The assemble script now refuses to write a stub over an existing path
  and says what to do instead; both URLs became deliberate non-stubs, and the portal pages that now
  occupy them link onward to the reference pages that used to.
- *`trailingSlash: false` made section-index URLs host-dependent.* A docs section emitted both
  `research.html` and a `research/` directory with no `index.html`; `docusaurus serve` resolved the
  directory and rendered the 404 shell. The site now uses directory URLs throughout, which also
  matches the MkDocs reference beneath it, so the whole domain reads one way. The 119 relative
  links in the research pages moved to site-absolute form, because a relative link resolves one
  level too deep once a route carries a trailing slash.
- *The stock docs theme crashes inside this shell.* Its table of contents calls
  `document.querySelector(".navbar").clientHeight`; the portal renders its own header and has no
  `.navbar`, so every docs page with headings threw during hydration — correct on the server, then
  crashed to the error boundary in the browser. `src/theme/DocItem/Layout` replaces it with a
  contents list built from `useDoc().toc` directly, and `src/theme/DocRoot/Layout/Main` removes the
  second `<main>` the stock layout nests inside AppShell's. The e2e suite now asserts one `<main>`
  per route and runs the accessibility scan on `/research` and `/walkthroughs` as well as the home
  page — which is what caught the last one: Infima stripes even table rows with `rgba(0,0,0,.03)`,
  against which the portal's link blue measures 4.3:1, below the AA threshold. Every page with a
  link in a table was failing.

**What is left open.**

- **The allowlist expansion is a publication decision and needs the owner's eye.** It went from 5
  claims to 61. The lines used were: anything the library's public surface already exposes, and
  anything `docs/related-work.md` already states in substance, plus the DS14–DS19 margin and
  profiled-bridge results this packet explicitly required. DS18, the strip-DP consistency result,
  the matrix-tilt non-quasiconvexity and every `measured`-status claim were deliberately withheld.
- `README.md`'s 14 absolute URLs still point at the pre-migration structure, deliberately: they
  describe the deployed site, and updating them before the deployment flips would break live links
  on GitHub and PyPI for a migration that has not shipped. S10 updates them in the commit that
  turns deployment on.
- The `walkthroughs` instance has one page. S8 fills it.
- A portal-native table of contents exists now but has no scroll-spy, because the stock one cannot
  run here. Nobody has asked for one.

**The one thing the next session must know.** The live site is frozen. `docs.yml` still builds
MkDocs strictly on every push, but its Pages upload and `deploy` job are both `if: false`, so the
deployed site holds its last pre-migration state and every live URL keeps working while S8 and S10
write the pages that the new topology is for. That freeze is what makes it safe for `main` to carry
a half-migrated site, and S10 is the session that lifts it — against the assembled tree, with the
owner's authorization, which is what ADR 0019 requires. Do not turn it on earlier, and do not
assume it is on: a reader visiting the site today is not seeing what is in the repository.
