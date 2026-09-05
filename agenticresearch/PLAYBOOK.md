# Running a research session

Choose work from `OPEN_PROBLEMS.md`. A file in `WORK/active/` may be parked; its location is
not authorization to resume it. One session executes one selected packet.

## Next session

```text
Proposed (not yet packeted): extend O6 (RETENTION-PLUGIN-CLT-FROZEN-SCALAR) from the scalar
retention ratio to the vector-score geometric-mean retention (det R)^(1/d) under a frozen rule --
derive the matrix influence function of the same cell moments, state where log det degenerates,
and run one coverage experiment on a two-parameter example. Alternatively, an independent audit
of O6 before any library use. Choose from OPEN_PROBLEMS.md; write the packet first.
```

## Other session types

- **Independent audit:** a fresh context receives a claim ID and frozen proof/artifacts,
  then follows `protocols/audit.md`. Do not give it the derivation transcript.
- **Literature:** identify one claim or question and follow `protocols/literature.md`.
  A search gap does not prove novelty.
- **Bookkeeping:** name the exact registry/document change; do no new mathematics.

Derivation remains with its owner; wide reading can be delegated under `AGENT.md`.
Do not prescribe a model hierarchy or start additional packets automatically.

## Handoff

Record the verdict, changed claim IDs, evidence, limitations and one proposed next action.
After claim edits, regenerate indexes. Validate with:

```bash
uv run python agenticresearch/py/registry.py reindex
uv run python agenticresearch/py/registry.py validate
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_research_claims.py tests/test_research_registry.py
```

Run the contributor checks relevant to other changed files. Promotion to a shipped guarantee
or publication claim requires independent audit. Pushes and merges require owner authorization.
