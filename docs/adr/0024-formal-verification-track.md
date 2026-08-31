# ADR 0024: keep selected formal proofs inside the research memory

**Status:** Accepted. Extends the research boundary documented in the root
contributor guidance; it does not change a public Python API.

## Context

ScoreQuant already distinguishes internally derived proofs, independent audits,
counterexamples, and measured evidence. The finite D exchange-to-Voronoi
theorem is load-bearing for both the manuscript and the library's compile
bridge, but its current certification is human-readable algebra plus exact
rational and numerical regression evidence.

A proof assistant can remove ambiguity from individual formal statements and
kernel-check their derivations. It cannot certify that the formal statement is
the intended informal theorem, nor that the Python/JAX implementation realizes
that theorem. Treating a partial formalization as certification of a broad claim
would therefore weaken rather than strengthen the research provenance.

## Decision

The pinned Lean 4 + Mathlib project lives at `agenticresearch/formal/`.
`agenticresearch/` remains the single mathematical memory: a claim may attach
an optional `formal_proof` object pointing to an exact reviewed spec, theorem,
and statement audit. Formalization does not create a new claim status and does
not replace `proof_location`, publication status, or adversarial audit.

The formal workflow is selective. It is required for publication-critical
claims and claims that support shipped guarantees when their mathematics lies
inside the approved finite Lean track. Partial coverage becomes a separate
atomic claim. A statement formalizer, a fresh statement auditor for critical
claims, and a prover have distinct ownership; after audit the prover cannot
edit the spec.

The trust gate is:

- exact stable Lean and Mathlib tags plus committed Lake manifest;
- `lake build --wfail` with no `sorry` or `admit`;
- guarded axiom reports with an explicit allowlist and no project axioms;
- namespace-wide `axiom-audit` and the bundled `leanchecker` in CI.

Nanoda was evaluated against the pinned toolchain but is not enabled: its
current parser fails on modern Lean export streams with `invalid digit found in
string`, an upstream incompatibility tracked in
[lean-action issue 169](https://github.com/leanprover/lean-action/issues/169).
Keeping Lean 4.33.1's kernel fixes is more important than downgrading the trusted
toolchain to accommodate a second checker. Re-enable nanoda only after that
upstream compatibility gate is resolved and locally reproduced.

The initial pilot covers only the scalar inequality inside the finite D
exchange lower bound. No Python runtime dependency, wheel content, solver
behavior, or public API changes.

## Consequences

The research graph can state exactly which subclaim is machine-checked without
overclaiming coverage of Theorem 3. Lean upgrades are explicit reviewed changes
instead of silent dependency drift, and a proof failure routes back into the
ordinary theorem/audit workflow rather than encouraging statement weakening.

Developers need Elan/Lake only when editing or locally running the formal gate;
the Python environment remains uv-only. CI pays for a separate cached Lean job,
and the release gate rechecks formal evidence before publication.

Specialized provers are deferred. AxProver requires a separate licensing,
credential, and value review after repeated proof-search stalls; LeanDojo-v2 is
reserved for programmatic proof-state research; SafeVerify is reserved for
untrusted external submissions.

## Validation and follow-up

The scalar pilot and its statement audit are the acceptance fixture. A future
ADR is unnecessary for each additional lemma while it follows the same
boundary; a new decision is required before population measure theory,
profiled \(D_s\), untrusted proof ingestion, or a specialized prover enters the
baseline workflow.
