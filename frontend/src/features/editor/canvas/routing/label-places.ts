import {lineBox} from './geometry.ts';
import type {Box, Point} from './geometry.ts';

export interface Size {
  readonly width: number;
  readonly height: number;
}
/** A place for a label; a lower rank is nearer the source. */
export interface Place {
  readonly box: Box;
  readonly rank: number;
}

/** Between a line and its label. */
const GAP = 4;
/** From the handle along the first piece. */
const CLEAR = 8;
const STEP = 6;
const OFFSETS = 24;
/** Half the width a line keeps clear. */
const LINE = 2;
/** How many pieces from the source a label may move along. */
const PIECES = 3;

/** The two places beside a straight piece of route, `offset` along it from its start. */
function beside(from: Point, to: Point, offset: number, size: Size): Box[] {
  const {width, height} = size;
  if (from.y === to.y) {
    const x = to.x >= from.x ? from.x + offset : from.x - offset - width;
    return [
      {x, y: from.y - GAP - height, width, height},
      {x, y: from.y + GAP, width, height},
    ];
  }
  const y = to.y >= from.y ? from.y + offset : from.y - offset - height;
  return [
    {x: from.x - GAP - width, y, width, height},
    {x: from.x + GAP, y, width, height},
  ];
}

/**
 * Places on both sides along the route's first pieces, from the source on and by rank: a
 * label may reach past the end of a piece when the route turns away from it.
 */
export function places(points: readonly Point[], size: Size): Place[] {
  return points.slice(0, PIECES).flatMap((from, index) => {
    const to = points[index + 1];
    if (to === undefined) return [];
    const length = Math.abs(to.x - from.x) + Math.abs(to.y - from.y);
    const extent = from.y === to.y ? size.width : size.height;
    const start = index === 0 ? CLEAR : GAP + LINE;
    const count = Math.min(OFFSETS, Math.floor(Math.max(0, length - extent - start) / STEP) + 1);
    return Array.from({length: count}, (_, step) => start + step * STEP).flatMap((offset) =>
      beside(from, to, offset, size).map((box) => ({box, rank: index * 1000 + offset})),
    );
  });
}

/** A route's straight pieces as thin boxes. */
export function lines(points: readonly Point[]): Box[] {
  return points.slice(1).map((point, index) => lineBox(points[index] ?? point, point, LINE));
}
