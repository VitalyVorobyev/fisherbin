# Targeted prior-art triangulation: DS18 exact non-centered basin transfer

Run 31 August 2026 for the frozen claim
`DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`, following the per-theorem minimum in
`protocols/literature.md`. The search combined score-function/Fisher
quantization, scalar optimal quantization, empirical optimal-codebook
consistency, generalized Lloyd convergence, and Hartigan one-point exchange.
It is a theorem-targeted search, not a field-saturation round. The status is
`search_gap`, never a novelty assertion.

## Triangulation (six fields per source)

- **Venkitasubramaniam, Tong & Swami (2006), *Score-Function Quantization for
  Distributed Estimation*.** **Exact problem:** design a finite-alphabet
  quantizer to preserve Fisher information for parameter estimation using
  score functions. **Exact result:** the quantized score conditional means
  determine the retained Fisher information, leading to score-space
  quantizer design. **Objective:** scalar Fisher-information retention (and
  its equivalent score-distortion formulation). **Feasible set:** finite
  scalar quantizers for a distributed observation. **What transfers:** the
  conditional-score identity underlying ScoreQuant's cell-moment objective
  and the legitimacy of optimizing in score space. **What does not:** no
  nuisance Schur complement, endogenous efficient-score tilt, exact
  non-centered law, global-isolation equality chain, empirical optimizer
  transfer, or one-point exchange statement.
- **Liu & Pagès (2020), *Convergence rate of optimal quantization and
  application to the clustering performance of the empirical measure*.**
  **Exact problem:** convergence of empirical optimal quadratic quantizers
  to population optimal codebooks. **Exact result:** quantitative clustering
  performance bounds under uniqueness/regularity; for strongly unimodal
  scalar laws the stationary/optimal quantizer is unique, with a
  positive-definite distortion Hessian under strict log-concavity.
  **Objective:** expected squared Euclidean distortion. **Feasible set:**
  finite codebooks and their Voronoi partitions. **What transfers:** the
  classical uniqueness/rigidity and empirical-consistency template used to
  interpret the scalar uniform upper problem. **What does not:** DS18 uses a
  profiled matrix functional rather than additive distortion and proves its
  own scalar equal-third/equality structure; the source supplies neither the
  Schur-complement sandwich nor exact finite exchange stability.
- **Sabin & Gray (1986), *Global convergence and empirical consistency of the
  generalized Lloyd algorithm*.** **Exact problem:** convergence of
  generalized Lloyd iterations and consistency of empirical fixed-point
  quantizers. **Exact result:** under convex source-independent additive
  distortions, empirical/fixed-point quantizer sets converge to their
  population counterparts under the paper's regularity conditions.
  **Objective:** additive expected distortion. **Feasible set:** generalized
  nearest-neighbor/centroid quantizers. **What transfers:** the closest
  structural precedent for moving from a population isolated quantizer to an
  empirical quantizer set. **What does not:** no profiled Fisher information,
  nuisance block, variational sandwich, global finite combinatorial
  optimizer squeeze, or ordinary one-point exchange domain.
- **Serinko & Babu (1992), *Weak limit theorems for univariate k-mean
  clustering under a nonregular condition*.** **Exact problem:** asymptotics
  of empirical univariate k-means split points, including a singular-Hessian
  optimum. **Exact result:** the regular case has the classical root-n limit;
  a unique nonregular double-exponential two-means optimum has an n^(1/4)
  limit after a slow/fast decomposition. **Objective:** scalar between-cell
  variance/equivalently squared-error k-means. **Feasible set:** ordered
  cutpoints and their interval cells. **What transfers:** the split-function
  formulation and the warning that empirical transfer depends on the
  population optimum's regularity/isolation. **What does not:** no
  profiled-information lower/upper squeeze, no off-(L) construction, and no
  theorem about every global optimizer's exact finite exchange stability.
- **Telgarsky & Vattani (2010), *Hartigan's Method: k-means Clustering without
  Voronoi*.** **Exact problem:** finite one-point Hartigan relocation for
  k-means and its relationship to Voronoi/Lloyd structure. **Exact result:**
  Hartigan terminal clusterings need not be Voronoi clusterings, and the
  paper analyzes convergence/complexity of the relocation method.
  **Objective:** finite-sample within-cluster squared error. **Feasible set:**
  labeled finite partitions under one-point moves. **What transfers:** the
  distinction between global optimality, exact relocation stability, and a
  Lloyd fixed point; this is precisely why DS18 derives stability from global
  finite optimality rather than from population cuts. **What does not:** no
  nuisance/profiled criterion, population law, almost-sure transfer, or
  boundary-noise theorem.

## Combined-theorem search gap

No located source combines all of the following: a non-centered
interest/nuisance score law; a Schur-complement Fisher objective; a unique
strict full-rank population quantizer obtained through a profiled-to-scalar
variational sandwich; almost-sure convergence of every finite global regular
optimizer; and exact finite ordinary one-point exchange stability. The five
sources separately cover score-Fisher identities, scalar uniqueness and
empirical consistency, generalized Lloyd set convergence, nonregular split
asymptotics, and Hartigan relocation. Accordingly DS18 remains
`literature_search_status: search_gap`; publication review must repeat the
search claim-by-claim.
