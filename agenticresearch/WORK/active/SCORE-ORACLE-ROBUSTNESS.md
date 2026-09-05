# SCORE-ORACLE-ROBUSTNESS — true-score evaluation of a frozen rule

**Programme:** P2 (OPEN_PROBLEMS.md) · **Opened:** 28 Aug 2026 · **Status:** active
**Scope revised:** 5 September 2026; first deliverable only, not the full P2 programme.

## Scientific question and user decision

For a quantizer fitted from estimated scores and then frozen, what can an
independent evaluation sample with true scores establish about its retained
Fisher information? The result should tell a user which retention number is
supported by truth-score evaluation, how uncertain it is, and when the data
do not support that conclusion.

Keep the fitted score provider and quantizer fixed. Write
\(Z=q(\hat s(X))\). The population target is
\(I_Z=\operatorname{Var}(E[s(X)\mid Z])\) under the stated regular model,
not the corresponding surrogate computed from \(\hat s\). State the score
origin, sampling measure, weights, reference point, and conditioning on the
training data explicitly. Do not center empirical scores to enforce a
population identity. Explain any finite-sample bias of the estimator rather
than calling an empirical second moment exact population information.

## Bounded first deliverable

Use one existing analytic example with true scores and an intentionally
imperfect score proxy. Fit on training data, freeze the complete rule, and
evaluate on independent data. Start with a scalar score and full D retention.
Reuse existing example/evaluation machinery; do not create a general solver
or a new public API.

1. Define the cell-moment and retention estimands and estimators. State the
   treatment of empty or low-mass evaluation cells, singular information,
   random denominators, and the shared evaluation sample used for the
   unbinned reference. Start with independent, equal-weight observations;
   importance weights require their own assumptions.
2. Establish one quantitative bound or uncertainty statement for this
   frozen-rule problem with explicit assumptions and constants or a stated
   asymptotic regime. Distinguish conditional evaluation uncertainty from
   variation caused by retraining. A bootstrap experiment alone is measured
   evidence, not a coverage theorem.
3. Check the statement in a deterministic, seeded falsification experiment
   against known population quantities. Compare true-score retained
   information with the proxy surrogate. Report the practical consequence,
   including when an error bar or a retention comparison is unsupported.

The deliverable is an evaluation result or a precise limitation. It need not
establish geometric boundary stability, recover representation information
\(I_R\), or prove that the surrogate is conservative.

## Relevant claims

Start with `PROXY-TRUE-RETAINED-FI`, `REPRESENTATION-QUANTIZATION-LOSS`, and
`FI-LOSS-DECOMPOSITION` through the graph lookup protocol. The open targets
are `OPEN-SCORE-PERTURBATION` and the adjacent
`OPEN-RETENTION-UNCERTAINTY`; use their actual scope when recording results.
`OPEN-CLASSIFIER-CALIBRATION-FI` and
`OPEN-REPRESENTATION-LOSS-ESTIMATION` remain later questions. This narrower
packet does not close them by implication.

## Separate mathematical questions

- **Frozen-label evaluation and perturbation:** compare true and proxy cell
  moments for the same deployed labels. Establish the needed moment and
  conditioning assumptions; do not assume that every such bound needs a
  geometric margin.
- **Changed labels or refitting:** changing the provider, partition, or
  training sample can move boundaries. Margin, identifiability, and
  optimizer-selection assumptions belong to this separate problem.
- **Classifier-to-score and representation loss:** calibration, tail ratios,
  training priors, and estimation of \(E[s\mid R]\) require their own
  arguments. They are not prerequisites for evaluating fixed labels when
  true evaluation scores are available.

## Effort checkpoints and stop outcomes

Use one derivation session for the scoped question. Set its concrete effort
limit before starting; do not extend it silently or start exhaustive searches
without a bounded search plan. At the checkpoint return one of:

- **Proved:** the specified evaluation statement, with assumptions and the
  seeded check; no claim of end-to-end training or classifier robustness.
- **Refuted:** a minimized counterexample to a precise candidate statement,
  plus the evaluation claim that must consequently be withheld.
- **Reduced:** the exact missing assumption or lemma, the evidence gathered,
  and what remains usable for the example. A reduction does not authorize
  automatically opening another packet.

An independent audit is a separate session with the frozen statement, proof,
and artifacts, not the researcher's transcript. Follow `protocols/audit.md`
before promoting a result to a shipped guarantee or publication claim.

## Artifacts and handoff

Follow `protocols/theorem.md`: patch only claims justified by the outcome,
serialize any exact counterexample, link measured checks in
`NUMERICAL_EVIDENCE.md`, and preserve the truth/proxy and
representation/quantization distinctions. Record a short proposed user
explanation and the diagnostic implications here; implementation belongs to
a separately scoped library change. Run registry validation and the relevant
research regression checks. End with the verdict and one proposed next
question for selection under `OPEN_PROBLEMS.md`.
