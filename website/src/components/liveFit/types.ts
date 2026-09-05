/**
 * Types shared by `LiveFit` (always in the route chunk) and `LiveFitRunner`
 * (reached only through a dynamic import, see `LiveFitRunner.tsx`).
 *
 * Deliberately self-contained rather than importing from `website/src/lab/`:
 * `LiveFit` must never import anything that transitively reaches the browser
 * runtime, and duplicating this small shape is cheaper than auditing every
 * transitive import of `../../lab/protocol` for that property forever.
 * `LiveFitRunner` narrows these into the real `LabProblem` shape at the one
 * point it is allowed to know about the wire protocol.
 */

/** One score row. Six columns is the browser Lab's own ceiling. */
export type LiveFitScoreRow = number[];

/**
 * Which public task a placement runs. Absent means `fit_quantizer`, matching
 * the wire protocol's own default.
 */
export type LiveFitTask = "fit_quantizer" | "optimize_partition";

/**
 * The solvers current placements ask for: exact D-exchange (every current
 * `fit_quantizer` and `optimize_partition` placement) and the guarded
 * Mahalanobis-Lloyd solver, `optimize_partition`'s other admitted solver.
 */
export type LiveFitSolver = "d_exchange" | "mahalanobis_lloyd";

/**
 * Seed the exchange from `efficient_score_bound(...).labels` instead of the
 * solver's own k-means++ initializer. Only meaningful with `task:
 * "optimize_partition"` and a profiled criterion.
 */
export type LiveFitInitialization = "efficient_score_bound";

/** The objective a placement optimizes, and its parameters of interest. */
export interface LiveFitCriterion {
  name: "d_optimality" | "profiled_d_optimality" | "normalized_trace";
  interest?: string[];
}

/** Ask the adapter to also report the profiled retention of the result. */
export interface LiveFitReport {
  profiledInterest: string[];
}

/** A bounded problem a `LiveFit` demo can hand to the browser runtime. */
export interface LiveFitProblem {
  criterion?: LiveFitCriterion;
  datasetId?: string;
  initialization?: LiveFitInitialization;
  nBins: number;
  report?: LiveFitReport;
  schema?: string[];
  scores: LiveFitScoreRow[];
  seed: number;
  solver: LiveFitSolver;
  task?: LiveFitTask;
  weights: number[];
}

/**
 * The shape of one placement's result, narrowed from the wire protocol's own
 * `LabResult` to the fields a placement renders.
 */
export interface LiveFitResult {
  labels: number[];
  retention: number;
  profiledRetention?: number;
  exchangeStable?: boolean;
}

/**
 * Resolve the problem to run, lazily.
 *
 * A synchronous placement (the committed fixture is already in memory)
 * returns a resolved promise; an asynchronous one (the score table is a
 * static asset fetched only on demand, e.g. `/get-started`) fetches it here,
 * on activation, rather than before the reader ever asks for it.
 */
export type LiveFitProblemLoader = () => Promise<LiveFitProblem>;

/** Props `LiveFit` hands to the dynamically imported `LiveFitRunner`. */
export interface LiveFitRunnerProps {
  /** Human label for what the committed number measures. */
  committedLabel: string;
  /** The number already published on the page. */
  committedRetention: number;
  /** How to render a retention value as text, matching the page's own convention. */
  formatRetention: (value: number) => string;
  /**
   * Which number to show as "your browser's run", read from the result.
   * Defaults to `result.retention`; a placement that asks for
   * `report.profiledInterest` passes this to show `profiledRetention`
   * instead, since that is the number the committed value beside it measures.
   */
  liveValue?: (result: LiveFitResult) => number;
  /** Human label for what the reader's own run measures. */
  liveLabel: string;
  /** Called once the reader is done: resets `LiveFit` back to its idle view. */
  onRelease: () => void;
  /** Resolve the problem to actually run, once activated. */
  problem: LiveFitProblemLoader;
  /** Render extra content below the two result cards, once a result exists. */
  renderResult?: (result: LiveFitResult) => React.ReactNode;
}
