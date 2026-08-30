/**
 * The browser-local score-file reader, tested against files NumPy actually
 * wrote.
 *
 * Hand-constructed bytes would only prove the parser agrees with my reading of
 * the format. The fixtures in `tests/fixtures/` come from `numpy.save`, so a
 * change in either the format or the parser shows up here.
 */

import {readFileSync} from "node:fs";
import {join} from "node:path";

import {describe, expect, it} from "vitest";

import {parseScoreFile} from "../src/lab/parseScoreFile";

const FIXTURES = join(__dirname, "fixtures");
const expected = JSON.parse(readFileSync(join(FIXTURES, "expected.json"), "utf8")) as {
  full: number[][];
  scores: number[][];
  weights: number[];
};

function fixture(name: string): File {
  const bytes = readFileSync(join(FIXTURES, name));
  return new File([new Uint8Array(bytes)], name);
}

function round(rows: number[][], digits = 5): number[][] {
  return rows.map((row) => row.map((value) => Number(value.toFixed(digits))));
}

describe("npy", () => {
  it.each([
    ["scores-f8.npy", 6],
    ["scores-f4.npy", 4],
    ["scores-fortran.npy", 6],
  ])("reads %s written by numpy.save", async (name, digits) => {
    const table = await parseScoreFile(fixture(name));
    expect(table.scores).toHaveLength(6);
    expect(round(table.scores, digits)).toEqual(round(expected.full, digits));
    // No header row in the format, so no names to recover.
    expect(table.schema).toBeUndefined();
    expect(table.weights.every((weight) => weight === 1)).toBe(true);
  });

  it("refuses an array that is not a table", async () => {
    await expect(parseScoreFile(fixture("scores-1d.npy"))).rejects.toThrow(/two-dimensional/);
  });

  it("refuses a pickled object array rather than interpreting it", async () => {
    // Loading one would mean executing whatever it contains.
    await expect(parseScoreFile(fixture("scores-object.npy"))).rejects.toThrow(/Python objects/);
  });

  it("refuses a file that is not an npy at all", async () => {
    await expect(parseScoreFile(new File([new Uint8Array([1, 2, 3])], "x.npy"))).rejects.toThrow(/not a NumPy/);
  });
});

describe("csv", () => {
  it("recovers column names and treats a weight column as the measure", async () => {
    const table = await parseScoreFile(fixture("scores-with-header.csv"));
    expect(table.schema).toEqual(["s_T", "s_B"]);
    expect(round(table.scores)).toEqual(round(expected.scores));
    expect(round([table.weights])).toEqual(round([expected.weights]));
  });

  it("detects a missing header instead of eating the first data row", async () => {
    const table = await parseScoreFile(fixture("scores-plain.csv"));
    expect(table.schema).toBeUndefined();
    expect(table.scores).toHaveLength(6);
    expect(round(table.scores)).toEqual(round(expected.scores));
  });

  it("names the row that could not be read", async () => {
    const file = new File(["a,b\n1,2\n3,oops\n"], "bad.csv");
    await expect(parseScoreFile(file)).rejects.toThrow(/Row 3 .*"oops"/);
  });

  it("refuses a table wider than the browser envelope", async () => {
    const header = Array.from({length: 8}, (_, index) => `s${String(index)}`).join(",");
    const row = Array.from({length: 8}, () => "1").join(",");
    await expect(parseScoreFile(new File([`${header}\n${row}\n`], "wide.csv"))).rejects.toThrow(/up to 6/);
  });

  it("refuses a table with no positive weight", async () => {
    await expect(parseScoreFile(new File(["s,weight\n1,0\n2,0\n"], "zero.csv"))).rejects.toThrow(/positive/);
  });
});

describe("unsupported formats", () => {
  it("explains what to do with an npz rather than failing obscurely", async () => {
    await expect(parseScoreFile(new File([new Uint8Array([1])], "bundle.npz"))).rejects.toThrow(/single `.npy`/);
  });

  it("names the formats it accepts", async () => {
    await expect(parseScoreFile(new File([new Uint8Array([1])], "data.parquet"))).rejects.toThrow(/`.csv`, `.tsv` or `.npy`/);
  });
});
