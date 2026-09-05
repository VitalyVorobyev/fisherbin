import {render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {BenchmarkTable} from "../src/components/BenchmarkTable";
import {portalData} from "../src/data/portal";

describe("BenchmarkTable", () => {
  it("shows a task description, its quality label, and a per-row accessible name", () => {
    render(createElement(BenchmarkTable, {runs: portalData.benchmarks.runs}));

    const certifyRun = portalData.benchmarks.runs.find((run) => run.scenario === "certify");
    expect(certifyRun).toBeDefined();

    expect(screen.getByText("Branch-and-bound global D certificate")).toBeInTheDocument();
    expect(screen.getByText("certified log det I_q")).toBeInTheDocument();
    expect(
      screen.getByLabelText("Branch-and-bound global D certificate benchmark row")
    ).toBeInTheDocument();
  });
});
