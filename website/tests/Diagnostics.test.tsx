import {render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {Diagnostics} from "../src/components/Diagnostics";
import type {DiagnosticsItem} from "../src/components/Diagnostics";

const items: DiagnosticsItem[] = [
  {label: "Retained information", meaning: "Fraction of Fisher information kept after binning.", value: "94.2%"},
  {label: "Bins used", meaning: "Hard labels the fitted partition assigns.", value: "6"}
];

describe("Diagnostics", () => {
  it("renders the label, value and meaning for every item", () => {
    render(createElement(Diagnostics, {items}));
    for (const item of items) {
      expect(screen.getByText(item.label)).toBeInTheDocument();
      expect(screen.getByText(item.value)).toBeInTheDocument();
      expect(screen.getByText(item.meaning)).toBeInTheDocument();
    }
  });

  it("renders an optional caption", () => {
    render(createElement(Diagnostics, {caption: "From the HEP classifier study.", items}));
    expect(screen.getByText("From the HEP classifier study.")).toBeInTheDocument();
  });
});
