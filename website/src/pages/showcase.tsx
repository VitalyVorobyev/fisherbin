import {useMemo, useState} from "react";
import Link from "@docusaurus/Link";

import {AppShell} from "../components/AppShell";
import {PageIntro} from "../components/PageIntro";
import {CompositionBars} from "../components/charts/CompositionBars";
import {MarkerHistogram} from "../components/charts/MarkerHistogram";
import {MethodComparison} from "../components/charts/MethodComparison";
import {Legend} from "../components/charts/Axes";
import {populationColor} from "../components/charts/scale";
import {showcaseData} from "../data/showcase";

const {comparison, dataset, exploration, headline, scoreSchema} = showcaseData;

function percent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export default function Showcase(): React.JSX.Element {
  // "other" dominates every panel by an order of magnitude, so the default view
  // hides it; the reader can put it back.
  const [visible, setVisible] = useState<number[]>(() =>
    dataset.populations.map((_, index) => index).filter((index) => index < dataset.populations.length - 1)
  );
  const [showAllMarkers, setShowAllMarkers] = useState(false);

  const markers = useMemo(
    () => (showAllMarkers ? exploration.markers : exploration.markers.slice(0, 6)),
    [showAllMarkers]
  );

  const toggle = (index: number): void => {
    setVisible((current) =>
      current.includes(index) ? current.filter((value) => value !== index) : [...current, index].sort((a, b) => a - b)
    );
  };

  return (
    <AppShell
      title="FlowCyt showcase"
      description="An end-to-end real-data study: bone-marrow flow cytometry compressed into eight hard bins."
    >
      <PageIntro
        eyebrow="End-to-end real data"
        title="Thirty patients, twelve markers, eight bins."
        lead="Flow cytometry measures individual cells. The scientific result is a vector of population fractions. This study puts ScoreQuant between the two and measures exactly what the compression costs."
      />

      <section className="section-wrap">
        <div className="showcase-headline">
          <div>
            <small>Information retained at {headline.bins} bins</small>
            <strong>{percent(headline.heldOutEfficiency)}</strong>
            <span>held-out D-efficiency of the supplied-score surrogate</span>
          </div>
          <div>
            <small>Held-out estimation error</small>
            <strong>{headline.macroRmse.toFixed(5)}</strong>
            <span>macro RMSE over ten frozen patients</span>
          </div>
          <div>
            <small>Unbinned baseline</small>
            <strong>{headline.unbinnedMacroRmse.toFixed(5)}</strong>
            <span>the same estimate with no compression at all</span>
          </div>
        </div>
        <p className="provenance-note">
          <span aria-hidden="true">◇</span>
          <span>
            Eight integer counts per patient reach within {((headline.macroRmse / headline.unbinnedMacroRmse - 1) * 100).toFixed(0)}% of
            what the full continuous classifier output achieves. That gap is the price of the
            compression, and it is a measured number rather than an assumption.
          </span>
        </p>
      </section>

      <section className="section-wrap">
        <h2>The problem</h2>
        <p>
          A bone-marrow report is written around cell-population fractions: how much of this marrow
          is T cells, B cells, monocytes, mast cells, and the CD34+ progenitor compartment. The
          measurement, though, is per cell — {dataset.markers.length} fluorescence and scatter
          channels for each of hundreds of thousands of events per patient.
        </p>
        <p>
          Somewhere between the two, the data must be reduced. Conventionally that is gating: a
          human draws polygons on two-dimensional projections. Gating is reproducible and
          interpretable, and it is chosen for those properties rather than for how much information
          about the fractions it keeps. The question this study asks is what a small number of hard
          categories can retain if they are chosen from the inference problem instead.
        </p>
        <div className="showcase-pipeline">
          <span>{dataset.markers.length}-dimensional cell measurements</span>
          <span>calibrated classifier</span>
          <span>density ratios</span>
          <span>{scoreSchema.parameters.length}-dimensional mixture score</span>
          <strong>ScoreQuant</strong>
          <span>{headline.bins} frozen hard bins</span>
          <span>integer counts</span>
          <span>mixture fit</span>
          <span>population fractions</span>
        </div>
        <p>
          Two of those boxes are deliberately not ScoreQuant. The classifier is not ScoreQuant, and
          the downstream mixture fitter is not ScoreQuant. What the library owns is the single step
          in the middle: turning a score vector into one of {headline.bins} labels while losing as
          little information about the fractions as possible.
        </p>
      </section>

      <section className="section-wrap">
        <h2>The data</h2>
        <div className="provenance-grid">
          <div>
            <small>Patients</small>
            <strong>{dataset.patients}</strong>
          </div>
          <div>
            <small>Split</small>
            <strong>
              {dataset.referencePatients.length} reference · {dataset.heldOutPatients.length} held out
            </strong>
          </div>
          <div>
            <small>Upstream events</small>
            <strong>{dataset.upstreamEvents.toLocaleString("en-US")}</strong>
          </div>
          <div>
            <small>Study sample</small>
            <strong>{dataset.studyCells.toLocaleString("en-US")} cells</strong>
          </div>
        </div>
        <p>
          The held-out patients were frozen before any fitting, and nothing downstream of the split
          has seen them. The charts on this page are computed from a committed{" "}
          {dataset.fixtureCells.toLocaleString("en-US")}-cell deterministic subset; the headline
          numbers come from the full study on {dataset.studyCells.toLocaleString("en-US")} cells.
        </p>
        <p className="provenance-note">
          <span aria-hidden="true">◇</span>
          <span>
            The {dataset.name} data is © Bini, Nassajian Mojarrad, Liarou, Matthes and
            Marchand-Maillet, and is licensed{" "}
            <a href={dataset.licenseUrl} rel="noreferrer noopener" target="_blank">
              {dataset.license}
            </a>{" "}
            — separately from ScoreQuant's MIT license. Everything derived from it on this page
            carries the same attribution and share-alike terms.{" "}
            <a href={dataset.repository} rel="noreferrer noopener" target="_blank">
              Benchmark repository
            </a>
            .
          </span>
        </p>
      </section>

      <section className="section-wrap">
        <h2>Exploring the measurements</h2>
        <p>
          Each marker separates some populations and not others — which is precisely why no single
          channel, and no pair of channels, is a sufficient summary. Densities are shown rather than
          counts, because the populations differ in size by two orders of magnitude, and the axis is
          the {exploration.markerScale}: on a linear intensity axis every panel collapses into one
          spike against the origin.
        </p>
        <div className="filter-row">
          {dataset.populations.map((population, index) => (
            <button
              className={`filter-chip ${visible.includes(index) ? "is-active" : ""}`}
              key={population}
              onClick={() => {
                toggle(index);
              }}
              style={visible.includes(index) ? {borderColor: populationColor(index)} : undefined}
            >
              {population}
            </button>
          ))}
        </div>
        <Legend
          entries={dataset.populations
            .filter((_, index) => visible.includes(index))
            .map((population) => ({
              color: populationColor(dataset.populations.indexOf(population)),
              label: population,
            }))}
        />
        <div className="marker-grid">
          {markers.map((panel) => (
            <MarkerHistogram key={panel.marker} panel={panel} visible={visible} />
          ))}
        </div>
        <button
          className="filter-chip"
          onClick={() => {
            setShowAllMarkers((value) => !value);
          }}
        >
          {showAllMarkers ? "Show the first six markers" : `Show all ${String(exploration.markers.length)} markers`}
        </button>
      </section>

      <section className="section-wrap">
        <h2>What is actually being estimated</h2>
        <p>
          The quantity of interest is one composition vector per patient. The spread across patients
          is large — far larger than any binning method&apos;s error — which is what makes the error
          numbers further down meaningful rather than merely small. These are the study&apos;s own
          measured compositions on the full sample, not counts from the reduced fixture on this
          page: that fixture deliberately draws a fixed number of cells per population for the
          reference patients, so counting it would plot the sampling design and call it biology.
        </p>
        <CompositionBars patients={exploration.patients} populations={dataset.populations} />
      </section>

      <section className="section-wrap">
        <h2>From cells to a score</h2>
        <p>
          A calibrated, cross-fitted classifier estimates the posterior over the{" "}
          {dataset.populations.length} populations for each cell. Dividing by the training priors
          turns those posteriors into density ratios, and the mixture parameterization turns the
          ratios into a score. One population is absorbed as the simplex-dependent reference, which
          is why {dataset.populations.length} populations give a{" "}
          {scoreSchema.parameters.length}-dimensional score:
        </p>
        <ul className="showcase-schema">
          {scoreSchema.parameters.map((parameter, index) => (
            <li key={parameter}>
              <span className="chart-swatch" style={{background: populationColor(index)}} aria-hidden="true" />
              <code>{parameter}</code>
            </li>
          ))}
        </ul>
        <p>
          Those names are not decoration. They are the score schema the library carries, so a
          profiled objective can name the compartment it is optimizing for —{" "}
          <code>interest=(&quot;HSPCs&quot;,)</code> — rather than a column index whose meaning
          lives in a comment.
        </p>
      </section>

      <section className="section-wrap">
        <h2>Results</h2>
        <p>
          Every method below compresses the same cells to the same number of bins, and every one is
          scored the same way: fit population fractions from the resulting counts on the ten frozen
          patients, and measure the error against their known composition. Lower is better.
        </p>
        <MethodComparison baseline={comparison.unbinnedBaseline} methods={comparison.methods} />
        <h3>Reading the result</h3>
        <p>
          The information-optimal methods separate from the convenience baselines by more than an
          order of magnitude, and the gap widens rather than closes as bins are added — a grid or a
          single score direction cannot spend extra bins usefully, because the directions it is
          spending them on are not the informative ones.
        </p>
        <p>
          The honest caveat is the flat part: past the operating point, more bins buy very little.
          At {headline.bins} bins the compression is already within{" "}
          {((headline.macroRmse / headline.unbinnedMacroRmse - 1) * 100).toFixed(0)}% of the
          unbinned estimate, so the remaining budget is spent on information the downstream fit
          cannot use. That is the useful finding: the number of bins you need is smaller than
          intuition suggests, and it is measurable in advance.
        </p>
        <p>
          The study also runs a genuine profiled-<em>D<sub>s</sub></em> experiment, treating one
          cell fraction as the parameter of interest and the rest as nuisance. It does{" "}
          <strong>not</strong> materially improve the measurement: plain <em>D</em> already sits
          close to a certified efficient-score ceiling. That is a negative result worth reporting,
          and it illustrates why <em>D<sub>s</sub></em> is a different inferential objective rather
          than an automatically better one.
        </p>
      </section>

      <section className="section-wrap">
        <h2>Run it yourself</h2>
        <p>
          The Lab loads this study&apos;s score table and runs the real solver in your browser —
          the actual ScoreQuant wheel on the NumPy backend, not a reimplementation. Change the bin
          budget, the criterion or the solver and watch the retained information move. You can also
          point it at your own score table; nothing you load leaves your machine.
        </p>
        <p>
          <Link className="lab-link" to="/lab">
            Open the Lab <span aria-hidden="true">↗</span>
          </Link>
        </p>
      </section>
    </AppShell>
  );
}
