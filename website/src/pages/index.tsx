import Link from "@docusaurus/Link";
import Layout from "@theme/Layout";

import {ScoreSpaceLiveFit} from "../components/ScoreSpaceLiveFit";
import {factsFor} from "../lib/facts";

/**
 * Every number this page displays resolves from committed evidence through the
 * fact contract; the page holds no numeric literal of its own, which
 * `tests/test_walkthrough_facts.py` enforces.
 */
const fact = factsFor("home");

export default function Home(): React.JSX.Element {
  return (
    <Layout
      title="ScoreQuant"
      description="Choose bins that keep the information your parameters depend on, and measure what the binning cost."
    >
      <section className="home-section section-wrap">
        <div className="home-opening">
          <div className="home-lede">
            <h1>Some analyses have to bin.</h1>
            <p>
              A great deal of statistical practice ends in counts. A template fit needs the expected
              number of events per category for each model component. A trigger has to route an
              event into one of a few tiers. A cytometry protocol reports the fraction of cells in
              named gates. A binned likelihood needs bins. In every one of these a continuous
              measurement is
              replaced by an integer label, and that step is irreversible.
            </p>
            <p>
              The bins are usually chosen for readability: equal width, equal population, a
              threshold on one discriminant, or whatever the previous analysis used. Those are
              choices about presentation. They are also, silently, choices about how much parameter
              sensitivity survives — and nothing in the usual workflow reports the size of what was
              given up.
            </p>
          </div>
          <aside className="home-identity" aria-label="What ScoreQuant is">
            <p className="home-identity__what">
              <b>ScoreQuant</b> is a Python library for choosing those bins so they keep the Fisher
              information your parameters depend on, and for measuring what the binning cost.
            </p>
            <p className="home-identity__install">
              <code>uv add scorequant</code>
            </p>
            <p className="home-identity__runtime">
              Runs on JAX by default, and on NumPy with no accelerator and no compiler.
            </p>
          </aside>
        </div>
      </section>

      <section className="home-section section-wrap section-rule">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Measured, not asserted</span>
            <h2>How much is given up</h2>
          </div>
          <p>
            Bone-marrow flow cytometry, six cell populations, thirty patients. One number: the
            geometric-mean retention computed from classifier-estimated scores for the population
            fractions, evaluated on held-out patients at a budget of {fact("bins")} bins.
          </p>
        </div>
        <dl className="home-measure">
          <div className="measure-row">
            <dt>Weighted k-means on the standardized markers</dt>
            <dd>{fact("naiveBestEfficiency")}</dd>
          </div>
          <div className="measure-row">
            <dt>Equal-frequency bins along the leading score direction</dt>
            <dd>{fact("naiveScoreProjectionEfficiency")}</dd>
          </div>
          <div className="measure-row">
            <dt>Equal-width grid on the first two principal components</dt>
            <dd>{fact("naiveGridEfficiency")}</dd>
          </div>
          <div className="measure-row measure-row--result">
            <dt>ScoreQuant, same data, same bin budget</dt>
            <dd>{fact("scorequantEfficiency")}</dd>
          </div>
        </dl>
        <p className="provenance-note">
          <span aria-hidden="true">◇</span>
          <span>
            The comparison is quoted against the strongest of the three standard rules, not the
            weakest. A headline measured against the worst available baseline reports the
            baseline&rsquo;s difficulty rather than the method.{" "}
            <Link to="/walkthroughs/flowcyt">How this surrogate was evaluated →</Link>
          </span>
        </p>
      </section>

      <section className="home-section section-wrap section-rule">
        <div className="section-heading">
          <div>
            <span className="eyebrow">The mechanism</span>
            <h2>The loss has a closed form</h2>
          </div>
          <p>
            Binning can only lose information, never create it. That is an identity rather than a
            claim, and it says exactly where the loss goes.
          </p>
        </div>
        <div className="home-explain">
          <div>
            <p>
              Write each event&rsquo;s local sensitivity as its <em>score</em>: the gradient of its
              log-likelihood with respect to the parameters, at a reference point. The information
              in the unbinned sample is the second moment of the score. A hard rule that sends each
              event to one of K labels keeps only the between-cell part, and the difference is the
              within-cell scatter of the score.
            </p>
            <div className="math-display">
              I<sub>∞</sub> − I<sub>q</sub> = Σ<sub>b</sub> E[ 1{"{"}q=b{"}"} (s − μ
              <sub>b</sub>)(s − μ<sub>b</sub>)<sup>T</sup> ] ⪰ 0
            </div>
            <p>
              Two things follow. Refining a partition can only help. And the loss is governed
              entirely by how the <em>score</em> varies inside each cell, not by how the observation
              does — a bin that is narrow in the measurement but flat in s costs almost nothing,
              while a bin that looks perfectly reasonable on a histogram but straddles a region
              where s swings costs a great deal. Equal-width and equal-population rules know nothing
              about s, which is why their loss is arbitrary with respect to the quantity anyone
              actually cares about.
            </p>
            <p>
              ScoreQuant optimizes in score space, where that identity is written. Score space also
              has one coordinate per parameter however many measurement variables an event carries,
              so a forty-channel measurement feeding a two-parameter fit is a two-dimensional
              problem.
            </p>
          </div>
          <ScoreSpaceLiveFit />
        </div>
      </section>

      <section className="home-section section-wrap section-rule">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Your decision, not a preference</span>
            <h2>Will you ever label an event that is not in this table?</h2>
          </div>
        </div>
        <div className="home-choice">
          <article className="choice">
            <h3>No — the rows are the final object</h3>
            <p>
              <code>optimize_partition</code> solves a finite assignment problem and hands back a
              label vector for those rows. A frozen Monte Carlo template set, a fixed calibration
              sample, a study of how much a given cell budget can retain.
            </p>
            <Link className="plain-link" to="/walkthroughs/flowcyt">
              A worked fixed-sample study →
            </Link>
          </article>
          <article className="choice">
            <h3>Yes — future events must be labeled the same way</h3>
            <p>
              <code>fit_quantizer</code> chooses a geometric rule on score space and hands back
              something <code>predict_scores</code> can apply anywhere. A trigger, a gate applied to
              new runs, a categorization shipped with an analysis.
            </p>
            <Link className="plain-link" to="/walkthroughs/michelson">
              A worked reusable rule →
            </Link>
          </article>
        </div>
        <p className="home-aside">
          <code>PartitionResult</code> deliberately has no predict method. Many different rules
          reproduce the same labels on a finite sample and disagree everywhere else, so a sample
          optimum does not name one of them. There is exactly one crossing between the two, and it
          is a theorem rather than a convenience — <Link to="/get-started">Get started</Link> shows
          it, and the refusal that guards it.
        </p>
      </section>

      <section className="home-section section-wrap section-rule">
        <div className="section-heading">
          <div>
            <span className="eyebrow">The way in</span>
            <h2>What do you already have?</h2>
          </div>
          <p>
            The door into score space is fixed by what your analysis can honestly supply, not by
            preference.
          </p>
        </div>
        <div className="home-doors">
          <article className="door-item">
            <h3>Scores, already computed</h3>
            <div className="door-item__body">
              <p>
                Pass the array, or wrap it in <code>ScoreSample</code>. The shortest and most
                transparent path.
              </p>
            </div>
          </article>
          <article className="door-item">
            <h3>A component or analytic model</h3>
            <div className="door-item__body">
              <p>
                <code>LinearComponentScore</code> or <code>ScoreFunction</code>, paired with an
                observation sample or a bounded quadrature source. The statistical model stays visible
                in the call.
              </p>
            </div>
          </article>
          <article className="door-item">
            <h3>Density ratios</h3>
            <div className="door-item__body">
              <p>
                <code>DensityRatioScore</code>, or <code>CentralLogRatioScore</code> for paired
                central classifiers. This is the classifier route, and the caveat belongs here rather
                than further in: an estimated ratio yields an estimated score. The optimization is
                unchanged, but the Fisher semantics are only as good as the calibration behind the
                ratio, so ScoreQuant records that provenance instead of letting it disappear, and{" "}
                <code>ratio_closure_report</code> measures whether the ratios actually close.
              </p>
              <Link className="plain-link" to="/walkthroughs/ratios">
                A worked classifier route →
              </Link>
            </div>
          </article>
        </div>
      </section>

      <section className="home-section section-wrap section-rule">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Where to go</span>
            <h2>Two ways to start</h2>
          </div>
        </div>
        <div className="home-exits">
          <article className="exit">
            <h3>Run it with nothing installed</h3>
            <p>
              The Lab loads ScoreQuant into your browser and fits a partition there, on the same
              NumPy backend the library ships.
            </p>
            <Link className="plain-link" to="/lab?job=ratios">
              Open a prefilled run →
            </Link>
          </article>
          <article className="exit">
            <h3>Install it and follow the path</h3>
            <p>
              <code>uv add scorequant</code>, then a page that walks the smallest real fit through
              to the meaning of every number it prints.
            </p>
            <Link className="plain-link" to="/get-started">
              Get started →
            </Link>
          </article>
        </div>
      </section>
    </Layout>
  );
}
