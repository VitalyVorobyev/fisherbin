# What binning loses

## The exact identity

For bin (b), define its total weight and mean score:

\[
W_b=\sum_{i:b(i)=b}w_i,
\qquad
\bar s_b=\frac{1}{W_b}\sum_{i:b(i)=b}w_i s_i.
\]

The count vector retains

\[
F_\text{binned}=\sum_b W_b\bar s_b\bar s_b^T.
\]

Subtracting it from the unbinned information gives an exact within-bin
covariance:

\[
F_\text{unbinned}-F_\text{binned}
=\sum_b\sum_{i:b(i)=b}
w_i(s_i-\bar s_b)(s_i-\bar s_b)^T
\succeq0.
\]

**Intuition.** A bin forgets differences between its members. Nothing is lost
when every event in a bin has the same score. More is lost when their score
arrows disagree.

## The oracle ordering

With exact scores, the matrix difference above is positive semidefinite, so no
hard binning can create Fisher information:

\[
F_\text{binned}\preceq F_\text{unbinned}.
\]

The synthetic evidence includes this oracle case and checks the matrix ordering
directly. This is a statement about the same correct statistical model on both
sides. It does not order the RMSE of two differently misspecified estimators.

## Poisson counts and fixed-total counts are different models

The identity above applies to the supplied score and measure. In an intensity
or Poisson model, the total event count can itself carry information. The
weighted score mean therefore has statistical meaning and FisherBin does not
subtract it.

A likelihood conditioned on a fixed total count is different. Its event score
is the supplied score minus its expectation,

\[
s_{\mathrm{cond}}(x)=s(x)-E[s(x)],
\]

and its information is the score covariance

\[
F_{\mathrm{cond}}
=E\!\left[(s-E[s])(s-E[s])^T\right].
\]

Only \(B-1\) of \(B\) fixed-total bin frequencies are independent. A binned
conditional likelihood for \(p\) locally identifiable parameters therefore
needs

\[
B-1\geq p.
\]

For a mixture of \(K\) fractions constrained to sum to one, \(p=K-1\), so at
least \(K\) bins are required. This is a rank condition, not an optimizer
preference. Five bins cannot identify all six fractions of a fixed-total
mixture, even if an unconditioned information diagnostic reports a nonzero
fifth direction.

Do not center scores before passing them to FisherBin. Conditioning belongs to
the downstream statistical model and should be checked as a separate
application diagnostic.

## Why score-space k-means appears

Taking the trace of the loss gives

\[
\operatorname{tr}(F_\text{unbinned}-F_\text{binned})
=\sum_b\sum_{i:b(i)=b}w_i\lVert s_i-\bar s_b\rVert^2.
\]

That is weighted k-means distortion in score space. FisherBin first removes
numerically singular Fisher directions and can whiten the retained directions,
so Euclidean distance does not depend on arbitrary parameter units.

**Limitation.** Trace loss treats directions additively. D-optimal optimization
instead balances the determinant across directions. Neither objective promises
a globally optimal hard partition, and neither repairs an incorrect score.

Next: [ways to construct scores](score-construction.md).
