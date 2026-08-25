# ADR 0015: efficient-score upper bound and solver initialization

**Status:** Accepted.

## Context

Profiled-\(D_s\) exchange has no cheap certificate of its own: `certify_partition`'s
singleton-completion bound is D-only because the profiled Schur objective is not Loewner-monotone
under cell refinement. A caller still needs some way to judge how far a profiled exchange result is
from the best any hard rule could do, and every exchange solver still starts from an initial
labeling that was, until now, always k-means++ or random.

## Decision

Add `efficient_score_bound`, returning `EfficientScoreBound`. It builds the full-data efficient
score \(\hat s = s_\psi - B^\ast s_\lambda\) from the *unbinned* information matrix and applies
efficient-score domination: the same-label profiled information of any hard rule with at most
`n_bins` cells is bounded by the between-cell information of \(\hat s\) under that rule. For one
scalar parameter of interest — the only case supported, since a multivariate efficient score would
need a genuine multivariate D solver and the returned value would become a heuristic rather than a
certificate — the maximizing rule over \(\hat s\) has ordered interval cells, found exactly by the
same weighted interval dynamic program `ScalarDPConfig` uses. `EfficientScoreBound.upper_bound`
uses `PartitionResult.objective`'s convention for `ProfiledDOptimality` (log of an uncentered
between-cell second moment) so `gap_to(result)` is directly comparable and meaningful only when the
result was built from the same scores and weights.

`EfficientScoreBound.labels` double as a solver initializer: `optimize_partition` accepts an
`initial_labels` argument that replaces the seeding of restart 0 only — `config.init` and `n_init`
(or `n_restarts`) still govern every other restart — and the guarded Mahalanobis-Lloyd solver
starts from the supplied labels directly. Passing `EfficientScoreBound.labels` starts profiled
exchange inside the efficient-score geometry instead of at generic k-means seeding.

Separately, `fit_quantizer` gained a `diagnostics: "final" | "endpoints" | "full"` knob controlling
how much of the recorded center-snapshot history is re-scored into
`trace.train_hard_retention`/`trace.validation_hard_retention`. Each full-dataset re-score is an
`O(N)` pass, so re-scoring every snapshot of a long soft-Voronoi schedule is expensive; the default
is `"endpoints"` (first and terminal snapshots only, two passes), `"final"` scores only the
terminal snapshot, and `"full"` scores every snapshot. Unscored snapshots hold `nan` so the returned
history always stays aligned with `trace.steps` regardless of mode; the choice affects only this
diagnostic history, never `centers`, `labels`, or either information report.

## Consequences

A profiled exchange result now has an inexpensive, criterion-matched upper bound even though it has
no branch-and-bound certificate of its own. Solver initialization is a documented contract
(`initial_labels` affects restart 0 only) rather than an implementation detail, so a certified or
externally computed starting labeling composes with the existing restart machinery instead of
bypassing it. `diagnostics="endpoints"` trades some mid-run retention visibility for a cheaper
default fit; callers who need the full curve opt in explicitly.
