---
title: What cannot be certified
sidebar_label: What cannot be certified
sidebar_position: 5
---

# What cannot be certified

The previous page listed what is proved. This page lists where those proofs stop, which is the part
that decides whether a given result may be relied on. Most of the entries are **exact
counterexamples**: small tables of rational numbers, enumerated exhaustively, that show a plausible
statement is false. Four of them are wired into the library, which refuses the operation they
forbid and names them in the error message.

One piece of vocabulary first. The ledger labels a counterexample *unresolved* when no targeted
prior-art search has been recorded for it. That label is about attribution, not about correctness —
the examples below are verified in exact arithmetic and carry regression tests. It means only that
they are presented as witnesses and diagnostics, never as claims of priority.

## The Voronoi structure does not run backwards

Exchange stability implies a nearest-centre structure. The converse is false: a partition can be a
fixed point of its own nearest-centre rule and still admit a single relocation with a strictly
positive exact gain ([D-VORONOI-NOT-EXCHANGE](/research/claim-record#d-voronoi-not-exchange)). The witness
is a four-row, one-dimensional, two-cell example.

*Consequence for a user.* "The labels look geometric" is not evidence that the partition is stable,
and stability — not the appearance of geometry — is what licenses compilation. This is why
`compile_quantizer()` refuses a partition whose stability certificate says `False`, citing
`CE-D-VORONOI-CONVERSE-001` — the boundary fixture of
[D-VORONOI-NOT-EXCHANGE](/research/claim-record#d-voronoi-not-exchange) — and points at the remaining gain
so you can see how far off it is.

The ledger records the nearest precedent as the analogous statement for sum-of-squared-errors,
where Lloyd fixed points are known not to be Hartigan-stable.

## Duplicate observations must be merged first

The theorem assumes coincident score rows have been merged into one weighted atom. Without that
assumption it is false: identical score rows sitting in different singleton cells can make a
partition *vacuously* stable — there is no move that changes anything — while strict nearest-centre
assignment and deterministic label reproduction both fail
([D-UNMERGED-DUPLICATES-FAIL](/research/claim-record#d-unmerged-duplicates-fail)). The witness is
one-dimensional with three singleton cells and two rows equidistant from their competing centres.

*Consequence for a user.* Merging duplicates is part of the contract, not an optimization. The
solver refuses a terminal state whose own Mahalanobis rule would relabel a row for more than the
gain tolerance, citing `CE-D-UNMERGED-DUPLICATES-001` — the fixture behind
[D-UNMERGED-DUPLICATES-FAIL](/research/claim-record#d-unmerged-duplicates-fail) — and the same code appears
if a compile attempt hits the same condition.

## Batch reassignment can make the objective worse

The obvious algorithm — freeze the metric, reassign every row to its nearest centre, recompute —
is not monotone for this objective. One such step can *decrease* the log determinant
([D-LLOYD-NONMONOTONE](/research/claim-record#d-lloyd-nonmonotone)). The committed eight-row,
two-dimensional, three-cell example loses 0.136521 nat in a single step, and a seeded census
recorded 57 decreasing steps in 300.

The reason is ordinary: the tangent of a concave function is an upper bound, not a lower one, so
the usual monotonicity argument for Lloyd-type iteration does not transfer.

*Consequence for a user.* The batch iteration is available, but only as a *proposal* generator
whose proposals are accepted on the exact objective
([D-GUARDED-LLOYD](/research/claim-record#d-guarded-lloyd)). The guard is part of the solver contract, not
an optional safeguard. The ledger labels the counterexample *unresolved* — no prior-art search has
been recorded, and it notes that adaptive-metric Lloyd non-monotonicity may already appear in the
determinant-clustering computational literature.

## The profiled criterion has no equivalent geometry

This boundary has the largest practical consequence of any on this page: it is why a profiled
result cannot be turned into a reusable rule.

For the profiled objective — some parameters of interest, the rest nuisance — the D-style argument
fails at both steps. A positive first-order margin in the natural profiled semimetric does not
imply a positive exact gain, so exchange stability does not force nearest-cell assignment
([DS-FINITE-GEOMETRY-FAILS](/research/claim-record#ds-finite-geometry-fails)). Worse, a *globally optimal*
profiled partition can violate its own first-order rule
([DS-GLOBAL-NONGEOMETRIC](/research/claim-record#ds-global-nongeometric)). The witness is exact: eight
rows, two score dimensions, one parameter of interest, three cells, enumerated exhaustively, with
the unique global optimum violating its own rule by margins of 2862/3239 and 618/3239.

*Consequence for a user.* A profiled result has **no canonical rule to compile into**. Calling
`compile_quantizer()` on one is refused, citing `CE-DS-GLOBAL-GEOMETRY-001` — the fixture of
[DS-GLOBAL-NONGEOMETRIC](/research/claim-record#ds-global-nongeometric) above — and the remedy is to fit an
explicit quantizer instead of converting a fixed-sample partition into one. The full decision
table for when a profiled terminal state may and may not be compiled — five observable cases,
assembled from the registered theorems — is
[DS-PROFILED-COMPILE-CERTIFICATE](/research/claim-record#ds-profiled-compile-certificate). The ledger notes
that its "only currently established" wording is relative to the registry, not an impossibility
theorem, and that verifying the certificate theory authorized no change to the library's
behaviour.

## The margins you would need are not free

The natural repair is to ask only for partitions that carry margins: cells with enough mass, a
binned information matrix bounded away from singular, centres that stay separated. Under those
margins there *is* a finite-to-population bridge
([OPEN-DS-FINITE-POP-BRIDGE](/research/claim-record#open-ds-finite-pop-bridge)) — a conditional theorem,
whose hypotheses are assumed rather than derived.

Three results say what those margins cost, and all three are scoped tightly: one parameter of
interest, one nuisance parameter, equal weights, and a class of score laws whose nuisance
component is conditionally centred. Nothing below is claimed outside that class.

**At free global optima the conditioning margin fails.** Along exact global finite optima the value
converges to the unrestricted population supremum, cell masses converge to positive limits — so the
mass margin comes for free — but the binned nuisance and cross blocks vanish, so the conditioning
margin fails for *every* threshold ([OPEN-DS-MARGINS-AT-OPTIMA](/research/claim-record#open-ds-margins-at-optima)).
The optimizer sheds binned nuisance information by design. The bridge therefore governs
margin-certified solutions, which are necessarily suboptimal, and never free global optima.

**The margin has a price.** For every conditioning threshold there is a strictly positive gap
between the best margin-carrying value and the unconstrained one — asymptotically, and uniformly
over every labelling rather than only over stable or optimal ones
([DS-STABLE-MARGINS-PRICE](/research/claim-record#ds-stable-margins-price)). The result
neither asserts that the constrained optimum is attained nor that the price varies continuously
with the threshold, and the ledger records both omissions explicitly.

**On that class the fully certified branch is eventually empty.** Stronger still: for conditionally
centred laws, and under one further regularity condition on the law, all sufficiently large samples
admit *no* ordinary exchange-stable labelling carrying the mass, conditioning and
centroid-separation margins at once
([DS-STABLE-BASINS-CENTERED-OBSTRUCTION](/research/claim-record#ds-stable-basins-centered-obstruction)).
The ledger is emphatic that this is a statement about *population* conditional centring, that it is
not permission to centre your sample, and that it does not extend to non-centred laws.

**A cardinality boundary.** A boundary example makes one hypothesis concrete: with too few cells,
exact centring forces every feasible labelling's profiled value to exactly zero — a rank effect,
not a data problem, and no sample size fixes it. The condition the ledger settled on is at least
one cell more than the score dimension, which for a single parameter of interest is two more than
the nuisance dimension. The library refuses such a configuration up front
rather than blaming the nuisance parameterization, citing `CE-DS-MARGINS-RANK-VACUITY-001`, the boundary
fixture of [OPEN-DS-MARGINS-AT-OPTIMA](/research/claim-record#open-ds-margins-at-optima).

## The profiled certificate is a bracket, and the bracket can stay open

For a single parameter of interest there is a two-sided certificate: a dynamic program over a
tilted scalar score gives a primal value and a dual ceiling, and when a specific gate condition is
met the two meet and certify a finite global optimum
([DS-TILT-DUAL-CERTIFICATE](/research/claim-record#ds-tilt-dual-certificate)).

Two limits are proved rather than suspected.

*Strong duality is false.* The gap can be order one, not a rounding artifact: an exact four-row,
three-cell table has a gap above 0.68, and the smallest possible witness — three rows, two cells —
has an exact gap of 1/6 ([DS-TILT-DUAL-STRONG-DUALITY-FAILS](/research/claim-record#ds-tilt-dual-strong-duality-fails)).
The ledger instructs that this not be called surprising: minimax interchange on a finite nonconvex
feasible set is expected to fail, and the contribution is the exact witnesses, not the phenomenon.

*An open bracket certifies nothing about the gap.* A reported non-closing bracket is not evidence
that a duality gap exists — a tie in the dynamic program can let a deterministic policy return a
labelling that hides a closure that was available. The gate is therefore set-valued and must
exhibit the closing labelling, not merely report an interval.

*Consequence for a user.* "Certified" here means "this specific labelling was exhibited and the
gate closed on it". Anything else is a reported interval.

## Why there is no E-optimality criterion

The smallest-eigenvalue criterion is the natural choice when you need a guarantee for every
parameter direction rather than for the volume. It is not implemented, and the reason is a
counterexample: an exhaustively searched finite example with a simple minimum eigenvalue has a
global optimum whose own rank-one nearest-cell rule disagrees with a training label
([E-GLOBAL-GEOMETRY-FAILS](/research/claim-record#e-global-geometry-fails)). The same ledger row records a
second failure: a positive first-order margin can come with a negative exact gain
([E-FIRSTORDER-NOT-FINITE](/research/claim-record#e-firstorder-not-finite)).

Two honesty notes the ledger requires. The witness is floating-point, not exact rational, unlike
most of the others on this page. And no prior-art search is recorded for it, so it is a witness
rather than a novelty claim.

## Next

Those are the negatives that are *proved*. [What is still open](/research/what-is-still-open)
lists the questions with no answer in either direction.
