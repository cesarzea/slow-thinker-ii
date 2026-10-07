import {expect, it} from 'vitest';
import {Position} from '@xyflow/react';
import type {InternalNode} from '@xyflow/react';
import {overlap} from '../src/features/editor/canvas/routing/geometry.ts';
import type {Box, Point} from '../src/features/editor/canvas/routing/geometry.ts';
import {routeAll} from '../src/features/editor/canvas/routing/routes.ts';
import {handleKey, sameScene, sceneOf} from '../src/features/editor/canvas/routing/scene.ts';
import type {HandleEnd} from '../src/features/editor/canvas/routing/scene.ts';

interface FakeHandle {
  readonly id: string;
  readonly position: Position;
  readonly x: number;
  readonly y: number;
}

/** A measured card at (x, y), 200 by 100, with 10 by 10 handles. */
function card(id: string, x: number, y: number, handles: Record<string, FakeHandle[]>) {
  const bounds = (list: FakeHandle[] = []) =>
    list.map((handle) => ({...handle, nodeId: id, width: 10, height: 10}));
  return {
    id,
    position: {x, y},
    data: {},
    measured: {width: 200, height: 100},
    internals: {
      positionAbsolute: {x, y},
      z: 0,
      userNode: {id, position: {x, y}, data: {}},
      handleBounds: {source: bounds(handles['source']), target: bounds(handles['target'])},
    },
  } as unknown as InternalNode;
}

const out = {id: 'out', position: Position.Right, x: 195, y: 45};
const into = {id: 'in', position: Position.Left, x: -5, y: 45};

/** Whether any straight piece of a route runs through the box. */
function crosses(points: readonly Point[], box: Box): boolean {
  return points.slice(1).some((point, index) => {
    const from = points[index] ?? point;
    const piece = {
      x: Math.min(from.x, point.x),
      y: Math.min(from.y, point.y),
      width: Math.abs(point.x - from.x) + 1,
      height: Math.abs(point.y - from.y) + 1,
    };
    return overlap(piece, box) > 0;
  });
}

function level(points: readonly Point[]): boolean {
  return points.slice(1).every((point, index) => {
    const from = points[index];
    return from !== undefined && (from.x === point.x || from.y === point.y);
  });
}

it('measures the cards and where connections meet their handles, by side', () => {
  const top = {id: 'top', position: Position.Top, x: 95, y: -5};
  const scene = sceneOf([
    card('a', 0, 0, {source: [out]}),
    card('b', 400, 0, {target: [into, top]}),
  ]);
  expect(scene.cards.map((item) => item.box)).toEqual([
    {x: 0, y: 0, width: 200, height: 100},
    {x: 400, y: 0, width: 200, height: 100},
  ]);
  const end = (key: string): Pick<HandleEnd, 'x' | 'y' | 'side'> | undefined => {
    const found = scene.handles.get(key);
    return found === undefined ? undefined : {x: found.x, y: found.y, side: found.side};
  };
  expect(end(handleKey('a', 'source', 'out'))).toEqual({x: 205, y: 50, side: 'right'});
  expect(end(handleKey('b', 'target', 'in'))).toEqual({x: 395, y: 50, side: 'left'});
  expect(end(handleKey('b', 'target', 'top'))).toEqual({x: 500, y: -5, side: 'top'});
  const moved = sceneOf([card('a', 0, 0, {source: [out]}), card('b', 410, 0, {target: [into]})]);
  expect(
    sameScene(
      scene,
      sceneOf([card('a', 0, 0, {source: [out]}), card('b', 400, 0, {target: [into, top]})]),
    ),
  ).toBe(true);
  expect(sameScene(scene, moved)).toBe(false);
});

it('routes a connection around a card in its way, level and plumb, from handle to handle', () => {
  const scene = sceneOf([
    card('a', 0, 0, {source: [out]}),
    card('wall', 300, -20, {}),
    card('b', 600, 0, {target: [into]}),
  ]);
  const routes = routeAll(
    scene,
    [
      {id: 'a-b', source: handleKey('a', 'source', 'out'), target: handleKey('b', 'target', 'in')},
      {
        id: 'lost',
        source: handleKey('a', 'source', 'nothing'),
        target: handleKey('b', 'target', 'in'),
      },
    ],
    {connections: 'routed', curvature: 0.25},
  );
  const route = routes.get('a-b');
  expect(routes.has('lost')).toBe(false);
  expect(route?.points[0]).toMatchObject({x: 205, y: 50});
  expect(route?.points.at(-1)).toMatchObject({x: 595, y: 50});
  expect(level(route?.points ?? [])).toBe(true);
  expect(crosses(route?.points ?? [], {x: 300, y: -20, width: 200, height: 100})).toBe(false);
  expect(route?.path).toMatch(/^M 205,50/u);
});
