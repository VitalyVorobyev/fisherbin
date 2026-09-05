import {fireEvent, render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it, vi} from "vitest";

import {LiveFitProvider} from "../src/components/liveFit/LiveFitProvider";
import {MichelsonBudgetExplorer} from "../src/components/MichelsonBudgetExplorer";
import {michelsonSweep} from "../src/data/michelsonSweep";

// `MichelsonBudgetExplorer` must never reach the browser runtime itself --
// only `LiveFit`'s own dynamic `import("./LiveFitRunner")`, behind a click,
// is allowed to. Mocking `useLabRunner` and asserting it is never called
// (without ever clicking the activation button) is the same check
// `tests/LiveFit.test.tsx` makes of `LiveFit` itself: if the explorer's
// static import graph pulled in `useLabRunner` -- directly, or through
// something that imports `LiveFitRunner` outside a dynamic import -- this
// mock would already be exercised on mount, before any click.
const useLabRunnerSpy = vi.fn();
vi.mock("../src/lab/useLabRunner", () => ({useLabRunner: useLabRunnerSpy}));

function renderExplorer(): ReturnType<typeof render> {
  return render(createElement(LiveFitProvider, null, createElement(MichelsonBudgetExplorer)));
}

const headlineRow = michelsonSweep.rows.find((row) => row.nBins === michelsonSweep.headlineBins);
if (headlineRow === undefined) throw new Error("fixture: no headline row in michelsonSweep");
const otherRow = michelsonSweep.rows.find((row) => row.nBins !== michelsonSweep.headlineBins);
if (otherRow === undefined) throw new Error("fixture: sweep needs at least two rows to test a budget change");

describe("MichelsonBudgetExplorer", () => {
  it("renders with the headline K checked and never touches the browser runtime", () => {
    renderExplorer();
    expect(screen.getByRole("radio", {name: String(michelsonSweep.headlineBins)})).toBeChecked();
    expect(
      screen.getByRole("img", {name: `Aperture readout at ${String(michelsonSweep.headlineBins)} counters`})
    ).toBeInTheDocument();
    expect(useLabRunnerSpy).not.toHaveBeenCalled();
  });

  it("disables Reset while already at the headline budget", () => {
    renderExplorer();
    expect(screen.getByRole("button", {name: "Reset to the headline budget"})).toBeDisabled();
  });

  it("choosing another radio updates the strip title and the comparison values to that row", () => {
    renderExplorer();
    fireEvent.click(screen.getByRole("radio", {name: String(otherRow.nBins)}));

    expect(
      screen.getByRole("img", {name: `Aperture readout at ${String(otherRow.nBins)} counters`})
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("img", {name: `Aperture readout at ${String(headlineRow.nBins)} counters`})
    ).not.toBeInTheDocument();

    expect(screen.getAllByText(otherRow.text.equalWidth).length).toBeGreaterThan(0);
    expect(screen.getAllByText(otherRow.text.dOptimal).length).toBeGreaterThan(0);
    expect(screen.getAllByText(otherRow.text.profiled).length).toBeGreaterThan(0);
    expect(screen.getAllByText(otherRow.text.ceiling).length).toBeGreaterThan(0);

    expect(screen.getByRole("button", {name: "Reset to the headline budget"})).toBeEnabled();
  });

  it("Reset restores the headline budget and disables itself again", () => {
    renderExplorer();
    fireEvent.click(screen.getByRole("radio", {name: String(otherRow.nBins)}));
    const resetButton = screen.getByRole("button", {name: "Reset to the headline budget"});
    expect(resetButton).toBeEnabled();

    fireEvent.click(resetButton);

    expect(screen.getByRole("radio", {name: String(michelsonSweep.headlineBins)})).toBeChecked();
    expect(resetButton).toBeDisabled();
    expect(
      screen.getByRole("img", {name: `Aperture readout at ${String(michelsonSweep.headlineBins)} counters`})
    ).toBeInTheDocument();
  });

  it("shows the LiveFit activation button without ever loading the browser runtime", () => {
    renderExplorer();
    expect(screen.getByRole("button", {name: "Refit this budget in your browser"})).toBeInTheDocument();
    expect(useLabRunnerSpy).not.toHaveBeenCalled();
  });
});
