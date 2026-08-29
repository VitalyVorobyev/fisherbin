# DS-MARGINS-AT-OPTIMA — are the DS14 margins automatic at finite \(D_s\) optima?

**Programme:** P1 (OPEN_PROBLEMS.md OP28, retired) · **Opened:** 28 Aug 2026 · **Status:** completed 29 Aug 2026
**Target claim:** `OPEN-DS-MARGINS-AT-OPTIMA`
**Descends from:** `WORK/completed/DS-POPULATION-BRIDGE.md` and
`WORK/completed/AUDIT-DS-POPULATION-BRIDGE.md`, which independently named this
as their next dependency-blocking question.

## Goal

Decide whether global (or exchange-stable) finite \(D_s\) optima under
light-tailed atomless laws asymptotically satisfy the three DS14 margins —
cell mass (M2), conditioning (M3), projected-centroid separation (M5) — almost
surely along the sequence. "Done" is decidable: a proof for a stated law class,
a counterexample law under which a margin fails infinitely often, or a
reduction to an explicitly stated conjecture node.

## Outcome

**Both decidable stop conditions were hit at once, by the same theorem.** DS15
(`KNOWN_RESULTS/05b-ds-bridge.md`, claim `OPEN-DS-MARGINS-AT-OPTIMA`, now
`project_proved`) proves, for \(d_\psi=1\) and conditionally centered laws
(\(E[S_\lambda\mid\hat s]=0\): Gaussian, elliptical) with a unique scalar
efficient-score quantizer and swap-rich nuisance conditionals, that along
exact global finite \(D_s\) optima, almost surely:

- **(M2) is proved** (stop condition "proved for a stated law class"): min
  cell mass converges to the positive population masses of the optimal
  efficient-score interval quantizer \(J^*\); singletons die out. The
  \(N\le18\) singleton evidence was pre-asymptotic, and the old 1/8-grid
  suite was additionally atomic-law evidence, as the audit had warned.
- **(M3) is refuted** (stop condition "refuted by a law under which a margin
  fails infinitely often" — it fails *eventually* for **every** law in the
  class): the optimum's value converges to the unrestricted population
  supremum \(v_K\), attained only by \(J^*\), which carries exactly zero
  binned nuisance information; hence \(\hat I_{\lambda\lambda},
  \hat I_{\psi\lambda}\to0\) and \(\lambda_{\min}(\hat I_N)\to0\).
- **(M5) is reframed**: at optima the projected-centroid object rides on a
  \(0/0\) regression slope; the meaningful reduced geometry is the scalar
  \(J^*\) geometry with distinct centroids. The exact-tie mechanism
  (`CE-DS-DEGENERATE-GLOBAL-TIE-001`) stays the finite-\(N\) witness.
- **OP28's remaining sub-questions**: \(v^*(\kappa)<v_K\) strictly for every
  \(\kappa>0\) (the margin-compatible optimum is strictly suboptimal; the
  unrestricted supremum *is* attained, only degenerately — the C2 attainment
  answer for this class), and DS11(a) domination becomes an equality at
  optima (the gap is the projection tax, which vanishes).
- **Deployability** (the point of the packet): on this class the compile
  target for profiled criteria is the **projected efficient-score interval
  rule** — estimate \(\hat B^*_N\) from the full sample, bin \(\hat s\) with
  the exact scalar DP, certify the 1-D margins and slope stability — not a
  DS14 (M3) certificate, which provably cannot hold at free optima. A
  margin-certified in-bin quantizer remains legitimate at a quantified price
  \(\delta(\kappa)=v_K-v^*(\kappa)>0\) of profiled information. This is the
  answer to the CMS-SANNT-shaped question the packet opened with: the
  ambiguous in-bin binning resolves into a deterministic scalar rule on the
  profiled efficient score.
- **The complement is reduced to an explicit open node** (third stop
  condition): non-centered laws, \(d_\psi>1\), and exchange-stable non-global
  sequences are `OPEN-DS-MARGINS-NONCENTERED` (OP29), with the measured
  contrast (Gaussian nuisance blocks collapse; mix3/tiny_cluster blocks stay
  macroscopic) already recorded.

Falsification discipline: the finite half of DS15 (the exact sandwich
\(\hat\Phi_s(z)\le\mathrm{btw}(\hat s_N;z)\le\hat v_K\) and the
projection-tax identity) was verified in exact rational arithmetic on every
instance of the new fine-grid suite before the proof was written, the float
screen was anchored against fully exact enumeration, and two failed
achievability constructions (tilt-IVT, greedy cancellation) are recorded in
the proof notes precisely because the numerics refused to let the tax vanish
at plain interval labelings — the steering construction is what survived.

## Artifacts

- `KNOWN_RESULTS/05b-ds-bridge.md` — new section DS15 (statement, proof,
  interpretation, deployability); DS14's "not claimed" paragraph updated.
- `claims/OPEN-DS-MARGINS-AT-OPTIMA.json` — `open` → `project_proved`
  (the dichotomy theorem); `claims/OPEN-DS-MARGINS-NONCENTERED.json` — new
  open node (OP29); `claims/OPEN-DS-FINITE-POP-BRIDGE.json` — warning and
  margin assumption updated; `claims/OPEN-DS-DOMINATION-EQUALITY.json` —
  equality-at-optima resolved for the class.
- `OPEN_PROBLEMS.md` — OP28 retired into the P1 status line; OP29 added.
- `py/ds_margins_at_optima.py` — fine-grid margins trend (atomless-emulating
  1/2^16 grid; exact sandwich, M3/M5 metrics, partition distance), scalar
  min-mass trend, population reference, exact-enumeration anchor.
- `NUMERICAL_EVIDENCE.md` — rows N-DS-MARGINS-TREND, N-DS-SCALAR-MASS,
  N-DS-MARGINS-EXACT-ANCHOR.
- `tests/test_research_claims.py::test_ds15_profiled_value_is_bounded_by_the_efficient_score_interval_optimum`
  — deterministic exact pin of the sandwich and tax identity (966 labelings).
- `LITERATURE/` — audit `audits/OPEN-DS-MARGINS-AT-OPTIMA-29-August-2026.md`
  (five confirmed gaps; two-camps frame); nine bibliography keys; new
  sections in `topics/01` and `topics/04`.
- `manuscripts/README.md` — staleness items (DS15 absent; new prior-art
  constellation).

## Next dependency-blocking question

`OPEN-DS-MARGINS-NONCENTERED` (OP29), and within it the deployment-facing
half first: **do exchange-stable non-global \(D_s\) solutions — what the
library's optimizer actually returns — retain the DS14 margins, and at what
measured information cost relative to \(v_K\)?** A positive answer gives
`compile_quantizer` a certified two-track story on conditionally centered
laws (projected efficient-score rule at the optimum; margin-certified in-bin
rule near it, with a stated \(\delta(\kappa)\) price); a negative one makes
the projected rule the only theorem-backed compile path. The mathematical
half (non-centered laws, \(d_\psi>1\)) feeds P6/C2 and can proceed
independently.
