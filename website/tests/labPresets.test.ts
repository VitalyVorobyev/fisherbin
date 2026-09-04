import {describe, expect, it} from "vitest";

import rawPresets from "../src/generated/lab-presets.json";
import {resolveJobPreset} from "../src/lab/jobPreset";
import {getLabPreset, solverForCriterion} from "../src/lab/presets";
import {LAB_LIMITS} from "../src/lab/protocol";
import type {LabCriterion, LabProblem} from "../src/lab/protocol";
import type {PresetDataset} from "../src/lab/presets";

const KNOWN_CRITERIA: LabCriterion["name"][] = [
  "d_optimality",
  "profiled_d_optimality",
  "normalized_trace"
];
const KNOWN_SOLVERS: LabProblem["solver"][] = [
  "d_exchange",
  "mahalanobis_lloyd",
  "kmeans",
  "scalar_dp",
  "soft_voronoi"
];
const KNOWN_DATASETS: PresetDataset[] = ["gaussian", "flowcyt", "hep", "michelson", "ratios"];

describe("the committed Lab preset registry", () => {
  const slugs = Object.keys(rawPresets);

  it("parses to a non-empty map of slugs", () => {
    expect(slugs.length).toBeGreaterThan(0);
  });

  it("every entry names a dataset, criterion, bin budget, and derived solver the Lab accepts", () => {
    for (const slug of slugs) {
      const preset = getLabPreset(slug);
      expect(preset, `${slug} failed registry validation`).toBeDefined();
      if (preset === undefined) continue;
      expect(KNOWN_DATASETS).toContain(preset.dataset);
      expect(KNOWN_CRITERIA).toContain(preset.criterion);
      expect(KNOWN_SOLVERS).toContain(solverForCriterion(preset.criterion));
      expect(Number.isInteger(preset.bins)).toBe(true);
      expect(preset.bins).toBeGreaterThanOrEqual(1);
      expect(preset.bins).toBeLessThanOrEqual(LAB_LIMITS.maxBins);
      expect(preset.detail.length).toBeGreaterThan(0);
      expect(preset.label.length).toBeGreaterThan(0);
    }
  });

  it("rejects a slug the registry does not name", () => {
    expect(getLabPreset("does-not-exist")).toBeUndefined();
  });
});

describe("resolveJobPreset", () => {
  it("returns null with no ?job= parameter", () => {
    expect(resolveJobPreset("")).toBeNull();
    expect(resolveJobPreset("?bins=6")).toBeNull();
  });

  it("returns null for an unknown or empty slug", () => {
    expect(resolveJobPreset("?job=not-a-real-preset")).toBeNull();
    expect(resolveJobPreset("?job=")).toBeNull();
  });

  it("seeds the exact control values for a plain-D preset", () => {
    expect(resolveJobPreset("?job=ratios")).toEqual({
      bins: 4,
      criterionName: "d_optimality",
      dataset: "ratios",
      interest: [],
      runner: "pyodide-numpy",
      solver: "d_exchange"
    });
  });

  it("derives the soft Voronoi solver for a profiled preset", () => {
    expect(resolveJobPreset("?job=hep")).toEqual({
      bins: 6,
      criterionName: "profiled_d_optimality",
      dataset: "hep",
      interest: ["mu_htautau"],
      runner: "pyodide-numpy",
      solver: "soft_voronoi"
    });
  });

  it("is tolerant of extra query parameters and a leading '?'", () => {
    expect(resolveJobPreset("job=ratios")).toEqual(resolveJobPreset("?job=ratios"));
    expect(resolveJobPreset("?other=1&job=ratios")).toEqual(resolveJobPreset("?job=ratios"));
  });
});
