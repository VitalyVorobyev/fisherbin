import {useMemo} from "react";

import {Axes, DEFAULT_FRAME, Legend, plotArea} from "./Axes";
import {extent, linearScale} from "./scale";
import type {MethodSeries} from "../../data/showcase";

const FRAME = {...DEFAULT_FRAME, height: 320, marginLeft: 74, width: 620};

const SCOREQUANT_COLORS = ["#2b77f3", "#20bfae", "#8b5cf6"];

// The baselines need to be distinguishable from each other as well as from
// ScoreQuant: four identical grey dashes are one line as far as a reader is
// concerned, and the legend would name four things it cannot point at. Muted
// hues keep them visibly secondary while staying separable.
const BASELINE_COLORS = ["#94a3b8", "#a1785c", "#7d8fa8", "#b0894f"];

interface MethodComparisonProps {
  baseline: {label: string; macroRmse: number};
  methods: MethodSeries[];
}

/**
 * Held-out estimation error against the bin budget.
 *
 * The vertical axis is logarithmic because the methods span two decades: on a
 * linear axis every ScoreQuant curve collapses onto the floor and the reader
 * cannot see that they separate from each other at all.
 */
export function MethodComparison({baseline, methods}: MethodComparisonProps): React.JSX.Element {
  const area = plotArea(FRAME);
  const {lines, x, y} = useMemo(() => {
    const allBins = methods.flatMap((method) => method.points.map((point) => point.bins));
    const allErrors = [
      ...methods.flatMap((method) => method.points.map((point) => Math.log10(point.macroRmse))),
      Math.log10(baseline.macroRmse),
    ];
    const xScale = linearScale(extent(allBins), [area.left, area.right]);
    const yScale = linearScale(extent(allErrors), [area.bottom, area.top]);
    let quantIndex = 0;
    let baselineIndex = 0;
    const built = methods.map((method) => {
      const color = method.isScoreQuant
        ? (SCOREQUANT_COLORS[quantIndex++ % SCOREQUANT_COLORS.length] ?? "#2b77f3")
        : (BASELINE_COLORS[baselineIndex++ % BASELINE_COLORS.length] ?? "#94a3b8");
      return {
        color,
        dashed: !method.isScoreQuant,
        label: method.label,
        marks: method.points.map((point) => ({
          cx: xScale(point.bins),
          cy: yScale(Math.log10(point.macroRmse)),
        })),
        points: method.points
          .map((point) => `${String(xScale(point.bins))},${String(yScale(Math.log10(point.macroRmse)))}`)
          .join(" "),
      };
    });
    return {lines: built, x: xScale, y: yScale};
  }, [area.bottom, area.left, area.right, area.top, baseline.macroRmse, methods]);

  const baselineY = y(Math.log10(baseline.macroRmse));
  return (
    <figure className="chart-figure chart-figure--wide">
      <svg viewBox={`0 0 ${String(FRAME.width)} ${String(FRAME.height)}`} role="img">
        <title>Held-out macro RMSE against bin budget, by binning method</title>
        <desc>
          Lower is better. ScoreQuant methods are drawn solid and coloured; convenience baselines
          are dashed and grey. The horizontal line is the unbinned classifier-ratio estimate.
        </desc>
        <Axes
          frame={FRAME}
          x={x}
          xLabel="bins"
          xTickCount={6}
          y={y}
          yLabel="log₁₀ macro RMSE"
          yTickCount={4}
        />
        <line className="chart-reference" x1={area.left} x2={area.right} y1={baselineY} y2={baselineY} />
        <text className="chart-annotation" x={area.right - 4} y={baselineY - 6} textAnchor="end">
          {baseline.label}
        </text>
        {lines.map((line) => (
          <g key={line.label}>
            <polyline
              className={line.dashed ? "chart-line chart-line--baseline" : "chart-line"}
              points={line.points}
              stroke={line.color}
            />
            {line.marks.map((mark, index) => (
              <circle key={`${line.label}-${String(index)}`} cx={mark.cx} cy={mark.cy} r={3} fill={line.color} />
            ))}
          </g>
        ))}
      </svg>
      <Legend
        entries={[
          ...lines.map((line) => ({color: line.color, label: line.label})),
          {color: "#64748b", label: baseline.label},
        ]}
      />
    </figure>
  );
}
