# Glossary

**Bin.** One category of a hard partition. After binning, events are represented
only by integer labels or aggregate counts.

**D-efficiency.** Geometric mean of retained-information eigenvalues. It
summarizes balanced local retention across informative parameter directions.

**Fisher information.** Expected outer product of the score. It measures local
model sensitivity, not estimator bias.

**Hard partition.** A deterministic mapping that assigns each event to exactly
one bin.

**Intensity.** An unnormalized event-rate model. Unlike a probability density,
its integral may encode expected yield.

**Likelihood.** The probability density or mass of observed data, viewed as a
function of model parameters.

**Likelihood ratio.** Ratio of two likelihoods or component densities. A
classifier posterior divided by its class prior can estimate component ratios
up to a common event-wise factor.

**Oracle.** A calculation using the exact data-generating likelihood or exact
score. A learned classifier ratio is not an oracle merely because it is used
without binning.

**Reference point.** Parameter value (	heta_0) at which scores and Fisher
information are evaluated.

**Score.** Gradient of log likelihood with respect to parameters. It describes
an event's local parameter sensitivity.

**Simplex.** Set of nonnegative fractions that sum to one. A (K)-component
mixture has (K-1) free directions.

**Template.** Conditional bin probabilities (P(B_j\mid k)) for a model
component (k).

**Whitening.** Linear scaling of informative score directions so that their
unbinned Fisher matrix is the identity. FisherBin does not mean-center scores.
