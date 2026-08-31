# Targeted prior-art triangulation: DS17 (DS-STABLE-BASINS)

Run 31 Aug 2026 by the DS-STABLE-BASINS researcher session
(`protocols/literature.md`, per-theorem minimum) on the frozen DS17
statements: the conditional-centering obstruction
(`DS-STABLE-BASINS-CENTERED-OBSTRUCTION`), the LCM merged-branch
classification (`DS-STABLE-BASINS-LCM-CLASSIFICATION`), and the fixed-point
gate (`DS-STABLE-BASINS-FIXED-POINT-GATE`). Retrieval was delegated
(verified metadata below; anything the retrieval could not verify is marked);
triangulation judgments are the researcher's. Registration: round 4 of
`LITERATURE/graph.json`; cluster annotation in
`topics/04-vector-quantization.md`. `literature_search_status` on all DS17
claims stays `search_gap` pending a dedicated novelty search near
publication; a search gap is not novelty (invariant 6).

## Triangulation (six fields per source)

- **Tarpey, Li & Flury (1995), *Principal points and self-consistent points
  of elliptical distributions*, Ann. Statist. 23(1):103–112.** *(abstract
  summarized; primary proof not read — no technique-transfer claim)*
  **Exact problem:** the linear span of \(k\) self-consistent points
  (each equal to the conditional mean of its nearest-point cell) of an
  elliptical law. **Exact result:** a dimension-\(q\) span of self-consistent
  points is spanned by top principal-component eigenvectors; principal points
  align with the principal subspace (confirming Flury's 1990 conjecture).
  **Objective:** self-consistency (a fixed-point condition), with principal
  points the globally optimal special case. **Feasible set:** \(k\)-tuples in
  \(\mathbb R^p\). **What transfers:** the *shape* of the theorem — a
  self-consistency hypothesis plus a symmetry/centering hypothesis forces a
  degenerate, aligned configuration; this is the nearest published cousin of
  DS17.1's "tilt-consistency + (L) forces a zero nuisance block".
  **What does not:** no nuisance/profiled information block (their conclusion
  is about the span's dimension, not an information matrix); no
  self-regenerating projection coefficient (\(\beta=B^*(I_q)\)) — their
  geometry is fixed by the covariance, DS17's tilt is itself a fixed-point
  variable; their hypothesis is ellipticity of the law, DS17's is the
  conditional-mean orthogonality (L), which holds far beyond elliptical laws;
  and DS17's proof runs through a conditional Chebyshev association
  inequality, about which no counterpart claim in their proof is made (unread).
- **Flury (1990), *Principal points*, Biometrika 77(1):33–41.** *(abstract
  level; primary text paywalled)* **Exact problem/result:** population
  \(k\)-means points of a \(p\)-variate law; existence; the
  Gaussian/elliptical programme and the principal-subspace conjecture.
  **Objective:** \(E\min_j\|X-\xi_j\|^2\). **Feasible set:** point
  \(k\)-tuples. **What transfers:** the existence-direction baseline the
  obstruction contrasts against — in plain quantization, optimal/self-
  consistent configurations exist under moment conditions; DS17 shows the
  profiled analogue's margin-carrying branch is empty on class (L).
  **What does not:** no partition-valued information objective, no nuisance,
  no obstruction content.
- **Tarpey & Flury (1996), *Self-consistency: a fundamental concept in
  statistics*, Statist. Sci. 11(3):229–243.** *(definition verified from the
  publisher abstract; full text not retrieved)* **Exact problem/result:**
  the unifying definition \(E[X\mid Y]=Y\) covering principal components,
  curves, points. **What transfers:** vocabulary and the conceptual frame:
  DS17's tilt-consistent strip rules are self-consistent summaries in exactly
  this sense, with the extra twist that the projection defining the summary
  is itself regenerated. **What does not:** survey; the load-bearing
  elliptical theorem is Tarpey–Li–Flury 1995 (misattribution avoided).
- **Serinko & Babu (1992), *Weak limit theorems for univariate k-mean
  clustering under a nonregular condition*, J. Multivariate Anal.
  41(2):273–296.** *(primary PDF read verbatim by the retrieval)*
  **Exact problem:** asymptotics of empirical 1-D \(k\)-means split points.
  **Exact result:** with the split-function formulation over ordered
  cutpoints and a unique population maximizer, a singular Hessian at the
  optimum (double exponential, \(k=2\)) yields \(n^{1/4}\) rates via a
  slow/fast subspace decomposition; regular case recovers the \(n^{1/2}\)
  CLT (Hartigan/Pollard). **Objective:** between-value of 1-D interval
  partitions — structurally the closest object to DS17's
  \(\operatorname{law}(T_\beta)\) Lloyd branches. **Feasible set:** the
  ordered-cutpoint simplex. **What transfers:** the 1-D interval-partition
  formulation and first-order (Lloyd) conditions DS17.1a's decomposition
  reuses; the precedent that degeneracy *at* a self-consistent optimum is a
  real phenomenon with real consequences. **What does not:** their optimum
  is global and assumed unique; degeneracy is a property of one example law,
  described, not forced — DS17 proves a class-wide forcing theorem; no
  nuisance block, no tilt, no exchange stability.
- **Adjacent, already registered (reused, not re-searched):**
  `Rakhlin-Caponnetto-2006` (codebook rigidity, powering the DS14/DS16
  uniform-law machinery DS17.0 intersects), `Telgarsky-Vattani-2010`
  (Hartigan terminals vs Voronoi states — why DS17.2 must consume exact
  stability through DS14 rather than assuming geometric structure),
  `Blanchard-Jaffe-Zhivotovskiy-2025` (constraint-restored consistency — the
  constrained-solver contrast for OP7 under the DS17 constraints).

## Obstruction-shaped search (negative)

Five queries were run for anything resembling the obstruction itself
("self-consistent points" nonexistence/collinear; principal points collinear;
self-consistent quantizer + linear conditional expectation; Voronoi
self-consistency fixed-point nonexistence; quantization fixed point +
profiled Fisher information). Nothing matching the combination —
a class-wide nonexistence theorem for self-consistent partitions with a
nondegenerate secondary information block under a conditional-mean
orthogonality hypothesis — was found. Nearest miss: Tarpey–Li–Flury's forced
alignment (above). Status: `search_gap` maintained on all three DS17 claims.

## Novelty axis

The DS17-specific objects — a self-regenerating tilt as the fixed-point
variable, the tilt-residual identity
\(B^*(I_q)-\beta=E[h(T_\beta)S_\lambda]/I_{\lambda\lambda}\), and the
conditional-centering class as the obstruction hypothesis — sit between the
self-consistency literature (no information block, no tilt) and the
optimal-design/nuisance literature recorded in the DS16 audits (no hard
partitions, no fixed points). No community for the combination surfaced in
rounds 2–4.
