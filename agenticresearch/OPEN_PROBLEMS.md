# Open problems and theorem cards

**Version:** 2.0 · 26 August 2026  
**Rule:** this file contains only genuinely unresolved questions or publication-grade audits. Results already established in `KNOWN_RESULTS.md` are inputs, not open tasks.

---

# Priority 1 — characterize why D is special

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
- exact D-style geometry theorem is false.

## OP3. Quantitative E necessity bound under a spectral gap

For simple \(\lambda_{\min}\) separated by gap \(\gamma>0\), determine whether exchange stability implies an approximate rank-one-Voronoi rule with an explicit \(O(w/\gamma)\)-type bound.

Use second-order eigenvalue perturbation; search counterexamples before proof.

---

# Priority 2 — finish practical \(D_s\) theory

## OP4. Finite-to-population \(D_s\) bridge

Current project result gives an \(O(K/N)\)-type geometric violation bound at balanced exchange-stable states.

**Question.** Under atomlessness, minimum-cell-mass, nuisance-block conditioning, and boundary-margin assumptions, does this imply convergence of empirical exchange-stable/global finite \(D_s\) solutions to population stationary deployable quantizers?

Distinguish:

- unrestricted finite assignments;
- explicit affine/semimetric inductive family;
- population optimum.

## OP5. Population common-metric / efficient-score geometry for \(D_s\)

For regular population \(D_s\), make the first-order efficient-semi-metric statement fully rigorous and characterize when one common deployable affine/Voronoi rule exists.

If it fails in general, identify minimal additional assumptions or necessary correction terms.

## OP6. Tightness/equality conditions for efficient-score domination

We know

\[
S_\psi(I_q)\preceq\operatorname{Var}(E[\widehat S\mid q]).
\]

Characterize equality:

- for a fixed \(q\);
- at the global optimum;
- asymptotically as \(K\to\infty\).

Interpret the finite-K gap as the cost of estimating nuisance structure from bins rather than using the full-data nuisance projection.

## OP7. Best practical \(D_s\) solver with theorem-backed certificate

This is now an algorithm-engineering/theory synthesis task, not a request to re-derive the exact move oracle.

Benchmark a pipeline:

1. full-data efficient score;
2. exact/projected D upper problem (DP if \(d_\psi=1\));
3. soft/affine inductive \(D_s\) fit;
4. exact finite \(D_s\) exchange audit/refinement where well posed;
5. report upper-bound gap and geometric-disagreement gap.

Need robust Cholesky/block updates and held-out evaluation.

---

# Priority 3 — unrestricted empirical/population consistency

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

---

# Priority 4 — global complexity and stronger certificates

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

Goal: certify substantially larger realistic instances.

---

# Priority 5 — information-loss theory

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

# Priority 6 — score-oracle and classifier robustness

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

# Priority 7 — HEP/template-fit specialization

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

# Priority 8 — robustness away from the reference point

## OP23. Parameter-mismatch degradation

For a quantizer optimized at \(\theta_0\), bound the D/\(D_s\) loss at \(\theta_0+\delta\). Seek local second-order perturbation results and practical validation metrics.

## OP24. Multi-reference / robust quantization

Study expected or minimax objectives over a parameter region. Determine whether affine/common-metric geometry survives or becomes a mixture of local metrics.

---

# Priority 9 — randomization, atoms, and soft-to-hard limits

## OP25. Atomic randomization gap

For finite/atomic score laws, determine whether splitting an atom among labels can strictly improve D or \(D_s\). Find the smallest exact counterexample or prove conditions for no gap.

## OP26. Soft-to-hard zero-temperature limit

When do stationary points or optima of a temperature-softened randomized affine/Voronoi family converge to stationary/optimal hard partitions as \(\tau\to0\)?

Separate:

- objective convergence for a fixed parameter path;
- convergence of global optima;
- convergence of local stationary branches.

---

# Agent completion rule

After every investigation:

1. patch `CLAIMS.json`;
2. add/minimize any counterexample in `COUNTEREXAMPLES/`;
3. update `LITERATURE.md` with exact theorem/page metadata for new prior art;
4. state whether `PROBLEM.md` assumptions change;
5. add numerical regression tests if the claim is computational;
6. identify the next **dependency-blocking** question.
