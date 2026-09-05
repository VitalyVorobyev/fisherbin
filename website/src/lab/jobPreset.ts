import {getLabPreset, solverForCriterion} from "./presets";
import type {PresetDataset} from "./presets";
import type {LabCriterion, LabProblem, LabRunRequest} from "./protocol";

/**
 * The Lab's existing control state, seeded from a resolved `?job=<slug>`.
 *
 * Every field names an existing `useState` in `website/src/pages/lab.tsx`;
 * this is initial-value seeding only, not a new control.
 */
export interface JobPresetSeed {
  bins: number;
  criterionName: LabCriterion["name"];
  dataset: PresetDataset;
  interest: string[];
  runner: LabRunRequest["runner"];
  solver: LabProblem["solver"];
}

/**
 * Resolve a `?job=<slug>` query string (`search`, with or without its
 * leading `?`) into the Lab's seeded control state, or `null` when there is
 * nothing to seed.
 *
 * An absent, malformed, or unknown slug returns `null`, indistinguishable to
 * the caller from "no job requested" -- the Lab opens on its ordinary
 * defaults, never an error. `runner` is always `"pyodide-numpy"`: none of
 * the committed presets is the built-in Gaussian fixture, the only table
 * the `"fixture"` runner covers.
 */
export function resolveJobPreset(search: string): JobPresetSeed | null {
  const slug = new URLSearchParams(search).get("job");
  if (slug === null) return null;
  const preset = getLabPreset(slug);
  if (preset === undefined) return null;
  return {
    bins: preset.bins,
    criterionName: preset.criterion,
    dataset: preset.dataset,
    interest: preset.interest ?? [],
    runner: "pyodide-numpy",
    solver: solverForCriterion(preset.criterion),
  };
}
