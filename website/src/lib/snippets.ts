import rawData from "../generated/snippet-outputs.json";

/**
 * One cell of the `/get-started` page's single-sourced program.
 *
 * `code` is the cell's verbatim source (stripped of its `# %% cell: <id>`
 * marker and surrounding blank lines) and `stdout` is exactly what running
 * that cell printed, captured by `generate_snippets.py`. Pages never format
 * or fabricate either string themselves -- both are the generator's own
 * record of one real run. See `website/scripts/get_started_program.py` for
 * the source program and `website/scripts/generate_snippets.py` for how the
 * two are captured.
 */
export interface SnippetCell {
  code: string;
  order: number;
  stdout: string;
}

/** The pinned runtime `get_started_program.py` ran under. */
export interface SnippetExecution {
  backend: string;
  precision: string;
  seed: number;
}

/** The `/get-started` first-fit cell's own committed result. */
export interface FirstFitSummary {
  /** `partition.train_report.geometric_mean_retention`, read from the same run. */
  retention: number;
}

interface SnippetData {
  cells: Record<string, SnippetCell | undefined>;
  execution: SnippetExecution;
  firstFit: FirstFitSummary;
  schemaVersion: number;
}

const snippetData = rawData as SnippetData;

/**
 * Thrown by `snippet`/`snippetExecution` when a cell id is not in the
 * generated data.
 *
 * MDX executes during the Docusaurus build, so this turns a typo in a cell
 * id into a build failure rather than an `undefined` reaching a published
 * page. Softening this to a fallback would defeat the entire point of
 * single-sourcing the page's snippets -- do not.
 */
export class SnippetError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "SnippetError";
  }
}

/**
 * Look up one cell by id, throwing a `SnippetError` naming it when it is
 * missing from the generated data.
 */
export function snippet(id: string): SnippetCell {
  const cell = snippetData.cells[id];
  if (cell === undefined) {
    throw new SnippetError(`No generated snippet cell exists for id "${id}".`);
  }
  return cell;
}

/** The runtime provenance every generated cell was captured under. */
export function snippetExecution(): SnippetExecution {
  return snippetData.execution;
}

/**
 * The `/get-started` first-fit cell's committed retention.
 *
 * Read from the same executed `partition` the cell's own captured stdout
 * prints `geometric_mean_retention` from
 * (`website/scripts/generate_snippets.py`) -- not reparsed from that text --
 * so `GetStartedFirstFitLiveFit` can show it before the reader ever clicks
 * anything, with no fetch of the (larger) score table required first.
 */
export function firstFitRetention(): number {
  return snippetData.firstFit.retention;
}
