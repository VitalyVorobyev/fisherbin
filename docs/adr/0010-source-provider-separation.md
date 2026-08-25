# ADR 0010: separate sources from score providers

**Status:** Accepted.

## Context

The objective is an expectation under a score law. An observation-to-score callback provides a map
but no measure; bounds provide a domain but no density.

## Decision

Represent the measure with `ScoreSample`, `ObservationSample`, or `IntegrationSource`, and the map
with `ScoreFunction`, `LinearComponentScore`, or `ClassifierScore`. Require an explicit density or
intensity for bounded integration. Reject a provider without a source and reject a provider paired
with an already scored sample.

## Consequences

Equivalent materializations share one numerical core. Population samplers and moment oracles may
later extend the source side without changing score-provider semantics.
