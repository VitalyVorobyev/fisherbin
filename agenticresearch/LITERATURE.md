# Annotated literature map

**Purpose:** nearest prior art and proof/tool sources for ScoreQuant theorem agents.  
**Rule:** a source belongs here because it contributes a result, technique, counterpoint, or terminology relevant to the hard-partition problem. It does not imply direct equivalence.

---

# 1. Optimal experimental design backbone

## Kiefer & Wolfowitz (1960) — D-equivalence theorem

**Paper:** *The Equivalence of Two Extremum Problems*  
**Result:** in approximate linear design, D-optimality is equivalent to a pointwise maximum-variance/sensitivity condition.  
**Why important:** establishes \(M^{-1}\) as the natural D sensitivity metric and provides the archetype for a global optimality certificate.  
**Does not solve:** partition-induced information, score centroids, finite label relocation.

- PDF: https://www.cambridge.org/core/services/aop-cambridge-core/content/view/B8B0626C11F52B0FD8C67C5D54BDDD43/S0008414X00010002a.pdf/the-equivalence-of-two-extremum-problems.pdf
- DOI: https://doi.org/10.4153/CJM-1960-030-4

## Wynn (1970) — sequential D-optimal design construction

**Paper:** *The Sequential Generation of D-Optimum Experimental Designs*  
**Result:** sequentially add points chosen by sensitivity; convergence and generalized-variance bounds.  
**Use:** algorithmic/sensitivity analogy.

- DOI: https://doi.org/10.1214/aoms/1177696809

## Wynn (1972) — D and \(D_s\) construction

**Paper:** *Results in the Theory and Construction of D-Optimum Experimental Designs*  
**Result:** extends generation ideas to \(D_s\), selected parameter subsets, and discrete designs.  
**Use:** primary historical \(D_s\) source.

- DOI: https://doi.org/10.1111/j.2517-6161.1972.tb00896.x

## Whittle (1973) — general concave criteria

**Paper:** *Some General Points in the Theory of Optimal Experimental Design*  
**Result:** general concave criterion/equivalence viewpoint; consequences for iterative construction and transformations including \(D_s\)-related ideas.  
**Use:** closest classical template for asking which parts of D geometry extend to other criteria.

- DOI: https://doi.org/10.1111/j.2517-6161.1973.tb00944.x

## Kiefer (1974) — general equivalence theory

**Paper:** *General Equivalence Theory for Optimum Designs (Approximate Theory)*  
**Result:** broad \(\Phi\)-optimal theory including D, L, E and other criteria.  
**Use:** generic sensitivity/supergradient machinery.

- DOI: https://doi.org/10.1214/aos/1176342810

## Fedorov (1972) — optimal experiments and exchange

**Book:** *Theory of Optimal Experiments*  
**Use:** exact/discrete design, exchange construction, rank-update thinking.

- Book page: https://books.google.com/books?id=v6vTAvqGny4C

## Näther & Reinsch (1981) — \(D_s\) equivalence

**Paper:** *D_s-optimality and Whittle's equivalence theorem*  
**Result:** \(D_s\) equivalence including singular cases; simplified sufficient conditions.  
**Use:** nuisance/Schur-complement sensitivity.

- DOI: https://doi.org/10.1080/02331888108801591

## Pukelsheim — modern reference

**Book:** *Optimal Design of Experiments*  
**Use:** matrix criteria, efficiency, equivalence, geometric formulation.

- SIAM chapter DOI: https://doi.org/10.1137/1.9780898719109.ch7

## Nguyen & Miller (1992) — exchange algorithms

**Paper:** *A review of some exchange algorithms for constructing discrete D-optimal designs*  
**Use:** historical terminology and practical exchange design.

- DOI: https://doi.org/10.1016/0167-9473(92)90064-M

## Huan, Jagalur & Marzouk (2024) — modern OED survey

**Paper:** *Optimal Experimental Design: Formulations and Computations*  
**Use:** current map of D, \(D_A/D_s\), E, Bayesian/nonlinear OED, computation.

- PDF: https://www.cambridge.org/core/services/aop-cambridge-core/content/view/38BBD0DC1A0386FDF306B6C0167DF7D9/S0962492924000023a.pdf/optimal-experimental-design-formulations-and-computations.pdf

---

# 2. Fisher-information quantization

## Venkitasubramaniam, Tong & Swami (2006)

**Paper:** *Score-Function Quantization for Distributed Estimation*  
**Core idea:** design quantizers in score-function space; scalar Fisher information loss is tied to score distortion; Lloyd–Max-style optimization.  
**Boundary marker:** “quantize scores to preserve Fisher information” is established prior art.

- Public PDF: https://www.lehigh.edu/~pav309/papers/VenkTongSwami_Quant_06CISS.pdf
- DOI: https://doi.org/10.1109/CISS.2006.286494

## Farias & Brossier (2013/2014)

**Paper:** *Optimal Scalar Quantization for Parameter Estimation*  
**Result:** high-resolution asymptotics, optimal scalar point density, FI loss versus bit depth.  
**Use:** main template for ScoreQuant high-rate theory.

- PDF: https://arxiv.org/pdf/1310.6945
- DOI: https://doi.org/10.1109/TSP.2014.2318140

## Barnes, Han & Özgür (2018)

**Paper:** *A Geometric Characterization of Fisher Information from Quantized Samples with Applications to Distributed Statistical Estimation*  
**Result:** multivariate conditional-score geometry and trace-FI bounds under finite-bit quantization; special geometric optimality results.  
**Use:** closest published multivariate score-space ancestor.

- PDF: https://web.stanford.edu/~aozgur/FisherAllerton.pdf
- DOI: https://doi.org/10.1109/ALLERTON.2018.8635899

## Barnes, Han & Özgür (later communication-constrained work)

**Use:** Fisher-information budgets and lower bounds for distributed estimation/learning.  
**Not a partition solver.**

## Dülek (2023)

**Paper:** *On the Optimality of Sufficient Statistics-Based Quantizers*  
**Result:** for exponential families, an optimal deterministic K-level trace-FIM quantizer can be chosen with convex-polytopal cells in sufficient-statistic space.  
**Boundary marker:** multivariate hard Fisher-optimal polyhedral quantizers are known for trace.

- DOI: https://doi.org/10.1109/TPAMI.2022.3172282

## Zhang, Blum, Kaplan & Lu (2016/2018)

**Paper:** *A Fundamental Limitation on Maximum Parameter Dimension for Accurate Estimation With Quantized Data*  
**Result:** quantization-induced identifiability/FIM singularity limitations.  
**Use:** related to the \(K-1\) rank ceiling.

- PDF: https://arxiv.org/pdf/1605.07679
- DOI: https://doi.org/10.1109/TIT.2018.2850968

## Domain-specific D-optimal threshold quantizers

Several sensor/localization works optimize restricted quantizer thresholds or bit allocation by \(\det I\).

Example:

**Jiang et al. (2026)**, *Direct target localization in USNs with hybrid quantized multi-snapshot measurements: A geometric structure-aided approach*.

- DOI: https://doi.org/10.1016/j.dsp.2025.105552

**Boundary marker:** “using determinant Fisher information to design a quantizer” is not itself new.

---

# 3. Determinant clustering and partition exchange

## Friedman & Rubin (1967)

**Paper:** *On Some Invariant Criteria for Grouping Data*  
**Result:** classical affine-invariant determinant grouping criteria.  
**Use:** determinant partition objectives are old.

- DOI: https://doi.org/10.1080/01621459.1967.10500923

## Scott & Symons (1971)

**Paper:** *Clustering Methods Based on Likelihood Ratio Criteria*  
**Result:** likelihood/determinant clustering under multivariate models.

- DOI: https://doi.org/10.2307/2529003

## Marriott

Classical determinant-based clustering criteria; useful historical terminology and objective comparison.

## Späth (1977)

**Paper:** *Computational experiences with the exchange method: Applied to four commonly used partitioning cluster analysis criteria*  
**Result:** single-point exchange for classical partition criteria including determinant-type criteria.  
**Use:** strong algorithmic prior art for exchange + determinant.

- DOI: https://doi.org/10.1016/S0377-2217(77)81005-9

## Späth (1985)

**Book:** *Cluster Dissection and Analysis: Theory, FORTRAN Programs, Examples*  
**Result/use:** determinant exchange routines and matrix/scatter update machinery in executable form.

## Coleman, Dong, Hardin, Rocke & Woodruff (1999)

**Paper:** *Some computational issues in cluster analysis with no a priori metric*  
**Result:** computational study of determinant-style clustering and first-improvement versus steepest-ascent moves.

- DOI: https://doi.org/10.1016/S0167-9473(99)00009-2

### Critical distinction from ScoreQuant

Classical determinant clustering usually minimizes a determinant of pooled **within-cluster scatter** or an equivalent Gaussian likelihood criterion.

ScoreQuant maximizes

\[
\det\left(
\sum_bW_b\mu_b\mu_b^\top
\right),
\]

the determinant of retained **between-cell score Fisher information**.

For dimension \(d>1\), fixed total scatter \(T=W+B\) does not make \(\min\det W\) equivalent to \(\max\det B\).

### Targeted audit for `D-EXCHANGE-IMPLIES-VORONOI` — 26 August 2026

The priority-0 audit rechecked the nearest design, score-quantization, and
determinant-clustering sources specifically for the following finite claim:

\[
\text{exact one-point D-exchange stability}
\Longrightarrow
\text{strict self-consistent }I_q^{-1}\text{-Voronoi assignment}.
\]

No direct equivalent was located. This is recorded only as a **search gap**, not
as a novelty or priority claim.

- **Kiefer--Wolfowitz:** approximate-design determinant maximization and
  pointwise sensitivity over a convexified design-measure feasible set; no
  partition-induced centroids or label-removal update.
- **Venkitasubramaniam--Tong--Swami:** scalar score-function quantization and
  Fisher-information distortion; no multivariate full-D finite exchange result.
- **Barnes--Han--Özgür:** conditional-score representation and multivariate
  trace-Fisher geometry; no determinant objective or hard-label relocation
  theorem.
- **Dülek:** trace-FIM optimal sufficient-statistic quantizers with polytopal
  cells for exponential families; not the finite full-D exchange implication.
- **Friedman--Rubin / Späth / Coleman et al.:** determinant partition and
  exchange precedents. The accessible Späth `DETEXM` source explicitly computes
  and minimizes a determinant of pooled within-cluster scatter. That objective
  is not retained between-cell score Fisher information.

Additional inspected sources:

- Späth program source: https://people.math.sc.edu/Burkardt/f_src/spaeth/spaeth.f90
- Coleman et al. repository page: https://scholarship.claremont.edu/pomona_fac_pub/295/
- Friedman--Rubin article page: https://www.tandfonline.com/doi/abs/10.1080/01621459.1967.10500923

The complete assumption-by-assumption comparison and independent proof are in
`AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md`.

---

# 4. Vector quantization and Voronoi theory

## Pollard (1981, 1982) and the k-means consistency cluster

**Papers:** *Strong Consistency of K-Means Clustering* (Ann. Statist. 9:135–140);
*A Central Limit Theorem for k-Means Clustering* (Ann. Probab. 10:919–926);
*Quantization and the Method of k-Means* (IEEE IT 28:199–205).
Refinements: Abaya & Wise (1984, SIAM J. Appl. Math. 44:183–189, optimal
quantizers under weakly converging sources); Sverdrup-Thygeson (1981, Ann.
Statist. 9:141–145); Cuesta-Albertos & Matrán (1988, PTRF 78:523–534);
Lember (2003, J. Approx. Theory 120:20–35, minimizing sequences /
non-unique optima); Linder (2000, CISM 464 survey, VC/covering-number
finite-sample bounds).

**Use (triangulated 28 Aug 2026 for the DS14 bridge):** the two-step "uniform
LLN over configuration classes + argmin continuity" skeleton is the direct
template for DS14 Steps 3–5; Lember/Abaya–Wise handle non-unique optima
(needed for the Ds tie degeneracy DS11(c)).

**Does not transfer:** every member assumes a fixed source-independent metric
and per-point additive distortion; none covers a solution-dependent
semimetric (the fitted \(G_s\)) or a determinant/Schur functional of
aggregated cell moments; center-convergence uniqueness conditions have no
log-det analogue.

- DOI: https://doi.org/10.1214/aos/1176345339

## Graf & Luschgy (2000, 2002)

**Papers:** *Foundations of Quantization for Probability Distributions*
(Springer LNM 1730; Ch. 4 existence/stationarity of optimal quantizers under
moment conditions); *Rates of convergence for the empirical quantization
error* (Ann. Probab. 30:874–897; bracketing-entropy uniform LLN over
Voronoi-cell indicator classes).

**Use:** nearest published instance of a uniform LLN over Voronoi-type
partition classes (DS14 Step 3 companion to C1) and of
existence/stationarity machinery for population quantizers.

**Does not transfer:** the whole framework is additive per-point distortion;
no result covers a global nonlinear matrix functional of cell moments.

## Sabin & Gray (1986)

**Paper:** *Global convergence and empirical consistency of the generalized
Lloyd algorithm* (IEEE IT 32:148–155).

**Use:** closest structural precedent for the DS14 bridge shape — set
convergence of empirical *fixed-point* (locally certified, not globally
optimal) quantizers to the population fixed-point set, for convex additive
distortions.

**Does not transfer:** ordinary nearest-neighbor fixed points under a
source-independent convex cost; no margin/rate analysis; no
Schur-complement self-consistency.

## Set-valued M-estimation / epi-convergence templates

**Sources:** van der Vaart & Wellner (1996, Thm. 3.2.2 argmax theorem);
Rockafellar & Wets, *Variational Analysis* (1998, Ch. 7 epi-convergence:
inf-value convergence + cluster points of minimizers are minimizers);
Royset & Wets (2020, Ann. Statist. 48:2759–2790, constrained M-estimators
with set-valued minimizers); Molchanov, *Theory of Random Sets* (2005/2017,
argmin sets as random closed sets).

**Use:** abstract shell for "empirical optimizer set converges to population
optimizer set" that is agnostic to additivity and metric structure; the
right vocabulary for the exchange-stable solution *set*.

**Does not transfer:** supplies no concrete entropy or margin estimates for
partition classes — those come from C1/Graf–Luschgy-style VC arguments.

## Margin conditions in quantization

**Sources:** Levrard (2015, Ann. Statist. 43:592–619, k-means margin
condition bounding mass near optimal cell boundaries, fast rates; survey
2018 J. SFdS 159:1–48); Mammen & Tsybakov (1999, Ann. Statist.
27:1808–1829); Antos, Györfi & György (2005, individual rates).

**Use:** conceptual template for the DS14 slab-margin assumption (M4) and
for a future fast-rate refinement of the bridge.

**Does not transfer:** fast-rate mechanics rely on a Pythagorean identity for
squared Euclidean distortion with no known log-det/Schur analogue.

## Determinant-criterion consistency — confirmed search gap (28 Aug 2026)

Targeted triangulation found **no published consistency theory, at any rate,
for D- or \(D_s\)-type (determinant/Schur) partition criteria estimated from
i.i.d. samples** — neither in the sequential/asymptotic optimal-design
literature (fixed or regression-design point sets, not sampled partitions)
nor in determinant clustering (Friedman–Rubin line: algorithms only). DS14
appears to be the first such bridge; recorded as a search gap, not a novelty
claim.

### Targeted audit for the DS-POPULATION-BRIDGE claims — 28 August 2026

The independent audit (`AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md`) reran the
novelty searches for DS11–DS14 with fresh queries. Two outcomes.

**DS11 (`DS-PROFILED-VARIATIONAL`): prior art found.** The boxed identity is
the extremal characterization of the generalized Schur complement.

- **Li & Mathias (2000)**, *Extremal Characterizations of the Schur Complement
  and Resulting Inequalities*, SIAM Review 42(2):233–246,
  doi:10.1137/S0036144599337290. **Exact problem:** PSD block matrix \(H\),
  generalized Schur complement \(S(H)=H_{22}-H_{12}^*H_{11}^\dagger H_{12}\).
  **Exact result (Thm 2.2):** \([Z|I]H[Z|I]^*\ge S(H)\) in the Loewner order
  for every \(Z\), equality iff \((Z+H_{12}^*H_{11}^\dagger)H_{11}=0\).
  **Transfers:** with \(Z=-B\) this is DS11's identity verbatim, including the
  Moore–Penrose extension and the exact attainment set \(BI_{\lambda\lambda}
  =I_{\psi\lambda}\). The paper attributes the characterization to **M. G.
  Krein (1947)** and notes **Anderson's shorted operator (1971;
  Anderson–Trapp 1975)** and Butler–Morley as independent sources.
  **Does not cover:** the binned-score reading via U1 (which needs centered
  scores), the refinement-neutrality/wasted-cell corollaries on the quantizer
  feasible set, and the DS9 feasibility-boundary observation — those stay
  project-level.
- **Classical statistics form:** the efficient score
  \(\ell_\psi-I_{\psi\lambda}I_{\lambda\lambda}^{-1}\ell_\lambda\) with
  variance the Schur complement (van der Vaart 1998 §25.4;
  Bickel–Klaassen–Ritov–Wellner 1993) is the nonsingular statistical special
  case; best-linear-predictor/partial-covariance algebra is the regression
  form.

**DS12–DS14: search gap re-confirmed.** Independent queries (adaptive/
Mahalanobis quantizer consistency with solution-dependent metrics;
determinant-criterion partition consistency; profiled-Fisher binning in HEP)
found no direct equivalent. New nearest-practice sources recorded:

- **INFERNO (de Castro & Dorigo 2018)** and **binned Poisson-likelihood NN
  optimization (Wunsch et al. 2020, doi:10.1007/s41781-020-00049-5)**:
  optimize profiled/Asimov Fisher information of binned likelihoods with
  nuisance parameters through soft binning — the engineering practice a DS14
  bridge would certify. **Does not transfer:** algorithms only; no hard-bin
  finite-to-population consistency statement, no margin analysis.
- **"Learning to bin" (2026, arXiv:2601.07756)**: differentiable/Bayesian
  optimization of multi-dimensional hard binnings for HEP discriminants;
  same status — optimization practice, no consistency theory.

The Pollard/Graf–Luschgy/Sabin–Gray non-transfer table above was re-checked
against the original settings and stands: fixed source-independent metrics
and additive per-point distortion throughout; no determinant/Schur functional
of aggregated cell moments, no fitted-semimetric self-consistency.

## Du, Faber & Gunzburger (1999)

**Paper:** *Centroidal Voronoi Tessellations: Applications and Algorithms*  
**Use:** CVT theory, Lloyd algorithm, geometric quantization.

- DOI: https://doi.org/10.1137/S0036144599352836

## Du, Emelianenko & Ju (2006)

**Paper:** *Convergence of the Lloyd Algorithm for Computing Centroidal Voronoi Tessellations*  
**Use:** convergence methods and assumptions for Lloyd/CVT.

- DOI: https://doi.org/10.1137/040617364

## Richter & Alexa (2015)

**Paper:** *Mahalanobis centroidal Voronoi tessellations*  
**Use:** adjacent common/anisotropic metric Voronoi geometry.

- DOI: https://doi.org/10.1016/j.cag.2014.09.009

## Bregman Voronoi / quantization literature

**Use:** generalized centroid/dual-space geometry and local distortion approximations.

**Caution:** ScoreQuant D objective is global/nonadditive, so Bregman/CVT results do not transfer automatically.

---

# 5. Inference-aware summaries and HEP categorization

## Brehmer, Louppe, Pavez & Cranmer (2020)

**Paper:** *Mining gold from implicit models to improve likelihood-free inference*  
**Ideas:** local score estimation, SALLY/SALLINO, simulation-based inference.  
**Use:** score oracle / local sufficient representation.

- DOI: https://doi.org/10.1073/pnas.1915980117

## de Castro & Dorigo (2019) — INFERNO

**Paper:** *INFERNO: Inference-Aware Neural Optimisation*  
**Idea:** differentiable optimization of binned summaries against an inference objective.  
**Use:** practical adjacent categorization method; not exact hard D partition theory.

- DOI: https://doi.org/10.1016/j.cpc.2019.06.007

## Matchev & Shyamsundar (2021) — ThickBrick

**Paper:** *Optimal event selection and categorization in high energy physics. Part I. Signal discovery*  
**Idea:** event category optimization with inference-aware criteria and Lloyd-like structure.  
**Use:** highly relevant HEP categorization prior art.

- DOI: https://doi.org/10.1007/JHEP03(2021)291

## Erdmann, Kasaraguppe & Mausolf (2026) — Learning to bin

**Paper:** *Learning to bin*  
**Idea:** direct learned multidimensional categories via differentiable/Bayesian methods.  
**Use:** modern software/algorithm comparison for category learning.

- arXiv PDF: https://arxiv.org/pdf/2601.07756

---

# 6. Software landscape

## Historical determinant partitioning

- Späth FORTRAN code: direct historical example of determinant exchange and matrix-update implementation.

## Optimal design packages — adjacent

Useful for algorithms/terminology, not direct hard score quantization:

- PyOptEx
- PyDOE optimal-design functionality
- optdesign
- BoFire / DoE ecosystems
- OApackage

## HEP/inference-aware toolkits — adjacent

- MadMiner: score/likelihood-ratio estimation and local optimal observables.
- INFERNO implementations: differentiable inference-aware summaries.
- ThickBrick-related categorization code where available.
- Learning-to-bin / modern differentiable category optimizers.

## General binning packages

- OptBinning and related supervised binning packages solve different objectives (predictive/monotonic/statistical binning), useful only as engineering/interface references.

## Current software gap

No public package was identified whose central abstraction is:

> multivariate hard score-space quantization with D and \(D_s\) objectives, exact information accounting, direct-score / density-ratio / calibrated-classifier interfaces, deployable partitions, and theorem-aware optimality diagnostics.

This is a **search gap**, not a proof of uniqueness.

---

# 7. Paper reading order for literature study

(This orders the *papers* below for a literature deep-dive; the workspace read
order is defined once, in `README.md`.)

1. `PROBLEM.md`
2. Kiefer–Wolfowitz (D sensitivity/equivalence)
3. Whittle + Wynn 1972 + Näther–Reinsch (\(D_s\), general criteria)
4. Venkitasubramaniam–Tong–Swami (score quantization)
5. Barnes–Han–Özgür (multivariate quantized-FI geometry)
6. Dülek (trace-optimal polytopal quantizers)
7. Späth 1977/1985 + Coleman et al. (determinant exchange prior art)
8. Pollard + CVT/Lloyd literature (population consistency/geometric algorithms)
9. SALLY/SALLINO, INFERNO, ThickBrick, Learning to bin (HEP/practical inference-aware context)
10. `KNOWN_RESULTS.md` and the project theorem registry

---

# 8. Search vocabulary for new prior art

Use combinations of:

- D-optimal quantization
- determinant Fisher information quantizer
- D_s optimal quantization
- nuisance-parameter optimal quantizer
- Fisher-information partition
- score-space quantization
- score-function quantization
- sufficient-statistic quantizer
- conditional score Fisher information
- determinant clustering exchange
- minimum determinant partition
- Hartigan determinant clustering
- Mahalanobis Voronoi quantization
- information preserving binning
- inference-aware categorization
- optimal event categories
- template fit bin optimization
- density-ratio binning Fisher information
- communication-constrained estimation Fisher quantization

Always inspect the actual theorem/objective; title-level similarity is not enough.
# 9. Additional score-compression and ratio-estimation sources (v2 update)

## Heavens, Jimenez & Lahav (2000) — MOPED

**Paper:** *Massive Lossless Data Compression and Multiple Parameter Estimation from Galaxy Spectra*  
**Result:** continuous linear compression to one summary per parameter preserving Fisher information under the paper's assumptions.  
**Use:** important ancestor for the “unbinned score/continuous compression is the information reference” viewpoint; not a finite hard quantizer.

- arXiv PDF: https://arxiv.org/pdf/astro-ph/9911102

## Alsing & Wandelt (2018) — generalized score compression

**Paper:** *Generalized Massive Optimal Data Compression*  
**Result:** likelihood-score compression gives locally Fisher-optimal continuous summaries under broad regularity conditions.  
**Use:** direct conceptual bridge from full observations to the score-space representation before finite quantization.

- arXiv PDF: https://arxiv.org/pdf/1712.00012

## Brehmer et al. — SALLY/SALLINO and MadMiner

**Use:** learned likelihood-score representations and practical score-space histograms in HEP. Establishes that learned scores and score histograms are prior art; ScoreQuant's question is how to optimize the hard cells under D/\(D_s\).

- Mining Gold PDF: https://arxiv.org/pdf/1805.12244
- MadMiner PDF: https://arxiv.org/pdf/1907.10621

## Wunsch et al. (2021)

**Paper:** *Optimal Statistical Inference in the Presence of Systematic Uncertainties Using Neural Network Optimization Based on Binned Poisson Likelihoods with Nuisance Parameters*  
**Use:** close HEP comparator for differentiable binned likelihood optimization with nuisances.

- arXiv PDF: https://arxiv.org/pdf/2003.07186

## Simpson & Heinrich (2022/23) — neos

**Paper:** *neos: End-to-End-Optimised Summary Statistics for High Energy Physics*  
**Use:** differentiable end-to-end expected-sensitivity optimization; adjacent software baseline, not score-Fisher hard partition theory.

- arXiv PDF: https://arxiv.org/pdf/2203.05570

## Density-ratio estimation

Direct density-ratio estimation (KLIEP, uLSIF and related methods) is a mature alternative to separately estimating component densities. Classifier posterior odds are another route. For ScoreQuant these are **model-access backends**, not the quantizer itself.

Useful reference: Sugiyama, Suzuki & Kanamori, *Density Ratio Estimation in Machine Learning*.

### Research-agent instruction

When a theorem depends on a density-ratio/classifier assumption, search the ratio-estimation literature separately from the quantization literature. Do not infer exact Fisher preservation merely from classifier discrimination performance.
