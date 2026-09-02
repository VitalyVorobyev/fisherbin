# Targeted triangulation for `OPEN-DS-PRACTICAL-CERTIFIED-SOLVER` — 1 September 2026

**Key:** Li-Mathias-2000, Silvey-Titterington-1973, Fisher-1958, Gajjar-Radhakrishnan-2019

This search targets the proposed scalar-POI tilt bracket

\[
\max_z\min_\beta V_z(\beta)
\;\le\;
\min_\beta\max_z V_z(\beta),
\]

its exact computation by scalar interval dynamic programming, and the separate
claim that the resulting strip-DP primal is value-consistent on the DS18 law.
The comparison domain is finite hard labelings, not approximate-design weights
or continuous score compression. Verification labels below are: **verbatim**
when the theorem/proof text was checked in an existing workspace audit or
primary scan, and **primary record** when the publisher or author preprint
statement was checked but the full proof was not reread in this session.

## Six-field triangulation

| Source | Exact problem | Exact result | Objective | Feasible set | What transfers / what does not |
|---|---|---|---|---|---|
| **Li & Mathias (2000), *Extremal Characterizations of the Schur Complement and Resulting Inequalities*, SIAM Review 42(2):233–246, Thm. 2.2** (`Li-Mathias-2000`; **verbatim** in the DS11 audit) | Extremal characterization of the generalized Schur complement of a positive-semidefinite block matrix. | For every matrix \(Z\), \([Z\mid I]H[Z\mid I]^*\succeq S(H)\), with equality exactly on the stated generalized normal equation; the theorem includes the Moore–Penrose case. | Loewner minimization of a partially evaluated quadratic form. | An unconstrained matrix \(Z\) for one fixed block matrix \(H\succeq0\). | **Transfers:** exactly supplies \(S_\psi^+(I_z)=\min_B V_z(B)\), including singular nuisance blocks and the attainment set. **Does not:** interchange \(\max_z\) and \(\min_B\), close the duality gap, or give an algorithm for the pointwise maximum over hard partitions. |
| **Silvey & Titterington (1973), *A Geometric Approach to Optimal Design Theory*, Biometrika 60(1):21–32** (`Silvey-Titterington-1973`; **primary publisher record**, existing deep review) | \(D\)- and \(D_s\)-optimal approximate experimental design, treated geometrically through duality. | The publisher summary states that the \(D\)/\(D_s\) equivalence theorems are formulated as duality theorems using Strong Lagrangian Theory, proves the \(D_s\) theorem, and establishes convergence of a monotone \(D\)-design construction. | Determinant and subset-parameter determinant criteria of a design information matrix. | The convex simplex of design weights on fixed regressors. | **Transfers:** the certificate/equivalence viewpoint and the warning that the comparison domain is load-bearing. **Does not:** strong duality relies on a convex design-measure feasible set; a hard partition couples cell masses and conditional means on a finite nonconvex set, so its minimax equality and algorithm do not follow. |
| **W. D. Fisher (1958), *On Grouping for Maximum Homogeneity*, JASA 53(284):789–798** (`Fisher-1958`; **verbatim**, Brown scan pp. 789–792) | Partition finitely many weighted scalar values into a fixed number of groups while minimizing within-group weighted squared error. | The appendix proves that an optimum is contiguous in sorted order, reducing all set partitions to \(\binom{N-1}{K-1}\) interval partitions; the usual scalar interval DP then gives the exact optimum. | Weighted within-group SSE, equivalently maximized scalar between-group sum of squares. | All hard partitions of a fixed weighted scalar table. | **Transfers:** for every fixed tilt \(\beta\), the exact inner problem is an ordered interval problem. Ties, duplicates, and deterministic weak-order handling remain implementation obligations; existing project regressions, not Fisher's citation, cover those cases. **Does not:** optimize over \(\beta\), bound the number of changes of the DP optimizer, prove bracket exactness, or imply value consistency for a data-dependent tilted rule. |
| **Gajjar & Radhakrishnan (2019), *Parametric Shortest Paths in Planar Graphs*, FOCS 2019:876–895** (`Gajjar-Radhakrishnan-2019`; **primary author preprint/publisher record**) | Shortest paths when edge weights vary linearly with a real parameter. | There are \(n\)-vertex planar instances whose optimal-path cost envelope has \(n^{\Omega(\log n)}\) pieces; the paper also records a matching-form \(n^{\log n+O(1)}\) general upper bound for linear weights and extensions to polynomial/multiparameter weights. | Minimum path cost as a parameterized lower envelope. | Source–sink paths in a parameterized planar graph. | **Transfers:** a scalar interval DP is a shortest-path computation on a DAG, so an exact all-breakpoint sweep needs a structure-specific complexity proof; “polynomially many input-line crossings” alone does not bound the optimizer envelope. **Does not:** their lower bound is not for the restricted interval-segmentation DAG or its quadratic segment costs, and therefore does not disprove polynomial exact computation of the ScoreQuant dual. |

Primary records: Li–Mathias DOI
`10.1137/S0036144599337290`; Silvey–Titterington DOI
`10.1093/biomet/60.1.21`; Fisher DOI
`10.1080/01621459.1958.10501479`; Gajjar–Radhakrishnan DOI
`10.1109/FOCS.2019.00057`, author preprint `arXiv:1811.05115`.

## Search outcome and boundary

The repository search covered generalized-Schur partial minimization,
\(D_s\)-design duality, scalar contiguity/exact DP, and tilted/parametric
one-dimensional clustering. A fresh concept search used four query families:
partial-quadratic minimax over finite actions; \(D_s\)/c-optimality duality;
parametric one-dimensional \(k\)-means DP; and parametric segmented least
squares. The only additional close computational boundary was parametric
shortest-path envelope complexity, represented above. The search was targeted,
not a citation-saturation round.

Direct prior art is therefore present for three ingredients separately:
fixed-partition quadratic minimization (Li–Mathias), convex-design duality
(Silvey–Titterington), and fixed-tilt scalar interval optimality (Fisher).
No located source establishes the combined theorem on the ScoreQuant feasible
set: validity and polynomial exact computation of
\(\min_\beta\max_z V_z(\beta)\), an exact zero-gap characterization for hard
partitions, or \(\Delta\)-consistency of the strip-DP primal on the DS18 law.
The claim-level conclusion is **`search_gap`**, never a novelty claim.

Two cautions are load-bearing. First, standard minimax theorems apply after
convexification or under convex–concave hypotheses and cannot silently replace
the finite hard-labeling domain. Second, generic parametric shortest paths can
have superpolynomially many envelope pieces, so exact polynomial computation
must use and prove additional structure of the ordered interval DP; the line
arrangement of tilted observations by itself is insufficient.
