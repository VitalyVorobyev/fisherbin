import Layout from "@theme/Layout";
import {useMemo, useState} from "react";

import {BenchmarkTable} from "../components/BenchmarkTable";
import {PageIntro} from "../components/PageIntro";
import {portalData} from "../data/portal";

export default function Benchmarks(): React.JSX.Element {
  const [scale, setScale] = useState<"all" | "20k" | "100k">("20k");
  const runs = useMemo(() => portalData.benchmarks.runs.filter((run) => scale === "all" || (scale === "20k" ? run.rows === 20_000 : run.rows === 100_000)), [scale]);
  const environment = portalData.benchmarks.environment;
  return (
    <Layout title="Benchmarks" description="Data-driven ScoreQuant speed, scale, memory, and quality evidence.">
      <PageIntro eyebrow="Committed performance evidence" title="What was measured, and on what machine" lead="Every view is rendered from the repository baseline JSON. Runtime, peak memory, dimensions, precision, backend, and quality meaning travel with the number." />
      <section className="section-wrap">
        <div className="provenance-grid">
          <div><small>Machine</small><strong>{environment.platform_system} · {environment.platform_machine}</strong></div>
          <div><small>Runtime</small><strong>Python {environment.python_version} · JAX {environment.jax_version}</strong></div>
          <div><small>Precision</small><strong>{environment.jax_enable_x64 === "1" ? "float64 / X64 enabled" : "float32"} · {environment.jax_default_backend}</strong></div>
        </div>
        <div className="filter-row">{(["20k", "100k", "all"] as const).map((value) => <button className={`filter-chip ${scale === value ? "is-active" : ""}`} key={value} onClick={() => setScale(value)}>{value === "all" ? "all committed runs" : `${value} rows`}</button>)}</div>
        <BenchmarkTable runs={runs} />
        <p className="provenance-note" style={{marginTop: 24}}><span aria-hidden="true">◇</span><span>Quality is exact for the seed and code path each row records, and is what to compare first; runtime varies by machine.</span></p>
      </section>
    </Layout>
  );
}
