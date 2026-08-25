# ADR 0007: Evolve the API around generic statistical contracts

**Status:** Accepted

## Context

Real applications expose missing abstractions as well as missing examples. A
strictly stable pre-release API would preserve accidental limitations. At the
other extreme, moving complete application workflows into ScoreQuant would make
the library depend on dataset vocabulary, estimator choices, and evaluation
protocols that do not belong to information-preserving binning.

The FlowCyt study makes this distinction concrete. Score matrices, measure
weights, fitted hard partitions, and retained-information diagnostics are
domain-independent. Cytometry marker preprocessing, patient cross-fitting,
classifier calibration, population templates, mixture fitting, and figure
layouts are choices of that application.

## Decision

API preservation is not a design goal before a stable release. ScoreQuant may
add, remove, or reshape public concepts when doing so produces a clearer generic
statistical contract.

A capability belongs in the public library only when:

- its name and semantics do not refer to a dataset, scientific domain, or
  evaluation protocol;
- its inputs, outputs, numerical invariants, and failure modes can be stated
  independently of one example;
- it composes with the physical-variable, component, or score representation
  layers instead of creating an overlapping workflow;
- deterministic tests exercise the abstraction without application fixtures;
- its API reduces duplication for plausible callers rather than merely hiding
  example orchestration.

Application-specific data access, model training, tuning, baselines, downstream
likelihoods, and reporting remain in examples until a narrower reusable concept
can be separated from them. A second use case is useful evidence, but it is not
a formal prerequisite when generic semantics and invariants are already clear.

## Consequences

Breaking changes are acceptable when documented with migration guidance. Real
use cases can drive core improvements, but they do not receive bespoke top-level
entry points or configuration fields. Reviews must justify both sides of the
boundary: why promoted code is generic and why remaining orchestration is not.
