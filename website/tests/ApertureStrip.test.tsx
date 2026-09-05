import {render, screen, within} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {ApertureStrip, runsFromLabels} from "../src/components/ApertureStrip";
import type {ApertureRun} from "../src/data/michelsonSweep";

const equalWidth: ApertureRun[] = [
  {end: 3.14, label: 0, start: 0},
  {end: 6.28, label: 1, start: 3.14}
];

const profiled: ApertureRun[] = [
  {end: 1, label: 1, start: 0},
  {end: 2, label: 0, start: 1},
  {end: 4, label: 1, start: 2},
  {end: 6.28, label: 0, start: 4}
];

describe("ApertureStrip", () => {
  it("draws exactly one rect per run, across every band, merging nothing", () => {
    const {container} = render(
      createElement(ApertureStrip, {
        bands: [
          {label: "Equal segments", runs: equalWidth},
          {label: "Profiled Ds", runs: profiled}
        ],
        description: "Two labellings of the same aperture.",
        fringes: 4,
        title: "Aperture readout at 6 counters",
        uMax: 6.28
      })
    );
    const rects = container.querySelectorAll(".aperture-strip__run");
    expect(rects).toHaveLength(equalWidth.length + profiled.length);
  });

  it("gives the chart an accessible name and description", () => {
    render(
      createElement(ApertureStrip, {
        bands: [{label: "Equal segments", runs: equalWidth}],
        description: "One labelling of the aperture.",
        fringes: 4,
        title: "Aperture readout at 6 counters",
        uMax: 6.28
      })
    );
    expect(screen.getByRole("img", {name: "Aperture readout at 6 counters"})).toBeInTheDocument();
  });

  it("marks a tick at every fringe boundary, 0 through fringes", () => {
    const {container} = render(
      createElement(ApertureStrip, {
        bands: [{label: "Equal segments", runs: equalWidth}],
        description: "One labelling of the aperture.",
        fringes: 4,
        title: "Aperture readout at 6 counters",
        uMax: 6.28
      })
    );
    const ticks = Array.from(container.querySelectorAll(".chart-tick")).map((node) => node.textContent);
    expect(ticks).toEqual(["0", "1", "2", "3", "4"]);
  });

  it("carries a hidden text alternative listing every run of every band", () => {
    render(
      createElement(ApertureStrip, {
        bands: [
          {label: "Equal segments", runs: equalWidth},
          {label: "Profiled Ds", runs: profiled}
        ],
        description: "Two labellings of the same aperture.",
        fringes: 4,
        title: "Aperture readout at 6 counters",
        uMax: 6.28
      })
    );
    const table = screen.getByRole("table", {hidden: true});
    const rows = within(table).getAllByRole("row", {hidden: true});
    // One header row plus one row per run across both bands.
    expect(rows).toHaveLength(1 + equalWidth.length + profiled.length);
    for (const run of [...equalWidth, ...profiled]) {
      expect(within(table).getAllByText(run.start.toFixed(4)).length).toBeGreaterThan(0);
    }
  });
});

describe("runsFromLabels", () => {
  it("merges consecutive equal labels into one run", () => {
    const runs = runsFromLabels([0, 0, 1, 1, 1, 0], 6);
    expect(runs).toEqual([
      {end: 2, label: 0, start: 0},
      {end: 5, label: 1, start: 2},
      {end: 6, label: 0, start: 5}
    ]);
  });

  it("tiles [0, uMax] exactly: the first run starts at 0 and the last ends at uMax", () => {
    const uMax = 10;
    const runs = runsFromLabels([2, 2, 0, 1], uMax);
    expect(runs[0]?.start).toBe(0);
    expect(runs.at(-1)?.end).toBe(uMax);
  });

  it("returns one run per node when no two consecutive nodes share a label", () => {
    const runs = runsFromLabels([0, 1, 2], 3);
    expect(runs).toHaveLength(3);
  });

  it("returns an empty array for an empty labels array", () => {
    expect(runsFromLabels([], 10)).toEqual([]);
  });
});

describe("ApertureStrip built from runsFromLabels (the LiveFit renderResult path)", () => {
  it("draws one rect per merged run from a small labels array", () => {
    const labels = [1, 1, 0, 2, 2, 2];
    const runs = runsFromLabels(labels, 6);
    const {container} = render(
      createElement(ApertureStrip, {
        bands: [{label: "Your browser's fit", runs}],
        description: "A small live re-fit, drawn from its raw labels array.",
        fringes: 2,
        title: "Your browser's readout at 3 counters",
        uMax: 6
      })
    );
    expect(runs).toHaveLength(3);
    expect(container.querySelectorAll(".aperture-strip__run")).toHaveLength(3);
    expect(screen.getByRole("img", {name: "Your browser's readout at 3 counters"})).toBeInTheDocument();
  });
});
