# ADR 0012: keep classifier training outside the core

**Status:** Accepted; partially supersedes ADR 0008.

## Context

Calibrated classifiers can estimate local likelihood ratios or relative mixture components, but
training frameworks, splits, preprocessing, and calibration policies are application-specific.
Treating an estimated score as exact would conflate estimator error with quantization loss.

## Decision

Expose a framework-neutral `ClassifierScore` around a ready callback and one of two pure transforms:
central calibrated log-ratio to score, or multiclass posterior to constrained mixture score. Apply
explicit training-prior correction. Keep fitting, calibration, and cross-fitting outside the core.
Classifier provenance is always estimated and cannot claim exact Fisher semantics.

## Consequences

ScoreQuant gains no classifier dependency. Applications can use any model but must retain model,
calibration, feature-transform, split, and validation provenance themselves. Supplied-score
information is reported as a surrogate unless separately validated against exact scores.
