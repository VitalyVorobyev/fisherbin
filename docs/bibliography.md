# Bibliography

These primary sources introduce the statistical ideas used by FisherBin. The
library combines established score compression, learned ratio/score estimation,
inference-aware optimization, and Fisher-aware quantization in a small hard-
partition workflow.

- Alsing and Wandelt, [*Generalized massive optimal data compression*](https://arxiv.org/abs/1712.00012). Introduces likelihood-score compression near a reference point.
- Brehmer et al., [*Mining gold from implicit models to improve likelihood-free inference*](https://arxiv.org/abs/1805.12244). Develops simulation-assisted likelihood-ratio and score estimators.
- Brehmer et al., [*A guide to constraining effective field theories with machine learning*](https://arxiv.org/abs/1805.00020). Includes the local score-based SALLY and SALLINO constructions.
- de Castro and Dorigo, [*INFERNO: Inference-Aware Neural Optimisation*](https://arxiv.org/abs/1806.04743). Optimizes a differentiable proxy for downstream inference precision.
- Valassi, [*Optimising HEP parameter fits via Monte Carlo weight derivative regression*](https://arxiv.org/abs/2003.12853). Constructs event sensitivities from simulated weight derivatives.
- Farias and Brossier, [*Optimal Scalar Quantization for Parameter Estimation*](https://arxiv.org/abs/1310.6945). Studies quantizer design through Fisher-information loss.

The links point to the papers themselves rather than secondary summaries. See
the [limitations chapter](learn/limitations.md) for where the local Fisher
picture needs additional validation.
