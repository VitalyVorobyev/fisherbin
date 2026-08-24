# The estimation problem

## From many measurements to a few unknowns

An **observation** is one measured event (x): a collision, a cell, a photon,
or a spectrum. A **parameter** (	heta) is an unknown quantity that the analysis
will estimate. The observation may have hundreds of coordinates while
(	heta) has only a few.

The statistical model answers a forward question:

\[
x\sim p(x\mid\theta).
\]

Inference asks the reverse question: given observed events, which values of
(	heta) are compatible with them?

### Why hard bins appear

A **hard partition** assigns every event to exactly one of (B) bins. Its output
is the integer (b(x)\in\{1,\ldots,B\}). The downstream data are then counts
(n_1,\ldots,n_B), not the original events.

Hard bins are useful when an analysis needs a template likelihood, fast repeated
fits, a stable interface between teams, limited storage, or a small set of
interpretable selections. They are also irreversible: two different events in
the same bin become indistinguishable to the count likelihood.

### Geometric binning is not parameter-aware

Ordinary grids, trees, and clustering group events that are close in the
measured variables. This is sensible for reconstructing the distribution of
(x), but parameter estimation is a different task. Two distant events may
carry the same evidence about (	heta); two neighboring events may pull the
estimate in opposite directions.

FisherBin changes the geometry. It first represents each event by its local
parameter sensitivity, called the [score](likelihood-and-score.md), and then
learns hard bins in that space.

## What FisherBin does—and does not do

The supported pipeline is

```text
physical variables X -> component values Phi -> score vectors -> hard bins
```

FisherBin owns the last step and provides common ways to construct scores from
linear components or classifier posteriors. It does not define the scientific
model, train a classifier, or fit the final parameters from observed counts.

This separation is important. A partition can preserve nearly all information
present in supplied scores while those scores are biased because their upstream
model is wrong. The [diagnostics chapter](diagnostics.md) keeps compression
loss, estimator bias, and downstream error separate.

## A running example

Imagine a sample containing signal and background with unknown signal fraction
(	heta):

\[
p(x\mid\theta)=\theta p_s(x)+(1-\theta)p_b(x).
\]

An event that is much more likely under (p_s) than (p_b) favors a larger
(	heta). An ambiguous event barely changes the estimate. The score turns that
statement into one number per event. Binning nearby score values preserves the
distinction that matters for estimating (	heta), even when (x) itself is
multidimensional.

Next: [likelihood and score](likelihood-and-score.md).
