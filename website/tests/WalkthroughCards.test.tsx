import {render, screen, within} from "@testing-library/react";
import {describe, expect, it} from "vitest";

import {WalkthroughCards} from "../src/components/WalkthroughCards";
import {portalData} from "../src/data/portal";
import {WALKTHROUGHS} from "../src/data/walkthroughs";

const TASKS = new Set(["optimize_partition", "fit_quantizer"]);

describe("WalkthroughCards", () => {
  it("renders one card per walkthrough, each linking to its page", () => {
    render(<WalkthroughCards />);
    for (const card of WALKTHROUGHS) {
      const article = screen.getByRole("article", {name: card.title});
      expect(within(article).getByRole("link", {name: card.title})).toHaveAttribute("href", card.href);
    }
    expect(screen.getAllByRole("article")).toHaveLength(WALKTHROUGHS.length);
  });

  it("names only real public symbols or one of the two tasks in its API tags", () => {
    const symbols = new Set(portalData.api.map((symbol) => symbol.name));
    for (const card of WALKTHROUGHS) {
      for (const tag of card.tags) {
        if (tag.kind === "data") continue;
        expect(symbols.has(tag.label) || TASKS.has(tag.label), `${card.slug}: ${tag.label}`).toBe(true);
      }
    }
  });

  it("types no digit into a summary except through a fact", () => {
    // A summary may carry a bin budget, which arrives from `factsFor`; the
    // guard is that the data module itself holds no numeral. The generated
    // budgets are small integers, so strip one- or two-digit numbers that a
    // fact resolved and require nothing else.
    for (const card of WALKTHROUGHS) {
      const residue = card.summary.replace(/\b\d{1,2}\b/g, "");
      expect(residue).not.toMatch(/\d/);
    }
  });
});
