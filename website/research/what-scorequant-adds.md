---
title: What ScoreQuant adds
sidebar_label: What ScoreQuant adds
sidebar_position: 4
---

# What ScoreQuant adds

*Who this is for: a reader who has read the prior art and wants the short list of results that were not already there, with the label each one actually carries.*

The novelty ledger has 103 rows, one per central statement. Their labels break down as: 34 *direct
corollary*, 31 *unresolved*, 20 *known*, 10 *adaptation*, 8 *apparently new*. Most of the machinery
is therefore inherited, a small number of statements are the project's own, and the largest single
category after corollaries is material recorded as unresolved.

What follows is the list that is *not* inherited, in the order a user meets it, with what each one
buys.

## Exact algebra for a single relocation — *adaptation*

Moving one weighted observation from one cell to another changes the binned information matrix by
a rank-two update ([D-RANK2-MOVE](/research/claim-record#d-rank2-move)), and the resulting change in the
log determinant has a closed form with no matrix refactorization in it
([D-LOGDET-GAIN](/research/claim-record#d-logdet-gain)).

*What it buys.* Every candidate move can be scored exactly and cheaply, so the solver never
compares two partitions by rebuilding and re-factorizing an information matrix, and it never
accepts a move on the strength of an approximation. Accepting only exactly positive gains makes
the search strictly monotone on a finite set of labellings, so it cannot cycle and it terminates
([D-EXCHANGE-TERMINATES](/research/claim-record#d-exchange-terminates)).

*What the label means.* The ledger calls this an adaptation, not a discovery: exchange-method
scatter updates go back to Späth, Friedman and Rubin, and Scott and Symons, and the determinant
lemma is classical. What is transferred here is the *between-cell* form with centroid-coupled
coefficients rather than the within-scatter form. The ledger also flags the risk plainly: if
Späth's exchange routines already carry the same centroid-coupled between-scatter update, this row
drops to *known*.

## Exchange stability implies a Voronoi structure — *apparently new*

This is the central structural theorem, and the only row in the manuscript's core section that
carries the *apparently new* label.

Take a partition in which no single observation can be moved to another cell with a positive exact
gain. Under stated conditions — coincident score rows merged into distinct weighted atoms, a
positive-definite binned information matrix, exactly K nonempty cells, no move restriction beyond
keeping cells nonempty, and a zero gain tolerance — that partition *is* a strict, self-consistent
Voronoi partition in the Mahalanobis metric given by the inverse binned information
([D-EXCHANGE-IMPLIES-VORONOI](/research/claim-record#d-exchange-implies-voronoi)). Any observation sitting
in the wrong cell under that rule would have supplied a strictly positive gain, with an explicit
lower bound on how large. Distinct cell centres are *derived* from stability rather than assumed.
The supporting inequality is a standard projection-leverage bound
([D-LEVERAGE](/research/claim-record#d-leverage)), which the ledger labels *known*.

*What it buys.* It converts a list of labels into a geometric object. Without it, a labelling of
your sample says nothing about a new observation; with it, the terminal labelling is exactly
reproduced by a nearest-centre rule you can write down, ship, and apply later.

*What the label means.* The ledger's rule is that this may be presented only as "we found no
direct precedent", and it names the nearest neighbour explicitly: Telgarsky and Vattani's analysis
of Lloyd versus Hartigan fixed points, which studies the same kind of terminal state for
sum-of-squared-errors and reaches the *opposite* conclusion. It also records that the
determinant-clustering literature between Friedman–Rubin and Späth has not been fully swept, and
that a Hartigan-style terminal-geometry result for another determinant criterion would demote this
row to *adaptation*.

## The compile bridge — *direct corollary*

Because a stable terminal state is a Voronoi partition, it compiles: the nearest-centre rule built
from the terminal centres and metric reproduces every training label
([D-FINITE-INDUCTIVE-CLOSURE](/research/claim-record#d-finite-inductive-closure)). Duplicate rows inherit
the label of the merged atom they belong to.

*What it buys.* This is the bridge between two of the
[three questions](/research/the-problem) — from "which labels do *these* observations get" to
"which rule labels the next one". It is bookkeeping rather than a second fit: no new optimization
runs, and the rule is not an approximation of the partition, it *is* the partition.

*What the label means.* It follows from the theorem above by routine argument, so the ledger gives
it no independent novelty. It also records a weakening the theorem statement does not carry: a
real solver stops at a positive gain tolerance, not at zero, so the deployable guarantee is
self-consistency *at that tolerance* — the rule reproduces every training label except on rows
whose relocation is worth no more than the tolerance the partition was certified at.

A second corollary of the same theorem: every globally optimal finite partition is exchange-stable,
so every global optimum is geometrically realizable, and optimizing over unrestricted labellings
and over realizable nearest-centre labellings give the same optimal value
([D-GLOBAL-GEOMETRIC-REALIZABILITY](/research/claim-record#d-global-geometric-realizability)).

## A usable global certificate — *direct corollary*

A partial assignment can be bounded above by completing it with one singleton cell per unassigned
observation, because refining a partition can only increase information
([D-BB-SINGLETON-BOUND](/research/claim-record#d-bb-singleton-bound)).

*What it buys.* On small instances a bounded search can either prove a partition optimal or report
honestly that its budget ran out before it could. The result object always states which of the two
happened; a certificate that says "budget exhausted" proves nothing about the incumbent, and says
so.

## Profiled criteria: a ceiling and a bound

When only some parameters are of interest and the rest are nuisance, the objective is a Schur
complement ([DS-SCHUR](/research/claim-record#ds-schur)) — that is classical design theory, cited here and
not claimed.

Two results sit on top of it.

**A computable ceiling.** For any rule, the profiled information it retains is dominated by the
between-cell information of the *full-data efficient score* under that same rule
([DS-EFFICIENT-SCORE-DOMINATION](/research/claim-record#ds-efficient-score-domination)). Maximizing the
latter over all rules with the same number of cells therefore gives a ceiling for the former, and
for a single parameter of interest that upper problem has ordered interval cells and is solved
exactly by a weighted interval dynamic program
([DS-SCALAR-EFFICIENT-DP](/research/claim-record#ds-scalar-efficient-dp)). *What it buys:* a number you can
subtract from your achieved objective to see how much room is left, plus a strong initializer for
the search. *What the labels mean:* the ledger is emphatic here. The variational identity
underneath the domination bound was re-attributed to Krein, Anderson, and Li and Mathias, and its
statistical reading is textbook semiparametrics; this is the ledger's **highest-risk attribution**
and it must be written as a corollary, never as a contribution. The interval-cell dynamic program
is *known*, with prior art going back to Fisher's 1958 grouping algorithm.

**A leverage bound at profiled stable states.** At an exchange-stable profiled partition there is
an exact inequality relating the leverages of the two cells involved in any candidate move
([DS-EXCHANGE-LEVERAGE-BOUND](/research/claim-record#ds-exchange-leverage-bound)). It needs no assumption
that the cells carry balanced mass. *What it buys:* it is the technical ingredient that replaces
the exact Voronoi geometry the profiled case does not have — see
[what cannot be certified](/research/what-cannot-be-certified). *What the label means:* it is
recorded as *apparently new* on the strength of a search gap alone, with the classical D-side
leverage inequality named as its nearest cousin, and the ledger notes it may drop to *adaptation*
under review.

## Differentiable rules, and what they do not guarantee — *direct corollary* and *known*

Replacing a hard assignment by an assignment *probability* is not a smoothing trick: the resulting
soft assignment is the exact Fisher information of a genuinely randomized quantizer, provided the
randomization does not itself depend on the parameter
([SOFT-RANDOMIZED-FIM](/research/claim-record#soft-randomized-fim)). Optimizing at a fixed positive
temperature then has the ordinary guarantees of smooth nonconvex optimization and no others
([SOFT-FIXED-TEMP-STATIONARY](/research/claim-record#soft-fixed-temp-stationary)).

*What it buys.* A gradient-based route to a rule that hard-boundary optimization cannot supply, and
a clear statement of what that route does not deliver: a stationary point of the soft objective is
not a local or global optimum of the hard one.

*What the labels mean.* The ledger explicitly instructs that the exact assignment gradient not be
pitched as a headline result — it is the chain rule applied to the identity above — and attributes
the soft-histogram idea to the inference-aware categorization line.

## A consistency result, for a restricted class — *adaptation*

For a compact, finite-capacity family of nearest-centre rules with uniformly positive cell masses
and bounded conditioning, cell moments and objective values converge uniformly, and approximate
empirical maximizers are value-consistent
([CONSISTENCY-RESTRICTED-AFFINE](/research/claim-record#consistency-restricted-affine)).

*What it buys.* It is the statement that fitting a rule on a sample and deploying it on new data
is asymptotically sound — but only inside that restricted class.

*What the label means.* The ledger calls it an adaptation of the standard empirical-process route
and notes that its registry statement adds uniform conditioning margins and an isolated population
optimum as hypotheses. The unrestricted version is open and is listed in
[what is still open](/research/what-is-still-open).

## One inherited property worth naming

The determinant criterion is invariant under invertible reparameterization: changing the parameter
basis changes the objective by the same constant for every rule, so the ranking of rules is
untouched ([D-REPARAM-INVARIANCE](/research/claim-record#d-reparam-invariance)). The ledger labels it
*known*. It is listed here because it is a practical reason to prefer that criterion, not because
it is a contribution.

## Next

[What cannot be certified](/research/what-cannot-be-certified) is the other half of this list, and
it is the longer one.
