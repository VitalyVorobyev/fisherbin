import rawPresets from "../generated/lab-presets.json";
import {LAB_LIMITS} from "./protocol";
import type {LabCriterion, LabProblem} from "./protocol";
import type {DatasetId} from "./useScoreTable";

/** A preset's dataset is always a committed table, never the "local" upload slot. */
export type PresetDataset = Exclude<DatasetId, "local">;

/**
 * One committed Lab preset: the control state a walkthrough's `?job=<slug>`
 * link seeds the Lab with.
 *
 * Written by `generate_walkthroughs.py`'s `write_lab_presets` to
 * `website/src/generated/lab-presets.json`; never edited by hand. Every
 * field names a value `website/src/pages/lab.tsx` already accepts -- see
 * `getLabPreset`, which checks that at runtime rather than trusting the cast.
 */
export interface LabPreset {
  bins: number;
  criterion: LabCriterion["name"];
  dataset: PresetDataset;
  detail: string;
  interest?: string[];
  label: string;
}

const LAB_PRESETS = rawPresets as Record<string, LabPreset>;

const KNOWN_DATASETS = new Set<PresetDataset>(["gaussian", "flowcyt", "hep", "michelson", "ratios"]);
const KNOWN_CRITERIA = new Set<LabCriterion["name"]>([
  "d_optimality",
  "profiled_d_optimality",
  "normalized_trace",
]);

/**
 * The solver a criterion requires, mirroring `validateCriterion` in
 * `./protocol.ts`: k-means fits only the normalized trace, and profiled
 * D_s has no canonical reusable rule outside the soft Voronoi solver.
 */
export function solverForCriterion(criterion: LabCriterion["name"]): LabProblem["solver"] {
  if (criterion === "normalized_trace") return "kmeans";
  if (criterion === "profiled_d_optimality") return "soft_voronoi";
  return "d_exchange";
}

/**
 * Look up one committed Lab preset by slug, validating that every field
 * names a value the Lab actually accepts.
 *
 * The registry is written by a generator this page cannot see fail, so this
 * revalidates its shape at runtime rather than trusting the cast: an
 * unknown slug, or a malformed entry, returns `undefined` rather than
 * seeding a run the Lab would refuse.
 */
export function getLabPreset(slug: string): LabPreset | undefined {
  const preset = LAB_PRESETS[slug];
  if (preset === undefined) return undefined;
  if (!KNOWN_DATASETS.has(preset.dataset)) return undefined;
  if (!KNOWN_CRITERIA.has(preset.criterion)) return undefined;
  if (!Number.isInteger(preset.bins) || preset.bins < 1 || preset.bins > LAB_LIMITS.maxBins) {
    return undefined;
  }
  if (preset.interest !== undefined && preset.interest.length === 0) return undefined;
  return preset;
}

/** Every slug the committed registry names, for tests that check coverage. */
export function labPresetSlugs(): string[] {
  return Object.keys(LAB_PRESETS);
}
