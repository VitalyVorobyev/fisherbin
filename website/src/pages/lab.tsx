import {useMemo, useState} from "react";

import {AppShell} from "../components/AppShell";
import {ScoreSpace} from "../components/ScoreSpace";
import {portalData, type ScoreScenario} from "../data/portal";
import type {LabProblem, LabRunRequest, ScoreRow} from "../lab/protocol";
import {useLabRunner} from "../lab/useLabRunner";

type MobilePanel = "controls" | "plot" | "diagnostics";

export default function Lab(): React.JSX.Element {
  const [bins, setBins] = useState(4);
  const [solver, setSolver] = useState<LabProblem["solver"]>("d_exchange");
  const [runner, setRunner] = useState<LabRunRequest["runner"]>("fixture");
  const [panel, setPanel] = useState<MobilePanel>("plot");
  const [lessonOpen, setLessonOpen] = useState(false);
  const lab = useLabRunner();
  const fixture = portalData.scoreSpace.scenarios[String(bins)];
  if (fixture === undefined) throw new Error(`No generated browser fixture exists for ${bins} bins.`);
  const scenario = useMemo<ScoreScenario>(() => lab.result === null ? fixture : {
    centers: lab.result.centers,
    labels: lab.result.labels,
    objective: lab.result.objective,
    retention: lab.result.retention
  }, [fixture, lab.result]);
  const problem: LabProblem = {
    scores: portalData.scoreSpace.points.map((row) => row as ScoreRow),
    weights: portalData.scoreSpace.weights,
    nBins: bins,
    solver,
    seed: 28,
    maxSteps: 120,
    maxScans: 120
  };
  const running = lab.state === "loading" || lab.state === "running";
  return (
    <AppShell lab title="Lab" description="Run bounded ScoreQuant NumPy jobs privately in your browser.">
      <div className="lab-page">
        <header className="lab-heading">
          <div><span className="eyebrow">Local computation workspace</span><h1>Score-space lab</h1></div>
          <div className="lab-privacy"><i className="status-dot"/><span>Inputs stay in this tab</span></div>
        </header>
        <nav className="lab-mobile-tabs" aria-label="Lab panel">
          {(["controls", "plot", "diagnostics"] as const).map((value) => <button key={value} className={panel === value ? "is-active" : ""} onClick={() => setPanel(value)}>{value}</button>)}
        </nav>
        <div className="lab-workspace">
          <aside className={`lab-panel lab-controls ${panel === "controls" ? "is-mobile-active" : ""}`}>
            <div className="lab-panel__title"><span>01</span><strong>Run controls</strong></div>
            <label className="lab-field"><span>Runner</span><select value={runner} onChange={(event) => setRunner(event.target.value as LabRunRequest["runner"])}><option value="fixture">Verified fixture · instant</option><option value="pyodide-numpy">Pyodide + NumPy · local</option></select></label>
            <label className="lab-field"><span>Solver</span><select value={solver} onChange={(event) => setSolver(event.target.value as LabProblem["solver"])}><option value="d_exchange">D exchange</option><option value="mahalanobis_lloyd">Guarded Lloyd</option><option value="kmeans">Whitened k-means</option><option value="soft_voronoi">Soft Voronoi</option></select></label>
            <label className="lab-field lab-field--range"><span>Hard bins <strong>{bins}</strong></span><input type="range" min="3" max="5" value={bins} onChange={(event) => setBins(Number(event.target.value))}/></label>
            <div className="lab-limit"><span>Browser envelope</span><strong>56 rows · 2 dimensions</strong><small>v1 maximum: 5,000 × 4D · 16 bins</small></div>
            <button className="lab-run" disabled={running} onClick={() => {lab.run(problem, runner); setPanel("plot");}}>{running ? "Running…" : runner === "fixture" ? "Load verified result" : "Run locally"}<span>▶</span></button>
            {running && <button className="lab-cancel" onClick={lab.cancel}>Cancel and terminate worker</button>}
          </aside>

          <section className={`lab-panel lab-plot ${panel === "plot" ? "is-mobile-active" : ""}`}>
            <div className="lab-panel__title"><span>02</span><strong>Score space</strong><small>{runner === "fixture" ? "precomputed native NumPy" : "browser NumPy"}</small></div>
            <ScoreSpace compact controlledBins={bins} scenarioOverride={scenario} />
            <div className="lab-legend"><span><i style={{background: "#2b77f3"}}/>hard assignment</span><span><i className="legend-center"/>cell mean</span><span><i className="legend-edge"/>Voronoi comparison</span></div>
          </section>

          <aside className={`lab-panel lab-diagnostics ${panel === "diagnostics" ? "is-mobile-active" : ""}`}>
            <div className="lab-panel__title"><span>03</span><strong>Diagnostics</strong></div>
            <div className="lab-status"><span>Runtime state</span><strong className={`lab-state lab-state--${lab.state}`}>{lab.state}</strong><p>{lab.error ?? lab.stage}</p>{running && <i><span style={{width: `${lab.progress * 100}%`}}/></i>}</div>
            <dl className="diagnostic-list">
              <div><dt>Retained information</dt><dd>{(scenario.retention * 100).toFixed(2)}%</dd></div>
              <div><dt>Objective</dt><dd>{scenario.objective.toFixed(5)}</dd></div>
              <div><dt>Execution</dt><dd>{lab.result?.execution ?? "numpy / fixture"}</dd></div>
              <div><dt>Seed</dt><dd>28</dd></div>
            </dl>
            <div className="lab-note"><strong>What this proves</strong><p>The result is a deterministic run for this weighted score table. It does not make estimated input ratios exact or turn local stability into global optimality.</p></div>
          </aside>
        </div>
        <section className="lab-lesson">
          <div><span className="eyebrow">Locked notebook lesson</span><h2>Derive the information loss interactively.</h2><p>A self-hosted marimo WASM lesson loads only when you ask for it. Its logic is fixed and its inputs are guided; arbitrary code editing remains outside v1.</p></div>
          {!lessonOpen ? <button className="button-primary" onClick={() => setLessonOpen(true)}>Load marimo lesson</button> : <iframe title="ScoreQuant marimo lesson" src="/scorequant/portal/lessons/score-space/" loading="lazy" sandbox="allow-scripts allow-same-origin allow-downloads"/>}
        </section>
      </div>
    </AppShell>
  );
}
