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
- `ScoreFunction`, `LinearComponentScore`, ready `ClassifierScore`, central-ratio and mixture
  transforms, and score provenance.
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

## Explicitly outside the development plan

An E-optimal solver is not planned. The E-optimality chapter and deterministic counterexample stay
as theory and boundary evidence, but there is no implementation milestone, public criterion, or
solver API. Reconsidering this decision requires a concrete application use case and a new roadmap
decision.

## Beyond 1.0

What stays deliberately out of scope, and why, in one place:

- **Population samplers, moment oracles, streaming aggregation, versioned persistence** — the
  four capability gaps recorded in the pre-1.0 API audit (`docs/system-design.md`); no concrete
  application is forcing any of them yet. In likely order: samplers/oracles, then streaming
  aggregation and further exact-D factorization profiling, then a non-pickle
  `save_quantizer`/`load_quantizer` artifact.
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
- **A second numerical backend, signed weights, advanced statistical objectives** — gated on an
  approved roadmap change per `AGENTS.md`; none is planned.

## Full handoff gate

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
```
