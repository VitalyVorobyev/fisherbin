# Fisher information

## Definition and intuition

**Fisher information** measures the local curvature or distinguishability of a
model around \(\theta_0\). For one event,

\[
F(\theta_0)=
\mathbb E_{x\sim p(x\mid\theta_0)}
\left[s(x;\theta_0)s(x;\theta_0)^T\right].
\]

Large information means that small parameter changes produce clearly different
data distributions. For several parameters, (F) is a positive-semidefinite
matrix: its eigenvectors are parameter directions and its eigenvalues quantify
local sensitivity along them.

For weighted integration events ((s_i,w_i)), FisherBin uses

\[
F_\text{unbinned}=\sum_i w_i s_i s_i^T,
\qquad w_i\geq0.
\]

Weights describe measure or exposure. Multiplying every weight by the same
positive number scales (F), but does not change normalized retention or the
learned partition. Zero-weight rows remain predictable but contribute no
information.

## What Fisher information can tell you

Under regularity conditions, the covariance of an unbiased efficient estimator
is locally bounded by the inverse Fisher matrix. This makes (F) a principled
design target when the goal is parameter precision.

FisherBin reports the eigenvalues of

\[
R=F_\text{unbinned}^{-1/2}
F_\text{binned}
F_\text{unbinned}^{-1/2}.
\]

Each retained eigenvalue lies between zero and one, up to numerical tolerance.
Their geometric mean is the reported D-efficiency.

## What it cannot tell you

Fisher information is not downstream RMSE. It describes local variance under a
specified model. It does not measure:

- bias from an approximate likelihood or learned ratio;
- finite-sample boundary behavior;
- robustness far from \(\theta_0\);
- systematic errors absent from the supplied score model.

This distinction resolves an apparent paradox in the FlowCyt study. Exact
unbinned likelihood ratios would provide an information upper bound. Classifier
ratios are estimates and can be biased. A binned pipeline may have lower
variance information but smaller total RMSE because its independently estimated
bin templates recalibrate the misspecified ratios.

Next: [the exact loss caused by binning](binning-loss.md).
