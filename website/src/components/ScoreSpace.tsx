import {useMemo, useState} from "react";

import {portalData, type ScoreScenario} from "../data/portal";

const palette = ["#2b77f3", "#20bfae", "#86a8ff", "#f0a84b", "#b77ee8"];

function scalePoint(point: number[]): [number, number] {
  return [292 + (point[0] ?? 0) * 112, 208 - (point[1] ?? 0) * 108];
}

function bisector(first: number[], second: number[], index: number): React.JSX.Element {
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
  scenarioOverride?: ScoreScenario;
}

export function ScoreSpace({compact = false, controlledBins, onBinsChange, scenarioOverride}: ScoreSpaceProps): React.JSX.Element {
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
        <g clipPath="url(#plot-clip)" className="score-bisectors">{pairs.map(([a, b], index) => bisector(a, b, index))}</g>
        <g>
          {portalData.scoreSpace.points.map((point, index) => {
            const [cx, cy] = scalePoint(point);
            const label = scenario.labels[index] ?? 0;
            return <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r={compact ? 3.3 : 4.2} fill={palette[label]} fillOpacity=".86"/>;
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
        <span><small>score dimensions</small><strong>2</strong></span>
        <span><small>hard bins</small><strong>{bins}</strong></span>
      </div>
    </div>
  );
}
