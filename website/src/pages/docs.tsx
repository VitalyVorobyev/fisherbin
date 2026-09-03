import Link from "@docusaurus/Link";
import {useMemo, useState} from "react";

import {AppShell} from "../components/AppShell";
import {PageIntro} from "../components/PageIntro";

const doors = {
  scores: {
    eyebrow: "Door 1 · score events",
    title: "Start from the sufficient representation",
    description: "Use a weighted table of event-level score vectors. No score provider or observation model is hidden inside the task.",
    steps: ["Choose partitioning or reusable quantization", "Pass scores and optional importance weights", "Inspect retention, geometry, and stability"],
    code: `import scorequant as sq\n\nexecution = sq.ExecutionConfig(\n    backend="numpy",\n    precision="float64",\n    device="cpu",\n)\n\nresult = sq.optimize_partition(\n    scores, weights=weights, n_bins=6,\n    execution=execution,\n)`
  },
  densities: {
    eyebrow: "Door 2 · known densities",
    title: "Keep the model components explicit",
    description: "Declare the component densities and the reference coefficients. LinearComponentScore produces exact mixture scores on a deterministic quadrature grid before the rule is fitted.",
    steps: ["Declare component densities and reference coefficients", "Choose the reference measure (sample or bounded quadrature)", "Fit a score-space quantizer"],
    code: `model = sq.LinearComponents(\n    components={"peak": peak_pdf, "flat": flat_pdf},\n    coefficients={"peak": 1.0, "flat": 0.5},\n    variables=["mass"],\n)\nsource = sq.IntegrationSource(\n    [[-2.0, 3.0]],\n    density=lambda X: peak_pdf(X) + 0.5 * flat_pdf(X),\n    quadrature=sq.GaussLegendreConfig(order=64),\n)\nquantizer = sq.fit_quantizer(\n    source, provider=sq.LinearComponentScore(model),\n    n_bins=6, config=sq.DExchangeConfig(seed=11),\n)`
  },
  ratios: {
    eyebrow: "Door 3 · density ratios",
    title: "Use estimated ratios without overclaiming",
    description: "Convert calibrated posterior estimates into component density ratios, record their provenance, and keep source weights separate.",
    steps: ["Calibrate class posteriors", "Convert with the training priors", "Validate the fitted rule on held-out observations"],
    code: `provider = sq.DensityRatioScore.from_classifier(\n    classifier.predict_proba,\n    class_priors,\n    sq.MixtureParameterization(fractions),\n    calibration="isotonic",\n)\nquantizer = sq.fit_quantizer(\n    source, provider=provider, n_bins=6,\n)`
  }
} as const;

type Door = keyof typeof doors;

export default function Docs(): React.JSX.Element {
  const [door, setDoor] = useState<Door>("scores");
  const selected = useMemo(() => doors[door], [door]);
  return (
    <AppShell title="Docs" description="Choose a ScoreQuant workflow from the representation you already have.">
      <PageIntro eyebrow="Task-first documentation" title="What do you have in hand?" lead="Begin with the representation your analysis can honestly supply. The portal keeps conversion, optimization, and prediction as separate visible steps." />
      <section className="section-wrap">
        <div className="workflow-doors" role="tablist" aria-label="Input representation">
          {(Object.keys(doors) as Door[]).map((name, index) => (
            <button key={name} role="tab" aria-selected={door === name} className={`workflow-door ${door === name ? "is-active" : ""}`} onClick={() => setDoor(name)}>
              <small>0{index + 1}</small><strong>{name[0]?.toUpperCase()}{name.slice(1)}</strong><span>{index === 0 ? "Event-level score rows" : index === 1 ? "Evaluable component PDFs" : "Exact or estimated ratios"}</span>
            </button>
          ))}
        </div>
        <div className="workflow-detail" role="tabpanel">
          <div>
            <span className="eyebrow">{selected.eyebrow}</span>
            <h2>{selected.title}</h2>
            <p>{selected.description}</p>
            <ol className="workflow-steps">{selected.steps.map((step) => <li key={step}>{step}</li>)}</ol>
            <Link className="plain-link" to="/examples">See complete workflows →</Link>
          </div>
          <pre className="code-block"><code>{selected.code}</code></pre>
        </div>
      </section>
      <section className="home-section section-wrap">
        <div><span className="eyebrow">Before any of it</span><h2>Install the package.</h2></div>
        <pre className="code-block"><code>uv add scorequant</code></pre>
        <p>
          Or <code>pip install scorequant</code> outside a <code>uv</code> project. Python 3.12 or
          newer. JAX and Optax are the numerical dependencies; NumPy is a supported portable
          runtime, which is what lets a saved rule predict where JAX is absent — including in the
          browser, which is exactly what the Lab on this site runs.
        </p>
      </section>
      <section className="home-section section-wrap">
        <div className="provenance-note"><span aria-hidden="true">◇</span><span>The portal teaches the public task contract. Exhaustive configuration, result fields, developer internals, and ADRs remain in the canonical MkDocs reference.</span></div>
      </section>
    </AppShell>
  );
}
