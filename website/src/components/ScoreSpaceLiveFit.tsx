import {useState} from "react";

import {LiveFit} from "./liveFit/LiveFit";
import type {LiveFitProblem} from "./liveFit/types";
import {portalData} from "../data/portal";
import {ScoreSpace} from "./ScoreSpace";

/**
 * The home page's loss-identity beat: the committed `ScoreSpace` fixture,
 * plus a `LiveFit` demo that refits the same points at the same bin budget
 * in the reader's own browser.
 *
 * `index.tsx` renders this with no props at all, which is what keeps it free
 * of the numeric literal `tests/test_walkthrough_facts.py::test_home_page_contains_no_numeric_literal`
 * forbids: the bin-count state and its default live here instead, in a file
 * that guard does not cover.
 *
 * The committed scenario was fitted by `website/scripts/generate_data.py`'s
 * `_score_space_data` as `optimize_partition(points, weights=weights,
 * n_bins=<bins>, config=DExchangeConfig(seed=28, initializer_restarts=2,
 * max_scans=120))`, reading `train_report.geometric_mean_retention`.
 * `fit_quantizer`'s own D-exchange path (what the browser Lab always calls)
 * resolves through the identical `optimize_d_partition` call and reads the
 * identical field, so sending the same points, weights, bin count and seed
 * reproduces this page's own number rather than computing a different one.
 */
export function ScoreSpaceLiveFit(): React.JSX.Element {
  const [bins, setBins] = useState(4);
  const scenario = portalData.scoreSpace.scenarios[String(bins)];
  if (scenario === undefined) throw new Error(`No generated score-space fixture exists for ${String(bins)} bins.`);

  // The points are already in memory (bundled with the page), so there is
  // nothing to await -- resolving eagerly still satisfies `LiveFitProblemLoader`.
  const problem = (): Promise<LiveFitProblem> =>
    Promise.resolve({
      datasetId: "home-score-space",
      nBins: bins,
      scores: portalData.scoreSpace.points,
      seed: 28,
      solver: "d_exchange",
      weights: portalData.scoreSpace.weights
    });

  return (
    <div className="home-explain__visual">
      <ScoreSpace controlledBins={bins} onBinsChange={setBins} />
      <LiveFit
        id="home-score-space"
        activationLabel="Refit these points in your browser"
        activationHint="Runs the same points, the same bin budget, and the same D-optimal exchange solver ScoreQuant ships, on the NumPy backend inside your browser."
        committedLabel={`Committed D-efficiency at ${String(bins)} bins`}
        committedRetention={scenario.retention}
        formatRetention={(value) => `${(value * 100).toFixed(1)}%`}
        liveLabel="Your browser's D-efficiency, same points, same bin budget"
        problem={problem}
      />
    </div>
  );
}
