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
