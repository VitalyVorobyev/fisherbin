# ADR 0001: Scores are the core data contract

**Status:** Accepted

## Decision

The core optimizer accepts weighted score vectors:

```text
scores  [N, P]
weights [N]  # optional
```

Score generation is upstream. Linear components, analytic likelihoods, autodiff, simulators, and learned estimators are adapters to this contract.

## Why

This is the smallest domain-independent boundary and keeps the optimization code independent of observation dimension and model implementation.
