# 12. Diagnostics, limitations, and choosing a method

No single objective value validates a quantization pipeline. Separate four error sources:

1. score-model error: \(\hat s\) differs from the true score;
2. integration error: the source approximates the wrong or insufficiently resolved measure;
3. optimization error: the solver misses a better rule in its task/family;
4. quantization error: the best chosen hard rule still loses information.

## Required diagnostics

- full and retained supplied-score information and effective rank;
- retained eigenvalues, determinant/trace summary, and PSD-loss residual;
- cell mass, row count, and effective sample size;
- exchange stability and remaining gain for finite D;
- train/validation difference for reusable rules;
- hardening gap for soft solvers;
- score provenance, calibration, prior correction, and mean-score closure;
- downstream bias/error and domain shift on frozen groups.

**Proposition (method choice).** Normalized-trace k-means is the simplest reusable baseline; exact D
exchange is appropriate for fixed-sample D assignment and, after verified compilation, a canonical
D rule; soft D is appropriate when directly fitting a geometric quantizer and accepting nonconvex
surrogate optimization. Profiled \(D_s\) and E require criterion-specific solvers and should not be
approximated by relabeling D output.

Use an unbinned likelihood when it is validated and affordable. Use ordinary geometric bins when
physical locality or rectangular interpretability is the true requirement. Use ScoreQuant when a
small hard interface is necessary and reliable local scores are available.

## FlowCyt capstone interpretation

The 600k deterministic corpus spans all 30 patients with a frozen patient-level split. Its report
compares score quantizers, physical-space and random baselines, and an unbinned classifier-ratio
fit. It audits calibration, mean-score closure, compression loss, identifiability, occupancy,
patient shift, gaps, and downstream fraction error. A 21.25M external corpus is reserved for a
transport/stress audit of the 600k approximation, not another tuning opportunity.

**Open problems.** Multi-reference robustness, weighted atomic geometry-gap rates, certified global
finite solvers at scale, population streaming, stable persistence, and valid treatment of signed
weights remain unresolved in the current design.
