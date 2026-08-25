# Glossary

**Bin.** One category of a hard partition. After binning, events are represented
only by integer labels or aggregate counts.

**D-efficiency.** Geometric mean of retained-information eigenvalues. It
summarizes balanced local retention across informative parameter directions.

**Finite assignment.** Labels optimized for one fixed weighted score table. It
does not by itself define labels for unseen scores.

**Fisher information.** Expected outer product of the score. It measures local
model sensitivity, not estimator bias.

**Hard quantizer.** A deterministic score-space mapping that assigns every
score to exactly one bin.

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

**Population design.** Optimization of a measurable rule under a specified
score law rather than only its finite realization.

**Reference point.** Parameter value \(\theta_0\) at which scores and Fisher
information are evaluated.

**Score.** Gradient of log likelihood with respect to parameters. It describes
an event's local parameter sensitivity.

**Score law.** The distribution or intensity measure induced on score space by
a reference source and an observation-to-score provider.

**Score provider.** A map from observations to score vectors. It does not
supply a reference measure.

**Simplex.** Set of nonnegative fractions that sum to one. A \(K\)-component
mixture has \(K-1\) free directions.

**Source.** An empirical table or integration rule that supplies the reference
measure used by an objective.

**Surrogate information.** Between-cell information computed from estimated
scores. It is exact for those supplied vectors but not automatically Fisher
information of the original statistical model.

**Template.** Conditional bin probabilities \(P(B_j\mid k)\) for a model
component \(k\).

**Whitening.** Linear scaling of informative score directions so that their
unbinned Fisher matrix is the identity. ScoreQuant does not mean-center scores.
