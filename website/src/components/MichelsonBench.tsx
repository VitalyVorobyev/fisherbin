import {useId, useMemo} from "react";

export interface MichelsonBenchProps {
  caption: React.ReactNode;
  segments?: number;
}

const WIDTH = 640;
const HEIGHT = 360;

const SOURCE_X = 56;
const AXIS_Y = 180;
const SPLITTER_X = 300;
const SPLITTER_HALF = 24;

const M1_X = 556;
const M1_TOP = 148;
const M1_BOTTOM = 212;

const M2_Y = 50;
const M2_LEFT = 268;
const M2_RIGHT = 332;

const STRIP_X = 170;
const STRIP_Y = 280;
const STRIP_WIDTH = 260;
const STRIP_HEIGHT = 42;

const FRINGE_BANDS = 24;
const FRINGE_CYCLES = 6;

/** One alternating light/dark band of the schematic fringe pattern drawn inside the detector strip. */
interface FringeBand {
  x: number;
  width: number;
  opacity: number;
}

function fringeBands(): FringeBand[] {
  const bandWidth = STRIP_WIDTH / FRINGE_BANDS;
  return Array.from({length: FRINGE_BANDS}, (_, index) => {
    const phase = (index / FRINGE_BANDS) * Math.PI * 2 * FRINGE_CYCLES;
    return {
      opacity: 0.08 + 0.28 * ((1 + Math.cos(phase)) / 2),
      width: bandWidth,
      x: STRIP_X + index * bandWidth
    };
  });
}

/**
 * A schematic Michelson interferometer bench, drawn without any data.
 *
 * Light leaves the source, splits at the beam splitter into a transmitted
 * arm (to mirror M1) and a reflected arm (to mirror M2), recombines at the
 * splitter, and falls on a segmented detector -- the same bench every
 * walkthrough number on this page is measured from, drawn once so a reader
 * has the geometry before the first chart of swept counter counts.
 */
export function MichelsonBench({caption, segments = 6}: MichelsonBenchProps): React.JSX.Element {
  const titleId = useId();
  const descId = useId();

  const bands = useMemo(() => fringeBands(), []);
  const cellWidth = STRIP_WIDTH / segments;
  const cells = Array.from({length: segments}, (_, index) => index);

  const description = `Light from the source splits at the beam splitter into two arms, each folded back by a mirror, and the recombined beam falls on a segmented detector of ${String(segments)} counters.`;

  return (
    <figure className="chart-figure michelson-bench">
      <svg
        viewBox={`0 0 ${String(WIDTH)} ${String(HEIGHT)}`}
        role="img"
        aria-labelledby={`${titleId} ${descId}`}
        width="100%"
      >
        <title id={titleId}>Michelson interferometer bench</title>
        <desc id={descId}>{description}</desc>

        {/* Arm 2: splitter to mirror M2, straight up. */}
        <line
          className="michelson-bench__beam"
          x1={SPLITTER_X}
          y1={AXIS_Y - SPLITTER_HALF / 2}
          x2={SPLITTER_X}
          y2={M2_Y + 8}
        />
        <line
          className="michelson-bench__mirror"
          x1={M2_LEFT}
          y1={M2_Y}
          x2={M2_RIGHT}
          y2={M2_Y}
        />
        <text className="michelson-bench__label" x={SPLITTER_X} y={M2_Y - 16} textAnchor="middle">
          mirror
        </text>

        {/* Source to splitter. */}
        <circle className="michelson-bench__source" cx={SOURCE_X} cy={AXIS_Y} r={9} />
        <line className="michelson-bench__beam" x1={SOURCE_X + 14} y1={AXIS_Y} x2={SPLITTER_X - SPLITTER_HALF} y2={AXIS_Y} />
        <text className="michelson-bench__label" x={SOURCE_X} y={AXIS_Y + 25} textAnchor="middle">
          source
        </text>

        {/* Arm 1: splitter to mirror M1, straight right. */}
        <line
          className="michelson-bench__beam"
          x1={SPLITTER_X + SPLITTER_HALF / 2}
          y1={AXIS_Y}
          x2={M1_X - 8}
          y2={AXIS_Y}
        />
        <line
          className="michelson-bench__mirror"
          x1={M1_X}
          y1={M1_TOP}
          x2={M1_X}
          y2={M1_BOTTOM}
        />
        <text className="michelson-bench__label" x={M1_X} y={M1_BOTTOM + 22} textAnchor="middle">
          mirror
        </text>

        {/* The beam splitter plate itself, a 45-degree line at the crossing. */}
        <line
          className="michelson-bench__splitter"
          x1={SPLITTER_X - SPLITTER_HALF}
          y1={AXIS_Y + SPLITTER_HALF}
          x2={SPLITTER_X + SPLITTER_HALF}
          y2={AXIS_Y - SPLITTER_HALF}
        />
        <text className="michelson-bench__label" x={SPLITTER_X + SPLITTER_HALF + 20} y={AXIS_Y - SPLITTER_HALF + 5} textAnchor="start">
          beam splitter
        </text>

        {/* Recombined beam, splitter down to the detector. */}
        <line
          className="michelson-bench__beam"
          x1={SPLITTER_X}
          y1={AXIS_Y + SPLITTER_HALF / 2}
          x2={SPLITTER_X}
          y2={STRIP_Y - 2}
        />
        <text className="michelson-bench__label" x={STRIP_X} y={STRIP_Y - 12} textAnchor="start">
          detector
        </text>

        {/* Detector: the fringe pattern first, then the segment cells on top. */}
        <g>
          {bands.map((band, index) => (
            <rect
              key={`fringe-${String(index)}`}
              x={band.x}
              y={STRIP_Y}
              width={band.width}
              height={STRIP_HEIGHT}
              className="michelson-bench__fringe"
              opacity={band.opacity}
            />
          ))}
        </g>
        <rect
          className="michelson-bench__strip"
          x={STRIP_X}
          y={STRIP_Y}
          width={STRIP_WIDTH}
          height={STRIP_HEIGHT}
        />
        {cells.map((cell) => (
          <rect
            key={`cell-${String(cell)}`}
            data-testid="bench-segment"
            className="michelson-bench__cell"
            x={STRIP_X + cell * cellWidth}
            y={STRIP_Y}
            width={cellWidth}
            height={STRIP_HEIGHT}
          />
        ))}
        <text className="chart-axis-label" x={STRIP_X + STRIP_WIDTH / 2} y={STRIP_Y + STRIP_HEIGHT + 20} textAnchor="middle">
          {`segmented detector, ${String(segments)} counters`}
        </text>
      </svg>
      <figcaption>{caption}</figcaption>
    </figure>
  );
}
