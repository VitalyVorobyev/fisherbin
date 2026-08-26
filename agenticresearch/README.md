# ScoreQuant LLM research workspace

**Version:** 2.0 · 26 August 2026

This workspace is a theorem-oriented scientific memory for **D- and \(D_s\)-optimal hard quantization of multivariate score space**.

## Read order

1. `PROBLEM.md` — canonical problem and goals.
2. `KNOWN_RESULTS.md` — all currently established project/literature results and negative results.
3. `CLAIMS.json` — granular machine-readable claim/dependency registry.
4. `COUNTEREXAMPLES/` — exact falsification fixtures.
5. `OPEN_PROBLEMS.md` — only unresolved tasks.
6. `LITERATURE.md` — annotated prior art and direct PDFs where known.
7. `NUMERICAL_EVIDENCE.md` — measured theorem/solver regression evidence.
8. `AGENT.md` — theorem-research operating protocol.
9. `START_HERE.md` — short scope-check prompt for a new agent.
10. `archive/` — historical context only.

## Canonical scope

The project asks how to construct a deployable hard \(K\)-cell quantizer of event score (or an explicitly tracked score proxy) that preserves maximal **D** or **\(D_s\)** Fisher information and reports information loss relative to unbinned inference.

Supported model access:

- direct scores;
- exact/autodiff scores;
- analytic or learned density ratios;
- component ratios;
- calibrated classifiers.

Primary application: multicomponent linear/template fitting with nuisance parameters, especially HEP.

## Important v2 corrections

The workspace now explicitly includes:

- exact finite D inductive closure and global geometric realizability;
- general concavity/supergradient screening;
- full-data efficient-score domination for \(D_s\);
- scalar efficient-score dynamic-programming upper certificate;
- \(K\le d\) split between in-bin profiling and external-nuisance projected formulation;
- exact global finite \(D_s\) non-geometric counterexample;
- E repeated-eigenvalue degeneracy and finite global failure;
- A exact move oracle + finite geometry failure;
- randomized-quantizer FIM and exact soft gradient;
- hard finite geometric objective piecewise constancy;
- atomless criterion-independent purification;
- **restricted affine-class consistency as an established project proposition**, while unrestricted consistency remains open;
- local Fisher-losslessness criterion;
- score-proxy truth-versus-surrogate Fisher accounting;
- numerical evidence separated from theorem status.

## Discipline

- `PROBLEM.md` defines the target.
- `KNOWN_RESULTS.md` defines the canonical mathematical state.
- `CLAIMS.json` defines machine-readable status/dependencies.
- `OPEN_PROBLEMS.md` must not contain already-solved claims.
- every exact counterexample gets a permanent artifact.
- every solver distinguishes sample-only labels from a deployable quantizer.
- every evaluation reports D/\(D_s\) information retention versus unbinned inference.


## CLAIMS.json registry model

`CLAIMS.json` is a machine-readable theorem graph, not a narrative document.

Each theorem, lemma, counterexample, certificate, or open question has a stable `id` and may contain:

- `status`
- `criterion`
- `level`
- `statement`
- `assumptions`
- `dependencies`
- `implies`
- `converse_failures`
- `counterexamples`
- `literature`
- `proof_location`
- `publication_status`

The file includes generated indexes by status, criterion, and problem level. An agent should locate a target node, recursively follow its `dependencies`, then open `proof_location` for the detailed mathematical statement.
