import {render, screen} from "@testing-library/react";
import {createElement} from "react";
import {describe, expect, it} from "vitest";

import {CONTRACT_ROWS, ProblemContract} from "../src/components/ProblemContract";

describe("ProblemContract", () => {
  it("renders every contract row, in the shared order, as a definition list", () => {
    const props = Object.fromEntries(CONTRACT_ROWS.map(({key}) => [key, `value of ${key}`])) as unknown as Parameters<typeof ProblemContract>[0];
    render(createElement(ProblemContract, props));
    const terms = screen.getAllByRole("term").map((node) => node.textContent);
    expect(terms).toEqual(CONTRACT_ROWS.map(({label}) => label));
    for (const {key} of CONTRACT_ROWS) {
      expect(screen.getByText(`value of ${key}`)).toBeInTheDocument();
    }
    expect(screen.getByLabelText("Problem contract").tagName).toBe("DL");
  });
});
