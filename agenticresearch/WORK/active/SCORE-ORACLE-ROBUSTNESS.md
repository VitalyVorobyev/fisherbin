# SCORE-ORACLE-ROBUSTNESS — uncertainty for a frozen rule

**Status:** ready for the next derivation session; no result established yet.
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
