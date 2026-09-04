import {render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {LiveFitProvider} from "../src/components/liveFit/LiveFitProvider";
import {ScoreSpaceLiveFit} from "../src/components/ScoreSpaceLiveFit";

describe("ScoreSpaceLiveFit", () => {
  it("shows the committed scenario's own retention beside the ScoreSpace plot", () => {
    render(createElement(LiveFitProvider, null, createElement(ScoreSpaceLiveFit)));
    // The default 4-bin scenario's committed D-efficiency, formatted the same
    // way `ScoreSpace` itself formats its own metrics row.
    expect(screen.getByRole("img", {name: "Score-space partition with 4 bins"})).toBeInTheDocument();
    expect(screen.getByText("Committed D-efficiency at 4 bins")).toBeInTheDocument();
    expect(screen.getByRole("button", {name: "Refit these points in your browser"})).toBeEnabled();
  });
});
