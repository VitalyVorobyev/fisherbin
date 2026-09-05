import {render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {BROWSER_MATRIX, LESSONS} from "../src/data/lessons";
import type {LabProblem} from "../src/lab/protocol";
import {validateProblem} from "../src/lab/protocol";
import Lessons from "../src/pages/lab";

/**
 * A tiny well-formed problem for one matrix row: three named columns so a
 * profiled criterion has a nuisance left over, and enough bins for any
 * determinant objective. Only the pairing rules are under test here.
 */
function problemFor(row: (typeof BROWSER_MATRIX)[number]): LabProblem {
  const problem: LabProblem = {
    nBins: 4,
    schema: ["a", "b", "c"],
    scores: [
      [0.1, 0.2, 0.3],
      [0.4, 0.5, 0.6],
      [0.7, 0.8, 0.9],
      [1.0, 1.1, 1.2],
      [1.3, 1.4, 1.5]
    ],
    seed: 1,
    solver: row.solver,
    task: row.task,
    weights: [1, 1, 1, 1, 1]
  };
  if (row.criterion === "profiled_d_optimality") problem.criterion = {interest: ["a"], name: row.criterion};
  else if (row.criterion === "normalized_trace") problem.criterion = {name: row.criterion};
  return problem;
}

describe("the browser capability matrix", () => {
  it("agrees with the protocol validator on every row", () => {
    for (const row of BROWSER_MATRIX) {
      const verdict = validateProblem(problemFor(row));
      expect(verdict === null, `${row.task} / ${row.criterion} / ${row.solver}: ${verdict ?? "accepted"}`).toBe(row.runnable);
    }
  });
});

describe("the lesson index", () => {
  it("states every contract row for every lesson and links each one", () => {
    render(createElement(Lessons));
    for (const lesson of LESSONS) {
      const heading = screen.getByRole("heading", {level: 2, name: lesson.title});
      expect(heading).toBeInTheDocument();
    }
    expect(screen.getAllByText("Admissible labels")).toHaveLength(LESSONS.length);
    expect(screen.getAllByText("Score provenance")).toHaveLength(LESSONS.length);
    expect(screen.getAllByText("Task and output")).toHaveLength(LESSONS.length);
    const links = screen.getAllByRole("link").filter((link) => (link.getAttribute("href") ?? "").includes("/walkthroughs/"));
    expect(links.length).toBeGreaterThanOrEqual(LESSONS.length);
  });

  it("carries no bin budget typed by hand", () => {
    for (const lesson of LESSONS) {
      expect(lesson.contract.budget).toMatch(/^\d+$/);
    }
  });
});
