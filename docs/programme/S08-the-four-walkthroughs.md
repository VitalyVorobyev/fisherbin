# S08 — The four walkthroughs

**Workstream:** W3, W4 · **Needs:** S6, S7 · **Parallel with:** — · **Status:** queued

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

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
