# ScoreQuant theorem-research agent protocol

**Version:** 2.0 · 26 August 2026

You are a mathematical research agent working on **D- and \(D_s\)-optimal hard quantization of multivariate score space**.

---

# 1. Mandatory reading order

1. `PROBLEM.md` — authoritative project definition.
2. `KNOWN_RESULTS.md` — canonical current mathematical state.
3. `CLAIMS.json` — machine-readable claim/dependency registry.
4. `COUNTEREXAMPLES/README.md` + exact JSON fixtures.
5. `OPEN_PROBLEMS.md` — unresolved research queue.
6. `LITERATURE.md` — annotated prior art.
7. `NUMERICAL_EVIDENCE.md` — regression evidence, never theorem authority.
8. `archive/` only for historical context.

If an archived document conflicts with the canonical files, the canonical files win.

---

# 2. Non-negotiable scope rules

1. Primary objectives are **D** and **\(D_s\)**; trace/A/E are controls unless explicitly targeted.
2. Every claim must identify one level:
   - `finite_assignment`;
   - `empirical_inductive_quantizer`;
   - `population_quantizer`.
3. The target decision variable is a **hard score/score-proxy partition**.
4. Never silently replace the problem with experimental design, subset selection, within-scatter determinant clustering, k-means, scalar thresholding, or soft neural categorization.
5. For in-bin \(D_s\), use the Schur complement, not the POI block alone.
6. Keep the **projected full-data efficient-score problem** separate from in-bin \(D_s\); it is an upper/reference formulation and can use externally supplied nuisance information.
7. For classifier/ratio input distinguish score estimation from quantization.
8. Every production method must explain assignment of unseen observations.
9. Every result must report exact guarantee vocabulary.
10. Information loss relative to unbinned inference is required.
11. A search gap is not a novelty proof.

---

# 3. Do not rediscover already-established project results

Treat the following as current inputs unless the task is explicitly an audit:

### Full D

- exact rank-two finite relocation;
- exact closed log-det gain;
- leverage inequality;
- one-point exchange stability ⇒ strict self-consistent D-Voronoi;
- exact finite D compiler reproducing training labels;
- global finite D optimum geometrically realizable;
- monotone finite exact exchange;
- adaptive D-Lloyd nonmonotonicity counterexample;
- Voronoi fixed does not imply exchange stable;
- fixed-\((d,K)\) \(N^{O(Kd)}\) exact route;
- singleton-refinement B&B.

### Generic concave criteria

- weighted supergradient/tangent screening is a sound finite-move rejection rule.

### \(D_s\)

- exact finite low-rank move evaluation;
- D-style finite geometric closure is false;
- exact global non-geometric finite counterexample exists;
- exchange-stable geometric violation has an \(O(K/N)\)-type bound under balanced conditions;
- full-data efficient-score domination theorem;
- scalar \(d_\psi=1\) projected D upper problem is exactly solvable by DP;
- \(K\le d\) makes full in-bin profiling singular, while the projected efficient-score formulation may remain well posed with external nuisance information.

### E/A controls

- E repeated-minimum-eigenvalue one-transfer first order can be non-identifying;
- global finite E geometry can fail even with simple minimum eigenvalue;
- A and E do not inherit D exchange⇒geometry;
- A exact \(O(d^2)\) move oracle;
- E exact evaluation + screening + Loewner B&B.

### Population/soft/consistency

- randomized soft assignment FIM is exact for the randomized quantizer;
- exact soft-assignment gradient is known;
- hard finite geometric objective is piecewise constant;
- DWW purification removes population randomization advantage for atomless laws for any criterion depending on \((W_b,m_b)\);
- compact regular affine-max families have a restricted-class uniform-consistency proposition;
- local Fisher-losslessness iff score is measurable with respect to the bin label.

If you believe one of these is wrong, open an **audit task** and try to falsify it; do not silently downgrade or overwrite it.

---

# 4. Canonical mathematical objects

Score:

\[
s(x)=\nabla_\theta\log p(x\mid\theta)|_{\theta_0}.
\]

Hard quantizer:

\[
q:\mathbb R^d\to[K].
\]

Retained information:

\[
I_q=\sum_bW_b\mu_b\mu_b^\top.
\]

D:

\[
\Phi_D=\log\det I_q.
\]

In-bin \(D_s\):

\[
\Phi_{D_s}=\log\det
(I_{\psi\psi}-I_{\psi\lambda}I_{\lambda\lambda}^{-1}I_{\lambda\psi}).
\]

D-efficiency:

\[
\eta_D=(\det I_q/\det I_{\rm full})^{1/d}.
\]

\(D_s\)-efficiency:

\[
\eta_{D_s}=
(\det S_\psi(I_q)/\det S_\psi(I_{\rm full}))^{1/s}.
\]

---

# 5. Model-access rules

Always identify the oracle:

- direct scores;
- exact/autodiff score;
- analytic density ratio;
- component ratios;
- direct learned density-ratio estimator;
- calibrated classifier posterior/ratio proxy.

For a classifier-derived score \(\hat s\), distinguish surrogate optimization from true retained Fisher information:

\[
I_{\rm true\ retained}
=\operatorname{Var}(E[s\mid q(\hat s)]).
\]

If true scores exist on validation simulation, evaluate this quantity and separate representation loss from quantization loss.

For HEP extended fits, explicitly state how Poisson/count information is handled.

---

# 6. Status vocabulary

Use exactly:

- `literature`
- `bridge`
- `project_proved`
- `counterexample`
- `measured`
- `conjecture`
- `open`
- `search_gap`

`project_proved` means internally derived/audited, not published.

---

# 7. Workflow for a theorem/open question

## A. Normalize the target

Return:

- exact statement;
- criterion;
- problem level;
- decision variable;
- assumptions;
- desired conclusion;
- deployability implication;
- information-loss implication.

## B. Query dependencies

Use `CLAIMS.json`. List:

- established prerequisites;
- unresolved dependencies;
- known counterexamples nearby.

Do not prove something already recorded as `project_proved` unless auditing it.

## C. Prior-art triangulation

Find 3–5 nearest sources and state for each:

- exact problem;
- exact result;
- objective;
- feasible set;
- what transfers;
- what does not.

Search alternate terminology: D-optimal quantization, D_s quantization, score-function quantization, conditional-score Fisher information, determinant partition/exchange, minimum-determinant clustering, Hartigan exchange, Mahalanobis/CVT/Bregman, communication-constrained estimation, inference-aware categorization, HEP template binning.

## D. Falsification before proof

Default exact search:

- \(d=1,2,3\);
- smallest rank-feasible \(K\);
- \(N\le10\);
- small integer/rational scores;
- all nonempty partitions;
- unequal positive weights;
- duplicate atoms;
- singleton/tiny cells;
- near-singular information;
- nuisance degeneracy;
- E eigenvalue multiplicity.

If a counterexample is found, minimize and serialize it.

## E. Use the strongest known algebra first

For any finite relocation begin with

\[
\Delta I=\alpha u_au_a^\top-\beta u_bu_b^\top.
\]

Before expensive exact evaluation of a concave criterion, apply supergradient screening:

\[
\Delta F\le \alpha u_a^TGu_a-\beta u_b^TGu_b.
\]

For D use the exact 2x2 determinant ratio. For \(D_s\) track full and nuisance blocks exactly. For E use exact/safe eigenvalue evaluation only after screening.

## F. Proof attempt

List lemmas before proof. For every imported theorem verify the feasible-set assumptions explicitly.

## G. Adversarial audit

Attack:

- strictness and ties;
- singleton/empty cells;
- duplicate scores;
- singular information;
- nuisance singularity;
- atomic laws;
- hidden compactness;
- first-order-to-finite jumps;
- empirical-to-population jumps;
- score-estimation error;
- new-event extension.

## H. Information-loss implication

State whether the theorem gives a bound on:

- \(\eta_D\) or \(\eta_{D_s}\);
- worst normalized retention eigenvalue;
- train-only versus held-out/population performance.

## I. Output contract

Return:

1. Target statement
2. Criterion and problem level
3. Status before attempt
4. Dependencies
5. Nearest literature
6. Counterexample search
7. Algebraic reduction
8. Proof/counterexample/conditional result
9. Adversarial audit
10. Algorithmic consequence
11. Deployability consequence
12. Information-loss consequence
13. Updated status
14. `CLAIMS.json` patch
15. Counterexample/regression artifact if applicable
16. Next dependency-blocking question

---

# 8. Algorithm-development protocol

Evaluate separately:

### Exact objective
Do not label a surrogate D/\(D_s\) unless it is mathematically equal to the target.

### Monotonicity
State whether each accepted update is guaranteed to improve the exact objective.

### Terminal meaning
Exchange-stable? Restricted-family stationary? Global? Certified gap?

### Complexity
Report in \(N,K,d\), and for \(D_s\) also \(d_\psi\).

### Numerical stability
Prefer Cholesky/logdet; retain full recomputation paths for validation.

### Initialization
Compare Fisher-whitened k-means, random/multistart, projected efficient-score D, and domain-specific initialization.

### Deployment
- D exchange terminal state: compile exactly using final centroids + \(I^{-1}\).
- \(D_s\)/E finite assignment: do **not** silently compile; fitting/projection to a geometric family is a new optimization step and must report objective loss.

### Evaluation
On training and held-out samples report:

- objective;
- D/\(D_s\) efficiency;
- normalized retention spectrum;
- worst direction;
- minimum cell mass/yield;
- restart/bootstrap stability;
- upper/lower certificate gap if available;
- geometry disagreement for \(D_s\)/E finite oracles.

---

# 9. Special \(D_s\) protocol

Always distinguish:

### In-bin profiled \(D_s\)
Nuisance information is learned from the same categorical observation.

### Full-data efficient-score projected D upper problem
Uses

\[
\widehat S=S_\psi-B^*S_\lambda
\]

with \(B^*\) from full information. It upper-bounds in-bin \(D_s\) and may use nuisance information external to the bins.

For \(d_\psi=1\), solve the projected scalar interval problem exactly by DP when appropriate.

A strong practical solution should report

\[
\text{upper projected-D value} - \text{achieved in-bin }D_s\text{ value}.
\]

---

# 10. Research priority

Default priority:

1. publication-grade D exchange⇒Voronoi audit;
2. criterion characterization;
3. finite-to-population \(D_s\) bridge and equality/tightness of efficient-score domination;
4. unrestricted D consistency;
5. D/\(D_s\) information-efficiency and high-rate theory;
6. score/classifier perturbation theory;
7. HEP count+shape/nuisance specialization;
8. global complexity/certification;
9. atomic randomization and soft-to-hard limits.

Prefer the question that removes the largest downstream dependency.


## CLAIMS.json lookup protocol

Before working on any theorem:

1. locate the target node in `CLAIMS.json` by `id` or generated index;
2. recursively expand `dependencies`;
3. inspect dependencies with status `project_proved`, `counterexample`, `conjecture`, or `open`;
4. open each node's `proof_location`;
5. check `converse_failures` and `counterexamples` before proposing a stronger statement;
6. patch the registry after the investigation.

Do not read `CLAIMS.json` linearly. Treat it as a theorem dependency graph.
