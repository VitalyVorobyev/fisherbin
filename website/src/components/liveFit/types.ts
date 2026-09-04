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
 * The one solver every current placement asks for: exact D-exchange, the
 * same solver `optimize_partition`'s D-optimal path always uses.
 */
export type LiveFitSolver = "d_exchange";

/** A bounded problem a `LiveFit` demo can hand to the browser runtime. */
export interface LiveFitProblem {
  datasetId?: string;
  nBins: number;
  schema?: string[];
  scores: LiveFitScoreRow[];
  seed: number;
  solver: LiveFitSolver;
  weights: number[];
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
  /** Human label for what the reader's own run measures. */
  liveLabel: string;
  /** Called once the reader is done: resets `LiveFit` back to its idle view. */
  onRelease: () => void;
  /** Resolve the problem to actually run, once activated. */
  problem: LiveFitProblemLoader;
}
