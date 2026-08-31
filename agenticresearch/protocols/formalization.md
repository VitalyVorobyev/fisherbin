# Protocol: formal certification of selected claims

Use this only after an informal claim is stable enough to justify the cost of
formalization. Formal proof is required for a claim that will support a
publication-critical theorem or a shipped library guarantee; it is optional
for ordinary `project_proved` results and never substitutes for falsification,
prior-art work, or an adversarial mathematical audit.

## 1. Select and normalize one atomic claim

- Start from `py/registry.py show <CLAIM-ID> --deps --proof`.
- Confirm that the status is neither `open`, `conjecture`, `measured`, nor
  `counterexample`.
- Split an oversized claim before formalizing it. A `formal_proof` marker means
  the registered statement is covered exactly; partial coverage gets its own
  atomic claim rather than a misleading marker on the parent theorem.
- Record explicit non-coverage: implementation equivalence, neighboring
  lemmas, boundary cases, and problem levels that Lean will not certify.

## 2. Statement formalization session

Create or update a `*Spec.lean` module containing only definitions and the
target proposition. Map every formal quantifier, assumption, definition, and
conclusion to the registry statement and its prose proof. Do not start proof
search while the mapping is ambiguous.

Deliver a statement-audit report under `AUDITS/` and attach it through the
claim's `formal_proof.statement_audit`. Human review freezes the specification.
After that point a prover owns the proof module, not the spec module.

## 3. Independent statement audit

For publication-critical or library-guarantee claims, use a fresh session that
did not draft the spec. Give it the claim branch, prose proof, spec file, and
statement-audit template, but not the formalizer's chat transcript. The auditor
checks both directions of correspondence and returns one of:

- exact match;
- match after explicitly listed assumption hardening;
- mismatch, which blocks proof work.

If the statement is weakened or assumptions change, patch the canonical claim
and downstream graph before continuing. Never let the prover make that change
silently to close a goal.

## 4. Prover session

The prover may edit the proof module and add private lemmas. It may not edit the
frozen spec, use `sorry`/`admit`, introduce axioms, or claim that formal
mathematics verifies the Python/JAX implementation. Iterate against:

```bash
cd agenticresearch/formal
lake build --wfail
```

Prefer small named lemmas matching the informal proof. Built-in Mathlib
automation is allowed because the kernel checks its generated proof term.

## 5. Trust and registry gate

- Add guarded `#print axioms` output for every exported theorem. Only reviewed
  standard Lean dependencies may appear; `sorryAx` and project axioms fail the
  gate.
- Add `formal_proof` only after the proof, statement audit, and axiom audit
  exist. Required fields are `system`, `spec`, `file`, `declaration`, and
  `statement_audit`.
- Run the registry validator and reindex. CI then runs Lean with `--wfail` and
  checks the full project namespace with `axiom-audit` and the bundled
  `leanchecker`. Nanoda is deferred until its modern-Lean export parser issue is
  resolved upstream.

## Failure and escalation

If Lean exposes a missing hypothesis, false statement, or unresolved
dependency, stop formalization and open an ordinary theorem/audit task. Update
the claim graph before returning to Lean. Repeated proof-search stalls may
justify a separately reviewed AxProver experiment; LeanDojo-v2 is reserved for
programmatic proof-state research, and SafeVerify for untrusted external proof
submissions. None belongs in the baseline workspace.

Population measure theory and profiled \(D_s\) remain out of the formal track
until the finite D chain reaches its explicit go/no-go gate.
