import rawData from "../generated/walkthrough-data.json";

/**
 * One number a walkthrough page is allowed to print, carrying its own
 * provenance.
 *
 * `value` is the raw value as it appears in the committed evidence file,
 * `text` is the generator's formatting of it (pages never format a value
 * themselves), and `source` is a repo-relative path plus a JSON Pointer into
 * the evidence that produced it. See `docs/programme/S08-the-four-walkthroughs.md`,
 * decision D2, for the full contract this type is part of.
 *
 * `value` is `number | string` because some facts are not numbers: a
 * provenance kind, a licence identifier, the text of a theorem-backed
 * refusal. Those still carry a pointer into evidence and are still checked
 * against it, so they belong here rather than in hand-written prose.
 */
export interface WalkthroughFact {
  source: string;
  text: string;
  value: number | string;
}

interface WalkthroughData {
  pages: Record<string, Record<string, WalkthroughFact> | undefined>;
  schemaVersion: number;
}

const walkthroughData = rawData as WalkthroughData;

/**
 * Thrown by `factsFor`/`factValue` when a page or a fact key is not in the
 * generated data.
 *
 * MDX executes during the Docusaurus build, so this turns a typo in a fact
 * key into a build failure rather than an `undefined` reaching a published
 * page. Softening this to a fallback would defeat the entire point of the
 * fact contract -- do not.
 */
export class WalkthroughFactError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "WalkthroughFactError";
  }
}

function lookupFact(page: string, key: string): WalkthroughFact {
  const pageFacts = walkthroughData.pages[page];
  if (pageFacts === undefined) {
    throw new WalkthroughFactError(`No generated walkthrough facts exist for page "${page}".`);
  }
  const fact = pageFacts[key];
  if (fact === undefined) {
    throw new WalkthroughFactError(`Walkthrough page "${page}" has no fact "${key}".`);
  }
  return fact;
}

/**
 * Build a fact lookup scoped to one walkthrough page.
 *
 * The returned function returns the generator's formatted `text` for `key`,
 * or throws a `WalkthroughFactError` naming both the page and the key. A
 * walkthrough page should call this once per page and never import
 * `walkthrough-data.json` directly.
 */
export function factsFor(page: string): (key: string) => string {
  return (key: string): string => lookupFact(page, key).text;
}

/**
 * The raw numeric value behind a fact, for the rare case a component needs it.
 *
 * `BinningComparison` needs real numbers to size its bars, while prose only
 * ever needs `text`. Throws if the fact is one of the string-valued ones, so a
 * chart cannot silently size a bar from a provenance kind.
 */
export function factValue(page: string, key: string): number {
  const fact = lookupFact(page, key);
  if (typeof fact.value !== "number") {
    throw new WalkthroughFactError(
      `Walkthrough fact "${page}.${key}" is not numeric (${JSON.stringify(fact.value)}).`
    );
  }
  return fact.value;
}
