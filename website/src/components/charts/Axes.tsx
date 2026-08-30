import {formatTick, type Scale} from "./scale";

export interface PlotFrame {
  height: number;
  marginBottom: number;
  marginLeft: number;
  marginRight: number;
  marginTop: number;
  width: number;
}

/** A frame with room for the axis labels most panels on this page need. */
export const DEFAULT_FRAME: PlotFrame = {
  height: 260,
  marginBottom: 38,
  // Wide enough for a rotated axis label outside the tick column; a narrower
  // margin clips the label against the viewBox edge.
  marginLeft: 56,
  marginRight: 16,
  marginTop: 16,
  width: 520,
};

export function plotArea(frame: PlotFrame): {
  bottom: number;
  left: number;
  right: number;
  top: number;
} {
  return {
    bottom: frame.height - frame.marginBottom,
    left: frame.marginLeft,
    right: frame.width - frame.marginRight,
    top: frame.marginTop,
  };
}

interface AxesProps {
  frame: PlotFrame;
  /** Horizontal gridlines make a value comparison possible without a ruler. */
  showGrid?: boolean;
  x: Scale;
  xLabel?: string;
  xTickCount?: number;
  y: Scale;
  yLabel?: string;
  yTickCount?: number;
}

/**
 * Draw both axes, their ticks and optional gridlines.
 *
 * Colours come from the CSS custom properties the rest of the site already
 * defines, so a chart follows the theme without knowing what the theme is.
 */
export function Axes({
  frame,
  showGrid = true,
  x,
  xLabel,
  xTickCount = 5,
  y,
  yLabel,
  yTickCount = 4,
}: AxesProps): React.JSX.Element {
  const area = plotArea(frame);
  return (
    <g className="chart-axes" aria-hidden="true">
      {showGrid &&
        y.ticks(yTickCount).map((tick) => (
          <line key={`grid-${String(tick)}`} className="chart-grid" x1={area.left} x2={area.right} y1={y(tick)} y2={y(tick)} />
        ))}
      <line className="chart-axis" x1={area.left} x2={area.right} y1={area.bottom} y2={area.bottom} />
      <line className="chart-axis" x1={area.left} x2={area.left} y1={area.top} y2={area.bottom} />
      {x.ticks(xTickCount).map((tick) => (
        <text key={`x-${String(tick)}`} className="chart-tick" x={x(tick)} y={area.bottom + 16} textAnchor="middle">
          {formatTick(tick)}
        </text>
      ))}
      {y.ticks(yTickCount).map((tick) => (
        <text key={`y-${String(tick)}`} className="chart-tick" x={area.left - 8} y={y(tick) + 4} textAnchor="end">
          {formatTick(tick)}
        </text>
      ))}
      {xLabel !== undefined && (
        <text className="chart-axis-label" x={(area.left + area.right) / 2} y={frame.height - 4} textAnchor="middle">
          {xLabel}
        </text>
      )}
      {yLabel !== undefined && (
        <text
          className="chart-axis-label"
          textAnchor="middle"
          transform={`translate(14 ${String((area.top + area.bottom) / 2)}) rotate(-90)`}
        >
          {yLabel}
        </text>
      )}
    </g>
  );
}

interface LegendProps {
  entries: {color: string; label: string}[];
}

/** A shared swatch legend, so every panel names its series the same way. */
export function Legend({entries}: LegendProps): React.JSX.Element {
  return (
    <ul className="chart-legend">
      {entries.map((entry) => (
        <li key={entry.label}>
          <span className="chart-swatch" style={{background: entry.color}} aria-hidden="true" />
          {entry.label}
        </li>
      ))}
    </ul>
  );
}
