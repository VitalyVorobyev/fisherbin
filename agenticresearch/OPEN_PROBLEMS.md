# Open problems — the research programme queue

**Version:** 3.0 · 28 August 2026
**Rule:** this file contains only genuinely unresolved questions. Results established in `KNOWN_RESULTS.md` are inputs, not open tasks.

This is the **single priority queue** of the project, organized as eight
research programmes (the narrative and goal live in
`research-plan-proposal.md`). Ordering is **product-first**: programmes whose
theorems unblock shippable ScoreQuant capabilities outrank purely academic
branches. A session works on a `WORK/active/` packet drawn from a programme —
the whole branch, not one OP leaf. OP numbers are stable ids; claim
`proof_location`s point at them.

---

# P1 · DS-POPULATION-BRIDGE — finish practical \(D_s\) theory

*Descends from research-plan-proposal.md Session 8 (moved to "Now" by the product-first decision).*
*Product payoff: unlocks `compile_quantizer` for profiled criteria — the largest math-gated library feature.*
*Status 28 Aug 2026: OP4, OP5, and the fixed-\(q\)/asymptotic parts of OP6 are resolved (`KNOWN_RESULTS.md` DS11–DS14; packet `WORK/completed/DS-POPULATION-BRIDGE.md`). The conditional bridge theorem DS14 awaits its independent audit (`WORK/active/AUDIT-DS-POPULATION-BRIDGE.md`); the surviving mathematical gap is OP28.*

## OP28. Margins at finite \(D_s\) optima

The conditional bridge DS14 assumes, along the sequence of empirical
solutions: a cell-mass margin, a conditioning margin, and a
projected-centroid separation margin.

**Question.** For light-tailed atomless laws, do global (or exchange-stable)
finite \(D_s\) optima satisfy these margins asymptotically, almost surely?
Sub-questions:

- Singleton cells persist at exact global optima through \(N=18\)
  (`NUMERICAL_EVIDENCE.md` N-DS-BRIDGE-TREND); the extreme-cell information
  heuristic (\(\sim2\log N/N\)) suggests they die out for Gaussian-tailed
  laws — prove or refute.
- Exact degenerate global ties exist (`CE-DS-DEGENERATE-GLOBAL-TIE-001`):
  characterize the laws/sample events for which the separation margin fails,
  and whether the merged-rule bridge conclusion is the best possible there.
- Does the margin-compatible geometric optimum \(v^*\) of DS14 equal the
  unrestricted population supremum over all measurable quantizers (ties into
  C2 attainment)?
- How does efficient-score-domination equality (DS11(a)) behave at global
  optima?

A positive resolution upgrades DS14 from conditional to unconditional for the
covered laws and unlocks an audited `compile_quantizer` for profiled criteria.

## OP7. Best practical \(D_s\) solver with theorem-backed certificate

This is now an algorithm-engineering/theory synthesis task, not a request to re-derive the exact move oracle.

Benchmark a pipeline:

1. full-data efficient score;
2. exact/projected D upper problem (DP if \(d_\psi=1\));
3. soft/affine inductive \(D_s\) fit;
4. exact finite \(D_s\) exchange audit/refinement where well posed;
5. report upper-bound gap and geometric-disagreement gap.

Need robust Cholesky/block updates and held-out evaluation. The multivariate
(\(d_\psi>1\)) certified upper problem — where the library currently refuses
rather than approximates — belongs here: a certified convex relaxation with a
stated gap would meet the project's standards.

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
(statement in `KNOWN_RESULTS.md` § E6).

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
