import {render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {ScoreSpace} from "../src/components/ScoreSpace";

describe("ScoreSpace", () => {
  it("renders generated scientific evidence instead of placeholder metrics", () => {
    render(createElement(ScoreSpace, {compact: true, controlledBins: 4}));
    expect(screen.getByRole("img", {name: "Score-space partition with 4 bins"})).toBeInTheDocument();
    expect(screen.getByText("D-efficiency").nextSibling?.textContent).toMatch(/%/);
    expect(screen.getByText("hard bins").nextSibling).toHaveTextContent("4");
  });
});
