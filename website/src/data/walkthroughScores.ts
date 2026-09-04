import {siteUrl} from "../lib/site";

/**
 * One walkthrough's deterministic score table, in exactly the shape
 * `ScoreTable` (`website/src/lab/useScoreTable.ts`) consumes.
 *
 * Written by `generate_walkthroughs.py`'s `write_walkthrough_score_tables`
 * to `website/static/walkthrough-scores/<slug>.json`; never edited by hand.
 */
export interface WalkthroughScoreTable {
  detail: string;
  label: string;
  schema: string[];
  scores: number[][];
  weights: number[];
}

/**
 * Fetch one walkthrough's committed score table on demand.
 *
 * Kept out of the bundle the same way `loadLabScores` keeps the FlowCyt table
 * out of it (`website/src/data/showcase.ts`): a `?job=` hand-off is the only
 * caller, so opening the Lab with no query fetches nothing extra.
 */
export async function loadWalkthroughScoreTable(
  slug: string,
  signal?: AbortSignal
): Promise<WalkthroughScoreTable> {
  const url = siteUrl(`walkthrough-scores/${slug}.json`);
  const response = await fetch(url, signal === undefined ? {} : {signal});
  if (!response.ok) {
    throw new Error(`The "${slug}" walkthrough score table is unavailable (${String(response.status)}).`);
  }
  return (await response.json()) as WalkthroughScoreTable;
}
