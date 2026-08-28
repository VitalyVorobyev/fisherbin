# Protocol: numerical falsification and evidence

## Default exact falsification search

Before attempting any proof, deliberately test:

- \(d=1,2,3\);
- smallest rank-feasible \(K\);
- \(N\le10\), all nonempty partitions (exhaustive);
- small integer/rational scores;
- unequal positive weights;
- duplicate score atoms;
- singleton/tiny cells;
- near-singular information;
- nuisance degeneracy (weak/singular nuisance blocks);
- E eigenvalue multiplicity;
- exact ties.

## Exact-arithmetic rules

- Claim-relevant checks run in `fractions.Fraction`; floating point is for
  screening only. Eigenvalue-dependent claims (E) may use high-precision
  floats with wide margins, and must say so.
- A counterexample found numerically is **minimized** (smallest \(N\), \(d\),
  \(K\), simplest rationals) before it is recorded.
- Every exact counterexample is serialized to `COUNTEREXAMPLES/<ID>.json`
  in the required format (see `COUNTEREXAMPLES/README.md`), cited from its
  claim node, and — if publication-critical — pinned by a deterministic test
  in `tests/test_research_claims.py`.

## Evidence ledger

- Every measured result worth keeping gets a row in `NUMERICAL_EVIDENCE.md`
  citing at least one claim id and one executable source (CI test, workspace
  script).
- Nothing in the ledger is a proof. `measured` status never upgrades to
  `project_proved` without a derivation.
- Store random seeds, code revision, and environment beside new benchmark
  output; keep theorem regressions separate from performance benchmarks.
- If a new implementation disagrees with an identity regression, treat it as a
  bug until independently explained. If a search finds a theorem violation,
  stop benchmarking and audit the theorem immediately.
