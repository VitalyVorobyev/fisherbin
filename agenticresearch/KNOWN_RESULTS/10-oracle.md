# 10. Score/density-ratio/classifier access

> Part of the ScoreQuant known-results ledger. Read `PROBLEM.md` first and
> `KNOWN_RESULTS/index.md` for the status vocabulary and the chapter map.
> Resolve any claim id with `python py/registry.py show <ID> --deps --proof`.

## O1. Density ratios suffice for local scores — [BRIDGE]

**Claims:** RATIO-LOCAL-SCORE

\[
s(x)=\left.\nabla_\theta\log\frac{p(x\mid\theta)}{p(x\mid\theta_0)}\right|_{\theta_0}.
\]

Full absolute densities are not required if the relevant local density ratio is available.

## O2. Linear-mixture component ratios suffice — [BRIDGE]

**Claims:** MIXTURE-RATIO-SCORE

For

\[
p(x\mid\theta)=\sum_\alpha\theta_\alpha\phi_\alpha(x),
\]

score coordinates depend on \(\phi_\alpha(x)/\sum_\beta\theta_{0\beta}\phi_\beta(x)\). Ratios to one reference component therefore suffice exactly after algebraic reconstruction.

## O3. Calibrated classifier posteriors provide ratios — [LIT/BRIDGE]

**Claims:** CLASSIFIER-MIXTURE-SCORE-FORMULA, CLASSIFIER-RATIO-ORACLE

With class priors \(\pi_\alpha\), posterior odds recover component density ratios. In the mixture parameterization,

\[
\boxed{
s_\alpha(x)=
\frac{\eta_\alpha(x)/\pi_\alpha}
{\sum_\beta\theta_{0\beta}\eta_\beta(x)/\pi_\beta}.
}
\]

Estimated classifiers solve the exact score problem only to the extent that they recover calibrated ratios.

## O4. True retained FI under an estimated score — [BRIDGE]

**Claims:** PROXY-TRUE-RETAINED-FI

If the quantizer uses \(\hat s\), the actual retained Fisher information is

\[
\boxed{
\operatorname{Var}(E[s\mid q(\hat s)]),
}
\]

not \(\operatorname{Var}(E[\hat s\mid q(\hat s)])\) unless \(\hat s=s\) in the relevant sense.

## O5. Representation loss and quantization loss separate — [BRIDGE]

**Claims:** REPRESENTATION-QUANTIZATION-LOSS

For a representation \(R(X)\),

\[
I_R=\operatorname{Var}(E[s\mid R]),
\qquad
I_q\preceq I_R\preceq I_{\rm full}.
\]

This separates oracle/representation loss from hard-quantization loss whenever truth scores are available for validation.

---

## O6. Frozen-rule scalar retention: plug-in asymptotics and a consistent variance — [BRIDGE]

**Claims:** RETENTION-PLUGIN-CLT-FROZEN-SCALAR, RETENTION-PLUGIN-COVERAGE-DOOR3

*Recorded 5 September 2026 by the SCORE-ORACLE-ROBUSTNESS session (packet
`WORK/completed/SCORE-ORACLE-ROBUSTNESS.md`). Verdict: **proved**, as a direct
corollary of the delta method; the special case of OP27 it settles is stated
exactly below and the broad claim `OPEN-RETENTION-UNCERTAINTY` stays open.
Instrument `py/score_oracle_retention_uncertainty.py`; artifacts under
`WORK/artifacts/SCORE-ORACLE-ROBUSTNESS/`. Not independently audited.*

### O6.0 Normalized target (protocol A)

- **Level:** `information_accounting`, conditional on a frozen
  `empirical_inductive_quantizer`. **Criterion:** the scalar retention ratio
  (for one score coordinate the D-, A- and E-efficiencies coincide with it).
- **Frozen:** training data, provider \(\hat s\), rule \(q\), reference point
  \(\theta_0\), finite \(K\). **Random:** an independent evaluation sample
  \(X_1,\dots,X_n\) iid from the reference law \(P\), equally weighted.
- **Observables:** \(S_i=s(X_i)\) (true scalar score) and
  \(Z_i=q(\hat s(X_i))\in\{1,\dots,K\}\). Because \(q\circ\hat s\) is a fixed
  measurable map, the pairs \((S_i,Z_i)\) are iid with a fixed joint law: the
  boundary non-smoothness of OP27 never enters this special case.
- **Population target:**
  \[
  p_b=P(Z=b),\qquad m_b=E[S\,\mathbf 1_{Z=b}],\qquad v=E[S^2],\qquad
  \eta=\frac{\sum_b m_b^2/p_b}{v},\qquad c_b=\frac{m_b}{p_b}.
  \]
  Under a regular model with \(E[S]=0\), \(v=I_{\rm full}\) and
  \(\sum_b m_b^2/p_b=I_Z\) (U1, `FI-QUANT-IDENTITY`, with \(q\) fixed in
  \(\theta\)), so \(\eta=\operatorname{Var}(E[s\mid q(\hat s)])/\operatorname{Var}(s)\)
  is exactly the *true* retained fraction of O4 (`PROXY-TRUE-RETAINED-FI`).
- **Estimator:** the ordinary plug-in ratio on the same evaluation sample,
  \(\hat p_b=n_b/n\), \(\hat m_b=n^{-1}\sum_i S_i\mathbf 1_{Z_i=b}\),
  \(\hat v=n^{-1}\sum_i S_i^2\), \(\hat\eta=\sum_b\hat m_b^2/\hat p_b\,/\,\hat v\),
  with \(0/0:=0\) for an empty cell. Scores are never centred.
- **Excluded (packet scope):** importance weights, growing \(K\), refitting the
  rule on the evaluation sample, boundary stability, \(D_s\), classifier
  calibration theory, bootstrap comparisons, any public uncertainty API.

**Assumptions.**
(A1) \(p_b>0\) for every \(b\);
(A2) \(E[S^4]<\infty\);
(A3) \(v=E[S^2]>0\);
(A4) \(\sigma^2>0\) with \(\sigma^2\) defined in O6.2.
(A2) is automatic for bounded scores, e.g. every mixture-fraction score at an
interior reference point (\(|s|\le\max_k 1/\theta_{0k}\)); (A3) is the
nonsingular unbinned-information hypothesis the library already imposes.

### O6.1 Finite-sample identity — [BRIDGE]

For every sample, with \(\hat c_b=\hat m_b/\hat p_b\) on nonempty cells,

\[
\boxed{\;
\hat\eta \;=\; 1-\frac{\sum_i\big(S_i-\hat c_{Z_i}\big)^2}{\sum_i S_i^2}
\;}
\]

so \(\hat\eta\) is one minus the within-cell residual sum of squares about the
cell means over the *uncentred* total sum of squares, and \(0\le\hat\eta\le1\)
always. Empty cells contribute nothing to either side, which is what the
\(0/0:=0\) convention encodes. For scalar scores \(\hat\eta\) coincides with the
public `information_report(...).geometric_mean_retention` (the whitening
divides by \(\hat v\); selftest agreement \(5\cdot10^{-17}\)).

*Proof.* \(\sum_i(S_i-\hat c_{Z_i})^2=\sum_b\big[\sum_{i\in b}S_i^2-n_b\hat c_b^2\big]
=\sum_iS_i^2-\sum_b n_b\hat c_b^2\) and \(n_b\hat c_b^2=(\sum_{i\in b}S_i)^2/n_b
=n\,\hat m_b^2/\hat p_b\). Divide by \(\sum_iS_i^2=n\hat v\). \(\square\)

### O6.2 Conditional asymptotic normality — [BRIDGE]

Under (A1)–(A3), conditionally on the frozen rule,

\[
\boxed{\;
\sqrt n\,(\hat\eta-\eta)\;\Rightarrow\;N(0,\sigma^2),\qquad
\sigma^2=E[\psi(S,Z)^2],\qquad
\psi(S,Z)=\frac{(1-\eta)\,S^2-(S-c_Z)^2}{v}.
\;}
\]

Equivalently, writing the numerator influence \(N_1=2c_ZS-c_Z^2\) (so that
\(E[N_1]=\eta v\)) and the denominator influence \(S^2\),

\[
\sigma^2=\frac{\operatorname{Var}(N_1)-2\eta\operatorname{Cov}(N_1,S^2)+\eta^2\operatorname{Var}(S^2)}{v^2},
\]

which is the numerator–denominator covariance form the packet asked for.

*Proof.* Let \(T_i=(\mathbf 1_{Z_i=b},\,S_i\mathbf 1_{Z_i=b},\,S_i^2)_{b=1..K}\in\mathbb R^{2K+1}\),
\(\theta=E[T_1]=(p_b,m_b,v)_b\). By (A2) \(T_1\) has finite second moments (the
largest is \(E[S^4]\)), so the multivariate CLT gives
\(\sqrt n(\bar T-\theta)\Rightarrow N(0,\Sigma)\), \(\Sigma=\operatorname{Cov}(T_1)\).
The map \(g(p,m,v)=\sum_b m_b^2/p_b\,/\,v\) is \(C^\infty\) on
\(\{p_b>0\ \forall b,\ v>0\}\), which contains \(\theta\) by (A1), (A3). The delta
method (van der Vaart 1998, Thm 3.1) yields
\(\sqrt n(g(\bar T)-g(\theta))\Rightarrow N(0,\nabla g^\top\Sigma\nabla g)\), and
\(\nabla g^\top\Sigma\nabla g=\operatorname{Var}(\nabla g^\top T_1)\). With

\[
\frac{\partial g}{\partial p_b}=-\frac{m_b^2}{p_b^2v},\qquad
\frac{\partial g}{\partial m_b}=\frac{2m_b}{p_bv},\qquad
\frac{\partial g}{\partial v}=-\frac{\eta}{v},
\]

\[
\nabla g^\top(T_1-\theta)
=\sum_b\Big[-\frac{m_b^2}{p_b^2v}(\mathbf 1_{Z=b}-p_b)+\frac{2m_b}{p_bv}(S\mathbf 1_{Z=b}-m_b)\Big]-\frac{\eta}{v}(S^2-v)
=\frac{2c_ZS-c_Z^2-\eta S^2}{v}+(\eta-2\eta+\eta)=\psi(S,Z),
\]

and \(2c_ZS-c_Z^2=S^2-(S-c_Z)^2\) gives the boxed form; \(E[\psi]=0\) is the
vanishing of the constant terms, so \(\operatorname{Var}(\psi)=E[\psi^2]\).
Finally \(\hat\eta=g(\bar T)\) on the event that every cell is nonempty, whose
complement has probability at most \(\sum_b(1-p_b)^n\to0\) by (A1); hence
\(\hat\eta\) and \(g(\bar T)\) share the limit law. \(\square\)

### O6.3 A consistent implementable variance — [BRIDGE]

Let \(\hat\psi_i=\big((1-\hat\eta)S_i^2-(S_i-\hat c_{Z_i})^2\big)/\hat v\) and
\(\hat\sigma^2=n^{-1}\sum_i\hat\psi_i^2\). Then \(\sum_i\hat\psi_i=0\) exactly
(by O6.1), and under (A1)–(A3) \(\hat\sigma^2\to\sigma^2\) almost surely.

*Proof.* Expanding, \(n^{-1}\sum_i\hat\psi_i^2\) is a fixed polynomial in
\((\hat\eta,\hat v^{-1},\hat c_1,\dots,\hat c_K)\) whose coefficients are the
within-cell empirical moments \(\hat M_{b,k}=n^{-1}\sum_iS_i^k\mathbf 1_{Z_i=b}\),
\(k=0,\dots,4\). By (A2) and the strong law each \(\hat M_{b,k}\to M_{b,k}=E[S^k\mathbf 1_{Z=b}]\)
a.s.; by (A1) \(\hat p_b=\hat M_{b,0}\to p_b>0\) so \(\hat c_b\to c_b\); by (A3)
\(\hat v\to v>0\); hence \(\hat\eta\to\eta\). The polynomial is continuous at the
limit point, and its value there is \(E[\psi^2]\) expanded in the same moments.
\(\square\)

### O6.4 Wald interval — [BRIDGE]

Under (A1)–(A4), \(P\big(\eta\in\hat\eta\pm z_{1-\alpha/2}\,\hat\sigma/\sqrt n\big)\to1-\alpha\)
(O6.2, O6.3 and Slutsky). **Unsupported cases and degeneracies:**

- *(A4) fails* iff \(\psi=0\) a.s., i.e. iff for a.e. \(b\) the conditional law
  of \(S\) given \(Z=b\) is supported on the roots of
  \((s-c_b)^2=(1-\eta)s^2\) — at most two atoms per cell. This includes both
  endpoints: \(\eta=1\) (\(S=c_Z\) a.s.) and \(\eta=0\) (all \(c_b=0\)). There the
  first-order limit is degenerate, \(n(\hat\eta-\eta)\) has a non-normal
  quadratic-form limit (not derived here), and the Wald interval is not
  supported. If \(S\mid Z=b\) is atomless on one cell of positive probability,
  (A4) holds automatically.
- *Empty evaluation cells:* handled by \(0/0:=0\); their probability vanishes
  exponentially under (A1). No uniformity over small \(p_b\) is claimed: a cell
  with \(p_b\) of order \(1/n\) is outside the theorem.
- *Edges:* the interval may leave \([0,1]\) near \(\eta\in\{0,1\}\); no
  transformation was attempted (one estimator, one interval, per packet).
- *No finite-sample guarantee:* coverage below is evidence of the first-order
  statement only.

### O6.5 What the interval does and does not measure — [BRIDGE]

The interval is for the **true** retention \(\eta\), conditional on the frozen
rule. The library's self-reported surrogate replaces \(S\) by \(\hat s\); its
population value \(\tilde\eta=\sum_b\tilde m_b^2/p_b/\tilde v\) with
\(\tilde m_b=E[\hat s\mathbf 1_{Z=b}]\), \(\tilde v=E[\hat s^2]\) is a *different
number* (O4). The same theorem applies verbatim to the surrogate plug-in as an
estimator of \(\tilde\eta\), so the surrogate carries a valid interval around the
wrong target. The gap \(\tilde\eta-\eta\) is bias of the proxy, of order one in
\(n\), and the \(O(n^{-1/2})\) interval excludes \(\tilde\eta\) with probability
\(\to1\): evaluation uncertainty and proxy discrepancy separate cleanly once an
oracle-score evaluation sample exists. Without an oracle sample nothing here
applies (OP27's remainder, and OP17/OP18).

### O6.6 Self-adversarial pass (protocol G)

- *Ties, duplicate scores:* irrelevant; the functional is smooth in moments.
- *Singleton/empty cells:* O6.4; under (A1) transient.
- *Singular information:* excluded by (A3); with \(v=0\) the target is
  undefined, matching the library's refusal.
- *Nuisance singularity, \(D_s\):* out of scope (scalar, no nuisance).
- *Atomic laws:* the only route to (A4) failure with \(0<\eta<1\); recorded above.
- *Hidden compactness:* none used.
- *First-order-to-finite jumps:* none claimed; measured \(O(1/n)\) bias below.
- *Empirical-to-population jumps:* none — the rule is frozen, the sample is
  independent of it; a rule refitted on the evaluation sample voids the iid
  structure and is exactly what OP27 still owes.
- *Score-estimation error:* enters only through the label map and the
  target's definition; the theorem is conditional on \(\hat s\).
- *Heavy tails:* (A2) is used for the CLT of \(S^2\) and the SLLN of fourth
  within-cell moments; with only \(E[S^2]<\infty\) the denominator CLT fails.

### O6.7 Measured (protocol D, run before the proof was trusted) — [MEASURED]

Frozen rule: door3 rung `n_per_class = 15` (classifier seed 101, four cells,
D-exchange seed 7, the rung with the largest published proxy gap). The
instrument reproduces the published ladder on door3's own test sample
(surrogate 0.9658, true 0.8847). Population references by two independent
composite Gauss–Legendre routes (disagreement \(1.1\cdot10^{-16}\), tail
truncation \(<10^{-18}\), closed-form score vs the exact provider
\(9\cdot10^{-16}\)); \(E[S]=-4.5\cdot10^{-17}\) confirms the zero-mean score.

| quantity | value |
|---|---|
| \(\eta\) (true retention) | 0.893663 |
| \(\sigma\) | 0.235410 |
| \(\tilde\eta\) (proxy population value) | 0.967064 |
| proxy gap \(\tilde\eta-\eta\) | 0.073402 |
| cell probabilities | 0.4953, 0.1215, 0.2193, 0.1638 |
| \(E[S^4]\) | 2.7336 |

Coverage of the 95% Wald interval, 2000 independent evaluation samples per
size, `SeedSequence(20260905)`:

| \(n\) | coverage ± SE | SD\((\hat\eta)\) | \(\sigma/\sqrt n\) | mean \(\hat\sigma/\sqrt n\) | rel. RMSE \(\hat\sigma/\sigma\) | \(n\cdot\)bias | studentized skew | covers \(\tilde\eta\) |
|---|---|---|---|---|---|---|---|---|
| 100 | 0.913 ± 0.006 | 0.02335 | 0.02354 | 0.02255 | 0.167 | 0.33 | +1.06 | 0.046 |
| 300 | 0.934 ± 0.006 | 0.01356 | 0.01359 | 0.01342 | 0.088 | 0.35 | +0.20 | 0.000 |
| 1000 | 0.953 ± 0.005 | 0.00738 | 0.00744 | 0.00742 | 0.049 | 0.18 | +0.11 | 0.000 |
| 3000 | 0.949 ± 0.005 | 0.00433 | 0.00430 | 0.00429 | 0.029 | 0.40 | +0.12 | 0.000 |

Reading: the sampling spread matches \(\sigma/\sqrt n\) at every size and
\(\hat\sigma\) converges to \(\sigma\); coverage reaches nominal by
\(n=1000\). The \(n=100\) shortfall is a second-order effect — the statistic
studentized with the *population* \(\sigma\) has skew \(-0.30\) and SD 0.99,
while the plug-in studentized statistic has skew \(+1.06\): \(\hat\sigma\) is
small precisely when \(\hat\eta\) is high. The measured bias is \(O(1/n)\)
(\(n\cdot\)bias \(\approx0.3\)). No interval left \([0,1]\); no evaluation cell
was empty. The interval for \(\eta\) essentially never covers the proxy value
\(\tilde\eta\), as O6.5 predicts. None of this is a proof of O6.2–O6.4, and
nothing is claimed about coverage below \(n=1000\) beyond the numbers shown.

### O6.8 Information-loss implication and verdict (protocol H)

O6 bounds nothing; it equips the true scalar retention \(\eta\) (equivalently
the D-, A- or E-efficiency of a one-parameter model) with a conditional
\(n^{-1/2}\) error bar on held-out oracle-score data. **Verdict: proved**, as a
bridge from the delta method, with the following left open and rerouted to
`OPEN-RETENTION-UNCERTAINTY`: vector scores and the geometric-mean retention
\((\det R)^{1/d}\) (a smooth matrix functional of the same moments — the
matrix influence function is the missing derivation); refitted rules, where
the evaluation sample enters the boundaries; weighted samples; and any
statement without an oracle score.
