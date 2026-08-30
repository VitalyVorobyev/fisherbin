import {useMemo, useState} from "react";

import {AppShell} from "../components/AppShell";
import {PageIntro} from "../components/PageIntro";
import {portalData} from "../data/portal";

export default function Benchmarks(): React.JSX.Element {
  const [scale, setScale] = useState<"all" | "20k" | "100k">("20k");
  const runs = useMemo(() => portalData.benchmarks.runs.filter((run) => scale === "all" || (scale === "20k" ? run.rows === 20_000 : run.rows === 100_000)), [scale]);
  const maximum = Math.max(...runs.map((run) => run.elapsed_seconds), 0.001);
  const environment = portalData.benchmarks.environment;
  return (
    <AppShell title="Benchmarks" description="Data-driven ScoreQuant speed, scale, memory, and quality evidence.">
      <PageIntro eyebrow="Committed performance evidence" title="Speed without hiding the machine." lead="Every view is rendered from the repository baseline JSON. Runtime, peak memory, dimensions, precision, backend, and quality meaning travel with the number." />
      <section className="section-wrap">
        <div className="provenance-grid">
          <div><small>Machine</small><strong>{environment.platform_system} · {environment.platform_machine}</strong></div>
          <div><small>Runtime</small><strong>Python {environment.python_version} · JAX {environment.jax_version}</strong></div>
          <div><small>Precision</small><strong>{environment.jax_enable_x64 === "1" ? "float64 / X64 enabled" : "float32"} · {environment.jax_default_backend}</strong></div>
        </div>
        <div className="filter-row">{(["20k", "100k", "all"] as const).map((value) => <button className={`filter-chip ${scale === value ? "is-active" : ""}`} key={value} onClick={() => setScale(value)}>{value === "all" ? "all committed runs" : `${value} rows`}</button>)}</div>
        <div className="benchmark-chart" aria-label="Benchmark runtime comparison">
          {runs.map((run) => (
            <div className="benchmark-row" key={`${run.scenario}-${run.rows}`}>
              <code>{run.scenario}</code>
              <span className="benchmark-row__bar"><i style={{width: `${Math.max(1, (run.elapsed_seconds / maximum) * 100)}%`}} /></span>
              <strong>{run.elapsed_seconds < .01 ? `${(run.elapsed_seconds * 1000).toFixed(1)} ms` : `${run.elapsed_seconds.toFixed(2)} s`}</strong>
              <span>{run.dims}D · {run.bins} bins</span>
            </div>
          ))}
        </div>
        <p className="provenance-note" style={{marginTop: 24}}><span aria-hidden="true">◇</span><span>Quality values are intentionally not forced onto one axis: log-determinant objectives and geometric-mean retention answer different questions. Select a run in the canonical benchmark record before comparing quality.</span></p>
      </section>
    </AppShell>
  );
}
