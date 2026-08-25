# ADR 0008: expose only the mathematical classifier-posterior bridge

## Status

Superseded in part by [ADR 0012](0012-classifier-callback-boundary.md). The pure
posterior transformation remains; a framework-neutral ready-callback provider
is now also public. Training remains application code.

## Context

Finite-mixture applications often estimate component density ratios with a
classifier. The training algorithm, feature preprocessing, group splitting,
posterior calibration, and prior estimation vary by application. The algebra
that converts ready posteriors into simplex score coordinates does not.

Keeping that algebra in each example duplicates validation-sensitive code.
Moving the full classifier workflow into the library would create an unstable,
estimator-specific API and blur the boundary between score estimation and hard
partitioning.

## Decision

Expose one array function:

```python
mixture_scores_from_posteriors(
    posteriors,
    class_priors,
    reference_fractions,
    *,
    reference_component=-1,
)
```

It validates explicit simplex contracts and computes class-prior-corrected
finite-mixture scores. It performs no clipping or hidden renormalization.

Classifier training, calibration, fold construction, prior estimation, and the
downstream mixture likelihood remain application code. There is no classifier
protocol, adapter object, dependency, or `fit_from_posteriors` entry point.

## Consequences

- Any classifier can supply the posterior matrix.
- The public API gains one stable statistical transformation rather than a
  parallel fitting workflow.
- Applications remain responsible for proving calibration and leakage control.
- Tutorials explain that classifier ratios are estimates, not oracle ratios.
