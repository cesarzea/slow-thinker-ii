import {expect, it} from 'vitest';
import {Position} from '@xyflow/react';
import type {InternalNode} from '@xyflow/react';
import {edgeRoutes} from '../src/features/editor/canvas/routing/edge-routes.ts';
import {sceneOf} from '../src/features/editor/canvas/routing/scene.ts';
import type {RouteEdgeType} from '../src/features/editor/canvas/types.ts';

function node(id: string, x: number, y: number): InternalNode {
  const bound = (name: string, position: Position, at: number) => [
    {id: name, nodeId: id, position, x: at, y: 45, width: 10, height: 10},
  ];
  return {
    id,
    position: {x, y},
    data: {},
    measured: {width: 200, height: 100},
    internals: {
      positionAbsolute: {x, y},
      z: 0,
      userNode: {id, position: {x, y}, data: {}},
      handleBounds: {
        source: bound('out', Position.Right, 195),
        target: bound('in', Position.Left, -5),
      },
    },
  } as unknown as InternalNode;
}

it('names a curved connection’s source port beside its start, clear of the curve', () => {
  const scene = sceneOf([node('a', 0, 0), node('b', 400, 200)]);
  const edge: RouteEdgeType = {
    id: 'a-b',
    source: 'a',
    sourceHandle: 'out',
    target: 'b',
    targetHandle: 'in',
    data: {from: 'a.out', to: 'b.in', route: 'A to B'},
  };
  const routed = edgeRoutes(scene, [edge], {connections: 'curved', curvature: 0.25}).get('a-b');
  if (routed?.label === null || routed === undefined) throw new Error('Not named');
  expect(routed.route.path).toMatch(/^M205,50 C/u);
  expect(routed.route.middle).toEqual({x: 300, y: 150});
  const {box, free} = routed.label.placement;
  expect(free).toBe(true);
  // The curve bends down towards B, so the name goes above the line leaving A.
  expect(box.y).toBeLessThan(50);
  expect(box.x).toBeGreaterThan(205);
});

it('bends curves more with a higher curvature where they lead back', () => {
  const scene = sceneOf([node('a', 400, 0), node('b', 0, 0)]);
  const edge: RouteEdgeType = {
    id: 'a-b',
    source: 'a',
    sourceHandle: 'out',
    target: 'b',
    targetHandle: 'in',
    data: {from: 'a.out', to: 'b.in', route: 'A to B'},
  };
  const path = (curvature: number): string =>
    edgeRoutes(scene, [edge], {connections: 'curved', curvature}).get('a-b')?.route.path ?? '';
  expect(path(0.25)).not.toBe(path(0.9));
  expect(path(0.25)).toMatch(/^M605,50 C/u);
});

it('draws React Flow’s simple bezier, with its control points halfway across', () => {
  const scene = sceneOf([node('a', 400, 0), node('b', 0, 100)]);
  const edge: RouteEdgeType = {
    id: 'a-b',
    source: 'a',
    sourceHandle: 'out',
    target: 'b',
    targetHandle: 'in',
    data: {from: 'a.out', to: 'b.in', route: 'A to B'},
  };
  const routed = edgeRoutes(scene, [edge], {connections: 'simple', curvature: 0.9}).get('a-b');
  expect(routed?.route.path).toBe('M605,50 C300,50 300,150 -5,150');
});
