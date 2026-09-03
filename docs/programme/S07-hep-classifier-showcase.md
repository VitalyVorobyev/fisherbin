# S07 — HEP classifier showcase (fallback: FlowCyt three-interface benchmark)

**Workstream:** W4 · **Needs:** S4 · **Parallel with:** S6 · **Status:** queued

## Goal

Close the last W4 gap: HEP has no example at all today. If S4's data spike confirmed a usable,
licensed dataset, this session builds `examples/hep_classifier/`, a Door 3 (classifier to ratios
to scores) route through profiled D_s with the tau-energy-scale nuisance, on a committed fixture
no larger than 5 MB with hash and licence recorded. If S4 found no usable dataset, this session
instead builds the fallback: a three-interface comparison on the FlowCyt fixture already committed
at `examples/data/flowcyt_fixture.npz`. Either way, done means the roadmap W4 gate names the
provenance of every number the example reports, not just that the example runs.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S04-showcase-foundations.md`: S4 closing report; carries the HEP dataset spike
  verdict that decides which deliverable this session builds.
- `examples/cell_population/`: the existing FlowCyt example structure, reused wholesale if the
  fallback path is taken.
- `examples/data/flowcyt_fixture.npz`: the committed fixture the fallback path compares against.
- `examples/door3_classifier.py`: the existing Door 3 (classifier to ratios to scores) pattern.
- `docs/examples/flowcyt-teaser.md`: existing FlowCyt doc page, precedent for the new doc page.
- `docs/three-doors.md`: Door 3 contract this example must match.
- `tests/test_evidence_suite.py`: pins evidence JSON; the new example's numbers register here.
- `docs/roadmap.md`: M12 W4 gate block; this session updates it to name the provenance of every
  reported number.

## Deliverables

If S4 confirmed a usable dataset:

- `examples/hep_classifier/`: Door 3 to profiled D_s with the tau-energy-scale nuisance.
- A committed fixture, 5 MB or smaller, with its hash and licence recorded alongside it.
- `docs/usecases/hep/`: doc page for the example.
- A notebook (`examples/notebooks/hep_classifier.ipynb`, matching the existing convention).
- Evidence JSON pinned in `tests/test_evidence_suite.py`.

If S4 found no usable dataset (fallback):

- `examples/cell_population/integration.py`: compares precomputed scores vs classifier-to-ratios-
  to-scores vs explicit component densities, all on the committed FlowCyt fixture.
- A doc page and evidence JSON for the comparison, following the same conventions as above.

Either way:

- `docs/roadmap.md` W4 gate text names the provenance (dataset, licence, or fixture source) of
  every number the chosen example reports.

## Done criteria

- The chosen example (HEP or fallback) exists, is present in the mkdocs nav, and executes in fast
  mode under both test tiers.
- If HEP was chosen: the committed fixture is 5 MB or smaller and its hash and licence are
  recorded in the example's doc page or a sibling file.
- Evidence JSON for the chosen example is pinned in `tests/test_evidence_suite.py`.
- `docs/roadmap.md` W4 gate names the provenance of every number in the example's output.
- Full handoff gate green (see Verification).
- roadmap M12 table shows S07 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Design the statistical comparison (HEP nuisance profiling, or the three-interface FlowCyt benchmark) | fable | written spec appended to this packet before code starts |
| Implement the example script, notebook, doc page, and evidence pinning | sonnet | source and doc diff |
| Verify fixture size, hash, and licence (HEP path only) | haiku | verification log |
| Update `docs/roadmap.md` W4 gate text with provenance | haiku | roadmap diff |
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

- Whether HEP or the fallback is built: decided by S4's closing report, not by this packet. If S4
  left the question genuinely open (neither confirmed nor ruled out), this session re-runs the
  fetch check itself before committing to a path.
- If HEP is chosen, the exact event/feature subset that keeps the fixture at or under 5 MB.

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
