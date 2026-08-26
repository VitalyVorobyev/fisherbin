# ScoreQuant research dossier: information-optimal quantization and partitioning

**Status:** literature-and-theorem reference for research agents  
**Last updated:** 26 August 2026  
**Primary use:** a compact but provenance-aware context document for an LLM or human working on open theorems in hard Fisher-information-preserving quantization.

---

## 0. How to use this document

This is deliberately **not** a narrative literature review. It is a working research dossier. The goal is to prevent an LLM from (i) rediscovering classical optimal-design theory, (ii) confusing adjacent determinant clustering with the ScoreQuant objective, or (iii) treating project-derived results as published prior art.

### Status labels

- **[LIT]** — result explicitly supported by published literature.
- **[BRIDGE]** — straightforward synthesis or transfer of published facts to the present notation; useful, but not a safe novelty claim.
- **[PROJECT]** — result currently derived/tested inside ScoreQuant; treat as unpublished until externally verified.
- **[NEGATIVE]** — counterexample or failure mode found in the project.
- **[SEARCH-GAP]** — targeted search did not find a direct precedent; this is *not* proof of novelty.
- **[OPEN]** — open problem worth assigning to a theorem agent.

### Research-agent rule

For any attempted theorem, first identify which objects are being optimized:

1. **experimental design** — choose/add design points or weights;
2. **sensor/resource selection** — choose measurements, powers, or bit allocations;
3. **quantizer thresholds** — optimize a restricted scalar/vector threshold family;
4. **finite sample labels** — partition a fixed set of score vectors;
5. **inductive hard quantizer** — learn a function `q(s)` for future observations;
6. **population quantizer** — optimize measurable cells under a score distribution.

The same criterion name (`D`, `D_s`, `E`) does **not** make these optimization problems equivalent.

---

# 1. Problem and notation

Let `X ~ P_theta` be a regular model and fix a reference parameter `theta_0 in R^d`. Define the score

\[
S=s(X)=\nabla_\theta \log p(X\mid\theta)\big|_{\theta_0},
\qquad \mathbb E[S]=0,
\qquad I_{\rm full}=\mathbb E[SS^\top]\succ0.
\]

A deterministic `K`-level score-space quantizer is

\[
q:\mathbb R^d\to\{1,\ldots,K\},\qquad Z=q(S).
\]

For cell `b`, define

\[
W_b=P(Z=b),\qquad
m_b=\mathbb E[S\,1_{Z=b}],\qquad
\mu_b=\frac{m_b}{W_b}=\mathbb E[S\mid Z=b].
\]

## 1.1 Quantized Fisher-information identity

**[LIT/BRIDGE]** Under the usual regularity assumptions and a parameter-independent quantizer, the score of the discrete label is the conditional score mean,

\[
\nabla_\theta\log P_\theta(Z=b)\big|_{\theta_0}
=\mathbb E[S\mid Z=b]=\mu_b.
\]

Therefore

\[
\boxed{
I_q
=\operatorname{Var}(\mathbb E[S\mid Z])
=\sum_{b=1}^K W_b\mu_b\mu_b^\top
=\sum_{b=1}^K\frac{m_bm_b^\top}{W_b}.
}
\]

This is the core identity connecting **quantization** and **matrix-valued Fisher information**. Barnes, Han & Özgür (2018) use the same conditional-score geometry for the trace of quantized FIM; score-function quantization papers give the scalar counterpart.

The law of total covariance gives

\[
\boxed{
I_{\rm full}-I_q
=\mathbb E[\operatorname{Cov}(S\mid Z)]\succeq0.
}
\]

Hence hard quantization loses precisely the average within-cell score covariance.

### Rank constraint

Since `sum_b m_b = E[S]=0`,

\[
\operatorname{rank}(I_q)\le \min(d,K-1).
\]

Thus `K >= d+1` is necessary for positive-definite unregularized `D`-optimal information.

---

# 2. The five literatures that meet here

## 2.1 Optimal experimental design

**Question:** Which experimental settings or design weights maximize a scalar functional of an information matrix?

Core names: Wald; Kiefer; Wolfowitz; Fedorov; Wynn; Whittle; Pukelsheim.

Important inheritance:

- `D`-optimality: maximize `log det M` or `det(M)^(1/p)`.
- `D_s` / `D_A`: optimize information for a subset or linear combinations of parameters in the presence of nuisance parameters.
- `E`: maximize the smallest eigenvalue.
- General equivalence theorems convert a global design optimum into a pointwise sensitivity inequality.
- Exchange / vertex-direction algorithms exploit rank-one information changes.

**Critical non-equivalence:** an approximate design has an additive information matrix `M(xi)=int m(x) dxi(x)` over a convex design-measure set. A quantizer has

\[
I_q=\sum_b m_bm_b^\top/W_b,
\]

which is nonlinear in cell moments and whose feasible set is induced by partitions. Classical equivalence theorems are therefore a conceptual and technical toolkit, not an off-the-shelf solution to partition optimization.

## 2.2 Fisher-optimal quantization / distributed estimation

**Question:** How should a finite alphabet be assigned to observations to retain information about unknown parameters?

Core names: Venkitasubramaniam, Tong, Swami; Farias, Brossier; Barnes, Han, Özgür; Dülek.

Established facts:

- scalar Fisher-information loss can be represented as distortion of the score;
- Lloyd–Max can optimize scalar score quantizers;
- multivariate quantized FIM has a geometric conditional-score representation;
- trace-optimal hard quantizers can have convex-polytopal structure in sufficient-statistic space for exponential families.

**This is the closest direct ancestor of ScoreQuant.**

## 2.3 Determinant clustering and partition exchange

**Question:** Partition multivariate observations using determinant / likelihood criteria, often with an unknown common covariance metric.

Core names: Friedman & Rubin; Scott & Symons; Marriott; Späth; Coleman, Dong, Hardin, Rocke & Woodruff.

Important results/tools:

- determinant criteria in partitioning are classical, not new;
- Späth's exchange algorithms include a determinant criterion and matrix-factor update machinery;
- first-improvement and steepest-ascent one-point moves were used decades ago.

**Critical distinction:** the classical objective is typically the determinant of pooled **within-cluster scatter** (or a likelihood-ratio equivalent under Gaussian cluster models), whereas ScoreQuant maximizes the determinant of **between-cell score scatter**, which is the FIM of the discrete label. With `T=W+B` fixed, `min det(W)` and `max det(B)` are not equivalent in dimensions greater than one.

## 2.4 Vector quantization / centroidal Voronoi theory

Core names: Lloyd; Gersho & Gray; Pollard; Du, Faber & Gunzburger; Du, Emelianenko & Ju; Bregman Voronoi literature.

Established facts:

- squared-error quantization gives centroidal Voronoi stationary geometry;
- Lloyd iterations are monotone for the additive distortion they optimize;
- strong empirical-to-population consistency is known for `k`-means under suitable conditions;
- anisotropic / Mahalanobis centroidal Voronoi tessellations and Bregman Voronoi quantization are mature adjacent theories.

This provides proof templates for existence, consistency, Voronoi structure, and algorithm convergence — but the ScoreQuant `log det I_q` objective is global/nonadditive.

## 2.5 Inference-aware learned summaries and categorization

Examples: SALLY/SALLINO, INFERNO, ThickBrick, differentiable `Learning to bin` / GATO-style methods.

These establish that:

- learned scores are practical representations;
- downstream histograms/categories can be optimized for statistical inference;
- soft-to-hard differentiable category learning is established adjacent work.

They do **not** appear to provide the exact full-matrix hard score-space `D` / `D_s` partition theory discussed below.

---

# 3. Criterion dictionary

Assume `I=I_q` is positive definite unless noted.

## 3.1 Full `D`-optimality

\[
\Phi_D(I)=\log\det I,
\qquad \nabla_I\Phi_D=I^{-1}.
\]

Interpretation: maximize local confidence-ellipsoid volume reduction / generalized precision. It is invariant (up to an additive constant in log-det) under nonsingular reparameterization.

### Classical design sensitivity

**[LIT]** Kiefer–Wolfowitz: in linear approximate design, `D`-optimality is equivalent to minimizing maximum prediction variance; at an optimum with `p` parameters,

\[
f(x)^\top M(\xi)^{-1}f(x)\le p
\]

for all design points, with equality on support under standard conditions.

### Quantizer first variation

**[PROJECT/BRIDGE]** If infinitesimal score mass at `s` moves from cell `a` to `b`, then

\[
dI
=\left[(s-\mu_a)(s-\mu_a)^\top-(s-\mu_b)(s-\mu_b)^\top\right]d\varepsilon.
\]

For any differentiable matrix criterion `F(I)` with symmetric gradient `G`,

\[
\frac{dF}{d\varepsilon}
=(s-\mu_a)^\top G(s-\mu_a)
-(s-\mu_b)^\top G(s-\mu_b).
\]

For `D`, `G=I^{-1}`. A population first-order stationary hard quantizer therefore satisfies

\[
q(s)\in\arg\min_b (s-\mu_b)^\top I^{-1}(s-\mu_b)
\quad \text{a.e.}
\]

The common quadratic term cancels in pairwise comparisons, so boundaries are hyperplanes. Thus the stationary cells form a **self-consistent common-metric Mahalanobis Voronoi / affine max partition**.

### Exact finite relocation

**[PROJECT]** For a weighted finite sample, move point `(s,w)` from non-singleton cell `a` to `b`, with current weights and centroids `(W_a,mu_a)` and `(W_b,mu_b)`. Define

\[
u_a=s-\mu_a,\qquad u_b=s-\mu_b,
\]

\[
\alpha=\frac{wW_a}{W_a-w},\qquad
\beta=\frac{wW_b}{W_b+w}.
\]

Then the information update is exactly rank two:

\[
\boxed{\Delta I=\alpha u_au_a^\top-\beta u_bu_b^\top.}
\]

With `H=I^{-1}` and

\[
q_{aa}=u_a^\top Hu_a,\quad q_{bb}=u_b^\top Hu_b,\quad q_{ab}=u_a^\top Hu_b,
\]

\[
\boxed{
\Delta\log\det I
=\log\left[(1+\alpha q_{aa})(1-\beta q_{bb})+\alpha\beta q_{ab}^2\right].
}
\]

This yields an exact `O(d^2)`-type candidate move with inverse/Cholesky caching.

### Finite geometry theorem

**[PROJECT; highest-value prior-art target]** A determinant-specific leverage inequality implies:

> Every positive-definite finite partition stable against all admissible one-point moves is a **strict self-consistent `I^{-1}`-Mahalanobis Voronoi partition** (after duplicate score atoms are handled appropriately).

This is stronger than ordinary first-order stationarity because it converts **finite exchange stability** into the population-style geometric assignment rule. The converse fails: a Voronoi fixed point need not be exchange-stable.

**[SEARCH-GAP]** We found close determinant-exchange prior art in clustering and rank-update prior art in optimal design, but no direct published theorem matching this implication for `max log det` of between-cell score scatter.

### Algorithmic consequences under current project theory

- strict-gain one-point exchange is monotone and terminates on finite samples;
- terminal states have a canonical inductive predictor (their self-consistent Mahalanobis cells);
- Voronoi realizability constrains global search;
- current project derives an `N^{O(Kd)}` exact arrangement-enumeration route for fixed `(d,K)` (XP, not known FPT);
- refinement monotonicity gives a branch-and-bound upper bound.

These are **project claims**, not classical experimental-design results.

---

## 3.2 `D_s` / `D_A` optimality: parameters of interest with nuisance parameters

Partition parameters as `theta=(psi,lambda)`, where `psi in R^s` is of interest. Write

\[
I=\begin{pmatrix}
I_{\psi\psi} & I_{\psi\lambda}\\
I_{\lambda\psi} & I_{\lambda\lambda}
\end{pmatrix}.
\]

The efficient/profiled information for `psi` is the Schur complement

\[
I_{\rm eff}
=I_{\psi\psi}-I_{\psi\lambda}I_{\lambda\lambda}^{-1}I_{\lambda\psi}.
\]

A `D_s` objective is

\[
\Phi_{D_s}(I)=\log\det I_{\rm eff}
=\log\det I-\log\det I_{\lambda\lambda}
\]

when the blocks are nonsingular. More generally `D_A` optimizes selected linear combinations `A^T theta`, often written via `A^T M^{-1}A`.

### Classical design theory

**[LIT]** Wynn (1972) extends sequential `D`-design generation to `D_s` for a selected subset of `s` parameters. Whittle (1973) gives a general concave-criterion equivalence framework and characterizes `D_s` under transformations. Näther & Reinsch (1981) develop a `D_s` equivalence theorem including singular cases via an information-matrix transformation.

A common `D_s` sensitivity form in block regression design is

\[
f(x)^\top M^{-1}f(x)
-f_\lambda(x)^\top M_{\lambda\lambda}^{-1}f_\lambda(x)
\le s,
\]

with appropriate assumptions/notation. This is the design analogue of efficient-information geometry.

### Quantizer geometry

**[PROJECT/BRIDGE]** The same infinitesimal move identity applies. The derivative matrix of `Phi_Ds` can be represented as a positive-semidefinite rank-`s` efficient-information metric (equivalently through the Schur-complement / efficient-score construction). Population stationarity again yields common-semimetric affine cell inequalities.

### Crucial finite-sample difference from `D`

**[NEGATIVE/PROJECT]** The exact finite implication

`exchange-stable => own first-order Voronoi assignment`

fails for profiled `D_s`. Exhaustive finite examples in the project include **globally optimal finite assignments** that violate their own first-order geometric rule.

Therefore do not silently transfer the full-D theorem to `D_s`.

### Current positive project results

**[PROJECT]**

1. An exact finite move oracle can still be derived using low-rank updates of the full and nuisance blocks.
2. The finite geometry violation for an exchange-stable state is bounded at order `O(K/N)` under balanced sampling (current project statement; verify exact assumptions before proof work).
3. Quantizing the **full-data efficient score** under full `D` supplies an upper problem / information bound for `D_s` quantization.

### Main open bridge

**[OPEN]** Does the `O(K/N)` finite violation plus regularity imply that global/exchange-stable finite `D_s` solutions converge to population efficient-Voronoi stationary quantizers? This is one of the best theorem-agent targets.

**[SEARCH-GAP]** Targeted searches found extensive classical `D_s` *experimental-design* theory but no direct literature on unrestricted hard score-space partitions optimized by profiled `D_s` information.

---

## 3.3 `E`-optimality

\[
\Phi_E(I)=\lambda_{\min}(I).
\]

Interpretation: maximize the weakest information direction / minimize the worst principal asymptotic variance direction.

### Classical design geometry

**[LIT]** `lambda_min` is concave but nonsmooth when the minimum eigenvalue is repeated. At an `E`-optimal design, a supporting supergradient can be chosen from the convex hull of projectors onto the minimum eigenspace. In a regression setting this leads to an extremal inequality of the form

\[
f(x)^\top G f(x)\le \lambda_{\min}(M),
\]

where

\[
G=\sum_j w_j q_jq_j^\top,\qquad
w_j\ge0,\quad \sum_jw_j=1,
\]

and `q_j` span the minimum-eigenvalue eigenspace (normalization conventions vary by source).

Kiefer's general equivalence theory includes `E`-optimality. Recent computation work treats the repeated-eigenvalue case with SDP/subgradient machinery.

### Quantizer consequences

**[PROJECT/BRIDGE]** For a chosen common supergradient `G`, the infinitesimal cell rule is again

\[
q(s)\in\arg\min_b (s-\mu_b)^\top G(s-\mu_b).
\]

But the nonsmooth criterion creates an extra global-consistency issue: a single `G` must support all relevant cell inequalities.

### Finite failure

**[NEGATIVE/PROJECT]** Globally optimal finite `E` assignments can violate a naive one-point first-order geometric rule. Repeated minimum eigenvalues can make the first-order direction non-identifying.

### Open theorem

**[OPEN]** Population common-supergradient theorem: prove or refute that every suitable population `E` optimum admits **one common minimum-eigenspace supergradient** supporting all cell inequalities almost everywhere.

---

## 3.4 `A`-optimality and trace criteria (important controls)

Classical `A`-optimality minimizes `tr(I^{-1})`; a concave maximization form is

\[
\Phi_A(I)=-\operatorname{tr}(I^{-1}),
\qquad \nabla\Phi_A(I)=I^{-2}.
\]

**[PROJECT/NEGATIVE]** The determinant-specific finite exchange-to-Voronoi implication should not be assumed for `A`; project counterexamples indicate failure.

A different, especially important criterion is normalized retained **trace information**,

\[
\operatorname{tr}(I_{\rm full}^{-1}I_q).
\]

After Fisher whitening `z=I_full^{-1/2}s`,

\[
d-\operatorname{tr}(I_{\rm full}^{-1}I_q)
=\mathbb E\|z-\mathbb E[z\mid Z]\|^2.
\]

Thus maximizing normalized trace is exactly weighted squared-error vector quantization / `k`-means in Fisher-whitened score space.

**[BRIDGE, essentially known]** Scalar score-distortion equivalence is explicit in score-function quantization; Barnes et al. supply the multivariate conditional-score formula; Dülek proves trace-optimal convex-polytopal quantizers in exponential families. Treat the whitened `k`-means statement as a clean synthesis, not a headline novelty theorem.

---

# 4. Publication ledger: what each source actually gives us

## A. Optimal-design backbone

### A1. Kiefer & Wolfowitz (1960), *The Equivalence of Two Extremum Problems*

**Problem.** Approximate regression design.  
**Result.** Maximizing determinant of the information matrix is equivalent to minimizing the maximum variance/sensitivity `f(x)^T M^{-1} f(x)`; at optimum the maximum equals the parameter dimension.  
**Technique.** Convexity + directional/sensitivity argument.  
**Use for us.** Explains why `I^{-1}` is the natural local metric for `D`; template for global certificates.  
**Does not prove.** Anything about quantizer partitions, conditional score centroids, or finite label exchanges.  
**PDF:** https://www.cambridge.org/core/services/aop-cambridge-core/content/view/B8B0626C11F52B0FD8C67C5D54BDDD43/S0008414X00010002a.pdf/the-equivalence-of-two-extremum-problems.pdf  
**DOI:** https://doi.org/10.4153/CJM-1960-030-4

### A2. Wynn (1970), *The Sequential Generation of D-Optimum Experimental Designs*

**Result.** Convergence to a D-optimum design measure by sequentially adding maximum-variance design points; gives bounds on generalized variance.  
**Use for us.** Algorithmic analogy: sensitivity-driven update and monotonic information improvement.  
**Do not conflate.** Adding an experiment is not moving probability mass between quantizer cells.  
**DOI:** https://doi.org/10.1214/aoms/1177696809

### A3. Wynn (1972), *Results in the Theory and Construction of D-Optimum Experimental Designs*

**Result.** Extends the generation theorem to `D_s` designs for a selected parameter subset; also treats discrete designs with fixed number of points and efficiency bounds.  
**Use for us.** Essential historical `D_s` source; useful for sensitivity and asymptotic-algorithm analogies.  
**DOI:** https://doi.org/10.1111/j.2517-6161.1972.tb00896.x

### A4. Whittle (1973), *Some General Points in the Theory of Optimal Experimental Design*

**Result.** Direct proof/interpretation of the equivalence theorem for a **general concave criterion**; consequences for Wynn-type iterative algorithms; transformation characterization connected to `D_s`.  
**Use for us.** Best compact source before trying to generalize a quantizer theorem to arbitrary concave matrix criteria.  
**DOI:** https://doi.org/10.1111/j.2517-6161.1973.tb00944.x

### A5. Kiefer (1974), *General Equivalence Theory for Optimum Designs (Approximate Theory)*

**Result.** General `Phi`-optimal equivalence theory including D, L, E and other criteria, multiresponse settings, variable covariance/cost.  
**Use for us.** Prevents reinventing generic concave-criterion sensitivity theory.  
**DOI:** https://doi.org/10.1214/aos/1176342810

### A6. Fedorov (1972), *Theory of Optimal Experiments*

**Result/use.** Foundational treatment of continuous/discrete optimal designs and exchange construction. Fedorov exchange iteratively replaces design points to improve D-efficiency.  
**Use for us.** Rank updates, exchange-search architecture, optimal-design terminology.  
**Book:** https://books.google.com/books/about/Theory_of_Optimal_Experiments.html?id=v6vTAvqGny4C

### A7. Näther & Reinsch (1981), *D_s-optimality and Whittle's equivalence theorem*

**Result.** Equivalence theorem for `D_s` including singular cases via a suitable transformation; notes complexity of the nonlinear derivative and supplies a simpler sufficient condition.  
**Use for us.** Direct reference when deriving the profiled criterion's sensitivity/supergradient.  
**DOI:** https://doi.org/10.1080/02331888108801591

### A8. Pukelsheim, *Optimal Design of Experiments*

**Use.** Modern reference text for matrix criteria, general equivalence theorem, efficiency, and design geometry.  
**Chapter DOI:** https://doi.org/10.1137/1.9780898719109.ch7

### A9. Nguyen & Miller (1992), review of exchange algorithms for discrete D-optimal design

**Result.** Reviews and compares Fedorov-style exchange algorithms for exact/discrete D designs.  
**Use for us.** Implementation and historical terminology for exchange local search.  
**DOI:** https://doi.org/10.1016/0167-9473(92)90064-M

### A10. Huan, Jagalur & Marzouk (2024), *Optimal Experimental Design: Formulations and Computations*

**Use.** Up-to-date survey of OED formulations and computation; useful as a modern map of D, `D_A/D_s`, E and algorithms.  
**PDF:** https://www.cambridge.org/core/services/aop-cambridge-core/content/view/38BBD0DC1A0386FDF306B6C0167DF7D9/S0962492924000023a.pdf/optimal-experimental-design-formulations-and-computations.pdf

---

## B. Fisher-information quantization

### B1. Venkitasubramaniam, Tong & Swami (2006), *Score-Function Quantization for Distributed Estimation*

**Problem.** Finite quantization for distributed parameter estimation.  
**Core idea.** Design the quantizer in score-function space; scalar Fisher loss is tied directly to score distortion; Lloyd–Max style optimization follows.  
**Use for us.** The strongest reason never to claim “quantize the score to preserve Fisher information” as new.  
**DOI:** https://doi.org/10.1109/CISS.2006.286494  
**Public PDF mirror used in prior project review:** https://www.lehigh.edu/~pav309/papers/VenkTongSwami_Quant_06CISS.pdf

### B2. Venkitasubramaniam/Tong/Swami line on maximin ARE (mid-2000s)

**Result.** Robust deterministic scalar quantizers for distributed estimation can be designed by maximin asymptotic relative efficiency; score/sufficient-statistic threshold structure and iterative person-by-person design are developed for broad model classes.  
**Use for us.** Prior art for robust/local-parameter uncertainty and distributed quantizer optimization.

### B3. Farias & Brossier (2013/2014), *Optimal Scalar Quantization for Parameter Estimation* / journal version

**Result.** High-resolution Fisher-optimal scalar quantization; asymptotic information loss, optimal quantizer point density, and practical adaptive thresholds. Information loss decays rapidly with bit depth in the high-rate regime.  
**Use for us.** Mature scalar asymptotics; possible template for high-`K` asymptotics of multivariate information quantization.  
**PDF:** https://arxiv.org/pdf/1310.6945  
**Journal DOI:** https://doi.org/10.1109/TSP.2014.2318140

### B4. Barnes, Han & Özgür (2018), *A Geometric Characterization of Fisher Information from Quantized Samples...*

**Problem.** Vector parameter under finite-bit quantization.  
**Result.** Geometric characterization/bounds for the **trace** of the quantized Fisher information through conditional means of the score; applications to communication-constrained estimation. Includes geometric extremal results such as half-space structure in special one-bit Gaussian settings.  
**Use for us.** Closest published multivariate score-space geometry. Supplies the conditional-score centroid identity underlying trace/k-means.  
**Does not supply.** Full log-det hard-partition optimization or the finite D exchange theorem.  
**PDF:** https://web.stanford.edu/~aozgur/FisherAllerton.pdf  
**DOI:** https://doi.org/10.1109/ALLERTON.2018.8635899

### B5. Barnes, Han & Özgür (2020), communication-constrained lower bounds via FI

**Result.** Uses Fisher information of quantized data to derive lower bounds for distributed learning/estimation.  
**Use.** Information-budget perspective, not partition optimization.

### B6. Dülek (2023), *On the Optimality of Sufficient Statistics-Based Quantizers*

**Result.** For exponential families, there exists an optimal deterministic `K`-level quantizer maximizing **trace FIM** whose sufficient-statistic cells are convex polytopes. Extreme-point / convex analysis also links to likelihood-ratio tests.  
**Use for us.** Strong boundary marker: hard multivariate Fisher-optimal **polyhedral** quantizers are already known for trace.  
**DOI:** https://doi.org/10.1109/TPAMI.2022.3172282

### B7. Zhang, Blum, Kaplan & Lu (2018; preprint 2016), *A Fundamental Limitation on Maximum Parameter Dimension for Accurate Estimation With Quantized Data*

**Result.** Quantization can force the FIM to be singular when parameter dimension exceeds a quantization-induced identifiability bound.  
**Use for us.** Related to the ScoreQuant structural rank bound `rank(I_q) <= K-1`; worth checking for sharper general identifiability limits under structured quantizers.  
**PDF:** https://arxiv.org/pdf/1605.07679  
**Journal DOI:** https://doi.org/10.1109/TIT.2018.2850968

### B8. Domain-specific determinant-FIM quantizer design

**[LIT, adjacent]** Several sensor-network/localization papers optimize quantization thresholds or bit allocations using `det(FIM)` / log-det as the scalar objective. A recent explicit example is Jiang et al. (2026), which designs hybrid quantization thresholds for underwater target localization by maximizing the determinant of the localization FIM and solves the nonconvex threshold problem with a genetic algorithm.

**Why this matters.** It invalidates any broad novelty statement such as “using D-optimality to design a quantizer is new.”  
**Why it is still different.** The quantizers are model-specific threshold families at sensors, not unrestricted `K`-cell partitions of a multivariate score law with centroid information `sum m_bm_b^T/W_b`.

Jiang et al., *Direct target localization in USNs with hybrid quantized multi-snapshot measurements*, Digital Signal Processing 168 (2026), 105552. DOI: https://doi.org/10.1016/j.dsp.2025.105552

**[SEARCH-GAP]** In the targeted search, no paper was found that develops a general `D_s`-optimal hard quantizer-partition theory analogous to classical `D_s` experimental design.

---

## C. Determinant clustering / partition optimization

### C1. Friedman & Rubin (1967), *On Some Invariant Criteria for Grouping Data*

**Result/use.** Classical affine-invariant determinant-type criteria for multivariate grouping. Establishes that determinant partition objectives have a long history.  
**DOI:** https://doi.org/10.1080/01621459.1967.10500923

### C2. Scott & Symons (1971), *Clustering Methods Based on Likelihood Ratio Criteria*

**Result/use.** Likelihood-ratio clustering connected to within-cluster covariance/scatter determinants.  
**DOI/JSTOR:** https://doi.org/10.2307/2529003

### C3. Marriott (1971/1982)

Key historical works on practical determinant cluster criteria and optimization methods of cluster analysis. They are useful prior art for local exchange and covariance-adaptive clustering terminology.

### C4. Späth (1977), *Computational experiences with the exchange method...*

**Result.** Empirical study of exchange minimization for four partitioning criteria, with recommendations for initialization/criterion sequencing.  
**DOI:** https://doi.org/10.1016/S0377-2217(77)81005-9

### C5. Späth (1985), *Cluster Dissection and Analysis: Theory, FORTRAN Programs, Examples*

**Important software prior art.** The public FORTRAN reimplementation contains `DETEXM`, an exchange algorithm for the determinant criterion, generalized distances, scatter computation, LDL/Cholesky and update routines.  
**Code:** https://people.math.sc.edu/Burkardt/f_src/spaeth/spaeth.html

This is particularly important when positioning ScoreQuant's finite exchange **algorithm**. The likely novelty, if any, must lie in the retained-Fisher objective and its exact structure/theorems — not in “use one-point exchange with determinant updates.”

### C6. Coleman, Dong, Hardin, Rocke & Woodruff (1999), *Some computational issues in cluster analysis with no a priori metric*

**Result.** Under a homogeneous unrestricted Gaussian covariance model, classification likelihood leads to minimizing the determinant of pooled within-cluster scatter. The paper compares combinatorial first-improvement and steepest-ascent single-exchange algorithms and hierarchical/EM combinations.  
**Use for us.** Strong algorithmic/historical comparator; also affine-invariance perspective.  
**DOI:** https://doi.org/10.1016/S0167-9473(99)00009-2

---

## D. Vector quantization, Voronoi, consistency

### D1. Pollard (1981), *Strong Consistency of K-Means Clustering*

**Result.** Under suitable distribution/uniqueness conditions, empirical optimal `k`-means centers converge almost surely to the population optimum.  
**Use for us.** Canonical proof template for empirical-to-population consistency.  
**PDF:** https://www.stat.yale.edu/~pollard/Papers/Pollard81AS.pdf  
**DOI:** https://doi.org/10.1214/aos/1176345339

### D2. Du, Faber & Gunzburger (1999), *Centroidal Voronoi Tessellations: Applications and Algorithms*

**Result.** Mature framework for population centroidal Voronoi tessellations, Lloyd methods, applications including vector quantization.  
**Use for us.** Geometric language and variational methods.  
**DOI:** https://doi.org/10.1137/S0036144599352836

### D3. Du, Emelianenko & Ju (2006), Lloyd convergence for CVT

**Use.** Algorithm convergence proofs for an additive centroidal energy; useful as a contrast because adaptive-`I^{-1}` Lloyd for ScoreQuant `D` is not automatically ascent.  
**DOI:** https://doi.org/10.1137/040617364

### D4. Richter & Alexa (2015), *Mahalanobis centroidal Voronoi tessellations*

**Result.** Anisotropic CVT with a learned local Mahalanobis metric; under their normalized formulation the optimal metric relates to inverse covariance.  
**Use.** Very close geometric vocabulary, but objective is an additive shape-approximation/CVT energy, not retained Fisher determinant.  
**DOI:** https://doi.org/10.1016/j.cag.2014.09.009

### D5. Bregman Voronoi / Bregman quantization literature

**Use.** Generalizes centroidal Voronoi and gives existence/stationarity tools for non-Euclidean divergences. Recent high-rate work extends Zador-type quantization to Bregman divergences and even spatially varying SPD metric fields. This may be relevant to asymptotic local approximations of information-optimal quantization, but it remains an additive distortion theory.

---

## E. Inference-aware categorization / score learning

### E1. Brehmer, Louppe, Pavez & Cranmer (2020), local score / SALLY-SALLINO line

**Result/use.** Score-based local likelihood-free inference; demonstrates practical learned score representations and score-space density/histogram inference.  
**DOI:** https://doi.org/10.1073/pnas.1915980117

### E2. de Castro & Dorigo (2019), INFERNO

**Result.** Differentiable event-to-bin summaries optimized through an inference objective derived from a binned likelihood / expected parameter uncertainty, including nuisances.  
**PDF:** https://arxiv.org/pdf/1806.04743  
**DOI:** https://doi.org/10.1016/j.cpc.2019.06.007

### E3. Matchev & Shyamsundar (2021), ThickBrick

**Result.** Iterative event selection/categorization for HEP significance with Lloyd-like structure.  
**Use.** Adjacent category-optimization prior art, not retained-FIM score quantization.

### E4. Erdmann, Kasaraguppe & Mausolf (2026), *Learning to bin*

**Result/use.** Modern multidimensional differentiable/Bayesian bin optimization, including annealed soft-to-hard categories.  
**Use.** Important comparator for optimization architecture; different objective/representation.

---

# 5. What transfers from optimal design — and what does not

| Classical design fact/tool | Safe transfer to quantizer research? | Comment |
|---|---|---|
| `D`: gradient `M^{-1}` | **Yes** | Matrix calculus is identical. |
| `D_s`: Schur complement / efficient information | **Yes** | Criterion algebra transfers. |
| `E`: minimum-eigenspace supergradients | **Yes** | Nonsmooth matrix calculus transfers. |
| General directional-derivative reasoning | **Yes** | Gives quantizer first variation after deriving `dI` for cell mass movement. |
| Kiefer–Wolfowitz sensitivity theorem itself | **No, not directly** | Feasible sets differ; design information is additive in design measure. |
| Fedorov exchange formulas | **Only as analogy/tooling** | A design-point replacement is not a label relocation; rank structure differs. |
| Submodularity of log-det subset selection | **Generally no** | Quantizer cell centroids couple many points; objective is not a simple sum of fixed rank-one terms. |
| Equivalence theorem as a global optimality certificate | **Open analogue** | Could inspire a population partition certificate, but requires a new feasible-direction argument. |
| D/A/E efficiencies | **Potentially useful** | Need define against full-information or population optimum carefully. |

---

# 6. False friends and terminology traps for an LLM

1. **“D-optimal quantization” is not automatically ScoreQuant.** There are threshold/bit-allocation papers maximizing determinant of a FIM.
2. **“Determinant clustering” is not the same objective.** Most old clustering work minimizes determinant of within-scatter or likelihood covariance.
3. **Trace FI quantization is not full-matrix D.** Trace is additive after whitening and reduces to `k`-means; log-det couples directions globally.
4. **A Lloyd fixed point is not an exact exchange local optimum.** For ScoreQuant D, adaptive metric Lloyd is not justified by the usual `k`-means monotonicity argument.
5. **Population stationarity is not finite exchange stability.** The project has a special D theorem bridging them; this bridge fails for `D_s` and E in general.
6. **D_s is not just D on the POI block.** Nuisance profiling requires a Schur complement / efficient-score construction.
7. **E-optimality is nonsmooth.** When the minimum eigenvalue is repeated, there is no unique gradient.
8. **Hard partition vs randomized/soft quantizer.** They have different feasible sets; purification removes randomization only under appropriate atomlessness and finite-moment/action conditions.
9. **Finite label optimization vs deployable quantizer.** A labeling of training points is not by itself a function for future scores.
10. **Estimated score vs exact Fisher problem.** Classifier/density-ratio scores introduce score-estimation error in addition to quantization error.

---

# 7. Project theorem ledger (keep separate from prior art)

The following is the current ScoreQuant research state and should be treated as **unpublished project content unless a source is later found**.

## T-P1. Retained information and first variation

- `I_q=sum_b m_bm_b^T/W_b`.
- infinitesimal mass transfer gives difference of two centered rank-one forms.
- for differentiable concave matrix criterion `F`, assignment stationarity is a common `G=nabla F(I_q)` quadratic rule.

**Status:** identity is literature-backed; general quantizer first-variation packaging is project synthesis/derivation.

## T-P2. Full D exact finite relocation

- exact rank-two `Delta I`;
- closed 2x2 determinant-ratio gain;
- fast inverse/Cholesky updates.

**Status:** project-derived; closest prior art is determinant clustering and design exchange, not same objective.

## T-P3. Full D exchange-stability => strict self-consistent Voronoi

**Status:** project-derived and important. Highest priority for independent proof audit and specialist prior-art search.

## T-P4. D monotone finite solver

Strict positive-gain one-point exchange terminates at an exchange-stable state; via T-P3 it has canonical self-consistent Mahalanobis extension.

**Status:** finite termination is elementary once exact gains are accepted; geometric conclusion relies on T-P3.

## T-P5. D global-search geometry

Self-consistent affine/Voronoi realizability implies an exact arrangement-enumeration route `N^{O(Kd)}` for fixed `d,K`; branch-and-bound uses refinement upper bounds.

**Status:** project-derived; compare carefully with Inaba/Katoh/Imai-style fixed-dimensional clustering enumeration before novelty claims.

## T-P6. Population purification

For atomless score laws, Dvoretzky–Wald–Wolfowitz-type purification can preserve the finite collection of cell probability and first-moment integrals, so randomized and deterministic quantizers have the same attainable `(W_b,m_b)` statistics.

**Status:** bridge from a classical purification theorem; exact assumptions should always be stated.

## T-P7. Profiled D_s finite nonclosure

Globally optimal finite assignments can violate their own first-order efficient-metric assignment rule.

**Status:** project counterexample; retain explicit smallest counterexample in the repository.

## T-P8. D_s asymptotic geometric bound

For balanced finite cells, exchange-stability violation of the first-order geometry is `O(K/N)`.

**Status:** project-derived; proof assumptions/constants need a theorem card in the registry.

## T-P9. Efficient-score upper problem for D_s

Full-D quantization of the full-data efficient score upper-bounds attainable profiled information in the original quantized problem.

**Status:** project-derived; likely connected to data processing / efficient score projection theory and deserves a targeted prior-art search.

## T-P10. E finite nonclosure and common-supergradient question

Finite E-optima need not obey a naive fixed first-order metric rule; repeated minimum eigenvalues produce nonuniqueness. Population existence of one common supporting minimum-eigenspace supergradient remains open.

---

# 8. Open-problem cards for theorem agents

## O1. Characterize criteria with finite exchange => stationary geometry

**Statement.** Characterize concave spectral/matrix criteria `F` such that every one-point-exchange-stable finite partition satisfies the first-order cell assignment rule induced by `G=nabla F(I)` (or a supergradient).

**Known anchor.** Full `log det` currently has a project proof; A and `D_s` have counterexamples; E is nonsmooth and also fails naively.

**Why hard.** Exact move has positive and negative rank-one components; first-order sign need not control finite gain for a generic concave criterion.

**Suggested proof route.** Derive the exact two-vector finite difference for a general spectral `F`; ask what curvature/operator-monotonicity inequality is required to preserve the sign. Search for self-concordance / matrix monotone / determinant-specific inequalities.

**Suggested falsification.** Exhaustive enumerate `N<=8`, `d<=3`, `K<=4` with rational/small integer scores for candidate criteria.

**High value:** very high.

## O2. D_s asymptotic bridge

**Statement.** Under atomless score law, regularity, balanced cell masses, and suitable uniqueness/separation assumptions, do empirical global or exchange-stable `D_s` solutions converge to population efficient-metric stationary quantizers?

**Known anchor.** Project `O(K/N)` violation bound; Pollard-style consistency templates; general M-estimation/ERM.

**Potential route.** Uniform law of large numbers for cell moment functionals over a controlled geometric partition class + compactness + stability margin converting approximate inequalities into exact population inequalities.

**Risk.** Unrestricted partitions have high complexity; vanishing cells and nuisance-block near-singularity can destroy uniformity.

## O3. Population consistency for full D

**Statement.** Establish consistency of empirical global D-optimal hard quantizers for the unrestricted population problem, or for progressively richer affine/Voronoi families.

**Nearest literature.** Pollard `k`-means consistency; M-estimator/empirical process theory; consistency of generalized clustering.

**Key obstacles.** log-det singularity near rank loss; nonadditive cell-moment functional; label/partition nonuniqueness.

**Potential simplification.** First prove for a compact parameterization of affine max-partitions with minimum cell mass and `lambda_min(I)>=epsilon`.

## O4. E common-supergradient geometry

**Statement.** At a population E-optimal hard quantizer, does there always exist a single `G` in the superdifferential of `lambda_min(I_q)` such that almost every score is assigned to a nearest centroid under `G`?

**Nearest literature.** General equivalence theory for E; extremal-polynomial characterization with convex combinations of minimum-eigenspace projectors.

**Potential proof.** Formulate partition perturbations as a convex cone of achievable `dI`; apply separation/minimax to interchange “for every feasible direction exists a supergradient” with “exists one supergradient for every direction.”

**Risk.** The interchange may fail because the feasible-direction cone is nonconvex before relaxation; counterexample search should precede a long proof attempt.

## O5. Soft-to-hard limit

**Statement.** When do stationary points/optima of temperature-softened randomized quantizers converge, as `T->0`, to stationary/optimal hard partitions?

**Tools.** Gamma-convergence/epi-convergence; entropic regularization; compactness of assignment probabilities; purification.

**Failure modes.** Ties, vanishing cells, singular information, local stationary branches that disappear in the zero-temperature limit.

## O6. Atomic score laws and randomization gap

**Statement.** Characterize when splitting an atom among labels can improve D / `D_s` / E versus every deterministic score quantizer.

**Known anchor.** Atomless DWW purification removes the gap by preserving relevant integrals. Atoms invalidate this direct argument.

**Suggested approach.** Reduce a finite-atom law to a finite-dimensional assignment polytope. Study extreme points and concavity of criterion in attainable `(W,m)` variables; search for minimal counterexamples.

## O7. Parameterized complexity

**Statement.** Determine hardness/FPT status as `K` or `d` varies. Is D-optimal score partitioning NP-hard for fixed `d=2` and growing `K`? For `K=d+1` and growing `d`? Is the current `N^{O(Kd)}` arrangement enumeration essentially tight?

**Nearest literature.** Euclidean k-means fixed-dimensional complexity; Voronoi-realizability enumeration; D-optimal subset selection is NP-hard, but that reduction does not automatically transfer.

**Agent caution.** Do not cite NP-hardness of D-optimal *design-point selection* as proof of partition hardness.

## O8. High-rate / large-K asymptotics

**Statement.** Is there a Zador/Gersho-style asymptotic theory for information loss `I_full-I_q` under D / `D_s` / E criteria as `K->infinity`?

**Nearest literature.** Farias–Brossier scalar Fisher high-resolution theory; Zador quantization; Bregman/asymmetric local metric quantization.

**Potential route.** For small cells, expand within-cell score covariance and log-det loss:

\[
\log\det I_q
=\log\det(I_{full}-L)
\approx \log\det I_{full}-\operatorname{tr}(I_{full}^{-1}L)-\tfrac12\operatorname{tr}[(I_{full}^{-1}L)^2]-\cdots.
\]

The leading term reduces to Fisher-whitened quadratic distortion, suggesting ordinary high-rate quantization may control the first asymptotic order, with D-specific effects entering at higher order. This is a promising theorem direction.

## O9. Stronger finite neighborhoods

**Statement.** Analyze two-point swaps, merge-split moves, or cell-boundary perturbations. Can stronger local stability imply approximation guarantees or stronger geometry?

**Nearest literature.** Hartigan local search; determinant clustering exchange; local-search approximation theory for clustering/design selection.

## O10. Robustness to estimated scores / density ratios

**Statement.** Given `||s_hat-s||` control in `L2` or uniform norm, bound errors in optimized cell moments, `I_q`, criterion value, and learned boundaries.

**Potential tools.** Matrix perturbation (Weyl, Davis–Kahan, log-det Lipschitz on `I >= epsilon I`), stability of argmax partitions under margin conditions, empirical-process bounds.

---

# 9. Software / implementation landscape

## 9.1 Directly relevant historical code

### Späth FORTRAN cluster-analysis implementation

- public FORTRAN90 source;
- contains `DETEXM` determinant-criterion exchange;
- contains scatter, generalized-distance, LDL/Cholesky and update routines.

**URL:** https://people.math.sc.edu/Burkardt/f_src/spaeth/spaeth.html

**Use for ScoreQuant:** inspect algorithmic details and nomenclature before claiming exchange-update novelty.

## 9.2 Optimal experimental design packages (adjacent, useful for algorithm ideas)

### PyOptEx

Modern Python package for optimal experiment design; designed to let researchers define custom metrics and optimization algorithms. Useful as an architecture reference, but optimizes experimental designs, not event partitions.

**Docs:** https://pyoptex.readthedocs.io/

### PyDOE optimal-design functions

Provides D/A/E/G/etc criteria and Wynn/Mitchell, Fedorov, modified Fedorov, DETMAX-style search. Again, candidate experimental design rather than quantization.

**Docs:** https://pydoe.github.io/pydoe/

### `optdesign`

Minimal Python implementation of linear D-optimal design / MaxVol algorithms; useful for readable reference implementations.

**PyPI:** https://pypi.org/project/optdesign/

### BASF DoE / BoFire lineage

Python D-optimal design tooling over constrained experimental spaces. The standalone `doe` repository is now superseded by BoFire.

**Docs:** https://basf.github.io/doe

### OApackage

Includes coordinate-exchange optimization combining D-efficiency, `D_s`-efficiency and related criteria for orthogonal-array/design construction.

**Docs:** https://oapackage.readthedocs.io/en/latest/generation.html

## 9.3 What appears absent

**[SEARCH-GAP]** No established public package was located whose primary abstraction is:

> multivariate score law + hard `K`-cell partition + full retained-FIM D / profiled `D_s` / E objective + deployable quantizer + exact finite relocation.

This is a useful software niche even if some mathematical components prove non-novel.

---

# 10. Recommended LLM research workflow

A single long literature document is useful, but **not sufficient** for theorem work. The best setup is a two-layer research memory:

1. **this dossier** — human/LLM-readable field map and conceptual guardrails;
2. **a machine-readable claim registry** — one record per theorem/claim/counterexample, with assumptions, provenance, dependencies and falsification tests.

## 10.1 Every claim card should contain

- stable ID (`D-FINITE-EXCHANGE-01`);
- exact mathematical statement;
- object level: finite / inductive empirical / population;
- criterion: trace / D / `D_s` / E / A;
- assumptions;
- status: literature / project proved / numerically supported / conjecture / disproved;
- source or proof file;
- dependencies;
- known counterexamples;
- smallest numerical test instance;
- proof obligations still unchecked;
- transfer risks (which classical theorem looks similar but is not applicable).

A JSON companion is generated next to this document for this purpose.

## 10.2 Agent protocol for a new theorem

**Phase A — normalize.** Restate the theorem with all quantifiers, domain (finite/population), positivity and nonempty-cell assumptions.

**Phase B — nearest known theorem.** Query the claim registry and bibliography. Explicitly list the 3 closest results and *why each does not already prove the target*.

**Phase C — falsify first.** Before a long proof, brute-force small rational/integer examples. For spectral criteria search degeneracies and near-singular matrices deliberately.

**Phase D — symbolic skeleton.** Reduce the statement to a minimal set of matrix inequalities. Use symbolic algebra only for identities, not as evidence for inequality truth.

**Phase E — proof attempt.** Keep lemmas modular. Every imported theorem must have assumptions checked against the quantizer feasible set.

**Phase F — adversarial audit.** A separate agent tries to break the proof, search prior art under alternate terminology, and construct counterexamples.

**Phase G — registry update.** Store theorem, proof/counterexample, and exact provenance so later agents do not redo the work.

## 10.3 Separate agents by role

A practical multi-agent loop:

- **Literature agent:** finds exact theorem statements and PDFs; never proves new claims.
- **Theorem agent:** works only from a frozen claim registry + selected papers.
- **Counterexample agent:** enumerates/samples small instances and attacks assumptions.
- **Proof auditor:** checks every algebraic transition and imported assumption.
- **Integrator:** updates manuscript and registry only after the auditor passes the result.

This separation is valuable because LLMs otherwise tend to turn a plausible analogy (“this looks like Kiefer–Wolfowitz”) into an unjustified transfer.

## 10.4 Keep a counterexample bank

For each criterion keep serialized smallest examples of:

- Lloyd decreases the true objective;
- Voronoi fixed but not exchange-stable (D);
- globally optimal but first-order-rule violating (`D_s`, E);
- any A-optimal counterexample;
- atomic-law randomization gap if found;
- singular/nuisance-degenerate failure cases.

The theorem agent should run these tests automatically after every proposed generalization.

## 10.5 Keep exact papers locally

For high-value sources, store the PDF plus a short `paper_card.md` containing:

- theorem numbers/pages;
- exact assumptions;
- notation translation into ScoreQuant notation;
- reusable lemmas;
- “not proved here” list.

For theorem work, this is better than relying on web-search snippets or a generic semantic index.

---

# 11. Suggested reading order for a theorem agent

1. **Kiefer & Wolfowitz (1960)** — understand D sensitivity/equivalence.
2. **Wynn (1970, 1972)** — sequential algorithms and D_s extension.
3. **Whittle (1973)** — general concave criterion and transformation viewpoint.
4. **Kiefer (1974)** — general equivalence theory including E.
5. **Näther & Reinsch (1981)** — D_s singular/equivalence subtleties.
6. **Venkitasubramaniam et al. (2006)** — score-function Fisher quantization.
7. **Farias & Brossier (2013/14)** — high-rate scalar Fisher quantization.
8. **Barnes, Han & Özgür (2018)** — vector score/Fisher geometry.
9. **Dülek (2023)** — trace-Fisher polytopal hard quantizers.
10. **Friedman–Rubin / Scott–Symons / Späth / Coleman et al.** — determinant partitioning and exchange prior art.
11. **Pollard + Du/Faber/Gunzburger** — population consistency/CVT proof templates.
12. **Current ScoreQuant theorem registry** — only then attack D / D_s / E open claims.

---

# 12. Conservative novelty boundary after the extended search

### Clearly known

- Fisher-information-optimal finite quantization.
- score-function quantization.
- scalar FI-loss/score-distortion equivalence and Lloyd–Max design.
- multivariate conditional-score representation of quantized FIM trace.
- hard convex-polytopal trace-FI quantizers in exponential families.
- D / `D_s` / E optimality and sensitivity/equivalence theory in experimental design.
- determinant-based partition/clustering objectives.
- single-point exchange and determinant/scatter matrix update algorithms in clustering.
- model-specific quantizer-threshold design using determinant of a Fisher matrix.
- differentiable inference-aware categories and soft-to-hard bin learning.

### Strong synthesis, but not safe as standalone novelty

- Fisher-whitened multivariate score `k`-means exactly optimizes normalized retained trace.
- using efficient scores to interpret `D_s` stationarity.
- viewing general differentiable Fisher criteria as common-quadratic first-order score partitions.

### Still not found as direct prior art

- unrestricted multivariate **score-space hard partitions** optimized by the determinant of retained between-cell Fisher information, with the exact finite relocation algebra stated in the ScoreQuant form;
- a theorem that **one-point D-exchange stability forces self-consistent `I_q^{-1}` Voronoi geometry**;
- the same finite/population bridge plus exact finite/global algorithms for this retained-Fisher objective;
- a general hard-partition theory for profiled `D_s` analogous to the above;
- a unified public library with D / `D_s` / E score-space hard quantization as its central abstraction.

These remain **[SEARCH-GAP]**, not “first ever” claims.

---

# 13. Bibliographic shortlist

1. J. Kiefer and J. Wolfowitz. *The Equivalence of Two Extremum Problems*. Canadian Journal of Mathematics 12, 363–366 (1960). DOI: 10.4153/CJM-1960-030-4.
2. H. P. Wynn. *The Sequential Generation of D-Optimum Experimental Designs*. Ann. Math. Stat. 41(5), 1655–1664 (1970). DOI: 10.1214/aoms/1177696809.
3. H. P. Wynn. *Results in the Theory and Construction of D-Optimum Experimental Designs*. JRSS B 34(2), 133–147 (1972). DOI: 10.1111/j.2517-6161.1972.tb00896.x.
4. P. Whittle. *Some General Points in the Theory of Optimal Experimental Design*. JRSS B 35(1), 123–130 (1973). DOI: 10.1111/j.2517-6161.1973.tb00944.x.
5. J. Kiefer. *General Equivalence Theory for Optimum Designs (Approximate Theory)*. Annals of Statistics 2(5), 849–879 (1974). DOI: 10.1214/aos/1176342810.
6. V. V. Fedorov. *Theory of Optimal Experiments*. Academic Press (1972).
7. W. Näther and V. Reinsch. *D_s-optimality and Whittle's equivalence theorem*. Series Statistics 12(3), 307–316 (1981). DOI: 10.1080/02331888108801591.
8. F. Pukelsheim. *Optimal Design of Experiments*. SIAM.
9. N.-K. Nguyen and A. J. Miller. *A review of some exchange algorithms for constructing discrete D-optimal designs*. CSDA 14(4), 489–498 (1992). DOI: 10.1016/0167-9473(92)90064-M.
10. P. Venkitasubramaniam, L. Tong, A. Swami. *Score-Function Quantization for Distributed Estimation*. CISS (2006). DOI: 10.1109/CISS.2006.286494.
11. R. C. Farias and J.-M. Brossier. *Optimal Scalar Quantization for Parameter Estimation*. arXiv:1310.6945; journal version TSP (2014), DOI: 10.1109/TSP.2014.2318140.
12. L. P. Barnes, Y. Han, A. Özgür. *A Geometric Characterization of Fisher Information from Quantized Samples with Applications to Distributed Statistical Estimation*. Allerton (2018), 16–23. DOI: 10.1109/ALLERTON.2018.8635899.
13. B. Dülek. *On the Optimality of Sufficient Statistics-Based Quantizers*. IEEE TPAMI 45(3), 3567–3573 (2023). DOI: 10.1109/TPAMI.2022.3172282.
14. H. P. Friedman and J. Rubin. *On Some Invariant Criteria for Grouping Data*. JASA 62(320), 1159–1178 (1967). DOI: 10.1080/01621459.1967.10500923.
15. A. J. Scott and M. J. Symons. *Clustering Methods Based on Likelihood Ratio Criteria*. Biometrics 27(2), 387–397 (1971). DOI: 10.2307/2529003.
16. H. Späth. *Computational experiences with the exchange method: Applied to four commonly used partitioning cluster analysis criteria*. EJOR 1(1), 23–31 (1977). DOI: 10.1016/S0377-2217(77)81005-9.
17. H. Späth. *Cluster Dissection and Analysis: Theory, FORTRAN Programs, Examples*. Ellis Horwood (1985).
18. D. Coleman, X. Dong, J. Hardin, D. M. Rocke, D. L. Woodruff. *Some computational issues in cluster analysis with no a priori metric*. CSDA 31(1), 1–11 (1999). DOI: 10.1016/S0167-9473(99)00009-2.
19. D. Pollard. *Strong Consistency of K-Means Clustering*. Annals of Statistics 9(1), 135–140 (1981). DOI: 10.1214/aos/1176345339.
20. Q. Du, V. Faber, M. Gunzburger. *Centroidal Voronoi Tessellations: Applications and Algorithms*. SIAM Review 41(4), 637–676 (1999). DOI: 10.1137/S0036144599352836.
21. Q. Du, M. Emelianenko, L. Ju. *Convergence of the Lloyd Algorithm for Computing Centroidal Voronoi Tessellations*. SIAM J. Numer. Anal. 44(1), 102–119 (2006). DOI: 10.1137/040617364.
22. R. Richter and M. Alexa. *Mahalanobis centroidal Voronoi tessellations*. Computers & Graphics 46, 48–54 (2015). DOI: 10.1016/j.cag.2014.09.009.
23. J. Brehmer, G. Louppe, J. Pavez, K. Cranmer. *Mining gold from implicit models to improve likelihood-free inference*. PNAS 117(10), 5242–5249 (2020). DOI: 10.1073/pnas.1915980117.
24. P. de Castro and T. Dorigo. *INFERNO: Inference-Aware Neural Optimisation*. CPC 244, 170–179 (2019). DOI: 10.1016/j.cpc.2019.06.007.
25. K. T. Matchev and P. Shyamsundar. *Optimal event selection and categorization in high energy physics. Part I. Signal discovery*. JHEP 03, 291 (2021).
26. Chunjin Jiang et al. *Direct target localization in USNs with hybrid quantized multi-snapshot measurements: A geometric structure-aided approach*. Digital Signal Processing 168, 105552 (2026). DOI: 10.1016/j.dsp.2025.105552.
27. X. Huan, J. Jagalur, Y. M. Marzouk. *Optimal Experimental Design: Formulations and Computations*. Acta Numerica / survey (2024). Public Cambridge PDF linked above.

---

## Final research note

The central scientific opportunity is narrower — and stronger — than “Fisher-optimal binning.” The established literature already contains Fisher-optimal quantizers, trace geometry, D/D_s/E design theory, determinant clustering, exchange algorithms and inference-aware bins. The distinctive mathematical object worth pursuing is the **nonadditive between-cell score-information functional** together with the exact geometry induced by full log-det and the ways in which that geometry breaks or weakens under profiling (`D_s`) and spectral worst-direction (`E`) criteria.

For theorem work, maintain the distinction between **published general matrix-optimality theory** and **new feasible-set geometry created by hard partitions**. That distinction is where the open questions live.
