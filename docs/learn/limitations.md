# Limitations and alternatives

## Local reference point

Scores and Fisher information are evaluated at (	heta_0). A partition can
lose performance when the true parameter is far away. Check several reference
points externally when a wide region matters.

## Approximate scores

FisherBin preserves information present in its inputs. It does not certify that
learned scores equal likelihood derivatives. Cross-fitting, calibration audits,
closure tests, and untouched cohorts remain necessary.

## Hard-partition capacity

Few bins cannot retain many independent directions. Sparse or empty bins also
make downstream templates unstable even when the retained Fisher matrix looks
good. Occupancy is an operational constraint, not a cosmetic plot.

## Regularity and boundaries

Fisher covariance is a local quadratic approximation. It can fail near a
simplex boundary, for rare components, or when the likelihood has singular
directions. FisherBin projects numerical null directions out; it does not add a
ridge that invents information.

## When to use something else

Use the exact unbinned likelihood when it is available, validated, and cheap
enough. Use learned ratio or posterior inference when retaining continuous
events matters more than a hard interface. Use a one-dimensional discriminant
when there is genuinely one inferential direction and its calibration is
controlled. Use geometric bins when spatial locality or interpretability is the
primary goal rather than parameter precision.

FisherBin is most useful when hard bins are required, the parameter dimension
is modest, and a credible local score can be supplied.

Continue with the [first tutorial](../tutorials/first-partition.md).
