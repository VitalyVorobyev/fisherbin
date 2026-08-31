# ScoreQuant LLM research workspace

**Version:** 4.1 · 31 August 2026

A theorem-oriented scientific memory for **D- and \(D_s\)-optimal hard
quantization of multivariate score space**, operated by research agents
(Claude Code, Codex, or any harness — the files are the contract). Knowledge
is stored finely (one claim per node); work is executed coarsely (one
`WORK/` packet per session).

## Read order (canonical — the only one)

A map, not a manual. Read 1–3 always; read everything else on demand.

1. `PROBLEM.md` — canonical problem and goals.
2. `AGENT.md` — invariants, map, claim-graph lookup, session policy.
3. Your `WORK/active/` packet (or `OPEN_PROBLEMS.md` to pick one).
4. The claim branch relevant to the packet — `python py/registry.py show <ID>
   --deps --proof` returns the node, its dependency closure, and its proof
   prose. Never read `claims/` linearly. Then the rest of what the branch
   cites: `COUNTEREXAMPLES/` fixtures, `LITERATURE/` entries,
   `NUMERICAL_EVIDENCE.md` rows.
5. The `protocols/` file for the activity at hand
   (`theorem`, `audit`, `literature`, `numerical`, `algorithm`, or
   `formalization`).
6. `manuscripts/README.md` — only if the task concerns the paper; never load
   the article bodies.
7. `archive/`, `design/` — historical/meta context only; canonical files win
   on any conflict.

`AGENT.md` and `registry.json` defer to this order; no other file defines one
(`LITERATURE/index.md`'s reading order is for literature study, not a
workspace read order).

## Workspace map

| Path | Role |
|---|---|
| `PLAYBOOK.md` | Operator playbook: copy-paste session prompts (research/audit/bookkeeping/literature) |
| `PROBLEM.md` | Canonical scientific target |
| `AGENT.md` | Non-negotiable invariants + map (short) |
| `registry.json` | Shared vocabularies, programme queue, bibliography |
| `claims/` | Fine-grained theorem/claim graph, one file per claim |
| `claims/INDEX.md` | **Generated** claim digest, grouped by programme in queue order |
| `py/registry.py` | `validate` / `reindex` / `show <ID> --deps --proof` |
| `KNOWN_RESULTS/` | Human-readable current mathematical state, one file per chapter |
| `OPEN_PROBLEMS.md` | The single priority queue: 8 programmes, OP sub-items |
| `research-plan-proposal.md` | North star, session model, roadmap narrative |
| `WORK/active/`, `WORK/completed/` | Coarse work packets (one per session) |
| `protocols/` | Detailed recipes, read when relevant |
| `formal/` | Pinned Lean/Mathlib workspace for selected machine-checked claim evidence |
| `COUNTEREXAMPLES/` | Immutable exact falsification fixtures |
| `AUDITS/` | Publication-grade audit reports |
| `LITERATURE/`, `../papers/` | Curated prior art + discovery state |
| `NUMERICAL_EVIDENCE.md` | Measured ledger; never theorem authority |
| `manuscripts/` | Frozen paper snapshots (lagging; see its README) |
| `py/` | Workspace numerical scripts and the registry tool |
| `design/` | Meta-reviews of the workspace itself |
| `archive/` | Historical documents |

CI keeps the memory honest: `tests/test_research_registry.py` runs
`py/registry.py validate` and the index-freshness check, and
`tests/test_research_claims.py` pins the counterexample fixtures. Both run in
the library's test suite, and a bookkeeping session can run the same checks
directly with `python py/registry.py validate`.

Formal evidence remains subordinate to this registry. An optional
`formal_proof` object links one exact claim to its reviewed Lean spec, theorem,
and statement audit; generated indexes display the marker. `lake build`,
`axiom-audit`, and `leanchecker` check the proof environment in separate CI,
while registry status continues to distinguish published, bridged, internally
proved, measured, and open work.

## Canonical scope

Construct a deployable hard \(K\)-cell quantizer of event score (or an
explicitly tracked score proxy) that preserves maximal **D** or **\(D_s\)**
Fisher information and reports information loss relative to unbinned
inference. Supported model access: direct scores; exact/autodiff scores;
analytic or learned density ratios; component ratios; calibrated classifiers.
Primary application: multicomponent linear/template fitting with nuisance
parameters, especially HEP. The research queue is ordered **product-first**
(see `research-plan-proposal.md`): theorems that unblock shippable library
capabilities outrank purely academic branches; the paper is harvested from
the ledger, not the other way around.

## Discipline

- `PROBLEM.md` defines the target; `KNOWN_RESULTS/` the canonical state;
  `claims/` machine-readable status/dependencies.
- `OPEN_PROBLEMS.md` must not contain already-solved claims.
- Every exact counterexample gets a permanent artifact; every solver
  distinguishes sample-only labels from a deployable quantizer; every
  evaluation reports D/\(D_s\) retention versus unbinned inference.
- Claims are atomic; work is not.

## Registry model

A machine-readable theorem graph, not a narrative document. One file per claim
under `claims/<CLAIM-ID>.json`; the shared vocabularies, the programme queue,
and the bibliography live in `registry.json`.

Each node has a stable `id` and may carry: `status`, `criterion`, `level`,
`statement`, `assumptions`, `dependencies`, `implies`, `converse_failures`,
`counterexamples`, `boundary_counterexamples`, `literature`,
`literature_search_status`, `proof_location`, `publication_status`, `audit`,
`artifact`, `formal_proof`, `programme`, `role`, `warning`.

**Nothing derived is stored by hand.** `claims/INDEX.md`,
`COUNTEREXAMPLES/INDEX.md`, and `LITERATURE/BIBLIOGRAPHY.md` are regenerated by
`python py/registry.py reindex`; `python py/registry.py validate` is what CI
runs, and it fails on a dead packet pointer, an unresolvable claim id in the
evidence ledger, a result section that does not declare its claims, an open
claim with no programme, a duplicated result label, or a stale index.

To investigate a claim: `python py/registry.py show <ID> --deps --proof`, then
check `converse_failures` and `counterexamples` before proposing anything
stronger, and patch the node's file when you are done.
