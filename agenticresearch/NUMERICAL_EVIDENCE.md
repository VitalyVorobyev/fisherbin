# Numerical evidence and regression-test ledger

**Purpose:** preserve empirical evidence that supports theorem auditing and solver regression tests. Nothing in this file is a proof.

Each row names the CLAIMS.json node(s) it supports and the executable source that produces it (`tests/…` runs in CI; `py/…` is a workspace script; legacy sweeps live in `py/dopt_*.py`).

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
| N-SCREEN | general concavity screening | D/A/Ds random moves | 0/4,886 violations | GENERAL-SUPERGRADIENT-SCREENING | py/dopt_addendum2.py | screening regression |

## Rules

1. Keep theorem tests separate from performance benchmarks.
2. Promote any publication-critical counterexample to exact JSON/rational form.
3. Store random seeds, code revision, and environment beside new benchmark output.
4. If a new implementation disagrees with an identity regression, treat it as a bug until independently explained.
5. If a new search finds a theorem violation, stop optimization benchmarking and audit the theorem immediately.
6. Every new row must cite at least one CLAIMS.json id and one executable source.
