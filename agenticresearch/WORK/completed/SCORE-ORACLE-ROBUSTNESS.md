# SCORE-ORACLE-ROBUSTNESS — uncertainty for a frozen rule

**Status:** completed 5 September 2026 — see Outcome below. (Original packet text kept verbatim.)
**Execution programme:** P2. **Claim target:** a restricted subresult of
`OPEN-RETENTION-UNCERTAINTY` (P4), not a resolution of `OPEN-SCORE-PERTURBATION`.

## Question

Conditional on a fitted score provider and quantizer, can an independent sample with true
scalar scores support an asymptotically valid confidence interval for retained Fisher information?
This would separate evaluation uncertainty from the discrepancy between proxy and true information.

Freeze training data, provider, rule, reference point and finite K. Evaluation observations are
iid, equally weighted pairs \((S_i,Z_i)\), where \(S_i\) is the true score and
\(Z_i=q(\hat s(X_i))\). Under a regular model, \(E[S]=0\). Target

\[
p_b=P(Z=b),\quad m_b=E[S\mathbf1_{Z=b}],\quad
\eta=\frac{\sum_b m_b^2/p_b}{E[S^2]}.
\]

Study the ordinary plug-in ratio of empirical cell moments and the unbinned second moment,
using the same evaluation sample for both. Never center the empirical scores.

## One result to attempt

Prove the conditional asymptotic distribution and consistency of an implementable variance
estimate. Include numerator–denominator covariance. Candidate assumptions: fixed positive
cell probabilities, finite fourth score moment, positive unbinned information and nonzero
asymptotic variance. State how empty evaluation cells are handled and where the interval is
unsupported; no uniform rare-cell or finite-sample coverage guarantee is requested.

Use `examples/door3_classifier.py` for one frozen imperfect provider/rule. Compare the proxy
surrogate with true retention; run one seeded coverage experiment over independent evaluation
samples. Obtain population references analytically or by controlled integration, labeling any
integration error. Do not interpret measured coverage as a proof.

## Read and stop

Follow `AGENT.md` and `protocols/theorem.md`. The needed claim closures are
`PROXY-TRUE-RETAINED-FI` and `OPEN-RETENTION-UNCERTAINTY` via `registry.py show --deps --proof`.
Read representation-loss material only if a dependency requires it. Check the statistical
literature for the plug-in/delta-method result before claiming novelty; a correct application
of established theory is an acceptable outcome.

One derivation session, one candidate estimator, one experiment. After the first proof attempt
and falsification experiment, return **proved**, **refuted**, or **reduced** with a precise missing
assumption or degeneracy. Stop there; do not switch estimators or launch a new programme silently.
Exclude importance weights, growing K, refitting, boundary stability, Ds, classifier-calibration
theory, bootstrap comparisons and a public uncertainty API.

Record the statement/proof or counterexample once, link its measured check, and update only
claims justified by the outcome. Preserve the broad open claim if only this special case is
settled. Run registry validation and research regression tests. Promotion requires a separate
independent audit. End with the practical interpretation and one proposed next action.

---

## Outcome (5 September 2026)

**Status:** completed · **Programme:** P2 · **Claim target:** the frozen-rule
scalar special case of `OPEN-RETENTION-UNCERTAINTY` (P4).

**Verdict: PROVED**, as a bridge from the delta method — not a resolution of
`OPEN-SCORE-PERTURBATION`, and `OPEN-RETENTION-UNCERTAINTY` stays open.

- **The result** (`KNOWN_RESULTS/10-oracle.md` §O6;
  `RETENTION-PLUGIN-CLT-FROZEN-SCALAR`, status `bridge`): conditional on the
  frozen provider and rule, for an iid equally weighted evaluation sample with
  true scalar scores, the plug-in ratio \(\hat\eta=\sum_b\hat m_b^2/\hat p_b/\hat v\)
  equals \(1-\mathrm{RSS}/\mathrm{TSS}\) exactly (O6.1), satisfies
  \(\sqrt n(\hat\eta-\eta)\Rightarrow N(0,\sigma^2)\) with the influence function
  \(\psi=((1-\eta)S^2-(S-c_Z)^2)/v\) (O6.2; the numerator–denominator
  covariance is the \(-\eta S^2\) cross term, spelled out as
  \(\sigma^2=[\operatorname{Var}N_1-2\eta\operatorname{Cov}(N_1,S^2)+\eta^2\operatorname{Var}S^2]/v^2\)),
  and admits the strongly consistent implementable variance
  \(\hat\sigma^2=n^{-1}\sum\hat\psi_i^2\) with \(\sum\hat\psi_i=0\) exactly
  (O6.3). The Wald interval is valid iff \(\sigma^2>0\) (O6.4).
  Assumptions: positive cell probabilities, finite fourth score moment
  (automatic for bounded mixture-fraction scores), positive unbinned
  information, nonzero asymptotic variance.
- **Degeneracy made precise:** \(\sigma^2=0\) iff, in every cell, \(S\) is
  supported on the two roots of \((s-c_b)^2=(1-\eta)s^2\) — the endpoints
  \(\eta\in\{0,1\}\) and atomic score laws with at most two atoms per cell.
  Any atomless cell of positive probability guarantees \(\sigma^2>0\). Empty
  evaluation cells are handled by \(0/0:=0\) and vanish exponentially; no
  uniform rare-cell or finite-sample guarantee is claimed.
- **Separation of evaluation uncertainty from proxy discrepancy** (O6.5): the
  interval is for the *true* retention \(\operatorname{Var}(E[s\mid q(\hat s)])/\operatorname{Var}(s)\);
  the surrogate's population value is a different number and the
  \(O(n^{-1/2})\) interval excludes it with probability \(\to1\). The same
  theorem gives the surrogate a valid interval around the wrong target.
- **Falsification run first** (`RETENTION-PLUGIN-COVERAGE-DOOR3`, measured):
  door3 rung `n_per_class = 15` frozen (reproduces the published ladder
  0.9658 / 0.8847); population references by two independent quadrature
  routes agreeing to \(10^{-16}\): \(\eta=0.893663\), \(\sigma=0.235410\),
  proxy value 0.967064. Coverage of the 95% Wald interval over 2000
  independent samples: 0.913, 0.934, 0.953, 0.949 at \(n=100,300,1000,3000\);
  the spread of \(\hat\eta\) equals \(\sigma/\sqrt n\) at every size and
  \(\hat\sigma\to\sigma\). The \(n=100\) shortfall is a recorded second-order
  effect (plug-in studentized skew \(+1.06\); \(n\cdot\)bias \(\approx0.3\)),
  not a counterexample. Did not falsify.
- **Prior art:** delta method (van der Vaart Thm 3.1; Serfling §3.3 Thm B;
  Cramér Ch. 28) and the influence-function variance (Hampel et al. 1986);
  `literature_search_status: prior_art_found`. The closed-form \(\psi\), the RSS
  identity and the \(\sigma^2=0\) characterisation were not located as stated
  and are project algebra inside the bridge node — not a novelty claim.

## Practical interpretation

With an oracle-score evaluation sample of \(n\) events, the true retention of
a frozen rule carries an error bar of about \(\sigma/\sqrt n\) — for the door3
rung \(\pm0.015\) at \(n=1000\) — computable from the same sample with one
extra pass (\(\hat\psi_i\)). The proxy gap (0.073 here) is five times that bar
and invisible to it: the interval quantifies evaluation noise, never the
oracle's bias. Without an oracle sample nothing here applies.

## Artifacts

- `KNOWN_RESULTS/10-oracle.md` §O6 (O6.0–O6.8: target, identity, CLT,
  variance, interval, proxy separation, protocol G pass, measured, verdict);
  `KNOWN_RESULTS/index.md` chapter row.
- Claims: `RETENTION-PLUGIN-CLT-FROZEN-SCALAR` (bridge),
  `RETENTION-PLUGIN-COVERAGE-DOOR3` (measured) new;
  `OPEN-RETENTION-UNCERTAINTY` patched (settled special case, remainders);
  `OPEN-SCORE-PERTURBATION` untouched.
- Instrument `py/score_oracle_retention_uncertainty.py` (modes selftest /
  popref / coverage / all); provenance-complete artifacts under
  `WORK/artifacts/SCORE-ORACLE-ROBUSTNESS/`; ledger rows N-ORACLE-CI-* in
  `NUMERICAL_EVIDENCE.md`.
- CI pin `tests/test_research_claims.py::test_o6_plugin_retention_influence_function_matches_finite_differences`.
- Literature round 9: six keys registered; triangulation
  `LITERATURE/audits/RETENTION-PLUGIN-CLT-FROZEN-SCALAR-5-September-2026.md`;
  annotations `LITERATURE/topics/08-plug-in-asymptotics.md`.
- `OPEN_PROBLEMS.md` (work limit, P2 preamble, OP27), `PLAYBOOK.md`,
  `manuscripts/README.md` current-state note.
- No `src/` change; no public uncertainty API (packet exclusion).

## Falsification discipline

The selftest (finite identities, Gateaux differences) and the coverage
experiment ran before the O6 proof was written down and were built to expose
under-coverage: the smallest size was chosen so that second-order effects
would show, the population references were computed by two independent
quadrature routes, and the proxy population value was tracked so a failure of
O6.5 would have been visible. Measured coverage is not a proof.

## Next dependency-blocking question

`OPEN-RETENTION-UNCERTAINTY`, vector case: under a frozen rule with
\(d\ge2\) score coordinates, is the geometric-mean retention
\((\det\hat R)^{1/d}\), \(\hat R=\hat I^{-1/2}\hat I_q\hat I^{-1/2}\), asymptotically
normal with an implementable matrix influence function, and where does
\(\log\det\) degenerate (a zero retention eigenvalue)? That is the library's
actually reported number; O6 covers only its scalar shadow. The refitted-rule
case — the boundary non-smoothness OP27 names — comes after it, and an
independent audit of O6 precedes any library use.
