import type {LabEvent, LabProblem, LabRunRequest} from "./protocol.generated";

export type {LabEvent, LabProblem, LabResult, LabRunRequest, ScoreRow} from "./protocol.generated";

export const LAB_LIMITS = {
  maxBins: 16,
  maxDimensions: 4,
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
  return null;
}

export function isLabEvent(value: unknown): value is LabEvent {
  if (typeof value !== "object" || value === null) return false;
  const event = value as Partial<LabEvent>;
  return event.protocolVersion === 1 && typeof event.runId === "string" && ["ready", "progress", "result", "error", "cancelled"].includes(event.type ?? "");
}

export function createRunRequest(problem: LabProblem, runner: LabRunRequest["runner"]): LabRunRequest {
  return {protocolVersion: 1, type: "run", runId: crypto.randomUUID(), runner, problem};
}
