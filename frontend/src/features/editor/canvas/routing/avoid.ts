import {
  AStarPath,
  ConnDirDown,
  ConnDirLeft,
  ConnDirRight,
  ConnDirUp,
  ConnEnd,
  ConnRef,
  ConnectorCrossings,
  OrthogonalRouting,
  Point as AvoidPoint,
  Rectangle,
  Router,
  ShapeRef,
  generateStaticOrthogonalVisGraph,
  idealNudgingDistance,
  improveOrthogonalRoutes,
  nudgeOrthogonalSegmentsConnectedToShapes,
  nudgeSharedPathsWithCommonEndPoint,
  segmentPenalty,
  shapeBufferDistance,
  vertexVisibility,
} from 'obstacle-router';
import type {PortSide} from '../../state/port-sides.ts';
import type {Point} from './geometry.ts';
import type {HandleEnd, SceneCard} from './scene.ts';

/** Where libavoid may leave or enter a handle: straight out of its side. */
const DIRECTIONS: Readonly<Record<PortSide, number>> = {
  left: ConnDirLeft,
  right: ConnDirRight,
  top: ConnDirUp,
  bottom: ConnDirDown,
};

export interface AvoidEnds {
  readonly id: string;
  readonly source: HandleEnd;
  readonly target: HandleEnd;
}

function orthogonalRouter(): Router {
  const router = new Router(OrthogonalRouting);
  // The package's late-bound orthogonal helpers; its own declarations disagree on types.
  Object.assign(router, {
    _generateStaticOrthogonalVisGraph: generateStaticOrthogonalVisGraph,
    _improveOrthogonalRoutes: improveOrthogonalRoutes,
    _ConnectorCrossings: ConnectorCrossings,
    _AStarPath: AStarPath,
    _vertexVisibility: vertexVisibility,
  });
  router.setRoutingParameter(shapeBufferDistance, 12);
  router.setRoutingParameter(idealNudgingDistance, 10);
  router.setRoutingParameter(segmentPenalty, 10);
  router.setRoutingOption(nudgeOrthogonalSegmentsConnectedToShapes, true);
  router.setRoutingOption(nudgeSharedPathsWithCommonEndPoint, true);
  return router;
}

type ShapeRouter = ConstructorParameters<typeof ShapeRef>[0];
/** The package's Router is its own IRouter at run time; its declarations disagree. */
const shapeRouter = (router: Router): ShapeRouter => router as unknown as ShapeRouter;

function end(handle: HandleEnd): ConnEnd {
  return ConnEnd.fromPoint(new AvoidPoint(handle.x, handle.y), DIRECTIONS[handle.side]);
}

/** Each card as an obstacle of the router. */
function obstacles(router: Router, cards: readonly SceneCard[]): ShapeRef[] {
  return cards.map(({box}) => {
    const corner = new AvoidPoint(box.x + box.width, box.y + box.height);
    return new ShapeRef(shapeRouter(router), new Rectangle(new AvoidPoint(box.x, box.y), corner));
  });
}

/** A connector's route as plain points. */
function routePoints(ref: ConnRef): Point[] {
  const route = ref.displayRoute();
  const points: Point[] = [];
  for (let index = 0; index < route.size(); index++) {
    const point = route.at(index);
    points.push({x: point.x, y: point.y});
  }
  return points;
}

/**
 * Every connection routed orthogonally around the cards by libavoid, all at once, so that
 * parallel pieces are spaced apart. Each route runs from its source handle to its target.
 */
export function avoidRoutes(
  cards: readonly SceneCard[],
  connections: readonly AvoidEnds[],
): Map<string, Point[]> {
  const router = orthogonalRouter();
  const shapes = obstacles(router, cards);
  const refs = connections.map((item) => ({
    id: item.id,
    ref: new ConnRef(router, end(item.source), end(item.target)),
  }));
  router.processTransaction();
  const routes = new Map(refs.map(({id, ref}) => [id, routePoints(ref)] as const));
  for (const shape of shapes) router.deleteShape(shape);
  return routes;
}
