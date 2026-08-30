# ADR 0022: make `ScoreProvider` a protocol, not a closed union

**Status:** Accepted. Extends [ADR 0010](0010-source-provider-separation.md) and
[ADR 0017](0017-density-ratio-representation.md).

## Context

`ScoreProvider` was a type alias:

```python
type ScoreProvider = ScoreFunction | LinearComponentScore | DensityRatioScore | CentralLogRatioScore
```

That is a closed list. An external estimator — a MadMiner score model, a direct density-ratio
estimator, a package that already emits scores — could not *be* a provider; it had to be wrapped in
`ScoreFunction` first. The union also was not exported, so the name in every signature referred to
something a caller could not import.

This contradicts the architecture the rest of the library states: arbitrary statistical machinery
produces a score, and ScoreQuant begins there. The union made "arbitrary" mean "one of these four".

## Decision

`ScoreProvider` is a `runtime_checkable` `Protocol` with two members: a `provenance` and a
`score(observations)`. It is exported. The four built-ins become implementations of it rather than
its definition.

`score` takes observations alone. The execution backend is ambient context established by the
public task through a contextvar, so an outside implementation needs no knowledge of
`ExecutionConfig` — which was already true of the call site, and is now true of the contract.

`runtime_checkable` proves only that the attributes exist. The provenance type is therefore checked
separately at the boundary: a provider whose `provenance` is a string would otherwise reach the
result and take part in deciding whether exact-Fisher language is justified. Validation uses
`isinstance`, never `issubclass`, because a protocol with non-method members supports the first and
raises `TypeError` on the second.

A provider may additionally expose `schema` ([ADR 0021](0021-named-score-schema.md)). This is
deliberately *not* in the required contract: adding it would make the minimal external
implementation larger for a feature it may not have names for. It is used when present.

The argument that carries a provider is renamed `score=` to `provider=`. It never accepted a score
array or a bare score function, and a `ScoreSample` rejects it outright; the old name described the
value's subject, not its type. No alias is kept — [ADR 0007](0007-generic-api-evolution.md) permits
the break, and a surviving alias would be the overlapping entry point the contributor contract
forbids.

## Consequences

An external class is a provider with no import from ScoreQuant beyond `ScoreProvenance`:

```python
class MyExternalScore:
    provenance = sq.ScoreProvenance(kind="estimated_ratio")

    def score(self, observations):
        return my_package.evaluate(observations)
```

The built-ins remain the recommended route for the representations they cover, because they also
carry the provenance and parameterization bookkeeping a hand-written provider would have to repeat.
