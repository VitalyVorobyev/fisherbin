/* Generated from schema/lab-protocol.schema.json. Do not edit. */

/**
 * Versioned backend-neutral request and event contract for the ScoreQuant browser lab.
 */
export type LabProtocol = LabRunRequest | LabEvent;
/**
 * @minItems 1
 * @maxItems 4
 */
export type ScoreRow = [number] | [number, number] | [number, number, number] | [number, number, number, number];

export interface LabRunRequest {
  protocolVersion: 1;
  type: "run";
  runId: string;
  runner: "fixture" | "pyodide-numpy" | "remote-jax" | "remote-pytorch";
  problem: LabProblem;
}
export interface LabProblem {
  /**
   * @maxItems 5000
   */
  scores: ScoreRow[];
  /**
   * @maxItems 5000
   */
  weights: number[];
  nBins: number;
  solver: "d_exchange" | "mahalanobis_lloyd" | "kmeans" | "scalar_dp" | "soft_voronoi";
  seed: number;
  maxSteps?: number;
  maxScans?: number;
}
export interface LabEvent {
  protocolVersion: 1;
  runId: string;
  type: "ready" | "progress" | "result" | "error" | "cancelled";
  stage?: string;
  progress?: number;
  result?: LabResult;
  message?: string;
}
export interface LabResult {
  labels: number[];
  centers: number[][];
  retention: number;
  objective: number;
  execution: string;
}
