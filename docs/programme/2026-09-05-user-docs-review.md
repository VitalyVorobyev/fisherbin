# User-facing documentation review — 5 September 2026

Reviewed PR #52 at `fb00562` (`portal-reduction`), plus the current research queue.
This is a review record; execution stays in `docs/roadmap.md`.

## Verdict

The four-surface portal is a useful reduction. Michelson now introduces an instrument and an
observation model before the API, but the PR was not ready as scientific exposition: several
confident explanations exceeded or contradicted its equations. Green fact/snippet tests did not
catch them. This local revision corrects those claims and reduces entry-point repetition.

## Findings and disposition

| Priority | Finding at reviewed commit | Local disposition |
| --- | --- | --- |
| P1 | Michelson confuses arm-length difference with round-trip optical path, and gives no external sources for the opening. | Corrected displacement relation; linked NYCU optics handout and LIGO introduction. Explicitly an idealized model, not instrument data. |
| P1 | Periodic intensity is used to claim periodic optimal readout although the frequency score contains u. | Removed the inference. Disconnected intervals are an observed feature of the illustrated plain-D rule; Ds results are identified separately. |
| P1 | “No other partition” / “no rule to compile” turns lack of a general Ds geometry guarantee into universal impossibility. | Corrected homepage and Michelson; compilation depends on verified D conditions. |
| P1 | Zero retention implies all information is lost; a plain-D local solution is called optimal; finite-grid certification reads as a continuum claim. | Qualified the metric, local optimum and quadrature scope. |
| P2 | README carries a literature survey, FlowCyt result narrative, multiple introductions and overlapping examples. | Reduced from 2,154 to 511 whitespace-delimited words; one executing quickstart, task table, generated solver table and links. |
| P2 | Documentation index repeats README and points to a retired Lab. Root landing duplicates the old quickstart. | Index becomes a short map; landing mirrors the tested README example and links to the actual first workflow. |
| P2 | Research entry/playbook/packet repeat each other's rules; a parked Ds packet says active. | Shortened entries and packet, made the queue authoritative, corrected parked status. |

## Editorial remarks addressed in the same PR

- Ratios now opens with the synthetic mixture and the score written as a function of the
  likelihood ratio, then states the classifier result precisely: the density ratio is the
  posterior odds divided by the prior odds, under calibration with respect to the training
  mixture and known training proportions. `three-doors.md` and the portal home carry the same
  statement; the FlowCyt score section no longer says posteriors divided by priors "are" ratios.
- FlowCyt opens with this dataset's per-cell channels, expert labels and per-patient composition
  target. The gating narrative, "the number a cytometrist cares about" and "what a practitioner
  would reach for" are gone; the interpretation is scoped to this cohort. HEP opens as a
  simulation study on the public sample and says what it does not describe.
- Attribution stays (licence, copyright, DOI, source repository). The HEP provenance narration
  and upstream commit, the FlowCyt fixture cell counts, and the "every number is read from a
  committed evidence file" sentences move behind the reference links. A stale reference to the
  removed Lab is corrected on FlowCyt and Get started.
- Overlap: `motivation.md` is a short problem statement with pointers (the loss identity, the
  ratio kinds and the two-task argument now live only in `method.md`, `three-doors.md` and the
  book); the book introduction loses its audience and structure sections; the portal home
  defines the criteria without the solver inventory and points to the method overview and the
  workflow page. Routes are unchanged; `user-workflow.md` remains the decision guide and
  `method.md` the overview.
- Walkthrough cards state the problem, then the data, then the task, input, criterion and
  solver tags; a unit test enforces that order and that every card names its task. Solver tags
  stay until reader review says otherwise.

## What still needs editorial work

- Accept the corrected Michelson explanation with a fresh reader before applying its form to
  the remaining three articles. This review is not that human acceptance.

## Research decision

No new mathematics was recorded since the earlier review; subsequent research edits were
editorial/archive work. Keep the D results and Ds limitations. The next packet now asks one
question: conditional asymptotic uncertainty for scalar true retention of a frozen rule,
using an independent equal-weight sample. It specifies the plug-in ratio, shared denominator,
assumptions, one coverage experiment and stop outcome. This is a restricted
`OPEN-RETENTION-UNCERTAINTY` result, not closure of score perturbation or classifier calibration.
Check existing statistical theory before claiming novelty. Formal pilot PR #28 remains a separate
verification/integration task; no merge or new proof audit was performed here.

## Validation

After the remarks above were addressed, on the final tree:

- `JAX_ENABLE_X64=1 MPLBACKEND=Agg uv run pytest -n auto`: 566 passed. Float32 smoke: 4 passed.
  Ruff check/format, ty, strict MkDocs and sdist/wheel build passed; `git diff --check` clean.
- Node 24.20.0 / pnpm 11.0.9: typecheck, lint, 126 unit tests and the static build passed;
  e2e 28 passed / 2 existing mobile runtime skips; assembly verified 52 redirects and 31 links.

No numerical core, claim status, proof, dependency or public API changed. Human reader
acceptance and a fresh proof audit were not run.
