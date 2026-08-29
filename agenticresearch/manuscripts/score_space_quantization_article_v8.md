<div class="layout">

<div role="main">

<div>

<div class="kicker">

Research manuscript draft · August 2026

</div>

# Information-optimal hard quantization of multivariate score space

<div class="subtitle">

Finite-sample assignment, deployable quantizers, population geometry, and exact optimization under D, profiled \\D_s\\, and E criteria

</div>

<div class="meta">

<span class="tag">Fisher information</span><span class="tag">score-space quantization</span><span class="tag">hard binning</span><span class="tag">D-optimality</span><span class="tag">profiled \\D_s\\</span><span class="tag">E-optimality</span>

</div>

</div>

<div class="section abstract">

## Abstract

Let \\X\sim P\_\theta\\ be a regular parametric model and let \\S=s(X)\in\mathbb R^d\\ denote the score at a reference parameter. We study compression of \\S\\ into \\K\\ hard labels while preserving matrix-valued Fisher information. The retained information is the between-cell score scatter, \\I_q=\operatorname{Var}(\mathbb E\[S\mid q(S)\])\\. A central distinction is made between three problems that are often conflated: unrestricted assignment of a finite observed sample, empirical fitting of an inductive quantizer that assigns future scores, and population quantizer design under the score law. For full D-optimality we derive an exact rank-two finite relocation identity and a closed determinant gain. A leverage inequality then yields a strong finite theorem: every one-point-exchange-stable positive-definite partition is already a strict self-consistent \\I_q^{-1}\\-Mahalanobis Voronoi partition. Thus a terminal finite D solution has a canonical extension to unseen score vectors. The corresponding implication fails for profiled \\D_s\\ and E criteria: exhaustive finite examples show globally optimal sample assignments that violate their own first-order geometric rule. For \\D_s\\, however, the violation of an exchange-stable state is quantitatively \\O(K/N)\\ under balanced sampling, and the profiled information is upper-bounded by D-optimal quantization of the full-data efficient score. For E-optimality, repeated minimum eigenvalues make one-point first-order geometry intrinsically non-identifying. We also formulate differentiable randomized quantizers, derive their exact assignment gradient, and clarify what gradient methods can and cannot guarantee. Finally, we show that full probability densities are not required for model access: the local score is the parameter derivative of a log density ratio, and in linear component models ratios of component densities to a single reference component suffice exactly. Analytic ratio functions, direct density-ratio estimators, and calibrated classifiers therefore form interchangeable upstream routes to score-space quantization. Estimated ratios are treated explicitly as model-access approximations: they recover the exact Fisher problem only when they recover the true local score.

</div>

<div class="status-grid">

<div class="status-card">

**Finite D theory**Exact rank-two move, determinant gain, monotone exchange, exchange-stability ⇒ self-consistent Mahalanobis geometry.

</div>

<div class="status-card">

**Inductive quantization**Explicit score-space predictors; affine/common-metric parameterizations; empirical and population objectives kept distinct.

</div>

<div class="status-card">

**Profiled and spectral criteria**Efficient-score \\D_s\\ geometry and bounds; E subgradient geometry, finite counterexamples, and nonsmooth degeneracy.

</div>

<div class="status-card">

**Model access**Finite scores; exact, autodiff, or classifier-estimated score maps; population samplers; direct moment/integration oracles.

</div>

</div>

<div id="intro" class="section">

## 1. Introduction

Many statistical pipelines ultimately replace a high-dimensional observation by a small categorical symbol: a histogram bin, event category, transmitted codeword, or discrete decision state. At a fixed reference parameter, local inferential content is summarized by the score. This motivates a direct design problem: partition multivariate score space into a small number of cells so that the resulting discrete label retains as much Fisher information as possible.

The problem is related to score-function quantization in distributed estimation [\[1\]](#ref-1), the geometric representation of Fisher information after quantization [\[3\]](#ref-3), sufficient-statistic quantization [\[4\]](#ref-4), determinant clustering [\[5\]](#ref-5)[\[6\]](#ref-6), vector quantization, and inference-aware learned categorization [\[17\]](#ref-17)[\[18\]](#ref-18)[\[19\]](#ref-19)[\[20\]](#ref-20). Yet the matrix criterion changes the optimization structure. Fisher-normalized trace reduces after whitening to weighted \\k\\-means, whereas D-optimality depends on the determinant of the entire retained information matrix and therefore couples all directions through a partition-dependent metric.

A second issue is equally important and more practical. Optimizing labels for the observations already present in memory is not the same task as learning a function that can assign the next observation. A finite labeling underdetermines its extension outside the observed score vectors. Conversely, a deployable quantizer is a function on score space and is therefore a statistical estimator learned from finite data. The distinction is immaterial for some classical quantizers because their optimization is posed directly over centers or boundaries; it becomes explicit when exact label-exchange methods are introduced.

<div class="result">

<div class="box-title">

Central structural distinction

</div>

This manuscript treats **finite assignment optimization** and **score-space quantizer design** as two legitimate but different computational tasks. For D-optimality a finite exchange theorem connects them: every terminal exchange-stable state admits a canonical self-consistent Mahalanobis predictor. For profiled \\D_s\\ and E, no such exact finite bridge exists in general, so a sample optimum and an inductive geometric optimum must remain distinct objects.

</div>

</div>

<div id="related" class="section">

## 2. Related work and positioning

### 2.1 Fisher-information quantization

Score-function quantizers were studied explicitly for distributed parameter estimation by Venkitasubramaniam, Tong, and Swami [\[1\]](#ref-1). Farias and Brossier analyzed Fisher-information-optimal scalar quantization for parameter estimation [\[2\]](#ref-2). Barnes, Han, and Özgür showed that the Fisher information of a quantized observation can be expressed geometrically through conditional score means and developed trace bounds for multivariate models [\[3\]](#ref-3). Dülek proved convex-polytopal sufficient-statistic quantizers for trace Fisher information in exponential families [\[4\]](#ref-4). These results establish the score representation and much of the trace geometry; the present focus is the nonlinear full-matrix criteria and exact finite relocation structure.

### 2.2 Determinant clustering, exchange methods, and Voronoi structure

Determinant-based clustering criteria date at least to Friedman and Rubin [\[5\]](#ref-5) and Scott and Symons [\[6\]](#ref-6). That literature primarily concerns determinants of within-cluster scatter or likelihood-ratio variants. In dimensions above one, minimizing \\\det W\\ is not equivalent to maximizing \\\det B\\ even when \\T=W+B\\ is fixed. Exact point-relocation methods have a long history in clustering, notably Hartigan-type local search; Telgarsky and Vattani analyzed the relation between Hartigan and Lloyd fixed points for \\k\\-means [\[8\]](#ref-8). Inaba, Katoh, and Imai used Voronoi realizability and arrangement enumeration to obtain fixed-parameter exact clustering algorithms [\[9\]](#ref-9). The finite D theorem below has a similar logical flavor but uses a determinant-specific leverage identity.

### 2.3 Population quantization and consistency

Centroidal Voronoi tessellations provide the classical population picture for squared-error vector quantization and a mature theory of Lloyd-type algorithms [\[13\]](#ref-13)[\[14\]](#ref-14). Pollard's strong consistency theorem for \\k\\-means is the canonical empirical-to-population template [\[12\]](#ref-12). These works are important comparators for the inductive problem, but their objective is additive squared distortion rather than a matrix information criterion. The general equivalence theory of optimal experimental design provides the relevant convex-analytic language for D, \\D_s\\, and E criteria, including nondifferentiable E-optimality [\[15\]](#ref-15) and classical \\D_s\\ equivalence results [\[16\]](#ref-16).

### 2.4 Density-ratio estimation, learned scores, and differentiable categorization

Density-ratio estimation is a mature alternative to separate density estimation. Direct methods estimate \(p_1(x)/p_0(x)\) from samples without constructing either density, including KLIEP- and least-squares-based approaches summarized by Sugiyama, Suzuki, and Kanamori [[22]](#ref-22). Probabilistic classification provides another route: calibrated posterior odds recover the same density ratio up to known class-prior odds [[21]](#ref-21). Local score estimation follows by differentiating or finite-differencing such ratios; score-based local likelihood-free inference develops this idea further [[17]](#ref-17).

This literature implies an important model-access principle for the present problem: a score-space quantizer does not need full component PDFs when the required local density ratios are available. A classifier is one estimator of those ratios, not a privileged part of the quantization method.

Modern inference-aware methods also learn summaries or categories by differentiating through an inference objective. Examples include INFERNO [[18]](#ref-18), iterative event categorization [[19]](#ref-19), and recent differentiable multidimensional bin optimization [[20]](#ref-20). Neither density-ratio estimation nor differentiable binning is claimed as a contribution here. The contribution is the information-quantization problem and its exact finite and population structure once an exact or estimated score representation has been supplied.

</div>

<div id="formulation" class="section">

## 3. Statistical formulation

### 3.1 Observation space, score space, and the push-forward law

Let \\(\mathcal X,\mathcal A)\\ be the observation space and let \\P\_\theta\\ be a regular parametric model with \\\theta\in\mathbb R^d\\. At a fixed reference point \\\theta_0\\, define \\ S=s(X)=\nabla\_\theta\log p(X\mid\theta)\big\|\_{\theta_0},\qquad \mathbb E\[S\]=0,\qquad I\_\mathrm{full}=\mathbb E\[SS^\top\]\succ0. \\ The decision rule considered here is a hard quantizer of score space, \\ q:\mathbb R^d\to\\1,\ldots,K\\,\qquad Z=q(S), \\ and the corresponding observation-space compressor is simply \\Q(x)=q(s(x))\\. Therefore two observations with the same score receive the same label. The optimization depends on the original statistical model only through the push-forward score law \\ P_S=s\_\\P\_{\theta_0}. \\ This is important computationally: the score law may be represented by a finite table, generated from an observation-space simulator, sampled directly in score space, or integrated analytically.

<div class="diagram">

![](figures/fig-01-score-quantization-pipeline.svg)

</div>

### 3.2 Fisher information retained by a hard label

For cell \\b\\, define \\ W_b=P(q(S)=b),\qquad m_b=\mathbb E\[S\\1\_\\q(S)=b\\\],\qquad \mu_b=\frac{m_b}{W_b}. \\ The score of the discrete label equals its conditional mean score [\[3\]](#ref-3), hence \\ \boxed{I_q=\sum\_{b=1}^K W_b\mu_b\mu_b^\top=\sum\_{b=1}^K\frac{m_bm_b^\top}{W_b}=\operatorname{Var}(\mathbb E\[S\mid Z\]).} \tag{1} \\ The law of total covariance gives \\ I\_\mathrm{full}=I_q+\mathbb E\[\operatorname{Cov}(S\mid Z)\],\qquad I_q\preceq I\_\mathrm{full}. \tag{2} \\ Thus all criteria in this paper depend on a quantizer only through the finite collection of cell probabilities and score first moments \\(W_b,m_b)\\.

### 3.3 Three optimization problems

<div class="mode-grid">

<div class="mode-card">

#### A. Population quantizer design

Optimize a measurable \\q\\ under \\P_S\\: \\\sup_q F(I_P(q))\\. The result is inherently a rule for future scores.

</div>

<div class="mode-card">

#### B. Empirical inductive fitting

Choose \\q\_\eta\\ in an explicit function class \\\mathcal Q\\ and maximize \\F(I\_{P_n}(q\_\eta))\\. The result carries a prediction rule and can be validated on new samples.

</div>

<div class="mode-card">

#### C. Finite assignment optimization

Optimize arbitrary labels \\z_1,\ldots,z_N\\ of a given weighted score table. The result is a transductive partition; it does not specify a unique extension away from the observed rows.

</div>

</div>

These problems need not have the same finite optimum. Problem C is a legitimate objective in its own right—for example when the final dataset is fixed and only its categorization matters. Problem B is the natural formulation when the learned object will be applied to future events. A theorem can sometimes connect them; D-optimality will provide exactly such a bridge.

### 3.4 Computational access to the score law

| Available input | What can be computed | Natural use |
|---|---|---|
| Weighted scores \((s_i,w_i)\) | Empirical \(W_b,m_b,I_q\) | Finite assignment and empirical inductive fitting |
| Observations \((x_i,w_i)\) + exact/autodiff `score(x)` | Scores are evaluated once, then the same empirical problems | Model-aware datasets with evaluable local likelihood derivatives |
| **Density-ratio oracle** \(r(x;\theta,\theta_0)\) + reference source | Exact or estimated local score without evaluating either density separately | Analytic ratios, simulator-based inference, learned ratio models |
| Component density ratios \(\phi_\alpha/\phi_{\rm ref}\) + reference coefficients | Exact mixture/intensity score coordinates | Template/component models where only relative shapes are available |
| Samples + direct density-ratio estimator | Estimated ratios, then estimated score coordinates | High-dimensional models where separate density estimation is undesirable |
| Observations or simulator + classifier ratio estimator | Estimated likelihood/component ratios and score table | Implicit models, detector-level simulation, data/MC components |
| Sampler \(X\sim P_{\theta_0}\) + score/ratio provider | Monte-Carlo estimates of population moments, stochastic gradients | Simulation-based population quantizer learning |
| Proposal sampler \(X\sim G\) + importance ratio \(dP_{\theta_0}/dG\) | Reference expectations by weighted Monte Carlo | Reuse of off-reference or component-wise samples |
| Direct score sampler \(S\sim P_S\) | Same as above without materializing observation space | Models whose score law is directly available |
| Density/integrator + score map | Quadrature or analytic cell moments; potentially deterministic population objective | Low-dimensional analytic models |
| Moment oracle for a proposed quantizer | Returns \(W_b,m_b\) directly, optionally derivatives | Specialized analytic backends |

**A score or ratio provider alone is not a training distribution.** Knowing \(s(x)\), or enough density ratios to construct it, is sufficient to apply an already learned score-space quantizer. Population optimization additionally requires the reference measure \(P_{\theta_0}\), a sample from it, importance weights relative to a proposal measure, or an equivalent integration oracle.

### 3.5 Density ratios are sufficient for the local score

The full likelihood is more information than this framework needs. Fix a reference parameter \(\theta_0\) and define the likelihood ratio

\[
r(x;\theta,\theta_0)=\frac{p(x\mid\theta)}{p(x\mid\theta_0)}.
\]

Because the denominator is independent of \(\theta\),

\[
\boxed{
s(x)=\nabla_\theta\log p(x\mid\theta)\big|_{\theta_0}
      =\nabla_\theta\log r(x;\theta,\theta_0)\big|_{\theta_0}.}
\]

Thus an exact local family of density ratios is an exact score oracle. Neither \(p(x\mid\theta)\) nor \(p(x\mid\theta_0)\) needs to be available separately. Numerically, for coordinate \(j\),

\[
s_j(x)=\lim_{\delta\to0}
\frac{\log r(x;\theta_0+\delta e_j,\theta_0)
      -\log r(x;\theta_0-\delta e_j,\theta_0)}{2\delta},
\]

or equivalently one may estimate the single ratio \(p(x\mid\theta_0+\delta e_j)/p(x\mid\theta_0-\delta e_j)\). This makes **density-ratio estimation**, rather than density estimation, the natural upstream inference problem. Direct density-ratio methods explicitly exploit this asymmetry: estimating \(p/q\) from samples can be easier and better conditioned than estimating \(p\) and \(q\) independently and dividing the estimates [[22]](#ref-22).

The statement is especially strong for the linear component model

\[
\lambda(x;\theta)=\sum_{\alpha=1}^d\theta_\alpha\phi_\alpha(x).
\]

Choose any reference component \(0\) with positive support and define only the relative component functions

\[
r_\alpha(x)=\frac{\phi_\alpha(x)}{\phi_0(x)},\qquad r_0(x)=1.
\]

For the eventwise extended-intensity score,

\[
\boxed{
s_\alpha(x)=\frac{\phi_\alpha(x)}{\lambda(x;\theta_0)}
=\frac{r_\alpha(x)}{\sum_\beta\theta_{0\beta}r_\beta(x)}.}
\]

The unknown common factor \(\phi_0(x)\) cancels exactly. Therefore ScoreQuant does **not** need a programmatic PDF for every component: a connected set of pairwise component ratios, or all ratios to one reference component, is sufficient. For a normalized mixture, the derivative of the normalization (or the corresponding constrained-weight transformation) must additionally be applied; it also depends only on the same ratios plus known component normalizations.

This ratio invariance should not be confused with arbitrary monotone invariance. A classifier ranking score is not sufficient in general: the optimizer needs numerical score coordinates, so the classifier output must be calibrated to posterior odds / likelihood ratios, or replaced by a direct ratio estimator.

### 3.6 Estimating density ratios: classifiers and direct methods

A probabilistic classifier is one convenient density-ratio estimator, but it is not the only one. Suppose a binary classifier \(D(x)\) distinguishes samples from \(p_1\) and \(p_0\) with training priors \(\pi_1,\pi_0\). At the Bayes optimum,

\[
\frac{p_1(x)}{p_0(x)}
=\frac{D(x)}{1-D(x)}\frac{\pi_0}{\pi_1}.
\]

This is the likelihood-ratio trick used in likelihood-free inference [[21]](#ref-21). Taking \(p_1=p(x\mid\theta_0+\delta e_j)\) and \(p_0=p(x\mid\theta_0-\delta e_j)\) gives

\[
\boxed{\hat s_j(x)=\frac{1}{2\delta_j}
\left[\operatorname{logit}D_j(x)-\log\frac{\pi_1}{\pi_0}\right],}
\]

with central finite-difference bias \(O(\delta_j^2)\) before ratio-estimation error.

For component classification, if \(\eta_\alpha(x)=P(C=\alpha\mid x)\) and the classifier training prior is \(\pi_\alpha\), Bayes' rule gives

\[
\frac{\phi_\alpha(x)}{\phi_\beta(x)}
=\frac{\eta_\alpha(x)/\pi_\alpha}{\eta_\beta(x)/\pi_\beta}.
\]

Combining this directly with the mixture-score expression avoids reconstructing any component density:

\[
\boxed{
s_\alpha(x)=
\frac{\eta_\alpha(x)/\pi_\alpha}
{\sum_\beta \theta_{0\beta}\,\eta_\beta(x)/\pi_\beta}.}
\]

When \(\pi_\alpha\propto\theta_{0\alpha}\), this simplifies to \(s_\alpha(x)=\eta_\alpha(x)/\theta_{0\alpha}\) for the extended-intensity parameterization. This is the clean mathematical explanation for the existing component-classifier workflow.

Classifier odds are only one backend. Direct ratio estimators such as KLIEP or uLSIF fit \(p_1/p_0\) from samples without separately estimating either density [[22]](#ref-22). A user may also provide analytic ratios, a parameterized neural ratio estimator trained elsewhere, or pairwise component-ratio callbacks. These should all enter the software through the same ratio-provider abstraction and be converted to score coordinates by model-specific algebra.

**Exact score versus estimated ratio/score.** Equation (1) is exact for the true score \(s\). If estimated ratios produce \(\hat s\neq s\), then \(\operatorname{Var}(\mathbb E[\hat s\mid q(\hat s)])\) is a surrogate objective; the true retained Fisher information is \(\operatorname{Var}(\mathbb E[s\mid q(\hat s)])\). Implementations should retain ratio-estimator provenance, class priors, calibration/direct-ratio validation, and preferably held-out or cross-fitted evaluation.

There is a second, independent use of density ratios. If population moments are evaluated with samples from a proposal law \(G\neq P_{\theta_0}\), reference expectations can be obtained with importance weights \(w(x)=dP_{\theta_0}/dG\). Again the absolute reference density need not be known, only its ratio to the sampling law.

### 3.7 Rank, refinement, and invariance

Since \\\sum_bm_b=0\\, \\\operatorname{rank}I_q\le\min(d,K-1)\\. Consequently \\K\ge d+1\\ is necessary for a finite unregularized full D criterion. Refining a partition increases \\I_q\\ in Loewner order because conditioning on a finer sigma-algebra increases between-cell variance. Under an invertible reparameterization of \\\theta\\, D-optimal partitions are invariant because \\\log\det I_q\\ changes only by a quantizer-independent additive constant.

</div>

<div id="variation" class="section">

## 4. First variation and common geometric stationarity

Consider moving infinitesimal probability mass \\d\varepsilon\\ at score \\s\\ from cell \\a\\ to cell \\b\\. Differentiating the cell moment expression gives \\ dI_q=\left\[(s-\mu_a)(s-\mu_a)^\top-(s-\mu_b)(s-\mu_b)^\top\right\]d\varepsilon. \tag{3} \\ For a differentiable criterion \\F(I)\\ with symmetric gradient \\G=\nabla_I F(I)\\, \\ \boxed{\frac{dF}{d\varepsilon}=(s-\mu_a)^\top G(s-\mu_a)-(s-\mu_b)^\top G(s-\mu_b).} \tag{4} \\ Therefore any regular atomless population local optimum must satisfy the nearest-cell rule \\ q(s)\in\arg\min_b (s-\mu_b)^\top G(s-\mu_b)\qquad P_S\text{-a.e.} \tag{5} \\ provided the criterion is differentiable at \\I_q\\ and boundary ties have zero probability.

<div class="proposition">

<div class="box-title">

Proposition 1 — affine form of a common-metric stationary partition

</div>

If the same symmetric matrix \\G\\ is used for all cells, pairwise comparisons cancel the common term \\s^\top Gs\\. Thus every cell is an intersection of affine halfspaces. For \\G\succeq0\\ the rule is a Mahalanobis Voronoi diagram, possibly cylindrical when \\G\\ is singular. Equivalently it is an affine-max classifier \\q(s)=\arg\max_b(a_b^\top s+c_b)\\.

</div>

Equation (5) is a population first-order condition. It is not a convergence theorem and does not imply that a finite hard empirical objective is smooth in geometric parameters. Those distinctions become important below.

</div>

<div id="d" class="section">

## 5. D-optimality

For \\ F_D(I)=\log\det I,\qquad G_D=I^{-1}, \tag{6} \\ regular population stationary quantizers are self-consistent Mahalanobis Voronoi partitions: \\ q(s)=\arg\min_b(s-\mu_b)^\top I_q^{-1}(s-\mu_b). \tag{7} \\ The metric is itself determined by the resulting partition.

### 5.1 Exact finite relocation

For a weighted empirical score table, move a point \\(s,w)\\ from a non-singleton source cell \\a\\ to destination \\b\\. Let \\ u_a=s-\mu_a,\quad u_b=s-\mu_b,\quad \alpha=\frac{wW_a}{W_a-w},\quad \beta=\frac{wW_b}{W_b+w}. \tag{8} \\ The exact change of retained information collapses to one positive and one negative rank-one update, \\ \boxed{\Delta I=\alpha u_au_a^\top-\beta u_bu_b^\top.} \tag{9} \\ With \\H=I^{-1}\\ and \\q\_{aa}=u_a^\top Hu_a\\, \\q\_{bb}=u_b^\top Hu_b\\, \\q\_{ab}=u_a^\top Hu_b\\, the determinant lemma gives \\ \boxed{\Delta F_D=\log\\\left\[(1+\alpha q\_{aa})(1-\beta q\_{bb})+\alpha\beta q\_{ab}^2\right\].} \tag{10} \\ The candidate move therefore requires only three inverse-metric inner products once the current factorization is available.

### 5.2 Exchange stability implies a deployable D quantizer

<div class="proposition">

<div class="box-title">

Lemma 2 — leverage bound

</div>

For a nonsingular partition, \\ (\mu_a-\mu_b)^\top I^{-1}(\mu_a-\mu_b)\le \frac1{W_a}+\frac1{W_b}. \tag{11} \\ It follows from the projection matrix associated with \\\[\sqrt{W_1}\mu_1,\ldots,\sqrt{W_K}\mu_K\]\\.

</div>

<div class="theorem">

<div class="box-title">

Theorem 3 — finite D exchange stability forces self-consistent Voronoi geometry

</div>

Assume positive weights, merged duplicate score atoms, distinct nonempty centroids, and positive-definite \\I\\. For an admissible move \\a\to b\\, if the point is no closer to its own centroid than to \\b\\ in the current D metric, \\ q\_{aa}\ge q\_{bb}, \\ then \\ \Delta F_D\ge \log\\\left(1+\frac{\alpha\beta}4q\_\delta^2\right)\>0, \qquad q\_\delta=(\mu_a-\mu_b)^\top I^{-1}(\mu_a-\mu_b). \tag{12} \\ Hence every one-point-exchange-stable finite D partition is a strict self-consistent \\I^{-1}\\-Mahalanobis Voronoi partition on the observed rows.

</div>

The theorem closes the finite-assignment/quantizer gap for D in a strong sense. An exchange solver may pass through arbitrary labelings, but once it reaches one-point stability the final state has the canonical inductive extension \\ \widehat q_D(s)=\arg\min_b(s-\mu_b)^\top \widehat I^{-1}(s-\mu_b), \tag{13} \\ which reproduces every training label strictly. Every global finite D optimum is exchange-stable, and therefore at least one global finite optimum is geometrically realizable in this canonical form. This does not imply population optimality or statistical consistency; it only proves that finite D optimization does not destroy the natural score-space geometry.

<figure>
<img src="figures/fig-02-exchange-slack-histogram.png" alt="Histogram of slack above Theorem 6 lower bound" />
<figcaption>Independent stress test on 15,000 random \(N=12,d=2,K=3\) configurations. Among 5,547 moves satisfying the theorem's Voronoi-violating premise, no violation of the exact lower bound was found; the smallest observed slack above the bound was \(2.04\times10^{-4}\) nat.</figcaption>
</figure>

### 5.3 Exact exchange, Lloyd proposals, and global search

Accepting only moves with positive exact gain yields a strictly monotone finite algorithm. Since there are finitely many labelings, it terminates. The tempting batch iteration that freezes \\I^{-1}\\, reassigns all points to nearest current centroids, and recomputes \\I\\ is not monotone: the tangent inequality for concave \\\log\det\\ is an upper bound, not a minorizer. A batch proposal should therefore be guarded by exact objective evaluation.

<div class="figure-pair">

<figure>
<img src="figures/fig-03-lloyd-counterexample-before.png" alt="Lloyd counterexample before step" />
<figcaption>Explicit \(N=8,K=3,d=2\) state before the adaptive batch step. Crosses mark Euclidean centroids only for visualization; the assignment itself uses the current \(I^{-1}\) metric.</figcaption>
</figure>

<figure>
<img src="figures/fig-04-lloyd-counterexample-after.png" alt="Lloyd counterexample after step" />
<figcaption>After one adaptive-Mahalanobis Lloyd reassignment. On the rounded coordinates reproduced here, \(\log\det I\) falls from \(-3.810643\) to \(-3.947164\): \(-0.136521\) nat.</figcaption>
</figure>

</div>

The finite geometry also restricts global optima to affine-max labelings. For fixed \\(d,K)\\, arrangement enumeration therefore gives an \\N^{O(Kd)}\\ exact algorithm, analogous in spirit to fixed-parameter Voronoi enumeration in clustering [\[9\]](#ref-9). A practical branch-and-bound upper bound follows from refinement monotonicity: treating every unassigned point as a singleton produces an information matrix that Loewner-dominates every completion.

<div class="figure-pair">

<figure>
<img src="figures/fig-05-exhaustive-hit-rates.png" alt="Hit rates against exhaustive optimum" />
<figcaption>Independent exhaustive benchmark. Each point cloud was centered and Fisher-whitened; the exhaustive search enumerated all \(S(10,3)=9{,}330\) nonempty unlabeled partitions. Ten-restart Euclidean \(k\)-means was globally D-optimal on 25/30 instances. Exact exchange repaired every miss in this particular seed; ten exchange starts also reached 30/30. This is a small benchmark, not a general global-optimality guarantee.</figcaption>
</figure>

<figure>
<img src="figures/fig-06-exhaustive-objective-gaps.png" alt="Objective gaps to exhaustive optimum" />
<figcaption>Log-determinant gaps to the exhaustive optimum for the same 30 independent instances. The largest k-means gap was \(0.1397\) nat. Exact exchange from the selected k-means initialization closed all gaps for this independent run.</figcaption>
</figure>

</div>

</div>

<div id="ds" class="section">

## 6. Profiled \\D_s\\-optimality

Partition the parameter as \\\theta=(\psi,\lambda)\\, with \\\psi\in\mathbb R^{d\_\psi}\\ of interest and \\\lambda\\ nuisance. Write \\ I=\begin{pmatrix}A&B\\B^\top&C\end{pmatrix},\qquad S\_\psi(I)=A-BC^{-1}B^\top, \\ and optimize \\ F_s(I)=\log\det S\_\psi(I)=\log\det I-\log\det C. \tag{14} \\ This is the profiled information when both interest and nuisance parameters are estimated from the same binned label.

### 6.1 Efficient-score semimetric

The matrix gradient is \\ G_s=I^{-1}-E\_\lambda C^{-1}E\_\lambda^\top =L^\top S\_\psi(I)^{-1}L\succeq0, \qquad L=\[I\_{d\_\psi},-BC^{-1}\], \tag{15} \\ with rank \\d\_\psi\\. Thus a regular population stationary quantizer is Voronoi in the projected *binned efficient score* \\ e_q(s)=s\_\psi-BC^{-1}s\_\lambda. \tag{16} \\ Its cells are cylindrical along the nuisance directions annihilated by \\L\\. This is a necessary population stationarity condition under the same regularity assumptions as Proposition 1.

### 6.2 Finite exchange remains exact, but the D bridge fails

The rank-two update (9) remains valid for any criterion. For \\D_s\\, the exact finite gain is the difference between two determinant-lemma gains, one for the full information matrix and one for the nuisance block. Positive-gain exchange is therefore still monotone. What fails is the D-specific implication from a first-order geometric violation to a positive finite gain: the nuisance determinant can improve enough to offset the full determinant in a way invisible to the efficient semimetric.

<div class="theorem">

<div class="box-title">

Proposition 4 — approximate finite efficient-Voronoi geometry

</div>

At a one-point-exchange-stable \\D_s\\ partition, let \\s\_{aa}=u_a^\top G_su_a\\, \\s\_{bb}=u_b^\top G_su_b\\, and \\q\_{aa}=u_a^\top I^{-1}u_a\\. For any admissible move, \\ \left\[s\_{aa}-s\_{bb}\right\]\_+ \le w_i q\_{aa}\left(\frac1{W_a}+\frac1{W_b}\right). \tag{17} \\ For uniform weights and cell masses bounded below on the order of \\1/K\\, the relative violation is \\O(K/N)\\.

</div>

This bound explains how finite exchange-stable solutions can approach the population efficient-Voronoi geometry as individual observation weights vanish. It is not by itself a consistency theorem: convergence of global finite optima, control of cell masses, and stability of the profiled information blocks require additional assumptions.

### 6.3 A global finite \\D_s\\ optimum can be non-geometric

<div class="warning">

<div class="box-title">

Exact finite counterexample

</div>

There exists a centered equal-weight \\N=8,d=2,d\_\psi=1,K=3\\ score table for which exhaustive enumeration of all 966 unlabeled nonempty three-cell partitions produces a unique global \\D_s\\ optimum that violates the nearest-cell rule induced by its own \\G_s\\ semimetric. In one exact-rational construction the best profiled scalar information is \\6241/984\\, the second-best value is \\4232/669\\, and two observations have strictly positive self-induced efficient-Voronoi violation margins \\2862/3239\\ and \\618/3239\\. Therefore the discrepancy is not a local-search artifact: unrestricted finite \\D_s\\ assignment and self-consistent inductive \\D_s\\ quantizer fitting are genuinely different finite problems.

</div>

### 6.4 Efficient-score domination

Let the *full-data* efficient score be \\ \widehat S=S\_\psi-B^\*S\_\lambda,\qquad B^\*=I\_{\psi\lambda}^{\mathrm{full}}(I\_{\lambda\lambda}^{\mathrm{full}})^{-1}. \tag{18} \\ For every quantizer \\q\\, regression residual monotonicity gives the pointwise matrix bound \\ \boxed{S\_\psi(I_q)\preceq \operatorname{Var}\\\left(\mathbb E\[\widehat S\mid q(S)\]\right).} \tag{19} \\ Consequently the best profiled \\D_s\\ value is upper-bounded by the best D value obtainable by quantizing the lower-dimensional efficient score, allowing randomized quantization of \\\widehat S\\. If the law of \\\widehat S\\ is atomless, Dvoretzky-Wald-Wolfowitz purification reduces that upper problem to deterministic hard quantizers of \\\widehat S\\ [\[10\]](#ref-10)[\[11\]](#ref-11). The atomlessness condition belongs to the efficient-score law itself; atomlessness of the original score law does not automatically imply it under an arbitrary dimension-reducing projection.

For \\d\_\psi=1\\, deterministic D-optimal quantization of an atomless scalar efficient score has ordered interval cells and can be solved by dynamic programming on a finite sample. This makes (19) a useful initializer and an upper certificate for the profiled problem. It also clarifies the case \\K\le d\\: full in-bin profiling is singular because \\\operatorname{rank}I_q\le K-1\\, while a lower-dimensional efficient-score compression may remain well posed if nuisance information is supplied externally. These are different statistical formulations and should be exposed as such rather than conflated.

</div>

<div id="e" class="section">

## 7. E-optimality

For \\ F_E(I)=\lambda\_\min(I), \tag{20} \\ the objective is concave and Loewner-monotone but nonsmooth at eigenvalue multiplicities. If the smallest eigenvalue is simple with unit eigenvector \\v\\, one gradient is \\ G_E=vv^\top, \\ so regular population stationarity reduces locally to a rank-one semimetric: \\ q(s)=\arg\min_b\big(v^\top(s-\mu_b)\big)^2. \tag{21} \\ Only the current least-informed projection matters to first order.

### 7.1 Repeated minimum eigenvalues

If the minimum eigenspace has orthonormal basis \\V\in\mathbb R^{d\times r}\\, then the superdifferential of the concave function \\\lambda\_\min\\ is \\ \partial^+\lambda\_\min(I)=\\VHV^\top:H\succeq0,\\ \operatorname{tr}H=1}\\. \tag{22} \\ There is no unique metric. More strongly, for a one-point infinitesimal transfer \\\Delta I=aa^\top-bb^\top\\, \\ d\lambda\_\min(I;\Delta I)=\lambda\_\min\\\left(V^\top\Delta I V\right)\le0 \\ whenever \\r\ge2\\: the projected update is a difference of two rank-one matrices and necessarily has a nonpositive minimum eigenvalue. Thus single-transfer first-order stability can become automatic at the very points where E-optimality equalizes weak directions. A useful global first-order characterization may require a common supergradient satisfying all transfer inequalities simultaneously, in the spirit of E-optimal experimental-design equivalence theory [\[15\]](#ref-15), but this remains to be established for the nonconvex quantizer set.

### 7.2 Finite E assignment

The finite D bridge fails even when the minimum eigenvalue is simple. Exhaustive enumeration on a centered \\N=8,d=2,K=3\\ example produces a global E-optimal partition whose own rank-one \\vv^\top\\ nearest-cell rule disagrees with a training label; the observed violation margin is approximately \\0.06796\\. At the move level, a positive first-order E margin can correspond to a negative exact eigenvalue change. The reverse direction does admit a safe screening rule from concavity: for any supergradient \\G\\, \\ F_E(I+\Delta I)-F_E(I)\le\operatorname{tr}(G\Delta I). \tag{23} \\ Therefore a nonpositive weighted tangent gain certifies that the move cannot improve the exact E objective. This makes supergradient screening useful even though it does not identify the exact finite geometry.

</div>

<div id="soft" class="section">

## 8. Direct geometric and differentiable quantizer optimization

### 8.1 Why hard empirical boundary optimization has no ordinary gradient

Suppose an inductive hard quantizer is parameterized by generators or affine discriminants \\q\_\eta\\. On a finite dataset, the objective \\F(I\_{P_n}(q\_\eta))\\ is piecewise constant in \\\eta\\: as long as no training score crosses a decision boundary, every label and therefore every empirical cell moment remains unchanged. Ordinary gradients are zero almost everywhere and undefined on boundary-crossing surfaces. Consequently, “gradient descent on the hard finite Voronoi objective” is not a useful generic algorithm.

### 8.2 Population hard geometry

For an absolutely continuous population law, moving a boundary changes positive probability mass and shape derivatives can exist. Classical centroidal Voronoi energies have such a theory [\[13\]](#ref-13) and Lloyd convergence has been studied under explicit assumptions [\[14\]](#ref-14). For the present D, \\D_s\\, and E information objectives, however, a complete theorem giving differentiability with respect to moving generators and convergence to local optima has not been established. Even in smooth nonconvex optimization, first-order methods generically guarantee convergence toward stationary points, not toward a local maximum without additional second-order structure.

### 8.3 Randomized soft quantizers

A differentiable formulation is obtained by replacing hard assignments by probabilities \\r_b(s;\eta)\ge0\\, \\\sum_br_b=1\\. For a weighted sample, \\ W_b=\sum_iw_ir\_{ib},\qquad m_b=\sum_iw_ir\_{ib}s_i,\qquad I\_\mathrm{soft}=\sum_b\frac{m_bm_b^\top}{W_b}. \tag{24} \\ This matrix is not merely a numerical surrogate: it is exactly the Fisher information of the corresponding randomized quantizer at the reference parameter. For differentiable \\F\\ with \\G=\nabla F(I\_\mathrm{soft})\\, \\ \boxed{\frac{\partial F}{\partial r\_{ib}}=w_i\left(2s_i^\top G\mu_b-\mu_b^\top G\mu_b\right).} \tag{25} \\ Up to the bin-independent term \\w_is_i^\top Gs_i\\, this is the negative squared \\G\\-distance to the cell centroid. Thus the same affine/Mahalanobis geometry appears directly in the gradient of the soft information objective.

A useful inductive family is \\ r_b(s;\eta,\tau)=\operatorname{softmax}\_b\\\left(\frac{a_b^\top s+c_b}{\tau}\right), \tag{26} \\ which approaches a hard affine-max partition as \\\tau\to0\\ when ties have zero mass. A softened common-metric Voronoi family is another option. Fixed-temperature D and \\D_s\\ objectives are smooth on compact regions bounded away from empty cells and singular information matrices; line-search gradient ascent or quasi-Newton methods can then be made monotone and standard nonconvex theory gives convergence of gradient norms toward zero. This is a stationary-point guarantee, not a generic guarantee of a hard local optimum. For E, one must use subgradients or a smooth spectral approximation near eigenvalue crossings and re-evaluate the exact hard E objective after hardening.

### 8.4 Randomization and purification

For an atomless score law \\P_S\\, the Dvoretzky-Wald-Wolfowitz theorem implies that every randomized \\K\\-action quantizer can be replaced by a deterministic score-space quantizer preserving all \\(W_b,m_b)\\ exactly [\[10\]](#ref-10)[\[11\]](#ref-11). Therefore soft randomization does not improve the *population optimum value* for any criterion depending only on these moments. This is an existence statement, not an optimization guarantee: it neither says that gradient ascent finds the optimum nor that hardening a particular soft parameterization produces the purifying partition. Finite empirical score laws are atomic and lie outside this exact purification result.

</div>

<div id="consistency" class="section">

## 9. From finite training to population quantization

Population stationarity describes the geometry of an ideal optimum; it does not by itself show that a quantizer learned from data converges to such an object. A clean route is to treat empirical inductive fitting as ordinary risk optimization over a finite-capacity geometric class.

<div class="proposition">

<div class="box-title">

Proposition 5 — restricted-class empirical consistency

</div>

Let \\\mathcal Q\\ be a compact parameterized class of \\K\\-cell affine-max quantizers. Assume scores are bounded, or satisfy sufficient uniform integrability conditions; assume the relevant cell masses are uniformly bounded below; and restrict to a region where the information matrices required by the chosen criterion remain uniformly nonsingular. Then the empirical cell probabilities and score first moments converge uniformly to their population counterparts over \\\mathcal Q\\. Consequently D, \\D_s\\, and E objectives converge uniformly on that regular subset. Any sequence of approximate empirical maximizers is therefore value-consistent for the best quantizer in \\\mathcal Q\\; with an isolated population maximizer, the usual argmax theorem yields parameter/decision consistency up to label permutations.

</div>

The proof is standard empirical-process theory: affine multiclass decision regions have finite capacity, so the indicator classes for the cells satisfy a uniform law of large numbers; bounded score coordinates give the same for \\s_j1\_{\\q(s)=b\\}\\; and the matrix criteria are continuous away from singular boundaries. This is analogous in role, though not identical in objective, to Pollard's consistency analysis for \\k\\-means [\[12\]](#ref-12).

For D, Theorem 3 makes the relationship to unrestricted finite assignment unusually favorable because every global finite optimum is already self-consistent geometric. For \\D_s\\ and E, the exact finite counterexamples show that no identical finite reduction is available. Whether their unrestricted global sample optima nevertheless approach population geometric optima as \\N\to\infty\\ under natural assumptions remains open.

</div>

<div id="computational" class="section">

## 10. Computational formulations and reference implementation

The theory naturally supports two top-level output types and several interchangeable sources of score information.

<div class="two-col">

<div class="note">

<div class="box-title">

Finite partition result

</div>

Input: a fixed weighted score table. Output: labels, cell moments, criterion value, exchange stability, exact move diagnostics, and optional global certificate. No prediction semantics are implied unless a criterion-specific theorem or an explicit extension rule is requested.

</div>

<div class="note">

<div class="box-title">

Quantizer result

</div>

Input: a score law representation or finite training source plus a geometric/functional quantizer family. Output: a serializable \\q(s)\\ with `predict_score`; observation-space prediction composes it with a supplied score function.

</div>

</div>

A reference library should therefore separate the *source*, *optimization target*, *criterion*, and *solver*. The same criterion can be applied to a finite partition or to a parameterized quantizer, while the same quantizer trainer can consume an empirical score table, an observation sampler plus score callback, a direct score sampler, or a moment oracle. This avoids embedding assumptions about analytic probability densities into the core algorithms.

| Criterion        | Finite assignment                                                | Inductive quantizer                                                      | Theory-backed relationship                                                                                  |
|------------------|------------------------------------------------------------------|--------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| D                | Exact rank-two exchange; exhaustive/B&B options                  | Mahalanobis or affine/soft fitting                                       | Every terminal one-exchange-stable finite state compiles to its final self-consistent Mahalanobis predictor |
| Profiled \\D_s\\ | Exact exchange is monotone and useful as a sample optimum/oracle | Efficient-semimetric/affine soft fitting; efficient-score initialization | Finite geometry only approximate in general; global finite optimum can be non-geometric                     |
| E                | Exact eigenvalue exchange plus supergradient screening           | Subgradient/smooth spectral geometric fitting                            | No exact finite bridge; multiplicity makes first-order geometry nonunique                                   |

</div>

<div id="experiments" class="section">

## 11. Numerical verification and falsification

The numerical program serves two purposes: verify exact algebra against full recomputation, and actively search for counterexamples to tempting but unjustified geometric or monotonicity claims. The resulting evidence is summarized below; exact-rational constructions are used where a sign claim is logically important.

| Question                                                                                  | Method                                                                  | Outcome                                                         |
|-------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|-----------------------------------------------------------------|
| Does the rank-two relocation identity match full recomputation?                           | Thousands of random admissible D moves                                  | Agreement to floating-point precision                           |
| Can adaptive-Mahalanobis Lloyd decrease D?                                                | Random search plus explicit \\N=8,d=2,K=3\\ example                     | Yes; one batch step decreases \\\log\det I\\ by about 0.137 nat |
| Does the D exchange lower bound fail under stress?                                        | Thousands of premise-satisfying moves                                   | No violation found; exact proof given in Theorem 3              |
| Can globally optimal finite \\D_s\\ assignment violate its own efficient-semimetric rule? | Exact enumeration of 966 three-cell partitions with rational arithmetic | Yes                                                             |
| Can globally optimal finite E assignment violate its simple-eigenvalue rank-one rule?     | Exhaustive \\N=8,d=2,K=3\\ enumeration                                  | Yes                                                             |
| Do terminal D exchange labels match the compiled predictor?                               | Random terminal states                                                  | Yes in all tested nonsingular cases, as guaranteed by Theorem 3 |

</div>

<div id="discussion" class="section">

## 12. Discussion

### 12.1 Finite assignment and quantizer learning are both legitimate

A finite assignment optimizer should not be demoted to a diagnostic merely because it lacks prediction semantics. In applications where the dataset is final—offline histogram construction, a fixed experimental sample, or compression of a stored corpus—the finite combinatorial optimum is itself the desired object. In online or reusable settings, a quantizer is required. The correct architecture is therefore not to choose one formulation globally, but to expose both and make their semantics explicit.

### 12.2 D is structurally exceptional

The determinant criterion has a finite cancellation that does not survive profiled subtraction or minimum-eigenvalue nonsmoothness. The equality \\ \frac{\alpha-\beta}{\alpha\beta}=\frac1{W_a}+\frac1{W_b} \\ meets the D leverage bound exactly and turns an infinitesimal Voronoi violation into a guaranteed finite improvement. This explains why D exchange can simultaneously be an exact sample optimizer and, at termination, a constructor of a canonical inductive geometry. \\D_s\\ retains the population semimetric but not the exact finite implication; E loses uniqueness of the metric itself at eigenvalue multiplicity.

### 12.3 Exact, automatic-differentiation, and learned score interfaces

The core theory never requires that scores originate from a stored matrix or that every component density be evaluable. It requires a representation of the score law. Since the local score is the parameter derivative of a log density ratio, exact or estimated density ratios are a natural upstream primitive. In linear mixture/intensity models even the component functions are only needed through ratios to a common reference component. A classifier is one way to estimate those ratios; direct ratio estimators and analytic ratio callbacks are equally valid. The quantizer ultimately sees score vectors, while provenance records whether they came from exact likelihood derivatives, exact ratios, or estimated ratios.

This separation exposes two different approximation errors: **score-estimation error** and **quantization error**. The exact D, \(D_s\), and E theorems concern the score vectors supplied to the optimizer. Interpreting the resulting matrix as Fisher information for the original model additionally requires those vectors to equal, or consistently estimate, the true local score.

### 12.4 Open theoretical problems

- **Full population consistency.** Extend Proposition 5 beyond a fixed affine family and determine conditions under which unrestricted empirical D, \\D_s\\, or E solutions converge to population optima.
- **\\D_s\\ asymptotic bridge.** Determine whether the \\O(K/N)\\ exchange-stability geometry bound is sufficient, with regularity assumptions, to force global finite \\D_s\\ optima toward population efficient-Voronoi solutions.
- **E common-supergradient geometry.** Establish or refute a population theorem guaranteeing a single minimum-eigenspace supergradient that supports all cell inequalities at an E-optimum.
- **Soft-to-hard limits.** Characterize when stationary points of temperature-softened randomized quantizers converge to stationary hard affine/Mahalanobis quantizers.
- **Hardness.** Determine parameterized complexity for variable \\K\\ or \\d\\; the fixed-\\(d,K)\\ arrangement algorithm is XP, not known FPT.
- **Atomic score laws.** Characterize the gap between randomized and deterministic score quantizers when the score law has atoms.
- **Criterion characterization.** Identify which concave matrix criteria, if any beyond full log determinant, possess a finite exchange-stability ⇒ stationary-geometry theorem.
- **Estimated-score robustness.** Quantify how error in a learned score oracle propagates to cell moments, optimized criteria, geometric boundaries, and true retained Fisher information.

</div>

<div id="conclusion" class="section">

## 13. Conclusion

Hard quantization of multivariate score space has three distinct levels: the population design problem, empirical learning of an inductive score-space rule, and unrestricted optimization of labels on a fixed sample. Treating these as separate objects resolves an apparent conflict between exact exchange optimization and deployability. For D-optimality the conflict disappears at one-point stability: the exact finite exchange algebra and a leverage inequality force the terminal partition to be the training realization of a self-consistent Mahalanobis Voronoi quantizer. For profiled \\D_s\\ and E this finite closure fails, even at global sample optima, although their population first-order geometry remains informative and \\D_s\\ admits a quantitative asymptotic bound and an efficient-score upper problem.

The same formalism also clarifies implementation. The fundamental input is not necessarily a matrix of precomputed scores but a representation of the push-forward score law: a weighted score sample, an observation sample with an exact/autodiff score provider, an exact or estimated density-ratio provider converted to scores, a population sampler, a direct score sampler, or an analytic moment backend. This makes exact finite assignment and reusable score-space quantization complementary capabilities of one framework rather than competing definitions of the problem.

</div>

<div id="references" class="section">

## References

1.  <span id="ref-1">P. Venkitasubramaniam, L. Tong, and A. Swami. “Score-Function Quantization for Distributed Estimation.” CISS, 2006. [doi:10.1109/CISS.2006.286494](https://doi.org/10.1109/CISS.2006.286494).</span>
2.  <span id="ref-2">R. C. Farias and J.-M. Brossier. “Optimal Scalar Quantization for Parameter Estimation.” 2013. [arXiv:1310.6945](https://arxiv.org/abs/1310.6945).</span>
3.  <span id="ref-3">L. P. Barnes, Y. Han, and A. Özgür. “A Geometric Characterization of Fisher Information from Quantized Samples with Applications to Distributed Statistical Estimation.” Allerton, 2018, 16–23. [doi:10.1109/ALLERTON.2018.8635899](https://doi.org/10.1109/ALLERTON.2018.8635899).</span>
4.  <span id="ref-4">B. Dülek. “On the Optimality of Sufficient Statistics-Based Quantizers.” IEEE TPAMI 45(3), 3567–3573, 2023. [doi:10.1109/TPAMI.2022.3172282](https://doi.org/10.1109/TPAMI.2022.3172282).</span>
5.  <span id="ref-5">H. P. Friedman and J. Rubin. “On Some Invariant Criteria for Grouping Data.” JASA 62(320), 1159–1178, 1967. [doi:10.1080/01621459.1967.10500923](https://doi.org/10.1080/01621459.1967.10500923).</span>
6.  <span id="ref-6">A. J. Scott and M. J. Symons. “Clustering Methods Based on Likelihood Ratio Criteria.” Biometrics 27(2), 387–397, 1971. [doi:10.2307/2529003](https://doi.org/10.2307/2529003).</span>
7.  <span id="ref-7">J. A. Hartigan. *Clustering Algorithms*. Wiley, 1975.</span>
8.  <span id="ref-8">M. Telgarsky and A. Vattani. “Hartigan’s Method: k-means Clustering without Voronoi.” AISTATS, PMLR 9, 820–827, 2010. [PMLR](https://proceedings.mlr.press/v9/telgarsky10a.html).</span>
9.  <span id="ref-9">M. Inaba, N. Katoh, and H. Imai. “Applications of weighted Voronoi diagrams and randomization to variance-based k-clustering.” SoCG, 332–339, 1994. [doi:10.1145/177424.178042](https://doi.org/10.1145/177424.178042).</span>
10. <span id="ref-10">A. Dvoretzky, A. Wald, and J. Wolfowitz. “Elimination of Randomization in Certain Statistical Decision Procedures and Zero-Sum Two-Person Games.” Annals of Mathematical Statistics 22(1), 1–21, 1951. [doi:10.1214/aoms/1177729689](https://doi.org/10.1214/aoms/1177729689).</span>
11. <span id="ref-11">M. A. Khan, K. P. Rath, and Y. Sun. “The Dvoretzky-Wald-Wolfowitz theorem and purification in atomless finite-action games.” International Journal of Game Theory 34, 91–104, 2006. [doi:10.1007/s00182-005-0004-3](https://doi.org/10.1007/s00182-005-0004-3).</span>
12. <span id="ref-12">D. Pollard. “Strong Consistency of K-Means Clustering.” Annals of Statistics 9(1), 135–140, 1981. [PDF](https://www.stat.yale.edu/~pollard/Papers/Pollard81AS.pdf).</span>
13. <span id="ref-13">Q. Du, V. Faber, and M. Gunzburger. “Centroidal Voronoi Tessellations: Applications and Algorithms.” SIAM Review 41(4), 637–676, 1999. [doi:10.1137/S0036144599352836](https://doi.org/10.1137/S0036144599352836).</span>
14. <span id="ref-14">Q. Du, M. Emelianenko, and L. Ju. “Convergence of the Lloyd Algorithm for Computing Centroidal Voronoi Tessellations.” SIAM J. Numer. Anal. 44(1), 102–119, 2006. [doi:10.1137/040617364](https://doi.org/10.1137/040617364).</span>
15. <span id="ref-15">F. Pukelsheim. *Optimal Design of Experiments*. SIAM Classics in Applied Mathematics. See Ch. 7, General Equivalence Theorem. [doi:10.1137/1.9780898719109.ch7](https://doi.org/10.1137/1.9780898719109.ch7).</span>
16. <span id="ref-16">W. Näther and V. Reinsch. “D_s-optimality and Whittle’s equivalence theorem.” Series Statistics 12(3), 307–316, 1981. [doi:10.1080/02331888108801591](https://doi.org/10.1080/02331888108801591).</span>
17. <span id="ref-17">J. Brehmer, G. Louppe, J. Pavez, and K. Cranmer. “Mining gold from implicit models to improve likelihood-free inference.” PNAS 117(10), 5242–5249, 2020. [doi:10.1073/pnas.1915980117](https://doi.org/10.1073/pnas.1915980117).</span>
18. <span id="ref-18">P. de Castro and T. Dorigo. “INFERNO: Inference-Aware Neural Optimisation.” Computer Physics Communications 244, 170–179, 2019. [doi:10.1016/j.cpc.2019.06.007](https://doi.org/10.1016/j.cpc.2019.06.007).</span>
19. <span id="ref-19">K. T. Matchev and P. Shyamsundar. “Optimal event selection and categorization in high energy physics. Part I. Signal discovery.” JHEP 03, 291, 2021. [doi:10.1007/JHEP03(2021)291](https://doi.org/10.1007/JHEP03(2021)291).</span>
20. <span id="ref-20">J. Erdmann, N. K. Kasaraguppe, and F. Mausolf. “Learning to bin: differentiable and Bayesian optimization for multi-dimensional discriminants in high-energy physics.” 2026. [arXiv:2601.07756](https://arxiv.org/abs/2601.07756).</span>
21. <span id="ref-21">K. Cranmer, J. Pavez, and G. Louppe. “Approximating Likelihood Ratios with Calibrated Discriminative Classifiers.” 2015. [arXiv:1506.02169](https://arxiv.org/abs/1506.02169).</span>
22. <span id="ref-22">M. Sugiyama, T. Suzuki, and T. Kanamori. *Density Ratio Estimation in Machine Learning*. Cambridge University Press, 2012. [doi:10.1017/CBO9781139035613](https://doi.org/10.1017/CBO9781139035613).</span>

</div>

</div>

<div class="toc-title">

Contents

</div>

[1. Introduction](#intro) [2. Related work](#related) [3. Statistical formulation](#formulation) [4. First variation](#variation) [5. D-optimality](#d) [6. Profiled D_s](#ds) [7. E-optimality](#e) [8. Differentiable optimization](#soft) [9. Statistical consistency](#consistency) [10. Computational formulations](#computational) [11. Numerical verification](#experiments) [12. Discussion](#discussion) [13. Conclusion](#conclusion) [References](#references)

</div>
