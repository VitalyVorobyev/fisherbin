/**
 * Linear scale mathematics shared by every chart on the showcase.
 *
 * Deliberately not a charting library: the LCP budget and the strict
 * type-aware lint configuration both make a dependency expensive here, and
 * every chart this site draws needs the same twenty lines.
 */

export interface Scale {
  /** Map a data value to a pixel coordinate. */
  (value: number): number;
  domain: readonly [number, number];
  range: readonly [number, number];
  /** Evenly spaced, human-readable tick values covering the domain. */
  ticks: (count: number) => number[];
}

/** Build a linear scale, collapsing a degenerate domain rather than dividing by zero. */
export function linearScale(domain: readonly [number, number], range: readonly [number, number]): Scale {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const span = d1 - d0;
  const scale = ((value: number): number =>
    span === 0 ? (r0 + r1) / 2 : r0 + ((value - d0) / span) * (r1 - r0)) as Scale;
  scale.domain = domain;
  scale.range = range;
  scale.ticks = (count: number): number[] => niceTicks(d0, d1, count);
  return scale;
}

/**
 * Tick values at a 1/2/5 x 10^n step.
 *
 * Round steps matter more than an exact count: a reader compares bars against
 * the gridline, and "0.02" is comparable at a glance where "0.0183" is not.
 */
export function niceTicks(low: number, high: number, count: number): number[] {
  if (!Number.isFinite(low) || !Number.isFinite(high) || low === high) return [low];
  const rawStep = (high - low) / Math.max(1, count);
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  const normalized = rawStep / magnitude;
  const step = (normalized >= 5 ? 5 : normalized >= 2 ? 2 : 1) * magnitude;
  const first = Math.ceil(low / step) * step;
  const ticks: number[] = [];
  for (let value = first; value <= high + step / 1e6; value += step) {
    // Re-round each tick: repeated addition of a fractional step accumulates
    // representation error that shows up as "0.30000000000000004" on an axis.
    ticks.push(Number((Math.round(value / step) * step).toPrecision(12)));
  }
  return ticks;
}

/** Extent of a series, ignoring non-finite entries; `[0, 1]` when nothing is finite. */
export function extent(values: readonly number[]): [number, number] {
  let low = Number.POSITIVE_INFINITY;
  let high = Number.NEGATIVE_INFINITY;
  for (const value of values) {
    if (!Number.isFinite(value)) continue;
    if (value < low) low = value;
    if (value > high) high = value;
  }
  if (!Number.isFinite(low) || !Number.isFinite(high)) return [0, 1];
  return low === high ? [low - 0.5, high + 0.5] : [low, high];
}

/** Format an axis value compactly without losing the distinction between ticks. */
export function formatTick(value: number): string {
  const magnitude = Math.abs(value);
  if (value === 0) return "0";
  // A whole number prints whole: a bin count of "6.0" invites the reader to
  // wonder what a fractional bin would be.
  if (Number.isInteger(value) && magnitude < 1e5) return value.toFixed(0);
  if (magnitude >= 1000 || magnitude < 0.001) return value.toExponential(1).replace("e+", "e");
  if (magnitude >= 10) return value.toFixed(0);
  if (magnitude >= 1) return value.toFixed(1);
  return value.toFixed(magnitude < 0.01 ? 4 : 3);
}

/**
 * Population colours, fixed by index so the same cell type is the same colour
 * on every panel of the page. A reader learns the mapping once.
 */
export const POPULATION_COLORS = [
  "#2b77f3",
  "#20bfae",
  "#f0a84b",
  "#e8618c",
  "#8b5cf6",
  "#94a3b8",
] as const;

/** Colour for a population index, wrapping rather than returning undefined. */
export function populationColor(index: number): string {
  return POPULATION_COLORS[index % POPULATION_COLORS.length] ?? "#94a3b8";
}
