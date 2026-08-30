import {describe, expect, it} from "vitest";

import {createRunRequest, LAB_LIMITS, validateProblem} from "../src/lab/protocol";
import type {LabProblem} from "../src/lab/protocol";

const validProblem: LabProblem = {
  scores: [[-1, 0], [0, 1], [1, 0]],
  weights: [1, 1, 1],
  nBins: 2,
  solver: "d_exchange",
  seed: 7,
  maxScans: 20
};

describe("lab protocol", () => {
  it("accepts a bounded finite problem", () => {
    expect(validateProblem(validProblem)).toBeNull();
    const request = createRunRequest(validProblem, "pyodide-numpy");
    expect(request).toMatchObject({protocolVersion: 1, runner: "pyodide-numpy", type: "run"});
  });

  it("rejects mismatched weights and scalar-only misuse", () => {
    expect(validateProblem({...validProblem, weights: [1]})).toContain("same number");
    expect(validateProblem({...validProblem, solver: "scalar_dp"})).toContain("one score dimension");
  });

  it("enforces the browser capacity envelope", () => {
    const scores = Array.from({length: LAB_LIMITS.maxRows + 1}, () => [0] as [number]);
    expect(validateProblem({...validProblem, scores, weights: scores.map(() => 1)})).toContain("5,000");
    expect(validateProblem({...validProblem, nBins: LAB_LIMITS.maxBins + 1})).toContain("16");
  });
});
