# Independent prior-art audit: DS16 stable margins and compile verdict

Run 30 August 2026 by the `AUDIT-DS-STABLE-MARGINS-COMPILE` session after the
three target statements were frozen. This search is independent of
`LITERATURE/audits/DS-STABLE-MARGINS-PRICE-30-August-2026.md`; that file was
used only for a final diff of coverage and conclusions.

**Claims:** `DS-STABLE-MARGINS-PRICE`, `DS-STABLE-STATE-SELECTION`,
`DS-PROFILED-COMPILE-CERTIFICATE`

## Query log

Primary-source searches used the standing terminology fan-out plus five
targeted axes:

1. `near optimal k-means quantizer uniqueness excess distortion convergence
   partitions theorem`, `approximate minimizers empirical k-means consistency`,
   `near optimal partitions symmetric difference convergence`;
2. `constrained balanced k-means consistency no asymptotic cost`, `minimum
   cell mass population consistency`, and forward checks from arXiv:2507.06226;
3. `Hartigan exchange stable local minima k-means convergence`, `one point
   relocation stable clustering`, and the Telgarsky--Vattani citation cluster;
4. `singular Ds optimal design measures`, `margin constrained Ds design`, and
   the Silvey--Titterington design lineage;
5. `nuisance hardened score compression`, `profiled Fisher hard quantization`,
   `Schur complement partition margin`, and `efficient score compile rule`.

Primary papers or official proceedings were opened whenever available. The
Silvey (1978) primary abstract was accessible but the theorem text remained
paywalled; no conclusion below relies on the inaccessible details.

## Six-field triangulation

### Rakhlin & Caponnetto (2006), *Stability of K-Means Clustering*

**Exact problem.** Empirical-risk minimization over the class of nearest-center
squared-error functions for bounded Euclidean data. **Exact result.** Their
§4 defines population almost-minimizers; under a unique population minimizer,
the diameter of that set tends to zero. A covering-number bound makes the risk
class uniform Glivenko--Cantelli, transferring the result to empirical
minimizers and data-perturbation stability. **Objective.** Additive scalar
within-cluster SSE. **Feasible set.** Bounded codebooks/nearest-center risk
functions, not arbitrary index groupings. **Transfers.** This is direct prior
art for the compact-codebook and uniform-law core of DS16.1. DS16 should not
present the near-optimal-codebook rigidity principle as new. **Does not
transfer.** It does not close the arbitrary-grouping gap, handle unbounded laws
under only a second moment, control signed nuisance moments, or prove the
profiled-(D_s) margin price and funnel.

### Telgarsky & Vattani (2010), *Hartigan's Method: k-means Clustering without Voronoi*

**Exact problem.** Greedy one-point relocation for finite ordinary k-means.
**Exact result.** Strict cost decrease, finite structural properties of
Hartigan terminal partitions, and quantitative separation from the induced
Voronoi partition. **Objective.** Additive within-cluster SSE. **Feasible
set.** Finite hard partitions under one-point moves. **Transfers.** It is the
nearest exchange-stability precedent and confirms that one-point terminals are
not interchangeable with Lloyd/Voronoi states. **Does not transfer.** No
Schur/profiled objective, nuisance block, information price, empirical-to-
population theorem, or seed-selection law.

### Blanchard, Jaffe & Zhivotovskiy (2026), *Consistency and inconsistency in k-means clustering*

**Exact problem.** Empirical k-means under weak moments, including balance
constraints. **Exact result.** Unique population optimal centers do not alone
ensure empirical-center convergence with only a first moment; extreme cluster
imbalance causes failures, while imposed lower balance restores forms of
consistency (EJS 20(2):3291--3334; arXiv v2). **Objective.** Additive k-means
distortion. **Feasible set.** Unconstrained or minimum-cardinality empirical
clusters. **Transfers.** It makes mass control and uniform-integrability steps
in DS16.1 visibly load-bearing and is the closest constrained-clustering
comparison for OP30. **Does not transfer.** Its constraint repairs a tail/
imbalance pathology; it neither prices a nuisance-information constraint nor
proves existence of margin-compatible exchange-stable sequences.

### Silvey (1978), *Optimal design measures with singular information matrices*

**Exact problem.** Necessary/sufficient-style conditions for optimal design
measures with singular information, including (D_s). **Exact result.** The
primary abstract states a generalized-inverse sufficient condition for a wider
convex criterion and discusses necessity. **Objective.** Convex optimal-design
criteria, including (D_s). **Feasible set.** Design weights on a convex
simplex. **Transfers.** Singular full information at a (D_s) solution is an
established design-side phenomenon. **Does not transfer.** Convex free design
weights have no hard-partition grouping, empirical exchange states, constrained
value (v^*(\kappa)), or value-funnel theorem.

### Alsing & Wandelt (2019), *Nuisance hardened data compression for fast likelihood-free inference*

**Exact problem.** Continuous low-dimensional summaries for likelihood-free
inference with nuisance marginalization. **Exact result.** A local/asymptotic
projection produces one nuisance-hardened summary per POI and preserves Fisher
information to leading order. **Objective.** Continuous Fisher-aware
compression. **Feasible set.** Smooth real-valued summaries, not hard cells.
**Transfers.** It is direct representation-level precedent for DS16's projected
efficient-score deployment track. **Does not transfer.** No finite alphabet,
in-bin profiling, all-quantizer upper bound, compile certificate, stability, or
margin price.

## Search verdict

The search found direct prior art for the **codebook rigidity ingredient** of
Lemma DS16.1 (Rakhlin--Caponnetto, supplementing Pollard) and for ordinary
Hartigan terminal geometry, so the DS16 proof and report must attribute those
ingredients explicitly. It found no source proving the combined theorem:
uniform-over-groupings nuisance-margin price, the profiled-(D_s) value funnel,
or the certificate-gated hard-quantizer deployment consequence.

All three target nodes therefore remain `literature_search_status: search_gap`.
That is a claim-specific search gap, not a novelty or field-saturation claim.
