# S04 — Showcase foundations (Gaussian/Michelson, NumPy example, HEP data spike)

**Workstream:** W4 · **Needs:** S3 · **Parallel with:** S5 · **Status:** queued

## Goal

Close two of the four gaps in W4's per-input-route showcase gate and de-risk the third. Today the
analytic `ScoreFunction` route and the NumPy backend have no example at all, and
`CentralLogRatioScore` is documented but never executed in the docs. This session builds one
example that covers both the `ScoreFunction` route and the NumPy backend at once
(Gaussian/Michelson, D vs profiled D_s with an explicit nuisance), adds one executed
`CentralLogRatioScore` fence to `docs/three-doors.md`, and spikes whether a HEP dataset is usable
for S7 (HiggsML Uncertainty Challenge first, then ATLAS Open Data, then MadMiner tutorial
outputs). Done means the new example runs in fast mode in both test tiers and the S7 dataset
question has a recorded answer, not an open one.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S03-library-internals-refactor.md`: S3 closing report; this session must build
  against the post-refactor API, not the pre-refactor one.
- `examples/gaussian_location.py`: closest existing example for statistical-design pattern.
- `examples/nuisance_profiled_ds.py`: existing profiled D_s pattern to reuse for the nuisance.
- `docs/examples/index.md`: current example index; the new page joins this list.
- `docs/three-doors.md`: holds the `CentralLogRatioScore` fence this session must make executable.
- `tests/test_evidence_suite.py`: pins evidence JSON; the new example's numbers register here.
- `docs/adr/0018-explicit-multi-backend-execution.md`: NumPy backend contract this example must
  demonstrate via `ExecutionConfig(backend="numpy")`.
- `mkdocs.yml`: nav entry for the new example page.
- `docs/roadmap.md`: M12 W4 gate block; this session's closing report is where the roadmap names
  the S7 dataset choice.

## Deliverables

- `examples/gaussian_michelson.py`: analytic `ScoreFunction` example, D vs profiled D_s with an
  explicit nuisance parameter, run on `ExecutionConfig(backend="numpy")`.
- `docs/examples/gaussian-michelson.md`: doc page for the example, added to the mkdocs nav.
- A notebook for the example (paired with the doc page, matching the existing example pattern).
- Evidence JSON for the new example pinned in `tests/test_evidence_suite.py`.
- One executed `CentralLogRatioScore` code fence added to `docs/three-doors.md`.
- HEP data spike: for each candidate dataset (HiggsML Uncertainty Challenge, ATLAS Open Data,
  MadMiner tutorial outputs, in that priority order), record URL, licence, size, and nuisance
  parameters, verified by actually fetching the data, not by reading its landing page. This record
  lives only in the S04 closing report, not in a separate repo file.

## Done criteria

- `examples/gaussian_michelson.py` and its doc page exist and the doc page is present in
  `mkdocs.yml` nav.
- The example executes in `SCOREQUANT_EXAMPLE_FAST` mode under both `tests/test_notebooks.py` and
  the docs-execution tier.
- The `CentralLogRatioScore` fence in `docs/three-doors.md` executes under
  `tests/test_docs_snippets.py`.
- `tests/test_evidence_suite.py` includes and pins the new example's evidence JSON.
- The S04 closing report names a usable HEP dataset (or states plainly that none of the three
  candidates is usable, with the reason for each).
- Full handoff gate green (see Verification).
- roadmap M12 table shows S04 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Design the Gaussian/Michelson statistical example (nuisance structure, D vs profiled D_s comparison) | fable | written spec appended to this packet before code starts |
| Implement the example script, notebook, doc page, and evidence pinning | sonnet | source and doc diff |
| Make the `CentralLogRatioScore` fence in `docs/three-doors.md` executable | sonnet | doc diff |
| Fetch and verify each HEP dataset candidate (URL, licence, size, nuisance parameters) | haiku | fetch log and verdict per dataset |
| Run gates, add nav entry, report failures verbatim | haiku | gate output |

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

- Which HEP dataset S7 uses, if any: the plan sets the fetch priority (HiggsML, then ATLAS Open
  Data, then MadMiner tutorial outputs) but the final pick depends on what this session's spike
  finds usable. If none is usable, S7 falls back to the FlowCyt three-interface benchmark by
  default.
- Notebook format and location: the plan requires a notebook but does not name its path; follow
  the existing `examples/notebooks/` convention used by other examples.

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
