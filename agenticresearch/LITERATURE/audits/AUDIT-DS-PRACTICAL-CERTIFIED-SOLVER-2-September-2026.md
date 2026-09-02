# Independent prior-art triangulation: the DS19 audit

**Key:** Toledo-1993, Megiddo-1983, Gronlund-etal-2017, Wang-Song-2011, Pukelsheim-Titterington-1983, Carstensen-1983

Run 2 September 2026 for `AUDIT-DS-PRACTICAL-CERTIFIED-SOLVER`, the
independent audit of `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER` and its DS19
components, following the per-theorem minimum of `protocols/literature.md`.
This is a **fresh** theorem-targeted search by the auditing session; the
researcher's `LITERATURE/audits/OPEN-DS-PRACTICAL-CERTIFIED-SOLVER-1-September-2026.md`
was read only afterwards as comparison material, and its four sources
(Li–Mathias, Silvey–Titterington, Fisher, Gajjar–Radhakrishnan) are treated
here as comparison material, not as audit conclusions. It is not a
citation-saturation round. Verification labels: **primary text** when the
statement was read in the paper itself this session; **primary record** when
the publisher/author record was checked; **secondary record** when only a
citing source was checked. The claim-level conclusion is `search_gap`, which is
never a novelty assertion.

## What DS19 actually consumes

The audit's algebraic reduction (report §7) splits the DS19 complex into six
separable ingredients, and each was searched for separately:

1. fixed-partition Loewner minimisation of the generalized Schur complement
   (the DS11 identity — classical, Li–Mathias / Krein / Anderson; not re-searched);
2. design-side \(D_s\) duality on a *convex* feasible set (the minimax template
   whose interchange step fails on hard partitions);
3. exact scalar grouping by contiguity and its interval DP, including weighted
   points and ties, and the best known running time;
4. exact minimisation of a convex function evaluated by a comparison
   algorithm — one-dimensional and fixed-dimensional parametric search;
5. superpolynomial breakpoint counts of parametric shortest paths (the
   obstruction to naive envelope enumeration);
6. empirical scalar quantizer consistency on a selection-independent event
   (the DS18 step DS19.4 reuses — already triangulated in the DS18 audit).

## Triangulation (six fields per source)

- **Pukelsheim & Titterington (1983), *General Differential and Lagrangian
  Theory for Optimal Experimental Design*, Ann. Statist. 11(4):1060–1068,
  DOI `10.1214/aos/1176346321` (`Pukelsheim-Titterington-1983`; primary
  record).** **Exact problem:** optimal experimental design in convex-analytic
  form. **Exact result:** duality results by two routes (subgradients and
  Lagrangian theory) yielding general Kiefer–Wolfowitz-type equivalence
  theorems, including singular designs and subset-parameter (\(K'\theta\),
  hence \(D_s\)) criteria. **Objective:** information functionals of the
  design moment matrix. **Feasible set:** design measures on a compact design
  space — a **convex** set. **Transfers:** the certificate viewpoint of DS19.1
  (a dual object certifies optimality) and the polar/Lagrangian language in
  which the tilt \(\beta\) is a multiplier. **Does not:** strong duality there
  rests on convexity of the feasible set; the hard-partition domain of DS19 is
  a finite nonconvex set and `CE-DS-TILT-DUAL-GAP-001/-002` show the interchange
  fails, so no equivalence theorem transfers.
- **Megiddo (1983), *Applying parallel computation algorithms in the design
  of serial algorithms*, J. ACM 30(4):852–865, DOI `10.1145/2157.322410`
  (`Megiddo-1983`; primary record; the technique is restated in Toledo's
  primary text §2).** **Exact problem:** optimise a parameter \(\lambda\) for
  which a decision problem is solved by a comparison algorithm. **Exact
  result:** parametric search — simulate the algorithm at the unknown
  optimum, resolving each comparison by evaluating the decision oracle at the
  roots of the comparison polynomial; total time is the product of the
  algorithm's comparison count and the oracle cost. **Objective:** generic.
  **Feasible set:** one real parameter. **Transfers:** at \(d_\lambda=1\) the
  fixed-tilt interval DP is such a comparison algorithm (linear sort
  comparisons, quadratic DP comparisons), and the one-sided derivative of
  \(v_K\) is a monotone sign oracle; this yields an *arithmetic-polynomial*
  exact minimiser. **Does not:** bit complexity is not analysed; the audit's
  own root-separation argument (report §7.5) supplies it.
- **Toledo (1993), *Maximizing non-linear concave functions in fixed
  dimension*, in Complexity in Numerical Optimization (P. M. Pardalos, ed.),
  World Scientific, pp. 429–447; extended abstract FOCS 1992, DOI
  `10.1109/SFCS.1992.267783` (`Toledo-1993`; **primary text**, author
  preprint `tau.ac.il/~stoledo/Bib/Pubs/concave.pdf`, abstract, §1 and the §2
  definitions read this session).** **Exact problem:** maximise a piecewise
  polynomial concave \(F\) over a convex set \(\mathcal P\subset\mathbb R^d\),
  \(d\) fixed, given an evaluator \(\mathcal A\) whose \(x\)-dependent
  branches depend only on signs of polynomials of bounded degree \(\delta\)
  (the evaluator may evaluate given polynomials of degree \(\le\delta\), add
  \(x\)-dependent variables, and multiply them by constants). **Exact
  result:** \(\max_{\mathcal P}F\) and a maximiser are found in time
  polynomial in the number of arithmetic operations of \(\mathcal A\) (RAM
  model), extending Megiddo's lifting to algorithms that also find roots, and
  Cohen–Megiddo / Norton–Plotkin–Tardos from affine comparisons to polynomial
  ones. **Objective:** concave maximisation. **Feasible set:** a convex set in
  fixed dimension. **Transfers:** with \(F=-v_K\), the fixed-tilt interval DP
  is an evaluator of degree \(\delta=2\) (sort comparisons are affine in
  \(\beta\), each cell cost \(M_b(\beta)^2/W_b\) is a given quadratic, the DP
  only adds and compares them), so for **fixed \(d_\lambda\)** and **variable
  \(K\)** the exact minimum is computable with polynomially many arithmetic
  operations — a strict widening of DS19.2's fixed-\((K,d_\lambda)\) scope.
  **Does not:** the bound is arithmetic (real-RAM with explicit algebraic
  numbers), not a polynomial *bit* bound; the fixed-dimension constant is not
  controlled; nothing is said for variable \(d_\lambda\).
- **Grønlund, Larsen, Mathiasen, Nielsen, Schneider & Song (2017/2018), *Fast
  Exact k-Means, k-Medians and Bregman Divergence Clustering in 1D*,
  arXiv:1701.07204 (`Gronlund-etal-2017`; **primary text**, pp. 1–2 read this
  session).** **Exact problem:** exact one-dimensional \(k\)-means (and
  \(k\)-medians / Bregman) on \(n\) points. **Exact result:** the standard
  contiguous-cluster DP runs in \(O(kn^2)\) time; the same recurrence runs in
  \(O(n\log n+kn)\), or \(O(kn)\) on sorted input, by monotone-matrix
  (SMAWK-type) search; the authors record that the problem was solved earlier
  as *weighted* discrete scalar quantization and state that all algorithms
  and proofs generalise to the weighted cost. **Objective:** weighted scalar
  SSE (equivalently our uncentered between value after the labeling-independent
  shift). **Feasible set:** contiguous partitions of sorted scalars.
  **Transfers:** DS19.2's fixed-tilt \(O(KN^2)\) rational-operation bound is
  the classical DP and is improvable to \(O(KN)\) after sorting; weighted
  points are covered. **Does not:** ties among tilted values are not
  discussed (the audit's tie lemma, report §7.2, covers them); nothing about
  optimising the tilt.
- **Wang & Song (2011), *Ckmeans.1d.dp: Optimal k-means Clustering in One
  Dimension by Dynamic Programming*, The R Journal 3(2):29–33, DOI
  `10.32614/RJ-2011-015` (`Wang-Song-2011`; primary record).** **Exact
  problem:** exact 1-D \(k\)-means. **Exact result:** the \(O(kn^2)\)-time,
  \(O(kn)\)-space contiguous DP with an implementation. **Objective:** scalar
  SSE. **Feasible set:** contiguous partitions. **Transfers:** the precise DP
  DS19.2 describes; weighted variants exist in the package. **Does not:** no
  parametric or tilt optimisation, no tie theory.
- **Carstensen (1983), *Complexity of some parametric integer and network
  programming problems*, Ph.D. thesis, University of Michigan
  (`Carstensen-1983`; **secondary record** via Gajjar–Radhakrishnan 2019 and
  the 2025 linear-parametric optimisation survey arXiv:2501.11544).** **Exact
  problem:** number of breakpoints of the optimal-cost curve of a parametric
  shortest path with linear edge weights. **Exact result:** instances with
  \(n^{\Omega(\log n)}\) breakpoints, and a matching \(n^{O(\log n)}\) upper
  bound. **Objective:** parametric path cost. **Feasible set:** \(s\)–\(t\)
  paths. **Transfers:** together with Gajjar–Radhakrishnan it is the warning
  that materialising the parametric envelope of a DAG shortest path can be
  superpolynomial, which is why DS19.2 refuses to call crossings-plus-midpoints
  exact. **Does not:** it does not bound the breakpoints of the restricted
  interval-segmentation DAG with quadratic costs, and Megiddo/Toledo show
  that the envelope need not be materialised at all in fixed dimension.

## Search outcome and boundary

Six query families were run (design-side \(D_s\)/Lagrangian duality; 1-D
\(k\)-means exact DP and its fastest variants; parametric search in one and
fixed dimension with polynomial comparisons; parametric shortest-path
breakpoint complexity; minimax over finite actions with quadratic payoffs;
weighted scalar grouping with ties). Direct antecedents exist for **five**
ingredients separately: the DS11 identity (Li–Mathias, already registered),
convex-design duality (Silvey–Titterington, Pukelsheim–Titterington), the
fixed-tilt DP and its \(O(KN)\) improvement (Fisher, Wang–Song, Grønlund et
al.), exact one-dimensional and fixed-dimensional parametric minimisation
(Megiddo, Toledo), and the envelope-complexity obstruction (Carstensen,
Gajjar–Radhakrishnan). No located source states the combined DS19 theorem on
the hard-partition feasible set: the two-domain bracket, the exact saddle
closure gate, the order-one gap, or the \(\Delta\)-consistency of the
strip-DP primal. Two attribution repairs follow from the search: (i) the
exact-computation scope of `DS-TILT-DUAL-CERTIFICATE` was narrower than the
literature already allows — Megiddo/Toledo settle fixed \(d_\lambda\) with
variable \(K\) in arithmetic complexity, and the audit supplies the
\(d_\lambda=1\) bit-polynomial version; (ii) the fixed-tilt bound is
\(O(KN)\) after sorting, not only \(O(KN^2)\). The compound statement remains
`search_gap`.
