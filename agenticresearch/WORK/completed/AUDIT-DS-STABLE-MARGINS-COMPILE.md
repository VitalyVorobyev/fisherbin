# AUDIT-DS-STABLE-MARGINS-COMPILE — adversarial audit of DS16

**Programme:** P1 · **Opened:** 30 August 2026 · **Closed:** 30 August 2026 · **Status:** completed
**Source:** `research-ds-stable-margins-compile` at `1b58518`

## Goal

Independently verify, harden, refute, or reduce the DS16 complex:
`DS-STABLE-MARGINS-PRICE`, `DS-PROFILED-COMPILE-CERTIFICATE`, and
`DS-STABLE-STATE-SELECTION`. The auditor did not produce DS16 and will not
trust its proof instrument or classification logic.

The deliverable is the 16-item publication-grade report
`AUDITS/AUDIT-DS-STABLE-MARGINS-COMPILE-001.md`, together with the exact
numerical, literature, registry, counterexample, and manuscript consequences
required by `protocols/audit.md`.

## Independence contract

- Re-derive DS16 from the Proposition-4 sandwich. Recheck the statements and
  imported hypotheses of DS11--DS15 without re-proving those audited claims;
  open a separate audit task if an imported result appears false.
- Do not import `py/ds_stable_margins.py` or reuse its stability classifier.
  The audit classifier recomputes every candidate state and move independently
  in pure-stdlib exact arithmetic.
- Recompute both DS16 fixtures from their raw scores and labels, independently
  reproduce a sample of the census headlines and one public-library seeding
  run at `N=100`, and run a fresh adversarial counterexample search.
- Run a fresh theorem-level prior-art pass. The researcher-side literature
  audit is comparison material only and supplies no audit conclusion.
- Do not edit `src/`.

## Attack plan

1. Check Lemma DS16.1 step by step: inactive-cell control, the `K` versus
   `K-1` distortion gap, active-centroid compactness, arbitrary groupings and
   split duplicates, the nearest-centroid comparison, and misassignment slabs.
   In particular, test whether the claimed pointwise SLLN at a data-dependent
   subsequential centroid limit needs a uniform compact-centroid law.
2. Verify the signed weighted-VC Glivenko--Cantelli statement uniformly in the
   tilt, its envelope integrability, boundary continuity, and the common
   probability-one event needed for every labeling sequence.
3. Audit PRICE and FUNNEL for strictness, empty constrained classes,
   measurability, relabeling, singular boundaries, and the exact role of `(R)`.
4. Separate `v^{*+}(kappa)` from DS15's `v^*(kappa)`. Check the FLOOR under
   empirical centering and do not infer constrained-value attainment or
   one-sided continuity unless they are actually proved.
5. Re-derive the centered-sample cardinality requirement through rank and
   Schur-rank additivity; reject any off-centered restatement that is not valid
   score/Fisher semantics.
6. Audit the compile verdict independently: distinguish an established path
   from uniqueness, a DS14-certified sequence from a single finite fit, the
   measured finite gap from the existential population price, and a
   conditional theorem from the open inhabitation question OP30.
7. Apply every attack in `protocols/theorem.md` section G and the complete
   numerical checklist in `protocols/numerical.md`.

## Verdict rules

- **Verified:** the registered statement follows as written, with every
  imported hypothesis and quantifier explicit.
- **Hardened:** the mathematical core survives but the statement, assumptions,
  proof, dependency graph, or deployment language requires correction.
- **Refuted:** an exact counterexample or a nonrepairable logical failure
  defeats the registered statement. Minimize and serialize every such boundary
  and pin it in CI.

## Stop condition

Close only after the audit report, independent numerical and literature
artifacts, verdict-driven registry patches, generated indexes, manuscript
staleness updates, and all required validation commands are green. Move this
packet to `WORK/completed/` in the final audit commit.

## Outcome

- `DS-STABLE-MARGINS-PRICE`: **hardened**. PRICE/FUNNEL/FLOOR survive after
  the compact tilt--codebook uniform-law repair, pathwise all-labelings event,
  raw-label/centered-moment FLOOR convention, and explicit non-attainment
  boundary for the constrained values.
- `DS-PROFILED-COMPILE-CERTIFICATE`: **hardened**. The projected rule is the
  only currently established unconditional registry path; DS14 is a theorem
  for certified sequences, not a population guarantee from one finite
  diagnostic. OP30 remains open.
- `DS-STABLE-STATE-SELECTION`: **hardened** as measured evidence. The exact
  census range is 5--944, and the researcher 0.004--0.046 library gap is an
  aggregate summary rather than a per-run bound.

Permanent report:
`AUDITS/AUDIT-DS-STABLE-MARGINS-COMPILE-001.md`. Independent artifacts:
`AUDITS/artifacts/AUDIT-DS-STABLE-MARGINS-COMPILE-001/`.

## Validation

- `uv run python agenticresearch/py/registry.py reindex` — PASS
- `uv run python agenticresearch/py/registry.py validate` — PASS
- `JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_research_claims.py tests/test_research_registry.py` — 21 PASS
- `uv run ruff check .` — PASS
- `uv run ruff format --check .` — 217 files formatted
- `uv run ty check src` — PASS
- `uv build` — sdist and wheel built
- `uv run mkdocs build --strict` — PASS
