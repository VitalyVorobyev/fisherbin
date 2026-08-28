# AUDIT-DS-POPULATION-BRIDGE — publication-grade audit of the profiled Ds population bridge

**Programme:** P1 (Ds bridge) · **Opened:** 28 Aug 2026 · **Status:** completed 28 Aug 2026

## Goal

Adversarially audit, per `protocols/audit.md` (all 16 items), the four
theorems of the DS-POPULATION-BRIDGE packet: `DS-PROFILED-VARIATIONAL`
(DS11), `OPEN-DS-POP-COMMON-METRIC` (DS12), `DS-EXCHANGE-LEVERAGE-BOUND`
(DS13), and `OPEN-DS-FINITE-POP-BRIDGE` (DS14, the highest-value target).

## Outcome

**All four verdicts: verified — none refuted, none reduced.** DS12 and DS13
verified with hardened assumptions (selection-independent deployability and
the atomic-law necessity boundary for DS12; merged atoms dropped, degenerate
destinations closed via Fischer, positive co-weight made explicit for DS13).
DS11 verified with hardened assumptions (centered scores; nonsingular full
nuisance block for the K→∞ part; scope of consequence (c)) and its core
identity re-attributed to classical prior art — Krein (1947) / Anderson
(1971) / Li–Mathias (2000, Thm 2.2), `literature_search_status:
prior_art_found`; the binned transfer and quantizer corollaries stay
project-level. DS14 verified as a **conditional** theorem after the audit
supplied the fixed-class slab Glivenko–Cantelli step, the derived
\(\Lambda=2E\|S\|^2\), the explicit compact parameter set, the two-sided
fixed-point identification, and the general-\(d_\psi\) merged-variant value
argument; its "audit pending" warning is lifted, the conditional-margins
warning stays (OP28). Independent exact evidence: 1,748 admissible moves at
all 171 stable states of five adversarial datasets (vector nuisance, vector
POI, duplicates, singular destinations) with zero violations; 400
variational-identity instances; both packet fixtures re-verified from raw
scores; a fully exact N=10 scan reconfirming singleton cells at global
optima. DS12–DS14 prior-art search: gap re-confirmed with fresh queries.

## Artifacts

- `AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md` (16-item report)
- `py/audit_ds_population_bridge.py` (independent pure-stdlib exact suite)
- `tests/test_research_claims.py::test_ds13_leverage_bound_at_every_stable_state_with_vector_nuisance`
- `NUMERICAL_EVIDENCE.md` rows `N-DS-AUDIT-LEVERAGE`, `N-DS-AUDIT-VARIATIONAL`,
  `N-DS-AUDIT-MARGINS`
- `CLAIMS.json`: node `AUDIT-DS-POPULATION-BRIDGE` added; audit pointers,
  hardened assumptions, and `literature_search_status` on all four audited
  nodes; `Li-Mathias-2000` bibliography entry; DS14 warning updated
- `KNOWN_RESULTS.md` DS11–DS14 hardened in place (including the stale DS13
  evidence-count fix); `LITERATURE.md` targeted-audit subsection (28 Aug 2026)
- Boundary reinterpretation: `CE-DS-GLOBAL-GEOMETRY-001` cited from DS12 as
  the atomic-law necessity witness

## Next dependency-blocking question

`OPEN-DS-MARGINS-AT-OPTIMA` (OP28): are the DS14 margins automatic at finite
Ds optima under light-tailed atomless laws, at least after merging
Φ-neutral splits? This is now the sole obstacle between the conditional
bridge and an unconditional compile guarantee for profiled criteria.
