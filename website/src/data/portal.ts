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

export interface ContentEntry {
  excerpt: string;
  reference: string;
  slug: string;
  tags?: string[];
  title: string;
}

export interface ResearchClaim {
  dependencies: string[];
  id: string;
  level: string;
  statement: string;
  status: string;
  title: string;
}

export interface ScoreScenario {
  centers: number[][];
  labels: number[];
  objective: number;
  retention: number;
}

export interface PortalData {
  api: ApiSymbol[];
  benchmarks: {
    environment: Record<string, string>;
    runs: BenchmarkRun[];
  };
  content: {chapters: ContentEntry[]; examples: ContentEntry[]};
  research: ResearchClaim[];
  schemaVersion: number;
  scoreSpace: {
    points: number[][];
    scenarios: Record<string, ScoreScenario>;
    weights: number[];
  };
}

export const portalData = rawData as PortalData;
