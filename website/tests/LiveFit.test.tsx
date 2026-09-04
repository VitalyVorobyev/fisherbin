import {fireEvent, render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it, vi} from "vitest";

import {LiveFit} from "../src/components/liveFit/LiveFit";
import {LiveFitProvider} from "../src/components/liveFit/LiveFitProvider";
import type {LiveFitProblem} from "../src/components/liveFit/types";

// `LiveFit` reaches `LiveFitRunner` only through a dynamic import inside its
// click handler, so this stands in for the runner rather than letting the
// real one load `useLabRunner`/`runtimeClient` (which needs a real `Worker`,
// unavailable under jsdom -- see `tests/runtimeClient.test.ts`'s own note).
// Asserting that dynamic import actually happens, and swaps the rendered
// component, is the whole point of these tests; what the runner itself does
// once loaded is covered end to end in `tests/e2e/portal.spec.ts`. Vitest
// hoists `vi.mock` above the imports above, so both already see the mock.
vi.mock("../src/components/liveFit/LiveFitRunner", () => ({
  LiveFitRunner: () => createElement("div", {"data-testid": "runner-active"}, "Runner active")
}));

const problem = (): Promise<LiveFitProblem> =>
  Promise.resolve({
    nBins: 2,
    scores: [[0], [1]],
    seed: 1,
    solver: "d_exchange",
    weights: [1, 1]
  });

function demo(id: string, label: string): React.JSX.Element {
  return createElement(LiveFit, {
    id,
    activationLabel: label,
    committedLabel: "Committed",
    committedRetention: 0.9123,
    formatRetention: (value: number) => value.toFixed(4),
    liveLabel: "Live",
    problem
  });
}

describe("LiveFit", () => {
  it("shows the committed result and exactly one activation button before any click", () => {
    render(createElement(LiveFitProvider, null, demo("demo-idle", "Run this in your browser")));
    expect(screen.getByText("0.9123")).toBeInTheDocument();
    expect(screen.getByText("Committed result")).toBeInTheDocument();
    expect(screen.getAllByRole("button")).toHaveLength(1);
    expect(screen.getByRole("button", {name: "Run this in your browser"})).toBeEnabled();
  });

  it("loads the runner chunk only once activated", async () => {
    render(createElement(LiveFitProvider, null, demo("demo-activate", "Run this in your browser")));
    expect(screen.queryByTestId("runner-active")).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", {name: "Run this in your browser"}));
    expect(await screen.findByTestId("runner-active")).toBeInTheDocument();
  });

  it("refuses a second activation while one demo is active, without queuing it", async () => {
    render(
      createElement(
        LiveFitProvider,
        null,
        demo("demo-a", "Run demo A"),
        demo("demo-b", "Run demo B")
      )
    );
    fireEvent.click(screen.getByRole("button", {name: "Run demo A"}));
    expect(screen.getByRole("button", {name: "Run demo B"})).toBeDisabled();
    expect(screen.getByText(/Only one live demo can run at a time on this page/)).toBeInTheDocument();
    // Let demo A's own activation settle so no update lands after the test ends.
    await screen.findByTestId("runner-active");
  });
});
