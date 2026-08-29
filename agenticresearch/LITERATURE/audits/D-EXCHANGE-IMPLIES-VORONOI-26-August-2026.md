# Targeted audit for `D-EXCHANGE-IMPLIES-VORONOI` — 26 August 2026

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
