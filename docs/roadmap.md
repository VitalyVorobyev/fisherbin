# ScoreQuant development roadmap

This is the single executable planning document. User-facing reference pages describe only
implemented interfaces.

## M1 — Canonical contracts and documentation

**Status:** implemented in the architectural update; keep as a permanent gate.

- Use ScoreQuant consistently.
- Separate population design, empirical quantizer fitting, and finite assignment.
- Separate sources from score providers and exact from surrogate information.
- Maintain the independent book, how-to/API reference, ADRs, and research provenance.

**Gate:** one glossary; no nonexistent APIs in published pages; documentation tests and strict
MkDocs pass.

### Phase 2 documentation overhaul

**Status:** done.

- Replaced the 12-chapter book with the gradual, 1D-first 14-chapter book (`docs/book/ch01`–`ch14`)
  and swapped the mkdocs nav and every cross-link to match.
- Rewrote `docs/book/index.md` as a book overview with a chapter list and two reading paths.
- Rewrote `docs/bibliography.md` with one anchored entry per citation used by the book, grouped by
  theme, verified against every `bibliography.md#anchor` reference in the published docs.
- Rewrote `docs/glossary.md` in alphabetical order with terms consistent with the new book
  (sample partitioning, space quantization, three doors, exchange stability, compile bridge,
  efficient score, retention).
- Swept `docs/api.md` of stale TODO markers and verified its claims against `src/scorequant/`.
- Removed dev-only notation (TODO/phase references) from published pages; tutorial pages keep
  their planned-for-replacement content with neutralized skip-marker wording.

### Phase 3 — synthetic examples and evidence suite

**Status:** done.

- 3A: shared examples infrastructure — `examples/baselines.py` (the three canonical naive
  baselines), `examples/_env.py` fast-mode helper, and the `tests/test_notebooks.py` harness.
- 3B: replaced the `Tutorials` nav section with `Examples`; added door1-score-events,
  door2-mixture-densities, and door3-classifier pages and notebooks.
- 3C: added the solver-shootout page and notebook, and rebuilt the gallery as a comparison
  dashboard.
- 3D: added the nuisance-profiled-ds and soft-purification pages and notebooks.
- 3E: added the three theorem-demonstration pages and notebooks — lloyd-nonmonotone,
  ds-geometry-counterexample, global-certification.
- 3F: added the flowcyt-teaser page (a pointer into the FlowCyt study, no notebook) and the
  `examples/index.md` section overview; verified every notebook-backed example page links its
  notebook and vice versa, and every example page links at least one book chapter; added
  reciprocal "runnable example" pointers on the relevant book chapters; closed orphaned-number
  gaps found in the claim-assertion sweep; updated the README and docs front matter to reference
  the Examples section.

**Gate:** all ten example pages and nine notebooks execute under `tests/test_docs_snippets.py`
and `tests/test_notebooks.py`; every headline number in prose is asserted in a page snippet or
in `tests/test_evidence_suite.py`/`tests/test_research_claims.py` from committed JSON; strict
MkDocs build passes.

### Phase 4 — FlowCyt master showcase and performance closure

**Status:** done.

- 4A: restructured the 534-line `docs/usecases/cellpopulation.md` wall into the six-page
  `docs/usecases/flowcyt/` section (index, data, scores, quantization, profiled, solvers) and
  added the profiled-\(D_s\) study extension on real data; every inbound link re-pointed, the old
  page deleted.
- 4B: added the real-data solver comparison (`docs/usecases/flowcyt/solvers.md`) covering every
  dispatch-table solver plus the three canonical baselines, on both the frozen CI fixture and the
  600,000-cell bounded sample, with committed JSON evidence and publish-grade figures.
- 4C: ran the profiling campaign to \(N=10^6\) (`benchmarks/README.md`: bottleneck table, machine
  roofline, folded-stack profiles under `benchmarks/profiles/`), applied three bit-identical
  numerical wins, refreshed `benchmarks/baselines.json`, reached a measured Rust no-go for the
  numerical core, and fixed the terminal geometry check that had blocked the converged
  \(N=10^6\) D-exchange measurement ([ADR 0016](adr/0016-tolerance-consistent-geometry-verification.md)).
- 4D: closure sweep — this page, `docs/system-design.md`, `docs/development.md`, and `README.md`
  truth-passed against final `src/`, `benchmarks/`, and `tests/`; repo-wide dev-notation and
  stray-artifact sweep; full exit gate re-run.

**Gate:** every number quoted from the 600,000-cell sample or the full corpus states its
provenance and is asserted from committed JSON; `tests/test_cell_population.py` and
`tests/test_readme.py` stay green; strict MkDocs build passes; the full validation gate at the
bottom of this page passes, plus `uv run python benchmarks/bench.py --check
benchmarks/baselines.json --time-tolerance 10 --quality-rtol 1e-6`.

## M2 — Exact finite D reference core

**Status:** implemented baseline.

- Exact cell statistics, rank-two relocation gain, deterministic monotone exchange, terminal scan,
  small-instance exhaustive oracle, zero-weight handling, and explicit compilation.
- Regression gates cover direct recomputation, monotonicity, small global optima, the D separation
  bound, invariants, and reproduction of positive-weight labels.

**Next:** profile factorization updates before optimizing performance further. The branch-and-bound
certificate workflow this milestone deferred is implemented; see the M7 certificate gate.

## M3 — Breaking task-explicit API

**Status:** implemented; compatibility break is intentional.

- `optimize_partition`/`PartitionResult` for fixed labels.
- `fit_quantizer`/`QuantizerResult` for reusable score rules.
- `DOptimality`, `NormalizedTrace`, and solver-specific configurations.
- Old `fit`, `fit_components`, and `fit_scores` names are removed without aliases.

**Gate:** examples, notebooks, API pages, and migration table use only the new surface; ordinary
partitions expose no prediction semantics.

## M4 — Sources, providers, and bounded integration

**Status:** first wave implemented.

- `ScoreSample`, `ObservationSample`, and low-dimensional bounded `IntegrationSource`.
- `ScoreFunction`, `LinearComponentScore`, ready classifier-derived providers, central-ratio and
  mixture constructions, and score provenance (reshaped around density ratios in M8).
- Deterministic tensor Gauss-Legendre quadrature with explicit density and capacity guard.

**Gate:** equivalent materializations agree; invalid combinations fail clearly; analytic quadrature
agrees with known moments and deterministic sampling; validation never affects fitting state.

**Deferred:** autodiff-model convenience, population samplers, direct score samplers, streaming,
and moment oracles.

## M5 — Book and FlowCyt capstone

**Status:** book and task-explicit 600k workflow integrated, including the exact-D reference.

- Maintain theorem/proposition/numerical-evidence/open-problem labels.
- Use analytic and rational laboratories for mathematical claims, never FlowCyt as proof.
- Compare finite D assignment, compiled D rule, trace k-means, soft D, marker/PCA/random baselines,
  and the unbinned classifier-ratio fit on the frozen patient split.
- Report score provenance/calibration, mean-score closure, compression loss, rank, occupancy,
  patient shift, hardening/geometry gaps, and downstream error.

**Completed solver gate:** vectorized exact-D scanning is included in the normative workflow on the
same 27,607-row partition sample as the learned quantizers. The compiled rule must reproduce every
positive-weight training label. This is deliberately not described as optimization over all 600,000
events.

**Solver-scale gate completed:** exact rank-two state/inverse updates and deterministic
memory-bounded candidate scans agree with full recomputation over repeated moves. The recorded CPU
benchmark covers 200k rows/ten moves and one million rows/one scan. Stored arrays and initialization
remain \(O(N)\), so this is not a claim of full-corpus or one-pass fitting.

**Data gate completed:** the reproducible downloader reconstructed all 30 `Case_*.csv` files
(21,254,866 events), and the frozen 600k sample was audited against every full-corpus row without
retuning. Maximum patient/class fraction error is \(3.39\times10^{-5}\); maximum standardized
marker-mean error is 0.0296. Hashes, aggregates, the patient table, and the plot are committed;
raw CSV/FCS data remain external.

## M6 — Profiled \(D_s\)

**Status:** implemented.

Implement finite exchange and a separate inductive solver. Add efficient scores, the finite
geometry-gap bound, the full-information upper problem, and exact scalar dynamic programming where
applicable.

**Gate:** exact relocation tests; rational non-Voronoi counterexample; no implicit compilation from
finite labels; clear same-data versus external-nuisance semantics.

**Upper-problem gate completed:** `efficient_score_bound` certifies a ceiling on the profiled
objective by solving the exact scalar interval program on the full-data efficient score, in the same
log-determinant convention the finite profiled solver reports, and its labels initialize profiled
exchange through `optimize_partition(..., initial_labels=...)`. The certificate is limited to one
interest column; a multivariate efficient score would need a multivariate solver and is refused
rather than approximated.

**Exact scalar gate completed:** the interval dynamic program is evaluated in memory-bounded
vectorized stripes instead of a per-stop Python loop, reproduces the previous implementation's
labels and objective bit for bit, and attains the exhaustive small-instance optimum.

## M7 — Population, scale, and persistence

In order: population samplers and moment oracles; streaming and factorization updates; then
versioned persistence. Signed weights, additional backends, and advanced objectives remain outside
scope until their mathematical contracts and independent use cases exist.

**Certificate gate completed:** `exchange_stability_report` certifies any supplied labeling with one
exact scan and reproduces the engine's own `best_remaining_gain`; `PartitionResult.geometry` reports
the Voronoi violation, the Theorem-3 guaranteed gain, and the cell-separation residual of a D
partition; and `certify_partition` proves global optimality by branch and bound with the
singleton-completion bound, agreeing with the exhaustive oracle on seeded weighted and unweighted
instances and downgrading to `status="budget_exhausted"` with a genuine outstanding bound when its
node budget runs out. Certification is D-only and never runs implicitly, per ADR 0014.

**Scale gate completed:** every certificate states the `gain_tolerance` it holds at, and every
geometry verification judges the exact relocation gain against that same tolerance instead of
against zero. A converged 1 000 000-row D-exchange or Mahalanobis-Lloyd fit therefore returns,
certifies, and compiles, where a zero-tolerance comparison previously rejected it over 13 boundary
rows in a million, per ADR 0016.

## M8 — Density ratios as a first-class representation

**Status:** implemented.

Per [ADR 0017](adr/0017-density-ratio-representation.md): the statistical representation layer is
named — exact densities, model density ratios, and scores — with the classifier decomposed into
one estimator of ratios. `ratios.py` owns `ratios_from_posteriors`, `mixture_scores_from_ratios`,
the two declared parameterizations, and `ratio_closure_report`; `DensityRatioScore` (with
`from_classifier`) and `CentralLogRatioScore` replace `ClassifierScore` and its transforms;
`ScoreProvenance` carries a structured `RatioProvenance`; model ratios and importance ratios keep
disjoint API homes (providers versus source weights).

**Gate:**

- The decomposition is equivalence-tested: `DensityRatioScore` over \(\Phi/\phi_{\rm ref}\)
  reproduces `LinearComponentScore` exactly, the two-step posterior chain reproduces the former
  composed transform, and gauge invariance holds for both parameterizations.
- Closure is exercised by an analytic laboratory (exact ratios close to numerical precision, a
  misdeclared prior does not) and two applications (door-3 example, FlowCyt calibration audit).
- Invalid combinations fail by name; ratio provenance round-trips through `to_dict()`.
- No repository reference to the removed names (`ClassifierScore`, `MixturePosteriorTransform`,
  `CentralLogRatioTransform`, `mixture_scores_from_posteriors`) outside ADR history and this gate.
- Reference pages and navigation cover the new surface; the full handoff gate passes.

## M9 — Explicit multi-backend execution

**Status:** implemented; parity and browser smoke gates pass.

1. Architecture foundation: land ADR 0018, the code-quality audit, dependency rules, the
   `ExecutionConfig` contract, and import-boundary checks.
2. Backend-neutral JAX extraction: canonicalize public arrays as NumPy, move JAX imports behind a
   private adapter, split solver responsibilities, and preserve the existing default path.
3. NumPy parity: run every hard solver and certificate, implement one analytic soft objective and
   gradient, apply it through Optax and a matching private NumPy Adam implementation, and build one
   backend-parameterized conformance suite.
4. Browser packaging: omit JAX/Optax on Emscripten, build a wheel, and pass a Pyodide smoke run.

**Gate:** every declared task/configuration/criterion combination runs under JAX and NumPy and
induces the same partition, compared up to bin relabeling; in float64 the retained information and
objective agree at `rtol=1e-10, atol=1e-12`, and the annealed soft solver at `rtol=1e-4`. In float32
only the *continuous* quantities are gated across backends (`rtol=1e-5, atol=1e-6`): a relocation
gain can fall inside the float32 noise floor, so the discrete solvers may walk to different,
individually exchange-stable optima, and each backend is gated on its own validity instead. Public
arrays are NumPy; invalid execution requests fail before work; default JAX benchmarks have no
unexplained quality regression; both architecture reviews pass.

## M10 — React learning portal and browser Lab

**Status:** initial vertical slice implemented; research expansion and root-site promotion remain
future milestones.

1. Product foundation: land ADR 0019, route/content manifests, design tokens, responsive
   wireframes, the custom Docusaurus shell, Pagefind command palette, and generated data contracts.
2. Polished vertical slice: ship Home, Docs, API, Examples, Theory, Benchmarks, Research, and Lab
   routes using real fixtures and authoritative source adapters rather than placeholder science.
3. Browser Lab: generate TypeScript from the versioned JSON Schema; lazily load Pyodide and the
   local ScoreQuant wheel in a cancellable worker; synchronize controls, score-space graphics, and
   diagnostics; include one locked lazy marimo lesson.
4. Dual-site publication: assemble MkDocs at the existing root and React at `/portal/`; keep
   deployment preview-only. Move React to the root only after content/link parity and a reviewed
   redirect manifest.
5. Research growth: expand the opt-in claim preview into history, implication, counterexample, and
   evidence-provenance views without exposing private registry state.
6. Development blog (ADR 0020): the Docusaurus blog at `/blog`, rendered through the ScoreQuant
   shell, with one plain-English post per merged research or feature arc — negative results
   included — and a selective backfill of the arcs that changed direction.

**Gate:** strict TypeScript, lint, unit/component tests, schema consistency, broken-link failure,
desktop/mobile Playwright flows, automated accessibility plus keyboard/reduced-motion review,
non-Lab Lighthouse LCP below 2.5 seconds and CLS below 0.1 on CI, no Pyodide/marimo requests on
ordinary routes, representative manual visual inspection, and a seeded browser scenario agreeing
with native NumPy in under ten seconds after warm-up.

## M12 — Consolidation programme

**Status:** active; S1-S6 done; S7 unblocked, and S8 waits on it. The remaining sessions are the
user-facing half of the programme and were re-scoped on 3 September 2026 around one direction:
the portal becomes the site root and explains rather than sells, MkDocs narrows to the
exhaustive reference, and four detailed walkthroughs — one per input route, two on real data —
carry the applied stories.

Theorem research paused with P1 closed on DS19 (2 Sep 2026). With 0.1.0 out, the project reflects
on what it has before the next release. Four things were wrong when the milestone opened: the
manuscript was three research sessions behind the claim registry, the library carried pre-1.0
design debt that would be breaking to fix later, the portal narrated research with hardcoded
timelines and sold rather than explained, and half of the documented input routes had only toy
examples. S3 and S5 closed the first two. The remaining two are what the user-facing half
addresses, and they are the reason a released library is still not a presentable one: a reader who
follows the URL the package advertises arrives at an exhaustive reference that re-derives the same
three concepts up to seven times and never states the problem in plain language.

This milestone is a multi-session programme; its standing memory is
`docs/programme/README.md` (orchestrator contract and session prompt) and one packet per session
under `docs/programme/`, each closed by a plain-English report. Nothing else holds programme
status: this table is the single source of truth for what is queued, active, and done.

Four workstreams, each with its own gate:

- **W1 — Manuscript v9.** `agenticresearch/manuscripts/NOVELTY_LEDGER.md` labels every central
  statement as known / direct corollary / adaptation / apparently new / unresolved, with
  attribution; v9 folds in every finding since v8 (DS11–DS19, A-optimality, information
  efficiency, the new counterexamples) and corrects every entry of the README staleness ledger.
  **Gate:** every ledger row is placed in v9 or marked deliberately omitted with a reason; an
  independent fresh-context audit read of v9 against the ledger records a verdict per statement;
  `registry.py validate` is green.
- **W2 — Library design pass.** No exported name that nothing accepts; every published code
  string executes in a test; the backend is documented; a small error hierarchy names contract
  violations and theorem-backed refusals; `fit_quantizer` is one pipeline with the profiled guard
  at one boundary; validation is single-sourced; results are constructed once. **Gate:** golden
  engine and backend conformance suites bit-identical before and after; an architecture test pins
  the layering; ADR 0024 and the CHANGELOG record every breaking change.
- **W3 — Portal.** The portal is the public face, served at the site root, and MkDocs is the
  exhaustive reference under `/reference/`; narrative duplicated between them moves out of
  MkDocs. The front door explains the problem and hands the reader onward — no slogans, no proof
  strip, and every published snippet shown with its actual output. The hardcoded research
  timeline and graph are replaced by a plain-English research section written from the novelty
  ledger. **Gate:** every portal snippet is executed by a test and every output it displays is
  captured from a run rather than typed; every research page states who it is for and links every
  claim it makes; every pre-cut MkDocs URL resolves — 51 of the 53 through stubs from a committed
  redirect manifest, the site root and `/reference/` by deliberately serving new content, with the
  parity checked against the assembled tree rather than by eye; Playwright end-to-end runs in CI;
  the root deployment is live.
- **W4 — Showcases.** A realistic end-to-end example for each input route: score sample and
  density ratios (FlowCyt, already real), an analytic `ScoreFunction` with an explicit nuisance on
  the NumPy backend (Michelson fringe phase against a fringe-frequency nuisance), an executed
  `CentralLogRatioScore` path, and a HEP
  classifier route on the FAIR Universe HiggsML public dataset (DOI 10.5281/zenodo.15131565,
  CC-BY-4.0, Parquet), verified reachable by fetching and carrying an explicit tau-energy-scale
  nuisance; the FlowCyt three-interface fallback is cut because that dataset check succeeded.
  **Gate:** each example executes in both test tiers in fast mode, has its evidence JSON pinned,
  is reachable from the portal's walkthrough index, and the roadmap names the provenance of every
  number it reports.

Sessions (one branch, one PR, one closing report each; `Needs` is the merge lock):

| # | Session | Workstream | Needs | Status |
|---|---|---|---|---|
| S1 | Scaffold + public-surface truth pass | memory, W2 | — | done |
| S2 | Manuscript reconciliation + novelty ledger | W1 | S1 | done |
| S3 | Library internals refactor | W2 | S1 | done |
| S4 | Showcase foundations (Michelson phase, NumPy example, HEP data spike) | W4 | S3 | done |
| S5 | Manuscript v9 draft | W1 | S2 | done |
| S6 | Portal topology, reference cut, research narrative | W3 | S2, S3 | done |
| S7 | HEP classifier showcase (FAIR Universe HiggsML) | W4 | S4 | active |
| S8 | The four walkthroughs | W3, W4 | S6, S7 | queued |
| S10 | Portal front door: home, get-started, e2e in CI, deployment | W3 | S8 | queued |
| S9 | Closure: independent v9 audit, exit gate, teardown | all | S5, S8, S10 | queued |

Deliberately cut, because it serves no user: renaming the six iteration-budget parameters (one
table in the API guide instead); `PartitionResult.from_dict` (`Quantizer.save`/`load` is the
round trip); flattening or regrouping the public namespace; a fresh adversarial literature search
(P8 stays deferred; only attribution facts already in the README ledger are used).

One cut is retired. Moving the portal to the site root was cut on the grounds that ADR 0019
requires link parity and a redirect manifest. That reasoning held while the portal was a second
reading surface; it stops holding once the portal is the explanatory front door, because a
visitor who lands on the documentation URL — the one the published package advertises — then
arrives at the reference rather than at the explanation. S6 does the promotion and pays ADR 0019's
price directly: a committed manifest of every pre-cut MkDocs URL, and a test that fails if any of
them stops resolving.

**Exit gate:** all four workstream gates hold; every session row reads `done` or `cut`; the full
handoff gate and `pnpm validate` are green on `main`; the session prompt in
`docs/programme/README.md` is retired; M11's gate can be evaluated.

## M11 — First public release

**Status:** done. Tag `v0.1.0` was pushed on 30 August 2026 and both artifacts
(`scorequant-0.1.0-py3-none-any.whl`, `scorequant-0.1.0.tar.gz`) were published to PyPI the same
day. This status line said "the tag is unpushed and nothing is published" until 3 September 2026,
which had been false for four days; `CHANGELOG.md` carried the same error as `[0.1.0] —
unreleased`. Both are corrected. The published project page advertises
`https://vitalyvorobyev.github.io/scorequant/` as both Homepage and Documentation, which is why
S6's redirect manifest is not optional: that URL is the one the world already holds.

The library had been installable only from git. That is a real barrier: it makes the package
unusable in a locked dependency set, gives no stable artifact to cite, and means every reported bug
has to be traced to a commit rather than a version.

1. Version single-sourcing: `scorequant.__version__` resolved from installed metadata, so
   `pyproject.toml` stays the only place a version is written.
2. `CHANGELOG.md`, and `Homepage`/`Changelog` project URLs.
3. `release.yml`: tag-triggered, gated on the full handoff gate, publishing through PyPI Trusted
   Publishing so no API token exists. `workflow_dispatch` runs the same gate and build without
   publishing, so an artifact can be inspected before a tag exists.
4. Two guards that cannot be fixed after publication: the git tag must match the packaged version,
   and `twine check` must pass so the README does not render as raw text on the project page.

**Gate** (met for 0.1.0 except its first clause, which the publication predated; it now gates
the next release rather than the first): M12 is done; the full handoff gate passes; `uv build`
produces a `py3-none-any` wheel
and an sdist that `twine check` accepts; the wheel installs into a clean environment and
`import scorequant` there reports the packaged version and completes a fit-and-predict round trip
from the installed package rather than the source tree; the trusted publisher is configured on the
index; and the tag is pushed deliberately.

Publication is an authorized action, not a merge side effect. Landing this milestone does not
publish anything.

## Explicitly outside the development plan

An E-optimal solver is not planned. The E-optimality chapter and deterministic counterexample stay
as theory and boundary evidence, but there is no implementation milestone, public criterion, or
solver API. Reconsidering this decision requires a concrete application use case and a new roadmap
decision.

## Beyond 1.0

What stays deliberately out of scope, and why, in one place:

- **Population samplers, moment oracles, streaming aggregation** — three of the four capability
  gaps recorded in the pre-1.0 API audit (`docs/system-design.md`); no concrete application is
  forcing any of them yet. In likely order: samplers/oracles, then streaming aggregation and
  further exact-D factorization profiling. The fourth gap, a versioned non-pickle quantizer
  artifact, is no longer deferred: the NumPy backend made "fit here, predict there" concrete, so
  `Quantizer.save`/`Quantizer.load` landed with the deployable-rule split.
- **E/A-optimality** — theory and a boundary counterexample only ([Chapter
  11](book/ch11-e-optimality.md)); no implementation milestone, public criterion, or solver API.
  Reconsidering needs a concrete application use case and a new roadmap decision (see "Explicitly
  outside the development plan" above).
- **A Rust port of `certify.py`'s branch-and-bound search** — the one hot path the Phase 4
  profiling campaign found with no JAX kernel in its inner loop, measuring a flat ~34-40k nodes/s
  across a 260x range of tree sizes with roughly 38% of that time in NumPy allocation and
  dispatch (`benchmarks/README.md`). A port of `_Search` alone would plausibly return **>=40x**.
  Deferred: reconsider when certifying more than ~48 atoms becomes a user-facing requirement, and
  only after the cheaper preallocated-buffer/hand-rolled-determinant step is tried first; a
  compiled extension is a large change to the distribution story for one bounded diagnostic.
- **Algebraic reformulation of the D-exchange gain kernel** — expanding the quadratic form
  measured a 3.5x speedup on one chunk while staying in JAX, but it is not bit-identical to the
  residual-first formulation and needs its own ADR and error analysis before it can replace it
  (`benchmarks/README.md`, "Optimizations deliberately not taken").
- **Profiled-\(D_s\) compile-to-quantizer via the projected efficient-score interval rule** —
  research result DS15 (`agenticresearch/KNOWN_RESULTS/05b-ds-bridge.md`) names the deployable
  rule for `ProfiledDOptimality` results that `compile_quantizer()` refuses to produce, but only
  at global optima of conditionally centered, single-parameter-of-interest laws. The question
  this paragraph used to wait on (OP29, whether the exchange-stable non-global solutions the
  optimizer actually returns keep the same margins) is resolved for the deployment-facing scalar
  case: DS17 disproved the conditional route on the class (L) laws the library fits, DS18 gives
  exactly one exact off-(L) witness with positive transfer, and DS19 certifies a bracket for the
  scalar tilt dynamic program with strong duality false. There is no compile route to implement;
  the refusal stands, and the remaining vector branches of OP29 are academic rigidity questions.
  Reconsider only on a new theorem, not on a further open-problem resolution.
- **Signed weights and advanced statistical objectives** — remain gated on a new mathematical
  contract and independent use case. NumPy is now the approved second backend in M9; PyTorch still
  requires a concrete workload, complete capability mapping, conformance evidence, and benchmark.

## Full handoff gate

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
```
