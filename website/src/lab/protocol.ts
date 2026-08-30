import type {LabCriterion, LabEvent, LabProblem, LabRunRequest} from "./protocol.generated";

export type {
  LabCriterion,
  LabEvent,
  LabProblem,
  LabResult,
  LabRunRequest,
  ScoreRow
} from "./protocol.generated";

/** Wire version. Bumped with `schema/lab-protocol.schema.json`, never separately. */
export const PROTOCOL_VERSION = 2;

export const LAB_LIMITS = {
  maxBins: 16,
  // Six columns: the FlowCyt mixture score is five-dimensional once the
  // reference component is absorbed, and the exchange gain is quadratic in this
  // dimension, so the ceiling buys headroom without inviting arbitrary data.
  maxDimensions: 6,
  maxRows: 5_000,
  maxScans: 500,
  maxSteps: 500
} as const;

export function validateProblem(problem: LabProblem): string | null {
  if (problem.scores.length === 0) return "Add at least one score row.";
  if (problem.scores.length > LAB_LIMITS.maxRows) return `Browser runs are limited to ${LAB_LIMITS.maxRows.toLocaleString()} rows.`;
  if (problem.weights.length !== problem.scores.length) return "Scores and weights must contain the same number of rows.";
  const dimensions = problem.scores[0]?.length ?? 0;
  if (dimensions < 1 || dimensions > LAB_LIMITS.maxDimensions) return `Browser runs support one to ${LAB_LIMITS.maxDimensions} score dimensions.`;
  if (problem.scores.some((row) => row.length !== dimensions || row.some((value) => !Number.isFinite(value)))) return "Every score row must have the same finite dimension.";
  if (problem.weights.some((weight) => !Number.isFinite(weight) || weight < 0) || !problem.weights.some((weight) => weight > 0)) return "Weights must be finite and nonnegative, with at least one positive value.";
  if (!Number.isInteger(problem.nBins) || problem.nBins < 1 || problem.nBins > LAB_LIMITS.maxBins) return `Choose between one and ${LAB_LIMITS.maxBins} bins.`;
  if (problem.nBins > problem.scores.length) return "The number of bins cannot exceed the number of score rows.";
  if (problem.solver === "scalar_dp" && dimensions !== 1) return "Exact scalar DP requires one score dimension.";
  if ((problem.maxSteps ?? 1) > LAB_LIMITS.maxSteps || (problem.maxScans ?? 1) > LAB_LIMITS.maxScans) return "The requested solver budget exceeds the browser limit.";
  if (problem.schema !== undefined && problem.schema.length !== dimensions) return `A score schema must name all ${String(dimensions)} columns.`;
  return validateCriterion(problem, dimensions);
}

/**
 * Check the objective against the score space it will be applied to.
 *
 * The library refuses these pairings too, but it refuses them after the run has
 * been shipped to a worker and a 15 MB runtime has warmed up; saying so here
 * turns a slow failure into an immediate one.
 */
function validateCriterion(problem: LabProblem, dimensions: number): string | null {
  const criterion = problem.criterion;
  const name = criterion?.name ?? "d_optimality";

  // k-means implements the normalized trace and nothing else, so pairing it
  // with a determinant objective is refused rather than quietly approximated.
  if (problem.solver === "kmeans" && name !== "normalized_trace") {
    return "The k-means solver fits the normalized trace. Choose that criterion, or another solver.";
  }
  if (name === "normalized_trace") {
    return problem.solver === "kmeans" ? null : "Normalized trace is fitted by the k-means solver.";
  }

  // Every D-optimal path needs at least as many bins as informative score
  // directions: with fewer, the between-cell information matrix is singular and
  // its log-determinant is undefined. The effective rank is only known once the
  // fit runs, but it is at most the score dimension.
  if (problem.nBins < dimensions) {
    return `D-optimality needs at least as many bins as informative score directions. This table has ${String(dimensions)}; raise the bin budget to ${String(dimensions)} or more.`;
  }
  if (criterion === undefined || name === "d_optimality") return null;
  if (problem.solver !== "soft_voronoi") {
    return "Profiled Dₛ needs the soft Voronoi solver: an exchange-stable profiled partition has no canonical reusable rule.";
  }
  const interest = criterion.interest ?? [];
  if (interest.length === 0) return "Choose at least one parameter of interest.";
  if (interest.length >= dimensions) return "At least one nuisance parameter must remain unprofiled.";
  if (problem.schema === undefined) return "Profiling by name needs a score schema.";
  const unknown = interest.filter((name) => !problem.schema?.includes(name));
  if (unknown.length > 0) return `Unknown parameter${unknown.length > 1 ? "s" : ""}: ${unknown.join(", ")}.`;
  return null;
}

export function isLabEvent(value: unknown): value is LabEvent {
  if (typeof value !== "object" || value === null) return false;
  const event = value as Partial<LabEvent>;
  return event.protocolVersion === PROTOCOL_VERSION && typeof event.runId === "string" && ["ready", "progress", "result", "error", "cancelled"].includes(event.type ?? "");
}

export function createRunRequest(problem: LabProblem, runner: LabRunRequest["runner"]): LabRunRequest {
  return {protocolVersion: PROTOCOL_VERSION, type: "run", runId: crypto.randomUUID(), runner, problem};
}

/** Human-readable objective label, used in the diagnostics panel and the result. */
export function criterionLabel(criterion: LabCriterion | undefined): string {
  if (criterion === undefined || criterion.name === "d_optimality") return "D-optimality";
  if (criterion.name === "normalized_trace") return "Normalized trace";
  return `Profiled Dₛ (${(criterion.interest ?? []).join(", ")})`;
}
