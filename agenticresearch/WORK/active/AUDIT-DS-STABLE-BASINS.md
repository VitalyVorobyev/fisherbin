# AUDIT-DS-STABLE-BASINS — adversarial audit of DS17

**Programme:** P1 · **Opened:** 31 August 2026 · **Status:** active
**Source:** `research-ds-stable-basins` at `ce8d59d` (merged as PR #27, `7e20983`)

## Goal

Independently verify, harden, refute, or reduce the DS17 complex:
`DS-STABLE-BASINS-CENTERED-OBSTRUCTION`,
`DS-STABLE-BASINS-LCM-CLASSIFICATION`,
`DS-STABLE-BASINS-FIXED-POINT-GATE`, and
`DS-STABLE-BASINS-GATE-SCANS`, together with the same PR's rewrite of
`DS-PROFILED-COMPILE-CERTIFICATE` clause (c) and its reroutes of
`OPEN-DS-STABLE-BASINS`, `OPEN-DS-MARGINS-NONCENTERED`, and
`OPEN-DS-PRACTICAL-CERTIFIED-SOLVER`. The auditor did not produce DS17 and
will not trust its proof instrument, its own protocol-G notes, or its
literature round.

DS17 is a **negative** result with a shipping consequence: it declares the
DS14 companion branch asymptotically vacuous on the whole conditionally
centered class and concludes that "`compile_quantizer`'s refusal needs no
certificate carve-out there". Three of the four nodes were born at
`project_proved`; the fourth is `measured`. `protocols/audit.md` therefore
applies in full, and the researcher's own packet requires this audit before
any `src/` change.

The deliverable is the 16-item publication-grade report
`AUDITS/AUDIT-DS-STABLE-BASINS-001.md`, together with the exact numerical,
literature, registry, counterexample, and manuscript consequences required by
`protocols/audit.md`.

## Independence contract

- Source frozen at `ce8d59d`. The audit session did not produce DS17 and has
  no access to the researcher's transcript.
- Do **not** import or extend `py/ds_stable_basins.py`, and do not reuse its
  strip-moment evaluator, branch tracker, root scanner, or geometry
  classifier. Build `py/audit_ds_stable_basins.py` independently: pure-stdlib
  `fractions.Fraction` where the claim is exact, an independent quadrature or
  closed-form path where it is not.
- Recheck the statements and imported hypotheses of DS11--DS16 without
  re-proving those audited claims; open a separate audit task if an imported
  result appears false.
- Audit scope is the DS17 complex. Two inherited structural weaknesses are to
  be **flagged as separate audit tasks, not chased here**: `project_proved`
  `DS-PROFILED-COMPILE-CERTIFICATE` depending directly on `measured`
  `DS-STABLE-STATE-SELECTION`, and the load-bearing `DS-SCHUR` /
  `FI-QUANT-IDENTITY` (status `literature`) and `FI-RANK-CEILING` (status
  `bridge`) nodes in the dependency closure.
- Run a fresh theorem-level prior-art pass.
  `LITERATURE/audits/DS-STABLE-BASINS-31-August-2026.md` is comparison
  material only and supplies no audit conclusion.
- Do not edit `src/`.

## Attack plan

1. **The population-to-empirical quantifier chain.** Theorem DS17.2 concludes
   that for all \(N\ge N_0(\omega)\) there is **no** margin-compatible stable
   labeling **at all** — strictly stronger than "no sequence". Check that
   Lemma DS17.0's single event \(\Omega_0\) really supports arbitrarily
   data-dependent, \(\omega\)-wise selections and the countable union over
   rational \((\kappa,c_0,\gamma)\), and that it consumes only the
   *audit-repaired* fixed-class uniform laws
   (`AUDITS/AUDIT-DS-POPULATION-BRIDGE-001.md` §8) rather than
   re-introducing a pointwise SLLN at a data-dependent limit — the exact
   defect the DS16 audit had to repair once already.
2. **DS14 Step 4 as the strip-structure import.** DS17.2 needs the limit
   \(q^*\) to be a genuine tilt-consistent strip rule. Verify Step 4 supplies
   the nearest-projected-centroid identification in that form (the proof
   insists on Step 4, "not bare DS12"), that the scalar-metric cancellation at
   \(d_\psi=1\) is legitimate, and that (M4) tie-nullity suffices to make the
   strips genuine.
3. **Lemma DS17.1a and the definition of tilt-consistency.** The identity
   \(B^*(I_q)-\beta=E[h(T_\beta)S_\lambda]/I_{\lambda\lambda}(q)\) requires
   \(I_{\lambda\lambda}(q)>0\), yet Theorem DS17.1's conclusion *is*
   \(I_{\lambda\lambda}(q)=0\). Pin down which definition each statement uses
   (\(B^*(I_q)=\beta\) versus \(E[hS_\lambda]=0\)), whether the registered
   claim statement is vacuous, imprecise, or correct as written, and whether
   the DS17.2 contradiction survives the correct reading.
4. **The conditional Chebyshev association step.** Verify at every sign of
   \(\delta=\beta-B^*\) including \(\delta=0\): existence of the regular
   conditional distribution and the conditional i.i.d. copy; integrability of
   the product; and the equality case — that a.s. constancy of
   \(h(\hat s-\delta S_\lambda)\) given \(\hat s\) really forces
   \(\hat s\)-measurable cell indicators, including when the \(t_b\) fail to
   be pairwise distinct or \(S_\lambda\) is conditionally degenerate.
5. **Scope of class (L).** Verify the corollary instances (jointly Gaussian,
   atomless elliptical, product, dependent `xcorr`) really lie in (L), and
   verify the (M4) proof for atomless elliptical laws — the
   \(O(\sqrt{t/r})\) angular-arc bound and the \(k_2t^{1/4}\) step. Then the
   deployment question: how wide is (L) among the models ScoreQuant actually
   targets (template/multicomponent fits, HEP, cytometry)? A theorem about a
   thin slice cannot license a general statement about what
   `compile_quantizer` may refuse. Separately confirm DS17's "conditional
   centering" is nowhere conflated with sample centering of scores — the
   library invariant is that the score-space origin has statistical meaning.
6. **DS17.3 and the DS16 hand-off.** Independently recompute the sign-split
   family on \(N(0,I_2)\): bounded-packet stationarity,
   \(I_q=\operatorname{diag}(2/\pi,\cdot)\), \(\lambda_{\min}\le1/\pi\) at
   \(v=0\), \(\Phi\equiv v_2=2/\pi\), \(v_3-v_2=0.1732\); and the reduction to
   \(K'\le K-1\) cells with \(\operatorname{rank}(I_{\rho'})\le1\). Then
   attack the inherited claim that this proves DS16's constraint class
   \(\{\lambda_{\min}(I_q)\ge\kappa\}\) **nonempty**: the DS16 audit
   explicitly separated \(v^{*+}(\kappa)\) from \(v^*(\kappa)\), and
   population quantizers from empirical labelings. Confirm the objects match
   before accepting the nonemptiness transfer, and confirm the caveat
   "\(\Phi(q)\le v_{K-1}\) proved only when \(B^*_q=B^*_{\text{pop}}\)" is not
   used anywhere it is unproved. Note the claim's own LCM-scoping of
   conclusion 2 against the bare-(L) scope of conclusion 1.
7. **The gate is necessary, not sufficient.** Corollary DS17.4 is a necessity
   gate and disclaims sufficiency. Check that nothing downstream leans on it
   as sufficient — the OP29(a) reroute, the "on mix3-like laws certification
   is free" deployment line, and the three `OPEN-*` patches.
8. **The scans.** Re-derive the compact tilt bound \(|\beta|\le2M/\kappa\) and
   check the scanned window \([-2.5,2.5]\) is justified by it rather than
   chosen. Attack branch enumeration: \(K=3\) interval rules have a
   two-parameter cut space, and a continuation tracking at most three branches
   can miss isolated stationary points — re-search independently (coarse
   two-dimensional cut grid, multistart, or exact rationals). Check that
   "rank one to \(2.4\times10^{-16}\)" is a genuine collapse and not a
   tolerance artifact. Reproduce the instrument's selftest against the public
   `IntegrationSource` tensor Gauss--Legendre path and the exact 8-atom
   rationals, and reproduce at least one `SEED_BASE = 20260831` library run.
   Per `protocols/numerical.md`, run exhaustive searches detached and report
   only the summary line plus the serialized artifact.
9. **The fixture.** Recompute `CE-DS-LCM-SIGNSPLIT-MARGIN-001` from its raw
   score and label arrays in `Fraction`; confirm it is minimized; confirm the
   pinned test would actually fail if the claim were false. Recheck the
   "(M5) is load-bearing" reading against `CE-DS-STABLE-MARGIN-RETAINING-001`
   and `CE-DS-POP-WASTED-CELLS-001`, and check the researcher's explanation of
   why the \(N\le14\) census witnesses do not contradict DS17.2.
10. **Registry adversarial pass on what this PR wrote.**
    - `implies`/`dependencies` asymmetry:
      `DS-STABLE-BASINS-CENTERED-OBSTRUCTION.implies` names
      `DS-PROFILED-COMPILE-CERTIFICATE`, but that node's `dependencies` does
      not name it back; likewise for `DS-STABLE-BASINS-LCM-CLASSIFICATION` and
      for `DS-STABLE-BASINS-GATE-SCANS -> DS-STABLE-BASINS-CENTERED-OBSTRUCTION`.
      `validate` does not enforce symmetry, so a `show --deps` walk
      **under-reports blast radius**: if DS17.1 falls, the compile certificate
      is affected invisibly.
    - `DS-STABLE-BASINS-GATE-SCANS` is `measured` yet `implies` a
      `project_proved` node, while `FIXED-POINT-GATE` depends on
      `CENTERED-OBSTRUCTION` and the scans depend on the gate. Check the
      logical order is genuinely acyclic and that no `measured` node carries
      theorem authority (`AGENT.md` invariant 6).
    - `claims/INDEX.md` has no `measured` or `open` status section, so
      `DS-STABLE-BASINS-GATE-SCANS`'s non-proved status is invisible there.
    - `registry.json` shows a large diff but only four semantic bibliography
      additions — the rest is whole-file reindentation, and its `updated`
      field stayed `2026-08-30`.
    - `WORK/artifacts/DS-STABLE-BASINS/` is a single `summary.json` behind all
      six `N-DS-BASINS-*` ledger rows; judge whether that is reproducible
      provenance under `protocols/numerical.md`.
    - Act on the erratum the researcher recorded but did not fix:
      `AUDITS/AUDIT-DS-STABLE-MARGINS-COMPILE-001.md` §15 cites the test name
      `test_ds16_interval_initializer_can_be_exchange_unstable`; the actual CI
      pin is `test_ds16_efficient_score_interval_seed_is_not_exchange_stable`.
11. **Literature.** Three DS17 nodes carry `search_gap` set by the researcher
    and `DS-STABLE-BASINS-GATE-SCANS` carries `not_searched`;
    `protocols/audit.md` makes that status an audit conclusion. Run an
    independent per-theorem triangulation (3--5 nearest sources, six fields
    each) with the re-attribution risks named explicitly: the tilt-residual
    identity versus classical efficient-score / least-favourable-direction
    orthogonality in semiparametric theory; the association step versus
    Chebyshev and FKG arguments in quantization; self-consistency and
    principal points (Flury 1990; Tarpey--Flury 1996; Tarpey--Li--Flury 1995;
    Serinko--Babu 1992 — only the last was deeply reviewed by the researcher).
    Verify those four registered sources are neither over- nor
    under-attributed.
12. **Protocol sweeps.** Apply every attack in `protocols/theorem.md` §G and
    the complete `protocols/numerical.md` checklist independently, rather than
    reading them off the researcher's own §G notes in
    `KNOWN_RESULTS/05b-ds-bridge.md`.

## Verdict rules

- **Verified:** the registered statement follows as written, with every
  imported hypothesis and quantifier explicit.
- **Hardened:** the mathematical core survives but the statement, assumptions,
  proof, dependency graph, or deployment language requires correction.
- **Refuted:** an exact counterexample or a nonrepairable logical failure
  defeats the registered statement. Minimize and serialize every such boundary
  and pin it in CI.
- **Reduced:** the result stands only under explicitly listed unresolved
  assumptions, each named individually.

A verdict is delivered per claim, not for the complex as a whole.

## Required deliverables

- `AUDITS/AUDIT-DS-STABLE-BASINS-001.md` — the 16-item report, sections
  numbered and in protocol order, front matter carrying `**Claims:**`,
  `**Audit:**`, `**Date:**`, `**Source frozen:**`, `**Result:**`.
  `AUDITS/AUDIT-D-EXCHANGE-VORONOI-001.md` is the size/rigor exemplar;
  `AUDITS/AUDIT-DS-STABLE-MARGINS-COMPILE-001.md` is the nearest precedent.
- Independent instrument `py/audit_ds_stable_basins.py` plus run records under
  `AUDITS/artifacts/AUDIT-DS-STABLE-BASINS-001/`, each carrying
  `git_revision`, `script_sha256`, `python`, `platform`, and the seed formula.
- Verdict-driven patches to the four DS17 claim nodes: an `audit` pointer
  (a workspace-relative path the validator can stat), hardened `assumptions`,
  `boundary_counterexamples`, audit-owned `literature_search_status`, a
  rewritten `warning`, and repaired `dependencies`/`implies` edges.
- A new node `claims/AUDIT-DS-STABLE-BASINS.json` whose
  `proof_location.file` is the report and whose `proof_location.section` is
  the report's `#` title verbatim (`validate` checks the section string occurs
  in the file), with `artifact` pointing at the audit script and
  `dependencies` including the audited claims.
- Any boundary failure minimized into `COUNTEREXAMPLES/<ID>.json` in the
  format required by `COUNTEREXAMPLES/README.md`, a catalogue entry, and a
  deterministic pin in `tests/test_research_claims.py` that recomputes the
  pathology from the raw arrays in `Fraction`.
- `LITERATURE/audits/AUDIT-DS-STABLE-BASINS-31-August-2026.md` with a query
  log, the six-field triangulation, and a search verdict; per-round counts in
  `LITERATURE/graph.json`; `reviewed.md`/`rejected.md` updates; a `**Key:**`
  line under the annotating heading for every new bibliography key.
- `NUMERICAL_EVIDENCE.md` rows for the independent recomputation, citing at
  least one claim id and one executable source.
- `KNOWN_RESULTS/05b-ds-bridge.md` §DS17 edits for anything hardened, and a
  `manuscripts/README.md` staleness entry for any statement the manuscripts
  now contradict — a re-attribution to prior art especially.
- A new research packet for OP29 branch (a), named after
  `OPEN-DS-MARGINS-NONCENTERED`, opened in the active packet directory from
  `WORK/TEMPLATE.md` and carrying the DS17.4 gate identity as its population
  test.
- Never hand-edit a generated index. Run `reindex`, then `validate`.
- No `src/` change in this packet.

## Stop condition

Close only after the audit report, the independent numerical and literature
artifacts, the verdict-driven registry patches, the regenerated indexes, the
manuscript staleness updates, the next research packet, and all required
validation commands are green:

```
uv run python agenticresearch/py/registry.py reindex
uv run python agenticresearch/py/registry.py validate
JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest tests/test_research_claims.py tests/test_research_registry.py
uv run ruff check . && uv run ruff format --check . && uv run ty check src
```

Move this packet to `WORK/completed/` in the final audit commit, with
`## Outcome`, `## Artifacts`, and `## Validation` sections, and close the
session with a plain-English report for a non-mathematician: what was done,
what survives, whether it matters, and the logical next step.

## Next dependency-blocking question

If DS17 is verified or hardened: for non-centered laws, does the
`DS-STABLE-BASINS-FIXED-POINT-GATE` root equation admit nondegenerate
solutions on a stated class, and does the empirical transfer hold from a
nondegenerate root's basin to exact one-point exchange stability against
\(O(1/N)\)-scale boundary noise (`OPEN-DS-MARGINS-NONCENTERED`, OP29(a))?
If DS17 is refuted or reduced: what remains of OP30(a), and does
`DS-PROFILED-COMPILE-CERTIFICATE` clause (c) revert to its pre-DS17 wording?
