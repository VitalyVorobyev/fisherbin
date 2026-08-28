# Numerical evidence and regression-test ledger

**Purpose:** preserve empirical evidence that supports theorem auditing and solver regression tests. Nothing in this file is a proof.

Each row names the claim node(s) it supports and the executable source that produces it (`tests/…` runs in CI; `py/…` is a workspace script; legacy sweeps live in `py/dopt_*.py`).

| ID | Test | Setting | Reported result | Claims | Source | Scientific use |
|---|---|---|---|---|---|---|
| N-D-MOVE | Rank-two relocation + exact D gain | thousands of random admissible moves | full recomputation agreement at numerical precision | D-RANK2-MOVE, D-LOGDET-GAIN | py/dopt_experiments.py | algebra regression |
| N-D-THM | D exchange⇒Voronoi lower bound stress | 15,000 states / 5,547 qualifying moves in independent suite | 0 violations | D-EXCHANGE-IMPLIES-VORONOI, D-EXCHANGE-VIOLATION-LOWER-BOUND | py/dopt_experiments.py; tests/test_research_claims.py::test_d_voronoi_violation_has_positive_gain_lower_bound | theorem falsification |
| N-D-AUDIT-EXACT | Exact-rational D exchange⇒Voronoi audit | 80 data sets; d=1,2,3; 8,727 PD partitions; 97,601 admissible moves; 30,881 tied-or-worse moves; 93 stable partitions | PASS; 0 identity, bound, or strict-geometry violations | AUDIT-D-EXCHANGE-VORONOI, D-EXCHANGE-IMPLIES-VORONOI, D-UNMERGED-DUPLICATES-FAIL | py/audit_d_exchange_voronoi.py | publication-grade theorem regression |
| N-D-LLOYD | Adaptive Mahalanobis Lloyd monotonicity | 300 instances | 57 contained a decreasing step; explicit ≈ −0.137 nat | D-LLOYD-NONMONOTONE | tests/test_research_claims.py::test_adaptive_mahalanobis_lloyd_step_can_decrease_d_objective; COUNTEREXAMPLES/CE-D-LLOYD-001.json | negative algorithm result |
| N-D-FIXED | Lloyd fixed vs exchange stable | 100 Lloyd fixed points | 35 exactly improvable; max ≈ +1.033 nat | D-VORONOI-NOT-EXCHANGE | py/dopt_experiments.py; COUNTEREXAMPLES/CE-D-VORONOI-CONVERSE-001.json | hierarchy regression |
| N-D-GLOBAL | Exhaustive D benchmark | N=12,d=2,K=3, 30 instances | best-of-10 exchange 30/30 global; whitened k-means 24/30 | D-GLOBAL-XP | py/dopt_experiments.py; tests/test_research_claims.py::test_small_d_exchange_matches_exhaustive_global_oracle | solver baseline |
| N-D-TRACE | Trace vs D optimum | same small exhaustive suite | different global partitions in 6/30 | TRACE-WHITENED-KMEANS | py/dopt_experiments.py | objective separation |
| N-D-RANDOM | single random-start exchange | reported suite | 86% global hit; worst stall ≈0.195 nat | D-GLOBAL-XP | py/dopt_experiments.py | multistart motivation |
| N-D-BB | branch-and-bound | reported d=2,K=3 | certified through N=40; hardest reported N=40 visited 131,799 nodes / 8.3 s | D-BB-SINGLETON-BOUND | py/dopt_* legacy sweep | exact solver regression |
| N-DS-BOUND | Ds finite geometry bound | 12,789 tested moves | PASS; observed max violation shrinks with N | DS-OKN-BOUND | py/dopt_addendum3.py | O(K/N) bound regression (manuscript Prop. 4) |
| N-DS-DOM | efficient-score domination | 300 random partitions | 300/300 PSD inequalities | DS-EFFICIENT-SCORE-DOMINATION | py/dopt_addendum3.py | theorem regression |
| N-DS-CERT1 | projected-D upper certificate | d=3,dpsi=1,K=4,N=60, 8 cases | gaps 0.003–0.118 nat | DS-EFFICIENT-SCORE-GLOBAL-UPPER | py/dopt_* legacy sweep | practical certificate |
| N-DS-CERT2 | projected-D upper certificate | d=4,dpsi=2,K=5,N=80, 4 cases | gaps 0.011–0.19 nat | DS-EFFICIENT-SCORE-GLOBAL-UPPER | py/dopt_* legacy sweep | practical certificate |
| N-E-FAIL | E D-style move geometry | 8,965 candidate moves | 2,167 rule-positive/exact-negative; 0 reverse screening violations | E-FIRSTORDER-NOT-FINITE, E-GLOBAL-GEOMETRY-FAILS | py/dopt_addendum3.py; tests/test_research_claims.py::test_global_e_partition_can_violate_simple_eigenvector_rule; COUNTEREXAMPLES/CE-E-GEOMETRY-001.json | criterion separation |
| N-A-FAIL | A D-style geometry | reported search | 443 counterexamples | A-FINITE-GEOMETRY-FAILS | py/dopt_addendum2.py; COUNTEREXAMPLES/CE-A-DSTYLE-001.json | criterion separation |
| N-DS-LEVERAGE | exact leverage stability bound at global Ds optima | 2,706 admissible moves at 110 exhaustively verified global optima (5 laws, N=8–18) + 32 moves on both canonical fixtures, exact rationals | 0 violations; max gap/bound ratio 0.5467 | DS-EXCHANGE-LEVERAGE-BOUND | py/ds_population_bridge.py (trend + analyze + leverage modes) | theorem falsification/regression |
| N-DS-BRIDGE-TREND | geometry of exact global Ds optima vs N | 110 exhaustive global optima; 5 laws; N=8,10,12,14,16,18; deterministic md5 seeds | max relative semimetric violation does not yet shrink at these N (worst 0.42 at N=10); min cell mass frequently 1/N (singleton cells at optima); exactly one exact projected-centroid coincidence (the tie fixture); all DS6 bounds respected | OPEN-DS-MARGINS-AT-OPTIMA, DS-GLOBAL-TIE-DEGENERACY, DS-OKN-BOUND | py/ds_population_bridge.py trend/analyze | margin-assumption evidence for the DS14 bridge |
| N-DS-AUDIT-LEVERAGE | independent exhaustive DS13 audit at ALL stable states | 5 adversarial datasets (vector nuisance d_lam=2, vector POI d_psi=2, unmerged duplicates, unequal weights, nuisance-symmetric); 1,707 feasible states, 171 exchange-stable states, 1,748 admissible moves incl. 230 singular-destination moves; exact rationals, no float screen | 0 violations; worst gap/bound ratio 1/2; centered K=2 probe structurally infeasible (U4); lambda-centered uncentered K=2 landscape exactly flat (106 tied global optima) | AUDIT-DS-POPULATION-BRIDGE, DS-EXCHANGE-LEVERAGE-BOUND | py/audit_ds_population_bridge.py ds13; tests/test_research_claims.py::test_ds13_leverage_bound_at_every_stable_state_with_vector_nuisance | publication-grade theorem regression |
| N-DS-AUDIT-VARIATIONAL | independent DS11 variational-identity audit | 400 deterministic exact PSD instances, d_psi,d_lam in {1,2}, 58 with singular nuisance blocks and multiple normal-equation solutions; plus the pseudo-inverse discontinuity witness diag(1,1/k) | 0 failures of consistency, solution-set value agreement, completion of squares, Loewner minimality, or Schur agreement | AUDIT-DS-POPULATION-BRIDGE, DS-PROFILED-VARIATIONAL | py/audit_ds_population_bridge.py ds11 | identity regression |
| N-DS-AUDIT-MARGINS | independent fully exact global-optimum margin scan | 3 own integer-LCG datasets, N=10, K=3, exact enumeration of all canonical labelings (no float screen, no top-k cut) | 1 of 3 exact global optima carries a singleton cell; DS13 and DS6 hold at all optima; both packet fixtures re-verified from raw scores through an independent code path | AUDIT-DS-POPULATION-BRIDGE, OPEN-DS-MARGINS-AT-OPTIMA | py/audit_ds_population_bridge.py margins + fixtures | margin-assumption evidence, fixture cross-check |
| N-SCREEN | general concavity screening | D/A/Ds random moves | 0/4,886 violations | GENERAL-SUPERGRADIENT-SCREENING | py/dopt_addendum2.py | screening regression |

## Rules

1. Keep theorem tests separate from performance benchmarks.
2. Promote any publication-critical counterexample to exact JSON/rational form.
3. Store random seeds, code revision, and environment beside new benchmark output.
4. If a new implementation disagrees with an identity regression, treat it as a bug until independently explained.
5. If a new search finds a theorem violation, stop optimization benchmarking and audit the theorem immediately.
6. Every new row must cite at least one claim id and one executable source; `py/registry.py validate` checks that every cited id resolves.
