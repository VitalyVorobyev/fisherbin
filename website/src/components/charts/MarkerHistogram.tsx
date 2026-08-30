import {useMemo} from "react";

import {Axes, DEFAULT_FRAME, plotArea} from "./Axes";
import {extent, linearScale, populationColor} from "./scale";
import type {MarkerPanel} from "../../data/showcase";

const FRAME = {...DEFAULT_FRAME, height: 200, marginLeft: 44, width: 340};

interface MarkerHistogramProps {
  panel: MarkerPanel;
  /** Populations to draw, by index. Hiding the dominant one reveals the rest. */
  visible: readonly number[];
}

/**
 * One marker, overlaid per population.
 *
 * Densities rather than counts, because the populations differ in size by two
 * orders of magnitude and raw counts would show only "other".
 */
export function MarkerHistogram({panel, visible}: MarkerHistogramProps): React.JSX.Element {
  const area = plotArea(FRAME);
  const {paths, x, y} = useMemo(() => {
    const shown = panel.series.filter((_, index) => visible.includes(index));
    const peak = Math.max(...shown.flatMap((series) => series.density), 1e-9);
    const xScale = linearScale(extent(panel.edges), [area.left, area.right]);
    const yScale = linearScale([0, peak], [area.bottom, area.top]);
    const built = shown.map((series) => {
      const original = panel.series.indexOf(series);
      // A step outline reads as binned data; a smooth curve would imply a
      // density estimate that was never computed.
      const points: string[] = [];
      series.density.forEach((value, bin) => {
        const left = panel.edges[bin];
        const right = panel.edges[bin + 1];
        if (left === undefined || right === undefined) return;
        points.push(`${String(xScale(left))},${String(yScale(value))}`);
        points.push(`${String(xScale(right))},${String(yScale(value))}`);
      });
      return {color: populationColor(original), label: series.population, points: points.join(" ")};
    });
    return {paths: built, x: xScale, y: yScale};
  }, [area.bottom, area.left, area.right, area.top, panel, visible]);

  return (
    <figure className="chart-figure">
      <svg viewBox={`0 0 ${String(FRAME.width)} ${String(FRAME.height)}`} role="img">
        <title>{`${panel.marker} intensity distribution by cell population`}</title>
        <desc>
          {`Binned intensity densities for ${panel.marker}, one outline per shown population.`}
        </desc>
        <Axes frame={FRAME} x={x} y={y} yTickCount={3} xTickCount={4} />
        {paths.map((path) => (
          <polyline key={path.label} className="chart-step" points={path.points} stroke={path.color} />
        ))}
      </svg>
      <figcaption>{panel.marker}</figcaption>
    </figure>
  );
}
