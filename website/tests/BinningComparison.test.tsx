import {render, screen, within} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {BinningComparison} from "../src/components/BinningComparison";
import type {BinningComparisonRow} from "../src/components/BinningComparison";

const rows: BinningComparisonRow[] = [
  {label: "Equal-width bins", text: "61.4%", value: 0.614},
  {label: "ScoreQuant D-optimal", isScoreQuant: true, text: "94.2%", value: 0.942},
  {label: "Unbinned classifier", isCeiling: true, text: "97.8%", value: 0.978}
];

describe("BinningComparison", () => {
  it("draws one bar per non-ceiling row and marks the ScoreQuant row", () => {
    const {container} = render(createElement(BinningComparison, {axisLabel: "retained information", rows}));
    const bars = container.querySelectorAll(".binning-comparison__bar");
    // The ceiling row is drawn as a reference line, not a competing bar.
    expect(bars).toHaveLength(2);
    expect(container.querySelectorAll(".binning-comparison__bar--scorequant")).toHaveLength(1);
  });

  it("gives the chart an accessible name naming the axis", () => {
    render(createElement(BinningComparison, {axisLabel: "retained information", rows}));
    expect(
      screen.getByRole("img", {name: "retained information, compared across 2 binning methods"})
    ).toBeInTheDocument();
  });

  it("carries a text alternative listing every row, including the ceiling", () => {
    render(createElement(BinningComparison, {axisLabel: "retained information", rows}));
    const table = screen.getByRole("table", {hidden: true});
    for (const row of rows) {
      expect(within(table).getByText(row.text)).toBeInTheDocument();
    }
  });
});
