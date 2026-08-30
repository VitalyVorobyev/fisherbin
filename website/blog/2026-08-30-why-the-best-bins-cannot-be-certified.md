---
slug: why-the-best-bins-cannot-be-certified
title: Why the best bins can never be certified
authors: [scorequant]
tags: [research, negative-result, profiled-ds]
---

ScoreQuant does one thing: it takes a pile of events and sorts them into a
handful of labelled bins, while throwing away as little information as possible
about the quantity you actually want to measure. Bins are cheap to store, cheap
to ship, and easy to explain. The whole question is how much you lose by using
them.

This week's result is a negative one, and it is the most useful thing the
project has produced so far.

<!-- truncate -->

## What we did

Real measurements usually come with a second, unwanted parameter. You want to
measure a signal fraction; the background rate is unknown too, and you have to
estimate it at the same time. Statisticians call the unwanted one a *nuisance*
parameter, and the criterion that accounts for it honestly is what we call
profiled information.

We wanted two things at once from the binning: bins that keep as much
information as possible, and a **certificate** — a number you can compute after
the fact that says "this arrangement is safely conditioned, you can trust the
error bars." Certificates matter for production. Without one, you have a
number, but no way to know when it has quietly gone bad.

We now have a proof that you cannot have both.

## Why it matters

The mechanism is almost perverse once you see it. The optimizer is allowed to
choose any arrangement of bins. It turns out the easiest way to raise its score
is to build bins that carry *no information at all* about the nuisance
parameter — pushing that part of the problem to exactly zero. The certificate
we wanted asks for the opposite: it demands that the binned data retain enough
information about the nuisance parameter to be well conditioned.

So as the sample grows, the best arrangements march steadily towards the one
place the certificate can never be issued. This is not a solver that needs more
tuning. Certification and free optimization are incompatible goals. You can
still insist on a certified arrangement — that remains perfectly legitimate —
but you now pay a price in information that we can quantify rather than guess.

Along the way the audit found something sharper, and a little embarrassing. If
you ask for too few bins — one more than the number of nuisance parameters —
the criterion is not merely hard to optimize. On a centred sample it is
*exactly zero for every possible arrangement of the data*, and no amount of
extra data changes that. We had two ways of handling this and both were wrong.
One route refused the job but blamed your data, suggesting you try a different
sample when no sample could ever work. The other quietly handed back a rule
that scores zero. Both now refuse it and explain the actual reason, which
ships alongside this post.

We also had to walk back part of our own claim. We originally stated the result
for any number of nuisance parameters; the independent audit produced an exact
counterexample and forced it down to one. The narrower statement is the one
that is true.

## What's next

Knowing what *cannot* be certified tells us what to build instead. The
deployable object for profiled criteria is a specific, modest thing: estimate
the nuisance slope once on the full sample, subtract it to form a single
combined score, and cut that one-dimensional line into intervals. It comes with
its own honest certificates, and the code to compute it already exists inside
the library — it just throws the result away instead of returning it. Making it
a first-class, reusable rule is the immediate task.

Two honest limits. The proof covers one parameter of interest and one nuisance
parameter, under a specific class of well-behaved distributions. And it
describes exact global optima, while our actual optimizer returns arrangements
that are merely locally stable. Whether those keep their margins is the open
question we are opening a research packet on next.
