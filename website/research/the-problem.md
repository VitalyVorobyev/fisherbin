---
title: The problem
sidebar_label: The problem
sidebar_position: 2
---

# The problem

## The situation, before any vocabulary

A pipeline produces many rich observations — waveforms, tracks, cells, images, spectra — and the
analysis that finally estimates a number reads only a small table: how many observations fell in
category one, how many in category two, and so on. Everything else is discarded.

There are ordinary reasons for this. Counts survive being written down and read again years
later. A likelihood built on a dozen counts can be fitted, profiled and combined with other
experiments. Systematic effects are easier to propagate through a dozen bins than through a
continuous density estimate. Sometimes the categories are forced: a sensor transmits a few bits,
or a collaboration publishes a table rather than a dataset.

The question this research asks is the one that follows immediately. **Given that you must throw
away almost everything, which few categories should you keep?** Two different sets of category
boundaries, applied to the same observations, leave you with different amounts of knowledge about
the parameter you are trying to measure. The gap between a thoughtless choice and a good one is
real, and it is computable.

## What "losing information" means exactly

The quantity being preserved is Fisher information about the model parameter. To make the
question sharp you need three facts, all of them established results rather than anything this
project proved.

**The information after labelling has a closed form.** If you replace each observation by its
category label, the label carries its own likelihood, and the Fisher information it carries is
the variance of the conditional mean of the score given the label
([FI-QUANT-IDENTITY](/research/claim-record#fi-quant-identity)). It is a sum over cells of one outer
product each — the cell's weighted score sum against itself, divided by the cell's weight. There
is no approximation and no asymptotics in that statement.

**Binning can never add information.** The difference between the full information and the binned
information is the expected within-cell covariance of the score, which is positive semidefinite
([FI-LOSS-DECOMPOSITION](/research/claim-record#fi-loss-decomposition)). So the whole problem is a
minimization of an unavoidable loss, never a search for a lucky gain. This also gives the natural
scale for reporting the loss: the binned information matrix normalized by the unbinned one has
every eigenvalue between zero and one
([INFO-RETENTION-SPECTRUM](/research/claim-record#info-retention-spectrum)), and the geometric mean of
those eigenvalues is the standard efficiency number
([INFO-D-EFFICIENCY](/research/claim-record#info-d-efficiency)).

**There is a hard ceiling from the number of categories.** With `K` categories and a
`d`-dimensional parameter, the binned information has rank at most `min(d, K-1)`, so a
nonsingular answer needs at least `d + 1` categories
([FI-RANK-CEILING](/research/claim-record#fi-rank-ceiling)). Asking three bins to measure four parameters
is not a hard optimization problem; it is an impossible one, and the library refuses it rather
than returning a degenerate answer.

## Why there is still a choice to make

Those three facts leave a matrix, not a number. To rank two candidate partitions you must summarize
the matrix, and the summary you pick changes the answer.

Adding up the diagonal gives the trace. Once the score coordinates are put into Fisher-whitened
units, maximizing the retained trace is *exactly* weighted k-means — the same objective, the same
optimum, the same algorithm ([TRACE-WHITENED-KMEANS](/research/claim-record#trace-whitened-kmeans)). That
is a useful thing to know in both directions: it explains why running k-means on whitened scores
is a principled answer, and it pins down precisely which question that answer is answering.

Taking the determinant instead couples all the parameter directions together rather than adding
them up, so it does not reduce to a distortion problem and it needs its own algorithms — the exact
relocation algebra and the geometry theorem described on the next two pages.

## Three questions that look like one

The ledger records a distinction that is framing rather than a theorem, and it is worth carrying
through everything that follows. Three questions are routinely merged:

1. **Which labels should these specific observations get?** A finite assignment problem, with a
   finite (if astronomically large) set of candidate answers.
2. **Which rule should label observations I have not seen yet?** A learning problem. A list of
   labels on a finite sample does not answer it: infinitely many rules agree with any given
   labelling and disagree everywhere else.
3. **Which rule is best against the underlying distribution?** A design problem, about a
   population rather than a sample.

The ledger notes that this three-level distinction has no registry claim of its own — it is a way
of organizing the material, not a proved statement — and attributes the underlying ideas to the
empirical-versus-population literature and to work on terminal versus Voronoi partitions in
clustering. It matters here because the results on the following pages sit at different levels,
and a result about level 1 is not automatically a result about level 2. One of the results on the
next page is a bridge from level 1 to level 2; it holds for one criterion, under stated
conditions, and not for the others.

## Next

[What was already known](/research/what-was-already-known) places this question in the four
literatures that had been working on parts of it.
