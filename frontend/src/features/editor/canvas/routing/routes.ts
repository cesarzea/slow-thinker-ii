import {svgDrawSmoothStepLinePath} from '@tisoap/react-flow-smart-edge';
import {corners, halfway, squared, step} from './geometry.ts';
import type {ConnectionView} from '../connection-style.ts';
import {curve} from './curves.ts';
import {avoidRoutes} from './avoid.ts';
import type {Point} from './geometry.ts';
import type {HandleEnd, Scene} from './scene.ts';

/** A connection's way between its handles: drawn path, points along it and middle. */
export interface Route {
  readonly path: string;
  readonly points: readonly Point[];
  /** Where its source port's name may go: along these straight pieces from the source. */
  readonly guide: readonly Point[];
  readonly middle: Point;
}
export interface RouteEnds {
  readonly source: HandleEnd;
  readonly target: HandleEnd;
}

const draw = svgDrawSmoothStepLinePath({borderRadius: 10});
const STUB = 20;

/** Straight out of both handles and across halfway, when no way around the cards is found. */
export function elbow({source, target}: RouteEnds): Point[] {
  const start = step(source, source.side, STUB);
  const end = step(target, target.side, STUB);
  const across = source.side === 'left' || source.side === 'right';
  const half = across ? (start.x + end.x) / 2 : (start.y + end.y) / 2;
  const bend = across
    ? [
        {x: half, y: start.y},
        {x: half, y: end.y},
      ]
    : [
        {x: start.x, y: half},
        {x: end.x, y: half},
      ];
  return corners(squared([source, start, ...bend, end, target], source.side, target.side));
}

/** The route through its corners, drawn with rounded corners. */
function drawn({source, target}: RouteEnds, points: readonly Point[]): Route {
  const inner = points.slice(1, -1).map((point) => [point.x, point.y]);
  return {path: draw(source, target, inner), points, guide: points, middle: halfway(points)};
}

export interface RouteRequest {
  readonly id: string;
  readonly source: string;
  readonly target: string;
}

/**
 * Each connection whose handles are measured: curved or simply curved as React Flow draws
 * it, or routed
 * around the cards with routes that would run on top of each other moved apart.
 */
export function routeAll(
  scene: Scene,
  requests: readonly RouteRequest[],
  view: ConnectionView,
): Map<string, Route> {
  const measured = requests.flatMap((request) => {
    const source = scene.handles.get(request.source);
    const target = scene.handles.get(request.target);
    return source === undefined || target === undefined ? [] : [{id: request.id, source, target}];
  });
  if (view.connections !== 'routed') {
    const curvature = view.connections === 'curved' ? view.curvature : null;
    return new Map(measured.map((ends) => [ends.id, curve(ends, curvature)]));
  }
  const avoided = avoidRoutes(scene.cards, measured);
  return new Map(
    measured.map((ends) => {
      const points = avoided.get(ends.id);
      const usable =
        points !== undefined && points.length >= 2
          ? corners(squared(points, ends.source.side, ends.target.side))
          : elbow(ends);
      return [ends.id, drawn(ends, usable)];
    }),
  );
}
