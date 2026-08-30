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
    description: "Build a LinearProblem from component densities and coefficients. The adapter produces exact mixture scores before fitting the rule.",
    steps: ["Define component density evaluations", "State the coefficient parameterization", "Fit a score-space quantizer"],
    code: `problem = sq.LinearProblem(\n    components=component_pdf,\n    coefficients=fractions,\n    weights=quadrature_weights,\n)\n\nquantizer = sq.fit_quantizer(\n    problem, n_bins=6,\n    execution=sq.ExecutionConfig(backend="jax"),\n)`
  },
  ratios: {
    eyebrow: "Door 3 · density ratios",
    title: "Use estimated ratios without overclaiming",
    description: "Convert calibrated posterior estimates into component density ratios, record their provenance, and keep source weights separate.",
    steps: ["Calibrate class posteriors", "Convert with the training priors", "Validate the fitted rule on held-out observations"],
    code: `provider = sq.DensityRatioScore.from_classifier(\n    classifier.predict_proba,\n    class_priors,\n    sq.MixtureParameterization(fractions),\n    calibration="isotonic",\n)\nquantizer = sq.fit_quantizer(\n    source, score=provider, n_bins=6,\n)`
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
        <div className="provenance-note"><span aria-hidden="true">◇</span><span>The portal teaches the public task contract. Exhaustive configuration, result fields, developer internals, and ADRs remain in the canonical MkDocs reference.</span></div>
      </section>
    </AppShell>
  );
}
