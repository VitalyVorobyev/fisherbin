# Independent prior-art triangulation: the DS18 audit

Run 31 August 2026 for the audit of `DS-NONCENTERED-GLOBAL-BASIN-TRANSFER`,
following the per-theorem minimum in `protocols/literature.md`. This is a
**fresh** theorem-targeted search by the auditing session; the researcher's
`LITERATURE/audits/OPEN-DS-MARGINS-NONCENTERED-31-August-2026.md` was read
only afterwards, as comparison material. It is not a field-saturation round.
The status stays `search_gap`, which is never a novelty assertion.

## What DS18 actually consumes

The audit's algebraic reduction (report §7) shows the theorem rests on five
separable pieces, and the search was pointed at each of them separately
rather than at the compound statement alone:

1. the nearest-codepoint reduction of a matrix criterion to a scalar
   quantization problem (uncentered second moments);
2. uniqueness of the optimal three-level scalar quantizer of
   \(\operatorname{Unif}[-1,1]\), a log-concave but **not strictly**
   log-concave law;
3. quantitative rigidity: near-optimal value forces a near-optimal partition;
4. almost-sure consistency of the empirical scalar optimum, uniformly over a
   compact codebook set, on a selection-independent event;
5. finite one-point (Hartigan) exchange stability and its relation to global
   optimality.

## Triangulation (six fields per source)

- **Kieffer (1983), *Uniqueness of locally optimal quantizer for log-concave
  density and convex error weighting function* (`Kieffer-1983`).**
  **Exact problem:** uniqueness of the locally optimal \(K\)-level scalar
  quantizer. **Exact result:** for a log-concave density and a convex,
  strictly increasing \(C^1\) error weight the locally optimal quantizer is
  unique, hence globally optimal, and Lloyd iterations converge to it.
  **Objective:** expected scalar error weight (squared error as the special
  case). **Feasible set:** \(K\)-level scalar quantizers / their codebooks.
  **What transfers:** exactly piece 2 — \(\operatorname{Unif}[-1,1]\) has a
  log-concave density, so DS18's scalar codebook uniqueness is *classical*,
  not new. **What does not:** nothing about a Schur-complement matrix
  functional, a nuisance block, partitions of \(\mathbb R^2\) that may depend
  on \(Z\), empirical transfer, or exchange stability.
- **Mease & Nair (2006), *Unique optimal partitions of distributions and
  connections to hazard rates and stochastic ordering*, Statistica Sinica
  16:1299–1312 (`Mease-Nair-2006`).** **Exact problem:** when is the optimal
  partition of a distribution unique. **Exact result:** uniqueness under
  log-concavity of the density, via likelihood-ratio ordering, plus an
  explicit counterexample refuting Eubank's weaker sufficient condition.
  **Objective:** within-cell squared error / equivalent partition criteria.
  **Feasible set:** interval partitions and their representatives.
  **What transfers:** piece 2 again, and the warning that the hypothesis must
  stay pinned to log-concavity of the density itself. **What does not:** the
  profiled criterion, the two-dimensional feasible set, and everything
  empirical.
- **Pollard (1981), *Strong consistency of \(k\)-means clustering*
  (`Pollard-1981`).** **Exact problem:** almost-sure convergence of empirical
  optimal quantizers/codebooks. **Exact result:** the empirical optimal
  distortion converges a.s. to the population optimum, and empirical optimal
  codebooks converge a.s. to the population optimal set (a single point when
  the optimum is unique). **Objective:** expected squared distance to the
  nearest codepoint. **Feasible set:** codebooks of size \(K\) and their
  Voronoi partitions. **What transfers:** piece 4 — DS18's
  \(\hat v_{3,N}\to8/27\) and the codebook limit are the classical statement,
  and its event is selection-independent, which is what carries DS18's
  "**every** sequence of global optimizers" quantifier. **What does not:**
  Pollard's optimizers minimise the distortion itself; DS18's optimizers
  maximise a *different* functional that merely dominates into the distortion
  problem, so the transfer needs DS18's own sandwich to connect them — the
  step no source supplies.
- **Rakhlin & Caponnetto (2006), *Stability of \(k\)-means clustering*
  (`Rakhlin-Caponnetto-2006`).** **Exact problem:** the geometry of
  almost-minimizers of the nearest-center risk. **Exact result:** for bounded
  sources the diameter of the population almost-minimizer set shrinks when
  the population minimizer is unique, and a covering-number uniform law
  transfers this to empirical minimizers. **Objective:** nearest-center
  squared-error risk. **Feasible set:** codebooks. **What transfers:** piece
  3 — this is the published template for DS18.1's strict isolation and for
  the empirical rigidity in DS18.2. **What does not:** their almost-minimizer
  is measured in codebook space, whereas DS18 needs isolation in the
  *decision distance* on partitions and starts from arbitrary
  \((X,Z)\)-measurable cells rather than nearest-center ones.
- **Telgarsky & Vattani (2010), *Hartigan's method: \(k\)-means clustering
  without Voronoi* (`Telgarsky-Vattani-2010`).** **Exact problem:** finite
  one-point relocation for \(k\)-means and its fixed points. **Exact result:**
  Hartigan terminals are a strict subset of Lloyd terminals and need not be
  Voronoi partitions; the induced "circlonoi" partition is strictly tighter.
  **Objective:** finite within-cluster squared error. **Feasible set:**
  labelings under one-point moves. **What transfers:** piece 5, and the
  reason DS18 must derive exchange stability from *global* finite optimality
  rather than from the population cuts — the audit's independent
  reproduction of the \(N=4\) boundary fixture is exactly that phenomenon.
  **What does not:** no matrix criterion, no nuisance block, no feasibility
  convention for singular destinations, no population law.
- **de Castro & Dorigo (2019), *INFERNO: inference-aware neural optimisation*,
  Comput. Phys. Commun. 244:170 (`deCastro-Dorigo-2019`).** **Exact problem:**
  learn a summary statistic that minimises the expected uncertainty on a
  parameter of interest in the presence of nuisance parameters.
  **Exact result:** a differentiable Asimov-likelihood loss built from the
  inverse Hessian (hence a profiled-Fisher surrogate) of a softened histogram
  outperforms classifier-based summaries when nuisances matter.
  **Objective:** the profiled variance/Fisher block of a binned Poisson
  likelihood. **Feasible set:** neural summaries feeding a *soft*,
  differentiable histogram. **What transfers:** the objective family — this is
  the closest applied statement of DS18's criterion, and it confirms that the
  nuisance-aware binning target is the one practitioners want.
  **What does not:** everything DS18 is about — hard partitions, exactness,
  uniqueness, strict isolation, empirical-to-population transfer, and finite
  exchange stability. INFERNO reports no optimality theorem at all.

## Search rounds and counts

| Round | Query family | Candidates inspected | New relevant | Outcome |
|---|---|---|---|---|
| 1 | scalar quantizer uniqueness, log-concave, Kieffer/Trushkin/Fleischer | 9 | 0 new | confirms `Kieffer-1983`, `Mease-Nair-2006`, `Liu-Pages-2020` already held |
| 2 | Fisher information + nuisance + Schur complement + binning | 10 | 0 | quantum-metrology and profile-likelihood hits only; no partition feasible set |
| 3 | strong consistency of empirical optimal quantizers | 10 | 0 new | confirms `Pollard-1981`, `Graf-Luschgy-2000`, `Liu-Pages-2020` |
| 4 | inference-aware binning with nuisance parameters (HEP) | 8 | 1 (`deCastro-Dorigo-2019`, previously annotated without a key) | soft histograms, no theorem |
| 5 | Hartigan one-point exchange vs global optimality | 10 | 0 new | confirms `Telgarsky-Vattani-2010` |
| 6 | unique optimal partitions of distributions | 9 | 0 new | confirms `Mease-Nair-2006` |
| 7 | consistency of empirical maximizers of Fisher information over partitions | 18 | 0 | no source with this feasible set; the compound gap |
| 8 | near-optimal clustering rigidity / margin stability | 10 | 0 new | confirms `Rakhlin-Caponnetto-2006`, `Levrard-2015` |
| 9 | quantizer design maximising Fisher information with nuisance parameters | 10 | 0 new | confirms `Venkitasubramaniam-Tong-Swami-2006/2007`; scalar, no nuisance block |

Rounds 1, 3, 5, 6, 8 and 9 returned overwhelmingly material the workspace
already holds — the saturation signal of `protocols/literature.md` for these
sub-problems. Round 7, the compound query, returned nothing with the right
feasible set.

## Attribution findings against the registered node

The registered `literature` list of `DS-NONCENTERED-GLOBAL-BASIN-TRANSFER` is
`Venkitasubramaniam-Tong-Swami-2006`, `Liu-Pages-2020`, `Sabin-Gray-1986`,
`Serinko-Babu-1992`, `Telgarsky-Vattani-2010`. Two defects:

1. **Under-attribution.** The four steps DS18 leans on hardest — scalar
   uniqueness, almost-minimizer rigidity, empirical scalar consistency, and
   one-dimensional contiguity — have direct antecedents *already in this
   project's own bibliography* (`Kieffer-1983`, `Mease-Nair-2006`,
   `Rakhlin-Caponnetto-2006`, `Pollard-1981`, `Fisher-1958`,
   `Graf-Luschgy-2000`) that the node does not cite. The audit adds them.
2. **Mis-scoped uniqueness citation.** `Liu-Pages-2020` is cited for the
   scalar uniqueness/conditioning DS18 needs, but its Proposition 11
   (positive-definite distortion Hessian at the optimum) assumes **strictly**
   log-concave densities, and `Fleischer-1964`'s uniqueness likewise assumes
   strict log-concavity. \(\operatorname{Unif}[-1,1]\) is log-concave but not
   strictly so, so that route does not cover the named law. `Kieffer-1983`
   and `Mease-Nair-2006` do cover it (log-concavity of the density suffices).
   For the conditioning statement the audit supplies the missing fact itself:
   the exact distortion Hessian at the optimal codebook \((-2/3,0,2/3)\) is
   \(\bigl[\begin{smallmatrix}1/2&-1/6&0\\-1/6&1/3&-1/6\\0&-1/6&1/2\end{smallmatrix}\bigr]\)
   with exact minimum eigenvalue \(1/6>0\)
   (`AUDITS/artifacts/AUDIT-DS-NONCENTERED-GLOBAL-BASIN-TRANSFER-001/population.json`).

## Combined-theorem search gap (independently reproduced)

No located source combines: a non-centered interest/nuisance score law; a
Schur-complement (profiled Fisher) objective over hard partitions of score
space; a unique strict population attainer with quantitative isolation in
decision distance; almost-sure transfer to **every** sequence of exact finite
global optimizers on one selection-independent event; and exact finite
one-point exchange stability with explicit rational margins. The auditing
session reaches the same conclusion as the research session, by an
independent query path. Recorded as `literature_search_status: "search_gap"`
on both the target and the audit node; it is a coverage statement, never a
novelty claim.

## Gaps this search did not close

- Communities not swept here: statistical-design literature on
  \(D_s\)-optimal designs with singular information matrices beyond
  `Silvey-1978`; the stratification/optimal-grouping literature in survey
  sampling (Dalenius–Hodges and descendants), which optimises a different
  variance functional over interval strata and could hold a rigidity lemma
  in our exact form.
- No forward-citation traversal was run on `Rakhlin-Caponnetto-2006` or
  `Mease-Nair-2006`; a saturation round for the *rigidity* sub-problem is
  recorded in `LITERATURE/gaps.md`.
