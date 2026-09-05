/* Generated from schema/lab-protocol.schema.json. Do not edit. */

/**
 * Versioned backend-neutral request and event contract for the ScoreQuant browser lab. Version 3 admits a choice of public task (fit_quantizer or optimize_partition), efficient-score-bound initialization, and a named profiled-retention report, and raises the score table ceiling to 8,000 rows.
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
  protocolVersion: 3;
  type: "run";
  runId: string;
  runner: "fixture" | "pyodide-numpy" | "remote-jax" | "remote-pytorch";
  problem: LabProblem;
}
export interface LabProblem {
  /**
   * @maxItems 8000
   */
  scores: ScoreRow[];
  /**
   * @maxItems 8000
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
  /**
   * Which public task to run. Absent means fit_quantizer (v2 semantics).
   */
  task?: "fit_quantizer" | "optimize_partition";
  /**
   * Seed the exchange from efficient_score_bound(...).labels; only with task optimize_partition and a profiled criterion.
   */
  initialization?: "efficient_score_bound";
  report?: {
    /**
     * Report the profiled retention of the result for these parameters of interest, resolved against schema, whatever criterion was solved.
     *
     * @minItems 1
     * @maxItems 5
     */
    profiledInterest?:
      | [string]
      | [string, string]
      | [string, string, string]
      | [string, string, string, string]
      | [string, string, string, string, string];
  };
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
  protocolVersion: 3;
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
  /**
   * Profiled retention for report.profiledInterest, whatever criterion the result was solved against.
   */
  profiledRetention?: number;
  /**
   * Whether the result is exchange-stable. optimize_partition only.
   */
  exchangeStable?: boolean;
}
