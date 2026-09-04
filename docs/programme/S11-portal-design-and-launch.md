# S11 — Portal design pass, inline demos, and launch

**Workstream:** W3 · **Needs:** S10 · **Parallel with:** — · **Status:** done

## Goal

S10 leaves the front door correct: the home page teaches the problem and opens on a measured
comparison, `/get-started` walks the first fit through to the meaning of every number it prints,
and every displayed output is captured from a run. What S10 does not leave is a *designed*
surface. There is no dark mode, the stylesheet is one 854-line file carrying rules for pages that
were deleted two sessions ago, and nothing on any page runs — a reader who wants to see the method
work must navigate to `/lab` and set it up themselves.

This session finishes the surface and then publishes it. It refines and extends the existing
design system rather than replacing it, embeds live runs where the reader is already reading, and
turns the site on at the URL the released package advertises. Done means both themes pass
accessibility on every route, three inline demos reproduce their page's committed numbers in the
reader's browser, and the root deployment is live at a URL recorded in the closing report.

The split that created this session is recorded in `docs/programme/README.md` as the sibling of
S6's retirement rule: **a surface is published by the session that finishes it.**

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S10-portal-front-door.md`: S10's closing report, and its design decisions D1-D10,
  which this session does not re-open.
- `website/src/css/global.css`: 854 lines, one file. Several comments record specific measured
  contrast ratios; they are load-bearing.
- `website/src/lab/useLabRunner.ts` and `website/src/lab/lab.worker.ts`: the browser runtime the
  inline demos reuse. The worker imports Pyodide through a constructed `Function` so webpack never
  sees it; a custom `runtime-boundary-warnings` webpack plugin in `docusaurus.config.ts` keeps the
  `lab-worker` chunk loadable.
- `website/tests/e2e/portal.spec.ts`: the invariant that ordinary routes issue no Pyodide, marimo
  or wheel requests, plus the five tests that pin `useLabRunner`'s behaviour.
- `.github/workflows/docs.yml`, `.github/workflows/portal-preview.yml`: the two pipelines the
  deployment flip changes.
- `website/scripts/assemble-site.mjs` and `website/redirects.json`: the assembled tree and the
  53-URL manifest whose parity the flip must preserve.
- `docs/adr/0019-react-learning-portal.md` and `docs/adr/0025-portal-at-the-site-root.md`: the
  deployment authorization chain.

## Deliverables

**Dark mode, which needs one shell entry point first.** `colorMode` is
`{defaultMode: "light", disableSwitch: true}` today, and flipping the switch is one line — but
`useColorMode()` requires `ColorModeProvider`, which Docusaurus mounts inside `@theme/Layout`,
and the five `website/src/pages/*.tsx` routes render `AppShell` directly, outside it. Calling the
hook there throws. So convert those pages to render inside `@theme/Layout` (already swizzled to
`AppShell`), after which every route in the site passes through one shell. Two simplifications
fall out: `AppShell`'s `lab` prop derives from `useLocation()`, which it already calls, and
`manageHead` disappears because `Layout` emits `PageMetadata` for all routes. Rejected: a
hand-rolled `data-theme` toggle with our own no-flash script, which fights Docusaurus's own
`data-theme` writer and leaves the Prism theme unswitchable.

**A semantic token layer.** `--surface`, `--surface-raised`, `--text`, `--text-muted`, `--border`,
`--accent` and their siblings, defined on `:root` and overridden under `[data-theme="dark"]`. Each
substitution must be colour-identical in light mode, so light mode stays byte-identical and only
dark mode is new. `.site-shell--lab` hard-codes roughly forty literal hexes; rewrite them as a
*scoped token override* rather than making the Lab theme-following, which keeps its instrument-panel
identity a deliberate palette instead of forty magic numbers and leaves the riskier flip to a later
session. `website/src/components/ScoreSpace.tsx` needs the same treatment; the chart components
already use `var(--line)` and follow tokens for free.

**`global.css` split into named files**, listed explicitly in `theme.customCss` rather than
`@import`ed, to avoid PostCSS ordering surprises: tokens, base, shell, prose, home, lab, charts,
components, responsive, print. One rule governs the split: **a rule may not be edited in the step
that moves it**, and comments travel with their rules. Verify mechanically — build before and
after, and diff the emitted stylesheet after whitespace normalisation. The diff must be empty.

**The dead-CSS purge**, from a Playwright `startCSSCoverage()` pass across all routes at both
viewports intersected with a class-name grep, so only the intersection is deleted. Confirmed dead
today: `.theory-layout`, `.chapter-list`, `.reading-progress`, `.theory-reader`, `.callout`,
`.example-grid`, `.example-card` and their `@media` appearances, all orphaned by the `theory.tsx`,
`research.tsx`, `examples.tsx` and `showcase.tsx` deletions in S6 and S8. Also `PortalData.content`
in `website/src/data/portal.ts` with `_content_data()` and `_plain_excerpt()` in
`website/scripts/generate_data.py`: generated, typed, and consumed nowhere.

**Inline demos.** The governing principle is that **a demo reproduces the page's committed number;
it does not introduce a new one.** Before activation the component shows the committed result;
after activation it shows the reader's own run beside it, labelled. That is what keeps live
computation compatible with the S8 fact contract instead of in tension with it — a number computed
in the reader's browser after an explicit click is the reader's run, not a published claim — and it
is the better demonstration, because "you just reproduced the number on this page" beats "here is a
number".

Three layers, so that the Pyodide import cannot reach an ordinary route chunk:

- `LiveFit` — always in the route chunk. Imports only React, the generated captured result,
  `ScoreSpace`, `Diagnostics`. Renders the committed result and one `<button>`.
- `LiveFitRunner` — reached only through `await import("./LiveFitRunner")` inside the click handler.
  This is the chunk that carries the `new Worker(new URL("./lab.worker.ts", import.meta.url))`
  reference. Use `useState<ComponentType | null>` plus `void import(...)`, not `React.lazy` with
  `Suspense`, which interacts badly with Docusaurus server rendering.
- `LiveFitProvider` — mounted once in `AppShell`, enforcing at most one activated demo per page.

Three demos, and only three: the home page's loss-identity beat, `/get-started` beside the first
fit, and `/walkthroughs/ratios` (600 rows, the smallest real table, and its `?job=ratios` preset
already exists). Deliberately none on flowcyt, hep or michelson — each extra demo multiplies
cold-start end-to-end time and accessibility surface, and these three already cover front door,
first fit and real data. Those keep the `/lab?job=<slug>` hand-off S8 built, which this session
extends with a few more prefilled jobs.

**A shared runtime client.** `useLabRunner` owns one `Worker` per hook instance today, so two
activated demos would instantiate two Pyodide heaps in one tab — a genuine out-of-memory risk on a
phone. Extract a module-level singleton owning worker creation, refcounting, routing by run id and
termination, and refactor `useLabRunner` to subscribe to it while keeping its exported interface
byte-identical, so `website/src/pages/lab.tsx` is untouched and its five e2e tests keep their
meaning. Only one run may be in flight; a second activation is refused, not queued. This is the
highest-risk change in the session, so the fallback is written down in advance: **if it is not
green by mid-session, ship per-mount workers and rely on the provider's one-active-demo guard**,
which gets most of the benefit for none of the risk.

**Accessibility made executable.** A test parsing the token file and asserting every declared
foreground/background pair meets 4.5:1 — 3:1 for large text and UI borders — in *both* themes. This
is the same move the S8 fact contract made on numbers, and it is what stops dark mode from quietly
reintroducing the 4.48:1 token S8 fixed. The axe scans run twice per route, once per theme, driven
through the real toggle rather than `emulateMedia` alone.

**The demo invariant, asserted in both directions.** The e2e suite today asserts only that ordinary
routes issue no heavy-runtime requests — an invariant a broken feature satisfies. Add one
desktop-only test that asserts zero matching requests after navigation, clicks the activation
button, and then asserts a Pyodide request does occur and the live result matches the committed one.

**Deployment.** The root deployment turned on: the portal at `/scorequant/`, MkDocs under
`/scorequant/reference/`, the S6 redirect stubs live. `docs.yml` and `portal-preview.yml`
reconciled into whatever single publishing path the session designs, with the preview path kept
for pull requests.

Publication is an authorized action, not a merge side effect. The flip needs the owner's explicit
go-ahead, requested with the assembled tree already verified, and the live URL is recorded in the
closing report.

**Also handed over by S6.** `README.md` carries **14 absolute
`https://vitalyvorobyev.github.io/scorequant/...` links**, and they describe the *deployed* site,
which does not change until this session flips the deployment. They were therefore deliberately
left pointing at the pre-migration structure: updating them earlier would have broken live links —
on GitHub and on the PyPI project page — for a migration that had not shipped. In the same commit
that turns deployment on, every one of them moves under `/reference/`, except the badge link and
any that should now point at a portal route. `docs/reference/` was renamed `docs/symbols/` in S6,
so the "reference" link becomes `.../reference/symbols/`. `pyproject.toml`'s `Homepage` and
`Documentation` already point at the site root and are correct unchanged — after the flip the root
is the portal home, which is the point.

## Done criteria

- Both themes pass axe on every scanned route; the contrast test covers every declared pair in
  both themes.
- `global.css` no longer exists as a single file, and the emitted-stylesheet diff across the split
  is empty.
- The named dead rules are gone, and `PortalData.content` with its generator is gone.
- The three demos load with zero heavy-runtime requests and produce one after an explicit click,
  asserted in both directions.
- `useLabRunner`'s exported interface is unchanged and `lab.tsx`'s five e2e tests pass unmodified,
  or the written fallback was taken and the closing report says so.
- `pnpm assemble:site` reports full stub/target parity.
- Every pre-cut MkDocs URL resolves on the live site, spot-checked against `website/redirects.json`
  after deployment and recorded in the closing report.
- The root deployment is live and its URL is in the closing report, flipped with the owner's
  recorded go-ahead.
- Full handoff gate green, plus `cd website && pnpm validate` and `pnpm test:e2e`.
- roadmap M12 table shows S11 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Write the design spec into this packet — token table, file split map, demo placement, the runtime-sharing decision and its fallback, the workflow reconciliation | orchestrator inline, or opus | packet section |
| One shell entry point: the five `src/pages/*.tsx` routes render inside `@theme/Layout` | sonnet | TSX diff |
| Dead-CSS coverage pass; produce the confirmed deletion list | haiku | class list with evidence |
| Split `global.css` verbatim; show the emitted-stylesheet diff empty | sonnet | CSS diff plus verification output |
| Token layer, colour-identical light-mode substitution, `[data-theme="dark"]`, scoped lab palette | sonnet | CSS diff |
| Contrast test, theme toggle, `colorMode` config, `prism.darkTheme` | sonnet | test and config diff |
| Shared runtime client state machine | opus to design, sonnet to implement | module plus unit test |
| `LiveFit` components and the three placements, against the written spec | sonnet | TSX diff |
| Extra Lab presets and their coverage | sonnet | generator and test diff |
| The design pass proper: rhythm, hierarchy, front-door components | opus, or orchestrator inline | TSX and CSS diff |
| Axe in both themes; the both-directions demo test | sonnet | e2e diff |
| Workflow reconciliation | sonnet | workflow diff |
| `README.md` absolute-link rewrite | haiku | link table and diff |
| Post-deployment redirect spot-check against the manifest | haiku | URL/status table |
| Run gates and e2e, report failures verbatim | haiku | gate output |

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
cd website && pnpm test:e2e
cd website && pnpm assemble:site
```

## Open decisions

- Whether `/lab` should eventually follow the site theme rather than keeping its scoped dark
  palette. This session deliberately defers it; the scoped-token rewrite is what makes it a
  one-block change later.
- Whether demo activation should respect `navigator.connection.saveData` or a metered-connection
  hint, given the runtime is roughly 15 MB on first activation.
- Whether `.github/workflows/docs.yml` survives as a fast MkDocs-only pull-request check or is
  folded into the single site workflow entirely.
- Whether to mirror the FlowCyt source data to object storage. `examples/cell_population/fixture.py`
  fetches from a single university file share, which is the reproducibility risk behind the M5 data
  gate; both downloaders already verify SHA-256, so a mirror is integrity-safe, and the missing
  piece is only a configurable base URL, since `REMOTE_RAW` and `RAW_BASE` are hard-coded constants
  and no environment override exists. The dataset is CC-BY-NC-SA-4.0. The owner confirmed on
  4 September 2026 that the intended host, `vitavision.dev`, is entirely non-commercial, so the
  NonCommercial clause is satisfied and that question is closed; what remains is mechanical, and
  binding — the licence notice and attribution must travel with any mirrored bytes, and ShareAlike
  applies to anything derived from them. Out of scope for this session; recorded so it is not
  rediscovered.
- Whether the deployment should anticipate a later custom domain. The eventual move changes
  `baseUrl` from `/scorequant/` to `/`; S6 already centralized that into `website/src/lib/site.ts`,
  and `docusaurus.config.ts`, `mkdocs.yml`'s `site_url` and the redirect manifest also encode the
  path. Keep the publishing path host-agnostic so the move stays a configuration change, and note
  that the github.io URL must keep resolving either way, because the published package advertises
  it — which makes the later move a redirect, not a replacement.

## Design decisions

Written before any code, per the orchestrator contract. The packet's open decisions are answered
at the end; these are the decisions that govern the build.

**D1 — there are four page routes, not five.** The packet says "the five `website/src/pages/*.tsx`
routes" throughout. That count was written before S10 deleted `docs.tsx`, and the directory now
holds exactly `index.tsx`, `api.tsx`, `benchmarks.tsx` and `lab.tsx`. Every instruction in this
packet that says five means those four.

**D2 — the page routes render `@theme/Layout`; they do not nest `AppShell` inside it.** The
problem the packet states is real: `useColorMode()` needs `ColorModeProvider`, Docusaurus mounts
it inside `@theme/Layout` via `LayoutProvider`, and all four page routes call `AppShell` directly,
outside it. But the fix is a *replacement*, not a wrapping. `website/src/theme/Layout/index.tsx`
already renders `AppShell` itself, so a page that rendered `<Layout>` around its own `<AppShell>`
would mount two complete shells: two `<header>`s, two `<footer>`s, two `SearchDialog`s each with
its own Ctrl/Cmd+K listener, two skip links, and two `<main id="main-content">` — a duplicate `id`,
which also makes the skip link's target ambiguous. So the four pages swap `<AppShell …>` for
`<Layout …>` and pass the same `title` and `description`.

This is worth stating because the existing guard would not have caught the mistake everywhere.
`website/tests/e2e/portal.spec.ts` asserts `main` count `=== 1`, but its route loop covers
`get-started`, `api`, `walkthroughs/*`, `benchmarks` and `research` — **not** `./` and not `./lab/`.
Home and the Lab are exactly the two routes whose shell this session changes most, so the loop
gains both entries in the same commit as the change.

**D3 — `manageHead` is deleted, and the Layout swizzle emits `PageMetadata` instead.** Today
`AppShell` owns a `<Head>` block gated on `manageHead`, defaulting true, and the Layout swizzle
passes `manageHead={false}` so blog and error routes do not race two `<title>` tags. Once every
route goes through `Layout`, that flag would be false everywhere and the four page routes would
silently lose their titles, because Docusaurus's `pages` plugin does not inject `PageMetadata` the
way the blog and docs plugins do.

The answer is the one upstream already uses, and it was checked rather than assumed: stock
`@docusaurus/theme-classic`'s `Layout` renders `<PageMetadata title={title} description={description} />`
as its first child inside `LayoutProvider`, and the blog and docs pages then render their *own*
`PageMetadata` nested inside it. React Helmet's last-wins semantics are what make that safe, and it
is the documented pattern rather than an accident. The swizzle adopts it verbatim, `AppShell` stops
importing `Head` altogether, and the `manageHead` prop disappears from the codebase.

**D4 — `AppShell`'s `lab` prop derives from the route.** `Layout`'s props are Docusaurus's own
type, so threading a custom `lab` boolean through it would need a cast. `AppShell` already calls
`useLocation()` (for nav active state), so the Lab's dark shell and suppressed footer key off the
pathname instead. The prop is removed, not merely defaulted.

**D5 — dark mode promotes a palette the site already owns.** This is the session's central design
decision and it is what "refine and extend, not a new identity" means concretely.

The portal is not a light-only design that must invent a dark one. It already contains a complete,
deliberate dark palette, used for the surfaces that represent *the machine*: `.score-space`
(`#091a37` ground, `#1b3455` grid, `#6c9ed4` bisectors), `.code-block` (`#263d5c` border,
`#dbe8f8` text), the snippet output block (`#05141f`), `.claim-graph`, `.api-symbol code`, and the
whole `.site-shell--lab`. Roughly a hundred colour literals live in those blocks. The light page is
paper; the dark inserts are instruments.

Dark mode therefore does not recolour the site. It **promotes the instrument ground to be the page
ground**, and the instruments stay dark — which is why the design survives the flip instead of
inverting into something unrecognizable. In dark mode the code block is no longer a dark rectangle
on paper; it is a slightly raised panel on a dark page, distinguished by its border and its own
deeper ground rather than by contrast with white. That is a smaller change than a conventional
inversion and a truer one.

**D6 — three tiers of token, not one.** The packet asks for a semantic layer. The inventory shows
it has to be three, because the site has three kinds of colour and they behave differently across
themes.

- *Palette* — the raw scale that exists today: `--ink-950`…`--ink-500`, `--paper`, `--paper-warm`,
  `--paper-blue`, `--line`, `--line-strong`, `--blue`, `--blue-dark`, `--cyan`, `--amber`, `--red`.
  Unchanged, and still the only place a hex literal is written.
- *Semantic* — new, and the only names rule bodies may use: `--surface`, `--surface-raised`,
  `--surface-sunken`, `--text`, `--text-muted`, `--text-faint`, `--border`, `--border-strong`,
  `--accent`, `--accent-strong`, `--accent-quiet`, `--good`, `--warn`, `--bad`. Defined on `:root`
  as aliases of palette tokens, redefined under `[data-theme="dark"]`.
- *Instrument* — `--inst-ground`, `--inst-raised`, `--inst-line`, `--inst-text`, `--inst-muted`,
  `--inst-accent`. The dark palette above, named. These are **the same in both themes**; that is
  the point of D5.

`.site-shell--lab` stops being forty magic numbers and becomes a scoped override of the *semantic*
tokens to instrument values. Whether `/lab` should eventually follow the site theme stays the
packet's open decision, and this rewrite is what reduces it to one block.

**D7 — light mode must come out pixel-identical, and that is checked by screenshot, not by eye.**
Every semantic token is introduced as an alias of exactly the palette token the rule already used,
so the *computed* colour cannot change; but the emitted stylesheet text does change, so the
packet's "diff the emitted stylesheet" test cannot be the check for this step. The check is:
build, screenshot all eleven routes at 1440x900 and 390x844 in light mode, apply the token
rewrite, rebuild, screenshot again, and require the pairs to match. A colour that moved shows up
as a changed image; nothing else can.

That diff-the-stylesheet test still applies, unchanged, to the **file split**, where no rule may be
edited at all.

**D8 — purge before splitting.** The packet orders these the other way. Splitting is the step whose
whole correctness argument is "the emitted stylesheet did not change", and that argument is
strictly easier to make about less code; deleting dead rules first means the split moves fewer of
them. The purge's own proof — that the emitted diff contains only deletions, and only of rules on
the evidence list — is also easier to read against one file than against ten. So: purge, then
split, then tokenize, then add the dark overrides.

**D9 — the split is ten files, cut on the section boundaries the inventory found.** The inventory
reports the file is cleanly ordered and that no `@media` block spans a section boundary, which is
what makes a purely mechanical split possible. `theme.customCss` takes an explicit array, in this
order, because PostCSS resolves `@import` in ways that would reorder cascade:

`tokens.css` · `base.css` · `shell.css` (header, nav, footer, search) · `prose.css` (docs and blog
frames, tables, the reading measure) · `home.css` · `instruments.css` (score-space, code blocks,
snippets, claim graph) · `charts.css` (charts, showcase, diagnostics, walkthrough components) ·
`components.css` (editorial panels, filters, API, benchmarks) · `lab.css` · `responsive.css`
(the five global `@media` blocks; section-local ones travel with their section).

The load-bearing comments at lines 29, 230, 252, 316, 558, 563, 587, 684, 744, 793, 813 and 825
travel with the rules they explain. Several of them record a measured contrast ratio and are the
only record of why a value is what it is; losing one to a careless cut would silently re-open a
fixed accessibility defect.

**D10 — a demo reproduces the page's committed number; it never introduces a new one.** Before
activation `LiveFit` renders the result already committed to `snippet-outputs.json` or
`walkthrough-data.json`. After activation it renders the reader's own run beside it, labelled as
theirs. This is what makes live computation compatible with the S8 fact contract rather than a
hole in it: a number computed in the reader's browser after an explicit click is the reader's run,
not a published claim. It is also the better demonstration — "you just reproduced the number on
this page" is a stronger statement than "here is a number".

Three layers keep the Pyodide import out of ordinary route chunks: `LiveFit` (route chunk; React,
the committed result, one button), `LiveFitRunner` (reached only by `await import()` in the click
handler; this is the chunk carrying the `new Worker(new URL("./lab.worker.ts", import.meta.url))`
reference), and `LiveFitProvider` in `AppShell`, allowing one activated demo per page. `useState`
plus `void import(...)`, not `React.lazy` with `Suspense`, which fights Docusaurus's server render.

Three placements and only three: the home page's loss-identity beat, `/get-started` beside the
first fit, and `/walkthroughs/ratios`. Each further demo multiplies cold-start end-to-end time and
accessibility surface, and these three already cover front door, first fit and real data.

**D11 — the runtime client is a module singleton, and the fallback is written down now.**
`useLabRunner` creates one `Worker` per hook instance and terminates it on unmount, so two
activated demos in one tab would hold two Pyodide heaps — roughly 15 MB of runtime each, and a
genuine out-of-memory risk on a phone. `runtimeClient.ts` takes ownership of creation, refcounting,
routing by `runId` and termination; `useLabRunner` becomes a subscriber whose exported interface —
`{cancel, error, progress, result, run, stage, state, warm}` — stays byte-identical, so
`website/src/pages/lab.tsx` is untouched and the four end-to-end tests that drive `lab.run`,
`lab.cancel`, `state` and `warm` keep their meaning.

One correction to the packet: it says "five e2e tests pin `useLabRunner`". The inventory finds
**four** that actually drive the hook (fixture run, native wheel run, validation/cancellation, and
the warm-second-run FlowCyt test); the fifth, `?job=ratios`, pins the preset seeding and never
calls `run`. There are no unit tests for the hook at all — it is pinned exclusively by Playwright
against the real worker. That raises the cost of getting the singleton wrong, so it gets a unit
test of its own state machine with a mocked `Worker`, which is new coverage either way.

Only one run may be in flight; a second activation is refused rather than queued. If this is not
green by mid-session the fallback ships instead: per-mount workers, relying on `LiveFitProvider`'s
one-active-demo guard, which gets most of the benefit for none of the risk.

**D12 — `docs.yml` is deleted, not reduced.** Its `build` job runs `mkdocs build --strict`; its
only other content is the frozen `upload-pages-artifact` (`path: site`) and the frozen `deploy`
job, both `if: false` since the S6 migration. `portal-preview.yml` already runs
`uv run mkdocs build --strict` as one of its steps, so once it becomes the publishing workflow the
strict reference build runs there on every pull request and every push to `main`. Keeping a second
workflow that also builds MkDocs means two files can disagree about how the reference is built,
for no coverage gain. `main` has no branch protection, so no required-check name is lost by the
deletion — that was verified against the API, not assumed.

`portal-preview.yml` becomes `site.yml`: it gains `push: branches: [main]`, an
`upload-pages-artifact` step with `path: .pages-preview` — the assembled tree, portal at the root
and MkDocs under `reference/`, not the bare MkDocs `site/` the frozen step would have uploaded —
and a `deploy` job gated on `github.ref == 'refs/heads/main'`. Pull requests keep the artifact
upload and get no deployment. GitHub Pages is already `build_type: workflow` with no CNAME, so
nothing outside the repository has to change.

**D13 — the deployment stays host-agnostic.** `website/src/lib/site.ts` already centralizes
`SITE_BASE`, and the eventual move to a custom domain changes it, `docusaurus.config.ts`'s
`baseUrl`, and `mkdocs.yml`'s `site_url`. Nothing in the publishing path may add a fourth place
that encodes `/scorequant/`. The github.io URL must keep resolving after any such move, because
the published package advertises it as both `Homepage` and `Documentation`; that makes the later
move a redirect, not a replacement. Recorded here so the workflow is not written in a way that
assumes the current host.

**D14 — the home design pass makes the six beats speak one structural vocabulary.** S10 handed
over two known gaps. Measured against the built page, they are worse than "gaps" and there is a
third:

- Beat 1 (`.home-lede`, capped at 760px) leaves roughly 620px of the 1376px frame empty.
- Beat 5 (`.home-doors`) is a stacked list whose paragraphs are capped at the 72ch reading measure,
  so all three doors sit in the left half and the right half is empty again.
- Beat 6 (`.home-exits`) is two bordered boxes — a card grid, which is exactly what the front-door
  brief said the page should not end on.

The three sibling blocks also disagree with each other: beat 4 (`.home-choice`) is a borderless
two-column layout with a top rule, beat 5 is a one-column ruled list, beat 6 is cards. That
inconsistency is the actual defect; the empty halves are its symptom.

The pass unifies them on the vocabulary the page already uses well — the rule-separated row, which
is what makes `.home-measure` the best block on the page — and does not introduce a new one:

- Beat 1 gains a right column carrying what the page currently never states: what ScoreQuant *is*.
  A new reader gets a problem statement and no product identification anywhere in the first screen.
  The column holds the name, one sentence of what the library does, the install line, and the
  runtime it accepts. Not a slogan and not a call to action — an identification, which is the one
  job a front door must do that this page was not doing.
- Beat 5 keeps its ruled rows but each row becomes a two-column grid, heading left and prose right,
  echoing `.measure-row`. It then reads as the definition list it actually is, and it fills the
  frame.
- Beat 6 loses its borders and adopts beat 4's top-ruled treatment, so the page ends the way it
  argued, without a card in sight.
- `.home-section`'s fixed `100px` block padding becomes fluid, closing the roughly 200px of dead
  space between beats at desktop width without touching the mobile rhythm.

Constraint carried over from S10 decision D7: `index.tsx` may still contain no numeric literal, so
the identity column's copy carries no version string and no digit of any kind.

**D15 — each demo re-runs a problem the page already publishes, and the three placements were
chosen by what the browser runtime can actually reproduce.** The Lab's worker protocol accepts a
`LabProblem` — scores, weights, a bin budget and a criterion — not arbitrary Python. So a demo can
only reproduce a number that *is* a partition fit on a score table the page can hand it. That
constraint, not taste, picks the placements:

- **Home, the loss-identity beat.** `ScoreSpace` already renders a committed score-space fixture
  and already accepts a `scenarioOverride` prop and a controlled bin count, so the seam exists. The
  demo re-fits that same fixture at the same budget and shows the reader's retention beside the
  committed one.
- **`/get-started`, beside the first fit.** The `first-fit` cell is a `LabProblem` in all but name:
  1,200 two-dimensional scores from a seeded generator, unit weights, five bins, D-optimality. The
  only missing piece is the score table itself, which lives only inside the generator's Python
  namespace — so `generate_snippets.py` gains one output, writing that cell's scores as a static
  JSON fetched on demand. Same program, same run, one more consumer; this keeps the captured-output
  contract intact rather than introducing a second source for the same numbers.
- **`/walkthroughs/ratios`.** `walkthrough-scores/ratios.json` already exists and the `?job=ratios`
  preset already proves the browser can run it.

Deliberately not flowcyt, hep or michelson: each additional demo multiplies cold-start end-to-end
time and accessibility surface, and these three already cover the front door, the first fit and
real data.

One semantic check the implementation must make rather than assume: the committed numbers are
`geometric_mean_retention` from a `train_report`, and the worker returns a `retention` field. If
those are not the same quantity, the demo must display the one that actually corresponds, or say
plainly that it is showing a different one. A demo that invites the reader to compare two numbers
must be comparing two numbers.

**D16 — dark mode overrides the palette tier, not the semantic tier.** The semantic tokens alias
palette tokens, so overriding Tier 1 flips Tier 2 for free *and* flips the roughly twenty rules
that still name a palette token directly. Overriding Tier 2 alone would have left those twenty
rules rendering light ink on a dark ground. Tier 3 is deliberately not overridden: that is decision
D5 made mechanical.

The dark values were chosen against measured contrast rather than by eye, and every one clears the
light-mode equivalent:

| pair | light | dark | threshold |
|---|---|---|---|
| body text on the page ground | 12.6:1 | 9.98:1 | 4.5 |
| muted text | 6.4:1 | 7.69:1 | 4.5 |
| faint text | 5.27:1 | 6.92:1 | 4.5 |
| link on the page ground | 4.58:1 | 8.44:1 | 4.5 |
| `--accent-strong` on `--accent-quiet` | 7.20:1 | 8.66:1 | 4.5 |

The two separator rules measure 1.58:1 and 2.03:1 in dark against 1.23:1 and 1.59:1 in light. They
are below 3:1 in both, and that is correct rather than a defect: WCAG's 3:1 applies to user
interface components and to graphics needed to understand content, not to a decorative hairline
between rows. The light values are the ones the axe scan already accepts, and dark is strictly
better than light on both. Recorded because it is exactly the kind of number a later reader would
try to "fix".

One consequence to watch and check on the screenshots rather than assume: with the page ground
dark, the deliberately-dark instruments no longer separate from the page by contrast alone, so they
need a border to keep reading as distinct panels. That adjustment is confined to
`[data-theme="dark"]`.

**D17 — the ratios demo compares two different quantities, and says so.** D15 required checking
that a demo's live number and its committed number are the same quantity rather than assuming it.
Checked empirically, not by reading code, and the three placements do not agree:

- **Home.** The browser's fit reproduces the committed retention *bit for bit* at three, four and
  five bins. `LabResult.retention` is `train_report.geometric_mean_retention` on this path.
- **`/get-started`.** Committed `0.6987764888683643`, browser `0.6987764888683644` — a
  sixteenth-digit difference, and both format to the four decimals the page prints. This is exactly
  the headroom S10's format-spec decision was chosen to leave.
- **`/walkthroughs/ratios`.** **Not the same quantity.** The committed number is a rule fitted on a
  *separate training sample* and then evaluated on the held-out table. What the browser can do with
  that table is fit a fresh D-optimal partition directly on it. Those differ by construction, and
  they measure 0.9700 against 0.9727.

The wrong response would have been to quietly show them side by side under one heading, which is
the failure the "compare like with like" rule exists to prevent. The demo instead labels them as
what they are — a frozen training-fitted rule evaluated out of sample, against a fresh fit on this
exact table — and says in the activation text that a fresh fit on held-out data is expected to
score slightly higher than a rule that never saw it. That is a more honest page than one showing
two numbers that happen to match, and it teaches the distinction the walkthrough is about.

**D18 — the split ships, and the packet's "empty emitted diff" criterion cannot be met. Here is
why, and what was checked instead.** The split moved 1,038 lines into ten files without editing a
rule; the line ranges partition the original with no gap, overlap or duplicate. But the emitted
stylesheet is not byte-equivalent, and the reason is structural rather than a mistake in the move.

Docusaurus runs PostCSS's custom-property fallback generator **per CSS module, before the
`customCss` files are concatenated**. While every rule lived in the same file as the `:root` block,
that plugin could resolve each `var()` statically and emit a literal fallback ahead of it
(`color:#07142d; color:var(--text)`). Once the tokens live in their own file, no other file's
module-local pass can see `:root`, so the literal is no longer generated. The surviving `var()`
declaration is unchanged in every case.

This is not a placement error and no ordering fixes it: it reproduces for *any* split that puts the
tokens in a separate entry, which is what the packet asks for. The only ways to restore the literals
would be to duplicate `:root` into all ten files or to modify the webpack/PostCSS pipeline, neither
of which is a pure move.

So the criterion was replaced with a stronger claim, and that claim was checked rather than
asserted: **every lost declaration is a static fallback superseded by a surviving `var()` on the
same selector and property.** Comparing the two emitted stylesheets as sets of atomic
`(selector, property, value)` facts gives 323 losses and 323 of them explained that way — zero
unexplained. Three declarations appear that did not before, all Infima `kbd` defaults the minifier
could no longer prove were unconditionally overridden; the portal's own `kbd` rule still overrides
them by source order.

The practical consequence is nil. A browser without custom-property support would previously have
received those fallbacks; it would also be unable to render dark mode, which is implemented purely
as `:root[data-theme="dark"]` custom-property overrides, and unable to render the token
architecture the portal has used since before this session. The site has no such supported viewer.

Recorded at length because the packet states the empty diff as a done criterion, and a future
reader finding it unmet deserves the reason rather than a shrug.

**D19 — the deployment gets an ADR, and the sweep for stale prose found three older bugs.**
The repository's contract requires an ADR when a decision is durable, and turning the deployment on
is exactly that: it discharges a condition ADR 0019 imposed ("Deployment remains preview-only until
separately authorized") and reverses a sentence in ADR 0025 ("Deployment does **not** change here").
[ADR 0026](../adr/0026-one-workflow-publishes-the-site.md) records the arrangement — one workflow,
a pull request that builds and uploads, a push to `main` that publishes — and the two reasons that
are easy to lose: `docs.yml` was deleted rather than un-frozen because un-freezing it would have
deployed `site/`, the MkDocs build alone, overwriting the assembled root and taking every portal URL
down with it; and the deployment stays host-agnostic because `scorequant 0.1.0` advertises the
github.io URL on PyPI and a spent version number cannot be reissued, so a custom domain later is a
redirect *from* that URL, never a replacement of it.

The older ADRs are annotated, not rewritten. ADR 0019's and ADR 0025's status blocks gain forward
pointers, and the now-false sentence in ADR 0025 gets its correction beside it rather than in place
of it — an ADR is a record of what was decided when, and editing the decision away would destroy the
only thing it is for.

Then a grep for the two deleted workflow names, which was expected to find nothing interesting,
found five references — and three of them were bugs older than this session that the launch would
have published:

- `README.md`'s Documentation badge pointed at `docs.yml`. With that workflow deleted the badge
  renders as "no status" on the repository front page **and on the PyPI project page**, which is the
  first thing a reader of the released package sees. Now `site.yml`.
- `docs/playbook.md` told a new contributor the dev server runs at `/scorequant/portal/`. That has
  been wrong since S6 moved the portal to the site root.
- The same page's "previewing both sites" section described the assembled tree as MkDocs at the root
  with the portal at `/portal/` — exactly backwards since S6 — and said `portal-preview.yml` only
  uploads an artifact.
- It also stated that `global.css` is one file holding every page's styles. Replaced not with a list
  of ten filenames but with the rule that actually bites: they are listed in **cascade order** in
  `theme.customCss`, there are no CSS modules, and order is the only thing resolving equal-specificity
  collisions.
- `docs/roadmap.md`'s M10 status still called root-site promotion a future milestone.

Worth recording because of what it says about the shape of the mistake. S11 deleted four things —
`global.css`, `manageHead`, and the two workflows — and every one of them was still named somewhere
in prose that no test reads. Deleting a file is not the same as retiring it, and the only thing that
closes the gap is a grep for the old name at the moment of deletion.

## Closing report

Ran 4 September 2026 on branch `consolidation-s11-portal-design-and-launch`, after S10 merged as
PR #42. The session finished the surface — one shell, a semantic colour system with a real dark
mode, three demos that run in the reader's browser, a purged and split stylesheet, and a single
publishing workflow. It stopped short of publishing; that awaits the owner's go-ahead, and the
reason is recorded at the end.

**One shell, which everything else depended on.** `useColorMode()` needs the provider Docusaurus
mounts inside `@theme/Layout`, and the plain page routes rendered `AppShell` directly, outside it.
The fix is a replacement rather than a wrapping: the four page routes — four, not the five the
packet says, because S10 deleted `docs.tsx` — now render `@theme/Layout`, which already renders
`AppShell`. Nesting would have mounted two headers, two footers, two search dialogs and two
`<main id="main-content">`, and the existing landmark test would not have caught it on the two
routes that matter most, because its loop covered neither the home page nor the Lab. Both were
added. `manageHead` is gone in favour of the pattern upstream already uses — checked in the
installed `@docusaurus/theme-classic` rather than assumed: stock `Layout` renders `PageMetadata`
first and lets pages nest their own inside it.

**Dark mode does not recolour the site; it promotes a palette the site already owned.** The portal
has always carried a complete dark palette, used for the surfaces that represent the machine — the
score space, the code blocks, the whole Lab. Dark mode makes that ground the page ground and leaves
the instruments alone, which is why the design survives the flip instead of inverting into
something unrecognizable. Mechanically: three token tiers, with the dark override applied to the
palette tier so the semantic layer and the rules still naming a palette token directly all follow.
Light mode came through the token rewrite **pixel-identical** on every route at two viewports,
which is the only check that actually proves no colour moved.

**Three demos, and the rule that keeps them honest.** A demo reproduces a number the page already
publishes; it never introduces a new one. Before the click the reader sees the committed result;
after it, their own run beside it, labelled. Home reproduces the committed retention bit for bit.
`/get-started` agrees to the sixteenth digit — inside the headroom S10's format-spec decision was
chosen to leave. `/walkthroughs/ratios` does **not**, and that is the most useful thing the demos
turned up: the committed number there is a rule fitted on a separate sample and evaluated out of
sample, while a browser fit on the displayed table is a fresh partition. 0.9700 against 0.9727. The
page says so, instead of showing two numbers under one heading and implying they are the same
measurement.

The runtime behind them is now a tab-wide singleton: `new Worker` appears exactly once in the
codebase, and `useLabRunner` is a subscriber whose exported interface is unchanged, so `lab.tsx`
was not touched. It gained the unit tests it never had — the hook was previously pinned only by
Playwright against a real Pyodide boot.

**What was verified.** `ruff check` clean; `ruff format --check` 257 files; `ty check src` clean;
`pytest -n auto` **553 passed**; `pytest tests/test_float32.py` 4 passed; `uv build` produced both
artifacts; `mkdocs build --strict` exit 0. `pnpm validate` clean with **118** vitest tests, against
71 at S10 and 52 at S6; `pnpm test:e2e` **14 passed, 6 skipped, 0 failed** across desktop and
mobile; `pnpm assemble:site` reports **50 redirect stubs verified**, with the manifest still at
50 + 3 unstubbed = 53.

Two guards were proved to bite rather than assumed to. The contrast test: a dark token was moved to
a failing value, and it failed naming the exact pair and theme. The demo invariant is asserted in
**both** directions — zero heavy-runtime requests on load, and at least one after the click — because
an invariant only ever asserted in the negative is satisfied by the feature being broken.

**Ten things found wrong.** Six were pre-existing and had nothing to do with this session's changes:

1. `.button-secondary` was dead. S10's closing report recorded that it survives because `lab.tsx`
   uses it; only `.button-primary` does, and `.button-secondary` appeared nowhere in the built site.
2. Chrome's CSS coverage marks a whole rule used when any selector in it matches, so twelve dead
   classes grouped with live ones read as used. Only grepping the built site distinguishes them.
3. Three classes were falsely dead — the route list under test had a blog index but no blog *post*,
   where they alone render. The list gained a post and the 404 route.
4. **The Lab page scrolled horizontally on every build back to the S10 baseline**, 1493px in a
   1440px viewport. `.lab-field input` outranks the `.visually-hidden` utility, so the accessibly
   hidden file input took `width: 100%` of the initial containing block. Dark mode is what made it
   visible, as a light strip beside a dark page.
5. **A 3.1:1 defect inside the Lab**, in both themes: four rules painted a page ink onto an
   instrument ground. They render only in conditional branches, which is why neither the axe scan
   nor any screenshot pass had ever reached them. Now 7.09:1.
6. `AppShell` kept `title` and `description` as required props after the refactor stopped reading
   them.

Four were introduced by this session's own work and caught by its own new checks:

7. Four colour pairs could not flip. A rule pairing `color: white` with `background: var(--accent)`,
   or a literal light tint with a token that flips, breaks when only one half moves — the button ink
   measured 2.2:1. Four new roles (`--on-accent`, `--tint-accent`, `--tint-good`, `--tint-bad`) fix
   it; those pairs now measure 8.70, 8.28, 6.24/8.94 and 8.08:1.
8. **Dark mode reintroduced exactly the defect class S8 fixed.** Prose links on all six docs routes
   fell through to Infima's default styling: 3.80:1 against surrounding text in light, which passes,
   and **1.97:1 in dark**, which fails `link-in-text-block`. The dual-theme scan caught it on its
   first run, which is the entire argument for scanning both themes.
9. A demo would have compared two different quantities — item three above.
10. Scanning immediately after the theme toggle produced phantom violations from the sticky header's
    `backdrop-filter` caught mid-repaint, on an element whose steady-state pair measures 7.69:1.
    Diagnosed as flakiness and fixed with a settle, rather than suppressed as a rule exception.

**What was cut or left open.**

The packet's criterion that the emitted stylesheet be unchanged across the file split **cannot be
met**, and D18 records why at length: Docusaurus runs PostCSS's custom-property fallback generator
per module, before the `customCss` files are concatenated, so once the tokens live in their own file
no other file can resolve a static fallback. The criterion was replaced by a stronger, checked claim
— every one of the 323 lost declarations is a static fallback superseded by a surviving `var()` on
the same selector and property, with zero unexplained losses.

`/lab` still keeps its own scoped palette rather than following the site theme; the token rewrite is
what reduces that to a one-block change later. Demo activation does not consult
`navigator.connection.saveData`. Neither was in scope.

**CI caught a defect the local run could not.** The first pull-request build failed, and the
failure is worth recording because of its shape: the home test packed nineteen navigations and
**sixteen axe analyses** — eight routes times two themes, each with a settle — into one test with
the default 30-second budget. S11 is what doubled it, by scanning every route in both themes
instead of once. It passed on this machine and timed out on a CI runner, on both projects and both
retries, which is the least useful way for a suite to fail: the machine that gates the merge
disagrees with the machine the work was done on, and the failure names a timeout rather than the
thing that is actually wrong.

The fix is not a longer timeout. That test was three contracts wearing one name — the home page's
content, the one-landmark-per-route count, and an accessibility sweep the name never mentioned — so
it became three: the home assertions, the route walk with its no-runtime check, and **one test per
scanned route**, generated in a loop. Every assertion survives unchanged. Each route now gets its
own budget and the workers run them in parallel, so the full suite went from a single serial
bottleneck to 32 passing tests in 14 seconds locally, and the accessibility scans are 1–4 seconds
each. A test that cannot fit in a budget is usually a test that is doing more than one job.

**The deployment was authorized and carried out.** Both blockers cleared on 4 September 2026: the
owner deleted `docs.yml` and `portal-preview.yml` — the sandbox had refused both, and until they
were gone a pull request would have built the site twice — and gave the explicit go-ahead to
publish. Publication is an authorized action rather than a merge side effect, which is why it waited
for that sentence and not for the merge. `site.yml` deploys on the push to `main` that merges this
work, so the first deployment is this session's, and ADR 0026 records the decision.

**The one thing the next session must know.** The site is live, and the check that matters is the
one no local run could perform: that all 53 pre-cut MkDocs URLs resolve against the live host, spot-
checked from `website/redirects.json`. That check is recorded in S9's closing report rather than
here, because it can only run after this branch is merged and deployed — S9 should treat it as an
inherited obligation and not assume S11 discharged it.

Note also that `site.yml` is now the only place `mkdocs build --strict` runs. `docs.yml` used to run
it on every push to `main`; if a future change moves the reference build out of `site.yml`, nothing
else will catch a broken reference link.
