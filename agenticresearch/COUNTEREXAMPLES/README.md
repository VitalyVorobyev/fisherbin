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

## CE-D-LLOYD-001 — adaptive D-Mahalanobis Lloyd can decrease log-det

**Status:** established project negative result; exact minimal dataset should be copied here from the numerical test suite before publication.

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

**Action:** add smallest rational-coordinate dataset, initial labels, old/new objective, and exact assignment once extracted from tests.

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

**Action:** store smallest explicit finite example.

---

## CE-DS-GEOMETRY-001 — exact finite \(D_s\) geometry can fail

**Status:** project negative result.

**Claim falsified:**

> A finite globally optimal or one-point exchange-stable \(D_s\) partition must assign each point according to the naive first-order efficient-score/common-metric rule.

**Known conclusion:** false in general.

**Action required for publication/research reuse:**

Store:

- score matrix \(S\);
- positive weights;
- POI/nuisance index split;
- \(K\);
- globally optimal labeling;
- exact \(D_s\) objective;
- first-order metric/sensitivity;
- violating point/cell comparison;
- exhaustive-search verification.

---

## CE-E-GEOMETRY-001 — naive E fixed-gradient rule fails

**Status:** project negative result.

**Claim falsified:**

> Choose one projector onto a minimum-eigenvalue eigenvector; every finite E-optimal partition is pointwise optimal under that fixed quadratic metric.

Repeated minimum eigenvalues make the criterion nonsmooth and there is no canonical unique gradient.

**Action:** store smallest exact example and then test the stronger common-supergradient conjecture.

---

## CE-A-DSTYLE-001 — A does not inherit D exchange-to-Voronoi theorem

**Status:** project negative/control result.

**Claim falsified:**

> The determinant-specific finite theorem extends to every smooth monotone matrix criterion.

**Action:** store exact smallest instance.

---

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
