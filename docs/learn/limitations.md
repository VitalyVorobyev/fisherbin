# Limitations and alternatives

## Local reference point

Scores and Fisher information are evaluated at \(\theta_0\). A partition can
lose performance when the true parameter is far away. Check several reference
points externally when a wide region matters.

## Approximate scores

FisherBin preserves information present in its inputs. It does not certify that
learned scores equal likelihood derivatives. Cross-fitting, calibration audits,
closure tests, and prospectively held-out cohorts remain necessary.

## Hard-partition capacity

Few bins cannot retain many independent directions. Sparse or empty bins also
make downstream templates unstable even when the retained Fisher matrix looks
good. Occupancy is an operational constraint, not a cosmetic plot.

The exact capacity depends on the downstream count model. A Poisson model has
\(B\) count coordinates, including the total rate. A likelihood conditioned on
a fixed total has only \(B-1\). A fixed-total mixture of \(K\) fractions therefore
needs at least \(K\) bins before all \(K-1\) free fraction directions can be
locally identifiable.

## Regularity and boundaries

Fisher covariance is a local quadratic approximation. It can fail near a
simplex boundary, for rare components, or when the likelihood has singular
directions. FisherBin projects numerical null directions out; it does not add a
ridge that invents information.

At a boundary, a symmetric Wald interval and a ratio of local-to-bootstrap
standard errors can be meaningless. Report how often constrained estimates hit
the boundary. Use profile-likelihood or another boundary-aware construction
when interval coverage for that component is required.

## When to use something else

Use the exact unbinned likelihood when it is available, validated, and cheap
enough. Use learned ratio or posterior inference when retaining continuous
events matters more than a hard interface. Use a one-dimensional discriminant
when there is genuinely one inferential direction and its calibration is
controlled. Use geometric bins when spatial locality or interpretability is the
primary goal rather than parameter precision.

FisherBin is most useful when hard bins are required and a credible local score
can be supplied. Its optimization dimension is the numerical rank of the score
information, regardless of whether the original observation space has fewer,
the same number of, or more coordinates than the parameter space.

Continue with the [first tutorial](../tutorials/first-partition.md).
