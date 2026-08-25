# ADR 0011: keep solver semantics criterion-specific

**Status:** Accepted.

## Context

Exchange, Lloyd, and soft optimization do not make identical guarantees across matrix criteria.
Counterexamples disprove a generic finite-assignment-to-geometry rule for profiled \(D_s\) and E.

## Decision

Use explicit criterion and solver configuration types and validate their pairings. D exchange may
compile at verified stability. Normalized trace uses weighted k-means. Soft D optimizes a
differentiable relaxation and reports hardening separately. Do not expose a generic criterion
plugin until stable reusable semantics exist.

## Consequences

New criteria require their own mathematical gate, result diagnostics, finite solver, and inductive
solver contract before appearing in public reference pages.
