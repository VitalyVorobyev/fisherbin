import {factsFor} from "../lib/facts";

/**
 * The walkthrough index: one card per applied problem.
 *
 * A card says what problem the page solves, on what data, and which parts of
 * the library it uses, as tags a reader can match against their own
 * situation. Bin budgets come from the walkthrough facts, never from a
 * literal typed here.
 */

export type TagKind = "task" | "input" | "criterion" | "solver" | "data";

export interface WalkthroughTag {
  kind: TagKind;
  label: string;
}

export interface WalkthroughCard {
  slug: string;
  title: string;
  /** Route within the portal. */
  href: string;
  /** One paragraph: the problem, the data, what the page shows. */
  summary: string;
  tags: readonly WalkthroughTag[];
}

export const TAG_KIND_LABELS: Record<TagKind, string> = {
  task: "Task",
  input: "Input",
  criterion: "Criterion",
  solver: "Solver",
  data: "Data"
};

const michelson = factsFor("michelson");
const ratios = factsFor("ratios");
const flowcyt = factsFor("flowcyt");
const hep = factsFor("hep");

export const WALKTHROUGHS: readonly WalkthroughCard[] = [
  {
    slug: "michelson",
    title: "A Michelson interferometer read out through K counters",
    href: "/walkthroughs/michelson",
    summary:
      `A fringe pattern is measured by ${michelson("bins")} counters, and the fringe frequency ` +
      "floats in the fit beside the phase. The model is exact, so the score has a closed form " +
      "and the library's numbers check the mathematics. The page finds which aperture " +
      "positions each counter should collect from, shows why equal segments can lose the phase " +
      "entirely, and refits the committed partition in your browser at any counter budget.",
    tags: [
      {kind: "task", label: "optimize_partition"},
      {kind: "task", label: "fit_quantizer"},
      {kind: "input", label: "ScoreFunction"},
      {kind: "input", label: "IntegrationSource"},
      {kind: "criterion", label: "ProfiledDOptimality"},
      {kind: "criterion", label: "DOptimality"},
      {kind: "solver", label: "DExchangeConfig"},
      {kind: "solver", label: "SoftVoronoiConfig"},
      {kind: "data", label: "analytic model, deterministic quadrature"}
    ]
  },
  {
    slug: "ratios",
    title: "A classifier instead of a likelihood",
    href: "/walkthroughs/ratios",
    summary:
      "The model is a trained classifier, not a density. Its calibrated output becomes a " +
      "density ratio, the ratio becomes a score, and the library reports how much of the " +
      `measurement ${ratios("bins")} bins keep. The mixture is generated on purpose so the exact ` +
      "score is also known, and the page checks whether the reported number is about the data " +
      "or about the classifier.",
    tags: [
      {kind: "task", label: "fit_quantizer"},
      {kind: "input", label: "DensityRatioScore"},
      {kind: "criterion", label: "DOptimality"},
      {kind: "solver", label: "DExchangeConfig"},
      {kind: "data", label: "synthetic mixture with a known truth score"}
    ]
  },
  {
    slug: "hep",
    title: "A Higgs search with a floating energy scale",
    href: "/walkthroughs/hep",
    summary:
      "Simulated collision events, a signal strength to measure, and a tau energy scale that " +
      `floats in the fit as a nuisance. Only ${hep("bins")} counts will be published. The page ` +
      "chooses them for the profiled information about the signal strength and compares that " +
      "against the usual slices of the classifier output on the same weighted events.",
    tags: [
      {kind: "task", label: "optimize_partition"},
      {kind: "input", label: "DensityRatioScore"},
      {kind: "input", label: "CentralLogRatioScore"},
      {kind: "criterion", label: "ProfiledDOptimality"},
      {kind: "solver", label: "DExchangeConfig"},
      {kind: "data", label: "simulated events, FAIR Universe HiggsML"}
    ]
  },
  {
    slug: "flowcyt",
    title: "Bone-marrow cell populations",
    href: "/walkthroughs/flowcyt",
    summary:
      "Each cell carries marker intensities; the report is a few population fractions per " +
      `patient. The page fits ${flowcyt("bins")} categories on reference patients from ` +
      "classifier-estimated scores, applies them to held-out patients, and measures the " +
      "composition error the reduction costs. The result is negative in an instructive way.",
    tags: [
      {kind: "task", label: "fit_quantizer"},
      {kind: "input", label: "DensityRatioScore"},
      {kind: "criterion", label: "DOptimality"},
      {kind: "solver", label: "DExchangeConfig"},
      {kind: "data", label: "real cells, FlowCyt benchmark, held-out patients"}
    ]
  }
];
