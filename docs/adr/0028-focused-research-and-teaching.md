# ADR 0028: Focus research on user decisions and documentation on executable lessons

**Status:** Accepted

**Extends:** ADR 0027 (URL topology stays unchanged); the completed M12 programme remains historical.

## Context

The owner's 5 September review request reopens research focus and documentation quality after
M12's technical gates passed. The assessment in `docs/programme/2026-09-05-review.md` finds useful
mathematics and sound task boundaries, alongside stale priorities, inaccurate explanatory
summaries and a portal whose first reader must navigate long motivation before seeing a task.

## Decision

Preserve the two public tasks, source/provider separation, criterion-specific capability table,
shared JAX/NumPy mathematics, research fixtures and audit authority. The next milestone improves
interpretation and teaching; it does not expand the numerical API by default.

The research priority queue remains `agenticresearch/OPEN_PROBLEMS.md`. One scientific question
is active at a time, with independent verification of a frozen artifact allowed alongside it.
The next question is evaluation of retained true-score information for a frozen estimated-score
rule. Refit stability, calibration rates and universal robustness claims do not block that first
question. Closed DS deployment conclusions stand; exact-complexity remainders need an explicit
reopening decision with a scientific or user payoff.

`docs/roadmap.md` owns implementation phases and their status. Research packets own scientific
work. Completed programme packets are history, not standing instructions for future sessions.
A future coordinator chooses bounded delegation by need; no model-brand ladder or obligatory
multi-agent hierarchy is part of the architecture.

Each teaching page states its question, model/reference point, admissible labels, input measure,
score provenance, task, output and evaluation regime before detailed exposition. Captured numbers
must be accompanied by the right interpretation. Figures must correspond to the deployed rule;
visual polish, source provenance and passing snippet tests do not establish that correspondence.

Use one exemplar walkthrough to validate this contract before revising the other three. Preserve
static explanations and precomputed evidence; load computation only through an explicit action.
Keep current URLs and build systems while improving content. No new site migration is implied.

Formal proof work is a bounded verification lane. First reconcile and integrate the existing
scalar pilot separately, including statement review, exact coverage and toolchain gates. Neither a
Lean build nor a formal claim marker certifies equivalence of the production implementation.

## Consequences

- Some open mathematical branches remain parked even when interesting. Their claims and proofs
  remain accessible and unchanged.
- A negative or restricted result can close a packet. Additional questions do not automatically
  become active tasks or trigger a manuscript rewrite.
- Human reader checks supplement automated tests. A page is complete only when its task can be
  correctly explained and its example reproduced by someone outside the authoring context.
- Public abstraction changes require a concrete second consumer, semantics, migration notes and
  proportional regression tests. Diagnostic experiments stay in examples until then.
- Research graph relation cleanup is a separate reviewed migration: mathematical dependencies,
  audit evidence and open remainders must not be silently relabelled during prose cleanup.

## Alternatives considered

A complete site rewrite would preserve the same content problems while adding routing risk.
Adding algorithms would enlarge the teaching burden. Deleting the research archive would destroy
useful falsification memory. Making formalization mandatory for every exploratory claim would
shift the focus problem into another toolchain. None is adopted.

## Validation

M13 supplies executable gates for correctness, the teaching pilot, the remaining walkthroughs,
research evidence and formal integration. Existing Python, docs and package gates remain in force.
The owner request authorizes these local planning changes; publication and merges remain separate.
