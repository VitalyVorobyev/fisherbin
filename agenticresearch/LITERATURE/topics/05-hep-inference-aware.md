# 5. Inference-aware summaries and HEP categorization

> Curated theorem-level annotations. Machine records for the citation graph
> live in `graph.json`; `BIBLIOGRAPHY.md` (generated) maps every registry
> bibliography key to the heading that annotates it.

## Brehmer, Louppe, Pavez & Cranmer (2020)

**Paper:** *Mining gold from implicit models to improve likelihood-free inference*  
**Ideas:** local score estimation, SALLY/SALLINO, simulation-based inference.  
**Use:** score oracle / local sufficient representation.

- DOI: https://doi.org/10.1073/pnas.1915980117

## de Castro & Dorigo (2019) — INFERNO

**Key:** deCastro-Dorigo-2019

**Paper:** *INFERNO: Inference-Aware Neural Optimisation*  
**Idea:** differentiable optimization of binned summaries against an inference objective.  
**Use:** practical adjacent categorization method; not exact hard D partition theory.

**DS18 audit (31 Aug 2026):** registered a bibliography key here because this is
the closest *applied* statement of the DS18 objective. INFERNO's loss is the
inverse Hessian of an Asimov binned-Poisson likelihood — a profiled-Fisher
surrogate — but the feasible set is a **soft**, differentiable histogram of a
neural summary. **What transfers:** the objective family and the confirmation
that nuisance-aware binning is the target practitioners want. **What does not:**
hard partitions, exactness, uniqueness, strict isolation in decision distance,
empirical-to-population transfer, and finite one-point exchange stability —
INFERNO reports no optimality theorem at all.

- DOI: https://doi.org/10.1016/j.cpc.2019.06.007

## Matchev & Shyamsundar (2021) — ThickBrick

**Paper:** *Optimal event selection and categorization in high energy physics. Part I. Signal discovery*  
**Idea:** event category optimization with inference-aware criteria and Lloyd-like structure.  
**Use:** highly relevant HEP categorization prior art.

- DOI: https://doi.org/10.1007/JHEP03(2021)291

## Valassi (2020) — weight-derivative regression

**Key:** Valassi-2020

**Paper:** *Optimising HEP parameter fits via Monte Carlo weight derivative regression* (CHEP2019)  
**Result:** defines the event-by-event sensitivity \(\gamma_i=(1/w_i)\,\partial w_i/\partial\theta\) — the
single-parameter score — shows the binned-fit information is \(I_\theta=\sum_k s_k\phi_k^2\) with
\(\phi_k=\langle\gamma\rangle_k\) the cell-mean sensitivity, and argues the optimal partitioning
variable is \(\gamma\) itself. Defines FIP\(_3=I_\theta/I_\theta^{(\rm ideal)}\in[0,1]\) and factors it as
FIP\(_{\rm efS}\times\)FIP\(_{\rm shS}\times\)FIP\(_{\rm shB}\) (efficiency \(\times\) signal sharpness \(\times\) background sharpness).  
**Boundary marker:** the \(d=1\) case of the score-space reduction and of the retained-information
identity is established prior art, stated in HEP language. FIP\(_3\) is \(\eta\) at \(s=1\); FIP\(_{\rm shS}\)
is precisely the sharpness of a hard binning of the score.  
**Boundary of what it does *not* do:** no multivariate score space, no determinant or any matrix
criterion, no nuisance profiling, and no optimality *theorem* for the binning — the partitioning
claim is an argument in the scalar case, not a geometric characterisation.  
**Open attribution question (for a literature session, not settled here):** whether FIP\(_3\) constitutes
prior art for `INFO-D-EFFICIENCY` at \(s=1\), and FIP\(_{\rm shS}\) for the retained-information ratio.
Both claims now cite it; neither has been demoted, and no
`literature_search_status` was set. Recorded in `reviewed.md`.

- arXiv PDF: https://arxiv.org/pdf/2003.12853
- Local copy: `../../../papers/valassi_2020_weight_derivative_regression_arXiv2003.12853.pdf`

## CMS Collaboration (2025) — SANNT

**Key:** CMS-2025

**Paper:** *Development of systematic uncertainty-aware neural network trainings for binned-likelihood
analyses at the LHC*  
**Method:** replaces cross-entropy with \(\Delta r_s=\sqrt{(F^{-1})_{r_s r_s}}\), where \(F\) is the Fisher
information of the binned likelihood over \(\{r_s\}\cup\{\theta_j\}\) and the \(\theta_j\) are up to 224
nuisance parameters. Applied to \(H\to\tau\tau\); 12–16% improvement in the signal-strength
uncertainty over a cross-entropy training.  
**Why it matters here:** \((F^{-1})_{r_sr_s}\) is the inverse Schur complement, so the SANNT objective is
the profiled criterion of `DS-SCHUR` with \(s=1\) — the production-scale realisation of the
\(D_s\) programme, arrived at independently.  
**Motivation datum:** the paper names our problem as its own open issue — the Fisher loss
"introduces an ambiguous choice of binning" and the binned likelihood "is not differentiable at its
bin edges". Its cited workarounds are INFERNO's softmax histogram and a KDE surrogate; neither is
an exact hard-partition result.  
**Not prior art for any registry theorem:** no claim cites it, deliberately. It uses the profiled
Fisher as a training loss and never studies the geometry of the optimal partition.

- DOI: https://doi.org/10.1140/epjc/s10052-025-14713-w
- Local copy: `../../../papers/cms_2025_systematic_aware_nn_training_arXiv2502.13047.pdf`

## Erdmann, Kasaraguppe & Mausolf (2026) — Learning to bin

**Paper:** *Learning to bin*  
**Idea:** direct learned multidimensional categories via differentiable/Bayesian methods.  
**Use:** modern software/algorithm comparison for category learning.

- arXiv PDF: https://arxiv.org/pdf/2601.07756

---
