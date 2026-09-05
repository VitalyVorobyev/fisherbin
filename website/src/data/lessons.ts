import {factsFor} from "../lib/facts";

/**
 * The lesson index: one entry per dataset and statistical task the portal
 * teaches, stated as the same compact contract every lesson opens with.
 *
 * This is the map from a reader's situation to a page. The wording here is
 * deliberately the contract vocabulary (observation, parameters of interest,
 * nuisance, reference point, source measure, score provenance, admissible
 * labels, task and output, criterion, evaluation), so a reader chooses a
 * lesson by the shape of their own problem rather than by domain. Bin budgets
 * come from the walkthrough facts, never from a literal typed here.
 *
 * `status` says how far each page has been brought to the seven-step lesson
 * pattern (problem, model and score, binning decision, run, evaluate, explore,
 * interpret). `browser` says what, if anything, that page computes in the
 * reader's browser today; the runtime is loaded only by that page's own
 * experiment, never by this index.
 */

export type LessonStatus = "complete" | "pending";

export interface LessonContract {
  /** What one row of the data is. */
  observation: string;
  /** The parameter(s) the measurement is for. */
  interest: string;
  /** Parameters that float alongside, or "none". */
  nuisance: string;
  /** The model point the scores are taken at. */
  referencePoint: string;
  /** The measure the labels are optimized against. */
  sourceMeasure: string;
  /** Exact-model score or an estimate, and through which provider. */
  provenance: string;
  /** Which assignments the task is allowed to choose among. */
  admissibleLabels: string;
  /** The public task and what it returns. */
  taskOutput: string;
  /** The criterion the labels optimize. */
  criterion: string;
  /** The bin budget the page's headline uses, from the walkthrough facts. */
  budget: string;
  /** How the result is judged and against what. */
  evaluation: string;
}

export interface Lesson {
  slug: string;
  title: string;
  /** The one plain-language question the page answers. */
  question: string;
  /** Route within the portal. */
  href: string;
  contract: LessonContract;
  /** What this page computes in the reader's browser, as of this build. */
  browser: string;
  status: LessonStatus;
}

const michelson = factsFor("michelson");
const ratios = factsFor("ratios");
const flowcyt = factsFor("flowcyt");
const hep = factsFor("hep");

export const LESSONS: readonly Lesson[] = [
  {
    slug: "michelson",
    title: "Detector segments for an interferometer phase",
    question: "Given K counters and a fringe frequency that floats in the fit, which aperture positions should each counter collect from?",
    href: "/walkthroughs/michelson",
    contract: {
      observation: `The fringe phase of each photon along the aperture, over ${michelson("fringes")} whole fringes.`,
      interest: "The fringe phase.",
      nuisance: "A fractional fringe-frequency error, profiled out rather than fixed.",
      referencePoint: "The nominal fringe law: zero phase offset and zero frequency error.",
      sourceMeasure: `The fringe intensity law on the aperture, tabulated on ${michelson("nNodes")} deterministic quadrature nodes for the fixed-table task and integrated by bounded quadrature for the reusable rule.`,
      provenance: "Exact: the analytic score of the fringe law, declared through ScoreFunction as an exact-model score at the reference point.",
      admissibleLabels: "Any assignment of aperture positions to K counters, including disjoint unions of intervals (a periodic mask, modulo addressing). Contiguous-only segmentation is a separate, harder-constrained problem the page does not solve; equal segments are its naive member.",
      taskOutput: "optimize_partition: a label per quadrature node, which is the readout map on the aperture. fit_quantizer: a rule for any position, for the plain-D criterion only.",
      criterion: "Profiled D-optimality for the phase after the fringe frequency is profiled; plain D-optimality shown as the contrast.",
      budget: michelson("bins"),
      evaluation: "Phase information retained after profiling, against the unbinned profiled ceiling. Deterministic quadrature, so there is no sampling split for the fixed-table task; the compiled plain-D rule is scored on a separate held-out sample."
    },
    browser: "Nothing yet. The lesson's experiment, a K control with a browser refit of the committed partition, arrives with the page's rewrite.",
    status: "pending"
  },
  {
    slug: "ratios",
    title: "A classifier instead of a likelihood",
    question: "When the only model you have is a trained classifier, is the retention number the library reports about your data or about your classifier?",
    href: "/walkthroughs/ratios",
    contract: {
      observation: "One scalar per event from a two-component mixture.",
      interest: "The signal fraction of the mixture.",
      nuisance: "None: the two fractions sum to one.",
      referencePoint: `A signal fraction of ${ratios("signalFraction")}, the mixture the density ratios are taken at.`,
      sourceMeasure: `An unlabelled sample from the reference mixture: ${ratios("nTrain")} events to fit and ${ratios("nTest")} held out to evaluate.`,
      provenance: "Estimated: a classifier's calibrated output converted to a density ratio and then to a score through DensityRatioScore. The exact Bayes score is also known, so the estimate can be checked.",
      admissibleLabels: "Any grouping of score values.",
      taskOutput: "fit_quantizer: a reusable rule on the score, frozen after fitting and applied to the held-out events.",
      criterion: "D-optimality.",
      budget: ratios("bins"),
      evaluation: "Held-out labels scored two ways: the retention the estimated score reports about itself, and the retention of the true score under the same labels."
    },
    browser: "The page refits a fresh D-optimal partition on its held-out table on request, labelled as a different computation from the frozen rule it reports.",
    status: "pending"
  },
  {
    slug: "flowcyt",
    title: "Bone-marrow cell populations",
    question: "If a patient must be summarised by a few integer counts, which categories should those counts be, and what do they cost the composition estimate?",
    href: "/walkthroughs/flowcyt",
    contract: {
      observation: "Marker intensities per cell, reduced by a classifier to a five-column score.",
      interest: "A patient's population fractions; five are independent, one population being the reference component.",
      nuisance: "None in the criterion.",
      referencePoint: "The reference cohort's composition, at which the mixture score is defined.",
      sourceMeasure: `Cells from the reference patients (${flowcyt("studyCells")} in the full study); a held-out group of patients is frozen before anything is fitted.`,
      provenance: "Estimated: density ratios from a classifier trained on expert-labelled cells; the reported retention is a surrogate, not exact Fisher information.",
      admissibleLabels: "Any grouping of score values; the categories are applied to cells of unseen patients.",
      taskOutput: "fit_quantizer: K categories that generalise to new patients. The same rows also serve optimize_partition, which stops at an assignment of exactly these cells.",
      criterion: "D-optimality.",
      budget: flowcyt("bins"),
      evaluation: "Held-out patients: surrogate D-efficiency beside the downstream composition error, which is the quantity the report is written around."
    },
    browser: "Nothing yet. The page's experiment, a held-out patient selector, arrives with its lesson rewrite.",
    status: "pending"
  },
  {
    slug: "hep",
    title: "A Higgs search with a floating energy scale",
    question: "Given that only a handful of counts will be published and the tau energy scale will float in the fit, which handful?",
    href: "/walkthroughs/hep",
    contract: {
      observation: `Simulated collision events (${hep("nEvents")} in the fixture), each carried at its Monte Carlo weight, read as one sensitivity per parameter.`,
      interest: "The signal strength of the Higgs-to-tau-tau process.",
      nuisance: "The combined background rate (a normalisation) and the tau energy scale (a shape).",
      referencePoint: "Unit signal strength, unit background rate and the nominal energy scale.",
      sourceMeasure: "The weighted simulated events themselves; the fit is on a fixed table.",
      provenance: "Estimated: a signal classifier's density ratio for the rate columns and a central-difference log ratio between energy-scale variants for the shape column, through DensityRatioScore and CentralLogRatioScore.",
      admissibleLabels: "Any grouping of events by score.",
      taskOutput: "optimize_partition: a category for each simulated event in the table.",
      criterion: "Profiled D-optimality for the signal strength with both nuisances profiled; plain D-optimality and classifier-output slices as baselines.",
      budget: hep("bins"),
      evaluation: "Profiled signal-strength information retained on the same weighted table, beside the same quantity for equal-frequency, logit and threshold slices of the classifier output."
    },
    browser: "Nothing yet. The page's experiment, a frozen-versus-profiled nuisance toggle, arrives with its lesson rewrite.",
    status: "pending"
  }
];

/** The reading order every lesson follows. */
export const LESSON_STEPS: readonly {title: string; detail: string}[] = [
  {title: "Problem", detail: "Two or three sentences and the contract above."},
  {title: "Model and score", detail: "Equations with the reference point visible."},
  {title: "Binning decision", detail: "What may be grouped together and which criterion is optimized."},
  {title: "Run", detail: "Executable inputs, the fit and its output."},
  {title: "Evaluate", detail: "Held-out labels, a matching baseline and the kind of information reported."},
  {title: "Explore", detail: "One control that changes one scientific question, with a reset and a static fallback."},
  {title: "Interpret", detail: "Where the result applies, the failure or refusal case and the theory it rests on."}
];

/**
 * One row of the task × criterion × solver matrix the browser runtime admits.
 *
 * `runnable` is checked by a test against the protocol's own validator, so
 * this table cannot drift from what the worker would actually accept.
 */
export interface BrowserCapability {
  task: "optimize_partition" | "fit_quantizer";
  criterion: "d_optimality" | "profiled_d_optimality" | "normalized_trace";
  solver: "d_exchange" | "mahalanobis_lloyd" | "kmeans" | "soft_voronoi";
  runnable: boolean;
  note: string;
}

export const BROWSER_MATRIX: readonly BrowserCapability[] = [
  {task: "optimize_partition", criterion: "d_optimality", solver: "d_exchange", runnable: true, note: "Exact finite relocation; the same path the committed fixtures were made with."},
  {task: "optimize_partition", criterion: "d_optimality", solver: "mahalanobis_lloyd", runnable: true, note: "Guarded Lloyd steps in the retained-information metric."},
  {task: "optimize_partition", criterion: "profiled_d_optimality", solver: "d_exchange", runnable: true, note: "Exact profiled exchange, optionally started from the efficient-score bound."},
  {task: "optimize_partition", criterion: "profiled_d_optimality", solver: "soft_voronoi", runnable: false, note: "The finite profiled task has no soft path; the soft family is a reusable-rule solver."},
  {task: "optimize_partition", criterion: "normalized_trace", solver: "kmeans", runnable: false, note: "Normalized trace is a fit_quantizer objective."},
  {task: "fit_quantizer", criterion: "d_optimality", solver: "d_exchange", runnable: true, note: "Exchange on the sample, then the verified compile into a Mahalanobis rule."},
  {task: "fit_quantizer", criterion: "d_optimality", solver: "mahalanobis_lloyd", runnable: true, note: "Lloyd in the retained-information metric, then the same compile step."},
  {task: "fit_quantizer", criterion: "normalized_trace", solver: "kmeans", runnable: true, note: "Whitened k-means; the only solver this objective pairs with."},
  {task: "fit_quantizer", criterion: "profiled_d_optimality", solver: "soft_voronoi", runnable: true, note: "A profiled rule fitted directly in the soft family and hardened afterwards."},
  {task: "fit_quantizer", criterion: "profiled_d_optimality", solver: "d_exchange", runnable: false, note: "An exchange-stable profiled partition has no canonical reusable rule; the library refuses to compile one."}
];
