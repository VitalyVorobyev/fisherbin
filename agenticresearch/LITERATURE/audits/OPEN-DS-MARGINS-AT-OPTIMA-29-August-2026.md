# Targeted triangulation for OPEN-DS-MARGINS-AT-OPTIMA — 29 August 2026

Run before the DS15 proof (protocol `theorem.md` step C) by a delegated
web-search session; verification labels: *verbatim* (statement read in the
source), *secondary* (peer-reviewed source quoting the original, named),
*abstract* (publisher abstract only). Full search log (19 query strings,
per-source tables) in the session deliverable; the durable annotations live
in `topics/01` and `topics/04` under the keys named below.

The literature splits into two camps pulling in opposite directions, and the
\(D_s\)-binning question sits in the unoccupied intersection:

- **Distortion camp** (quantization/\(k\)-means): remote small cells are
  *penalized*. Graf–Luschgy Thm 4.1/4.2 (secondary): every cell of a
  population-optimal quantizer has positive mass — the deletion-vs-
  \(W_{K-1}\) mechanism DS15's rigidity lemma reuses. Pollard 1981
  (verbatim): empirical optima converge a.s. to the unique population
  optimum — the only classical template converting population margins into
  empirical-optima margins, and it needs uniqueness. Levrard 2015 (verbatim):
  \(p_{\min}\), \(B\), and the boundary-mass margin condition codify what
  (M2)/(M5) buy; always hypotheses on the law, never proven automatic.
  Kieffer 1983 (secondary, twice independently): scalar log-concave
  uniqueness — Gaussian covered; Liu–Pagès 2020 Lemma 10/Prop 11 close the
  1-D chain and give a positive-definite Hessian at the optimum.
- **Determinant camp** (optimal design, D-subsampling): extreme support
  points are *rewarded*. Sibson–Kenny 1975 (abstract): D-optimal weights
  bounded **above** by \(1/k\); no lower bound exists in print. Silvey 1978
  (secondary): \(D_s\)-optimal designs can carry **singular** full
  information — the design-side (M3) failure, handled there by generalized
  inverses. Wang–Yang–Stufken 2019 (verbatim): the D-determinant over an
  i.i.d. normal sample is maximized by extreme order statistics at
  per-point scale \(2\log n\) — the undiluted-mass premise of the
  extreme-cell heuristic.
- **Singleton phenomenology** (robust clustering): García-Escudero–Gordaliza
  1999 (abstract), Hennig 2004 (secondary, verbatim restatement 2023): a
  single far-enough point earns a one-point cluster at the exact fixed-\(K\)
  optimum — adversarial contamination, no i.i.d. rates.

## Confirmed gaps (searched 29 Aug 2026)

1. **Extreme-cell heuristic:** no published result addresses whether exact
   optimal partitions of an i.i.d. sample isolate the sample's extreme
   points, under any criterion, at any generality. The \(2\log N/N\) die-out
   computation appears nowhere.
2. **(M2) for determinant criteria:** no lower bound on cell masses at
   D/\(D_s\)-optimal partitions or designs.
3. **(M3):** only the adverse design-side analogue (Silvey); nothing at the
   partition level.
4. **(M5):** nothing for projected centroids under a profiled information
   metric.
5. **Fisher-information-preserving binning with margin analysis:** the
   score-function-quantizer literature (Venkitasubramaniam–Tong–Swami 2006)
   contains no cell-mass/degeneracy discussion.

All five gaps are what DS15 now fills for conditionally centered laws at
\(d_\psi=1\); the complement class is OP29.

## Consequence for the registry

`OPEN-DS-MARGINS-AT-OPTIMA.literature_search_status = search_gap` (the
theorem itself), with the transferable-template sources recorded on the node:
Pollard-1981, Kieffer-1983, Graf-Luschgy-2000, Levrard-2015, Silvey-1978.
New bibliography keys added 29 Aug 2026: Graf-Luschgy-2000, Levrard-2015,
Kieffer-1983, Liu-Pages-2020, Garcia-Escudero-Gordaliza-1999, Hennig-2004,
Wang-Yang-Stufken-2019, Sibson-Kenny-1975, Silvey-1978.
