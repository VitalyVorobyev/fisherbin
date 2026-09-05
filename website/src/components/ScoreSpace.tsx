import {useMemo, useState} from "react";

import {portalData, type ScoreRegions, type ScoreScenario} from "../data/portal";

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

/**
 * Rasterize the compiled cell regions ``scenario.regions`` carries.
 *
 * The rule drawn here is the compiled Mahalanobis rule
 * `argmin_b (s - mu_b)^T M (s - mu_b)`, with `M` the scenario's exported
 * `metric` -- the inverse retained information Theorem 3 makes canonical for
 * an exchange-stable D partition (see `PartitionResult.compile_quantizer`).
 * The picture below is therefore a raster of that library-computed rule, one
 * label per grid cell from `predict_scores`, rather than a geometric
 * construction: a general Mahalanobis Voronoi boundary has no closed form a
 * handful of line segments could draw exactly.
 *
 * Equal labels adjacent within a row are merged into one `<rect>` (a simple
 * run-length pass per row) to keep the DOM to a few dozen elements instead of
 * one per grid cell.
 */
function regionRects(scalePoint: Projector, regions: ScoreRegions): React.JSX.Element[] {
  const {labels, nx, ny, x0, x1, y0, y1} = regions;
  const dx = (x1 - x0) / nx;
  const dy = (y1 - y0) / ny;
  const rects: React.JSX.Element[] = [];
  for (let row = 0; row < ny; row += 1) {
    let runStart = 0;
    for (let column = 0; column <= nx; column += 1) {
      const atRowEnd = column === nx;
      const label = labels.charCodeAt(row * nx + runStart) - 48;
      if (atRowEnd || labels.charCodeAt(row * nx + column) - 48 !== label) {
        const [cornerAX, cornerAY] = scalePoint([x0 + runStart * dx, y0 + row * dy]);
        const [cornerBX, cornerBY] = scalePoint([x0 + column * dx, y0 + (row + 1) * dy]);
        rects.push(
          <rect
            key={`${row}-${runStart}`}
            x={Math.min(cornerAX, cornerBX)}
            y={Math.min(cornerAY, cornerBY)}
            width={Math.abs(cornerBX - cornerAX)}
            height={Math.abs(cornerBY - cornerAY)}
            fill={palette[label % palette.length]}
            fillOpacity={0.16}
          />
        );
        runStart = column;
      }
    }
  }
  return rects;
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
  // The exported regions were rasterized in 2D score space; above that, this
  // picture is already a projection and the regions would not describe it.
  const drawableRegions = dimensions <= 2 ? scenario.regions : undefined;
  const regions = useMemo(
    () => (drawableRegions === undefined ? [] : regionRects(scalePoint, drawableRegions)),
    [drawableRegions, scalePoint]
  );
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
        <span><i className="status-dot"/> committed fixture</span>
        {!compact && (
          <label>Bins <input type="range" min="3" max="5" value={bins} onChange={(event) => setBins(Number(event.target.value))}/><strong>{bins}</strong></label>
        )}
      </div>
      <svg viewBox="0 0 600 410" role="img" aria-label={`Score-space partition with ${bins} bins`}>
        <defs><clipPath id="plot-clip"><rect x="24" y="18" width="552" height="354" rx="8"/></clipPath></defs>
        <g className="score-grid"><path d="M24 106H576M24 194H576M24 282H576M162 18V372M300 18V372M438 18V372"/></g>
        {regions.length > 0 && (
          <g clipPath="url(#plot-clip)" className="score-regions">{regions}</g>
        )}
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
