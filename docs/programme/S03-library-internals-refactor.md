# S03 — Library internals refactor

**Workstream:** W2 · **Needs:** S1 · **Parallel with:** S2 · **Status:** done

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

## Design spec (written 3 September 2026)

Line numbers refer to the untouched branch at `173afc1`. Baseline for the bit-identity gate:
`JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_golden_engine.py tests/test_execution_backends.py -q`
gave `43 passed in 15.69s` (saved with suite sha256s in the session scratchpad `s3-baseline.txt`).

Corrections to the packet's assumptions, found while reading:

- The third weight-validation copy is `ratios.py:334-342` (`ratio_closure_report`), not
  `components.py:154` (that line validates coefficient counts). `components.py` has no weight code.
- `config.py` cannot import `_validation.py` (`_validation -> _execution -> config` is already a
  chain), so the shared `rank_rtol` validator lives in `config.py` next to `_validate_finite`;
  `_validation.py` keeps the weight validator. Reason recorded in section 2.
- `PartitionResult` and `QuantizerResult` already declare `execution` as a required constructor
  field, and `partition.py:747` already passes `execution=current_execution()`. The patch at
  `api.py:261` is redundant; only `schema` (and the profiled report's schema) needs plumbing.
- `RefusalError(RuntimeError)` is not a `ValueError`, so every `except ValueError` around a
  refusal breaks by design: 5 test lines, 3 executed docs pages, 2 notebooks, 1 example script
  (all listed in section 1). The packet sentence "subclassing keeps every existing
  `except ValueError` working" is true for `ContractError` only.
- Raise-site census: 254 `raise` lines; 214 `ValueError`, 33 `TypeError`, 5 `RuntimeError`
  (`_execution.py`), 2 `FloatingPointError` (`partition.py:263,356`), 1 `NotImplementedError`
  (`information.py:616`), 1 `KeyError` (`sources.py:93`), 1 `ImportError` (`visualization.py:21`).

### 1. Exception hierarchy — `src/scorequant/_errors.py` (Implementer A)

```python
"""Library exception hierarchy. Stdlib-only; imported by every module that raises."""

from __future__ import annotations


class ScoreQuantError(Exception):
    """Base of every exception ScoreQuant raises deliberately."""


class ContractError(ScoreQuantError, ValueError):
    """The caller violated an input, shape, range, or pairing contract.

    Detectable from the arguments alone; the remedy is to change the call.
    Subclasses ``ValueError`` so existing ``except ValueError`` handlers keep working.
    """


class RefusalError(ScoreQuantError, RuntimeError):
    """The library declines a valid request because a theorem-backed condition fails on the data.

    Parameters
    ----------
    message
        Plain-English refusal, unchanged from the pre-hierarchy message text.
    counterexample
        Registry id (``agenticresearch/COUNTEREXAMPLES/<id>.json``) of the counterexample that
        forces the refusal. Always a string literal at the raise site.
    """

    counterexample: str

    def __init__(self, message: str, counterexample: str) -> None:
        super().__init__(message, counterexample)  # positional args keep pickling/copy intact
        self.counterexample = counterexample

    def __str__(self) -> str:
        return f"{self.args[0]} [{self.counterexample}]"
```

Open decision settled: **structured reference, not free text.** `counterexample` is a required
positional attribute so tests can assert `error.counterexample == "CE-..."`, and the architecture
test (section 6) can verify every cited id exists as a file, which is the AGENTS.md rule "code that
refuses a capability names the counterexample; keep both in sync with the registry" made
executable. `str(error)` appends ` [<id>]` so a traceback names it too; `args[0]` stays the exact
old text, so every existing `match=`/`in str(error)` check still passes. Only the `==` assertion at
`docs/examples/ds-geometry-counterexample.md:162` needs the suffix (C edits that page anyway).

Reclassification rule (A applies it mechanically, module by module):

- Every `raise ValueError(` in `src/scorequant/**` becomes `raise ContractError(` — 208 sites —
  except the six refusal sites below. Import as `from ._errors import ContractError` (solvers:
  `from scorequant._errors import ContractError`). Message text is unchanged everywhere.
- `TypeError`, `KeyError`, `ImportError`, `NotImplementedError` (`information.py:616`, test
  pins the type), `FloatingPointError`, and the five `_execution.py` `RuntimeError`s
  (environment, not contract) stay as they are.
- Docstring `Raises` blocks that say `ValueError` (`api.py:156-164`, `result.py:330-335`, comment
  `api.py:96-98`) are updated to the new names.

`RefusalError` sites — exactly these, with the counterexample each must cite:

| Site | Message (unchanged) | `counterexample` |
|---|---|---|
| `result.py:339` `compile_quantizer`, non-D criterion | "finite profiled-D labels have no canonical inductive compilation; ..." | `CE-DS-GLOBAL-GEOMETRY-001` |
| `result.py:349` `compile_quantizer`, not exchange-stable | "only an exchange-stable D partition can be compiled; ..." | `CE-D-VORONOI-CONVERSE-001` |
| `result.py:363` `compile_quantizer`, rule relabels beyond tolerance | "D compilation is degenerate: ..." | `CE-D-UNMERGED-DUPLICATES-001` |
| `partition.py:418` terminal D state geometrically degenerate | "terminal D state is geometrically degenerate: ..." | `CE-D-UNMERGED-DUPLICATES-001` |
| `partition.py:308` initial profiled-D partition singular | "initial profiled-D partition is singular: ..." | `CE-DS-MARGINS-RANK-VACUITY-001` |
| `api.py:395` (moves; see section 3) profiled-D fit degenerate | "profiled-D fit is degenerate: ..." | `CE-DS-MARGINS-RANK-VACUITY-001` |

`result.py:354` and `api.py:464` ("D compilation geometry is unavailable") are internal-invariant
guards, not refusals: `ContractError`. `certify.py:161` ("DOptimality only") and
`partition.py:449,523` (bin-budget bounds) are pairing/feasibility contracts: `ContractError`.

Catch sites that must change from `ValueError` because they wrap a refusal:

- Tests (A edits, one token each): `tests/test_evidence_suite.py:599`, `tests/test_lloyd.py:193`,
  `tests/test_profiled_d.py:66`, `tests/test_research_claims.py:792,814` →
  `pytest.raises(sq.RefusalError, match=...)`.
- Docs/examples (C edits): `docs/examples/ds-geometry-counterexample.md:161`,
  `docs/examples/lloyd-nonmonotone.md:148`, `docs/examples/nuisance-profiled-ds.md:207`,
  `examples/ds_geometry_counterexample.py:447`, and the JSON source lines
  `examples/notebooks/ds_geometry_counterexample.ipynb:180`,
  `examples/notebooks/nuisance_profiled_ds.ipynb:209` → `except sq.RefusalError as error:`.
  The other executed `except ValueError` sites (`three-doors.md`, `global-certification.md`,
  `book/ch05`) wrap `ContractError`s and stay.

Exports: **yes.** `src/scorequant/__init__.py` imports `ContractError, RefusalError,
ScoreQuantError` from `._errors` and adds all three to `__all__` (keep the list's existing loose
alphabetical order). `docs/reference/results.md` gains `::: scorequant.ScoreQuantError`,
`::: scorequant.ContractError`, `::: scorequant.RefusalError` at the end (C).

### 2. Single-sourced validation (Implementer A)

`src/scorequant/_validation.py`, new function placed before `validate_sample`:

```python
def validate_weights(
    weights: ArrayLike | None, n_rows: int, *, dtype: DTypeLike = np.float64
) -> np.ndarray:
    """Return the validated ``[n_rows]`` weight vector as a NumPy array of ``dtype``.

    ``None`` means unit weights. Raises ContractError on shape, non-finite, negative, or
    all-zero weights. Checked in NumPy on the host: O(N) scalars never justify a device trip.
    """
    if weights is None:
        return np.ones(n_rows, dtype=dtype)
    array = np.asarray(weights, dtype=dtype)
    if array.shape != (n_rows,):
        raise ContractError(f"weights must have shape [{n_rows}], got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ContractError("weights must be finite")
    if np.any(array < 0):
        raise ContractError("weights must be nonnegative; signed weights are not supported")
    if not np.any(array > 0):
        raise ContractError("at least one weight must be positive")
    return array
```

`DTypeLike` comes from `numpy.typing` (add it to `_typing.py` as `type DTypeLike = _NumPyDTypeLike`).
Messages are the `_validation.py` variants (the most informative of the three). Call sites:

- `_validation.py:86-103` (`validate_sample`): replace the `if weights is None ... else ...`
  block and the three weight checks with
  `weight_array = jnp.asarray(validate_weights(weights, int(score_array.shape[0]), dtype=score_array.dtype))`;
  keep the `scores must be finite` check where it is. Same values and dtype as today's
  `jnp.asarray(weights, dtype=...)` on both backends, x64 on or off (both round to nearest).
- `sources.py:257-269` (`ObservationSample.__init__`, currently
  `weight_array = (np.ones(...) if weights is None else np.asarray(weights, dtype=array.dtype))`
  plus four checks): `weight_array = validate_weights(weights, array.shape[0], dtype=array.dtype)`.
  `sources.py` already imports from `._validation`.
- `ratios.py:334-342` (`ratio_closure_report`, `weight_array = jnp.asarray(weights, dtype=values.dtype)`
  plus four checks): `weight_array = jnp.asarray(validate_weights(weights, int(values.shape[0]), dtype=values.dtype))`.
  Add `validate_weights` to the existing `from ._validation import promote_low_precision`.

`src/scorequant/config.py`, new function after `_validate_finite` (line 77):

```python
def validate_rank_rtol(rank_rtol: float | None) -> float | None:
    """Validate a relative rank threshold: ``None`` (dtype default) or a finite value in [0, 1)."""
    if rank_rtol is not None:
        _validate_finite("rank_rtol", rank_rtol, positive=False)
        if rank_rtol >= 1:
            raise ContractError("rank_rtol must be less than one")
    return rank_rtol
```

Reason it is in `config.py`, not `_validation.py`: `_validation.py` imports `_execution`, which
imports `config`, so `config -> _validation` would be a cycle at module import. `config.py` is the
backend-free contract layer (`test_domain_contracts_do_not_import_solver_or_api_layers` pins it)
and already hosts the sibling scalar validators that `certify.py:40` imports. Call sites:

- `config.py:90-93` inside `_validate_common_config`: replace with `validate_rank_rtol(rank_rtol)`.
- `config.py:289-292`, `:362-365`, `:415-418` (each `if self.rank_rtol is not None:` block):
  replace with `validate_rank_rtol(self.rank_rtol)`.
- `transforms.py:134-136` (`resolved_rtol = ...; if not np.isfinite(resolved_rtol) or resolved_rtol < 0: raise ValueError("rank_rtol must be finite and nonnegative")`):
  becomes `resolved_rtol = _default_rank_rtol(matrix.dtype) if validate_rank_rtol(rank_rtol) is None else rank_rtol`
  and the inline check is deleted. Messages for a bad `rank_rtol` at `fisher_transform` change to
  the shared "must be finite"/"must be nonnegative"/"must be less than one" texts; no test matches
  the old sentence (`tests/test_scalar_dp.py:164`, `tests/test_lloyd.py:216` match `"rank_rtol"`).

### 3. `fit_quantizer` split (Implementer A) — `src/scorequant/api.py`

Current shape: `api.py:273-322` shared prologue (materialize, validate validation, resolve
config/criterion, `_validate_solver`, resolve profiled names); `:324-363` compile path (D-exchange
or Lloyd, `object.__setattr__(partition, "schema", ...)` at `:336`); `:365-372` prepare+solve;
`:373-399` the inline profiled-degeneracy guard; `:400-452` diagnostics, profiled reports, result.

Target — three private functions, `fit_quantizer` keeps its signature and docstring:

```python
def fit_quantizer(...):          # :273-322 unchanged, then:
    if isinstance(resolved_config, (DExchangeConfig, MahalanobisLloydConfig)):
        return _fit_compiled_quantizer(train, validation_sample, n_bins=n_bins,
            config=resolved_config, source_kind=source_kind, execution=resolved_execution)
    return _fit_geometric_quantizer(train, validation_sample, n_bins=n_bins,
        criterion=resolved_criterion, config=resolved_config, diagnostics=diagnostics,
        source_kind=source_kind, execution=resolved_execution)


def _fit_compiled_quantizer(
    train: ScoreSample, validation: ScoreSample | None, *, n_bins: int,
    config: DExchangeConfig | MahalanobisLloydConfig, source_kind: SourceKind,
    execution: ExecutionConfig,
) -> QuantizerResult:
    """Fit by finite D exchange and compile the exchange-stable partition (Theorem 3)."""
    # body = :329-363 with ``schema=train.schema`` passed to optimize_d_partition and the
    # object.__setattr__ line deleted; the comment at :325-328 moves here.


def _require_profiled_fit_regular(
    prepared: _PreparedFit, labels: jnp.ndarray, n_bins: int, criterion: Criterion
) -> None:
    """Refuse a profiled labeling whose binned information cannot be profiled.

    Must run after hard assignment and before any report reads ``labels`` (the retention
    history scores snapshots through the same profiled report, so a check placed downstream
    never gets to run). The rank ceiling is a bin-budget fact, so deciding for the final
    labeling decides for every snapshot.
    """
    if not isinstance(criterion, ProfiledDOptimality):
        return
    information = binned_fisher_information(
        prepared.train_sample.scores, labels, prepared.train_sample.weights, n_bins=n_bins
    )
    if binned_information_is_degenerate(information):
        raise RefusalError(
            f"profiled-D fit is degenerate: {n_bins} bins cannot generate nonsingular "
            f"{prepared.train_sample.scores.shape[1]}-dimensional binned information. "
            f"{PROFILED_RANK_ADVICE}",
            "CE-DS-MARGINS-RANK-VACUITY-001",
        )


def _fit_geometric_quantizer(
    train: ScoreSample, validation: ScoreSample | None, *, n_bins: int,
    criterion: Criterion, config: KMeansConfig | SoftVoronoiConfig | ScalarDPConfig,
    diagnostics: DiagnosticsMode, source_kind: SourceKind, execution: ExecutionConfig,
) -> QuantizerResult:
    prepared = _prepare_score_fit(train, validation, n_bins=n_bins, config=config)
    run = _run_geometric_quantizer(prepared, n_bins, criterion)
    labels = chunked_hard_assign(prepared.all_train_coordinates, run.centers)
    _require_profiled_fit_regular(prepared, labels, n_bins, criterion)   # the one boundary
    # rest = :400-452 verbatim (train/validation profiled reports, hardening gap, result)
```

The message f-string is byte-identical to `:396-398`. Nothing else in the two bodies changes;
the diff is a move plus parameter renames (`resolved_config→config`, `resolved_criterion→criterion`,
`resolved_execution→execution`, `validation_sample→validation`).

### 4. Results constructed once (Implementer A)

Patch sites in `api.py`: `:261` (`execution`), `:262` (`schema`), `:267-269` (`profiled_report`
with schema), `:336` (`schema` on the partition before compile). No other `object.__setattr__`
exists in `api.py`. Neither result dataclass changes its fields: `execution` is already a
required field on both (`result.py:91`, `:256`) and `schema: ScoreSchema | None = None` is
already the last `PartitionResult` field (`:270`), so no default-ordering issue arises.

Changes in `src/scorequant/partition.py`:

- `optimize_d_partition(:378-386)` and `optimize_profiled_d_partition(:489-498)` gain a
  keyword `schema: ScoreSchema | None = None` (after `provenance`); import `ScoreSchema` from
  `.sources` (line 74).
- `_partition_result(:714-729)` gains `schema: ScoreSchema | None = None` and passes
  `schema=schema` into `PartitionResult(...)` (after `profiled_geometry=` at `:766`).
- `:425` and `:543` pass `schema=schema`; `:552-558` passes `schema=schema` into
  `profiled_information_report(...)`, which already accepts it (`api.py:413` does the same).
- `:747` `execution=current_execution()` stays; it is the same context `api.py:234/:309` read.

`api.py:235-270` becomes: build `sample`, resolve, validate, call the solver with
`schema=sample.schema`, `return canonicalize_public(result)`. Drop the now-unused
`from dataclasses import dataclass, replace` → `from dataclasses import dataclass`.
`canonicalize_public` (`_execution.py:408`) still uses `object.__setattr__` to swap arrays in
place; that is array canonicalization, not result patching, and is out of scope.
`artifact.py`, `result.py:to_dict`, and the `.sqz` format are unaffected: no field changes.

### 5. `quantizers.py` seam (Implementer B)

Seam: `quantizers.py:36` copies `_scalar._DYNAMIC_WORKING_SET_BYTES` at import, and the two
wrappers write it back on every call (`:45` `_scalar._DYNAMIC_WORKING_SET_BYTES = _DYNAMIC_WORKING_SET_BYTES`
and `:56` likewise) so that monkeypatching the façade reaches the kernel. Removal: delete
`:33-57`; add `scalar_interval_dp, scalar_weighted_kmeans_dp` to a plain
`from .solvers.scalar import ...`; drop the now-unused `numpy`, `xp`, `ScalarDPConfig`, and
`from .solvers import scalar as _scalar` imports. `__all__` is unchanged. Module docstring:
"Private solver façade re-exporting the solver package's kernels."

`tests/test_scalar_dp.py` (C): `:10` `from scorequant import quantizers` →
`from scorequant.solvers import scalar as scalar_dp`; `:83` →
`monkeypatch.setattr(scalar_dp, "_DYNAMIC_WORKING_SET_BYTES", 512)`. `scalar_interval_dp` reads
the module global at call time through `_dynamic_stripe_rows` (`solvers/scalar.py:26`), so the
patch is observed.

### 6. Prediction kernel relocation (Implementer B)

Decision: **new `src/scorequant/_predict.py`**, not `solvers/common.py`. `artifact.py` is the
deployable, backend-free layer; `solvers/` is the fitting layer. Importing the fitting package
from the deployable rule inverts the layering this session pins, and `solvers/common.py` already
carries `QuantizerRun`, which a loaded artifact has no business seeing. `_predict.py` depends only
on `_chunking` and `_execution`.

Move `result.py:419-466` verbatim into `_predict.py` as `predict_distances`, `predict_labels`,
`chunked_predict_labels` (leading underscores dropped; the module is private). Docstrings move
with them. Then: `result.py:22` keeps `from .artifact import Quantizer`; add
`from ._predict import chunked_predict_labels`; `:357` calls it; delete `:17` `assignment_chunk_rows`
and the `backend_array` name from `:18` if unused. `artifact.py:120` becomes a module-scope
`from ._predict import chunked_predict_labels` (alphabetically after `._json`); `:125` calls it.
`artifact.py:147` (`information_report`) stays a call-time import: `information.py` imports the
solver package, which the artifact must not pull in at import.

Resulting edges: `artifact -> _predict`, `result -> _predict`, `result -> artifact`,
`partition -> result`, `api -> {result, artifact, partition, quantizers}`; `_predict -> {_chunking, _execution}`.

`tests/test_architecture.py` additions (C), using the existing `_imports` helper (relative
imports report bare module names, e.g. `"result"`):

```python
def test_artifact_never_imports_fit_layers() -> None:
    forbidden = {"result", "api", "partition", "quantizers", "solvers", "certify", "visualization"}
    assert sorted(_imports(PACKAGE / "artifact.py") & forbidden) == []

def test_solvers_never_import_orchestration() -> None:
    forbidden = {f"scorequant.{m}" for m in ("api", "result", "artifact", "partition", "quantizers", "information", "certify")}
    offenders = {p.name: sorted(_imports(p) & forbidden) for p in (PACKAGE / "solvers").glob("*.py")}
    assert {k: v for k, v in offenders.items() if v} == {}

def test_predict_and_errors_modules_stay_leaf() -> None:
    assert _imports(PACKAGE / "_predict.py") <= {"__future__", "_chunking", "_execution"}
    assert _imports(PACKAGE / "_errors.py") <= {"__future__"}

def test_api_constructs_results_once() -> None:
    assert "object.__setattr__" not in (PACKAGE / "api.py").read_text()
    assert "_DYNAMIC_WORKING_SET_BYTES" not in (PACKAGE / "quantizers.py").read_text()

def test_every_refusal_cites_a_registered_counterexample() -> None:
    # ast-walk every package source for Call nodes whose func name is "RefusalError"; the
    # second positional (or ``counterexample=`` keyword) must be an ast.Constant str, and
    # ROOT / "agenticresearch" / "COUNTEREXAMPLES" / f"{id}.json" must exist. Assert at least
    # six sites were found so the test cannot pass vacuously.
```

### 7. Dead code and `Literal` retyping (Implementer B)

- `api.py:115` `backends: tuple[BackendName, ...] = ("jax", "numpy")` — delete, together with
  the unreachable check `:183-187` (every spec lists both backends, so the branch never fires)
  and `BackendName` from the `:26-36` import; `current_execution` stays (used at `:234`, `:309`).
- `sources.py`, after `RatioParameterizationKind` (`:24`):
  `type SourceKind = Literal["score_sample", "observation_sample", "integration_source"]` and
  `type InformationKind = Literal["exact_fisher", "supplied_score_surrogate"]`. These are the
  only values in use (`api.py:531,544,557`; `artifact.py:105`, `result.py:141,291`).
- Retype: `result.py:98` `source_kind: SourceKind = "score_sample"`; `api.py:527`
  `-> tuple[ScoreSample, SourceKind]`; `information_kind` properties at `artifact.py:103`,
  `result.py:133`, `result.py:283` return `InformationKind`. Import the aliases from `.sources`
  (the modules already import from it). `ty` narrows the ternaries to the literal union.

### 8. Property tests — `tests/test_invariants_property.py` (Test writer C)

`hypothesis>=6.130` is already in the `dev` group (`pyproject.toml:53`); nothing to add. Module
header: `settings.register_profile("scorequant", deadline=None, max_examples=25, derandomize=True)`
and `settings.load_profile("scorequant")`. Backends: `pytest.mark.parametrize("backend", ["jax", "numpy"])`
with `sq.ExecutionConfig(backend=backend, precision="float64", device="cpu")` (the conformance
suite's `_execution`); call `pytest.skip` for `"jax"` when `not jax.config.jax_enable_x64`,
mirroring `test_golden_engine._require_x64` (CI sets `JAX_ENABLE_X64=1`).

Strategies (shared helper `problem()` via `st.composite`): `n = st.integers(8, 20)`,
`d = st.integers(1, 3)`, `k = st.integers(d + 1, 4)` (one bin above rank keeps D feasible on a
centered draw), `scores = hnp.arrays(np.float64, (n, d), elements=st.floats(-3, 3, allow_nan=False))`,
`weights = hnp.arrays(np.float64, (n,), elements=st.floats(0.1, 2.0))`,
`labels = hnp.arrays(np.int64, (n,), elements=st.integers(0, k - 1))`; guard
`assume(np.linalg.matrix_rank(scores) == d)` and, for the report-based invariants,
`assume(len(set(labels)) == k)`. Tolerance: `np.testing.assert_allclose(..., rtol=1e-10, atol=1e-12)`
on `geometric_mean_retention`, `logdet_retention`, and `retained_eigenvalues`.

| Invariant | Public function | Check |
|---|---|---|
| Bin relabeling | `sq.information_report(scores, labels, weights, n_bins=k, execution=...)` | `labels` vs `perm[labels]` for a drawn permutation of `range(k)`: retention metrics equal; `bin_weights` equal up to the same permutation |
| Row ordering (report) | same | `scores[p], labels[p], weights[p]` for a drawn permutation `p` of `range(n)`: retention metrics equal |
| Row ordering (solver) | `sq.optimize_partition(scores, weights=..., n_bins=3, config=sq.DExchangeConfig(solver_restarts=1, batch_moves=False, max_scans=None, seed=0), execution=...)` with **fixed** `n=12, d=2` so JAX compiles one shape | `objective` of the permuted problem (`scores[p], weights[p]`) equals the original's within `1e-9`; the labelings induce the same row partition: `perm_labels[i] == perm_labels[j]` iff `labels[p[i]] == labels[p[j]]` (seeding is row-order invariant via `solvers/kmeans.py:229` `lexsort`). If a drawn problem exposes a gain tie, weaken to the objective check and report it in the closing report |
| Uniform weight scaling | `information_report` | `weights * c`, `c = st.floats(0.5, 20)`: retention metrics equal; `fisher_binned` scales by `c` |
| Split-weight duplication | `information_report` | pick row `i = st.integers(0, n-1)`, `t = st.floats(0.1, 0.9)`; append row `i` again with weights `w_i*t`, `w_i*(1-t)` and the same label, `n_bins=k`: retention metrics and `fisher_binned` equal |

Keep the solver test to that one fixed shape; the four report tests draw shapes freely.

### 9. Bit-identity procedure

`tests/test_golden_engine.py` freezes labels/objectives as inline literals (no fixture files;
docstring `:1-10`), for `optimize_partition` D and profiled-D and for the k-means `fit_quantizer`
path. `tests/test_execution_backends.py` is the conformance suite: it runs the full solver
matrix on both backends and asserts JAX/NumPy parity plus NumPy-only public arrays. Neither can
regenerate anything, so **passing both after the refactor is the bit-identity proof**, provided
the two files are untouched: the gate runner re-runs the baseline command and compares against
`43 passed` and the sha256s recorded in `s3-baseline.txt` (also `tests/_oracles.py`). Nobody in
this session edits those three files.

### 10. Docs (C)

`docs/adr/0024-error-hierarchy-and-fit-pipeline.md`, ADR 0023's format (title, `**Status:**
Accepted. Extends ADR 0009 and ADR 0023.`, then `## Context` / `## Decision` / `## Consequences`).
Context: 254 stdlib raises with no library type, so a malformed call and a theorem refusal were
indistinguishable; `fit_quantizer` mixed two fits and patched frozen results; the façade mutated
solver state for a test; the rule imported the fit. Decision: the three classes and the
Contract-vs-Refusal rule with a structured counterexample id (`RefusalError` deliberately not a
`ValueError`); validation single-sourced; the two-stage fit with the guard at one boundary;
results built once; `_predict.py` as the leaf both the artifact and the result use; seam removed.
Consequences: catch `ScoreQuantError` for everything, `ContractError` to fix a call,
`RefusalError` to read `counterexample`; the one compatibility break is `except ValueError` around
`compile_quantizer` and degenerate profiled fits; layering is now test-enforced. Add line `24. [ADR 0024 — Exception hierarchy and two-stage fit pipeline](0024-error-hierarchy-and-fit-pipeline.md) — extends ADR 0023`
to `docs/adr/index.md`.

`docs/api.md`: insert `## Errors` after the Execution section (before the `---` / `# Advanced`
divider at `:265-267`). Content: the three names with one sentence each; "A `ContractError` means
change the call; a `RefusalError` means the library declined a valid request because a theorem
condition fails on your data, and `error.counterexample` names the registry entry"; a
`<!-- snippet: skip -->` try/except example; the sentence "`compile_quantizer()` and a degenerate
profiled `fit_quantizer` raise `RefusalError`, which is not a `ValueError`". Also update `:346-347`
("rejects an unstable or geometrically degenerate result") to say "raises `RefusalError`".

Budget-parameter table as `### Budgets` directly under `## Errors` (both answer "why did it stop"):

| Parameter | Class | Default | Meaning |
|---|---|---|---|
| `max_iter` | `KMeansConfig` | 100 | Lloyd iterations per restart |
| `kmeans_max_iter` | `SoftVoronoiConfig` | 100 | Lloyd iterations per initialization restart |
| `max_steps` | `SoftVoronoiConfig` | 1000 | Adam updates |
| `max_scans` | `DExchangeConfig` | `None` (run to stability) | complete candidate scans |
| `max_iter` | `MahalanobisLloydConfig` | 100 | guarded batch iterations |
| `max_nodes` | `CertificationConfig` | 2 000 000 | branch-and-bound nodes before `budget_exhausted` |

Follow it with one sentence separating restarts (`KMeansConfig.solver_restarts` 8,
`DExchangeConfig.solver_restarts` 1, `initializer_restarts` 8 on the soft, exchange, and Lloyd
configs) and capacity caps (`ScalarDPConfig.max_rows` 20 000, `CertificationConfig.max_rows` 64,
ceiling 512) from the iteration budgets above: "how long it may run" versus "how big it may be".

`CHANGELOG.md`: under `## [0.1.0] — unreleased`, new `### Errors` subsection after `### Contracts`:
"- Every deliberate exception is a `ScoreQuantError`. `ContractError` (a `ValueError`) reports a
malformed call; `RefusalError` (a `RuntimeError`, deliberately not a `ValueError`) reports a
theorem-backed refusal and carries `counterexample`, the registry id that forces it.
`compile_quantizer()` on an unstable, profiled, or geometrically degenerate partition and a
rank-deficient profiled `fit_quantizer` now raise `RefusalError`." Plus one bullet under
`### Contracts`: "Weight and `rank_rtol` validation is single-sourced; the messages are the
`ScoreSample` ones everywhere."

### 11. Work split and ownership

**Order: B lands first, then A rebases; C runs in parallel with both.**

Implementer B (small, mechanical; ~1 h): creates `_predict.py`; edits `quantizers.py` (whole
file), `artifact.py` (`:25-37` imports, `:103` annotation, `:120-125`), `result.py` (`:17-22`
imports, `:98`, `:133`, `:283`, `:357`, delete `:419-466`), `sources.py` (add two `type` aliases
after `:24`), `api.py` (`:26-36` import list, delete `:115`, delete `:183-187`, `:527` annotation
+ import `SourceKind` from `.sources` at `:55-61`). B runs ruff, ty, and the two bit-identity
suites, then commits.

Implementer A (starts immediately on files B never touches, rebases before touching the shared
three): creates `_errors.py`; edits `__init__.py`, `_validation.py`, `config.py`,
`transforms.py`, `ratios.py`, `partition.py`, and every other module's `raise ValueError` sites
(`criteria`, `information`, `certify`, `reports`, `visualization`, `components`, `providers`,
`solvers/*`), plus the five test lines in section 1. After B's commit, A edits `sources.py`
(only `:257-269` and its raises), `result.py` (only the `compile_quantizer` raises `:339-367` and
its docstring; B has already changed `:17-22`, `:98`, `:133`, `:283`, `:357` and removed the
kernel block), and `api.py` (fit split `:273-452`, `optimize_partition` `:233-270`, raises at
`:182`, `:464-575`; B has already removed `:115`, `:183-187`, and retyped `:527`, and the imports
at `:26-36`/`:55-61` no longer include `BackendName` but do include `SourceKind`).

Test/doc writer C (parallel; touches no `src/`): creates `tests/test_invariants_property.py`
and `docs/adr/0024-error-hierarchy-and-fit-pipeline.md`; edits `tests/test_architecture.py`,
`tests/test_scalar_dp.py`, `docs/api.md`, `docs/adr/index.md`, `docs/reference/results.md`,
`CHANGELOG.md`, the three docs pages, two notebooks, and one example script listed in section 1.
C's `RefusalError` references resolve only once A lands, so C runs the docs tier last.

Gate runner: the Verification block, then the done-criteria greps, then the baseline command
compared against `s3-baseline.txt`.

## Closing report

Session S3 ran on 3 September 2026 on branch `consolidation-s3-library-internals-refactor`
(one Claude Code session; one fable design agent, three sonnet agents; gates run by the
orchestrator).

**Delivered.** The design spec above was written first and the code follows it. The library
now has `src/scorequant/_errors.py`: `ScoreQuantError`, `ContractError` (also a `ValueError`,
so existing `except ValueError` keeps working) and `RefusalError` (a `RuntimeError`) whose
`counterexample` attribute names the registered fixture the refusal rests on; the three names
are exported from the package. Of the 254 raise sites, 183 contract checks became
`ContractError`, six theorem-backed refusals became `RefusalError` (compile refusals citing
`CE-D-VORONOI-CONVERSE-001` and `CE-D-UNMERGED-DUPLICATES-001`, the profiled no-compile refusal
citing `CE-DS-GLOBAL-GEOMETRY-001`, the rank-vacuity refusal citing
`CE-DS-MARGINS-RANK-VACUITY-001`), and `TypeError` and the rest stay as they were. Weight
validation is single-sourced as `validate_weights` in `_validation.py`; `rank_rtol` validation
as `validate_rank_rtol` in `config.py` (it cannot live in `_validation.py` because of the
`_validation -> _execution -> config` import chain), with `transforms.py` as a fifth call site
the packet had not listed. `fit_quantizer` validates and dispatches to
`_fit_compiled_quantizer` and `_fit_geometric_quantizer`; the profiled guard sits at that one
boundary. `schema` is a constructor argument, so `api.py` no longer patches frozen results.
The prediction kernel lives in the new leaf module `_predict.py` (depends only on `_chunking`
and `_execution`); `artifact.py` and `result.py` both import it, and `artifact.py` never
imports `result.py`. The `quantizers.py` seam is gone and `tests/test_scalar_dp.py`
monkeypatches `solvers.scalar._DYNAMIC_WORKING_SET_BYTES` directly. `_SolverSpec.backends` and
its unreachable check are deleted; `source_kind` and `information_kind` are `Literal` aliases
(`SourceKind`, `InformationKind` in `sources.py`). New tests: ten hypothesis property tests in
`tests/test_invariants_property.py` (relabeling, ordering, uniform weight scaling, split-weight
duplication, on both backends) and five layering and refusal assertions in
`tests/test_architecture.py`, including one that every counterexample id cited by a
`RefusalError` exists under `agenticresearch/COUNTEREXAMPLES/`. Docs: ADR 0024, an `Errors`
section and a `Budgets` table in `docs/api.md`, the three exceptions in the results reference,
and a CHANGELOG entry. Refusal messages now end with ` [<counterexample id>]`, so the pinned
evidence JSON for the D_s geometry counterexample, the docs pages, notebooks and tests that
caught `ValueError` around refusals were switched to `RefusalError` and the pinned string
updated.

**Verified.** All green on the branch: `ruff check`, `ruff format --check`, `ty check src`,
the full pytest suite under X64 (493 passed), the float32 leg (4 passed), `uv build`,
`mkdocs build --strict` (exit 0). Bit identity: `tests/test_golden_engine.py` and
`tests/test_execution_backends.py` (the backend-conformance suite) pass unmodified before
(43 passed at `173afc1`, recorded in the session scratch) and after (43 passed), with no diff
to those files or `tests/_oracles.py`; their literals are inline, so passing unchanged is the
proof. Done-criteria greps: no `object.__setattr__` in `api.py`; `quantizers.py` mentions
`solvers.scalar` only in a plain re-export import (the seam is gone); `artifact.py` has no
import of `result.py`.

**Cut or left open.** Nothing in the packet was cut. Two things the packet described
inaccurately are recorded in the spec: the third weight-validation copy was in `ratios.py`,
not `components.py`, and `execution` was already a constructor field, so only `schema` needed
plumbing. The `except ValueError` compatibility promise holds for `ContractError` only;
callers catching `ValueError` around `compile_quantizer` or degenerate profiled fits must
switch to `RefusalError` (CHANGELOG records this as a breaking change).

**The one thing the next session must know.** The public API is now frozen for S4, S6 and
S8: they may quote `sq.ContractError` / `sq.RefusalError` and rely on refusal messages ending
with the counterexample id in brackets. S5 is paused at setup on
`consolidation-s5-manuscript-v9-draft` (local commit, not pushed); its packet carries the
design decisions and resume instructions.
