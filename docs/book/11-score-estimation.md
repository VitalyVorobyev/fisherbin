# 11. Exact, autodiff, and classifier-estimated scores

The quantization algebra is exact for whatever vectors it receives. Statistical interpretation
depends on how those vectors were obtained.

## Exact and automatic differentiation

An analytic callback can evaluate the local score directly. A differentiable normalized
`log_prob` can in principle be differentiated at \(\theta_0\); the resulting score is exact up to
model and numerical error. In either case, the reference measure is still required separately.

## Central classifier ratios

For coordinate \(j\), compare \(p(x\mid\theta_0-\delta_je_j)\) and
\(p(x\mid\theta_0+\delta_je_j)\). A calibrated classifier probability ratio, corrected for its
training priors, estimates their likelihood ratio. Then

$$
\hat s_j(x)=\frac{1}{2\delta_j}
\left[\log\frac{D_j(x)}{1-D_j(x)}-log\frac{\pi_{j,+}}{\pi_{j,-}}\right].
$$

**Proposition (central-difference bias).** For a smooth exact likelihood-ratio oracle, this equals
the local score plus \(O(\delta_j^2)\). Classifier approximation and calibration error add separate
terms.

## Multiclass component ratios

For class posterior \(\eta_k(x)\) trained under priors \(\pi_k\), relative component density is
proportional to \(\eta_k(x)/\pi_k\). Combining those ratios with reference mixture fractions yields
the constrained mixture score. Hidden clipping or renormalization would change the implied model
and is therefore forbidden at the transform boundary.

**Proposition (surrogate information).** If \(\hat s\ne s\), optimizing information from \(\hat s\)
does not in general optimize true Fisher information. True retained information must assign labels
with \(q(\hat s)\) and evaluate moments of \(s\).

Training, feature transforms, calibration, class priors, finite-difference steps, folds, hashes, and
validation metrics form classifier provenance. Cross-fitted or held-out predictions prevent direct
training overfit from masquerading as quantization performance.
