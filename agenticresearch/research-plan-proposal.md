# Research plan — goal and crosswalk

**Version:** 2.0 · 5 September 2026
**Status:** canonical statement of the research goal. The executable priority queue, the
current work limit and the parked questions live in `OPEN_PROBLEMS.md`, which wins on any
priority conflict. The twelve-session plan and the 28 August 2026 priority snapshot this file
used to carry are archived as `archive/research-plan-proposal-v1.3.md`; they are history, not
instructions to resume a branch.

ScoreQuant research is organized around **one scientific question at a time**, not around a
collection of individual theorems.

## Research goal

> **Find and characterize the best deployable \(K\)-category compression of score information
> for statistical inference, and provide algorithms whose statistical and optimization
> guarantees are understood.**

Concretely: given a statistical experiment and only \(K\) allowed event categories, which
partition should be used, how is it computed, what information does it retain, and what can be
proved about its geometry, optimality and deployment to unseen events?

$$
X \longrightarrow s(X) \longrightarrow q(s)\in\{1,\dots,K\} \longrightarrow I_q
$$

Four connected questions follow, and every claim in the registry belongs to one of them:

1. **Statistics:** what exactly is the Fisher information after quantization?
2. **Geometry:** what form must an optimal or locally optimal partition have?
3. **Optimization:** how is such a partition found reliably, and when is it certified?
4. **Deployment:** how does a finite training sample become a deterministic rule for future
   observations, and what is retained when the scores were estimated?

The HEP use case is an important specialization, not the definition of the problem. The
D-optimal chain (exact relocation algebra, monotone finite exchange, terminal Mahalanobis
geometry, finite-to-inductive compilation) is the coherent core; profiled \(D_s\) results,
classifier proxies and robustness attach to it.

## Discipline

- **Product-first ordering.** A question that changes what a user can conclude or what the
  library ships outranks an academic branch. The paper is harvested from the audited ledger
  when a publication decision requires it; it is not the driver.
- **One active question.** `OPEN_PROBLEMS.md` names it. A follow-up question is proposed at the
  packet's checkpoint and selected deliberately; it is never activated by default.
- **Unit of work.** One `WORK/` packet holds one substantial scientific question
  (`AGENT.md`, `WORK/TEMPLATE.md`); internal subproblems do not become project tasks.
- **Negative results close packets.** A restricted verdict, a counterexample or a documented
  impossibility is a complete outcome and is recorded with the same care as a theorem.

## Session-to-programme crosswalk

The original plan was drafted as twelve sessions before the product-first decision. This table
maps them onto the programme queue so that older packets and audits remain readable. It carries
no status column: current state lives in `claims/INDEX.md` (generated), `OPEN_PROBLEMS.md` and
`WORK/completed/`.

| Original session | Programme |
|---|---|
| 1 — freeze the problem | delivered as `PROBLEM.md` |
| 2 — finite D audit | delivered as `AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md` |
| 3 — population D geometry | P6 (OP8/OP9 context) |
| 4 — finite ↔ population D | P6 (OP8, OP9) |
| 5 — solver theory | claims D5/D6, library `partition.py`, ADR 0014; residuals P7 (OP12) |
| 6 — global optimization/certification | library `certify.py`; residuals P7 (OP11, OP13) |
| 7 — empirical advantage over k-means | P6 |
| 8 — \(D_s\) as a separate theory | P1, closed 1 September 2026 |
| 9 — HEP mixture specialization | P5 (OP20–OP22) |
| 10 — learned score / ratio oracle | P2, the active question |
| 11 — information loss vs systematics | P3/P5 |
| 12 — synthesis and novelty audit | P8, deferred until the publication decision |
