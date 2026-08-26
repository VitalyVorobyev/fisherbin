# ADR 0017: density ratios are a first-class statistical representation

**Status:** Accepted; partially supersedes [ADR 0012](0012-classifier-callback-boundary.md) and
extends the supersession of [ADR 0008](0008-classifier-posterior-bridge.md). Clarifies
[ADR 0003](0003-small-core.md).

## Context

The score is the gradient of a log density ratio, so absolute densities are never required to
build it: for component models the relative densities \(\phi_k/\phi_{\rm ref}\) determine every
score coordinate, up to a common event-wise factor that cancels. The library nevertheless treated
the *classifier* as the abstraction for estimated scores (`ClassifierScore` plus two closed
transforms), and the density ratio — the actual statistical estimand — was computed twice
internally and surfaced nowhere. Classifiers are only one ratio estimator; direct estimators
(KLIEP, uLSIF), calibrated neural likelihood-ratio models, and analytic ratio formulas target the
same object. The FlowCyt application had already grown a de-facto ratio provider and a
ratio-closure diagnostic outside the library.

Scores remain the optimizer contract ([ADR 0001](0001-score-contract.md) stands), and exact
density APIs remain (`LinearComponents`). The question was where the ratio belongs between them.

## Decision

Name the ratio layer and decompose the classifier into it.

- `ratios.py` owns the ratio algebra: `ratios_from_posteriors` (prior correction),
  `mixture_scores_from_ratios` (normalized-simplex parameterization),
  `IntensityParameterization`/`MixtureParameterization` (declared ratio-to-score maps), and
  `ratio_closure_report` (the \(\int r_k\,d\mu = 1\) diagnostic, promoted from the FlowCyt
  application). `scores_from_components` doubles as the intensity ratio-to-score map through its
  documented gauge invariance; no twin function is added.
- `DensityRatioScore` pairs a ratio callback with a declared parameterization;
  `DensityRatioScore.from_classifier` composes the classifier chain
  (posteriors → prior-corrected ratios → scores) and can never claim exact provenance.
  `CentralLogRatioScore` absorbs the central finite-difference construction as one standalone
  provider. `ClassifierScore`, `MixturePosteriorTransform`, `CentralLogRatioTransform`, and
  `mixture_scores_from_posteriors` are removed without aliases — a surviving wrapper would be a
  parallel path to the same scores.
- `ScoreKind` replaces `"estimated_classifier"` with `"estimated_ratio"`; the classifier is an
  estimator identity, not a provenance kind. `ScoreProvenance` gains a structured
  `ratio: RatioProvenance` record (estimator, parameterization, reference fractions or
  coefficients, reference component, training priors, calibration, finite-difference offsets),
  sufficient to reconstruct how the representation was obtained. `exact_fisher` stays derived from
  `kind`; estimated ratios cannot claim exact Fisher semantics, and closure never upgrades them.
- Model density ratios and importance ratios are kept in different places by construction: model
  ratios enter through providers and build scores; importance ratios \(p_{\theta_0}/g\) are
  source weights and never pass through a provider. The two kinds never share an argument.

Ratio *estimation* — training, splitting, calibration policies, direct-estimator fitting — stays
outside the core, exactly as ADR 0012 held for classifiers. Naming the estimand is not "learned
score estimation" in the sense ADR 0003 defers; the library ships the exact algebra and the
diagnostic, not the estimator.

## Consequences

- The classifier is no longer special: every ratio backend enters through one provider with one
  provenance schema, and the docs present the classifier as one implementation of density-ratio
  estimation.
- Estimated-score results are labeled as before (`information_kind ==
  "supplied_score_surrogate"`), now with reconstructible ratio provenance behind them.
- The FlowCyt closure audit and the door-3 example consume `ratio_closure_report` instead of
  bespoke normalizer code, giving the diagnostic two independent uses plus an analytic
  laboratory (`DensityRatioScore` over \(\Phi/\phi_{\rm ref}\) reproduces
  `LinearComponentScore` exactly).
- A generalized local-ratio provider (asymmetric offsets, arbitrary directions) remains a
  possible future extension; it has no example yet and is deliberately not added.
