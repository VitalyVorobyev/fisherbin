# ScoreQuant LLM research workspace

**Version:** 3.0 · 28 August 2026

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
4. The `CLAIMS.json` branch relevant to the packet (graph lookup, never a
   linear read), then the documents that branch cites: `KNOWN_RESULTS.md`
   sections, `COUNTEREXAMPLES/` fixtures, `LITERATURE.md` entries,
   `NUMERICAL_EVIDENCE.md` rows.
5. The `protocols/` file for the activity at hand
   (`theorem`, `audit`, `literature`, `numerical`, `algorithm`).
6. `manuscripts/README.md` — only if the task concerns the paper; never load
   the article bodies.
7. `archive/`, `design/` — historical/meta context only; canonical files win
   on any conflict.

`AGENT.md` and `CLAIMS.json` defer to this order; no other file defines one
(`LITERATURE.md` §7 is a paper reading order for literature study, not a
workspace read order).

## Workspace map

| Path | Role |
|---|---|
| `PLAYBOOK.md` | Operator playbook: copy-paste session prompts (research/audit/bookkeeping/literature) |
| `PROBLEM.md` | Canonical scientific target |
| `AGENT.md` | Non-negotiable invariants + map (short) |
| `CLAIMS.json` | Fine-grained theorem/claim dependency graph (96 nodes) |
| `KNOWN_RESULTS.md` | Human-readable current mathematical state |
| `OPEN_PROBLEMS.md` | The single priority queue: 8 programmes, OP sub-items |
| `research-plan-proposal.md` | North star, session model, roadmap narrative |
| `WORK/active/`, `WORK/completed/` | Coarse work packets (one per session) |
| `protocols/` | Detailed recipes, read when relevant |
| `COUNTEREXAMPLES/` | Immutable exact falsification fixtures |
| `AUDITS/` | Publication-grade audit reports |
| `LITERATURE.md`, `LITERATURE/`, `../papers/` | Curated prior art + discovery state |
| `NUMERICAL_EVIDENCE.md` | Measured ledger; never theorem authority |
| `manuscripts/` | Frozen paper snapshots (lagging; see its README) |
| `py/` | Workspace numerical scripts |
| `design/` | Meta-reviews of the workspace itself |
| `archive/` | Historical documents |

CI keeps the memory honest: `tests/test_research_registry.py` (registry
integrity) and `tests/test_research_claims.py` (fixture-pinned claims) run in
the library's test suite.

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

- `PROBLEM.md` defines the target; `KNOWN_RESULTS.md` the canonical state;
  `CLAIMS.json` machine-readable status/dependencies.
- `OPEN_PROBLEMS.md` must not contain already-solved claims.
- Every exact counterexample gets a permanent artifact; every solver
  distinguishes sample-only labels from a deployable quantizer; every
  evaluation reports D/\(D_s\) retention versus unbinned inference.
- Claims are atomic; work is not.

## CLAIMS.json registry model

A machine-readable theorem graph, not a narrative document. Each node has a
stable `id` and may carry: `status`, `criterion`, `level`, `statement`,
`assumptions`, `dependencies`, `implies`, `converse_failures`,
`counterexamples`, `boundary_counterexamples`, `literature`,
`literature_search_status`, `proof_location`, `publication_status`, `audit`,
`artifact`, `priority`, `role`, `warning`. Generated indexes exist by status,
criterion, and level. Locate a node, recursively follow `dependencies`, open
`proof_location` for the detailed statement (protocol in `AGENT.md`).
