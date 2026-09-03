# S10 — Portal front door: home, get-started, e2e, deployment

**Workstream:** W3 · **Needs:** S8 · **Parallel with:** — · **Status:** queued

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
- `.github/workflows/docs.yml`, `.github/workflows/portal-preview.yml`: the two pipelines the
  deployment flip changes.
- `docs/adr/0019-react-learning-portal.md` and S6's migration ADR: the deployment authorization
  chain.

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

**Deployment.** The root deployment turned on: the portal at `/scorequant/`, MkDocs under
`/scorequant/reference/`, the S6 redirect stubs live. `docs.yml` and `portal-preview.yml`
reconciled into whatever single publishing path the session designs, with the preview path kept
for pull requests.

Publication is an authorized action, not a merge side effect. The flip needs the owner's explicit
go-ahead, requested with the assembled tree already verified, and the live URL is recorded in the
closing report.

## Done criteria

- The home page carries none of: a hero slogan, the proof strip, paired call-to-action buttons, a
  three-card grid. Its first piece of evidence is a measured comparison with a link to its
  derivation.
- No route contains a sentence the slogan auditor flags; the before/after list is in the closing
  report.
- Every snippet on `/get-started` is executed by `tests/test_portal_snippets.py` and asserts a
  result object, and every output the page displays comes from `website/src/generated/`. A `grep`
  for output literals in the page source finds none.
- `website/src/pages/docs.tsx` is gone or is a redirect stub only.
- Nav is the eight final entries; navigation tests match.
- Every pre-cut MkDocs URL resolves on the live site, spot-checked against `website/redirects.json`
  after deployment and recorded in the closing report.
- The root deployment is live and its URL is in the closing report, flipped with the owner's
  recorded go-ahead.
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
| Design and implement the deployment path; reconcile the two workflows | sonnet | workflow diff |
| Post-deployment redirect spot-check against the manifest | haiku | URL/status table |
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

## Open decisions

- Whether `docs.tsx` is deleted or kept as a redirect stub to `/get-started`. `/docs` is the route
  most likely to have been linked externally, which argues for a stub; S6's redirect manifest
  covers MkDocs URLs, not portal ones, so if a stub is wanted it is this session's to add.
- How the two publishing workflows reconcile: one workflow that builds both surfaces and deploys
  the assembled tree, or `docs.yml` reduced to producing the MkDocs artifact that the portal
  workflow assembles. The second keeps the existing division of labour; the first has one place
  where deployment happens.
- Whether the captured-output generator runs the snippets in-process or as a subprocess per
  snippet. A subprocess gives a genuinely clean namespace per snippet at the cost of JAX start-up
  per call; in-process matches what `tests/test_docs_snippets.py` already does.

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
