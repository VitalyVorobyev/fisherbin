---
title: What is still open
sidebar_label: What is still open
sidebar_position: 6
---

# What is still open

*Who this is for: a reader who wants to know which of their questions the project cannot answer, and a researcher looking for something to work on.*

The previous page listed statements that are proved *false*. This page lists statements that are
neither proved nor refuted. Each entry has a registry claim of its own, so "open" here means
recorded and tracked, not forgotten.

## Whether the central theorem is actually new

The implication from exchange stability to a Voronoi structure is labelled *apparently new* on the
strength of one targeted literature search that found no direct equivalent. The ledger treats that
as a search gap, not a novelty proof, and schedules an adversarial prior-art review that could
demote it. Two specific holes are named: the determinant-clustering literature between Friedman and
Rubin's 1967 paper and Späth's exchange routines has not been fully swept, including non-English
and pre-digital sources; and a Hartigan-style terminal-geometry result for any other determinant
criterion would change the label. Several of the counterexamples on the previous page have no
recorded search either, so they are witnesses rather than firsts.

This is an open question about attribution rather than about mathematics, and it is the reason none
of these pages uses the word "first".

## How hard the global problem is

Because every global optimum is realizable as a nearest-centre labelling, an arrangement
enumeration solves the finite problem exactly in time polynomial in the sample size for a fixed
parameter dimension and cell count ([D-GLOBAL-XP](/research/claim-record#d-global-xp)) — a direct
application of a known enumeration template. Whether that exponent is tight, and where the
NP-hardness and fixed-parameter-tractability boundaries actually lie, is open
([OPEN-D-PARAMETERIZED-COMPLEXITY](/research/claim-record#open-d-parameterized-complexity)); the ledger
insists that any answer come with a valid reduction rather than an analogy.

For the profiled criterion the picture is sharper and the remaining gap is narrower. Exact
minimization of the tilt dual is polynomial in bit complexity when there is a single nuisance
parameter, for every cell count, and polynomial in arithmetic operations for any fixed nuisance
dimension. What remains open is a polynomial *bit* bound for a fixed nuisance dimension of two or
more with a variable cell count, and any exact statement — or hardness obstruction — when the
nuisance dimension itself varies
([OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY](/research/claim-record#open-ds-tilt-dual-exact-complexity)). The
ledger notes that generic parametric-search lower bounds do not automatically transfer to this
particular grouping problem, which is why the question is not already answered by the general
theory.

## Whether fitting on a sample generalizes, without restrictions

Consistency is proved for a restricted class of rules. Whether *unrestricted* empirical global
optima converge, in value or in decision, to population optima is open
([OPEN-D-UNRESTRICTED-CONSISTENCY](/research/claim-record#open-d-unrestricted-consistency)). The structural
theorem makes the D case look favourable — global optima are geometrically realizable, so the
unrestricted and restricted problems have the same optimal value — but "looks favourable" is not a
proof, and the ledger says so.

On the profiled side the corresponding questions have been narrowed rather than closed. Beyond the
audited scalar-interest, scalar-nuisance, conditionally centred class, the margins dichotomy is
open in two specific directions: more than one parameter of interest needs a uniqueness and
rigidity theory for vector quantization of the efficient score that does not yet exist, and two or
more nuisance parameters need a steering construction spanning every nuisance direction, which is
neither built nor refuted
([OPEN-DS-MARGINS-NONCENTERED](/research/claim-record#open-ds-margins-noncentered)). Two further remainders
concern whether stable empirical sequences can track the degenerate configurations the theory
allows, and whether the constrained optimal values are attained at all
([OPEN-DS-STABLE-BASINS](/research/claim-record#open-ds-stable-basins)).

## Which criteria have a geometry at all

The determinant criterion has an exchange-implies-geometry theorem. The profiled and
smallest-eigenvalue criteria demonstrably do not. **Why** is unknown: there is no characterization
of which concave matrix criteria admit such an implication
([OPEN-CRITERION-CHARACTERIZATION](/research/claim-record#open-criterion-characterization)). The ledger
adds a caution worth repeating — nothing proves that the determinant is the *unique* criterion with
this property, and no page may hint that it is.

## What happens when the score law has atoms

Randomized and deterministic rules attain the same population optimum when the score law is
atomless. Real samples are atomic. Whether splitting a single atom between labels can strictly beat
every deterministic rule is open
([OPEN-ATOMIC-RANDOMIZATION-GAP](/research/claim-record#open-atomic-randomization-gap)). A closely related
question governs the differentiable solver: when, if ever, do the stationary points or optima of a
softened family converge to hard stationary points or optima as the temperature goes to zero
([OPEN-SOFT-HARD-ZEROTEMP](/research/claim-record#open-soft-hard-zerotemp))? Until that is answered,
hardening a soft fit is an operation whose result must be verified on the hard objective rather
than inferred.

## What an estimated score does to the guarantee

Every theorem in this section is a statement about a table of numbers. It is silent about where
those numbers came from. When the score is estimated — from a classifier, a learned ratio, a
simulator — one thing is already known and is not reassuring: the information actually retained is
governed by the *true* score conditioned on the estimated rule, not by the estimated score
conditioned on itself ([PROXY-TRUE-RETAINED-FI](/research/claim-record#proxy-true-retained-fi)). The two
coincide only when the proxy is exact in the relevant sense.

What is missing is any quantitative version of that gap. Neither the propagation from classifier
calibration error to retained-information loss
([OPEN-CLASSIFIER-CALIBRATION-FI](/research/claim-record#open-classifier-calibration-fi)) nor a perturbation
theory bounding the change in cell moments, objective and boundaries from a norm bound on the score
error ([OPEN-SCORE-PERTURBATION](/research/claim-record#open-score-perturbation)) exists. This is why
estimated-score provenance never claims exact Fisher semantics anywhere in the library: the
downgrade is not caution, it is the absence of a theorem.

## How a rule survives being moved

A rule is fitted at a reference parameter value. Bounding the efficiency lost when it is evaluated
at a different value is open ([OPEN-PARAMETER-MISMATCH](/research/claim-record#open-parameter-mismatch)), as
is whether the common-metric geometry survives at all under an average or minimax objective over a
region of parameter space
([OPEN-MULTIREFERENCE-ROBUST](/research/claim-record#open-multireference-robust)).

## How many bins, and with what error bar

Two questions a user asks immediately have no answer in the literature or here.

*How many cells do I need?* There is no sharp bound on efficiency as a function of the cell count,
and no inversion rule giving a required cell count for a target efficiency
([OPEN-D-EFFICIENCY-VS-K](/research/claim-record#open-d-efficiency-vs-k)). The rank ceiling gives a
*minimum*; everything above it is empirical.

*Is my reported efficiency itself uncertain?* Retention is reported as a point estimate. Confidence
intervals for it — handling the non-smoothness of hard assignment at cell boundaries — do not exist
yet ([OPEN-RETENTION-UNCERTAINTY](/research/claim-record#open-retention-uncertainty)).

A third, narrower question belongs beside them: a good determinant efficiency does not by itself
guarantee that every parameter direction is well measured. Only the trivial ordering between the
worst direction, the geometric mean and the average is available; anything sharper is open
([OPEN-D-DIRECTIONAL-BOUND](/research/claim-record#open-d-directional-bound)). The direction-resolved
diagnostics exist precisely because the summary number cannot be trusted to speak for the worst
direction.

## Next

[How the API names each result](/research/api-and-theorems) maps every statement on these pages to
the object or the error message you actually encounter.
