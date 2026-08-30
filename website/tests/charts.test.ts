import {describe, expect, it} from "vitest";

import {extent, formatTick, linearScale, niceTicks, populationColor} from "../src/components/charts/scale";

describe("linearScale", () => {
  it("maps the domain onto the range", () => {
    const scale = linearScale([0, 10], [100, 200]);
    expect(scale(0)).toBe(100);
    expect(scale(10)).toBe(200);
    expect(scale(5)).toBe(150);
  });

  it("centres a degenerate domain instead of dividing by zero", () => {
    // A single-valued series is real -- one bin budget, one measurement -- and
    // must not render as NaN.
    expect(linearScale([4, 4], [0, 100])(4)).toBe(50);
  });
});

describe("niceTicks", () => {
  it("uses round 1/2/5 steps rather than hitting the requested count exactly", () => {
    // A step of 0.25 would satisfy the count; 0.2 is the round step, and a
    // reader compares against a round gridline far more easily.
    expect(niceTicks(0, 1, 4)).toEqual([0, 0.2, 0.4, 0.6, 0.8, 1]);
    expect(niceTicks(0, 30, 6)).toEqual([0, 5, 10, 15, 20, 25, 30]);
  });

  it("does not accumulate floating-point noise across ticks", () => {
    // Repeated addition of 0.1 produces 0.30000000000000004 without rounding.
    for (const tick of niceTicks(0, 1, 10)) {
      expect(String(tick).length).toBeLessThan(6);
    }
  });

  it("degrades to a single tick rather than looping forever", () => {
    expect(niceTicks(2, 2, 5)).toEqual([2]);
    expect(niceTicks(Number.NaN, 1, 5)).toEqual([Number.NaN]);
  });
});

describe("extent", () => {
  it("ignores non-finite entries", () => {
    expect(extent([1, Number.NaN, 5, Number.POSITIVE_INFINITY])).toEqual([1, 5]);
  });

  it("returns a usable range when nothing is finite", () => {
    expect(extent([Number.NaN])).toEqual([0, 1]);
  });

  it("pads a constant series so it has a drawable height", () => {
    expect(extent([3, 3, 3])).toEqual([2.5, 3.5]);
  });
});

describe("formatTick", () => {
  it("prints whole numbers whole", () => {
    expect(formatTick(8)).toBe("8");
    expect(formatTick(30)).toBe("30");
    expect(formatTick(0)).toBe("0");
  });

  it("keeps small values distinguishable", () => {
    expect(formatTick(0.002)).toBe("0.0020");
    expect(formatTick(-1.25)).toBe("-1.3");
  });
});

describe("populationColor", () => {
  it("is stable per index so a population keeps its colour across panels", () => {
    expect(populationColor(0)).toBe(populationColor(0));
    expect(populationColor(0)).not.toBe(populationColor(1));
  });

  it("wraps rather than returning undefined", () => {
    expect(typeof populationColor(99)).toBe("string");
  });
});
