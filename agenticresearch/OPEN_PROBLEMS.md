# Open problems — the research programme queue

**Version:** 4.0 · 1 September 2026
**Rule:** this file contains only genuinely unresolved questions. Results established in `KNOWN_RESULTS/` are inputs, not open tasks.

This is the **single priority queue** of the project, organized as seven live
research programmes (the narrative and goal live in
`research-plan-proposal.md`). Ordering is **product-first**: programmes whose
theorems unblock shippable ScoreQuant capabilities outrank purely academic
branches. A session works on a `WORK/active/` packet drawn from a programme —
the whole branch, not one OP leaf. OP numbers are stable ids; claim
`proof_location`s point at them.

---

## Closed programme P1 — deployment verdict (1 September 2026)

P1 is complete and is no longer a live programme. DS19 closes its deployment
question with a **Tier A REDUCED** verdict: the scalar tilt-DP bracket is valid,
has an exact saddle closure condition, admits fixed-tilt exact evaluation and
polynomial certified-accuracy minimization, and its DS18 interval-DP primal is
value-consistent; exact polynomial bit complexity for variable
\((K,d_\lambda)\) is isolated as OP31. Strong duality fails by an exact
order-one gap. The observable decision is therefore to certify an exhibited
regular saddle, report a nonclosed bracket without claiming optimality, use the
distinct projected efficient-score route where authorized, apply a DS14
companion only under all audited sequence hypotheses, and otherwise refuse.
No public compile surface is authorized before an independent DS19 audit.

Tier B is **DISPROVED**: the multivariate matrix-tilt outer objective need not
be quasiconvex (`DS-MATRIX-TILT-NONQUASICONVEX`). The remaining academic
margins and stable-basin questions are OP29 in P6 and OP30 in P7.

---

# P2 · SCORE-ORACLE-ROBUSTNESS — estimated scores and classifiers

*Descends from research-plan-proposal.md Session 10 (moved to "Now").*
*Product payoff: honest error bars for every real dataset; the library book calls this "the largest practical gap in the framework". Active packet: `WORK/active/SCORE-ORACLE-ROBUSTNESS.md`.*

## OP17. Perturbation theory for estimated scores

Assume \(\|\hat s-s\|_{L^2}\le\varepsilon\) or a stronger bound. Control:

- cell moments;
- \(I_q\);
- D/\(D_s\) objective;
- efficiency;
- geometric boundaries under a margin condition.

## OP18. Classifier calibration error → Fisher loss

Relate posterior/ratio calibration error to:

1. density-ratio error;
2. score error;
3. pre-quantization representation loss;
4. final D/\(D_s\) efficiency.

This should produce a meaningful classifier-quality requirement beyond AUC.

## OP19. Estimating representation versus quantization loss

When truth scores exist only on simulation, devise cross-fitted estimators and uncertainty bars for

\[
I_R=\operatorname{Var}(E[s\mid R]),
\qquad
I_q=\operatorname{Var}(E[s\mid q(R)]).
\]

---

# P3 · INFORMATION-BUDGET — how many bins does a target need

*Descends from the information-loss theory tier; ground truth from the exact scalar DP solver.*
*Product payoff: a user-facing bin-count recommendation ("bins needed for target efficiency").*

## OP14. Sharp D-efficiency versus K

Study

\[
\eta_D(K)=
\sup_{|q|=K}
\left(\frac{\det I_q}{\det I_{\rm full}}\right)^{1/d}.
\]

Find distribution-dependent/distribution-free bounds and inversion formulas for “how many bins are needed for target efficiency?”.

## OP15. High-rate \(K\to\infty\) asymptotics

Let \(L=I_{\rm full}-I_q\). Expand

\[
\log\det(I_{\rm full}-L)
=
\log\det I_{\rm full}
-\operatorname{tr}(I_{\rm full}^{-1}L)
-\frac12\operatorname{tr}[(I_{\rm full}^{-1}L)^2]-\cdots.
\]

Working hypothesis:

- first order reduces to Fisher-whitened quadratic quantization;
- genuinely D-specific cell-shape effects appear at second order.

Connect to Zador/Gersho high-rate theory.

## OP16. Direction-wise guarantees from determinant efficiency

Given \(\eta_D\), derive useful bounds on \(\lambda_{\min}(R)\), and conversely. Identify additional assumptions under which determinant retention controls worst-direction loss tightly.

---

# P4 · DEPLOYMENT-ROBUSTNESS — away from the reference point, with error bars

*Product payoff: retention numbers with uncertainty, and a story for the assumption "most likely to be violated quietly" (the local reference point).*

## OP23. Parameter-mismatch degradation

For a quantizer optimized at \(\theta_0\), bound the D/\(D_s\) loss at \(\theta_0+\delta\). Seek local second-order perturbation results and practical validation metrics.

## OP24. Multi-reference / robust quantization

Study expected or minimax objectives over a parameter region. Determine whether affine/common-metric geometry survives or becomes a mixture of local metrics.

## OP27. Finite-sample uncertainty for retention estimates

Every retention number the library reports is a point estimate. Develop
influence-function or bootstrap confidence intervals for retention
functionals (e.g. geometric-mean retention), handling the non-smoothness of
hard assignment at cell boundaries. Pairs naturally with OP17.

---

# P5 · HEP-SPECIALIZATION — template fits made mathematically explicit

*Descends from research-plan-proposal.md Session 9.*
*Product payoff: the connection to a real multicomponent template fit becomes theorems and recipes rather than motivational prose.*

## OP20. Canonical parameterization for linear mixtures

For mixture fractions and extended yields, derive numerically stable score coordinates under:

- simplex constraints;
- reference-component coordinates;
- unconstrained local coordinates;
- yield parameterization.

Clarify D invariance and \(D_s\) POI/nuisance transformations.

## OP21. Count + shape information in extended fits

Formalize

\[
I_{\rm total}=I_{\rm count}+I_{\rm shape}
\]

for the relevant extended-likelihood conventions and specify exactly what event hard quantization changes.

Produce a canonical API/evaluation recipe.

## OP22. Systematic template morphing and nuisance scalability

Study score/efficient-score construction for calibration, template-shape, normalization, MC-statistical, and correlated nuisance parameters without making the operational score dimension impractical.

---

# P6 · D-CORE-COMPLETION — the paper's remaining spine

*Descends from research-plan-proposal.md Sessions 3, 4, 7. Queued, not blocking: the D-core paper is harvested when this completes.*

## OP8. Unrestricted D global consistency

Restricted compact affine-max consistency is already established in the project.

The unresolved question is stronger:

> Do unrestricted empirical global D optima converge in value/decision to population global D quantizers under natural assumptions?

D finite geometric realizability may allow reduction to a controlled geometric class, but the metric/centroids are data-dependent and singular boundaries must be controlled.

## OP9. Consistency of exchange-stable D solutions

Do one-point-exchange-stable empirical D quantizers converge to the population stationary set? What assumptions prevent spurious local branches from persisting?

Possible tools: set-valued M-estimation, stability margins, uniform convergence of move gains.

## OP10. Unrestricted \(D_s\)/E consistency

Finite global optima can be non-geometric for \(D_s\) and E. Determine whether their non-geometric discrepancy vanishes asymptotically and whether global finite objective values converge to the corresponding population hard-quantizer optimum.

The programme also carries the empirical half of the paper story (proposal
Session 7): the controlled D-versus-trace/k-means benchmark establishing
*when* D differs, not merely that it wins on its own objective.

## OP29. Margins beyond conditional centering

The deployment-facing scalar remainder is closed by DS19. Two vector academic
branches remain:

- **\(d_\psi>1\):** complete the uniqueness and rigidity theory for vector-D
  quantization of the efficient score before transferring DS15's
  degenerate-attainer dichotomy.
- **\(d_\lambda\ge2\):** above the load-bearing centered-sample threshold
  \(K\ge d_\psi+d_\lambda+1\), construct or refute a vector-(R) steering
  mechanism spanning all nuisance directions. At
  \(K=d_\psi+d_\lambda\), `CE-DS-MARGINS-RANK-VACUITY-001` already shows
  that every feasible profiled value is zero.

These are P6 consistency/rigidity questions, not deployment blockers. Do not
reopen the audited scalar DS15, DS18, or DS19 claims.

Target claim: `OPEN-DS-MARGINS-NONCENTERED`.

---

# P7 · FOUNDATIONS — why D is special, complexity, randomization

*Academic anchor; also decides permanently whether A/E solvers are ever worth building.*

## OP1. Which concave matrix criteria have finite exchange ⇒ first-order geometry?

For retained-information partitions and concave \(F(I)\), characterize when

\[
\text{one-point exchange stable}
\Rightarrow
\text{pointwise first-order assignment under a common }G.
\]

Known anchors:

- true for full D under current project theorem;
- false for A;
- false for \(D_s\);
- false naively for E, with nonsmooth complications;
- the reverse/screening direction follows from concavity for all four.

Desired result: necessary/sufficient curvature/operator inequality, useful subclass, or impossibility theorem showing log-det is essentially exceptional.

## OP2. Quantitative finite-geometry bound for A

Derive or disprove an A analogue of the \(D_s\) \(O(w_i(1/W_a+1/W_b))\) necessity bound.

Current facts:

- exact \(O(d^2)\) A move oracle exists;
- concavity screening exists;
- exact D-style geometry theorem is false (`CE-A-DSTYLE-001`).

## OP3. Quantitative E necessity bound under a spectral gap

For simple \(\lambda_{\min}\) separated by gap \(\gamma>0\), determine whether exchange stability implies an approximate rank-one-Voronoi rule with an explicit \(O(w/\gamma)\)-type bound.

Use second-order eigenvalue perturbation; search counterexamples before proof.
The population-level companion question is `OPEN-E-COMMON-SUPERGRADIENT`
(statement in `KNOWN_RESULTS/06-e-optimality.md` § E6).

## OP11. Parameterized complexity

Determine:

- NP-hardness for fixed \(d=2\), variable \(K\)?
- NP-hardness for \(K=d+1\), variable \(d\)?
- FPT in \(K+d\)?
- W[1]/ETH bounds?
- tightness of the current \(N^{O(Kd)}\) exact route?

Do not import k-means or D-optimal subset-selection hardness without a valid reduction.

## OP12. Stronger local neighborhoods

Analyze two-point swaps, move-two, merge-split, boundary perturbations, and rank-\(r\) determinant updates.

Questions:

- approximation guarantees from stronger local stability?
- does 2-swap stability imply stronger geometry?
- can these neighborhoods materially reduce multistart dependence?

## OP13. Stronger branch-and-bound upper bounds

Improve singleton-refinement bounds using moment relaxations, SDP/convex upper envelopes, affine-realizability pruning, or minimum-cell-mass constraints.

Goal: certify substantially larger realistic instances. (A materially better
bound is also the mathematical alternative to the deferred Rust port of the
library's `certify.py`.)

## OP25. Atomic randomization gap

For finite/atomic score laws, determine whether splitting an atom among labels can strictly improve D or \(D_s\). Find the smallest exact counterexample or prove conditions for no gap.

## OP26. Soft-to-hard zero-temperature limit

When do stationary points or optima of a temperature-softened randomized affine/Voronoi family converge to stationary/optimal hard partitions as \(\tau\to0\)?

Separate:

- objective convergence for a fixed parameter path;
- convergence of global optima;
- convergence of local stationary branches.

## OP30. Inhabitation and selection of margin-retaining stable states

DS17 already proves that the full (M2)+(M3)+(M5) ordinary-stable branch is
eventually empty on its scalar conditionally centered class. Two foundational
remainders survive in P7:

- **(M5)-free tracking:** decide whether empirical exchange-stable sequences
  can track coincident-projected-centroid wasted-cell configurations.
- **Constrained-value regularity:** prove or refute attainment and one-sided
  continuity of \(v^*(\kappa)\) and \(v^{*+}(\kappa)\) under their distinct
  DS16 conventions. The Gaussian sign-split family proves nonemptiness for
  the closed constraint when \(\kappa\le1/\pi\), not attainment or
  continuity.

Solver design and non-centered value transfer are closed out of this OP by
DS19. No wasted-cell state becomes deployable merely by retaining a nuisance
floor.

Target claim: `OPEN-DS-STABLE-BASINS`.

## OP31. Exact bit complexity of the tilt-DP dual

For positive rational weights and a rational score table, with \(K\) and
\(d_\lambda\) part of the input, decide whether

\[
\min_\beta \hat v_K(S_\psi-\beta S_\lambda)
\]

admits exact algebraic optimization in polynomial bit complexity using the
fixed-tilt interval-DP oracle, including ties and active refinements, without
materializing a potentially superpolynomial parametric-DP envelope.

DS19 already proves exact fixed-tilt evaluation, polynomial
certified-\(\varepsilon\) minimization, and exact computation for fixed
\((K,d_\lambda)\). General parametric-shortest-path envelope lower bounds do
not automatically transfer to this restricted grouping DP; closure requires a
valid hardness reduction or a structure-exploiting exact algorithm.

Target claim: `OPEN-DS-TILT-DUAL-EXACT-COMPLEXITY`.

---

# P8 · LITERATURE-GRAPH — coverage you can defend

*Infrastructure; can interleave with any programme. Procedure and artifacts: `protocols/literature.md`, `LITERATURE/`.*

Run bidirectional citation snowballing from `LITERATURE/seeds.md` to citation
saturation, recording per-round counts. The final claim-by-claim adversarial
novelty search (proposal Session 12) is **deferred until the publication
decision** — novelty is searched against frozen theorem statements, not
moving targets.

---

# Agent completion rule

After every investigation, run the completion checklist in
`protocols/theorem.md` (registry patch, counterexample minimization,
literature update, assumption review, regression tests, next
dependency-blocking question) and update your `WORK/` packet.
