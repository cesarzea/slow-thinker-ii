import {splitRef} from '../../state/ports.ts';
import {DEFAULT_VIEW} from '../connection-style.ts';
import type {ConnectionView} from '../connection-style.ts';
import type {RouteEdgeType} from '../types.ts';
import type {Box} from './geometry.ts';
import {placeLabels} from './labels.ts';
import type {Placement} from './labels.ts';
import {routeAll} from './routes.ts';
import type {Route} from './routes.ts';
import {handleKey} from './scene.ts';
import type {Scene} from './scene.ts';

/** A connection's route, and its source port's name beside it when there is room. */
export interface EdgeRoute {
  readonly route: Route;
  readonly label: {readonly text: string; readonly placement: Placement} | null;
}
interface Routed {
  readonly edge: RouteEdgeType;
  readonly route: Route;
  /** The port's name, full first and then shorter, by width. */
  readonly texts: ReadonlyMap<number, string>;
}

/** The label font is monospaced: 11px characters advance by about 6.6px. */
const CHARACTER = 6.6;
const PADDING = 10;
const LABEL_HEIGHT = 17;
const LENGTHS = [18, 12, 8, 5];

/** A port name for a label, shortened with an ellipsis to at most `length` characters. */
function labelText(port: string, length = LENGTHS[0] ?? 18): string {
  return port.length > length ? `${port.slice(0, length - 1)}…` : port;
}

function labelWidth(text: string): number {
  return Math.ceil(text.length * CHARACTER + PADDING);
}

/** The port's name for its label by width: full, then shorter where it does not fit. */
function labelTexts(port: string): Map<number, string> {
  const texts = LENGTHS.map((length) => labelText(port, length));
  return new Map([...new Set(texts)].map((text) => [labelWidth(text), text]));
}

/** The message count at a route's middle, which port labels keep clear of. */
function countBox(edge: RouteEdgeType, route: Route): Box[] {
  if (typeof edge.label !== 'string') return [];
  const width = edge.label.length * CHARACTER + 8;
  return [{x: route.middle.x - width / 2, y: route.middle.y - 9, width, height: 18}];
}

function sourcePort(edge: RouteEdgeType): string {
  return splitRef(edge.data?.from ?? '')[1];
}

/** Each connection's route, with its port's name in every length a label may take. */
function routedEdges(
  scene: Scene,
  edges: readonly RouteEdgeType[],
  view: ConnectionView,
): Routed[] {
  const routes = routeAll(
    scene,
    edges.map((edge) => ({
      id: edge.id,
      source: handleKey(edge.source, 'source', edge.sourceHandle ?? ''),
      target: handleKey(edge.target, 'target', edge.targetHandle ?? ''),
    })),
    view,
  );
  return edges.flatMap((edge): Routed[] => {
    const route = routes.get(edge.id);
    return route === undefined ? [] : [{edge, route, texts: labelTexts(sourcePort(edge))}];
  });
}

/** Where every label goes, clear of cards, handles, message counts and routes. */
function placements(scene: Scene, routed: readonly Routed[]): Map<string, Placement> {
  const boxes = [
    ...scene.cards.map((card) => card.box),
    ...[...scene.handles.values()].map((end) => end.box),
    ...routed.flatMap(({edge, route}) => countBox(edge, route)),
  ];
  const labels = routed.map(({edge, route, texts}) => ({
    id: edge.id,
    widths: [...texts.keys()],
    height: LABEL_HEIGHT,
    points: route.guide,
  }));
  return placeLabels(labels, {
    boxes,
    routes: new Map(routed.map(({edge, route}) => [edge.id, route.points])),
  });
}

/** Every connection routed around the cards, then its source port's name placed beside it. */
export function edgeRoutes(
  scene: Scene,
  edges: readonly RouteEdgeType[],
  view: ConnectionView = {...DEFAULT_VIEW, connections: 'routed'},
): Map<string, EdgeRoute> {
  const routed = routedEdges(scene, edges, view);
  const placed = placements(scene, routed);
  return new Map(
    routed.map(({edge, route, texts}) => {
      const placement = placed.get(edge.id);
      const text = placement === undefined ? undefined : texts.get(placement.width);
      const label = placement === undefined || text === undefined ? null : {text, placement};
      return [edge.id, {route, label}];
    }),
  );
}
