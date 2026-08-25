# ADR 0009: separate finite partitions from quantizers

**Status:** Accepted; supersedes ADR 0005.

## Context

Optimizing labels for a fixed table and learning a rule for unseen scores are different
mathematical problems. A finite labeling alone does not specify prediction away from its rows.

## Decision

Expose `optimize_partition` returning `PartitionResult` and `fit_quantizer` returning
`QuantizerResult`. A partition has no prediction method. A quantizer predicts only from explicit
scores through `predict_scores`.

Allow explicit D compilation only after a positive-definite, one-point-exchange-stable state and
only when its Mahalanobis rule reproduces every positive-weight training label. Do not infer a
future-event rule from finite profiled-\(D_s\) or E labels.

## Consequences

The former `fit`, `fit_components`, and `fit_scores` APIs are removed without aliases. Callers must
choose the actual task. Result types cannot accidentally promise unsupported prediction semantics.
