# AUDIT-DS-POPULATION-BRIDGE — publication-grade audit of the \(D_s\) bridge theorems

**Programme:** P1 (OPEN_PROBLEMS.md) · **Opened:** 28 Aug 2026 · **Status:** active (blocked on session independence)

## Goal

Adversarially audit, per `protocols/audit.md` (all 16 items), the four
theorems produced by `WORK/completed/DS-POPULATION-BRIDGE.md`:

1. `DS-PROFILED-VARIATIONAL` (KNOWN_RESULTS DS11) — including the claim that
   the pseudo-inverse extension leaves the in-bin formulation;
2. `OPEN-DS-POP-COMMON-METRIC` as promoted (DS12 population stationary
   geometry) — especially the bounded-packet stationarity definition, the
   Besicovitch-free affinity argument, and the deployability
   characterization;
3. `DS-EXCHANGE-LEVERAGE-BOUND` (DS13) — the four-line determinant algebra
   and its edge cases (singleton sources, degenerate post-move states);
4. `OPEN-DS-FINITE-POP-BRIDGE` as promoted (DS14 conditional bridge) — the
   highest-value target: the C1 class-embedding step, the VC/slab
   Glivenko–Cantelli step, the two-limit argument in Steps 1–2, the
   compactness/continuity chain in Steps 3–5, and the merged-rule variant.

These are library-load-bearing (future `compile_quantizer` for profiled
criteria) and publication-critical.

## Independence rule

This audit must run in a **fresh session that did not produce the proofs**
(`protocols/audit.md`). Inputs: this packet, the registry branch, KNOWN_RESULTS
DS10–DS14, the two fixtures, `py/ds_population_bridge.py`, and the
N-DS-LEVERAGE / N-DS-BRIDGE-TREND ledger rows. Do not import the researcher
session's context.

## Suggested attack surface (from the researcher's own §G pass)

- ties and null-set discipline in DS12 (a.e. statements under (A4));
- unbounded scores: where exactly \(E\|S\|^2<\infty\) suffices vs. where
  truncation is hidden;
- the (A2) singleton exclusion interacting with DS13 admissibility;
- whether Step 5's class \(\bar Q(c_0,\kappa,\gamma)\) is genuinely compact
  and its value sup continuous;
- the merged-rule variant's subsequence bookkeeping;
- prior-art check of the DS11 variational identity (likely classical in
  regression form — find the exact source or record a bridge status).

## Deliverables

Audit report in `AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md`; hardened
assumptions and `audit:` pointers on the four nodes; any boundary
counterexamples serialized; `literature_search_status` updates.
