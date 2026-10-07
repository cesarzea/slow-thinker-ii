import {getBezierPath, getSimpleBezierPath, Position} from '@xyflow/react';
import type {PortSide} from '../../state/port-sides.ts';
import {step} from './geometry.ts';
import type {Point} from './geometry.ts';
import type {HandleEnd} from './scene.ts';

const POSITIONS: Readonly<Record<PortSide, Position>> = {
  left: Position.Left,
  right: Position.Right,
  top: Position.Top,
  bottom: Position.Bottom,
};
const SAMPLES = 24;
/** How far along a handle's side its port name may move. */
const GUIDE = 120;

/** How far a control point lies from its handle, as React Flow's `getBezierPath` does it. */
function controlOffset(distance: number, curvature: number): number {
  return distance >= 0 ? 0.5 * distance : curvature * 25 * Math.sqrt(-distance);
}

function control(side: PortSide, from: Point, to: Point, curvature: number): Point {
  const offset = (distance: number): number => controlOffset(distance, curvature);
  const offsets: Readonly<Record<PortSide, Point>> = {
    left: {x: from.x - offset(from.x - to.x), y: from.y},
    right: {x: from.x + offset(to.x - from.x), y: from.y},
    top: {x: from.x, y: from.y - offset(from.y - to.y)},
    bottom: {x: from.x, y: from.y + offset(to.y - from.y)},
  };
  return offsets[side];
}

/** Points along a cubic curve, from its start to its end. */
function sampled(start: Point, first: Point, second: Point, end: Point): Point[] {
  return Array.from({length: SAMPLES + 1}, (_, index) => {
    const t = index / SAMPLES;
    const [a, b, c, d] = [(1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3];
    return {
      x: a * start.x + b * first.x + c * second.x + d * end.x,
      y: a * start.y + b * first.y + c * second.y + d * end.y,
    };
  });
}

/** React Flow's simple bezier: each control point halfway towards the other end, on its axis. */
function simpleControl(side: PortSide, from: Point, to: Point): Point {
  return side === 'left' || side === 'right'
    ? {x: (from.x + to.x) / 2, y: from.y}
    : {x: from.x, y: (from.y + to.y) / 2};
}

interface Ends {
  readonly source: HandleEnd;
  readonly target: HandleEnd;
}
interface Curve {
  readonly path: string;
  readonly points: readonly Point[];
  readonly guide: readonly Point[];
  readonly middle: Point;
}

function ends({source, target}: Ends) {
  return {
    sourceX: source.x,
    sourceY: source.y,
    sourcePosition: POSITIONS[source.side],
    targetX: target.x,
    targetY: target.y,
    targetPosition: POSITIONS[target.side],
  };
}

/**
 * The curve React Flow draws between two handles, with points along it for what must keep
 * clear of it, and a straight guide out of the source handle along which its name goes.
 * Without a curvature, React Flow's simple bezier.
 */
export function curve({source, target}: Ends, curvature: number | null): Curve {
  const [path, x, y] =
    curvature === null
      ? getSimpleBezierPath(ends({source, target}))
      : getBezierPath({...ends({source, target}), curvature});
  const first =
    curvature === null
      ? simpleControl(source.side, source, target)
      : control(source.side, source, target, curvature);
  const second =
    curvature === null
      ? simpleControl(target.side, target, source)
      : control(target.side, target, source, curvature);
  return {
    path,
    points: sampled(source, first, second, target),
    guide: [source, step(source, source.side, GUIDE)],
    middle: {x, y},
  };
}
