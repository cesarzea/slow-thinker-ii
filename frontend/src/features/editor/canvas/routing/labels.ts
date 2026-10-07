import {distance, grow, overlap} from './geometry.ts';
import type {Box, Point} from './geometry.ts';
import {lines, places} from './label-places.ts';
import type {Place} from './label-places.ts';

/** A connection's source port name to place beside its route, near the source. */
export interface LabelRequest {
  readonly id: string;
  /** The label's widths, full first and then shortened, tried in turn. */
  readonly widths: readonly number[];
  readonly height: number;
  /** The route's corners from its source handle on. */
  readonly points: readonly Point[];
}
export interface Placement {
  readonly box: Box;
  /** Which of the label's widths fits. */
  readonly width: number;
  /** False when every place beside the route covers something; the box is the least bad. */
  readonly free: boolean;
}
/** What labels must leave clear: cards, handles and other boxes, and every route by its id. */
export interface Surroundings {
  readonly boxes: readonly Box[];
  readonly routes: ReadonlyMap<string, readonly Point[]>;
}

/** Kept around cards, handles and labels. */
const MARGIN = 2;
/** More room than this around a label does not count. */
const ROOM = 24;

function covered(box: Box, obstacles: readonly Box[]): number {
  return obstacles.reduce((sum, obstacle) => sum + overlap(box, obstacle), 0);
}

/** Closeness to other routes and labels counts against a place, up to some distance. */
function crowding(box: Box, neighbours: readonly Box[]): number {
  const room = Math.min(ROOM, ...neighbours.map((neighbour) => distance(box, neighbour)));
  return (ROOM - room) * 2;
}

/** A free place's rank with its crowding, or null when it covers something. */
function freeRank(
  place: Place,
  obstacles: readonly Box[],
  neighbours: readonly Box[],
): number | null {
  if (obstacles.some((obstacle) => overlap(place.box, obstacle) > 0)) return null;
  return place.rank + crowding(place.box, neighbours);
}

/** The free place nearest the source and away from other routes, if any. */
function freePlace(
  candidates: readonly Place[],
  obstacles: readonly Box[],
  neighbours: readonly Box[],
): Box | null {
  let best: Place | null = null;
  for (const place of candidates) {
    if (best !== null && place.rank >= best.rank) break;
    const rank = freeRank(place, obstacles, neighbours);
    if (rank === null) continue;
    if (best === null || rank < best.rank) best = {box: place.box, rank};
  }
  return best === null ? null : best.box;
}

/** The place covering the least, when none is free. */
function leastCovered(candidates: readonly Place[], obstacles: readonly Box[]): Box | null {
  let best: {box: Box; area: number} | null = null;
  for (const place of candidates) {
    const area = covered(place.box, obstacles);
    if (best === null || area < best.area) best = {box: place.box, area};
  }
  return best?.box ?? null;
}

/**
 * The free place nearest the source and away from other routes, shortening the label when it
 * does not fit; else the least covered place for the full label. `obstacles` are everything
 * to keep clear; `neighbours` the other routes and labels.
 */
function placeLabel(
  label: LabelRequest,
  obstacles: readonly Box[],
  neighbours: readonly Box[],
): Placement | null {
  const at = (width: number): Place[] => places(label.points, {width, height: label.height});
  for (const width of label.widths) {
    const box = freePlace(at(width), obstacles, neighbours);
    if (box !== null) return {box, width, free: true};
  }
  const width = label.widths[0] ?? 0;
  const box = leastCovered(at(width), obstacles);
  return box === null ? null : {box, width, free: false};
}

/** Each label in turn, clear of everything and of the labels placed before it. */
export function placeLabels(
  labels: readonly LabelRequest[],
  surroundings: Surroundings,
): Map<string, Placement> {
  const boxes = surroundings.boxes.map((box) => grow(box, MARGIN));
  const routes = [...surroundings.routes].map(([id, points]) => ({id, lines: lines(points)}));
  const placed: Box[] = [];
  const placements = new Map<string, Placement>();
  for (const label of labels) {
    const others = routes.filter((route) => route.id !== label.id).flatMap((route) => route.lines);
    const own = routes.find((route) => route.id === label.id)?.lines ?? [];
    const neighbours = [...others, ...placed];
    const placement = placeLabel(label, [...boxes, ...own, ...neighbours], neighbours);
    if (placement === null) continue;
    placements.set(label.id, placement);
    placed.push(grow(placement.box, MARGIN));
  }
  return placements;
}
