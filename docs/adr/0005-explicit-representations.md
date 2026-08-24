# ADR 0005: Make variables, components, and scores explicit API layers

**Status:** Accepted

## Context

A bare matrix cannot communicate whether its columns are physical variables, evaluated model components, or score coordinates. Reusing one overloaded fitting function would make prediction semantics equally ambiguous.

## Decision

Expose three entry points: `fit(X, model=...)`, `fit_components(Phi, coefficients=...)`, and `fit_scores(scores, ...)`. Each returns a result whose `predict` method accepts the same representation used during fitting. All paths delegate to the score-space implementation.

`LinearComponents` freezes callable order, names, coefficients, and optional variable metadata. A high-level fitted result retains that model, so callers do not resupply it for prediction. `LinearProblem` represents an already evaluated component matrix and is accepted by `fit_components`.

Do not add an `optimize` alias. The explicit fitting names are sufficient and avoid a fourth overlapping entry point.

## Consequences

The pre-release `fit(scores, ...)` prototype becomes `fit_scores(scores, ...)`. This intentional hard break makes the common workflow clearer before a stable release. Model callables remain in-memory concerns and are omitted from JSON-ready result metadata.
