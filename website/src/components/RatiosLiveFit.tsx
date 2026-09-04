import {loadWalkthroughScoreTable} from "../data/walkthroughScores";
import {factValue} from "../lib/facts";
import {LiveFit} from "./liveFit/LiveFit";
import type {LiveFitProblem} from "./liveFit/types";

/**
 * A `LiveFit` demo on `/walkthroughs/ratios`, beside the classifier ladder's
 * Diagnostics table.
 *
 * This intentionally does *not* claim to reproduce the page's "reported at
 * 300 events per class" number bit for bit. That number
 * (`factValue("ratios", "largeSurrogate")`) is
 * `quantizer.evaluate_scores(estimated_test_scores).geometric_mean_retention`
 * in the page's own snippet: the *frozen* rule from a partition fitted on a
 * separate training sample, evaluated on this held-out table. What this demo
 * runs is `fit_quantizer` on this exact held-out table directly -- the same
 * D-optimal exchange, same bin budget, but a *fresh* partition optimized on
 * the very points shown, not the training-fitted rule scored against them.
 * Both are genuine D-efficiencies of the same classifier-scored table at the
 * same bin budget, and empirically close (a fresh browser run measured
 * ~0.9727 against the committed 0.9700), but they are not the same
 * computation, so both are labelled for what they actually are rather than
 * implied to be identical.
 */
export function RatiosLiveFit(): React.JSX.Element {
  const problem = async (): Promise<LiveFitProblem> => {
    const table = await loadWalkthroughScoreTable("ratios");
    return {
      datasetId: "walkthroughs-ratios",
      nBins: 4,
      schema: table.schema,
      scores: table.scores,
      seed: 7,
      solver: "d_exchange",
      weights: table.weights
    };
  };

  return (
    <LiveFit
      id="walkthroughs-ratios"
      activationLabel="Fit this table fresh in your browser"
      activationHint={
        "Fetches the same 600-row classifier-scored table shown above and fits a new D-optimal " +
        "partition on it directly, at the same four-bin budget. This is a different computation " +
        "from the reported number: that one evaluates the frozen rule fitted on a separate " +
        "training sample, while this fits fresh on the table you can already see, so expect a " +
        "nearby but not identical value."
      }
      committedLabel="Reported held-out D-efficiency at 300 events/class (frozen training-fitted rule)"
      committedRetention={factValue("ratios", "largeSurrogate")}
      formatRetention={(value) => value.toFixed(4)}
      liveLabel="Your browser's own D-optimal fit on this exact table (a fresh partition, not the frozen rule)"
      problem={problem}
    />
  );
}
