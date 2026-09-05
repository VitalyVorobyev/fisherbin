import {render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {ScoreSpace} from "../src/components/ScoreSpace";
import {portalData} from "../src/data/portal";

describe("ScoreSpace", () => {
  it("renders generated scientific evidence instead of placeholder metrics", () => {
    render(createElement(ScoreSpace, {compact: true, controlledBins: 4}));
    expect(screen.getByRole("img", {name: "Score-space partition with 4 bins"})).toBeInTheDocument();
    expect(screen.getByText("D-efficiency").nextSibling?.textContent).toMatch(/%/);
    expect(screen.getByText("hard bins").nextSibling).toHaveTextContent("4");
  });

  it("draws the compiled cell regions instead of Euclidean bisector lines", () => {
    const {container} = render(createElement(ScoreSpace, {compact: true, controlledBins: 4}));
    expect(container.querySelectorAll("line")).toHaveLength(0);
    const regionGroup = container.querySelector(".score-regions");
    expect(regionGroup).not.toBeNull();
    expect(regionGroup?.querySelectorAll("rect").length).toBeGreaterThan(0);
  });

  it("draws no regions for an overridden scenario that carries none", () => {
    const fixture = portalData.scoreSpace.scenarios["4"];
    if (fixture === undefined) throw new Error("no generated score-space fixture for 4 bins");
    const {centers, labels, objective, retention} = fixture;
    const {container} = render(
      createElement(ScoreSpace, {
        compact: true,
        controlledBins: 4,
        scenarioOverride: {centers, labels, objective, retention}
      })
    );
    expect(container.querySelector(".score-regions")).toBeNull();
  });
});
