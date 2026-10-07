import type {PortSide} from '../../state/port-sides.ts';

export interface Point {
  readonly x: number;
  readonly y: number;
}
export interface Box {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

/** The step away from a card on each of its sides. */
const OUTWARD: Readonly<Record<PortSide, Point>> = {
  left: {x: -1, y: 0},
  right: {x: 1, y: 0},
  top: {x: 0, y: -1},
  bottom: {x: 0, y: 1},
};

export function step(point: Point, side: PortSide, distance: number): Point {
  const outward = OUTWARD[side];
  return {x: point.x + outward.x * distance, y: point.y + outward.y * distance};
}

export function grow(box: Box, by: number): Box {
  return {x: box.x - by, y: box.y - by, width: box.width + 2 * by, height: box.height + 2 * by};
}

/** How much two boxes overlap; zero when they only touch or are apart. */
export function overlap(a: Box, b: Box): number {
  const width = Math.min(a.x + a.width, b.x + b.width) - Math.max(a.x, b.x);
  const height = Math.min(a.y + a.height, b.y + b.height) - Math.max(a.y, b.y);
  return width > 0 && height > 0 ? width * height : 0;
}

/** The distance between two boxes; zero when they overlap. */
export function distance(a: Box, b: Box): number {
  const across = Math.max(0, a.x - (b.x + b.width), b.x - (a.x + a.width));
  const along = Math.max(0, a.y - (b.y + b.height), b.y - (a.y + a.height));
  return Math.hypot(across, along);
}

/** The box a straight piece of a route covers, `half` to each side of the line. */
export function lineBox(from: Point, to: Point, half: number): Box {
  return {
    x: Math.min(from.x, to.x) - half,
    y: Math.min(from.y, to.y) - half,
    width: Math.abs(to.x - from.x) + 2 * half,
    height: Math.abs(to.y - from.y) + 2 * half,
  };
}

const collinear = (a: Point, b: Point, c: Point): boolean =>
  (a.x === b.x && b.x === c.x) || (a.y === b.y && b.y === c.y);

/** The corners of a route: repeated points and points in the middle of a straight run go. */
export function corners(points: readonly Point[]): Point[] {
  const kept: Point[] = [];
  for (const point of points) {
    const last = kept.at(-1);
    if (last?.x === point.x && last.y === point.y) continue;
    const before = kept.at(-2);
    if (last !== undefined && before !== undefined && collinear(before, last, point)) kept.pop();
    kept.push(point);
  }
  return kept;
}

const horizontal = (side: PortSide): boolean => side === 'left' || side === 'right';

/**
 * The route with a corner wherever two points are not level or plumb: the router lines its
 * ends up with the handles, which can leave a slanted piece. Leaving the source and reaching
 * the target, pieces run along their sides' axes; elsewhere they keep their direction.
 */
export function squared(points: readonly Point[], from: PortSide, to: PortSide): Point[] {
  const result: Point[] = [];
  points.forEach((point, index) => {
    const last = result.at(-1);
    if (last !== undefined && last.x !== point.x && last.y !== point.y) {
      const across = acrossFirst(index === points.length - 1, result.at(-2), last, from, to);
      result.push(across ? {x: point.x, y: last.y} : {x: last.x, y: point.y});
    }
    result.push(point);
  });
  return result;
}

/** Whether a slanted piece turns into a corner by going across first, then up or down. */
function acrossFirst(
  reachesTarget: boolean,
  before: Point | undefined,
  last: Point,
  from: PortSide,
  to: PortSide,
): boolean {
  if (reachesTarget) return !horizontal(to);
  if (before === undefined) return horizontal(from);
  return before.y === last.y;
}

/** The point halfway along a route. */
export function halfway(points: readonly Point[]): Point {
  const lengths = points.slice(1).map((point, index) => {
    const from = points[index] ?? point;
    return Math.abs(point.x - from.x) + Math.abs(point.y - from.y);
  });
  let rest = lengths.reduce((sum, length) => sum + length, 0) / 2;
  for (const [index, length] of lengths.entries()) {
    const from = points[index];
    const to = points[index + 1];
    if (from === undefined || to === undefined) break;
    if (rest <= length && length > 0) {
      const share = rest / length;
      return {x: from.x + (to.x - from.x) * share, y: from.y + (to.y - from.y) * share};
    }
    rest -= length;
  }
  return points[0] ?? {x: 0, y: 0};
}
