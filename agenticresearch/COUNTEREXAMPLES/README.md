# Counterexample bank
**Purpose:** reusable falsification cases for theorem agents.

A counterexample is only useful if it is:

- exactly reproducible;
- stored with objective/criterion;
- explicit about finite/population level;
- explicit about weights, labels, and parameter split;
- verified by recomputation;
- accompanied by the exact claim it falsifies.

Do not store only screenshots or random seeds.

---

The quick table of every fixture is generated: see `INDEX.md`.

# Required JSON format for new cases
Each exact case should also have a `.json` file:

```json
{
  "id": "CE-...",
  "criterion": "D|Ds|E|A|...",
  "level": "finite_assignment",
  "claim_falsified": "...",
  "scores": [[...], [...]],
  "weights": [...],
  "K": 3,
  "labels_before": [...],
  "labels_after_or_optimum": [...],
  "poi_indices": [0],
  "nuisance_indices": [1],
  "objective_before": null,
  "objective_after": null,
  "verification": {
    "method": "exhaustive|exact_formula|high_precision",
    "notes": "..."
  },
  "source": "project test / theorem investigation",
  "date": "YYYY-MM-DD"
}
```

---

# Falsification checklist
For every new theorem candidate, deliberately test:

- \(d=1,2,3\);
- smallest rank-feasible \(K\);
- \(N\le10\) exhaustive partitions;
- unequal weights;
- tiny cells;
- singleton cells;
- duplicate score atoms;
- near-singular \(I_q\);
- repeated E minimum eigenvalues;
- weak/singular nuisance blocks;
- exact ties;
- rational/integer coordinates when possible.

The counterexample bank is part of the mathematical memory of the project, not merely a debugging directory.

---

# Catalogue

One entry per fixture: what it falsifies, the construction, and the
boundary resolution. The `.json` files are the machine source of truth.

## CE-A-DSTYLE-001 — A does not inherit D exchange-to-Voronoi theorem

**Status:** exact rational counterexample.

**Claim falsified:**

> The determinant-specific finite theorem extends to every smooth monotone matrix criterion — in particular, for the A criterion \(-\operatorname{tr}(I_q^{-1})\), a relocation with strictly positive first-order \(I_q^{-2}\) Mahalanobis margin must not decrease the exact objective.

\(N=6\), \(d=2\), \(K=3\), integer scores centered exactly, uniform weights.
Moving row 2 from cell 1 to cell 0 has first-order margin \(567/20 > 0\)
(the D-style screening says "must improve"), yet \(\operatorname{tr}(I_q^{-1})\)
rises from \(81/10\) to \(1512/125\) — exact A gain \(-999/250\). The log-det
coincidence that powers the D theorem does not survive replacing
\(\log\det\) by \(-\operatorname{tr}(I^{-1})\).

**Fixture:** `CE-A-DSTYLE-001.json`.

---

## CE-D-LLOYD-001 — adaptive D-Mahalanobis Lloyd can decrease log-det

**Status:** exact rational counterexample.

**Claim falsified:**

> Reassigning all points to their nearest current centroids under \(I_q^{-1}\), then recomputing centroids, monotonically increases \(\log\det I_q\).

**Reason the proof attempt fails:**

\[
\log\det J
\le
\log\det I
+
\operatorname{tr}(I^{-1}(J-I)).
\]

The tangent is an upper bound, so improvement of the fixed-metric trace surrogate is not a minorize-maximize step for log-det.

Eight exact-decimal rows in \(d=2\), uniform weights \(1/8\), \(K=3\), initial
labels \((1,0,0,1,2,2,2,1)\). The batch adaptive-Mahalanobis step (argmin
decided in exact rational arithmetic) relabels to \((0,0,1,1,2,1,0,1)\) and the
exact determinant strictly drops; the log-det decrease is \(\approx 0.136521\)
nat.

**Fixture:** `CE-D-LLOYD-001.json`.
**Regression:** `tests/test_research_claims.py::test_adaptive_mahalanobis_lloyd_step_can_decrease_d_objective`.

---

## CE-D-UNMERGED-DUPLICATES-001 — split duplicate atoms block strict D-Voronoi closure

**Status:** exact rational boundary counterexample.

**Claim falsified:**

> One-point exchange stability implies strict self-consistent nearest-centroid
> assignment even when coincident positive-weight score atoms may be assigned
> to different cells.

Take scalar scores \((1,1,-1)\), weights \((1/4,1/4,1/2)\), and put each row in
one of \(K=3\) singleton cells. Then \(I_q=1\), all cells are nonempty, and no
nonempty-preserving relocation exists. The labeling is therefore vacuously
exchange stable. The first two centroids coincide, however, so strict assignment
fails and no deterministic score-only rule can reproduce the split labels.

**Boundary resolution:** merge coincident score atoms before optimization, or
require labels to be constant on each duplicate class. The audited theorem then
forces distinct centroids and strict assignment.

**Fixture:** `CE-D-UNMERGED-DUPLICATES-001.json`.

---

## CE-D-VORONOI-CONVERSE-001 — D-Voronoi fixed does not imply exchange stable

**Status:** project negative result.

**Claim falsified:**

> Every self-consistent \(I_q^{-1}\)-Voronoi finite partition is one-point exchange stable.

The proven/project direction is the reverse:

\[
\text{exchange stable}
\Rightarrow
\text{strict D-Voronoi}.
\]

**Status:** exact rational counterexample, minimal (\(N=4\), \(d=1\), \(K=2\)).

Centered scalar scores \((-3/4,-3/4,1/4,5/4)\), uniform weights, labels
\((0,0,0,1)\). Every row is strictly nearest its own centroid (cell centroids
\(-5/12\) and \(5/4\)), so the partition is a strict self-consistent D-Voronoi
partition; yet relocating row 2 to cell 1 raises \(I_q\) from \(25/48\) to
\(9/16\). Voronoi fixed therefore does not imply one-point exchange stable.

**Fixture:** `CE-D-VORONOI-CONVERSE-001.json`.

---

## CE-DS-DEGENERATE-GLOBAL-TIE-001 — a finite global \(D_s\) optimum can be a 31-fold exact tie class with coincident projected centroids

**Status:** exact rational counterexample (exhaustive enumeration).

**Claim falsified:**

> An exact finite global profiled-\(D_s\) optimum is unique up to label
> permutation, keeps its efficient-projected centroids pairwise separated, and
> — when it has zero first-order violations — is reproducible from its own
> efficient-semimetric nearest-cell rule.

A centered equal-weight \(N=8,d=2,d_\psi=1,K=3\) sample (drawn from a
correlated Gaussian and rounded to exact eighths) whose global in-bin optimum
\(1083/4096\) is attained by exactly 31 labelings — the feasible refinements
of one reduced bipartition. Every tied optimum has two exactly coincident
projected centroids, so no efficient-semimetric rule separates them; the
unique nuisance-mean-equal refinement is infeasible (singular nuisance block)
with generalized pseudo-inverse value \(1191/4096\) **above** the feasible
optimum, showing the pseudo-inverse extension leaves the in-bin statistical
formulation. Theory: `KNOWN_RESULTS/05b-ds-bridge.md` DS11(c–d).

**Fixture:** `CE-DS-DEGENERATE-GLOBAL-TIE-001.json`.

---

## CE-DS-MARGINS-RANK-VACUITY-001 — at \(K=d_\lambda+1\) every feasible labeling has profiled value exactly zero

**Status:** exact rational boundary counterexample (exhaustive enumeration; the
mechanism is a two-line rank argument, universal over samples).

**Claim falsified:**

> DS15's margins dichotomy as first registered for general nuisance dimension
> under the bare cardinality assumption \(K\ge3\): conclusion (i) — value
> convergence to the positive unrestricted supremum \(v_K\) — for
> \(d_\lambda\ge2\) with \(K=d_\lambda+1\).

Exact centering gives \(\sum_b m_b=0\), so \(\operatorname{rank}(I_z)\le K-1\);
when the \(d_\lambda\times d_\lambda\) binned nuisance block is nonsingular
with \(d_\lambda=K-1\), Schur rank additivity forces the profiled value to be
exactly zero — for **every** sample and every feasible labeling. The minimized
witness (\(N=4\), integer scores with zero column sums, \(d_\lambda=2\),
\(K=3\)) has all six feasible labelings at value \(0\), efficient-score
interval optimum \(81/50>0\), and \(K=4=d_\lambda+2\) value \(9/5>0\) on the
same atoms. Hence the dichotomy needs \(K\ge d_\lambda+2\); at
\(d_\lambda=1\) that is exactly the recorded \(K\ge3\). Theory:
`KNOWN_RESULTS/05b-ds-bridge.md` DS15 (audited scope) and DS9/FI-RANK-CEILING.

**Fixture:** `CE-DS-MARGINS-RANK-VACUITY-001.json`.

---

## CE-DS-GLOBAL-GEOMETRY-001 / -002 — exact finite \(D_s\) geometry can fail

**Status:** two independent exact rational counterexamples for the same claim.

**Claim falsified:**

> A finite globally optimal or one-point exchange-stable \(D_s\) partition must assign each point according to the naive first-order efficient-score/common-metric rule.

**Known conclusion:** false in general.

- `CE-DS-GLOBAL-GEOMETRY-001.json` — the canonical fixture harvested from the
  26 Aug 2026 manuscript (\(N=8\), 966 partitions, optimum \(6241/984\),
  runner-up \(4232/669\)).
- `CE-DS-GLOBAL-GEOMETRY-002.json` — the independent witness pinned by the CI
  regression test (\(N=8\), optimum \(20449/1920\), margin to second best
  \(2929/21120\), row 6 violates its own efficient-semimetric rule by exactly
  \(8/195\)).
  **Regression:** `tests/test_research_claims.py::test_global_profiled_ds_partition_can_violate_its_own_metric_rule`.

The two instances are unrelated data sets; keep both and do not conflate them.

---

## CE-DS-POP-WASTED-CELLS-001 — population-stationary \(D_s\) partitions can defeat every efficient-semimetric rule

**Status:** exact rational construction (symmetric quadrature verification).

**Claim falsified:**

> A first-order stationary population profiled-\(D_s\) quantizer has
> pairwise-distinct efficient-projected centroids, so its cells can always be
> recovered from a common efficient-semimetric nearest-cell rule.

Under a nuisance-sign-symmetric law, a \(\psi\)-threshold partition with each
side split by \(\operatorname{sign}(s_\lambda)\) (K=4) is exactly stationary
(zero violations, ties allowed), its two extra cells add nuisance information
\(9/4\) but exactly zero profiled information, and its projected centroids
coincide pairwise — while its K=2 coarsening has an exactly singular binned
nuisance block. The symmetry argument applies verbatim to any
nuisance-sign-symmetric atomless law. Theory: `KNOWN_RESULTS/05b-ds-bridge.md` DS12.

**Fixture:** `CE-DS-POP-WASTED-CELLS-001.json`.

---

## CE-E-GEOMETRY-001 — naive E fixed-gradient rule fails

**Status:** project negative result.

**Claim falsified:**

> Choose one projector onto a minimum-eigenvalue eigenvector; every finite E-optimal partition is pointwise optimal under that fixed quadratic metric.

Repeated minimum eigenvalues make the criterion nonsmooth and there is no canonical unique gradient. The stored instance is stronger: the minimum eigenvalue is **simple** (spectral gap \(\approx 0.068\)) and the rank-one \(vv^\top\) rule still fails.

**Status:** float witness verified by exhaustive enumeration (high-precision, not exact-rational — eigenvalue computation).

\(N=8\), \(d=2\), \(K=3\), uniform weights. The unique global E optimum
\((0,1,1,2,0,0,0,1)\) has a simple minimum eigenvalue, yet row 7 is strictly
closer to cell 2 than to its own cell 1 under the \(vv^\top\) metric, with
margin \(\approx 0.068\).

**Fixture:** `CE-E-GEOMETRY-001.json`.
**Regression:** `tests/test_research_claims.py::test_global_e_partition_can_violate_simple_eigenvector_rule`.
**Next step:** test the stronger common-supergradient conjecture (`OPEN-E-COMMON-SUPERGRADIENT`).

---
