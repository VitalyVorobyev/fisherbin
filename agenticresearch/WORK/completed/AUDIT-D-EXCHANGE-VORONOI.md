# AUDIT-D-EXCHANGE-VORONOI — publication-grade audit of the finite D exchange⇒Voronoi theorem

**Programme:** (pre-dated the programme queue; maps to the D core) · **Opened:** 26 Aug 2026 · **Status:** completed 27 Aug 2026

## Goal

Determine whether the finite D exchange→Voronoi theorem survives a
publication-grade adversarial audit.

## Outcome

Theorem verified after making its duplicate-atom, feasibility, and tolerance
assumptions explicit. `AUDIT-D-EXCHANGE-VORONOI` promoted `open →
project_proved`; `D-EXCHANGE-IMPLIES-VORONOI` restated with six explicit
assumptions; new boundary counterexample `CE-D-UNMERGED-DUPLICATES-001`
(claim `D-UNMERGED-DUPLICATES-FAIL`); targeted prior-art search recorded as a
search gap, not novelty.

## Artifacts

- `AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md` (16-item report; the audit exemplar)
- `COUNTEREXAMPLES/CE-D-UNMERGED-DUPLICATES-001.json`
- `py/audit_d_exchange_voronoi.py` (80 data sets, exact-rational, PASS)
- `NUMERICAL_EVIDENCE.md` row `N-D-AUDIT-EXACT`
- `tests/test_research_claims.py::test_unmerged_duplicate_atoms_are_an_exact_boundary_failure`

This packet is the reference for task size: several claim nodes, one coherent
scientific question, one session.
