import {render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {FringeCurve} from "../src/components/FringeCurve";
import {michelsonSweep} from "../src/data/michelsonSweep";

describe("FringeCurve", () => {
  it("gives the chart an accessible name", () => {
    render(createElement(FringeCurve, {caption: "The fringe law."}));
    expect(screen.getByRole("img", {name: "Fringe intensity along the aperture"})).toBeInTheDocument();
  });

  it("draws the curve as a single path starting with a moveto", () => {
    const {container} = render(createElement(FringeCurve, {caption: "The fringe law."}));
    const path = container.querySelector(".fringe-curve__curve");
    expect(path).not.toBeNull();
    expect(path?.getAttribute("d")).toMatch(/^M/);
  });

  it("marks one fringe-boundary tick label per fringe, plus the origin", () => {
    const {container} = render(createElement(FringeCurve, {caption: "The fringe law."}));
    const ticks = container.querySelectorAll(".chart-tick");
    const tickLabels = Array.from(ticks)
      .map((node) => node.textContent)
      .filter((text) => text === "0" || /^\d+π$/.test(text));
    expect(tickLabels).toHaveLength(michelsonSweep.fringes + 1);
  });

  it("draws one dashed boundary per internal segment edge, using the default segment count", () => {
    const {container} = render(createElement(FringeCurve, {caption: "The fringe law."}));
    const boundaries = container.querySelectorAll(".fringe-curve__segment-boundary");
    expect(boundaries).toHaveLength(michelsonSweep.headlineBins - 1);
  });

  it("draws `segments - 1` dashed boundaries when overridden", () => {
    const {container} = render(createElement(FringeCurve, {caption: "The fringe law.", segments: 8}));
    const boundaries = container.querySelectorAll(".fringe-curve__segment-boundary");
    expect(boundaries).toHaveLength(7);
  });
});
