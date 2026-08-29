# ScoreQuant canonical research problem

**Status:** authoritative project scope for mathematical, algorithmic, and software work  
**Version:** 2.0 · 26 August 2026  
**Rule:** read this file before proving theorems, searching literature, designing algorithms, or changing APIs.

---

## 1. Canonical objective

Develop theory and practical algorithms for **deterministic hard quantization of multivariate statistical score space** that maximize **D- or \(D_s\)-optimal Fisher information**, support exact or estimated score access—including direct scores, analytic PDFs, density ratios, and calibrated classifiers—and return a **deployable event partition** with explicit optimality diagnostics and quantitative information loss relative to unbinned inference.

A primary application is **multicomponent linear/template fitting**, especially in high-energy physics (HEP), where the parameters are component weights/yields, nuisance parameters are important, and event-level score information can often be constructed from **component density ratios** without reconstructing all component PDFs.

The scientific motivation is not generic dimensionality reduction. It is:

> If a robust analysis requires a finite set of bins/categories for systematic-control, calibration, validation, MC-statistics, and downstream likelihood construction, choose those bins so that the relevant statistical information loss is as small and as measurable as possible.

---

## 2. Statistical setting

Let

\[
X\sim p(x\mid\theta),\qquad \theta\in\Theta\subset\mathbb R^d,
\]

and fix a reference point \(\theta_0\). The local score is

\[
S=s(X)=\nabla_\theta\log p(X\mid\theta)\big|_{\theta_0}\in\mathbb R^d,
\]

with

\[
E[S]=0,\qquad I_{\rm full}=E[SS^\top].
\]

A deterministic hard \(K\)-level score quantizer is

\[
q:\mathbb R^d\to\{1,\ldots,K\},\qquad Z=q(S).
\]

For cell \(b\),

\[
W_b=P(Z=b),\qquad
m_b=E[S1_{\{Z=b\}}],\qquad
\mu_b=E[S\mid Z=b]=m_b/W_b.
\]

The exact Fisher information of the categorical observation is

\[
\boxed{
I_q
=\sum_bW_b\mu_b\mu_b^\top
=\sum_b\frac{m_bm_b^\top}{W_b}
=\operatorname{Var}(E[S\mid Z]).
}
\]

The unbinned-to-binned information decomposition is

\[
\boxed{
I_{\rm full}-I_q
=E[\operatorname{Cov}(S\mid Z)]\succeq0.
}
\]

Because \(\sum_bm_b=0\),

\[
\operatorname{rank}(I_q)\le\min(d,K-1).
\]

Thus full unregularized D requires \(K\ge d+1\).

---

## 3. Primary criteria

### 3.1 Full D-optimality

\[
\Phi_D(I)=\log\det I,
\qquad
q_D^\star\in\arg\max_q\Phi_D(I_q).
\]

Interpretation: maximize generalized local precision / minimize confidence-ellipsoid volume.

### 3.2 Profiled \(D_s\)-optimality

Partition

\[
\theta=(\psi,\lambda),
\]

where \(\psi\in\mathbb R^s\) are parameters of interest and \(\lambda\) are nuisance parameters. Write

\[
I=
\begin{pmatrix}
I_{\psi\psi}&I_{\psi\lambda}\\
I_{\lambda\psi}&I_{\lambda\lambda}
\end{pmatrix}.
\]

When the nuisance block is nonsingular, the in-bin profiled information is

\[
\boxed{
S_\psi(I)
=I_{\psi\psi}
-I_{\psi\lambda}I_{\lambda\lambda}^{-1}I_{\lambda\psi}.
}
\]

The primary nuisance-aware objective is

\[
\Phi_{D_s}(I)=\log\det S_\psi(I).
\]

Equivalently, in the nonsingular full-block regime,

\[
\Phi_{D_s}(I)=\log\det I-\log\det I_{\lambda\lambda}.
\]

### 3.3 A distinct projected-efficient-score formulation

The project also uses the **full-data efficient score**

\[
\widehat S=S_\psi-B^*S_\lambda,
\qquad
B^*=I^{\rm full}_{\psi\lambda}(I^{\rm full}_{\lambda\lambda})^{-1}.
\]

D-optimal quantization of \(\widehat S\) is an upper/reference problem for in-bin \(D_s\), and may remain well posed when \(K\le d\) provided nuisance information is supplied externally. This is **not the same statistical formulation** as profiling nuisance parameters using only the binned categorical observation. Software and theorems must not conflate the two.

### 3.4 Secondary/control criteria

Normalized trace, A, and E are retained as baselines, controls, and theorem-falsification tools. They are not the primary project target unless a task says otherwise.

---

## 4. Three optimization levels

Every claim must state its level.

### A. Finite transductive assignment

Given a weighted score table \((s_i,w_i)_{i=1}^N\), optimize arbitrary labels

\[
z_i\in\{1,\ldots,K\}.
\]

This is a finite combinatorial problem. Its output is a labeling, not automatically a rule for unseen observations.

### B. Empirical inductive quantizer fitting

Choose an explicit function family \(q_\eta:\mathbb R^d\to[K]\) and maximize empirical D or \(D_s\). The output is a function that can be frozen and evaluated on held-out/new scores.

Natural families include affine-max partitions and common-metric Mahalanobis Voronoi partitions.

### C. Population quantizer design

Optimize a measurable \(q\) under the score law \(P_S\):

\[
\sup_q\Phi(I_P(q)).
\]

Population first-variation geometry is not by itself a consistency theorem for a quantizer learned from finite data.

### Criterion-specific bridge

- **D:** current project theory gives a strong finite bridge: every one-point-exchange-stable positive-definite finite solution has a canonical self-consistent Mahalanobis extension that reproduces all training labels.
- **\(D_s\):** this exact finite bridge fails; even a global finite optimum can be non-geometric.
- **E:** this exact finite bridge also fails.

See `KNOWN_RESULTS/` for exact status.

---

## 5. Score/model-access regimes

These are alternative ways to supply the same downstream quantization problem.

### 5.1 Direct score sample

Input \((s_i,w_i)\) directly. This is the lowest-level mathematical API.

### 5.2 Exact/autodiff score function

Given observations \(x\) and a likelihood model, evaluate

\[
s(x)=\nabla_\theta\log p(x\mid\theta)|_{\theta_0}.
\]

### 5.3 Density-ratio oracle

The local score can be obtained from a density ratio against a fixed reference:

\[
s(x)=\left.\nabla_\theta\log\frac{p(x\mid\theta)}{p(x\mid\theta_0)}\right|_{\theta_0}.
\]

Absolute densities are therefore not intrinsically required.

### 5.4 Linear/template-component ratios

For a component model

\[
p(x\mid\theta)=\sum_\alpha\theta_\alpha\phi_\alpha(x),
\]

score coordinates contain

\[
\frac{\phi_\alpha(x)}{\sum_\beta\theta_{0\beta}\phi_\beta(x)}.
\]

Thus ratios of component shapes to one reference component are sufficient to reconstruct the score after choosing a parameterization.

### 5.5 Calibrated classifier oracle

For classifier posteriors \(\eta_\alpha(x)=P(C=\alpha\mid x)\) with training priors \(\pi_\alpha\),

\[
\frac{\phi_\alpha(x)}{\phi_r(x)}
=
\frac{\eta_\alpha(x)}{\eta_r(x)}\frac{\pi_r}{\pi_\alpha}.
\]

For the linear component parameterization this yields

\[
\boxed{
s_\alpha(x)=
\frac{\eta_\alpha(x)/\pi_\alpha}
{\sum_\beta\theta_{0\beta}\eta_\beta(x)/\pi_\beta}.
}
\]

If \(\pi_\alpha\propto\theta_{0\alpha}\), the extended-intensity form simplifies accordingly.

**Calibration and training priors are part of the statistical model access. Classification accuracy/AUC alone is not sufficient validation.**

### 5.6 Exact score versus estimated score

If an estimated ratio/classifier produces \(\hat s\neq s\), optimizing

\[
\operatorname{Var}(E[\hat s\mid q(\hat s)])
\]

is a surrogate. The true retained Fisher information of the resulting bin label is

\[
\boxed{
I_{q(\hat s)}
=
\operatorname{Var}(E[s\mid q(\hat s)]).
}
\]

When true scores are available on simulation/validation data, evaluation should use the latter.

---

## 6. Primary application: HEP linear/template fitting

The canonical HEP use case is a mixture/intensity model with component weights or yields as fit parameters, possibly accompanied by many systematic nuisance parameters.

For an extended intensity

\[
\lambda(x\mid\nu)=\sum_c\nu_cf_c(x),
\]

the event-dependent derivative is

\[
\frac{\partial\log\lambda(x\mid\nu)}{\partial\nu_c}
=
\frac{f_c(x)}{\sum_j\nu_jf_j(x)}.
\]

The extended likelihood also contains count/Poisson information. Every example must state whether this count information is kept separately, represented in an augmented score, or intentionally conditioned away.

The reason for hard categories is typically systematic-control and model robustness, not inability to process a high-dimensional observation.

---

## 7. Information loss is a first-class output

### 7.1 D-efficiency

\[
\boxed{
\eta_D
=
\left(\frac{\det I_q}{\det I_{\rm full}}\right)^{1/d}
\in[0,1].
}
\]

Suggested loss score:

\[
L_D=1-\eta_D.
\]

### 7.2 \(D_s\)-efficiency

\[
\boxed{
\eta_{D_s}
=
\left(
\frac{\det S_\psi(I_q)}
{\det S_\psi(I_{\rm full})}
\right)^{1/s}.
}
\]

Suggested loss score:

\[
L_{D_s}=1-\eta_{D_s}.
\]

### 7.3 Direction-resolved retention

For full D,

\[
R=I_{\rm full}^{-1/2}I_qI_{\rm full}^{-1/2},
\qquad
0\preceq R\preceq I.
\]

Report:

- geometric retention \((\det R)^{1/d}=\eta_D\);
- mean retention \(\operatorname{tr}(R)/d\);
- worst retained direction \(\lambda_{\min}(R)\);
- optionally the full spectrum/eigenvectors.

Use the analogous normalized efficient-information matrix for \(D_s\).

### 7.4 Separate score-oracle loss from quantization loss

For any representation \(R(X)\), define

\[
I_R=\operatorname{Var}(E[s(X)\mid R(X)]).
\]

For a hard quantizer \(q(R)\),

\[
I_q\preceq I_R\preceq I_{\rm full}.
\]

Thus, when true scores are available,

\[
I_{\rm full}-I_R
\]

is representation/oracle loss and

\[
I_R-I_q
\]

is hard-quantization loss.

### 7.5 Exact local losslessness criterion

A hard quantizer is locally Fisher-lossless at \(\theta_0\) iff

\[
\boxed{
I_q=I_{\rm full}
\iff
s(X;\theta_0)=h(q(X))\quad\text{a.s.}
}
\]

Equivalently, conditional score covariance inside every occupied bin vanishes. Generic smooth score laws therefore lose information under finite hard quantization.

---

## 8. Required deliverables

A successful method must provide all of the following.

### 8.1 Practical solver

- useful initialization and multistart;
- exact/safeguarded objective evaluation;
- numerical stability;
- cell-mass/yield constraints where needed;
- train/validation separation;
- reproducible hard prediction.

### 8.2 Explicit guarantee vocabulary

A returned result must say exactly whether it is:

- first-order stationary;
- Voronoi/Lloyd fixed;
- one-point exchange stable;
- \(r\)-swap stable;
- local optimum in a declared quantizer family;
- finite global optimum;
- globally optimal within a restricted family;
- population/value consistent.

Never write “optimal” without the qualifier.

### 8.3 New-event assignment

Production output must contain an explicit rule

\[
x\mapsto s(x)\mapsto q(s).
\]

Finite labels alone are a benchmark/oracle, not a deployable product, except where a theorem supplies an exact compiler (currently D).

### 8.4 Information accounting

Always compare against unbinned inference using D/\(D_s\) efficiency and direction-resolved retention.

---

## 9. Practical constraints kept separate from the clean core

The clean theory assumes positive weights and nonempty cells. Extensions requiring explicit treatment include:

- minimum expected bin yield/probability;
- negative MC weights;
- singular/near-singular information;
- regularization;
- atomic/duplicate score distributions;
- ties;
- weakly identified nuisance blocks;
- boundary simplicity/interpretability constraints;
- robustness away from \(\theta_0\).

Negative MC weights must not be silently interpreted as probabilities.

---

## 10. Locality and robustness

Score/Fisher optimization is local at \(\theta_0\). Secondary research questions include:

- degradation away from \(\theta_0\);
- multi-reference optimization;
- expected or minimax criteria over parameter regions;
- iterative reoptimization after fitting.

---

## 11. Scope guardrails

A result is adjacent but not automatically a solution if its decision variable is only:

- experimental-design weights/points;
- sensor or feature selection;
- scalar threshold placement;
- within-cluster determinant minimization;
- ordinary k-means;
- soft categories with no hard deployable map;
- D-optimal subset selection.

The target feasible set is induced by **hard partitions of score/score-proxy space**, and the information matrix is that of the resulting categorical observation.

---

## 12. Success questions

For a model and chosen \(K\), ScoreQuant should answer:

1. How is the event score obtained or estimated?
2. Which exact statistical objective is being optimized—full D, in-bin \(D_s\), or a projected efficient-score reference problem?
3. How is a hard deployable partition constructed?
4. What local/global guarantee does the returned solution satisfy?
5. How are unseen events assigned?
6. How much information is lost relative to unbinned inference?
7. Which parameter directions lose information?
8. How much additional loss came from score/ratio estimation?
9. How sensitive is the result to finite sample size, nuisance parameters, cell constraints, and reference-point mismatch?
