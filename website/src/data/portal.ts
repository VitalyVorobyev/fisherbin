import rawData from "../generated/portal-data.json";

export interface ApiSymbol {
  kind: "class" | "function";
  name: string;
  reference: string;
  signature: string;
  source: string;
  summary: string;
}

export interface BenchmarkRun {
  bins: number;
  dims: number;
  elapsed_seconds: number;
  peak_rss_megabytes: number;
  quality: number;
  quality_label: string;
  rows: number;
  scenario: string;
}

export interface ResearchClaim {
  dependencies: string[];
  id: string;
  level: string;
  statement: string;
  status: string;
  title: string;
}

export interface ScoreRegions {
  /** One digit per grid cell, row-major (`ny` rows of `nx`); decode with `charCodeAt(i) - 48`. */
  labels: string;
  nx: number;
  ny: number;
  x0: number;
  x1: number;
  y0: number;
  y1: number;
}

export interface ScoreScenario {
  centers: number[][];
  labels: number[];
  metric?: number[][];
  objective: number;
  regions?: ScoreRegions;
  retention: number;
}

export interface PortalData {
  api: ApiSymbol[];
  benchmarks: {
    environment: Record<string, string>;
    runs: BenchmarkRun[];
  };
  research: ResearchClaim[];
  schemaVersion: number;
  scoreSpace: {
    points: number[][];
    scenarios: Record<string, ScoreScenario>;
    weights: number[];
  };
}

export const portalData = rawData as PortalData;
