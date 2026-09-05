import {benchmarkScenarios, qualityLabels} from "../data/benchmarkScenarios";
import type {BenchmarkRun} from "../data/portal";

/** Quality labels reporting a fraction of retained Fisher information, formatted as a percentage. */
const RETENTION_LABELS = new Set(["geometric_mean_retention", "held_out_geometric_mean_retention"]);

/**
 * Format a run's ``quality`` value using the convention its ``quality_label`` implies:
 * a log-determinant objective to three decimals, a geometric-mean retention as a
 * percentage with one decimal.
 */
function formatQuality(run: BenchmarkRun): string {
  if (RETENTION_LABELS.has(run.quality_label)) {
    return `${(run.quality * 100).toFixed(1)}%`;
  }
  return run.quality.toFixed(3);
}

function formatElapsed(elapsedSeconds: number): string {
  return elapsedSeconds < 0.01 ? `${(elapsedSeconds * 1000).toFixed(1)} ms` : `${elapsedSeconds.toFixed(2)} s`;
}

interface BenchmarkTableProps {
  runs: readonly BenchmarkRun[];
}

/**
 * Render the committed benchmark rows: what each scenario measures, its stopping
 * rule, and its timing, in that order. Extracted from the ``benchmarks`` page so
 * it can be rendered without Docusaurus's ``Layout`` context under Vitest.
 */
export function BenchmarkTable({runs}: BenchmarkTableProps): React.JSX.Element {
  const maximum = Math.max(...runs.map((run) => run.elapsed_seconds), 0.001);
  return (
    <div className="benchmark-chart" aria-label="Benchmark runtime and quality comparison">
      {runs.map((run) => {
        const scenario = benchmarkScenarios[run.scenario];
        const task = scenario?.task ?? run.scenario;
        const stop = scenario?.stop ?? "n/a";
        const qualityLabel = qualityLabels[run.quality_label] ?? run.quality_label;
        return (
          <div aria-label={`${task} benchmark row`} className="benchmark-row" key={`${run.scenario}-${run.rows}`}>
            <span className="benchmark-row__task">
              {task}
              <code>{run.scenario}</code>
            </span>
            <span className="benchmark-row__quality">
              <strong>{formatQuality(run)}</strong>
              <small>{qualityLabel}</small>
            </span>
            <span className="benchmark-row__stop">{stop}</span>
            <span className="benchmark-row__bar"><i style={{width: `${Math.max(1, (run.elapsed_seconds / maximum) * 100)}%`}} /></span>
            <strong>{formatElapsed(run.elapsed_seconds)}</strong>
            <span>{run.dims}D · {run.bins} bins</span>
          </div>
        );
      })}
    </div>
  );
}
