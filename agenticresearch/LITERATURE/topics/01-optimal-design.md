# 1. Optimal experimental design backbone

> Curated theorem-level annotations. Machine records for the citation graph
> live in `graph.json`; `BIBLIOGRAPHY.md` (generated) maps every registry
> bibliography key to the heading that annotates it.

## Kiefer & Wolfowitz (1960) — D-equivalence theorem

**Key:** Kiefer-Wolfowitz-1960

**Paper:** *The Equivalence of Two Extremum Problems*  
**Result:** in approximate linear design, D-optimality is equivalent to a pointwise maximum-variance/sensitivity condition.  
**Why important:** establishes \(M^{-1}\) as the natural D sensitivity metric and provides the archetype for a global optimality certificate.  
**Does not solve:** partition-induced information, score centroids, finite label relocation.

- PDF: https://www.cambridge.org/core/services/aop-cambridge-core/content/view/B8B0626C11F52B0FD8C67C5D54BDDD43/S0008414X00010002a.pdf/the-equivalence-of-two-extremum-problems.pdf
- DOI: https://doi.org/10.4153/CJM-1960-030-4

## Wynn (1970) — sequential D-optimal design construction

**Key:** Wynn-1970

**Paper:** *The Sequential Generation of D-Optimum Experimental Designs*  
**Result:** sequentially add points chosen by sensitivity; convergence and generalized-variance bounds.  
**Use:** algorithmic/sensitivity analogy.

- DOI: https://doi.org/10.1214/aoms/1177696809

## Wynn (1972) — D and \(D_s\) construction

**Key:** Wynn-1972

**Paper:** *Results in the Theory and Construction of D-Optimum Experimental Designs*  
**Result:** extends generation ideas to \(D_s\), selected parameter subsets, and discrete designs.  
**Use:** primary historical \(D_s\) source.

- DOI: https://doi.org/10.1111/j.2517-6161.1972.tb00896.x

## Whittle (1973) — general concave criteria

**Key:** Whittle-1973

**Paper:** *Some General Points in the Theory of Optimal Experimental Design*  
**Result:** general concave criterion/equivalence viewpoint; consequences for iterative construction and transformations including \(D_s\)-related ideas.  
**Use:** closest classical template for asking which parts of D geometry extend to other criteria.

- DOI: https://doi.org/10.1111/j.2517-6161.1973.tb00944.x

## Kiefer (1974) — general equivalence theory

**Key:** Kiefer-1974

**Paper:** *General Equivalence Theory for Optimum Designs (Approximate Theory)*  
**Result:** broad \(\Phi\)-optimal theory including D, L, E and other criteria.  
**Use:** generic sensitivity/supergradient machinery.

- DOI: https://doi.org/10.1214/aos/1176342810

## Fedorov (1972) — optimal experiments and exchange

**Book:** *Theory of Optimal Experiments*  
**Use:** exact/discrete design, exchange construction, rank-update thinking.

- Book page: https://books.google.com/books?id=v6vTAvqGny4C

## Näther & Reinsch (1981) — \(D_s\) equivalence

**Key:** Nather-Reinsch-1981

**Paper:** *D_s-optimality and Whittle's equivalence theorem*  
**Result:** \(D_s\) equivalence including singular cases; simplified sufficient conditions.  
**Use:** nuisance/Schur-complement sensitivity.

- DOI: https://doi.org/10.1080/02331888108801591

## Pukelsheim — modern reference

**Book:** *Optimal Design of Experiments*  
**Use:** matrix criteria, efficiency, equivalence, geometric formulation.

- SIAM chapter DOI: https://doi.org/10.1137/1.9780898719109.ch7

## Nguyen & Miller (1992) — exchange algorithms

**Paper:** *A review of some exchange algorithms for constructing discrete D-optimal designs*  
**Use:** historical terminology and practical exchange design.

- DOI: https://doi.org/10.1016/0167-9473(92)90064-M

## Huan, Jagalur & Marzouk (2024) — modern OED survey

**Paper:** *Optimal Experimental Design: Formulations and Computations*  
**Use:** current map of D, \(D_A/D_s\), E, Bayesian/nonlinear OED, computation.

- PDF: https://www.cambridge.org/core/services/aop-cambridge-core/content/view/38BBD0DC1A0386FDF306B6C0167DF7D9/S0962492924000023a.pdf/optimal-experimental-design-formulations-and-computations.pdf

---

## Design-side margins: weight bounds, singular \(D_s\) designs, extreme-point selection (29 Aug 2026)

**Key:** Sibson-Kenny-1975, Silvey-1978, Wang-Yang-Stufken-2019

**Papers:** Sibson & Kenny (1975, JRSS-B 37:288–292): in a D-optimal design,
either the support is saturated with equal weights \(1/k\), or every weight
is strictly below \(1/k\) (Atwood's inequality) — the design-side mass bound
runs **upward**; no published lower bound on D/\(D_s\)-optimal support
weights was found (OP28 audit). Silvey (1978, Biometrika 65:553–559,
secondary-verified): \(D_s\)-optimal design measures can carry **singular**
full information matrices, handled by generalized-inverse equivalence
theory — the design-side analogue of DS15's (M3) failure at \(D_s\)-optimal
partitions, and independent support for the project-don't-ridge invariant.
Wang, Yang & Stufken (2019, JASA 114): the D-determinant over an i.i.d.
sample is maximized by extreme order statistics, with per-point information
scale \(2\log n\) for normal covariates (Thm 2, 6) — the undiluted-mass side
of the extreme-cell heuristic.

**Use:** prior-art frame for DS15: determinant criteria reward extremes and
tolerate singular information at optima, in contrast to distortion criteria
(topic 4), which penalize both. The binning problem sits in the intersection:
mass dilution (\(W_b\mu_b\mu_b^\top/W_b\)-structure) restores the distortion
side's (M2) while keeping the design side's (M3) failure.

**Does not transfer:** design measures are free of the conditional-mean
coupling; exact-design theory has no equivalence theorem; nothing controls
the partition-restricted optimum.
