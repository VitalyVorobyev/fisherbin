import Link from "@docusaurus/Link";

import {AppShell} from "../components/AppShell";
import {ScoreSpace} from "../components/ScoreSpace";
import {portalData} from "../data/portal";

export default function Home(): React.JSX.Element {
  return (
    <AppShell title="ScoreQuant" description="Learn and run information-preserving score-space quantization.">
      <section className="home-hero">
        <div className="home-hero__inner">
          <div className="home-hero__copy">
            <span className="eyebrow">Information-optimal hard binning</span>
            <h1>Compress events.<br/><em>Keep the evidence.</em></h1>
            <p>
              ScoreQuant turns continuous or high-dimensional observations into a few hard labels,
              then accounts for exactly how much Fisher information survived.
            </p>
            <div className="hero-actions">
              <Link className="button-primary" to="/docs">Choose your workflow</Link>
              <Link className="button-secondary" to="/lab">Open the browser lab</Link>
            </div>
          </div>
          <div className="home-hero__visual"><ScoreSpace /></div>
        </div>
      </section>

      <section className="home-proof" aria-label="Project evidence">
        <div><small>Runtime</small><strong>JAX + NumPy</strong></div>
        <div><small>Objective</small><strong>Fisher retention</strong></div>
        <div><small>Rules</small><strong>Hard, reusable bins</strong></div>
        <div><small>Research</small><strong>Claims with provenance</strong></div>
      </section>

      <section className="home-section section-wrap">
        <div className="section-heading">
          <div><span className="eyebrow">Start with the task</span><h2>Two questions that should never be conflated.</h2></div>
          <p>One dataset may need a final partition. A future stream needs a reusable rule. ScoreQuant keeps that distinction explicit.</p>
        </div>
        <div className="task-grid">
          <article className="task-card">
            <span className="task-card__number">01</span>
            <h3>Partition this sample</h3>
            <p>Assign the rows you have now. Optimize a finite weighted score table and return labels—no predictor implied.</p>
            <Link className="plain-link" to="/docs?task=partition">Use optimize_partition →</Link>
          </article>
          <article className="task-card">
            <span className="task-card__number">02</span>
            <h3>Fit a reusable quantizer</h3>
            <p>Learn a rule in score space, validate it honestly, and apply it to later scores through predict_scores.</p>
            <Link className="plain-link" to="/docs?task=quantizer">Use fit_quantizer →</Link>
          </article>
        </div>
      </section>

      <section className="home-section section-rule">
        <div className="section-wrap">
          <div className="section-heading">
            <div><span className="eyebrow">Then choose a door</span><h2>Different observations. One score law.</h2></div>
            <Link className="plain-link" to="/research">Why scores are sufficient here →</Link>
          </div>
          <div className="door-grid">
            <article className="door"><small>Door 1 · direct</small><h3>You already have scores</h3><p>Bring event-level score vectors and optional importance weights. This is the shortest, most transparent path.</p></article>
            <article className="door"><small>Door 2 · exact model</small><h3>You have densities</h3><p>Construct scores from component densities and coefficients, keeping the statistical model visible.</p></article>
            <article className="door"><small>Door 3 · estimated</small><h3>You have density ratios</h3><p>Use calibrated ratios from a classifier without claiming the exact Fisher semantics of a known model.</p></article>
          </div>
        </div>
      </section>

      <section className="home-section section-wrap research-preview">
        <div>
          <span className="eyebrow">Research memory</span>
          <h2 style={{fontFamily: "var(--font-heading)", fontSize: 44, letterSpacing: "-.045em", lineHeight: 1.05}}>
            Theorems, bridges, and limits—not a wall of citations.
          </h2>
          <p style={{color: "var(--ink-600)"}}>The public graph is deliberately curated. Every node names its evidence level and dependencies.</p>
          <Link className="plain-link" to="/research">Explore the claim map →</Link>
        </div>
        <div className="research-preview__claims">
          {portalData.research.slice(0, 4).map((claim) => (
            <Link key={claim.id} to="/research">
              <span>{claim.status.replace("_", " ")}</span><strong>{claim.title}</strong><span>↗</span>
            </Link>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
