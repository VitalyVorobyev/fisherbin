# Why ScoreQuant

## The problem: some analyses have to bin

A great deal of statistical practice ends in counts. A template fit needs the expected number of
events per category for each model component. A trigger has to route an event into one of a few
tiers. A cytometry protocol reports the fraction of cells in named gates. A binned likelihood
needs bins. In every one of these the continuous measurement is replaced by an integer label, and
that step is irreversible.

The bins are usually chosen for readability: equal width, equal population, a threshold on one
discriminant, or whatever the previous analysis used. Those are choices about presentation. They
are also, silently, choices about how much parameter sensitivity survives — and nothing in the
usual workflow reports the size of what was given up.

## Why naive binning loses information

Write the local sensitivity of one event as the score at a reference point \(\theta_0\),

$$
s(x)=\nabla_\theta\log p(x\mid\theta)\big|_{\theta_0},
$$

with the corresponding event score \(\nabla_\theta\log\lambda(x;\theta)\) for an intensity model.
The Fisher information of the unbinned sample is the weighted second moment \(I_\infty=E[ss^\top]\).
A hard rule \(q\) that maps each event to one of \(K\) labels retains only the between-cell part,

$$
I_q=\sum_b W_b\,\mu_b\mu_b^\top,
\qquad W_b=E[\mathbf 1_{q=b}],\qquad \mu_b=E[s\mid q=b],
$$

and the difference is exactly the within-cell scatter of the score,

$$
I_\infty-I_q=\sum_b E\!\left[\mathbf 1_{q=b}\,(s-\mu_b)(s-\mu_b)^\top\right]\succeq 0 .
$$

Two consequences follow immediately. First, binning can only lose information, never create it, and
refining a partition can only help. Second — and this is the operative point — the loss is governed
entirely by how the *score* varies inside each cell, not by how the observation does. A bin that is
narrow in the measurement variable but flat in \(s\) costs almost nothing. A bin that looks
perfectly reasonable on a histogram but straddles a region where \(s\) swings costs a great deal.
Equal-width and equal-population rules know nothing about \(s\), so their loss is arbitrary with
respect to the quantity anyone actually cares about.

Binning by a single discriminant is the near miss. It is the right idea in one dimension: for a
scalar parameter the optimal cells really are intervals of the score, and ScoreQuant solves that
case exactly. But with several parameters the score is a vector, and a single ranking cannot
separate directions that matter for different parameters. Compressing to one axis first, then
binning, discards the multivariate structure before the binning ever gets to see it.

## Why score space

The score is the natural coordinate system for this problem because the loss identity above is
written entirely in it. Three practical consequences:

- **It is the right dimension.** Score space has one coordinate per parameter, however many
  measurement variables the events have. A 40-channel measurement feeding a two-parameter fit
  becomes a two-dimensional quantization problem.
- **It is comparable across sources.** An analytic likelihood, a linear component model, and a
  calibrated classifier all produce score vectors, so one optimizer serves all of them.
- **Its origin means something.** \(I_q\) is a second moment about zero, not a variance about the
  sample mean, because \(s=0\) is the direction of no sensitivity. ScoreQuant therefore never
  centers scores. It projects out numerically singular directions rather than repairing them with
  a ridge, because a ridge would invent information that the sample does not contain.

Score space also draws the honesty boundary. When the supplied vectors really are the model score,
their second moment is Fisher information. When they come from a trained classifier, the same
algebra is exact *for the vectors you supplied* and only a surrogate for the original model:

$$
\widehat I_q=\operatorname{Var}\!\big(E[\hat s\mid q(\hat s)]\big),
\qquad
I_q^{\mathrm{true}}=\operatorname{Var}\!\big(E[s\mid q(\hat s)]\big).
$$

Every result therefore carries score provenance, and `information_kind` reads `exact_fisher` only
when the provenance permits it. Classifier training, calibration, and cross-fitting belong to the
application; their error must never be reported as quantization loss.

## Why two tasks and not one

There are two genuinely different questions here, and one `fit` method cannot answer both honestly.

**Sample partitioning** is transductive. You have a finite weighted table of scores and you want
the labels that maximize the retained information *of those rows*. This is a combinatorial
assignment problem, and its answer is a vector of labels. It does not by itself say anything about
a score you have not seen: many different rules reproduce the same labels on the sample and
disagree everywhere else. That is why `PartitionResult` has no predict method. Adding one would
force the library to pick a rule the mathematics did not determine, and users would apply it to
new data believing the sample optimality transferred.

**Space quantization** is inductive. You have a score law — an empirical sample, or a density over
a bounded box — and you want a reusable rule that assigns any future score to a bin. Its answer is
a geometric object: a transform, a set of centers, sometimes a metric. Prediction is well defined
because the rule is defined everywhere.

The two tasks are connected by exactly one theorem, and ScoreQuant exposes that connection
explicitly rather than assuming it. If a finite D-optimal partition is stable against every
admissible single-row relocation, and its between-cell information is nonsingular, then it is
already a strict self-consistent Voronoi partition in the \(I_B^{-1}\)-Mahalanobis metric. Only
then is there a canonical rule to hand back, and `compile_quantizer()` returns it after verifying
that the rule reproduces every positive-weight training label. An unstable or degenerate partition
is refused. The implication also does not generalize: for profiled \(D_s\), exact fixtures show
globally optimal finite assignments that violate the corresponding nearest-cell geometry, so a
profiled partition has no compilation method that could succeed by accident.

## When to use it, and when not

ScoreQuant is worth reaching for when downstream inference needs hard gates, categories, or
template counts, when several parameters matter at once, and when local parameter sensitivity
matters more than proximity in measurement space.

It is not a general-purpose compressor, a classifier trainer, or a complete likelihood framework,
and it cannot certify that an upstream simulator or a learned likelihood ratio is unbiased. It
optimizes what the supplied scores say; the quality of the scores is your responsibility, and the
[book chapter on estimated scores](book/11-score-estimation.md) explains how to check it.
