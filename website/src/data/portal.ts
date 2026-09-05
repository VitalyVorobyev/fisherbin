import rawData from "../generated/portal-data.json";

export interface ApiSymbol {
  kind: "class" | "function";
  name: string;
  reference: string;
  signature: string;
  source: string;
  summary: string;
}

export interface ResearchClaim {
  dependencies: string[];
  id: string;
  level: string;
  statement: string;
  status: string;
  title: string;
}

export interface PortalData {
  api: ApiSymbol[];
  research: ResearchClaim[];
  schemaVersion: number;
}

export const portalData = rawData as PortalData;
