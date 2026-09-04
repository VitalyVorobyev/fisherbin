# S11 — Portal design pass, inline demos, and launch

**Workstream:** W3 · **Needs:** S10 · **Parallel with:** — · **Status:** queued

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

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
