/**
 * Read a score table from a file the reader chose, entirely in this tab.
 *
 * There is no server to upload to: the portal is a static site and the only
 * runtime is Pyodide in a worker. That is a privacy property worth stating in
 * the interface, and it is also why the parsing lives here rather than being
 * posted somewhere that could do it more comfortably.
 *
 * CSV and `.npy` only. `.npz` is a ZIP container and would need a real ZIP
 * reader for one convenience; a user with an `.npz` can save one array out.
 */

import {LAB_LIMITS} from "./protocol";

export interface ParsedScoreTable {
  /** Column names, from a CSV header when one is present. */
  schema: string[] | undefined;
  scores: number[][];
  weights: number[];
}

/** Column names that mean "measure", not "score dimension". */
const WEIGHT_COLUMNS = ["weight", "weights", "w"];

export async function parseScoreFile(file: File): Promise<ParsedScoreTable> {
  const name = file.name.toLowerCase();
  if (name.endsWith(".npy")) return parseNpy(await file.arrayBuffer());
  if (name.endsWith(".csv") || name.endsWith(".tsv") || name.endsWith(".txt")) {
    return parseDelimited(await file.text(), name.endsWith(".tsv") ? "\t" : ",");
  }
  if (name.endsWith(".npz")) {
    throw new Error("`.npz` is an archive of arrays. Save the score table as a single `.npy`, or export it as CSV.");
  }
  throw new Error("Choose a `.csv`, `.tsv` or `.npy` file.");
}

function finish(rows: number[][], header: string[] | undefined, weightColumn: number | null): ParsedScoreTable {
  if (rows.length === 0) throw new Error("The file contains no data rows.");
  if (rows.length > LAB_LIMITS.maxRows) {
    throw new Error(`The file has ${rows.length.toLocaleString()} rows; browser runs are limited to ${LAB_LIMITS.maxRows.toLocaleString()}.`);
  }
  const width = rows[0]?.length ?? 0;
  if (rows.some((row) => row.length !== width)) throw new Error("Every row must have the same number of columns.");

  const weights = weightColumn === null ? rows.map(() => 1) : rows.map((row) => row[weightColumn] ?? 0);
  const scores = rows.map((row) => row.filter((_, index) => index !== weightColumn));
  const schema = header?.filter((_, index) => index !== weightColumn);

  const dimensions = scores[0]?.length ?? 0;
  if (dimensions < 1) throw new Error("The file has no score columns.");
  if (dimensions > LAB_LIMITS.maxDimensions) {
    throw new Error(`The file has ${String(dimensions)} score columns; browser runs support up to ${String(LAB_LIMITS.maxDimensions)}.`);
  }
  if (scores.some((row) => row.some((value) => !Number.isFinite(value)))) {
    throw new Error("Every score value must be a finite number.");
  }
  if (!weights.some((weight) => weight > 0)) throw new Error("At least one weight must be positive.");
  return {schema, scores, weights};
}

function parseDelimited(text: string, delimiter: string): ParsedScoreTable {
  const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0);
  if (lines.length === 0) throw new Error("The file is empty.");
  const cells = lines.map((line) => line.split(delimiter).map((cell) => cell.trim()));

  // A header is present when the first row is not numeric. Detecting it beats
  // asking, and a mis-detection is visible immediately in the column names.
  const first = cells[0] ?? [];
  const hasHeader = first.some((cell) => cell.length > 0 && !Number.isFinite(Number(cell)));
  const header = hasHeader ? first.map((cell) => cell.replace(/^["']|["']$/g, "")) : undefined;
  const body = hasHeader ? cells.slice(1) : cells;

  const weightColumn = header?.findIndex((name) => WEIGHT_COLUMNS.includes(name.toLowerCase())) ?? -1;
  const rows = body.map((row, index) =>
    row.map((cell) => {
      const value = Number(cell);
      if (!Number.isFinite(value)) {
        throw new Error(`Row ${String(index + 1 + (hasHeader ? 1 : 0))} contains a non-numeric value: "${cell}".`);
      }
      return value;
    })
  );
  return finish(rows, header, weightColumn >= 0 ? weightColumn : null);
}

/**
 * Read a NumPy `.npy` array.
 *
 * The format is a short ASCII header describing dtype, order and shape,
 * followed by raw little-endian data. Only the numeric dtypes a score table can
 * plausibly have are accepted; anything else -- including a pickled object
 * array -- is refused by name rather than partially interpreted.
 */
function parseNpy(buffer: ArrayBuffer): ParsedScoreTable {
  const bytes = new Uint8Array(buffer);
  const magic = String.fromCharCode(...bytes.subarray(1, 6));
  if (bytes[0] !== 0x93 || magic !== "NUMPY") throw new Error("That file is not a NumPy `.npy` array.");
  const major = bytes[6] ?? 0;
  const headerLengthBytes = major === 1 ? 2 : 4;
  const view = new DataView(buffer);
  const headerLength =
    major === 1 ? view.getUint16(8, true) : view.getUint32(8, true);
  const headerStart = 8 + headerLengthBytes;
  const header = new TextDecoder().decode(bytes.subarray(headerStart, headerStart + headerLength));

  const descr = /'descr':\s*'([^']+)'/.exec(header)?.[1];
  const fortran = /'fortran_order':\s*(True|False)/.exec(header)?.[1] === "True";
  const shapeText = /'shape':\s*\(([^)]*)\)/.exec(header)?.[1] ?? "";
  const shape = shapeText.split(",").map((part) => part.trim()).filter((part) => part.length > 0).map(Number);

  if (descr === undefined) throw new Error("The `.npy` header is unreadable.");
  if (descr.startsWith("|O") || descr.includes("O")) throw new Error("That `.npy` holds Python objects, not numbers.");
  if (shape.length !== 2) throw new Error(`A score table must be two-dimensional; this array has ${String(shape.length)} dimensions.`);

  const [rowCount = 0, columnCount = 0] = shape;
  const dataStart = headerStart + headerLength;
  const read = numpyReader(descr, buffer, dataStart);

  const rows: number[][] = [];
  for (let r = 0; r < rowCount; r += 1) {
    const row: number[] = [];
    for (let c = 0; c < columnCount; c += 1) {
      row.push(read(fortran ? c * rowCount + r : r * columnCount + c));
    }
    rows.push(row);
  }
  return finish(rows, undefined, null);
}

function numpyReader(descr: string, buffer: ArrayBuffer, offset: number): (index: number) => number {
  const littleEndian = !descr.startsWith(">");
  const kind = descr.replace(/^[<>|=]/, "");
  const view = new DataView(buffer, offset);
  switch (kind) {
    case "f8":
      return (index) => view.getFloat64(index * 8, littleEndian);
    case "f4":
      return (index) => view.getFloat32(index * 4, littleEndian);
    case "i8":
      return (index) => Number(view.getBigInt64(index * 8, littleEndian));
    case "i4":
      return (index) => view.getInt32(index * 4, littleEndian);
    case "i2":
      return (index) => view.getInt16(index * 2, littleEndian);
    case "u4":
      return (index) => view.getUint32(index * 4, littleEndian);
    default:
      throw new Error(`Unsupported \`.npy\` dtype "${descr}". Save the table as float64, float32 or a standard integer type.`);
  }
}
