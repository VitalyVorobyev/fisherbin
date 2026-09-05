import {render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {MichelsonBench} from "../src/components/MichelsonBench";

describe("MichelsonBench", () => {
  it("gives the schematic an accessible name built from its title and description", () => {
    render(createElement(MichelsonBench, {caption: "The bench."}));
    expect(screen.getByRole("img", {name: /^Michelson interferometer bench/})).toBeInTheDocument();
  });

  it("draws the default six detector segments", () => {
    const {container} = render(createElement(MichelsonBench, {caption: "The bench."}));
    expect(container.querySelectorAll("[data-testid='bench-segment']")).toHaveLength(6);
  });

  it("draws exactly `segments` detector segments when overridden", () => {
    const {container} = render(createElement(MichelsonBench, {caption: "The bench.", segments: 10}));
    expect(container.querySelectorAll("[data-testid='bench-segment']")).toHaveLength(10);
  });

  it("renders the caption", () => {
    render(createElement(MichelsonBench, {caption: "A schematic of the bench."}));
    expect(screen.getByText("A schematic of the bench.")).toBeInTheDocument();
  });
});
