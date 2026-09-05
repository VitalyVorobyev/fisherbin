# Running a research session

Choose work from `OPEN_PROBLEMS.md`. A file in `WORK/active/` may be parked; its location is
not authorization to resume it. One session executes one selected packet.

## Next session

```text
Execute agenticresearch/WORK/active/SCORE-ORACLE-ROBUSTNESS.md.
Follow agenticresearch/README.md and protocols/theorem.md.
Derive the frozen-rule scalar retention uncertainty result, run its one falsification/
coverage experiment, and stop at proved, refuted or reduced. No new public API.
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
