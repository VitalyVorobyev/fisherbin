# 2. Fisher-information quantization

> Curated theorem-level annotations. Machine records for the citation graph
> live in `graph.json`; `BIBLIOGRAPHY.md` (generated) maps every registry
> bibliography key to the heading that annotates it.

## Venkitasubramaniam, Tong & Swami (2006)

**Key:** Venkitasubramaniam-Tong-Swami-2006

**Paper:** *Score-Function Quantization for Distributed Estimation*  
**Core idea:** design quantizers in score-function space; scalar Fisher information loss is tied to score distortion; Lloyd–Max-style optimization.  
**Boundary marker:** “quantize scores to preserve Fisher information” is established prior art.

- Public PDF: https://www.lehigh.edu/~pav309/papers/VenkTongSwami_Quant_06CISS.pdf
- DOI: https://doi.org/10.1109/CISS.2006.286494

## Farias & Brossier (2013/2014)

**Key:** Farias-Brossier-2013

**Paper:** *Optimal Scalar Quantization for Parameter Estimation*  
**Result:** high-resolution asymptotics, optimal scalar point density, FI loss versus bit depth.  
**Use:** main template for ScoreQuant high-rate theory.

- PDF: https://arxiv.org/pdf/1310.6945
- DOI: https://doi.org/10.1109/TSP.2014.2318140

## Barnes, Han & Özgür (2018)

**Key:** Barnes-Han-Ozgur-2018

**Paper:** *A Geometric Characterization of Fisher Information from Quantized Samples with Applications to Distributed Statistical Estimation*  
**Result:** multivariate conditional-score geometry and trace-FI bounds under finite-bit quantization; special geometric optimality results.  
**Use:** closest published multivariate score-space ancestor.

- PDF: https://web.stanford.edu/~aozgur/FisherAllerton.pdf
- DOI: https://doi.org/10.1109/ALLERTON.2018.8635899

## Barnes, Han & Özgür (later communication-constrained work)

**Key:** Barnes-Han-Ozgur-2020

**Paper:** *Lower Bounds for Learning Distributions under Communication Constraints via Fisher Information*
**Use:** carries the quantized-Fisher geometry into minimax lower bounds for
interactive communication protocols.
**Not a partition solver:** the results constrain attainable information but
do not construct a deterministic hard quantizer.

- PDF: https://arxiv.org/pdf/1902.02890

## Venkitasubramaniam, Tong & Swami (2007)

**Key:** Venkitasubramaniam-Tong-Swami-2007

**Paper:** *Quantization for Maximin ARE in Distributed Estimation*
**Result:** optimizes the worst scalar asymptotic relative efficiency across
parameter values using score-function threshold quantizers and an iterative
design.
**Boundary marker:** this is robust scalar Fisher quantization, not a
multivariate determinant or profiled \(D_s\) partition theorem.

- DOI: https://doi.org/10.1109/TSP.2007.894279

## Dülek (2023)

**Key:** Dulek-2023

**Paper:** *On the Optimality of Sufficient Statistics-Based Quantizers*  
**Result:** for exponential families, an optimal deterministic K-level trace-FIM quantizer can be chosen with convex-polytopal cells in sufficient-statistic space.  
**Boundary marker:** multivariate hard Fisher-optimal polyhedral quantizers are known for trace.

- DOI: https://doi.org/10.1109/TPAMI.2022.3172282

## Zhang, Blum, Kaplan & Lu (2016/2018)

**Key:** Zhang-Blum-Kaplan-Lu-2018

**Paper:** *A Fundamental Limitation on Maximum Parameter Dimension for Accurate Estimation With Quantized Data*  
**Result:** quantization-induced identifiability/FIM singularity limitations.  
**Use:** related to the \(K-1\) rank ceiling.

- PDF: https://arxiv.org/pdf/1605.07679
- DOI: https://doi.org/10.1109/TIT.2018.2850968

## Domain-specific D-optimal threshold quantizers

**Key:** Jiang-et-al-2026

Several sensor/localization works optimize restricted quantizer thresholds or bit allocation by \(\det I\).

Example:

**Jiang et al. (2026)**, *Direct target localization in USNs with hybrid quantized multi-snapshot measurements: A geometric structure-aided approach*.

- DOI: https://doi.org/10.1016/j.dsp.2025.105552

**Boundary marker:** “using determinant Fisher information to design a quantizer” is not itself new.

---
