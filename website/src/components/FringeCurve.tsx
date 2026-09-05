import {useId, useMemo} from "react";

import {linearScale} from "./charts/scale";
import {michelsonSweep} from "../data/michelsonSweep";

export interface FringeCurveProps {
  caption: React.ReactNode;
  segments?: number;
}

const WIDTH = 560;
const HEIGHT = 230;
const MARGIN = {bottom: 34, left: 34, right: 16, top: 16};
const SAMPLES = 400;

/** One fringe-boundary tick: a fraction of `uMax` at a whole multiple of `2*PI`, and its label. */
interface FringeTick {
  label: string;
  u: number;
}

function fringeTicks(fringes: number): FringeTick[] {
  return Array.from({length: fringes + 1}, (_, index) => ({
    label: index === 0 ? "0" : `${String(index * 2)}π`,
    u: index * 2 * Math.PI
  }));
}

/**
 * The fringe intensity law, `y = 1 + V * cos(u)`, along the aperture.
 *
 * `V` (visibility) and `uMax` come straight from the committed Michelson
 * sweep evidence (`michelsonSweep.visibility`, `.uMax`), never a literal
 * here. Equal-width segment boundaries are drawn underneath the curve as
 * dashed lines with a faint alternating fill, so a reader sees the fixed
 * detector geometry beating against the fringe pattern it must resolve.
 */
export function FringeCurve({caption, segments = michelsonSweep.headlineBins}: FringeCurveProps): React.JSX.Element {
  const titleId = useId();
  const {fringes, uMax, visibility} = michelsonSweep;

  const {curvePath, plotHeight, plotWidth, scaleX, scaleY, segmentBoundaries, ticks} = useMemo(() => {
    const width = WIDTH - MARGIN.left - MARGIN.right;
    const height = HEIGHT - MARGIN.top - MARGIN.bottom;
    const x = linearScale([0, uMax], [0, width]);
    const y = linearScale([1 - visibility, 1 + visibility], [height, 0]);

    const points = Array.from({length: SAMPLES}, (_, index) => {
      const u = (uMax * index) / (SAMPLES - 1);
      const value = 1 + visibility * Math.cos(u);
      return `${index === 0 ? "M" : "L"}${String(x(u))} ${String(y(value))}`;
    });

    const step = uMax / segments;
    const boundaries = Array.from({length: Math.max(segments - 1, 0)}, (_, index) => (index + 1) * step);

    return {
      curvePath: points.join(" "),
      plotHeight: height,
      plotWidth: width,
      scaleX: x,
      scaleY: y,
      segmentBoundaries: boundaries,
      ticks: fringeTicks(fringes)
    };
  }, [fringes, segments, uMax, visibility]);

  const description = `Fringe intensity across ${String(fringes)} fringes, overlaid with ${String(segments)} equal detector segments.`;
  const maxY = MARGIN.top + scaleY(1 + visibility);
  const minY = MARGIN.top + scaleY(1 - visibility);

  return (
    <figure className="chart-figure fringe-curve">
      <svg viewBox={`0 0 ${String(WIDTH)} ${String(HEIGHT)}`} role="img" aria-labelledby={titleId} width="100%">
        <title id={titleId}>Fringe intensity along the aperture</title>
        <desc>{description}</desc>

        {Array.from({length: segments}, (_, index) => index)
          .filter((index) => index % 2 === 0)
          .map((index) => (
            <rect
              key={`segment-fill-${String(index)}`}
              className="fringe-curve__segment-fill"
              x={MARGIN.left + scaleX((index * uMax) / segments)}
              y={MARGIN.top}
              width={Math.max(scaleX(uMax / segments), 0)}
              height={plotHeight}
            />
          ))}

        {ticks.map((tick) => (
          <line
            key={`grid-${tick.label}`}
            className="chart-grid"
            x1={MARGIN.left + scaleX(tick.u)}
            x2={MARGIN.left + scaleX(tick.u)}
            y1={MARGIN.top}
            y2={MARGIN.top + plotHeight}
          />
        ))}

        {segmentBoundaries.map((u, index) => (
          <line
            key={`segment-boundary-${String(index)}`}
            className="fringe-curve__segment-boundary"
            x1={MARGIN.left + scaleX(u)}
            x2={MARGIN.left + scaleX(u)}
            y1={MARGIN.top}
            y2={MARGIN.top + plotHeight}
          />
        ))}

        <line className="chart-reference" x1={MARGIN.left} x2={MARGIN.left + plotWidth} y1={maxY} y2={maxY} />
        <line className="chart-reference" x1={MARGIN.left} x2={MARGIN.left + plotWidth} y1={minY} y2={minY} />
        <text className="chart-tick" x={MARGIN.left - 6} y={maxY + 4} textAnchor="end">
          {(1 + visibility).toFixed(2)}
        </text>
        <text className="chart-tick" x={MARGIN.left - 6} y={minY + 4} textAnchor="end">
          {(1 - visibility).toFixed(2)}
        </text>

        <path className="chart-line fringe-curve__curve" d={curvePath} transform={`translate(${String(MARGIN.left)} ${String(MARGIN.top)})`} />

        <line
          className="chart-axis"
          x1={MARGIN.left}
          x2={MARGIN.left + plotWidth}
          y1={MARGIN.top + plotHeight}
          y2={MARGIN.top + plotHeight}
        />
        {ticks.map((tick) => (
          <text
            key={`tick-${tick.label}`}
            className="chart-tick"
            x={MARGIN.left + scaleX(tick.u)}
            y={MARGIN.top + plotHeight + 16}
            textAnchor="middle"
          >
            {tick.label}
          </text>
        ))}
        <text className="chart-axis-label" x={MARGIN.left + plotWidth / 2} y={HEIGHT - 4} textAnchor="middle">
          Position along the aperture, in fringes
        </text>
      </svg>
      <figcaption>{caption}</figcaption>
    </figure>
  );
}
