# S07 — HEP classifier showcase

**Workstream:** W4 · **Needs:** S4 · **Parallel with:** S6 · **Status:** queued

## Goal

Close the last W4 gap: HEP has no example at all today. **S4's spike settled the dataset question
in favour of the HEP route, so the FlowCyt fallback this packet used to describe is cut and must
not be built.** Read the "HEP data spike record" section of
`docs/programme/S04-showcase-foundations.md` for the verified facts; the short version is the FAIR
Universe HiggsML Uncertainty Challenge public dataset, DOI `10.5281/zenodo.15131565`, CC-BY-4.0,
Parquet, with a 0.13 MB sample of 1,000 rows x 31 columns already committed upstream and an
explicit `tes` tau-energy-scale nuisance implemented as a transformation of `PRI_had_pt`.

This session builds `examples/hep_classifier/`: a Door 3 route (classifier to ratios to scores)
through profiled \(D_s\) with the tau-energy-scale nuisance, on a committed fixture no larger than
5 MB with its hash and licence recorded. Done means the roadmap W4 gate names the provenance of
every number the example reports, not just that the example runs.

## Inputs

- `docs/programme/README.md`: orchestrator contract and delegation ladder, read first.
- `docs/programme/S04-showcase-foundations.md`: the "HEP data spike record" section carries the
  verified dataset facts — DOI, licence, format, sample size and shape, the nuisance list, and the
  provenance warning that the upstream GitHub repository has no licence file so the CC-BY-4.0
  claim must cite the Zenodo record. Also the Michelson example, whose analytic-nuisance arc this
  session should not duplicate.
- `examples/cell_population/`: the module shape to mirror — the only existing example built around
  a real, externally licensed dataset.
- `examples/data/README.md`: the provenance pattern a committed third-party fixture follows.
- `examples/door3_classifier.py`: the existing Door 3 (classifier to ratios to scores) pattern.
- `docs/examples/flowcyt-teaser.md`: existing FlowCyt doc page, precedent for the new doc page.
- `docs/three-doors.md`: Door 3 contract this example must match.
- `tests/test_evidence_suite.py`: pins evidence JSON; the new example's numbers register here.
- `docs/roadmap.md`: M12 W4 gate block; this session updates it to name the provenance of every
  reported number.

## Deliverables

- `examples/hep_classifier/`: Door 3 to profiled \(D_s\) with the tau-energy-scale nuisance,
  following the module shape of `examples/cell_population/` (a `data.py` contract layer, a
  `scores.py` classifier-to-score bridge, an `experiment.py`, a `figures.py`).
- A committed fixture, 5 MB or smaller, with its hash and the CC-BY-4.0 licence and Zenodo DOI
  recorded alongside it, following `examples/data/README.md`'s existing provenance pattern.
- `docs/usecases/hep/`: doc page for the example.
- A notebook (`examples/notebooks/hep_classifier.ipynb`, matching the existing convention).
- Evidence JSON pinned in `tests/test_evidence_suite.py`.
- `docs/roadmap.md` W4 gate text names the provenance (dataset, licence, fixture hash) of every
  number the example reports.

**Cut:** the FlowCyt three-interface fallback (`examples/cell_population/integration.py`). S4
confirmed a usable HEP dataset, so building the fallback would add a second FlowCyt example that
no gate asks for.

## Done criteria

- `examples/hep_classifier/` exists, is present in the mkdocs nav, and executes in fast mode under
  both test tiers.
- The committed fixture is 5 MB or smaller and its hash, licence (CC-BY-4.0) and Zenodo DOI are
  recorded in the example's doc page or a sibling file, citing the Zenodo record and not the
  unlicensed upstream GitHub path.
- Evidence JSON for the example is pinned in `tests/test_evidence_suite.py`.
- `docs/roadmap.md` W4 gate names the provenance of every number in the example's output.
- Full handoff gate green (see Verification).
- roadmap M12 table shows S07 `done`; this packet's Closing report is written.

## Delegation

| Task | Tier | Output |
|---|---|---|
| Design the statistical arc (which parameters are of interest, how `tes` enters the score, what the naive baseline is) | orchestrator inline (never `fable`) | written spec appended to this packet before code starts |
| Implement the example script, notebook, doc page, and evidence pinning | sonnet | source and doc diff |
| Verify fixture size, hash, and licence; cite the Zenodo DOI not the GitHub path | haiku | verification log |
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

- **Resolved by S4:** HEP is built and the FlowCyt fallback is cut.
- The exact event/feature subset that keeps the fixture at or under 5 MB, and whether the upstream
  0.13 MB sample is enough. It carries all four processes but only 26 `ttbar` and 4 `diboson` rows,
  so it supports the `tes` nuisance (which acts on every event) and not the background-normalization
  nuisances. If a larger fixture is wanted, S4's record notes the cost: one 15.1 GB download from
  the Zenodo release.
- Whether the classifier is trained inside the example or its calibrated posteriors are committed
  alongside the fixture. `examples/cell_population/scores.py` trains a
  `HistGradientBoostingClassifier` at run time; at 1,000 rows that is cheap, so training in-example
  is probably right, but the fast-mode budget decides.

## Closing report

_Written at session end. Plain English, for a reader who did not watch the session: what was
delivered, what was verified (commands and results), what was cut or left open, and the one thing
the next session must know._
