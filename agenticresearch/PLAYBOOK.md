# Operator playbook — running research sessions

How to drive this workspace as the human operator. Works with Claude Code or
Codex; the prompts below are copy-paste ready. One session = one `WORK/`
packet. Keep prompts short — the workspace files carry the protocol, so the
prompt only needs to point at them.

## Session types at a glance

| Session | Model / effort | Context rule |
|---|---|---|
| Research (theorem work) | Strongest model, extended thinking / high reasoning | Owns the packet; delegates reads, never derivation |
| Adversarial audit | Strongest model, extended thinking | **Fresh session**; must not share the researcher's context |
| Bookkeeping | Mid-tier model is fine | Registry/doc edits; validator tests catch slips |
| Literature | Mid-tier + web search | Writes into `LITERATURE/`, links papers to claim ids |

## 1. Research session (the default)

Start a fresh session in the repo root, on a fresh branch, and paste:

```text
You are running a ScoreQuant research session.

Read agenticresearch/README.md and follow its canonical read order.
Execute the work packet agenticresearch/WORK/active/DS-POPULATION-BRIDGE.md
following agenticresearch/protocols/theorem.md. Falsify before proving.

Rules of engagement:
- Work on branch research-<packet-id>; commit as you go.
- Delegate wide reading and exhaustive numerical searches if your harness
  supports it; do the mathematics yourself.
- Do not re-derive project_proved claims; if one looks wrong, record an
  audit task instead.
- Before finishing: patch CLAIMS.json (regenerate indexes), serialize any
  counterexample, update the packet's status, and run
  JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_research_claims.py tests/test_research_registry.py
  and uv run ruff check . — both must be green.
- End with the packet's stop-condition verdict and the next
  dependency-blocking question.
```

Swap the packet path for whichever `WORK/active/` packet is current. If no
packet exists yet, first ask a session (or do it yourself) to draft one from
the top unblocked programme in `OPEN_PROBLEMS.md` using `WORK/TEMPLATE.md`.

## 2. Adversarial audit session

Run only when a result is being promoted (novelty/publication claim, or a
guarantee the library will ship). **Must be a brand-new session** — never a
continuation of the researcher's session, and never given the researcher's
chat transcript. Paste:

```text
You are an independent adversarial auditor for a ScoreQuant research claim.
You did not produce this proof; your job is to break it.

Read agenticresearch/README.md (canonical read order), then
agenticresearch/protocols/audit.md and follow its 16-item output contract
exactly. AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md is the size/rigor exemplar.

Audit target: claim <CLAIM-ID> in agenticresearch/CLAIMS.json, proof at
<proof_location>.

Rules of engagement:
- Recheck every dependency yourself; do not trust the researcher's summary.
- Run your own counterexample search per protocols/numerical.md (exact
  rationals; attack ties, duplicates, singletons, singular information).
- Run your own targeted prior-art search per protocols/literature.md; an
  empty result is a search gap, never novelty.
- Verdict must be one of: verified (possibly with hardened assumptions),
  refuted (with a serialized counterexample), or reduced to explicitly
  listed unresolved assumptions.
- Deliverables: AUDITS/AUDIT-<CLAIM-ID>-00N.md, registry patch, any
  boundary counterexamples with fixtures and a pinned test, and the same
  green test/lint gate as a research session.
```

## 3. Bookkeeping session

```text
Bookkeeping session for agenticresearch/ — no mathematics.
Read agenticresearch/README.md. Task: <e.g. regenerate CLAIMS.json indexes
after manual edits / serialize the counterexample described in <file> /
sync KNOWN_RESULTS section X with claim Y>.
Finish with JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest
tests/test_research_registry.py tests/test_research_claims.py and
uv run ruff check . green.
```

## 4. Literature session

```text
Literature session for agenticresearch/. Read agenticresearch/README.md and
agenticresearch/protocols/literature.md. Run one snowballing round from
LITERATURE/seeds.md (or the targeted novelty search for claim <ID>).
Record per-round candidate/relevant counts in LITERATURE/graph.json, update
reviewed.md / rejected.md / gaps.md, and link every paper to claim ids.
Do not change claim statuses; report proposed status changes instead.
```

## After any session (operator checklist)

1. `git log --oneline` — commits are small and labeled.
2. `JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_research_claims.py tests/test_research_registry.py` — green.
3. Skim the packet file — status updated, stop condition addressed.
4. Open a PR; the registry validator runs in CI on every push.
5. If a result was promoted toward publication-critical, schedule the audit
   session (type 2) before merging the promotion.

## Escalation ladder (from AGENT.md)

- exploratory lemma → one research session;
- promising theorem → research session + one independent audit session;
- publication-critical claim → research + adversarial audit + independent
  prior-art search (types 2 and 4, separate sessions).
