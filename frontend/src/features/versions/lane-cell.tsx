import type {ReactElement} from 'react';
import type {LaneRow} from './lanes.ts';

const STEP = 14;
const LEFT = 7;
/** The dot's height: level with the version badge. */
const DOT = 19;
const COLORS = 5;

const x = (lane: number): number => LEFT + lane * STEP;
const tone = (lane: number): string => `lane-${String(lane % COLORS)}`;

/** The width the lanes of a graph take. */
export function lanesWidth(lanes: number): number {
  return LEFT * 2 + Math.max(lanes - 1, 0) * STEP;
}

function curve(from: number, to: number): string {
  const [start, end, dot] = [String(x(from)), String(x(to)), String(DOT)];
  return `M ${start} 0 C ${start} ${dot}, ${end} 0, ${end} ${dot}`;
}

/** Lines crossing the row, leaving the dot downwards and arriving at it from above. */
function Lines({row}: {readonly row: LaneRow}): ReactElement {
  const here = x(row.lane);
  return (
    <>
      {row.through.map((lane) => (
        <line
          key={`t${String(lane)}`}
          className={tone(lane)}
          x1={x(lane)}
          x2={x(lane)}
          y1={0}
          y2="100%"
        />
      ))}
      {row.down && <line className={tone(row.lane)} x1={here} x2={here} y1={DOT} y2="100%" />}
      {row.into.map((lane) => (
        <path key={`i${String(lane)}`} className={tone(lane)} d={curve(lane, row.lane)} />
      ))}
    </>
  );
}

/** The lines and the dot of one version row; decorative, the row's text says the same. */
export function LaneCell(props: {
  readonly row: LaneRow;
  readonly lanes: number;
  readonly active: boolean;
}): ReactElement {
  const {row} = props;
  return (
    <svg className="lanes" width={lanesWidth(props.lanes)} aria-hidden="true" focusable="false">
      <Lines row={row} />
      <circle
        className={`${tone(row.lane)}${props.active ? ' active' : ''}`}
        cx={x(row.lane)}
        cy={DOT}
        r={props.active ? 5.5 : 4}
      />
    </svg>
  );
}
