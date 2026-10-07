import {grow, lineBox, overlap} from './geometry.ts';
import type {Box, Point} from './geometry.ts';

/** A straight piece of a route: level or plumb, at a height or across, between two values. */
interface Piece {
  readonly level: boolean;
  readonly at: number;
  readonly from: number;
  readonly to: number;
}

/** Pieces closer than this run on top of each other. */
const CLOSE = 4;
const SHIFTS = [8, -8, 16, -16, 24, -24];

function pieceOf(points: readonly Point[], index: number): Piece | null {
  const start = points[index];
  const end = points[index + 1];
  if (start === undefined || end === undefined) return null;
  const level = start.y === end.y;
  const [a, b] = level ? [start.x, end.x] : [start.y, end.y];
  return {level, at: level ? start.y : start.x, from: Math.min(a, b), to: Math.max(a, b)};
}

function piecesOf(points: readonly Point[]): Piece[] {
  return points.slice(1).flatMap((_, index) => pieceOf(points, index) ?? []);
}

function clash(a: Piece, b: Piece): boolean {
  return (
    a.level === b.level &&
    Math.abs(a.at - b.at) < CLOSE &&
    Math.min(a.to, b.to) - Math.max(a.from, b.from) > CLOSE
  );
}

/** The route with one piece moved sideways; its neighbours stretch or shrink to meet it. */
function moved(points: readonly Point[], index: number, shift: number): Point[] {
  const piece = pieceOf(points, index);
  return points.map((point, at) => {
    if (piece === null || (at !== index && at !== index + 1)) return point;
    return piece.level ? {x: point.x, y: point.y + shift} : {x: point.x + shift, y: point.y};
  });
}

/** Whether a piece and its two neighbours still run their way, clear of every card. */
function fits(
  before: readonly Point[],
  after: readonly Point[],
  index: number,
  cards: Box[],
): boolean {
  for (const at of [index - 1, index, index + 1]) {
    const [a, b, c, d] = [before[at], before[at + 1], after[at], after[at + 1]];
    if (a === undefined || b === undefined || c === undefined || d === undefined) return false;
    const was = Math.sign(b.x - a.x + b.y - a.y);
    const is = Math.sign(d.x - c.x + d.y - c.y);
    if (was !== is || cards.some((card) => overlap(lineBox(c, d, 1), card) > 0)) return false;
  }
  return true;
}

/** A sideways move for a piece that runs on top of another route's piece, if one fits. */
function separated(
  points: readonly Point[],
  index: number,
  others: readonly Piece[],
  cards: Box[],
): Point[] | null {
  for (const shift of SHIFTS) {
    const candidate = moved(points, index, shift);
    const piece = pieceOf(candidate, index);
    if (piece === null || others.some((other) => clash(piece, other))) continue;
    if (fits(points, candidate, index, cards)) return candidate;
  }
  return null;
}

/**
 * Routes found one by one may run on top of each other. Each middle piece that does is moved
 * sideways until it runs alone; pieces at a handle stay, so connections still meet their ports.
 */
export function nudged(routes: readonly (readonly Point[])[], cards: readonly Box[]): Point[][] {
  const result = routes.map((points) => [...points]);
  const padded = cards.map((card) => grow(card, 2));
  result.forEach((points, route) => {
    const others = (): Piece[] =>
      result.flatMap((item, at) => (at === route ? [] : piecesOf(item)));
    for (let index = 1; index < points.length - 2; index++) {
      const current = result[route] ?? points;
      const piece = pieceOf(current, index);
      if (piece === null || !others().some((other) => clash(piece, other))) continue;
      const better = separated(current, index, others(), padded);
      if (better !== null) result[route] = better;
    }
  });
  return result;
}
