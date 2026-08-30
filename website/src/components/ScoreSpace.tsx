import {useMemo, useState} from "react";

import {portalData, type ScoreScenario} from "../data/portal";

const palette = ["#2b77f3", "#20bfae", "#86a8ff", "#f0a84b", "#b77ee8"];

type Projector = (point: readonly number[]) => [number, number];

/**
 * Fit the plot to the data rather than to one fixture's scale.
 *
 * The original mapping was tuned for a standard-normal fixture. A real mixture
 * score has a range several times wider, and under a fixed scale nearly every
 * point lands outside the frame -- the plot looked empty while reporting a
 * perfectly good fit. Bounds come from the 1st-99th percentile so a few extreme
 * rows cannot squeeze everything else into the middle pixel.
 */
function makeProjector(points: readonly (readonly number[])[], quantile: number): Projector {
  const bounds = (axis: number): [number, number] => {
    const values = points.map((point) => point[axis] ?? 0).sort((a, b) => a - b);
    if (values.length === 0) return [-2.6, 2.6];
    const low = values[Math.floor((values.length - 1) * quantile)] ?? 0;
    const high = values[Math.ceil((values.length - 1) * (1 - quantile))] ?? 0;
    const pad = (high - low) * 0.08 || 1;
    return [low - pad, high + pad];
  };
  const [x0, x1] = bounds(0);
  const [y0, y1] = bounds(1);
  const spanX = x1 - x0 || 1;
  const spanY = y1 - y0 || 1;
  return (point) => [
    36 + ((( point[0] ?? 0) - x0) / spanX) * 528,
    360 - (((point[1] ?? 0) - y0) / spanY) * 330
  ];
}

function bisector(scalePoint: Projector, first: readonly number[], second: readonly number[], index: number): React.JSX.Element {
  const [x1, y1] = scalePoint(first);
  const [x2, y2] = scalePoint(second);
  const middleX = (x1 + x2) / 2;
  const middleY = (y1 + y2) / 2;
  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.hypot(dx, dy) || 1;
  const px = (-dy / length) * 460;
  const py = (dx / length) * 460;
  return <line key={`${index}-${middleX}`} x1={middleX - px} y1={middleY - py} x2={middleX + px} y2={middleY + py} />;
}

interface ScoreSpaceProps {
  compact?: boolean;
  controlledBins?: number;
  onBinsChange?: (bins: number) => void;
  /** Points to draw. Defaults to the committed Gaussian fixture. */
  pointsOverride?: readonly (readonly number[])[];
  scenarioOverride?: ScoreScenario;
  /** Shown instead of the plot when there is nothing meaningful to draw yet. */
  placeholder?: string;
}

export function ScoreSpace({compact = false, controlledBins, onBinsChange, placeholder, pointsOverride, scenarioOverride}: ScoreSpaceProps): React.JSX.Element {
  const [localBins, setLocalBins] = useState(4);
  const bins = controlledBins ?? localBins;
  const scenario = scenarioOverride ?? portalData.scoreSpace.scenarios[String(bins)];
  if (scenario === undefined) throw new Error(`No generated score-space fixture exists for ${bins} bins.`);
  const pairs = useMemo(
    () => scenario.centers.flatMap((center, index) => scenario.centers.slice(index + 1).map((other) => [center, other] as const)),
    [scenario]
  );
  const setBins = (value: number): void => {
    setLocalBins(value);
    onBinsChange?.(value);
  };
  const points = pointsOverride ?? portalData.scoreSpace.points;
  // A mixture score is heavy-tailed: a handful of cells sit orders of magnitude
  // out, and bounds that contain them squeeze everything else into one pixel.
  // The frame therefore holds the central bulk and the rest is clipped, which
  // the caption states rather than leaving the reader to infer an empty plot.
  const heavyTailed = (points[0]?.length ?? 2) > 2;
  const scalePoint = useMemo(
    () => makeProjector([...points, ...scenario.centers], heavyTailed ? 0.08 : 0.01),
    [heavyTailed, points, scenario.centers]
  );
  // Above two dimensions the picture is a projection onto the first two
  // coordinates; the caller says so beside the plot.
  const dimensions = points[0]?.length ?? 2;
  // A large table would draw tens of thousands of overlapping circles for no
  // added information, so the plot samples it evenly and says nothing it cannot
  // show honestly.
  const stride = Math.max(1, Math.ceil(points.length / 1500));
  const drawn = stride === 1 ? points : points.filter((_, index) => index % stride === 0);
  const clipped = drawn.filter((point) => {
    const [x, y] = scalePoint(point);
    return x < 24 || x > 576 || y < 18 || y > 372;
  }).length;

  if (placeholder !== undefined) {
    return (
      <div className={compact ? "score-space score-space--compact" : "score-space"}>
        <p className="score-space__placeholder">{placeholder}</p>
      </div>
    );
  }

  return (
    <div className={compact ? "score-space score-space--compact" : "score-space"}>
      <div className="score-space__toolbar">
        <span><i className="status-dot"/> live fixture</span>
        {!compact && (
          <label>Bins <input type="range" min="3" max="5" value={bins} onChange={(event) => setBins(Number(event.target.value))}/><strong>{bins}</strong></label>
        )}
      </div>
      <svg viewBox="0 0 600 410" role="img" aria-label={`Score-space partition with ${bins} bins`}>
        <defs><clipPath id="plot-clip"><rect x="24" y="18" width="552" height="354" rx="8"/></clipPath></defs>
        <g className="score-grid"><path d="M24 106H576M24 194H576M24 282H576M162 18V372M300 18V372M438 18V372"/></g>
        <g clipPath="url(#plot-clip)" className="score-bisectors">{pairs.map(([a, b], index) => bisector(scalePoint, a, b, index))}</g>
        <g>
          {drawn.map((point, index) => {
            const [cx, cy] = scalePoint(point);
            const label = scenario.labels[index * stride] ?? 0;
            return <circle key={`${String(index)}-${cx}-${cy}`} cx={cx} cy={cy} r={compact ? 3.3 : 4.2} fill={palette[label % palette.length]} fillOpacity={stride === 1 ? ".86" : ".55"}/>;
          })}
          {scenario.centers.map((center, index) => {
            const [cx, cy] = scalePoint(center);
            return <g key={`${cx}-${cy}`} className="score-center"><circle cx={cx} cy={cy} r="10"/><path d={`M${cx - 4} ${cy}h8M${cx} ${cy - 4}v8`}/><title>Bin {index + 1} center</title></g>;
          })}
        </g>
        <text x="560" y="397">s₁</text><text x="8" y="30">s₂</text>
      </svg>
      <div className="score-space__metrics">
        <span><small>D-efficiency</small><strong>{(scenario.retention * 100).toFixed(1)}%</strong></span>
        <span><small>score dimensions</small><strong>{dimensions}</strong></span>
        <span><small>hard bins</small><strong>{bins}</strong></span>
      </div>
      {clipped > 0 && (
        <p className="score-space__note">
          {`${Math.round((clipped / drawn.length) * 100)}% of the plotted rows fall outside this frame. The score distribution has long tails, so the view holds the bulk rather than compressing everything into the centre.`}
        </p>
      )}
    </div>
  );
}
