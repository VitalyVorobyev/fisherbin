# S03 — Library internals refactor

**Workstream:** W2 · **Needs:** S1 · **Parallel with:** S2 · **Status:** queued

## Goal

Close the pre-1.0 design debt that would become a breaking change later. Concretely: give the
library an exception hierarchy (254 raises across 5 stdlib types today, none of them library
specific); single-source weight and `rank_rtol` validation, currently triplicated at
`_validation.py:96`, `sources.py:255`, `components.py:154` (weights) and `config.py:289,362,415`
(`rank_rtol`); split the 181-line `fit_quantizer` (`api.py:324-363` compile path,
`api.py:365-452` geometric path, plus an order-sensitive inline profiled guard) into two named
functions with the guard at one boundary; stop constructing frozen results and then patching them
with `object.__setattr__` (`api.py:261-269,336`); remove the `quantizers.py` state seam that
mutates `solvers.scalar` for a test (`:45,56`); and move the prediction kernel out of
`artifact.py`'s call-time import of `result.py` (`:120,147`). Done means these are gone, not
merely documented, and the golden-engine and backend-conformance suites are bit-identical before
and after.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S01-scaffold-and-public-surface.md`: S1 closing report; confirms
  `LinearProblem` is already removed and the public surface this refactor builds on.
- `src/scorequant/api.py`: owns `fit_quantizer`, the `object.__setattr__` patch sites, and the
  criterion/config orchestration this session must not disturb.
- `src/scorequant/_validation.py`: current home of one of the three weight-validation copies.
- `src/scorequant/sources.py`: second weight-validation copy (`:255`).
- `src/scorequant/components.py`: third weight-validation copy (`:154`).
- `src/scorequant/config.py`: `rank_rtol` validation re-inlined at `:289,362,415`.
- `src/scorequant/quantizers.py`: the façade that mutates `solvers.scalar` state (`:45,56`).
- `src/scorequant/artifact.py`: imports its prediction kernel from `result.py` at call time
  (`:120,147`).
- `docs/api.md`: needs an errors section and the budget-parameter table this session adds.
- `docs/adr/0023-versioned-quantizer-artifact.md`: most recent ADR precedent for format and depth.

## Deliverables

- `src/scorequant/_errors.py`: `ScoreQuantError`, `ContractError(ScoreQuantError, ValueError)`,
  `RefusalError(ScoreQuantError, RuntimeError)` naming the counterexample for theorem-backed
  refusals. Subclassing keeps every existing `except ValueError` working; `TypeError` sites stay
  plain.
- Weight validation and `rank_rtol` validation single-sourced in `_validation.py`; the three/four
  call sites above call the shared function instead of re-implementing it.
- `fit_quantizer` split into `_fit_compiled_quantizer` and `_fit_geometric_quantizer`, with the
  profiled guard applied at one boundary instead of inline.
- Results constructed once: `execution` and `schema` become constructor arguments; zero
  `object.__setattr__` remaining in `api.py`.
- `quantizers.py` state seam removed; `tests/test_scalar_dp.py` monkeypatches `solvers.scalar`
  directly instead.
- Prediction kernel relocated to `solvers/common.py` (or a new `_predict.py`, session decides) so
  `artifact.py` never imports `result.py`.
- Dead `_SolverSpec.backends` removed; `source_kind` and `information_kind` retyped `Literal`.
- `tests/test_invariants_property.py`: hypothesis tests for relabeling, ordering, uniform weight
  scaling, split-weight duplication, on both backends.
- `tests/test_architecture.py`: a layering assertion (e.g. `artifact.py` does not import
  `result.py`).
- `docs/adr/0024-error-hierarchy-and-fit-pipeline.md`; `docs/api.md` errors section and
  budget-parameter table; `CHANGELOG.md` entry.

## Done criteria

- `grep -rn "object.__setattr__" src/scorequant/api.py` returns nothing.
- `grep -rn "solvers.scalar" src/scorequant/quantizers.py` returns nothing (or the file no longer
  mutates it; the seam is gone).
- `grep -n "import result" src/scorequant/artifact.py` (or equivalent) returns nothing.
- `tests/test_invariants_property.py` and `tests/test_architecture.py` exist and pass.
- Golden-engine and backend-conformance suites are bit-identical before and after the refactor.
- Full handoff gate green (see Verification).
- roadmap M12 table shows S03 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Design the error hierarchy, the fit-pipeline split, and the module boundary for the prediction kernel | opus/fable | written spec appended to this packet before code starts |
| Implement `_errors.py`, single-sourced validation, `fit_quantizer` split, constructor-arg results | sonnet | source diff |
| Remove `quantizers.py` seam, relocate prediction kernel, retype `Literal` fields, remove dead code | sonnet | source diff |
| Write hypothesis property tests and the architecture test | sonnet | test diff |
| Write ADR 0024, `docs/api.md` sections, CHANGELOG entry | sonnet | doc diff |
| Run gates, grep the done-criteria checks, report failures verbatim | haiku | gate output |

## Verification

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check src
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto
JAX_ENABLE_X64=0 MPLBACKEND=Agg uv run pytest tests/test_float32.py
uv build
uv run mkdocs build --strict
```

## Open decisions

- Exact module name for the relocated prediction kernel: `solvers/common.py` vs a new
  `_predict.py`. The plan names both as options; the session picks and records the reason.
- Whether `RefusalError` messages carry a structured counterexample reference or free text; the
  plan only requires that the refusal names the counterexample.

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
