# ADR 0023: separate the deployable rule from the fit, and give it a versioned artifact

**Status:** Accepted. Extends [ADR 0009](0009-partition-quantizer-separation.md) and
[ADR 0018](0018-explicit-multi-backend-execution.md). Closes the fourth capability gap recorded in
the pre-1.0 API audit (`docs/system-design.md`).

## Context

`QuantizerResult` held two different things: the record of a fit — labels, train and validation
reports, an optimization trace, solver diagnostics, provenance, criterion and config — and the rule
that fit produced, which is a transform, a set of centers and an optional metric.

For a library whose stated purpose is to produce a rule for future events, that conflation was
visible in the API. `to_dict()` carried an explicit disclaimer that it is JSON-ready diagnostic
state and *not* a persistence format, and there was no inverse for it or for any of the other
twenty-six `to_dict` methods. The only way to move a rule to another process was to refit there.

[ADR 0018](0018-explicit-multi-backend-execution.md) made this concrete rather than theoretical.
Once NumPy became a supported runtime because Pyodide has no JAX, "fit on the accelerated backend,
predict somewhere that does not have it" became a real workflow with no way to carry the rule
across.

`PartitionResult.compile_quantizer()` had a related problem: the theorem behind it says an
exchange-stable, nonsingular D partition *already is* a Mahalanobis-Voronoi rule, so compiling is
bookkeeping. It nevertheless returned a full `QuantizerResult`, synthesizing a trace of constant
centers so the shape would match — a fit-shaped object standing in for a fact.

## Decision

`Quantizer` is the rule alone: transform, centers, optional metric, schema, provenance, criterion
and execution. It holds nothing about the training sample.

- `fit.quantizer` exposes it. `compile_quantizer()` returns one.
- `QuantizerResult` keeps its name and its `predict_scores`, delegating; `centers`, `metric`,
  `transform` and `schema` read through. `predict_scores` remains the one prediction verb the
  contract requires, and removing it would have churned 190 references across tests, docs,
  notebooks and the portal to say the same thing.
- `evaluate_scores` moves onto the rule. How much information a rule retains on a new weighted
  sample is a property of the rule; a loaded artifact can now answer it with no fit present.

The artifact is a zip archive containing one `manifest.json` and one `.npy` member per array.

- **Versioned.** The manifest declares `format_version`. A reader refuses a version it does not
  know, by name, rather than interpreting a field it has never seen.
- **Not a pickle.** Arrays are written and read with `allow_pickle=False`, so loading an artifact
  executes no code from the file. Reading is otherwise field-by-field narrowing of JSON, which also
  means a hand-edited artifact cannot promote an estimated ratio into exact Fisher semantics:
  `exact_fisher` is derived from `kind`, never read back.
- **Backend-free.** Loading and predicting import no JAX. This is covered by a test that installs
  an import blocker in a subprocess and asserts the labels match the JAX-side fit exactly, rather
  than by assuming the import did not happen.

## Consequences

The two objects now match the two questions. `QuantizerResult` answers "what happened during the
fit"; `Quantizer` answers "what should happen to the next event", and is the thing that is saved,
shipped and loaded.

`to_dict()` on the result types keeps its disclaimer and its role. There is now a separate,
honest answer for the durable case, so the disclaimer no longer describes a missing capability.

The format is deliberately minimal. It stores no training data, no reports and no trace, so an
artifact is small and says nothing about the sample it was fitted on beyond its provenance.
Extending it later is a `format_version` bump with an explicit reader, which is why the version is
there from the first release rather than added once a second version exists.
