# ADR 0029: Lessons replace the free-form browser Lab

**Status:** Accepted

**Extends:** ADR 0028 (teaching pages open with a contract and load computation only through an
explicit action). **Supersedes in part:** ADR 0019 (the locked marimo lesson embed and the
console-style Lab route).

## Context

The portal shipped `/portal/lab/` as a solver console: a runner picker, a solver picker, a
criterion picker, a bin slider, three interchangeable score tables including a file upload, a
two-dimensional projection of whatever table was loaded, and a hidden marimo notebook behind a
button. On 5 September 2026 the owner reviewed the published page and found it illustrated
nothing: the picture showed points and cell means for a multidimensional score without saying
what the scores were, which model produced them at which reference point, which of the two
public tasks was being run, or how any control mapped to the library's API and to the theory
that justifies it. A reader could change every control and learn nothing about their own
problem.

The existing `?job=<walkthrough>` hand-offs made this worse rather than better. The Michelson
preset could not validate at all (its table has 8,000 rows against a 5,000-row ceiling) and,
where it could have run, it would have fitted a soft profiled rule with `fit_quantizer` while
the page it came from fits an exact profiled partition with `optimize_partition`.

## Decision

Computation in the portal is reached only through a lesson's experiment. A lesson is one
dataset and one statistical task, taught in the fixed order of ADR 0028's pattern: problem and
contract, model and score, binning decision, run, evaluate, explore, interpret. The experiment
is the "explore" step: one control that changes one scientific question, with a reset and a
static fallback, and a browser run that reproduces a committed number on the same table with
the same task, criterion, solver and seed.

`/portal/lab/` keeps its URL (ADR 0027) and becomes the lesson index. It states each lesson's
contract in the shared vocabulary (observation, parameters of interest, nuisance, reference
point, source measure, score provenance, admissible labels, task and output, criterion, bin
budget, evaluation), says what each page computes in the browser today, and shows the task,
criterion and solver pairs the browser runtime admits, checked by a test against the protocol's
own validator. It loads no runtime.

The free-form console is removed rather than demoted: no runner, solver or criterion pickers
over an unexplained table, no file upload, no notebook embed. The marimo export leaves the
build. The browser protocol (version 3) names the task explicitly, admits
`optimize_partition` beside `fit_quantizer`, can seed a profiled exchange from the
efficient-score bound and can report the profiled retention of any result, so that a lesson's
browser run is the page's own computation and not a neighbouring one.

## Consequences

- The Pyodide runtime, the worker protocol and the one-demo-at-a-time `LiveFit` machinery stay;
  they are now used only from lesson pages.
- A walkthrough that has not yet been brought to the pattern appears on the index as a
  walkthrough with the pattern pending, and says that it computes nothing in the browser. It is
  not decorated with a console link to compensate.
- Bringing your own score table to the browser is not a feature. The README and the reference
  show the one-line install; a reader with a table runs the library.
- Browser-side coverage of five-dimensional profiled runs rests on the Python adapter test until
  a lesson with such a run exists.
- The M13-E formal-pilot ADR takes number 0030.

## Alternatives considered

Keeping the console under an "advanced" link keeps the thing the owner rejected, one click
further away. Replacing the picture with a better picture keeps a page whose first question is
"which solver" rather than "which problem".
