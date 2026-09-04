# S10 — Portal front door: home, get-started, captured outputs

**Workstream:** W3 · **Needs:** S8 · **Parallel with:** — · **Status:** done

## Goal

Write the front door last, because a front door summarizes everything behind it and should quote
that work's real numbers rather than promise them. Today the home page is a landing page — hero
slogan, a four-box proof strip, paired call-to-action buttons, three-card grids — and `/docs` is a
three-tab widget that shows a snippet per door and never its output or its meaning, so a reader
cannot get from the page to a working analysis. This session replaces both: a home page that
teaches the problem with a measured comparison instead of asserting a benefit, and a
`/get-started` that walks the first fit through to the interpretation of every number it prints,
with each output captured from a run rather than typed. Then it turns the site on. Done means no
route carries a slogan, every displayed output is captured, and the root deployment is live at a
URL recorded in the closing report.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S08-the-four-walkthroughs.md`: S8 closing report; the four walkthroughs this
  front door hands readers into, and the real numbers it may quote.
- `docs/programme/S06-portal-topology-and-reference-cut.md`: S6 closing report; the topology, and
  the scratch file holding the narrative material retired from `docs/motivation.md`,
  `docs/three-doors.md` and `docs/user-workflow.md`. `/get-started` is built from that material,
  not written from scratch.
- `website/src/pages/index.tsx`: the current home page, replaced.
- `website/src/pages/docs.tsx`: the current `/docs`, replaced by `/get-started`.
- `website/src/components/ScoreSpace.tsx`: the existing score-space visual, reused on the home
  page.
- `website/src/lab/useLabRunner.ts`, `website/src/pages/lab.tsx`: the Lab, whose prefilled-job
  mechanism S8 established and this session reuses inline.
- `docs/usecases/flowcyt/quantization.md` and the FlowCyt evidence JSON: the source of the
  measured naive-versus-optimal comparison the home page opens on.
- `examples/baselines.py`: `rectangular_observation_bins`, `equal_frequency`, Euclidean k-means —
  the naive baselines that comparison is measured against.
- `tests/test_portal_snippets.py`: the harness, extended in S8 to MDX, extended here to the
  captured-output pages.

## Deliverables

**Home page**, with no hero slogan, no proof strip, no paired call-to-action buttons, and no
three-card grid. Six beats, in order:

1. The problem in plain language, before any ScoreQuant vocabulary. `docs/motivation.md` §1 is the
   best statement the project has ever written of it and is the starting text.
2. A measured before/after, not a claim: naive gates versus ScoreQuant bins on the FlowCyt data,
   both D-efficiencies, the real figure, and a link into `/walkthroughs/flowcyt` for how it was
   obtained. The page's first evidence is a number someone can check.
3. What the library does: the loss identity in words, then in one equation — binning can only lose
   information, and the loss is the within-cell scatter of the score — with the existing
   `ScoreSpace` visual.
4. The two tasks as the reader's own decision, phrased as the question `docs/user-workflow.md`
   already asks: will you ever label an event that is not in this table? Each answer links to its
   walkthrough.
5. The three doors as "what do you already have", with the estimated-ratio caveat stated on the
   page rather than deferred.
6. Two exits, both concrete: run it now with nothing installed (Lab, prefilled), or install it and
   follow `/get-started`.

**`/get-started`**, built from the retired `docs/user-workflow.md` material, as a single
continuous path rather than a tab switcher:

- Install, and what the runtime choice means (JAX default, NumPy portable, X64 the application's
  call).
- The smallest real fit, then **its actual printed output**, then what each number in that output
  means — the retention spectrum and its geometric mean, effective rank against the parameter
  count, bin weights and effective sample sizes, `exchange_stable` with `best_remaining_gain`.
- The same problem as a reusable rule: `fit_quantizer`, `predict_scores`, `Quantizer.save` and
  `load`, and why prediction is explicit.
- The one sanctioned crossing, `compile_quantizer`, and the refusal that guards it — including
  what a `RefusalError` message's bracketed counterexample id points at.
- The diagnostics checklist to run on any fit, as a closing summary.
- A Lab affordance beside the first fit.

**Captured outputs.** `website/scripts/generate_snippets.py`, run under `pnpm generate`: executes
each `/get-started` snippet and records its printed output into `website/src/generated/`. The page
renders the captured text; it never contains an output literal. Showing outputs is this session's
main facilitation win and its main drift risk, and this is the mechanism that removes the risk by
construction.

**Navigation.** The final nav: Get started · Walkthroughs · Lab · API · Research · Benchmarks ·
Reference · Blog. Eight entries, each a verb or a place. `docs.tsx` deleted or left as a redirect
stub to `/get-started` (see Open decisions).

**Slogan audit.** A haiku pass over every route, flagging every sentence that asserts a benefit
without either explaining a mechanism or citing a measured number. The before/after list goes in
the closing report.

**Handed over by S6 (decision R1).** This session also retires `docs/motivation.md` and
`docs/user-workflow.md`, because this session writes the portal home and `/get-started` that
replace them. `motivation.md` has no code fences and retires cleanly. `user-workflow.md` carries
**9 executed `python` fences**; they move into `/get-started`, whose whole point is showing each
snippet with its captured output, and the fence count before and after goes in the closing report.
On retirement, remove both from `tests/test_readme.py`'s `_FRONT_DOOR`, add them to
`test_retired_pages_are_gone`, re-point every inbound link the S6 closing report lists, and change
their `website/redirects.json` entries from `reference/...` to the portal pages that replace them.
`docs/user-workflow.md` also holds one of the seven hand-copies of the criterion/solver table
(S6 decision R3 kept it because it is advice rather than a matrix); check whether `/get-started`
should consume the generated fragment instead.

## Done criteria

- The home page carries none of: a hero slogan, the proof strip, paired call-to-action buttons, a
  three-card grid. Its first piece of evidence is a measured comparison with a link to its
  derivation.
- No route contains a sentence the slogan auditor flags; the before/after list is in the closing
  report.
- Every snippet on `/get-started` is executed by `tests/test_portal_snippets.py` and asserts a
  result object, and every output the page displays comes from `website/src/generated/`. A `grep`
  for output literals in the page source finds none.
- `website/src/pages/docs.tsx` is deleted outright (see Open decisions).
- Nav is the eight final entries; navigation tests match.
- Full handoff gate green, plus `cd website && pnpm validate` and `pnpm test:e2e`.
- roadmap M12 table shows S10 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Write the home page copy and the `/get-started` prose from the retired narrative material — plain language, no slogans, every claim either a mechanism or a measured number | orchestrator inline, one beat at a time | page copy |
| Measure the naive-versus-optimal FlowCyt comparison the home page opens on, from the committed evidence and `examples/baselines.py` | sonnet | numbers plus their generator keys |
| Implement the two routes in TSX against the written copy | sonnet | TSX diff |
| Build `website/scripts/generate_snippets.py` and wire it into `pnpm generate` | sonnet | script and generated-output diff |
| Extend `tests/test_portal_snippets.py` to the `/get-started` snippets | sonnet | test diff |
| Final nav cut, delete or stub `docs.tsx`, update navigation tests | sonnet | TSX diff |
| Slogan audit over every route | haiku | flagged and removed sentences |
| Run gates and e2e, report failures verbatim | haiku | gate output |

Never a `fable` subagent (`docs/programme/README.md`, budget rule). The front-door prose is the
session's whole point and is written inline by the orchestrator, one beat at a time, not delegated.

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
```

## Design decisions

Written before any code, per the orchestrator contract. The three decisions the packet left open
are answered first, then the decisions this session added.

**D1 — `docs.tsx` is deleted outright, with no redirect stub.** The packet's argument for a stub
was that `/docs` is the route most likely to have been linked externally. That premise is false,
and was checked rather than assumed: `.github/workflows/docs.yml`'s Pages artifact has been
`path: site` — the MkDocs build alone — from the repository's first commit (`d43cae9`) through
the S6 freeze. The portal has never been served at any URL, so `/scorequant/docs/` has never
resolved and no external link to it can exist. A stub would redirect from a URL that has only
ever returned 404, at the cost of a route, a build artifact, a sitemap entry and a line in the
navigation test forever.

One consequence must be handled in the same commit: `tests/test_portal_snippets.py` builds its
snippet list at *module import* and ends in `assert escaped_snippets`, so deleting `docs.tsx`
without replacing that extractor turns the file into a collection error rather than one failing
test.

**D2 — the two publishing workflows are S11's problem.** Deployment moved out of this session
entirely; see `docs/programme/S11-portal-design-and-launch.md`.

**D3 — the captured-output generator runs in-process, in one shared namespace.** The packet posed
this as in-process versus a subprocess per snippet, but subprocess-per-snippet is wrong on the
merits rather than merely slow: the snippets share one namespace today, exactly as
`docs/user-workflow.md` says ("Every snippet runs, and they share one namespace"), and a page that
teaches a workflow must keep that. In-process also matches `tests/test_docs_snippets.py`. The one
thing `contextlib.redirect_stdout` cannot capture is a C-level write; if that pollutes capture in
practice, escalate to **one subprocess for the whole program** with file-descriptor redirection,
never one per cell.

**D4 — snippets are single-sourced from one runnable program.** `website/scripts/get_started_program.py`
is a genuine top-to-bottom Python file divided by `# %% cell: <id>` markers, so a reader can run it
and get the page's output. Three consumers share that one source: the generator (executes cells in
order, captures stdout), the page (renders `<Snippet id="..."/>`), and
`tests/test_portal_snippets.py` (executes the same cells and asserts a result object). This makes
two things true by construction instead of by check — the page cannot show an output no run
produced, *and* it cannot show code no run executed. Rejected: leaving fences in the MDX and having
the generator parse the page, because a fence and its adjacent output block can silently reorder.

**D5 — printed numbers are computed on the NumPy backend at float64.** Every cell that prints a
number passes an explicit `sq.ExecutionConfig(backend="numpy", precision="float64", device="cpu")`,
visible in the snippet, seeded with `np.random.default_rng(21)`. This removes XLA from the
determinism question, and it is the same configuration the browser Lab runs, which is how "JAX
default, NumPy portable, X64 the application's call" gets taught concretely rather than asserted.
Format specifications live in the snippet (`f"{value:.4f}"`, never a bare `repr` of a float or an
array), leaving roughly 1e-4 of headroom against last-bit BLAS ordering differences. A cell that
would print something genuinely unstable prints a stable projection —
`bool(partition.exchange_stable)`, not a raw iteration count.

**D6 — `/get-started` is a third `plugin-content-docs` instance**, at `website/get-started/index.mdx`
with `id: "getstarted"` and `sidebarPath: false`, matching the two instances S6 created. It
inherits four mechanisms that already exist and are already tested: the swizzled
`src/theme/DocItem/Layout` table of contents (which S6 built precisely because the stock one
crashes in this shell), `src/theme/DocRoot/Layout/Main` — which is *why* docs routes have exactly
one `<main>`, a count the e2e suite asserts on every route — the keyboard-reachable table in
`MDXComponents.tsx`, and the MDX prose pipeline the numeric guard already parses. Rejected: an MDX
*page* route, because `@theme/MDXPage` renders its own `<main>` inside AppShell's and would need a
fourth theme swizzle to stay axe-clean; and TSX, because it recreates exactly the fragile
template-literal extraction this session is deleting.

**D7 — the home page's numbers are guarded by a whole-file numeric-literal ban.** The prose guard
in `tests/test_walkthrough_facts.py` strips JSX expressions and tags, so applied to a TSX file it
would strip nearly everything and prove nothing. Instead `website/src/pages/index.tsx` may contain
no numeric literal at all outside a short allowlist with recorded reasons, which forces every
displayed number through `factsFor("home")`. This is achievable only if the rewritten page carries
no inline `style` props; today's page has two, and the redesign wants them gone regardless.

**D8 — one fact generator, not two.** The `home` and `get-started` facts become new page keys in
the existing `website/scripts/generate_walkthroughs.py` table, and its module docstring and the
`FACTS` comment are updated in the same commit. Splitting the contract across a second generator
is precisely the drift the contract exists to prevent.

**D9 — the criterion/solver table stays hand-written.** S6 decision R3 kept `user-workflow.md`'s
copy because it is advice about when to choose a solver, not a compatibility matrix. That
judgement is unchanged by the move, so `/get-started` keeps the prose and links to the generated
matrix at `reference/method/` rather than consuming the fragment. Recorded here so the next reader
does not re-open it.

**D10 — the retirements re-point redirects rather than dropping them.** Deleting
`docs/motivation.md` and `docs/user-workflow.md` removes `reference/motivation/` and
`reference/user-workflow/` from the assembled tree, and `website/scripts/assemble-site.mjs`
resolves every redirect target, so this is a guaranteed build failure unless handled in the same
commit. `motivation/` re-points to the site root and `user-workflow/` to `get-started/`, which
keeps `sourceSitemapCount === unstubbed + redirects` at 53 and makes both entries portal-targeted
like the `three-doors/` entry S8 added.

## Closing report

Ran 4 September 2026 on branch `consolidation-s10-portal-front-door`. The session's own first act
was a re-scope: the owner split the remaining portal work in two, so S10 kept the front door and a
new **S11** took the visual design pass, the inline demos and the deployment flip. The deployment
material moved verbatim into `docs/programme/S11-portal-design-and-launch.md` rather than being
rewritten, and `docs/programme/README.md` records the rule that motivated the split — *a surface is
published by the session that finishes it*, the sibling of S6's retirement rule.

**What was delivered.**

The home page no longer sells. It opens by stating the problem in plain language — the text is
`motivation.md` §1, which is the best statement the project has ever written of it — and its first
evidence is a measured comparison a reader can check: on the FlowCyt data at eight bins, three
standard binning rules retain 0.0704, 0.0378 and 0.0223 of the Fisher information about the
population fractions, against ScoreQuant's 0.9853, all held out. The hero slogan, the four-box
proof strip, the paired call-to-action buttons and both card grids are gone.

The comparison is quoted against the **strongest** of the three naive rules, not the weakest. This
was the session's one genuinely contestable choice. The obvious headline was the 0.0223 rectangular
grid, which flatters the method most; the S7 precedent says the opposite, because a number measured
against the worst available baseline reports the baseline's difficulty rather than the method. All
three are published side by side so a reader can see the spread.

`/get-started` replaces the `/docs` tab widget, which showed code and never its output. It is one
continuous path: install and what the runtime choice means, the smallest real fit and what each of
its four numbers means, the spectrum and the occupancy check, certifying labels you did not
produce, the same problem as a reusable rule with save/load, a baseline worth running, the one
theorem-backed crossing and the refusal that guards it, and three things a reader needs next.

**No output on that page is typed.** `website/scripts/get_started_program.py` is a single runnable
file split by `# %% cell:` markers; `generate_snippets.py` executes its twelve cells in one shared
namespace and captures their stdout into `website/src/generated/snippet-outputs.json`; the page
renders `<Snippet/>`, and `tests/test_portal_snippets.py` executes the same cells through the same
splitter. One source, three consumers, so the page cannot show an output no run produced *or* code
no run executed. The cells pin the NumPy backend at float64 with a fixed seed and carry their own
format specs, which makes exact string equality a realistic contract — and it is the same
configuration the browser Lab runs, so the page teaches the backend choice by using it.

**What was verified.** `ruff check` clean; `ruff format --check` 257 files; `ty check src` clean;
`pytest -n auto` **553 passed** (540 at S8); `pytest tests/test_float32.py` 4 passed; `uv build`
produced both artifacts; `mkdocs build --strict` exit 0 with no warnings; `pnpm validate` clean with
**71** vitest tests (52 at S6); `pnpm test:e2e` **13 passed, 5 skipped, 0 failed**;
`pnpm assemble:site` reports **50 redirect stubs verified**.

Three new guards were proved to bite rather than assumed to, the way S8 proved its fact guard:
pasting a captured output line into the page fails `test_get_started_page_contains_no_output_literal`;
corrupting one committed stdout fails `test_captured_outputs_are_current`; and writing `0.9853`
into a heading fails `test_home_page_contains_no_numeric_literal`. All three were restored after.

**Five things found wrong, and fixed.**

1. **A layout defect on every docs route, not just the new one.** `.docs-frame__content` capped the
   whole grid at the 72ch reading measure, so the body and the 232px table of contents *shared*
   it: every walkthrough, every research page and the new `/get-started` rendered prose at **351px
   of a 1376px frame** — about 45 characters a line — with wide code clipped mid-token. The
   measured fix separates the two measures: prose keeps 72ch, code and tables get their own, and
   the contents column sits beside them. Prose is now 641px and code 800px at a 1440px viewport.
   This has been live since S6 and was found only because a page full of wide code was put through
   it.
2. **A link distinguishable by colour alone.** `.home-aside`'s inline link measured **1.15:1**
   against its own muted surrounding text, against the 3:1 axe requires. Underlining it, as
   `.provenance-note a` already did, fixed it.
3. **Code blocks unreachable by keyboard.** Adding `/get-started/` to the axe scan immediately
   exposed `scrollable-region-focusable` on every `.code-block`: they scroll horizontally and were
   not focusable, so their content was unreadable without a mouse. This is the same defect class S8
   found in `BinningComparison`, in markup the old `/docs` page shared — it went unseen because that
   page was never scanned.
4. **The slogan audit's blanket "all clean" was wrong.** A haiku pass reported zero findings across
   nine routes. Re-checking it directly — the programme's own rule about delegated negatives — found
   three: `benchmarks.tsx`'s "Speed without hiding the machine.", `api.tsx`'s "An API you can
   inspect, not memorize." and the footer's "Hard bins, with the information loss made visible."
   All three assert a benefit rhetorically; all three are replaced with plain statements ("What was
   measured, and on what machine", "The public surface, generated from the source", "Hard bins, and
   a measurement of what the binning cost."). The audit had considered two of them and talked itself
   out of both.
5. **A duplicated navigation entry.** `SearchDialog`'s route table listed Walkthroughs twice.

**Decisions taken, recorded above as D1-D10.** The three the packet left open are answered:
`docs.tsx` is **deleted outright**, because the premise for a stub is false — the Pages artifact has
been `path: site`, the MkDocs build alone, since the repository's first commit, so `/scorequant/docs/`
has never resolved and no external link to it can exist; the workflow reconciliation moved to S11;
and the generator runs **in-process in one shared namespace**, because the cells have always shared
one and subprocess-per-snippet is wrong on the merits rather than merely slow.

**Fence accounting.** `docs/user-workflow.md` carried 9 executed `python` fences and
`docs/motivation.md` none. Both are retired. `/get-started` carries **12** executed cells, 11 of
which print captured output, so every behaviour the retired page demonstrated still runs in a test,
with five additions (save/load round trip, the refusal message, the baseline gap, the occupancy
readout, and prediction on fresh scores).

**What was left open.** The `.research-layout` rule is now unreferenced but was left alone: it
belongs to S11's dead-CSS sweep, which has the coverage tooling to prove the rest of the list.
`.button-primary`/`.button-secondary` survive because `lab.tsx` still uses them. The home page's
opening block leaves its right half empty, and the two closing "ways to start" blocks still read as
cards; both are deliberate hand-offs to S11's design pass rather than defects. Nothing was
committed or pushed.

**The one thing the next session must know.** The site is still frozen and S11 is the session that
turns it on: `docs.yml`'s Pages upload and its `deploy` job are both `if: false`, and the packet now
carries the deployment brief, the authorization chain and the README's 14 absolute links verbatim.
Two things S11 inherits that are easy to miss. First, the docs layout fix above changed the measure
on **all fifteen** docs pages, so the design pass is starting from a wider column than the one S8
and S6 were written against — look at the walkthroughs before restyling them. Second, the axe scan
now covers `/get-started/`, and it earned its place immediately by finding a defect on its first
run; when S11 adds dark mode, scanning **both themes** on that route is what will stop the 4.48:1
class of regression coming back.
