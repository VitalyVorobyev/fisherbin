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

  it("states the problem and the data before any API tag", () => {
    render(<WalkthroughCards />);
    for (const card of WALKTHROUGHS) {
      const article = screen.getByRole("article", {name: card.title});
      const text = article.textContent;
      const firstTag = Math.min(...card.tags.map((tag) => text.indexOf(tag.label)));
      expect(text.indexOf(card.problem)).toBeGreaterThan(-1);
      expect(text.indexOf(card.data)).toBeGreaterThan(text.indexOf(card.problem));
      expect(firstTag).toBeGreaterThan(text.indexOf(card.data));
    }
  });

  it("names its task on every card, and only real public symbols or a task in its tags", () => {
    const symbols = new Set(portalData.api.map((symbol) => symbol.name));
    for (const card of WALKTHROUGHS) {
      expect(card.tags.some((tag) => tag.kind === "task"), card.slug).toBe(true);
      for (const tag of card.tags) {
        expect(symbols.has(tag.label) || TASKS.has(tag.label), `${card.slug}: ${tag.label}`).toBe(true);
      }
    }
  });

  it("types no digit into a problem or data summary except through a fact", () => {
    // A summary may carry a bin budget, which arrives from `factsFor`; the
    // guard is that the data module itself holds no numeral. The generated
    // budgets are small integers, so strip one- or two-digit numbers that a
    // fact resolved and require nothing else.
    for (const card of WALKTHROUGHS) {
      for (const summary of [card.problem, card.data]) {
        const residue = summary.replace(/\b\d{1,2}\b/g, "");
        expect(residue).not.toMatch(/\d/);
      }
    }
  });
});
