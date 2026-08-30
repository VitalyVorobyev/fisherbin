/* Generated from schema/lab-protocol.schema.json. Do not edit. */

/**
 * Versioned backend-neutral request and event contract for the ScoreQuant browser lab. Version 2 admits a named score schema, a criterion selection including profiled D_s, and score spaces up to six dimensions so real mixture scores fit.
 */
export type LabProtocol = LabRunRequest | LabEvent;
/**
 * One score row. Six columns is the browser ceiling: the FlowCyt mixture score is five-dimensional after the reference component is absorbed, and the exchange scan is quadratic in this dimension.
 *
 * @minItems 1
 * @maxItems 6
 */
export type ScoreRow =
  | [number]
  | [number, number]
  | [number, number, number]
  | [number, number, number, number]
  | [number, number, number, number, number]
  | [number, number, number, number, number, number];

export interface LabRunRequest {
  protocolVersion: 2;
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
  criterion?: LabCriterion;
  /**
   * Parameter names in score-column order, so a profiled criterion can name them.
   *
   * @minItems 1
   * @maxItems 6
   */
  schema?:
    | [string]
    | [string, string]
    | [string, string, string]
    | [string, string, string, string]
    | [string, string, string, string, string]
    | [string, string, string, string, string, string];
  /**
   * Identifier of the score table the request was built from, recorded for provenance.
   */
  datasetId?: string;
}
/**
 * The objective to optimize. Profiled D_s requires parameters of interest.
 */
export interface LabCriterion {
  name: "d_optimality" | "profiled_d_optimality" | "normalized_trace";
  /**
   * Parameters of interest by name; resolved against `schema`.
   *
   * @minItems 1
   * @maxItems 5
   */
  interest?:
    | [string]
    | [string, string]
    | [string, string, string]
    | [string, string, string, string]
    | [string, string, string, string, string];
}
export interface LabEvent {
  protocolVersion: 2;
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
  /**
   * The objective the reported retention is measured against.
   */
  criterionLabel?: string;
  /**
   * Parameters of interest, echoed back by name when the criterion profiled.
   */
  interest?: string[];
}
