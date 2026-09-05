# Why ScoreQuant

## Some analyses have to bin

A great deal of statistical practice ends in counts. A template fit needs the expected number of
events per category for each model component. A trigger has to route an event into one of a few
tiers. A cytometry protocol reports the fraction of cells in named gates. A binned likelihood
needs bins. In every one of these the continuous measurement is replaced by an integer label, and
that step is irreversible.

The bins are usually chosen for readability: equal width, equal population, a threshold on one
discriminant, or whatever the previous analysis used. Those are choices about presentation. They
are also, silently, choices about how much parameter sensitivity survives, and nothing in the
usual workflow reports the size of what was given up.

## What binning costs, and where the cost lives

For a regular model the local sensitivity of one event is its score, the gradient of the
log-likelihood at a reference point, and the Fisher information of the unbinned sample is the
score's second moment. A hard rule that maps each event to one of \(K\) labels keeps only the
between-cell part of that second moment; the difference is exactly the within-cell scatter of the
*score*. The [method overview](method.md) states the identity and the
[book](book/ch05-information-after-binning.md) derives it. Two consequences matter here.

Binning can only lose information, and refining a partition can only help. And the loss is
governed by how the score varies inside each cell, not by how the observation does: a cell that is
narrow in the measurement variable but flat in the score costs almost nothing, while a cell that
looks reasonable on a histogram but straddles a region where the score swings costs a great deal.
Equal-width and equal-population rules know nothing about the score, so their loss is arbitrary
with respect to the quantity anyone actually cares about.

Binning by a single discriminant is the near miss. For a scalar parameter the optimal cells really
are intervals of the score, and ScoreQuant solves that case exactly. With several parameters the
score is a vector, and a single ranking cannot separate directions that matter for different
parameters; compressing to one axis first discards the multivariate structure before the binning
ever sees it.

## Why score space

Score space is the natural coordinate system because the loss identity is written in it. It has
one coordinate per parameter, however many measurement variables the events have, so a
forty-channel measurement feeding a two-parameter fit becomes a two-dimensional problem. An
analytic likelihood, a linear component model and an estimated density ratio all produce score
vectors, so one optimizer serves all of them. And its origin means something: the retained
information is a second moment about zero, because a score of zero is the direction of no
sensitivity. ScoreQuant therefore never centers scores, and it projects out numerically singular
directions rather than repairing them with a ridge, because a ridge would invent information the
sample does not contain.

Score space also draws the honesty boundary. When the supplied vectors are the model score, their
second moment is Fisher information. When they are estimates, most often built from estimated
density ratios, the same algebra is exact for the vectors you supplied and only a surrogate for
the model. Every result carries score provenance, and `information_kind` reads `exact_fisher`
only when the provenance permits it. [Three doors](three-doors.md) describes the input routes and
[Chapter 13](book/ch13-estimated-scores.md) what a surrogate does and does not mean.

## Two tasks

Labelling the rows of a fixed table and fitting a rule for rows not yet seen are different
questions, and one `fit` method cannot answer both honestly. `optimize_partition` solves the
first: a combinatorial assignment whose answer is a label vector, and `PartitionResult` has no
predict method because many rules reproduce the same labels on a sample and disagree everywhere
else. `fit_quantizer` solves the second: a geometric rule on score space, defined everywhere, with
prediction through `predict_scores`. One theorem connects them, and `compile_quantizer()` exposes
it only where its hypotheses are verified. [Choosing your workflow](user-workflow.md) decides
between the tasks; [Chapter 6](book/ch06-two-tasks.md) is the argument.

## When to use it, and when not

ScoreQuant is worth reaching for when downstream inference needs hard gates, categories, or
template counts, when several parameters matter at once, and when local parameter sensitivity
matters more than proximity in measurement space.

It is not a general-purpose compressor, a ratio estimator, or a complete likelihood framework, and
it cannot certify that an upstream simulator or a learned density ratio is unbiased: the closure
check bounds visible bias from below, never from above. It optimizes what the supplied scores say;
the quality of the representation behind them is your responsibility, and
[Chapter 13](book/ch13-estimated-scores.md) explains how to check it.
