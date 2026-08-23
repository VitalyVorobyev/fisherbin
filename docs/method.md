# Method

## 1. Score-space formulation

At a reference parameter point $\theta_0$, describe each observation by the score

$$
s(x)=\nabla_\theta \log p(x\mid\theta)\big|_{\theta_0}.
$$

For weighted samples, FisherBin works directly with

$$
(s_i, w_i), \qquad s_i\in\mathbb{R}^P.
$$

This is the canonical library input. The observation dimension does not enter the optimization once scores have been computed.

Weights represent nonnegative measure, frequency, or exposure. Zero-weight rows are ignored. Signed weights do not preserve the positive-semidefinite identities below and are outside the v0.1 contract. Multiplying all weights by a common positive factor scales both Fisher matrices but does not change normalized retention or the fitted partition.

## 2. Fisher information before and after binning

For a weighted sample, the unbinned Fisher information is estimated by

$$
F_\infty = \sum_i w_i s_i s_i^T.
$$

For a partition $b(i)\in\{1,\ldots,B\}$ define

$$
W_b = \sum_{i:b(i)=b} w_i,
\qquad
\bar s_b = \frac{1}{W_b}\sum_{i:b(i)=b} w_i s_i.
$$

The Fisher information retained by the bin counts is

$$
F_B = \sum_b W_b\bar s_b\bar s_b^T.
$$

The loss is exactly

$$
F_\infty-F_B
=
\sum_b\sum_{i:b(i)=b}
w_i(s_i-\bar s_b)(s_i-\bar s_b)^T
\succeq 0.
$$

This is the central result:

> Binning loses information when observations with different score vectors are grouped together.

Taking the trace gives a weighted within-bin squared-distance objective, so **k-means in score space is a natural baseline**.

## 3. Linear-component models

For

$$
\lambda(x;c)=\sum_\alpha c_\alpha\phi_\alpha(x),
$$

the score is

$$
s_\alpha(x)=\frac{\phi_\alpha(x)}{\lambda(x;c)}.
$$

Therefore the natural representation is the vector of **relative components**, not the absolute component values. This generalizes the original component-space Voronoi idea.

The $\phi_\alpha$ are intensity components, not necessarily normalized probability densities. Individual components and coefficients may be signed; the required physical condition is that the reference intensity $\lambda(x;c_0)$ is finite and strictly positive on the integration sample.

## 4. Algorithms

### Score k-means

Weighted k-means in score space is the first implementation and the main baseline. By default scores are projected onto the numerically informative eigensubspace and whitened using $F_\infty^{-1/2}$ so Euclidean distance corresponds to normalized parameter-information directions. Scores are not mean-centered. Discarded directions and the numerical rank threshold are part of every fitted result.

### Soft Voronoi optimization

For a more flexible objective, represent $B$ bins by centers $z_b$ and use soft assignments during optimization:

$$
r_{ib}
=
\frac{\exp[-\|u_i-z_b\|^2/(2\sigma^2)]}
{\sum_{b'}\exp[-\|u_i-z_{b'}\|^2/(2\sigma^2)]},
$$

where $u_i$ is the score or whitened score. These assignments define differentiable bin statistics and therefore a differentiable Fisher matrix.

The initial objective is D-optimality in the informative subspace:

$$
\max \log\det F_B.
$$

Start from score-k-means centers, optimize with a finite temperature, gradually reduce $\sigma$, then convert to the final hard nearest-center partition.

The differentiable objective uses fractional bin statistics during fitting. The optimizer trace separately records soft retention and the retention of the current hardened partition; the final hard partition is the result users evaluate. D-optimal fitting requires at least as many bins as informative Fisher directions. K-means remains defined below that limit, with zero retained eigenvalues reported explicitly.

Other objectives, nuisance-parameter profiling, occupancy constraints, and weighted Voronoi cells are useful extensions, but are not required for the first implementation.

## 5. Diagnostics

A fitted partition should report at least:

- $F_\infty$ and $F_B$;
- retained-information eigenvalues of

$$
R=F_\infty^{-1/2}F_BF_\infty^{-1/2};
$$

- bin populations and effective sample sizes;
- performance on held-out data.

The fundamental numerical check is

$$
F_B\preceq F_\infty.
$$

For a bin with weights $w_i$, the effective sample size is $(\sum_i w_i)^2/\sum_i w_i^2$. Splitting one event's weight among identical copies leaves every information statistic unchanged; duplicating the event without splitting its weight doubles its information contribution.

## 6. Local nature of the method

The score is defined at a reference point $\theta_0$, so the optimized partition is locally optimal. Robustness across a wider parameter region should be evaluated explicitly when needed; multi-reference optimization can be added later.

## 7. Related work

The method builds on established ideas rather than claiming score-based compression itself as new:

- optimal observables and likelihood-score compression;
- Alsing & Wandelt, *Generalized massive optimal data compression* (2018), arXiv:1712.00012;
- Brehmer et al., local score estimation and SALLY/SALLINO (2018), arXiv:1805.00020 and arXiv:1805.12244;
- de Castro & Dorigo, *INFERNO* (2018), arXiv:1806.04743;
- Valassi, *Optimising HEP parameter fits via Monte Carlo weight derivative regression* (2020), arXiv:2003.12853;
- literature on Fisher-information-aware quantization for parameter estimation.

## 8. Proposed contribution

FisherBin's contribution is the combination of these ideas into a small, domain-independent tool:

1. formulate binning directly in arbitrary-dimensional score space;
2. use the exact Fisher-information-loss identity as the design and validation principle;
3. provide practical score-k-means and differentiable Voronoi optimizers for multiple parameters;
4. separate score estimation from bin optimization;
5. provide a reusable, tested implementation with explicit information-retention diagnostics.

The novelty claim should remain conservative: the value is the general formulation, practical algorithms, and high-quality reusable implementation rather than invention of score compression or Fisher-aware quantization themselves.
