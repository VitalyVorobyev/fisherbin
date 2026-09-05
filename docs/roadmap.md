# ScoreQuant development roadmap

This is the single executable planning document. User-facing reference pages describe only
implemented interfaces. Delivered milestones are summarized in one table near the end; their
detail lives in the ADRs, `CHANGELOG.md` and git history, not here.

## M13 — Focused research and teaching

**Status:** active; phases A and B done 5 September 2026, C is next. The owner's review of the
portal the same day reduced it to four surfaces and recast the Michelson page as an article
([ADR 0031](adr/0031-portal-reduced-to-four-surfaces.md)); C applies that form to the other three pages.
This is the current execution entry point. The site topology is
[ADR 0027](adr/0027-landing-page-at-the-root.md): landing `/`, documentation `/docs/`, portal
`/portal/`. Keep those routes during this milestone.

**Basis:** [review and evidence](programme/2026-09-05-review.md),
[ADR 0028](adr/0028-focused-research-and-teaching.md). The objective is a reader who can select
and reproduce the correct statistical task, and research that changes a concrete inference
or implementation decision. No new solver, public abstraction or site-stack migration is required.

### Execution order and gates

| Phase | Status | Depends on | Outcome and owned surface | Validation and stop condition |
| --- | --- | --- | --- | --- |
| A — Interpretation and geometry | done (5 Sep 2026) | review | Correct remaining theorem summaries, route-to-example mismatches and the `ScoreSpace` metric/boundary depiction; state the surrogate meaning at every headline. Owns portal explanations, book summaries and chart data contract. | Test plotted boundaries against `predict_scores` with a nonidentity metric and unequal display-axis scales, or remove the unsupported boundary overlay. Explain label colors, axes and cached/live states. No remaining false guarantee in audited entry paths; targeted tests, full handoff gate and `pnpm validate` pass. |
| B — One teaching exemplar | done (5 Sep 2026) | A | Rework Michelson into problem → model/score → admissible labels → run → evaluation → one experiment. Distinguish contiguous physical segments from potentially disjoint electronic labels at the opening. Keep existing evidence and URLs. The free-form Lab console is retired and `/portal/lab/` is the lesson index; browser computation is reached only through a lesson's experiment ([ADR 0029](adr/0029-lessons-replace-the-free-form-lab.md)). The lesson index was itself retired the same day ([ADR 0031](adr/0031-portal-reduced-to-four-surfaces.md)). The Michelson page keeps the seven-step order as the author's checklist, reads as an article (instrument, history, what is measured, the data, the objective, the result, one experiment), states the disjoint-label class in prose, and its experiment refits the committed profiled partition in the browser. The human reader gate stays pending. | A reader outside the authoring context can identify POI/nuisance, reference law, task/output, score provenance and the meaning of the benchmark, and reproduce the result. Keyboard/reset/static-fallback checks pass. Stop after this page passes; do not mass-rewrite the rest before the pattern works. |
| C — Four coherent walkthroughs | queued | B | Apply the article form of the Michelson page to ratios, FlowCyt and HEP: subject and data first, the contract in prose, numbers in sentences, one experiment. Give each page its distinct lesson from the review. The portal entry, navigation and index cards are done (ADR 0031). | Each page states its full problem contract within its opening prose, has a runnable path and one meaningful interaction; all numbers retain provenance and information kind. Reader checks for all four, snippet/fact tests, `pnpm validate`, desktop/mobile e2e, assembly/link gate. Preserve old pages until their replacement covers their examples. |
| D — Frozen-rule evidence | queued | reset complete; independent of B/C | Execute the P2 packet in `agenticresearch/WORK/active/SCORE-ORACLE-ROBUSTNESS.md`. Owns that packet and its research/example artifacts; no production estimator yet. | One reproducible truth-score evaluation with explicit conditioning and a theorem, estimator limitation or counterexample. Independent audit for promotion; registry/index/fixture gates. At the packet's effort checkpoint, close, reduce or name a precise blocker; do not activate unrelated DS work. |
| E — Existing formal pilot integration | queued | separate branch review | Reconcile `codex/formal-verification-pilot` with current registry, CI, ADR numbering and roadmap; preserve reviewed scalar spec and coverage. No expansion to population or Ds proofs. | `lake build --wfail`, statement correspondence audit, allowed-axiom audit, checker and main regression gates. Resolve ADR 0024/M12 collisions before integration (the pilot's ADR takes number 0030; 0029 is taken). Merge requires owner authorization. Stop at accepted pilot; next formal dependency gets its own bounded decision. |
| F — Research graph semantics | queued | D yields a stable handoff; E metadata known | Separate theorem prerequisites from audit/evidence/remainder links. Owns registry schema/tool/tests and migrated links. Preserve claim IDs, proof locations and statuses. | Inspect every moved edge; mathematical dependency DAG validates, audit links remain retrievable, indexes regenerate, old fixtures pass. A compile query no longer imports an open complexity problem as proof authority. Do not split the long Ds proof file until link migration is verified. |

A–C form the documentation spine. D is the **only active scientific question** once started;
E is bounded verification of existing work, not a second exploratory programme. These rows are
not a mandate to run six agents. Start A next; D may run in an independent research session.

### Reader acceptance script

Use a fresh reviewer who has not authored the page. Ask them, without hints, to:

1. State what is observed, what is estimated, and what K constrains.
2. Identify whether the output labels existing rows or predicts labels for future scores.
3. Identify the reference point and whether the information is exact-model or surrogate.
4. Reproduce the displayed fit and explain its hard metric, evaluation split and baseline.
5. Change one control and explain why the output changed and which guarantee still applies.

Record misunderstandings and the corresponding edit. Automated checks are necessary but cannot
replace this script. An agent review is a useful rehearsal; it is not evidence of actual user
usability. Owner/external-reader feedback is the final learning-quality gate, not a prerequisite
to implementing a concrete page for review.

### Session workflow

The implementer reads this current phase, the relevant contributor rules, and its named source
files. Work from the code and mathematical record; historical session prompts are not active
instructions. Delegate only an independently useful read, implementation boundary or audit.
The research derivation owner remains responsible for its mathematics; its promotion audit uses
a fresh context and the frozen statement/artifact. No model names are prescribed.

Each handoff records: the user/scientific decision changed, files and evidence, exact checks,
remaining uncertainty, and one next action. The coordinator verifies any decisive negative
finding before cutting a capability. A remaining question is parked unless deliberately selected
in the research queue. The paper is updated from audited results when a publication decision
requires it, not after every packet.

### Explicit cuts and deferred work

- Retire M12's universal delegation/model-tier workflow from future execution; its packets are
  deleted and live in git history.
- Park OP31 exact Ds bit-complexity and the broad Ds margins tail in the research queue.
- Keep generic profiled compilation unsupported; a restricted research certificate does not
  imply a stable production compiler.
- Keep the two task APIs, versioned quantizer, providers, shared backend mathematics and fixtures.
- Defer a public uncertainty API, universal bin-budget recommender, new solvers, full-site
  migration and full theorem-chain formalization until their own evidence supports them.

### Risks and decision points

| Risk / unknown | Owner and resolution |
| --- | --- |
| Attractive figures imply unsupported geometry | A implementer supplies numerical correspondence tests; reviewer checks actual plotted meaning. |
| Michelson labels require hardware freedom the reader lacks | B author states the admissible label class before comparison; contiguous-only hardware is a separate problem. |
| No truth-score oracle on real data | D researcher states simulation/conditional scope; do not infer true information from calibration closure alone. |
| Formal branch carries obsolete planning identifiers and CI assumptions | E integrator reconciles only pilot changes; preserve later main-branch work and record the checker actually run. |
| Human learning gate cannot be automated | C owner schedules reader review after a concrete pilot; until then report that gate as pending. |
| Graph cleanup accidentally changes proof authority | F migration reviewer audits relations and status preservation; no automatic status downgrades. |

## Delivered milestones

One row per milestone. Nothing here is a standing instruction; the durable decisions are the
ADRs named in the last column.

| Milestone | Delivered | Durable record |
| --- | --- | --- |
| M1 Canonical contracts and documentation | Consistent naming; population design, empirical quantizer fitting and finite assignment kept distinct; sources separate from providers and exact from surrogate information; the 1D-first book, glossary, bibliography, examples suite and the six-page FlowCyt study; the profiling campaign to \(N=10^6\). | ADR 0001–0010, 0016; `docs/book/`, `docs/usecases/flowcyt/`, `benchmarks/README.md` |
| M2 Exact finite D core | Exact cell statistics, rank-two relocation gain, deterministic monotone exchange, terminal scan, small-instance exhaustive oracle, explicit compilation. | ADR 0009, 0014 |
| M3 Task-explicit API | `optimize_partition`/`PartitionResult` and `fit_quantizer`/`QuantizerResult`; criterion plus solver configuration pairs; old fitting names removed without aliases. | ADR 0009, 0011, 0013 |
| M4 Sources and providers | `ScoreSample`, `ObservationSample`, bounded tensor-quadrature `IntegrationSource`; the provider protocol; named score schema and provenance. | ADR 0010, 0021, 0022 |
| M5 Book and FlowCyt capstone | The task-explicit 600,000-cell workflow with the exact-D reference on the frozen sample; exact rank-two state updates at one million rows; audited data reconstruction. | `docs/usecases/flowcyt/`, ADR 0015 |
| M6 Profiled \(D_s\) | Finite profiled exchange, the soft inductive solver, the efficient-score upper bound, the exact scalar interval dynamic program. | ADR 0014, 0015 |
| M7 Certificates, scale and persistence | Exchange-stability and geometry reports, branch-and-bound `certify_partition`, tolerance-consistent verification, the versioned `Quantizer` artifact. | ADR 0014, 0016, 0023 |
| M8 Density ratios | Exact densities, model density ratios and scores named as the representation layer; `DensityRatioScore`, `CentralLogRatioScore`, ratio provenance and the closure diagnostic. | ADR 0017 |
| M9 Explicit multi-backend execution | `ExecutionConfig`; JAX and NumPy behind one mathematical core; one conformance suite; the browser wheel. | ADR 0018 |
| M10 React portal and browser Lab | The Docusaurus shell, generated data contracts, the Pyodide Lab, the development blog. | ADR 0019, 0020 |
| M11 First public releases | 0.1.0 on 30 August 2026 and 0.2.0 on 4 September 2026 through PyPI Trusted Publishing, gated on the full handoff gate. | `CHANGELOG.md`, `.github/workflows/release.yml` |
| M12 Consolidation programme | Novelty ledger and manuscript v9; the error hierarchy and one fit pipeline; the HEP classifier showcase; the four walkthroughs; the portal launch, whose root placement was then reversed. Closed 4 September 2026. | ADR 0024–0027, `CHANGELOG.md` |

### Standing gates carried over

These clauses were stated inside the delivered milestones and still apply.

- One glossary; no nonexistent API in a published page; every published code fence executes in a
  test; MkDocs builds strictly.
- Every number quoted from a study or benchmark is asserted from committed evidence
  (`tests/test_evidence_suite.py`, `tests/test_walkthrough_facts.py`,
  `benchmarks/bench.py --check`).
- Certification is D-only and never runs implicitly (ADR 0014); every certificate and geometry
  verification states the `gain_tolerance` it holds at (ADR 0016).
- A compiled rule reproduces every positive-weight training label of the partition it came from.
- Backend parity tolerances are pinned in `tests/test_execution_backends.py`. In float32 only the
  continuous quantities are compared across backends: a relocation gain can fall inside the float32
  noise floor, so the discrete solvers may reach different, individually exchange-stable optima.

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
- **Research views in the portal** — history, implication, counterexample and evidence-provenance
  views of the claim registry (the last open item of M10) remain unscheduled; the plain-English
  research section is the published surface.
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
