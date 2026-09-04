# Changelog

All notable changes to ScoreQuant are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[semantic versioning](https://semver.org/spec/v2.0.0.html) — with the usual `0.x` caveat that the
public API may still change between minor releases.

## [Unreleased]

Changes on `main` since 0.1.0. Nothing below has been released: verified against the `v0.1.0`
tag, where `RefusalError` does not exist anywhere in `src/` and `LinearProblem` is still
exported. These sections were appended while the version heading read `unreleased`, and a later
commit dated that heading, which retroactively asserted they had shipped.

### Site

- The learning portal is published at the site root, with the strict MkDocs reference beneath it
  at `reference/`, assembled and deployed by a single workflow (ADR 0026). A pull request builds
  and uploads the whole tree; only a push to `main` deploys.

### Contracts

- Weight and `rank_rtol` validation is single-sourced; the messages are the `ScoreSample` ones
  everywhere.

### Errors

- Every deliberate exception is a `ScoreQuantError`. `ContractError` (a `ValueError`) reports a
  malformed call; `RefusalError` (a `RuntimeError`, deliberately not a `ValueError`) reports a
  theorem-backed refusal and carries `counterexample`, the registry id that forces it.
  `compile_quantizer()` on an unstable, profiled, or geometrically degenerate partition and a
  rank-deficient profiled `fit_quantizer` now raise `RefusalError`.

### Removed

- `LinearProblem` and `LinearComponents.evaluate` — exported and documented but accepted by no
  task; use `LinearComponents.evaluate_components` plus `scores_from_components` to hand an
  evaluated component matrix to `optimize_partition` or a `ScoreSample`.

## [0.1.0] — 2026-08-30

First public release. Everything below describes the shape being released rather than a change
against a previous version, since there is none.

### Two tasks, kept separate

- `optimize_partition(scores, ...) -> PartitionResult` optimizes the labels of one fixed weighted
  score table. It is transductive, and the result has no generic predict method.
- `fit_quantizer(source, provider=..., ...) -> QuantizerResult` fits a reusable rule on score
  space. Prediction is always the explicit `predict_scores`.
- The one crossing between them is a theorem, not a convenience:
  `PartitionResult.compile_quantizer()` returns the Mahalanobis-Voronoi rule that an
  exchange-stable, nonsingular D-optimal partition already is, and refuses otherwise.

### Score access

- Three routes to a score, all reaching the same optimization problem: precomputed vectors
  (`ScoreSample`), an explicit model or oracle (`ScoreFunction`, `LinearComponentScore`), and
  density ratios (`DensityRatioScore`, `CentralLogRatioScore`).
- `ScoreProvider` is a public runtime-checkable protocol, so an external estimator is a provider
  without being wrapped.
- `ScoreSchema` names the score coordinates, so a profiled criterion can declare
  `interest=("HSPCs",)` instead of `interest=(4,)` and reports print names.
- Sources and providers are separate contracts. Model density ratios build scores and enter through
  providers; importance ratios reweight the measure and enter as source weights.

### Objectives, solvers and certificates

- `DOptimality`, `ProfiledDOptimality` and `NormalizedTrace`, paired with a closed set of solver
  configurations. An unsupported pairing is rejected before any optimization runs.
- Exact positive-gain D exchange, guarded Mahalanobis-Lloyd, annealed soft Voronoi, weighted
  k-means, and an exact scalar interval dynamic program.
- Certificates are explicit, separately invoked operations that never run silently during fitting:
  `exchange_stability_report`, `certify_partition`, `efficient_score_bound`, and the measured
  geometry reports.

### Deployment

- `Quantizer` is the deployable rule, separate from the record of the fit. `Quantizer.save` writes
  a versioned, non-pickle artifact that loads and predicts in a process with no JAX installed.
- Every public entry point takes `execution=`. JAX is the default runtime; NumPy is the supported
  portable one, which is what makes the browser and JAX-free deployment possible.

### Contracts

- Public arrays are always `numpy.ndarray`. The package never mutates global JAX configuration at
  import, so 64-bit precision stays an application choice.
- Scores are never centred; numerically singular Fisher directions are projected out rather than
  repaired with a ridge; validation data is diagnostic only.
