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

## M2 — Exact finite D reference core

**Status:** implemented baseline.

- Exact cell statistics, rank-two relocation gain, deterministic monotone exchange, terminal scan,
  small-instance exhaustive oracle, zero-weight handling, and explicit compilation.
- Regression gates cover direct recomputation, monotonicity, small global optima, the D separation
  bound, invariants, and reproduction of positive-weight labels.

**Next:** profile factorization updates before optimizing performance; add branch-and-bound only
after a concrete certificate workflow exists.

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

In order: population samplers and moment oracles; branch-and-bound certificates; streaming and
factorization updates; then versioned persistence. Signed weights, additional backends, and advanced
objectives remain outside scope until their mathematical contracts and independent use cases exist.

## Explicitly outside the development plan

An E-optimal solver is not planned. The E-optimality chapter and deterministic counterexample stay
as theory and boundary evidence, but there is no implementation milestone, public criterion, or
solver API. Reconsidering this decision requires a concrete application use case and a new roadmap
decision.

## Next execution order

1. Profile exact-D factorization updates and chunked candidate scans before increasing the bounded
   partition-table capacity.
2. Design and gate finite profiled-\(D_s\) exchange before exposing any new public API.
3. Add population samplers and moment oracles, then certificates, streaming, and persistence in
   that order.

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
