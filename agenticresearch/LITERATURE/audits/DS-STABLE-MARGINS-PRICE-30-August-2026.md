# Targeted prior-art triangulation: DS-STABLE-MARGINS-PRICE (DS16)

Run 30 Aug 2026 by the DS-STABLE-MARGINS-COMPILE researcher session
(`protocols/literature.md`, per-theorem minimum), on the frozen DS16
statement (margin price + value funnel at arbitrary finite labelings,
(L)+(S), \(d_\psi=d_\lambda=1\), \(K\ge3\)) and its selection/compile
corollaries (`DS-STABLE-STATE-SELECTION`, `DS-PROFILED-COMPILE-CERTIFICATE`).
The packet requirement was to clear the round-3 snowball additions
(`LITERATURE/graph.json`, merged 30 Aug 2026); round 3 is explicitly **not**
a saturation claim (`LITERATURE/gaps.md`), and this triangulation reuses the
round-3 records plus the DS15-era retrievals — no new full-text fetches were
needed for a researcher-side pass. `literature_search_status` on all three
new claims stays `search_gap` pending a dedicated novelty search near
publication.

## Triangulation (six fields per source)

- **Silvey & Titterington (1973), *A geometric approach to optimal design
  theory*; Silvey, Titterington & Torsney (1978), *An algorithm for optimal
  designs on a finite design space*.** *(round 3; deeply_reviewed)*
  **Exact problem:** optimal approximate design measures — free weights on a
  fixed finite support; concave criteria (D, \(D_s\)) on a **convex**
  feasible set. **Exact result:** geometric D/\(D_s\) duality via Lagrangian
  duality; monotone convergent weight algorithms. **Objective:**
  \(\log\det\) and its \(D_s\) variants of \(\sum_i w_i x_ix_i^\top\).
  **Feasible set:** the simplex of design weights. **What transfers:** the
  ascent-to-stationarity frame and the sensitivity-function certificate idea
  — DS13's leverage bound is the partition-side stationarity certificate the
  DS16 compile verdict consumes. **What does not:** convexity. In
  approximate design the equivalence theorem makes first-order stationarity
  *global*, so "margins at stable non-global states" cannot even be posed
  there; hard partitions couple masses and conditional means on a
  combinatorial set, exchange-stable ≠ global
  (`DS-FINITE-GEOMETRY-FAILS`), and DS16's subject — the price and selection
  of non-global stable states — has no design-theory counterpart.
- **Silvey (1978), *Optimal design measures with singular information
  matrices*.** *(secondary only — primary unread, recorded in
  `LITERATURE/gaps.md`)* **Exact problem/result:** \(D_s\)-optimal design
  measures may carry singular full information, handled by
  generalized-inverse equivalence theory. **What transfers:** the design-side
  analogue of the DS15/DS16 degeneracy — a \(D_s\)-driven optimum shedding
  nuisance information is natural, and the pseudo-inverse (never ridge)
  treatment matches DS11's extension. **What does not:** population design
  measures; no finite stable states, no empirical uniformity, no
  margin-constrained optimum \(v^*(\kappa)\), no price.
- **Alsing & Wandelt (2019), *Nuisance hardened data compression for fast
  likelihood-free inference*.** *(round 3; deeply_reviewed)* **Exact
  problem:** continuous score-space summaries preserving POI information
  under nuisances. **Exact result:** locally/asymptotically
  Fisher-preserving projection using the nuisance Schur geometry. **What
  transfers:** the statistical reading of DS16's Track 1 — profile at the
  full-likelihood level, compress for the POI; the closest published
  antecedent of the projected efficient-score compile target. **What does
  not:** continuous summaries only — no hard quantizers, no Loewner
  domination over all partitions, no stability, no margins, no price.
- **Zhang, Blum, Kaplan & Lu (2018), *A fundamental limitation on maximum
  parameter dimension for accurate estimation with quantized data*.**
  *(round 3; deeply_reviewed)* **Exact problem/result:**
  quantization-induced FIM rank/identifiability ceilings. **What
  transfers:** the rank mechanism behind DS16's cardinality restatement
  (\(\operatorname{rank}(I_z)\le K-1\) on a centered sample; `n_bins >
  dimension`; commit `891bbf3`). **What does not:** distributed-estimation
  alphabet design, no partition optimization, no margin analysis.
- **Pollard (1981), *Strong consistency of k-means clustering* (with
  Graf–Luschgy (2000) for uniqueness classes).** *(DS15-era retrieval;
  verbatim)* **Exact problem:** empirical optimal \(k\)-point quantization
  of an i.i.d. sample. **Exact result:** a.s. value convergence and argmin
  consistency of empirical optimal centroid sets. **What transfers:** the
  uniform empirical machinery powering DS15 Proposition 5 and DS16 Lemma
  16.1's steps (iii)–(iv). **What does not:** no nuisance dimension, no
  profiled criterion, no constrained class; and the clustering-consistency
  literature works with measurable partitions/centroid sets, whereas DS16's
  rigidity must run over *groupings* of sample indices (duplicate atoms may
  split) — the gap Lemma DS16.1 closes with the nearest-centroid SSE
  comparison.

## Novelty axis

The specific DS16 objects — an empirical, uniform-over-labelings price
\(\delta(\kappa)\) for a feasibility/conditioning margin, and a
seed-independent value-funnel argument replacing global optimality — sit on
the "constrained/penalized quantization where a feasibility margin interacts
with the optimum" gap already recorded in `LITERATURE/gaps.md` after the
DS15 audit (practice-side evidence only: INFERNO remark, Erdmann et al.
2026 penalties, Wunsch et al. 2021; watch arXiv:2507.06226). Round 3 added
no theory community for it. Status: `search_gap` — a search gap is not
novelty (invariant 6).
