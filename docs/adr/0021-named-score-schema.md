# ADR 0021: name the score coordinates, and keep the reference point out of the schema

**Status:** Accepted. Extends [ADR 0001](0001-score-contract.md) and
[ADR 0005](0005-explicit-representations.md).

## Context

A score table is a matrix of partial derivatives with one column per model parameter. The column
order carries the entire meaning of the table, and nothing in the library recorded it. The only
per-parameter-ordered structure was `ScoreProvenance.reference_point`, which holds values, not
names.

For a two-parameter demonstration this is tolerable. For a real problem it is not, and the
evidence was already in this repository: `examples/cell_population/profiled.py` declares

```text
INTEREST_INDEX = 4
```

under a ten-line comment explaining which cell population column 4 is and why it was chosen. That
comment exists precisely because there was nowhere to put the name. A user of a thirty-component
model has to remember that a reference component was absorbed, that no upstream step reordered the
columns, and that index 37 is still the parameter they meant. Reports made this worse by printing
`interest: (4,)`.

## Decision

Introduce `ScoreSchema`, a frozen tuple of parameter names, carried by `ScoreSample` and by
providers, and reaching both result types and the profiled report.

`ProfiledDOptimality.interest` accepts names or indices, never a mixture. Names are resolved to
score columns **exactly once**, at the public task boundary in `api.py`, immediately after the
sample is materialized. Every consumer downstream — the profiled objective in `partition.py`, the
Schur-complement algebra in `information.py`, the soft solver, the reports — continues to receive
integers and is unchanged. They read `interest_indices`, which is statically `tuple[int, ...]` and
raises by name if an unresolved criterion ever reaches a solver, so the single resolution point is
enforced rather than merely intended.

**The schema does not carry the reference point.** `ScoreProvenance.reference_point` already does.
Two homes for one fact drift apart, and the drift would be silent: nothing would notice a schema
naming five parameters beside a reference point with four entries. Instead the two are validated
against each other, and against the score dimension.

The division of labour is: `ScoreSchema` answers *what does each coordinate mean*;
`ScoreProvenance` answers *where did these numbers come from, and at which \(\theta_0\)*.

Providers supply the schema for the observation-space routes. `LinearComponentScore` derives it
from the component names its model already declares — the names existed, they were simply not
propagated. The others accept it explicitly.

Validation samples are now compared by parameter name when both sides declare one. The previous
check compared column counts, which cannot see a reordering.

## Consequences

`interest=("HSPCs",)` is available wherever a schema is, and reports print
`interest: HSPCs / nuisance: T cells, B cells, monocytes, mast cells`. The index form remains
fully supported and is still what the criterion stores after resolution, so `to_dict()` output and
every downstream computation are unchanged for existing callers.

A schema is optional. Nothing requires one, and omitting one costs only the names.

The one asymmetry left: `efficient_score_bound` takes a raw array and indices. Extending it to
accept a `ScoreSample` would let names work there too, and is deferred rather than decided against.
