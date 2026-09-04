import {useEffect, useMemo, useRef, useState} from "react";

import {useLocation} from "@docusaurus/router";

import {AppShell} from "../components/AppShell";
import {ScoreSpace} from "../components/ScoreSpace";
import {portalData, type ScoreScenario} from "../data/portal";
import {resolveJobPreset} from "../lab/jobPreset";
import {LAB_LIMITS, criterionLabel} from "../lab/protocol";
import type {LabCriterion, LabProblem, LabRunRequest} from "../lab/protocol";
import {useLabRunner} from "../lab/useLabRunner";
import {useScoreTable, type DatasetId} from "../lab/useScoreTable";
import {siteUrl} from "../lib/site";

type MobilePanel = "controls" | "plot" | "diagnostics";

/** Shown before a run when no precomputed fixture covers the current controls. */
const EMPTY_SCENARIO: ScoreScenario = {centers: [], labels: [], objective: 0, retention: 0};

const DATASETS: {detail: string; id: DatasetId; label: string}[] = [
  {detail: "56 rows · 2D", id: "gaussian", label: "Gaussian fixture"},
  {detail: "5,000 cells · 5D", id: "flowcyt", label: "FlowCyt scores"},
  {detail: "csv or npy", id: "local", label: "Your own file"},
];

export default function Lab(): React.JSX.Element {
  const [bins, setBins] = useState(4);
  const [solver, setSolver] = useState<LabProblem["solver"]>("d_exchange");
  const [runner, setRunner] = useState<LabRunRequest["runner"]>("fixture");
  const [panel, setPanel] = useState<MobilePanel>("plot");
  const [lessonOpen, setLessonOpen] = useState(false);
  const [criterionName, setCriterionName] = useState<LabCriterion["name"]>("d_optimality");
  const [interest, setInterest] = useState<string[]>([]);
  const fileInput = useRef<HTMLInputElement>(null);
  const lab = useLabRunner();
  const data = useScoreTable();
  const {chooseFlowCyt, chooseGaussian, loadPreset} = data;
  // Seeded from `?job=<slug>` once on mount (D5,
  // docs/programme/S08-the-four-walkthroughs.md). This page is server-rendered
  // by Docusaurus, so the query is read in an effect rather than during
  // render: an effect runs only after hydration, so the server render and the
  // client's first paint both see the same unseeded defaults above, and only
  // then does this apply the seed -- there is no render for the two to
  // disagree on. The ref guards it to exactly one application even if
  // `search` changes later while this page stays mounted.
  const jobAppliedRef = useRef(false);
  const {search} = useLocation();
  useEffect(() => {
    if (jobAppliedRef.current) return;
    jobAppliedRef.current = true;
    const seed = resolveJobPreset(search);
    if (seed === null) return;
    setBins(seed.bins);
    setCriterionName(seed.criterionName);
    setInterest(seed.interest);
    setSolver(seed.solver);
    setRunner(seed.runner);
    if (seed.dataset === "gaussian") chooseGaussian();
    else if (seed.dataset === "flowcyt") chooseFlowCyt();
    else loadPreset(seed.dataset);
  }, [chooseFlowCyt, chooseGaussian, loadPreset, search]);
  const fixture = portalData.scoreSpace.scenarios[String(bins)];
  const scenario = useMemo<ScoreScenario>(() => lab.result === null ? (fixture ?? EMPTY_SCENARIO) : {
    centers: lab.result.centers,
    labels: lab.result.labels,
    objective: lab.result.objective,
    retention: lab.result.retention
  }, [fixture, lab.result]);
  const dimensions = data.table.scores[0]?.length ?? 0;
  const maxBins = Math.min(LAB_LIMITS.maxBins, data.table.scores.length);
  // Every D-optimal path refuses a budget below the number of informative score
  // directions: the between-cell information would be singular. The effective
  // rank is only known once the fit runs, but the score dimension bounds it, so
  // the control can avoid *defaulting* into a refusal.
  const determinantObjective = criterionName !== "normalized_trace";
  const binFloor = determinantObjective ? Math.min(dimensions, maxBins) : 1;
  const effectiveBins = Math.min(maxBins, Math.max(bins, binFloor));
  const parameters = data.table.schema ?? [];
  // The schema encodes its length bounds as a tuple union, which a list built
  // from user selections cannot satisfy statically. `validateProblem` enforces
  // the same bounds at runtime, immediately, before anything is dispatched.
  const criterion: LabCriterion | undefined =
    criterionName === "d_optimality"
      ? undefined
      : criterionName === "normalized_trace"
        ? {name: "normalized_trace"}
        : {name: "profiled_d_optimality", interest: interest as unknown as NonNullable<LabCriterion["interest"]>};
  const problem: LabProblem = {
    scores: data.table.scores,
    weights: data.table.weights,
    nBins: effectiveBins,
    solver,
    seed: 28,
    maxSteps: 120,
    maxScans: 120,
    datasetId: data.table.id,
    ...(data.table.schema === undefined
      ? {}
      : {schema: data.table.schema as unknown as NonNullable<LabProblem["schema"]>}),
    ...(criterion === undefined ? {} : {criterion})
  };
  const running = lab.state === "loading" || lab.state === "running";
  // The score-space panel is a two-dimensional picture. Above two dimensions it
  // is a projection onto the first two coordinates, and saying so matters:
  // cells that overlap here are not necessarily adjacent in the real space.
  const projected = dimensions > 2;
  return (
    <AppShell lab title="Lab" description="Run bounded ScoreQuant NumPy jobs privately in your browser.">
      <div className="lab-page">
        <header className="lab-heading">
          <div><span className="eyebrow">Local computation workspace</span><h1>Score-space lab</h1></div>
          <div className="lab-privacy"><i className="status-dot"/><span>Inputs stay in this tab — this site has no server</span></div>
        </header>
        <nav className="lab-mobile-tabs" aria-label="Lab panel">
          {(["controls", "plot", "diagnostics"] as const).map((value) => <button key={value} className={panel === value ? "is-active" : ""} onClick={() => setPanel(value)}>{value}</button>)}
        </nav>
        <div className="lab-workspace">
          <aside className={`lab-panel lab-controls ${panel === "controls" ? "is-mobile-active" : ""}`}>
            <div className="lab-panel__title"><span>01</span><strong>Run controls</strong></div>
            <label className="lab-field"><span>Runner</span><select value={runner} onChange={(event) => setRunner(event.target.value as LabRunRequest["runner"])}><option value="fixture" disabled={data.table.id !== "gaussian"}>Verified fixture · instant</option><option value="pyodide-numpy">Pyodide + NumPy · local</option></select></label>
            <label className="lab-field"><span>Solver</span><select value={solver} onChange={(event) => setSolver(event.target.value as LabProblem["solver"])}><option value="d_exchange">D exchange</option><option value="mahalanobis_lloyd">Guarded Lloyd</option><option value="kmeans">Whitened k-means</option><option value="soft_voronoi">Soft Voronoi</option></select></label>
            <label className="lab-field lab-field--range"><span>Hard bins <strong>{effectiveBins}</strong></span><input type="range" min="2" max={String(maxBins)} value={effectiveBins} onChange={(event) => setBins(Number(event.target.value))}/></label>
            <div className="lab-field lab-field--group">
              <span>Score table</span>
              <div className="filter-row filter-row--tight">
                {DATASETS.map((entry) => (
                  <button
                    className={`filter-chip ${data.table.id === entry.id ? "is-active" : ""}`}
                    key={entry.id}
                    onClick={() => {
                      if (entry.id === "gaussian") data.chooseGaussian();
                      else if (entry.id === "flowcyt") data.chooseFlowCyt();
                      else fileInput.current?.click();
                      setInterest([]);
                      setCriterionName("d_optimality");
                      setSolver("d_exchange");
                    }}
                  >
                    {entry.label}
                    <small>{entry.detail}</small>
                  </button>
                ))}
              </div>
              <input
                accept=".csv,.tsv,.txt,.npy"
                className="visually-hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file !== undefined) data.loadFile(file);
                  event.target.value = "";
                }}
                ref={fileInput}
                type="file"
              />
            </div>
            <label className="lab-field"><span>Criterion</span><select value={criterionName} onChange={(event) => {setCriterionName(event.target.value as LabCriterion["name"]); setInterest([]);}}><option value="d_optimality">D-optimality</option><option value="profiled_d_optimality">Profiled D&#8347;</option><option value="normalized_trace">Normalized trace</option></select></label>
            {criterionName === "profiled_d_optimality" && (
              <div className="lab-field lab-field--group">
                <span>Parameters of interest</span>
                {parameters.length === 0 ? (
                  <small className="lab-hint">This table has no named columns, so there is nothing to profile by name. Load the FlowCyt scores or a CSV with a header row.</small>
                ) : (
                  <div className="filter-row filter-row--tight">
                    {parameters.map((name) => (
                      <button
                        className={`filter-chip ${interest.includes(name) ? "is-active" : ""}`}
                        key={name}
                        onClick={() => {
                          setInterest((current) => current.includes(name) ? current.filter((value) => value !== name) : [...current, name]);
                        }}
                      >
                        {name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
            <div className="lab-limit">
              <span>{data.table.label}</span>
              <strong>{data.table.scores.length.toLocaleString()} rows · {dimensions} dimensions</strong>
              <small>{data.loading ? "Loading…" : data.table.detail}</small>
              <small>Browser ceiling: {LAB_LIMITS.maxRows.toLocaleString()} × {LAB_LIMITS.maxDimensions}D · {LAB_LIMITS.maxBins} bins</small>
            </div>
            {data.error !== null && <p className="lab-hint lab-hint--error">{data.error}</p>}
            <button className="lab-run" disabled={running} onClick={() => {lab.run(problem, runner); setPanel("plot");}}>{running ? "Running…" : runner === "fixture" ? "Load verified result" : "Run locally"}<span>▶</span></button>
            {running && <button className="lab-cancel" onClick={lab.cancel}>Cancel and terminate worker</button>}
          </aside>

          <section className={`lab-panel lab-plot ${panel === "plot" ? "is-mobile-active" : ""}`}>
            <div className="lab-panel__title"><span>02</span><strong>Score space</strong><small>{runner === "fixture" ? "precomputed native NumPy" : "browser NumPy"}</small></div>
            {effectiveBins > bins && (
              <p className="lab-hint">Raised to {effectiveBins} bins: D-optimality needs at least as many bins as the {dimensions} informative score directions, or the between-cell information is singular.</p>
            )}
            <ScoreSpace
              compact
              controlledBins={effectiveBins}
              pointsOverride={data.table.scores}
              scenarioOverride={scenario}
              {...(lab.result === null && data.table.id !== "gaussian"
                ? {placeholder: `${data.table.scores.length.toLocaleString()} rows loaded. Run the solver to see the partition — there is no precomputed result for this table.`}
                : {})}
            />
            {projected && <p className="lab-hint">Projected onto the first two of {dimensions} score dimensions. Cells that overlap in this picture need not be adjacent in the space the solver worked in.</p>}
            <div className="lab-legend"><span><i style={{background: "#2b77f3"}}/>hard assignment</span><span><i className="legend-center"/>cell mean</span><span><i className="legend-edge"/>Voronoi comparison</span></div>
          </section>

          <aside className={`lab-panel lab-diagnostics ${panel === "diagnostics" ? "is-mobile-active" : ""}`}>
            <div className="lab-panel__title"><span>03</span><strong>Diagnostics</strong></div>
            <div className="lab-status"><span>Runtime state</span><strong className={`lab-state lab-state--${lab.state}`}>{lab.state}</strong><p>{lab.error ?? lab.stage}</p>{running && <i><span style={{width: `${lab.progress * 100}%`}}/></i>}</div>
            <dl className="diagnostic-list">
              <div><dt>Retained information</dt><dd>{(scenario.retention * 100).toFixed(2)}%</dd></div>
              <div><dt>Hard bins</dt><dd>{effectiveBins}</dd></div>
              <div><dt>Objective</dt><dd>{scenario.objective.toFixed(5)}</dd></div>
              <div><dt>Objective kind</dt><dd>{lab.result?.criterionLabel ?? criterionLabel(criterion)}</dd></div>
              <div><dt>Execution</dt><dd>{lab.result?.execution ?? "numpy / fixture"}</dd></div>
              <div><dt>Runtime</dt><dd>{lab.warm ? "warm — reruns skip the cold start" : "cold"}</dd></div>
              <div><dt>Seed</dt><dd>28</dd></div>
            </dl>
            <div className="lab-note"><strong>What this proves</strong><p>The result is a deterministic run for this weighted score table. It does not make estimated input ratios exact or turn local stability into global optimality.</p></div>
          </aside>
        </div>
        <section className="lab-lesson">
          <div><span className="eyebrow">Locked notebook lesson</span><h2>Derive the information loss interactively.</h2><p>A self-hosted marimo WASM lesson loads only when you ask for it. Its logic is fixed and its inputs are guided; arbitrary code editing remains outside v1.</p></div>
          {!lessonOpen ? <button className="button-primary" onClick={() => setLessonOpen(true)}>Load marimo lesson</button> : <iframe title="ScoreQuant marimo lesson" src={siteUrl("lessons/score-space/")} loading="lazy" sandbox="allow-scripts allow-same-origin allow-downloads"/>}
        </section>
      </div>
    </AppShell>
  );
}
