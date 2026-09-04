# S08 — The four walkthroughs

**Workstream:** W3, W4 · **Needs:** S6, S7 · **Parallel with:** — · **Status:** done

## Goal

Give the project the thing it does not have: several detailed, well-designed walkthroughs of
realistic examples, each carrying one applied problem from the question through the data, the
score model, the fit, the numbers, and what the numbers mean — including what they would have
been under the binning the reader would otherwise have used. Today the portal indexes ten MkDocs
example pages as filter cards and tells no story of its own except `/showcase`, which is the one
page on the site that actually explains something and is therefore the shape to copy. This
session writes four walkthroughs as MDX under the route S6 created, one per input route, two of
them on real data, and makes every displayed number and every displayed output traceable to a run
rather than to a keystroke. Done means all four pages exist, no number on them is hand-typed, and
every Python fence on them executes in a test.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S06-portal-topology-and-reference-cut.md`: S6 closing report; the route, the
  plugin instance, the `AppShell` rendering path, and the scratch file holding the narrative
  material retired from MkDocs.
- `docs/programme/S07-hep-classifier-showcase.md`: S7 closing report; which HEP path shipped, the
  fixture, its licence, and the evidence JSON keys `hep.mdx` reads.
- `docs/programme/S04-showcase-foundations.md`: S4 closing report; the Michelson example, its
  evidence JSON, and the executed `CentralLogRatioScore` fence `ratios.mdx` builds on.
- `website/src/pages/showcase.tsx`: the existing FlowCyt narrative. It is the model for the arc
  and the source `flowcyt.mdx` absorbs; it is deleted at the end of this session.
- `website/scripts/generate_showcase.py`: the existing generator pattern — reads
  `examples/cell_population/data.py` and the committed fixture, writes
  `website/src/generated/showcase-data.json`. Every new walkthrough's data goes through a
  generator of this shape.
- `tests/test_portal_snippets.py`: extracts and executes portal `code:` strings against a fixture
  namespace and asserts a result object. This is the harness to extend to MDX fences.
- `tests/test_docs_snippets.py`: `_extract_blocks`, `Snippet`, and the
  `<!-- snippet: skip -->` / `<!-- snippet: fresh -->` markers — reuse these, do not write a
  second extractor.
- `website/src/components/charts/`: `Axes`, `CompositionBars`, `MarkerHistogram`,
  `MethodComparison`, `scale.ts`, and `ScoreSpace.tsx`. Reuse before adding.
- `website/src/css/global.css`: the design tokens. New components use them; they do not introduce
  a second palette or type scale.
- `.github/workflows/portal-preview.yml`: the workflow this session adds `pnpm test:e2e` to.
- `website/tests/e2e/portal.spec.ts`, `website/playwright.config.ts`: the e2e suite that exists
  and has never run in CI.

## Deliverables

**Four MDX walkthroughs** under `website/walkthroughs/`, each following the same arc, in this
order, with the section names free but the beats fixed:

1. The applied question, in the domain's own words, before any ScoreQuant vocabulary.
2. The data and its provenance — where it came from, its licence, how much of it is committed.
3. The score model: which door, why that door, and what the score coordinates mean here.
4. The fit: the call, with its configuration explained rather than displayed.
5. The numbers: retention spectrum and D-efficiency, effective rank, bin weights, stability, and
   whichever diagnostics this problem actually turns on.
6. What the numbers mean for the original question.
7. The comparison: what the reader's default binning would have retained on the same data.
8. The honest caveat — the surrogate-information limit, the profiled refusal, a negative result.
   `/showcase` and the blog already do this; none of the four pages may drop it.

The four:

- `flowcyt.mdx` — real cells, classifier-derived ratios, Door 3. Absorbs `/showcase` wholesale and
  links into the exhaustive study under `/reference/usecases/flowcyt/` for the full record. Its
  negative result ("it does not materially improve the measurement") stays.
- `hep.mdx` — the S7 example: real events if S4's spike found a usable dataset, the
  three-interface FlowCyt benchmark if not. Profiled \(D_s\) with the nuisance S7 chose.
- `michelson.mdx` — the S4 example (`examples/michelson_phase.py`): analytic `ScoreFunction`, the
  phase/fringe-frequency nuisance, on the NumPy backend. The one walkthrough where the score is known in closed form, which is what makes its
  D-versus-profiled comparison exact rather than estimated.
- `ratios.mdx` — the ratio door end to end, including `CentralLogRatioScore`, the ratio-closure
  diagnostic, and why an estimated ratio does not carry exact Fisher semantics.

**No hand-typed numbers.** Every figure caption, table cell and inline value is read from
committed JSON generated by a script of the `generate_showcase.py` shape out of the Python
examples and their pinned evidence. A number that cannot be traced to a generator is a defect,
not a shortcut.

**Executed fences.** `tests/test_portal_snippets.py` extended to discover every Python fence in
`website/walkthroughs/*.mdx`, execute them per page in one namespace using
`tests/test_docs_snippets.py`'s existing extractor and markers, and assert a result object rather
than a name.

**Components**, only where the reused charts cannot carry the beat: a captioned figure block, a
before/after retention comparison, and a diagnostics readout that labels each number with what it
means. Built on the existing tokens.

**Index and navigation.** `website/walkthroughs/index.mdx` filled in: each walkthrough with its
domain, its door, whether its data is real, and the one thing it teaches — so the reader chooses
by their own situation, not by a tag filter.

**Lab hand-off.** One prefilled Lab job per walkthrough, so a reader who has just understood a
fit can run it without installing anything.

**CI.** `pnpm test:e2e` added to `.github/workflows/portal-preview.yml`, covering the four new
routes.

**Retirement.** `website/src/pages/showcase.tsx` and `examples.tsx` deleted; `docs.tsx` left for
S10, which replaces it with `/get-started`. Nav and navigation tests updated.

**Handed over by S6 (decision R1).** This session also retires `docs/three-doors.md`, because
this session writes the pages that replace it. The page carries **13 executed `python` fences**
covering the source-versus-provider contract, all three provider constructions (including
`CentralLogRatioScore`) and validation samples. Every one of them moves into walkthrough MDX,
where the extended `tests/test_portal_snippets.py` executes it; the fence count before and after
goes in the closing report. Deleting the page without moving the fences would silently drop
coverage the programme has already ruled must not disappear. On retirement, remove
`three-doors.md` from `tests/test_readme.py`'s `_FRONT_DOOR`, add it to
`test_retired_pages_are_gone`, re-point every inbound link the S6 closing report lists, and change
its `website/redirects.json` entry from `reference/three-doors/` to the walkthrough that replaces
it.

## Done criteria

- Four MDX walkthroughs exist and render; each hits all eight beats, verified against this packet
  by a haiku checklist pass whose result is in the closing report.
- Every number displayed on the four pages traces to generated JSON. The audit is a haiku pass
  listing each displayed value and its generator key; any value with no key is fixed before the
  session closes.
- Every Python fence on the four pages is executed by `tests/test_portal_snippets.py` and asserts
  a result object.
- `website/src/pages/showcase.tsx` and `examples.tsx` no longer exist; no route links to them.
- `walkthroughs/index.mdx` describes all four by situation, not by tag.
- `pnpm test:e2e` runs in `portal-preview.yml` and is green.
- Full handoff gate green, plus `cd website && pnpm validate` and `pnpm test:e2e`.
- roadmap M12 table shows S08 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Design the shared walkthrough arc: the eight beats as a concrete page skeleton, the component inventory, and the generator contract for traceable numbers | orchestrator inline | written spec appended to this packet before any prose |
| Write `flowcyt.mdx` (absorbing `/showcase`) and `ratios.mdx` | opus | MDX drafts |
| Write `hep.mdx` and `michelson.mdx` | opus | MDX drafts |
| Implement the generators for the three new walkthroughs' data | sonnet | generator and JSON diff |
| Extend `tests/test_portal_snippets.py` to MDX fences | sonnet | test diff |
| Build the captioned-figure, comparison and diagnostics-readout components on the existing tokens | sonnet | TSX and CSS diff |
| Fill in the walkthrough index; delete `showcase.tsx` and `examples.tsx`; update nav and tests | sonnet | TSX diff |
| Wire `pnpm test:e2e` into `portal-preview.yml` and extend the spec to the four routes | sonnet | workflow and spec diff |
| Beat-coverage checklist over the four pages | haiku | checklist per page |
| Traceability audit: every displayed number to its generator key | haiku | value/key table, gaps flagged |
| Run gates, report failures verbatim | haiku | gate output |

Never a `fable` subagent (`docs/programme/README.md`, budget rule). The two writing tasks are
independent and run in parallel; every task that edits `website/src/pages/` or the nav waits its
turn.

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

The handoff gate applies: extending `tests/test_portal_snippets.py` and adding generators touches
Python.

## Open decisions

- Whether the fence-execution harness reads MDX with the existing Markdown extractor unchanged, or
  needs an MDX-aware pass because of JSX interleaving. Try the existing extractor first; the
  fences are ordinary fenced blocks and JSX between them should be inert to it.
- How much of each walkthrough's code is shown inline versus linked. The arc requires the fit call
  to be visible; whether data loading and score construction are shown in full or summarized is
  per page, decided by whether a reader could reproduce the result from what is on the page.
- Whether `michelson.mdx` and `ratios.mdx` displace their MkDocs counterparts or link to them,
  which depends on the verdict S6 recorded for the three door pages.

## Design decisions — the walkthrough arc

Written inline by the orchestrator before any code, per `docs/programme/README.md` invariant 4.
Every decision below is a constraint on the implementing agents, not a suggestion. Where a
decision corrects something this packet or an earlier one assumed, it says so.

### D1 — The page skeleton

Every walkthrough is one `.mdx` file under `website/walkthroughs/`, with frontmatter carrying
only `title`, `sidebar_label` and `sidebar_position` (the fields the `research` instance already
uses; there is no `description` field and no `slug` — the route comes from the filename). The
body opens `# <Title>` followed by a single italic *"Who this is for: …"* line, matching the
convention every research page established in S6. Nothing else may precede the first section.

The eight beats become eight `##` sections, in this fixed order. Section titles are the page's
own — the beat is what is fixed, not the wording:

| Beat | Must contain | Must not contain |
|---|---|---|
| 1 The question | The applied problem in the domain's vocabulary | The words score, partition, Fisher, retention |
| 2 The data | Provenance, licence, committed size, and the licence's *basis* | A licence claim with no record behind it |
| 3 The score model | Which door, why that door, what each score coordinate means here | A derivation that `docs/book/` already carries |
| 4 The fit | The actual call, with its configuration explained in prose | A pasted config dump |
| 5 The numbers | A `<Diagnostics>` readout: every number labelled with what it means | Any number not from a generated fact |
| 6 What it means | The answer to beat 1, in beat 1's vocabulary | New numbers |
| 7 The comparison | `<BinningComparison>`: what the reader's default binning retains on the same data | A baseline chosen because it loses |
| 8 The caveat | A measured limitation, not a disclaimer | "Results may vary" |

Beat 8 is the one most likely to be quietly dropped, so it is a done criterion: each page's
caveat must be a *number or a refusal the library actually produced*, not a hedge. The four are
already known and are not negotiable — FlowCyt's negative result (it does not materially improve
the measurement), HEP's baseline spread (D9 below), Michelson's criterion mismatch and its
compile-bridge refusal, and the ratio door's surrogate gap (D4 below).

Two corrections to this paragraph, both found by the independent review at the end of the
session and both mine. First, it originally called Michelson's mismatch a
`NormalizedTrace`-versus-profiled one; `NormalizedTrace` appears **zero** times in
`examples/michelson_phase.py`, which has only ever compared `DOptimality` against
`ProfiledDOptimality`. The page follows the example and is right; the packet was wrong. Second,
the ratio door's surrogate gap turned out to be that page's *headline* rather than its caveat —
it is the answer to beat 1, so it belongs in beats 5 and 6. What sits in its beat 8 is a
different measured limitation: the closure diagnostic's own wrong-measure trap, which reports a
residual of 0.18 for a *perfect* score (D4). That substitution is deliberate and is the better
page; a caveat slot filled with the page's own headline would have been a restatement.

A page may end with one optional `## The same door, other inputs` appendix, whose only purpose is
to hold migrated fences that serve no beat (D3). It is an appendix, not a beat, and it comes
after beat 8.

### D2 — The fact contract: no number reaches a page except through a generator

This is the packet's hardest requirement and the one most easily satisfied in appearance only. A
haiku audit that reads pages and looks for suspicious digits is not enforcement — it is a spot
check that passes the day it runs and rots afterwards. So the traceability is made structural in
three layers, and the audit becomes a confirmation rather than the mechanism.

**Layer 1 — the generator.** One new script, `website/scripts/generate_walkthroughs.py`, of the
`generate_showcase.py` shape, added to `pnpm generate`. It reads only committed evidence
(`docs/examples/assets/hep-classifier.json`, `docs/examples/assets/michelson-phase.json`,
`docs/examples/assets/door3-classifier.json` from D4, and the three FlowCyt files under
`docs/usecases/assets/`) and writes `website/src/generated/walkthrough-data.json`:

```json
{
  "schemaVersion": 1,
  "pages": {
    "hep": {
      "headlineGap": {
        "value": 0.5007568385278702,
        "text": "0.5008",
        "source": "docs/examples/assets/hep-classifier.json#/scorequant_vs_classifier_binning/profiled_retention_gap"
      }
    }
  }
}
```

Every fact carries all three fields. `value` is the raw number as it appears in the evidence,
`text` is the generator's formatting of it (pages never format), and `source` is a repo-relative
path plus a JSON Pointer into it.

**Layer 2 — the lookup throws.** `website/src/lib/facts.ts` exports
`factsFor(page: string): (key: string) => string`, returning `text` and throwing a named error on
a missing key. MDX is executed during the Docusaurus build, so a typo in a fact key fails
`pnpm build`, not a reader's eye. Pages import nothing else for numbers; a raw import of
`walkthrough-data.json` in a walkthrough page is a defect.

**Layer 3 — the pointer is checked against the evidence.** New `tests/test_walkthrough_facts.py`:
for every fact in the generated file, resolve `source` against the named committed file and
assert it equals `value`, and assert `text` is a faithful rendering of `value` (same number to the
digits shown). This is what makes the chain real — without it the generator could compute
anything and call it traceable. It also fails when an example is re-run and its evidence moves,
which is the drift the packet is actually worried about.

**Two limits of this enforcement, both found by the independent review and both recorded rather
than closed.** The bare-number guard matches digits, so a measurement spelled as a word — "the
six-bin partition" — passes it; three such spellings exist across the four pages and all three
agree with a fact elsewhere on the same page, but the guard would not catch one that drifted.
And `flowcyt.mdx` reads `showcase-data.json` directly for its three charts, because a bar chart
needs series rather than formatted strings, so those numbers sit outside the three layers
above. The half of that gap that matters is closed by
`test_showcase_chart_data_is_current`, which fails if the FlowCyt study is re-run without
regenerating the portal data; the other half — that a chart could in principle be driven by a
number no evidence backs — is a known gap, and the honest statement of the guarantee is "every
number in walkthrough *prose* is traceable, and the chart series are checked for currency
against their study."

**The bare-number guard.** The same test module scans the four `.mdx` files and fails on any
numeric literal outside a fenced code block, outside a JSX attribute, and not in a small
allowlist committed alongside it (years, counts of things named in the same sentence such as
"two doors", and bin budgets that also appear as a fact). The allowlist is a committed dict with
a reason per entry, so an addition is a visible decision rather than a silent one.

**Layer 2 was verified rather than assumed.** A probe page calling `factsFor("nosuchpage")
("nosuchkey")` was built: `pnpm build` exits 1 with a stack trace through `lookupFact`, so a
missing fact is a build failure and not an `undefined` on a published page. Worth recording
because the first probe appeared to pass — Docusaurus silently ignores content files whose name
begins with an underscore, so `_probe.mdx` was never rendered at all. A page added under
`website/walkthroughs/` with a leading underscore is invisible, which is a trap for anyone adding
a draft there.

Together these mean the haiku traceability audit is a confirmation pass over a property already
enforced by the build and the suite. It still runs, and its table still goes in the closing
report, but nothing depends on it being thorough.

### D3 — Fence migration out of `three-doors.md`

`docs/three-doors.md` carries **13** fenced `python` blocks, none marked, all executing
cumulatively in one namespace. Fence 0 is the shared import block; fences 1–12 are substantive.
Deleting the page without moving them drops coverage the programme has already ruled must not
disappear.

**The MDX comment problem, which this packet listed as an open question and which is now
answered.** The extractor's regex in `tests/test_docs_snippets.py` recognises markers only in the
HTML-comment form `<!-- snippet: skip -->`. Docusaurus 3.10 uses MDX 3, where an `.mdx` file is
parsed in MDX mode and `<!-- -->` is not a comment but invalid JSX — it fails the build. No `.mdx`
file in the repository contains one today. So the marker form in MDX is `{/* snippet: skip */}`,
and `_BLOCK_PATTERN` must accept both spellings. This is a change to the shared extractor, so it
is made once, in `tests/test_docs_snippets.py`, and the existing Markdown pages keep working
unchanged; a test asserts both spellings parse.

**Placement.** Every substantive fence goes to the page whose beat it serves, by door:

| Page | Fences | Why there |
|---|---|---|
| `flowcyt.mdx` | 1 (source/provider contract), 2 (Door 1 `ScoreSample`), 12 (validation samples) | It is where a reader first meets a `ScoreSample`, and it is the only study with a genuine held-out split, so the validation-sample fence lands on the page that actually has one |
| `michelson.mdx` | 3 (`LinearComponents`), 4 (Monte Carlo `ObservationSample`), 5 (`IntegrationSource`), 6 (exact score callback), 7 (`scores_from_components`) | Michelson *is* Door 2 — it uses 5 and 6 for real; 3, 4 and 7 are the sibling constructions and belong in its appendix |
| `ratios.mdx` | 8 (posteriors→ratios→scores), 9 (`DensityRatioScore.from_classifier`), 10 (`ratio_closure_report`), 11 (`CentralLogRatioScore`) | The whole of Door 3 |
| `hep.mdx` | — | Its `CentralLogRatioScore` usage is real and at scale; a synthetic duplicate would weaken it |

Each page opens with its own imports fence, so a page's code runs as shown rather than depending
on a fixture namespace a reader cannot see. Accounting for the closing report: **13 fences in,
12 substantive fences placed plus 4 page-local import fences = 16 fences out**, across four pages.
That arithmetic is reported, not asserted vaguely.

**The harness.** `tests/test_portal_snippets.py` is extended (not duplicated) to discover
`website/walkthroughs/*.mdx`, reusing `_extract_blocks`/`Snippet` from `tests/test_docs_snippets.py`
— the packet's instruction to try the existing extractor first stands, and JSX between fences is
inert to a regex that anchors on ```` ```python ````. Each page executes in its **own fresh
namespace, cumulative across that page's fences**, with no pre-seeded fixture: the deliberate
difference from the `docs.tsx` snippets, and the reason each page carries its own imports. After a
page's fences run, the module asserts the namespace holds at least one `sq.PartitionResult` or
`sq.QuantizerResult` — the packet's "asserts a result object" contract, applied per page rather
than per fence, since the arc reaches a fit once. The existing `sq.__all__` AST check is applied
to walkthrough fences too.

These tests execute published prose, which is exactly what `tests/conftest.py`'s `docs_execution`
marker is for, so the walkthrough fence tests join that tier. `test_portal_snippets.py`'s existing
`docs.tsx` tests stay where they are; S10 rewrites that page and can decide then.

### D4 — `ratios.mdx` needs evidence that does not exist yet, and the honest version of the page is better than the planned one

The inventory turned up a real gap the packet did not anticipate: there is **no committed evidence
JSON for a ratio example**. `CentralLogRatioScore` appears in exactly two places — the synthetic
fence on `three-doors.md`, which has no numbers behind it, and `examples/hep_classifier/scores.py`,
which is `hep.mdx`'s subject. So `ratios.mdx` as planned would have had either no numbers or
borrowed ones, and the no-hand-typed-numbers rule would have been satisfied by having nothing to
type.

`examples/door3_classifier.py` already contains the fix, and it is a better page than the one
planned. That module trains a logistic classifier on a two-component Gaussian mixture *and* builds
the analytic Bayes-optimal score for the same mixture (`exact_provider()`, `kind="exact"`). Its
`run_ladder` measures, at three training-set sizes, both what the estimated-ratio provider
*reports* about itself (`surrogate_retention`) and what it actually achieved against the true
scores (`true_retention`). It produces a committed figure and no JSON.

So `ratios.mdx`'s applied question is: **"I have a classifier, not a likelihood. Can I trust the
number the library hands back?"** That is a real question with a measured answer, it is the honest
counterpart to FlowCyt and HEP — both of which use classifier ratios and have no ground truth to
check them against — and it makes beat 8 a measurement instead of a disclaimer. It is also the
page that carries `ScoreProvenance`'s design: `exact_fisher` is *derived* from `kind` rather than
accepted as a flag (`src/scorequant/sources.py:153-168`), so an estimated score cannot claim exact
Fisher semantics even by mistake. That is a library guarantee worth showing, and no page shows it.

Work this requires, all in `examples/door3_classifier.py`:

- A `Study` dataclass and `run_study()` following the `michelson_phase.py` shape, honouring
  `SCOREQUANT_EXAMPLE_FAST` through `examples/_env.py` the way the other examples do.
- `main()` writes `docs/examples/assets/door3-classifier.json` alongside the existing PNG.
- The ladder keeps its three training sizes and adds the exact-provider ceiling as an explicit row,
  plus a `ratio_closure_report` diagnostic, since `ratios.mdx` teaches the closure check.
- Pinned in `tests/test_evidence_suite.py` with a `DOOR3_METRICS` constant, a
  `_matches_the_published_*` test and a `test_fast_rerun_reproduces_*` test, matching the file's
  existing pattern for every other example.
- `docs/examples/door3-classifier.md` gains the numbers it now has evidence for. It stays in
  MkDocs; `ratios.mdx` links to it rather than restating it (D8).

### D5 — The Lab hand-off is new work, not wiring

The packet asks for "one prefilled Lab job per walkthrough". Checked directly rather than taken
from the inventory, because a negative that changes what gets built is re-checked by the
orchestrator: `DatasetId` is `"gaussian" | "flowcyt" | "local"`, and nothing under
`website/src/lab/` or `website/src/pages/lab.tsx` reads `location.search`, `URLSearchParams` or a
router query. The single existing showcase→Lab link carries no parameters. There is no mechanism
to reuse.

The minimum that makes the deliverable real:

- `generate_walkthroughs.py` also writes one score table per walkthrough to
  `website/static/walkthrough-scores/<slug>.json`, in the shape `useScoreTable` already consumes.
  These are small — HEP is 1,000 rows by 3 columns, Michelson and the ratio ladder smaller still —
  unlike FlowCyt's 300 KB table, which is already fetched on demand and is reused as-is.
- A committed preset registry in the same generated file: slug → dataset, bin budget, criterion,
  interest parameter.
- `lab.tsx` reads `?job=<slug>` once on mount, validates it against the registry, and seeds its
  existing `useState` initial values; an unknown or malformed slug is ignored and the Lab opens on
  its current default. No new state, no new control flow.
- Each walkthrough's beat 6 or 8 links `/lab?job=<slug>`.

If the score-table export proves larger than expected for any page, that page links to `/lab`
unparameterised and the closing report says which and why. The mechanism ships regardless, because
it is what S10's "one Lab job prefilled per walkthrough" also depends on.

### D6 — Retirement, and where the inbound links go

`three-doors.md` is retired here, by the session publishing its replacement, per the standing rule
in `docs/programme/README.md`.

- **MkDocs-internal links** (`docs/method.md:43`, `docs/index.md:50` and `:116`,
  `docs/user-workflow.md:47`, `docs/examples/*.md` × 9, `docs/examples/index.md:15`,
  `docs/book/ch04-scores-and-doors.md:234`, `docs/usecases/hep/index.md:3`) re-point to
  **`docs/book/ch04-scores-and-doors.md`**, not to a walkthrough. Reason: the portal is not
  deployed until S10, so a MkDocs page linking to a portal URL would be a dead link on the live
  site for the whole of S8 and S9; ch04 is reference material that survives the cut and covers the
  same ground. `mkdocs build --strict` fails on a broken internal link, which is the check.
- **`mkdocs.yml:49`** loses its nav entry.
- **`website/redirects.json`**: the `three-doors/` entry re-points from `reference/three-doors/`
  to `walkthroughs/ratios/`, which is the page that replaces it. This also keeps `README.md`'s two
  absolute `.../scorequant/three-doors/` URLs working after S10 flips deployment, which is why
  they are left alone here — S6 deliberately deferred every README absolute URL to the commit that
  turns deployment on, and that decision stands.
- **`examples/` moves out of `unstubbed` and back into `redirects`, pointing at
  `reference/examples/`.** This is a consequence the packet did not draw. That URL is unstubbed
  *only* because a portal route occupies it, and the manifest's own note says entries move to
  `unstubbed` when a route occupies the URL — so deleting `examples.tsx` frees the path and the
  entry must move back, or link parity silently breaks for a URL that was in the pre-cut sitemap.
  `reference/examples/` is the target because that is where the content that used to be at
  `/examples/` now lives; the unstubbed entry's own reason already says so.
- **`/showcase/`** needs no stub: it is a portal-native route, the portal has never been deployed,
  and nothing outside `website/src/` links to it (checked across `README.md`, `docs/` and
  `mkdocs.yml`).
- **`tests/test_readme.py`**: `"three-doors.md"` leaves `_FRONT_DOOR`, and `"docs/three-doors.md"`
  joins `test_retired_pages_are_gone`, whose existing assertions also check the path is gone from
  `mkdocs.yml`.
- **Deletions**: `website/src/pages/showcase.tsx` and `website/src/pages/examples.tsx`. The nav
  array in `website/src/components/AppShell.tsx:12-21` keeps eight entries; `Docs` stays for S10.
  The three chart components that only showcase used — `CompositionBars`, `MarkerHistogram`,
  `MethodComparison` — move with the content into `flowcyt.mdx` rather than being deleted.

### D7 — e2e into CI

`.github/workflows/portal-preview.yml` stops at `pnpm test` (vitest) and never runs Playwright,
though the suite exists and passed 13 tests in S6. Add, after `pnpm build`: a
`pnpm exec playwright install --with-deps chromium` step and `pnpm test:e2e`. `pnpm validate` is
left alone — it is the fast local loop, and e2e needs browsers.

The spec at `website/tests/e2e/portal.spec.ts` needs three changes: its route list loses
`./showcase/` and `./examples/` (both deleted) and gains the four walkthrough routes; its
one-`<main>`-landmark assertion covers them; and the axe scan, which already covers
`./walkthroughs/`, extends to the four pages. The showcase-specific test block moves to
`flowcyt.mdx`'s route with its assertions intact — including the CC-BY-NC-SA-4.0 attribution
check, which is a licence obligation and must not be lost in the move.

### D8 — What the walkthroughs must not do

MkDocs already carries substantial prose for all four subjects: `docs/usecases/flowcyt/index.md`
(116 lines plus five companion pages), `docs/usecases/hep/index.md` (236 lines),
`docs/examples/michelson-phase.md` (266 lines) and `docs/examples/door3-classifier.md` (220
lines). Those pages stay. A walkthrough that restates them produces two sources of truth for the
same numbers and doubles the drift surface the fact contract exists to close.

So each walkthrough is the *narrative* — the arc from question to meaning — and hands off to the
reference for the exhaustive record: the full method, the derivations, the sweeps, the diagnostics
tables. Each page carries exactly one prominent onward link to its reference counterpart, in beat
2 or beat 5, written as a sentence rather than a "see also". If a walkthrough finds itself
reproducing a reference table, the table belongs in the reference and the walkthrough quotes one
number from it.

### D9 — The HEP page's numbers are fixed by S7's correction

From S7's closing report, and not to be re-derived: `hep.mdx` quotes **0.5008** as the headline
profiled-retention gap, against `classifier_logit_equal_width`, and reads
`scorequant_vs_classifier_binning.best_baseline_key` rather than hard-coding which baseline won —
so that if a future re-run changes the winner, the page follows. It also carries the baseline
spread, **0.2098**: binning the same classifier posterior two reasonable ways moves retained
profiled information by 0.21, which sets how much of the headline is the method and how much is
the baseline's difficulty. That point is the most useful thing this example teaches a
practitioner and it is beat 8 for that page.

The provenance sentence in beat 2 states all three facts separately, as the fixture's own
provenance JSON does: the bytes came from the `FAIR-Universe/HEP-Challenge` code repository, that
repository carries no licence file, and the CC-BY-4.0 claim is made under the Zenodo archival
record (DOI 10.5281/zenodo.15131565) for the dataset the sample is drawn from. It must not be
compressed into "CC-BY-4.0".

## Closing report

Session S8 ran on 4 September 2026 on branch `consolidation-s8-the-four-walkthroughs`. The design
spec above (D1–D9) was written into this packet before any code, per the orchestrator contract;
two opus agents wrote the four pages from it, four sonnet agents built the evidence, components,
Lab hand-off and generators, and one sonnet agent audited the result independently at the end.

**What this session was for.** The portal had a route for walkthroughs and one page in it saying
they did not exist yet. The reader who wanted to know whether this library would help them had a
reference that re-derives the method and a showcase page for one study. This session writes the
four applied stories, retires the last narrative page from MkDocs, and — the part that took the
most care — makes it structurally impossible for a number on those pages to have come from
anywhere but a run.

**What was delivered.**

*Four walkthroughs* under `website/walkthroughs/`, each following the same eight beats from the
applied question to a measured limitation. `ratios` (the ratio door, on a synthetic mixture where
the exact Bayes score is known), `hep` (FAIR Universe HiggsML, profiled \(D_s\) against a tau
energy scale), `flowcyt` (real bone-marrow cytometry, absorbing `/showcase`), and `michelson` (an
analytic score, on the NumPy backend). The index no longer lists what is planned; it sorts the
four by the reader's situation rather than by domain.

*The fact contract.* `website/scripts/generate_walkthroughs.py` holds a table of every value the
four pages may print — 124 of them — each carrying a JSON Pointer into a committed evidence file.
`website/src/lib/facts.ts` throws on a missing key, and because MDX executes during the build, a
typo is a failed build rather than an `undefined` on a published page (verified with a probe:
`pnpm build` exits 1 through `lookupFact`). `tests/test_walkthrough_facts.py` re-resolves every
pointer against the evidence with its own pointer walk, checks each displayed string renders its
own value, and fails on a numeric literal in prose outside a small allowlist. The guard was tested
against the failure it exists for: injecting `0.7106` where `0.5008` belongs fails it by name.

*The retirement.* `docs/three-doors.md` is gone, by the session that published its replacement.
Its 24 inbound MkDocs links re-point to `docs/book/ch04-scores-and-doors.md` — deliberately not to
a portal URL, because the portal is not deployed until S10 and a MkDocs page linking into it would
be a dead link on the live site for the whole of S8 and S9. `showcase.tsx` and `examples.tsx` are
deleted.

*The Lab hand-off.* `/lab?job=<slug>` arrives pre-configured, which required building the
mechanism: there was none. A generated preset registry, three score tables under
`website/static/walkthrough-scores/` (312 KB, fetched on demand), and a `useEffect`-seeded read of
the query so the server and client first renders agree.

*e2e in CI.* `portal-preview.yml` installs Chromium and runs `pnpm test:e2e` after the build,
uploading the Playwright report on failure. The suite's route list drops the two deleted pages,
gains the four walkthroughs, and the accessibility scan now covers all four.

**What was verified.** `ruff check`; `ruff format --check` (256 files); `ty check src`;
`pytest -n auto` **540 passed**; the two tiers separately (449 library, 91 docs execution);
`pytest tests/test_float32.py` 4 passed; `uv build` (wheel and sdist); `mkdocs build --strict`;
`pnpm validate`; and `pnpm test:e2e` **13 passed, 5 skipped, 0 failed**.

**Five things that were wrong and are not now.**

1. *A working diagnostic was about to be published as unreliable.* The delegated door-3 work
   reported, honestly, that the **exact** provider's `ratio_closure_report` residual (0.180) was
   *larger* than every estimated classifier's, and concluded the diagnostic was dominated by noise.
   The diagnosis stopped one step short. `ratio_closure_report`'s contract is that the weights
   carry the measure of the ratio *denominator*; the example was evaluating closure on a sample
   from the 0.3/0.7 reference mixture while the ratios are defined against the 0.5/0.5 training
   prior. Under the correct measure the exact provider's residual is 0.0017 and the ladder is
   monotone (0.0420, 0.0185, 0.0032). The analytic ratio means under the wrong measure are 0.8411
   and 1.1589 — a fixed offset present with a *perfect* estimator, verified by quadrature. Publishing
   the original would have taught readers that a working check cannot be trusted. The wrong-measure
   number is now published deliberately, as a demonstration of a specific mistake.
2. *Two fact keys pointed at the wrong thing, and both would have printed a plausible wrong
   number.* FlowCyt's two ScoreQuant methods disagree in opposite directions on the two metrics —
   soft Voronoi wins on macro RMSE (0.001929 against 0.002094), the compiled D exchange wins on
   held-out D-efficiency (0.9853 against 0.9846) — and the retired showcase page quoted one
   method's pair as a single headline without naming it. Every FlowCyt key now names its method.
   Michelson's "equal-width segments retain exactly zero" is the **four**-bin row; the headline
   budget is six, where equal-width retains 0.2054. Every sweep key now names its budget.
3. *The portal's code theme has never met WCAG AA.* Wiring the e2e suite into CI surfaced it
   immediately: Palenight's numeric token measures 4.48:1 against its own background and its
   comment token 2.84:1, so every number and every comment in a fenced snippet was a serious
   violation — 93 nodes on one page. It went unnoticed because no portal page carried substantial
   code until these four. Also fixed: inline `code` inside a link at 4.49:1, and
   `BinningComparison`'s screen-reader table, which the article's own `overflow-x: auto` rule
   turned into a scroll region no keyboard could reach at phone width.
4. *Deleting `examples.tsx` would have silently broken link parity.* The `examples/` URL was in
   `redirects.json`'s `unstubbed` list *only because* a portal route occupied it; the manifest's
   own note says entries move there when a route takes the URL. Deleting the route frees the path,
   so the entry moved back into `redirects`, pointing at `reference/examples/`. The `three-doors/`
   stub re-points to `walkthroughs/ratios/`, which makes it the only stub in the manifest whose
   target is a portal route rather than the reference — recorded as a named exception in
   `website/tests/redirects.test.ts` rather than by relaxing the rule that caught it.
5. *This packet named a criterion the example has never used.* D1 called Michelson's caveat a
   `NormalizedTrace`-versus-profiled mismatch. `NormalizedTrace` appears zero times in
   `examples/michelson_phase.py`, which has only ever compared `DOptimality` against
   `ProfiledDOptimality`. The page followed the code and is right; the packet is corrected.

**One result worth reading before the next session quotes this library's advantage.** The
independent audit found `ratios.mdx`'s comparison beat weak: it measured what the library
*reported* against what it *achieved*, but had no naive-binning baseline, which every other
walkthrough has. Adding one changed what that page teaches. On this one-dimensional score, at the
same four-bin budget, the fitted partition beats the better naive rule by at most **0.0155**, and
at the largest training size naive equal-width cells are **ahead** of it, 0.9678 against 0.9665.
That is the measured result, produced without adjusting budget, seeds or baseline. It is now the
page's beat 7, stated flatly: on a one-dimensional score, which binning rule you choose barely
matters, and the residual differences are smaller than the error the classifier introduces. This is
the honest boundary of the method — and it is what makes the multi-dimensional examples mean
something, since HEP's comparison at the same budget moves retained profiled information by an
order of magnitude more.

**What is left open.**

- *Two limits of the fact contract, recorded rather than closed.* A measurement spelled as a word
  ("the six-bin partition") passes the digit-based prose guard; three such spellings exist and all
  three agree with a fact on the same page, but a drifting one would not be caught. And
  `flowcyt.mdx` reads `showcase-data.json` directly for its three charts, because a bar chart needs
  series rather than formatted strings. The half that matters is closed by
  `test_showcase_chart_data_is_current`; the honest statement of the guarantee is that every number
  in walkthrough *prose* is traceable and the chart series are checked for currency.
- *`hep.mdx`'s comparison chart carries the same five rows as its reference page's table*, in chart
  form. Beat 7 requires exactly that data, so this is duplication the arc asks for rather than
  redundancy, but it is the one place a walkthrough and its reference hold the same table in full.
- *The fence accounting in D3 was a prediction, not a measurement.* It expected 16 fences out; the
  pages carry **26** (flowcyt 6, hep 4, michelson 8, ratios 8, none skipped). Every one of the 12
  substantive fences assigned from `three-doors.md` is present and rewritten into context; the
  extras are the page-native fences beat 4 requires. `hep.mdx` runs the real cross-fitted pipeline
  at the published configuration and reproduces the published numbers exactly.
- *`README.md`'s two absolute `three-doors/` URLs are untouched*, per S6's standing decision that
  every README absolute URL moves in the commit that turns deployment on. They keep working through
  the re-pointed stub.

**The one thing the next session must know.** The live site is still frozen — `docs.yml`'s Pages
upload and `deploy` job are both `if: false`, and S10 is the session that lifts it, with the
owner's authorization, against the assembled tree. Everything S10 needs from this session is in
place: the walkthroughs it must quote real numbers from, the fact contract to quote them through
(add a row to the `FACTS` table; never type a number), and the `?job=` Lab mechanism its
get-started page was going to need anyway. Two things S10 inherits directly: it retires
`motivation.md` and `user-workflow.md` alongside the pages that replace them, and `user-workflow.md`
carries **9 executed fences** that must move the way `three-doors.md`'s 13 just did — the extractor
now accepts both the Markdown `<!-- snippet: skip -->` and the MDX `{/* snippet: skip */}` marker
spellings, and `tests/test_portal_snippets.py` already discovers and executes MDX pages, so the
machinery is built.
