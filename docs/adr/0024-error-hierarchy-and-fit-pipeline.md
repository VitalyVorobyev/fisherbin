# ADR 0024: an exception hierarchy, and a two-stage fit pipeline to earn it

**Status:** Accepted. Extends [ADR 0009](0009-partition-quantizer-separation.md) and
[ADR 0023](0023-versioned-quantizer-artifact.md).

## Context

The library raised 254 stdlib exceptions with no type of its own: 214 `ValueError`, 33
`TypeError`, and the rest a mix of `RuntimeError`, `FloatingPointError`,
`NotImplementedError`, `KeyError`, and `ImportError`. Two of those `ValueError` sites were not
like the other 212. `compile_quantizer()` on an unstable, profiled, or geometrically degenerate
partition, and a rank-deficient profiled `fit_quantizer`, are not malformed calls — every
argument is well-formed and the request is one the library would gladly answer if the data
supported it. They are refusals: a theorem-backed condition failed on the data in front of the
solver, and the library said so rather than returning an answer it could not back. Nothing in
the exception type told a caller, or a `except ValueError` handler, which kind of `ValueError`
it had caught, and nothing forced the message to name the counterexample that made the refusal
necessary, even though AGENTS.md already required exactly that in the raise-site comment.

Three smaller problems compounded it. `fit_quantizer` read as one function but was actually two
fits — a compiled, theorem-backed path and a solved, geometric path — sharing one prologue and
one long body, so the profiled-degeneracy guard sat wherever the diff happened to land rather
than at the one point that could see every downstream report before it ran. `PartitionResult`
and `QuantizerResult` are frozen dataclasses, yet `api.py` and `partition.py` finished building
them and then patched `execution` and `schema` on afterward with `object.__setattr__`, which
means the type declares immutability it briefly does not have. And `quantizers.py`, meant to be
a thin re-export façade over `solvers/`, copied a solver's module-level tuning constant at
import time and wrote it back on every call so that a test could monkeypatch the façade and have
the patch reach the kernel underneath — private solver state, mutated for a test, through a
module that is supposed to know nothing about it.

## Decision

Three exception classes in a new `scorequant._errors`, stdlib-only so every module can import
them without risking a cycle: `ScoreQuantError`, the base of everything the library raises
deliberately; `ContractError(ScoreQuantError, ValueError)` for a malformed call — detectable from
the arguments alone, and still catchable by any existing `except ValueError`; and
`RefusalError(ScoreQuantError, RuntimeError)` for a theorem-backed refusal on data that would
otherwise be accepted. `RefusalError` is deliberately not a `ValueError`. The two kinds of
failure call for different remedies — change the call, or accept that the data does not support
the request — and a shared base class that could not be told apart by type was the accident this
ADR closes, not a compatibility guarantee worth preserving. `RefusalError` carries a required
`counterexample` attribute naming the registry entry
(`agenticresearch/COUNTEREXAMPLES/<id>.json`) that forces the refusal, and `str(error)` appends
`[<id>]` to the unchanged message text, so the raise-site comment AGENTS.md already asked for
becomes a structured, checkable field instead of prose that can drift from the registry. Of 214
`raise ValueError(` sites, all but six become `ContractError`; the six that guard
`compile_quantizer()`'s theorem preconditions and the profiled rank-deficiency check become
`RefusalError`, each citing the counterexample that makes the refusal necessary. `TypeError`,
`KeyError`, `ImportError`, `NotImplementedError`, `FloatingPointError`, and `_execution.py`'s
environment `RuntimeError`s are unaffected; they were never contract-vs-refusal questions.

Weight and `rank_rtol` validation, previously copied across three or four call sites with
slightly different messages, are single-sourced: `validate_weights` in `_validation.py` and
`validate_rank_rtol` in `config.py` (kept out of `_validation.py` specifically to avoid a
`config -> _validation -> _execution -> config` import cycle). Every call site now raises the
same `ContractError` with the same message.

`fit_quantizer` splits into `_fit_compiled_quantizer` (the D-exchange or Lloyd path that
compiles a theorem-backed rule) and `_fit_geometric_quantizer` (the solved path), with the
profiled-degeneracy guard, `_require_profiled_fit_regular`, called once at the one point after
hard assignment and before any report reads the labels — the boundary the guard's placement
needed and did not reliably have before. Both `PartitionResult` and `QuantizerResult` are now
constructed once, with every field passed to the constructor; `optimize_d_partition`,
`optimize_profiled_d_partition`, and the two result-builders gained an explicit `schema`
parameter so the value that used to arrive by `object.__setattr__` after the fact now arrives at
construction time, and `api.py` no longer imports `dataclasses.replace`.

`quantizers.py`'s import-time copy of `_DYNAMIC_WORKING_SET_BYTES` and the write-back on every
call are removed; the module is a plain `from .solvers.scalar import ...` re-export, and a test
that wants to change the working-set budget monkeypatches `scorequant.solvers.scalar` directly,
the module that actually owns the constant.

The prediction kernel — `predict_distances`, `predict_labels`, `chunked_predict_labels` — moves
out of `result.py` into a new `scorequant._predict`, a leaf module depending only on
`_chunking` and `_execution`. `artifact.py`, the deployable, backend-free rule, and `result.py`,
the record of a fit, both import from this leaf instead of one importing the prediction kernel
from the other; `solvers/common.py` was rejected as the destination because it already carries
`QuantizerRun`, fitting-layer state a loaded artifact has no business seeing.

## Consequences

Catch `scorequant.ScoreQuantError` to handle anything the library refuses deliberately.
Catch `ContractError` (a `ValueError`) when the fix is to change the call. Catch `RefusalError`
(a `RuntimeError`) when the data itself does not support the request, and read
`error.counterexample` for the registry entry that says why. The one compatibility break this
session makes is that `compile_quantizer()` on an unstable or degenerate partition, and a
degenerate profiled `fit_quantizer`, now raise `RefusalError` rather than `ValueError`; an
`except ValueError` around either call stops catching it, by design, since `RefusalError` was
never a contract violation to begin with. A new architecture test asserts that every
`RefusalError` call site in the package cites a counterexample id that actually exists in the
registry, making the AGENTS.md rule executable rather than a convention to remember. Layering is
now test-enforced too: `artifact.py` cannot import any fitting-layer module, nothing in
`solvers/` can import the orchestration layer, and `_predict.py` and `_errors.py` stay leaves.
