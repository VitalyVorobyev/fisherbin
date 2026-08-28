# DS-POPULATION-BRIDGE — finite→population theory for profiled \(D_s\)

**Programme:** P1 (OPEN_PROBLEMS.md) · **Opened:** 28 Aug 2026 · **Status:** completed 28 Aug 2026

## Goal

Determine what statistical guarantee connects finite profiled-\(D_s\)
solutions (exchange-stable or global) to population efficient-score
quantizers: prove a bridge theorem under explicit regularity assumptions, or
reduce the question to precisely stated unresolved conditions.

## Outcome

**Both stop conditions "proved under explicit assumptions" and "reduced to a
precise unresolved condition" were hit.** Four theorems and two exact
counterexamples:

- **DS11 (variational form).** \(S_\psi^+(I_q)=\min_B\operatorname{Var}(E[S_\psi-BS_\lambda\mid Z])\)
  — extends the profiled objective to singular nuisance blocks, gives exact
  refinement-neutrality characterization, re-derives efficient-score
  domination with its exact gap
  \((B^*_{\rm full}-B^*_q)I^q_{\lambda\lambda}(\cdot)^\top\), and settles the
  fixed-\(q\) and \(K\to\infty\) parts of OP6.
- **DS12 (population geometry, OP5).** Bounded-packet stationarity ⟺ a.e.
  nearest projected centroid in the \(S_\psi(I_q)^{-1}\) metric on the
  efficient projection; deployability iff projected centroids separate and
  tie sets are null. Stationarity does *not* force separation
  (`CE-DS-POP-WASTED-CELLS-001`).
- **DS13 (leverage bound).** Exchange stability implies
  \(s_{aa}-s_{bb}\le w_i\,q_{aa}q_{bb}\) exactly — no balancedness needed;
  0 violations in 2,738 exact checks.
- **DS14 (conditional bridge, OP4).** Under atomlessness, a slab margin, and
  mass/conditioning/separation margins along the sequence: exchange-stable
  finite solutions geometrize (vanishing companion-rule disagreement),
  subsequential limits are self-consistent population-stationary
  efficient-Voronoi quantizers with convergent values, and global optima
  converge to the margin-compatible population geometric optimum. A
  merged-rule variant drops the separation margin.
- **The precise unresolved condition is OP28** (new node
  `OPEN-DS-MARGINS-AT-OPTIMA`): the margins are *not* automatic — exact
  global optima at \(N\le18\) regularly carry singleton cells, and
  `CE-DS-DEGENERATE-GLOBAL-TIE-001` is a 31-fold exactly tied global optimum
  with coincident projected centroids (only its reduced bipartition is
  identified).

Library consequence: `compile_quantizer` for profiled criteria remains
correctly refused; DS14 (post-audit, plus OP28 progress) specifies exactly
what a future conditional compile bridge would return: the companion
efficient-Voronoi rule with margin diagnostics, merged along coincident
projected centroids.

## Artifacts

- `KNOWN_RESULTS.md` DS10–DS14 (rewritten/new), DS7 pointer, C2 unchanged
- `CLAIMS.json`: OPEN-DS-POP-COMMON-METRIC, OPEN-DS-FINITE-POP-BRIDGE,
  OPEN-DS-DOMINATION-EQUALITY promoted; new DS-PROFILED-VARIATIONAL,
  DS-EXCHANGE-LEVERAGE-BOUND, DS-GLOBAL-TIE-DEGENERACY, DS-POP-WASTED-CELLS,
  OPEN-DS-MARGINS-AT-OPTIMA (102 nodes)
- `COUNTEREXAMPLES/CE-DS-DEGENERATE-GLOBAL-TIE-001.json`,
  `COUNTEREXAMPLES/CE-DS-POP-WASTED-CELLS-001.json` + README entries
- `py/ds_population_bridge.py` (trend/analyze/leverage/degenerate modes)
- `NUMERICAL_EVIDENCE.md` rows N-DS-LEVERAGE, N-DS-BRIDGE-TREND
- `tests/test_research_claims.py::test_global_profiled_ds_optimum_can_be_a_degenerate_tie_class`,
  `::test_symmetric_wasted_cells_defeat_the_efficient_semimetric_rule`
- `LITERATURE.md` §4 expanded (Pollard cluster, Graf–Luschgy, Sabin–Gray,
  epi-convergence templates, Levrard margins; determinant-criterion
  consistency confirmed as a search gap)
- `OPEN_PROBLEMS.md`: OP4/OP5/OP6 retired, OP28 opened
- Follow-up: `WORK/active/AUDIT-DS-POPULATION-BRIDGE.md` (independent audit)

## Next dependency-blocking question

OP28: do the DS14 margins hold asymptotically at finite \(D_s\) optima for
light-tailed atomless laws? (The \(\sim2\log N/N\) extreme-cell heuristic
says yes for Gaussian tails; the \(N\le18\) evidence says not yet.)
