import {loadGetStartedScoreTable} from "../data/walkthroughScores";
import {firstFitRetention} from "../lib/snippets";
import {LiveFit} from "./liveFit/LiveFit";
import type {LiveFitProblem} from "./liveFit/types";

/**
 * A `LiveFit` demo beside `/get-started`'s "first-fit" snippet.
 *
 * The committed retention comes from `website/src/lib/snippets.ts`
 * (`firstFitRetention`), already bundled with the page -- the same
 * `partition.train_report.geometric_mean_retention` the snippet's own
 * captured stdout prints as "D-efficiency", read structurally rather than
 * reparsed from that text. The (larger) score table is fetched only once
 * the reader activates the demo, from
 * `website/static/walkthrough-scores/get-started.json`
 * (`loadGetStartedScoreTable`), which also carries the exact bin count,
 * seed and solver the "first-fit" cell ran with, so a browser rerun cannot
 * silently drift from it.
 */
export function GetStartedFirstFitLiveFit(): React.JSX.Element {
  const problem = async (): Promise<LiveFitProblem> => {
    const table = await loadGetStartedScoreTable();
    return {
      datasetId: "get-started-first-fit",
      nBins: table.nBins,
      schema: table.schema,
      scores: table.scores,
      seed: table.seed,
      solver: table.solver,
      weights: table.weights
    };
  };

  return (
    <LiveFit
      id="get-started-first-fit"
      activationLabel="Refit this table in your browser"
      activationHint="Fetches the same 1,200 rows this page fits, then runs the same D-optimal exchange solver on the NumPy backend inside your browser."
      committedLabel="D-efficiency printed by get_started_program.py"
      committedRetention={firstFitRetention()}
      formatRetention={(value) => value.toFixed(4)}
      liveLabel="Your browser's D-efficiency, same table, same bins, same seed"
      problem={problem}
    />
  );
}
