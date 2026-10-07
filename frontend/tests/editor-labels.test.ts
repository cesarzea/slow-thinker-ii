import {expect, it} from 'vitest';
import {Position} from '@xyflow/react';
import type {InternalNode} from '@xyflow/react';
import {edgeRoutes} from '../src/features/editor/canvas/routing/edge-routes.ts';
import {overlap} from '../src/features/editor/canvas/routing/geometry.ts';
import type {Box, Point} from '../src/features/editor/canvas/routing/geometry.ts';
import {placeLabels} from '../src/features/editor/canvas/routing/labels.ts';
import {sceneOf} from '../src/features/editor/canvas/routing/scene.ts';
import type {RouteEdgeType} from '../src/features/editor/canvas/types.ts';

const label = (id: string, points: Point[], widths = [40]) => ({id, widths, height: 17, points});
const straight: Point[] = [
  {x: 0, y: 0},
  {x: 200, y: 0},
];

it('puts a label beside the first piece of its route, near the source', () => {
  const placed = placeLabels([label('a', straight)], {
    boxes: [],
    routes: new Map([['a', straight]]),
  });
  expect(placed.get('a')).toEqual({
    box: {x: 8, y: -21, width: 40, height: 17},
    width: 40,
    free: true,
  });
});

it('puts it on the side away from another route running alongside', () => {
  const above: Point[] = [
    {x: 0, y: -30},
    {x: 200, y: -30},
  ];
  const placed = placeLabels([label('a', straight)], {
    boxes: [],
    routes: new Map([
      ['a', straight],
      ['b', above],
    ]),
  });
  expect(placed.get('a')?.box.y).toBe(4);
});

it('moves along the route when the first piece has no room, and never covers a card', () => {
  const route: Point[] = [
    {x: 0, y: 0},
    {x: 20, y: 0},
    {x: 20, y: 120},
    {x: 300, y: 120},
  ];
  const cards: Box[] = [
    {x: -200, y: -60, width: 190, height: 120},
    {x: 30, y: -60, width: 200, height: 160},
  ];
  const placed = placeLabels([label('a', route)], {boxes: cards, routes: new Map([['a', route]])});
  const box = placed.get('a')?.box;
  expect(placed.get('a')?.free).toBe(true);
  expect(box?.x).toBe(-24);
  expect(cards.every((card) => box !== undefined && overlap(box, card) === 0)).toBe(true);
});

it('shortens a label that does not fit, and keeps labels clear of each other', () => {
  const short: Point[] = [
    {x: 0, y: 0},
    {x: 60, y: 0},
  ];
  const wall: Box = {x: 60, y: -40, width: 100, height: 80};
  const placed = placeLabels([label('a', short, [70, 40]), label('b', short, [40])], {
    boxes: [wall],
    routes: new Map([['a', short]]),
  });
  const [a, b] = [placed.get('a'), placed.get('b')];
  expect(a?.width).toBe(40);
  expect(a !== undefined && b !== undefined && overlap(a.box, b.box) === 0).toBe(true);
});

it('falls back to the least covered place when nothing is free', () => {
  const crowded: Box = {x: -50, y: -60, width: 300, height: 120};
  const placed = placeLabels([label('a', straight)], {
    boxes: [crowded],
    routes: new Map([['a', straight]]),
  });
  expect(placed.get('a')?.free).toBe(false);
  expect(placeLabels([label('a', [{x: 0, y: 0}])], {boxes: [], routes: new Map()}).size).toBe(0);
});

function node(id: string, x: number, handles: {source?: string; target?: string}): InternalNode {
  const bound = (name: string | undefined, position: Position, at: number) =>
    name === undefined
      ? []
      : [{id: name, nodeId: id, position, x: at, y: 45, width: 10, height: 10}];
  return {
    id,
    position: {x, y: 0},
    data: {},
    measured: {width: 200, height: 100},
    internals: {
      positionAbsolute: {x, y: 0},
      z: 0,
      userNode: {id, position: {x, y: 0}, data: {}},
      handleBounds: {
        source: bound(handles.source, Position.Right, 195),
        target: bound(handles.target, Position.Left, -5),
      },
    },
  } as unknown as InternalNode;
}

it('routes every connection and names its source port beside it, shortened when long', () => {
  const scene = sceneOf([
    node('a', 0, {source: 'a-port-with-a-very-long-name'}),
    node('b', 500, {target: 'in'}),
  ]);
  const edge: RouteEdgeType = {
    id: 'a-b',
    source: 'a',
    sourceHandle: 'a-port-with-a-very-long-name',
    target: 'b',
    targetHandle: 'in',
    label: '7',
    data: {from: 'a.a-port-with-a-very-long-name', to: 'b.in', route: 'A to B'},
  };
  const quiet = {...edge, label: undefined};
  const routed = edgeRoutes(scene, [quiet, {...edge, id: 'missing', target: 'c'}]);
  expect([...routed.keys()]).toEqual(['a-b']);
  const shown = routed.get('a-b');
  expect(shown?.label?.text).toBe('a-port-with-a-ver…');
  expect(shown?.label?.placement.free).toBe(true);
  expect(shown?.route.points.at(-1)).toMatchObject({x: 495, y: 50});
  // The message count at the middle leaves room for a shorter name only.
  expect(edgeRoutes(scene, [edge]).get('a-b')?.label?.text).toBe('a-port-with…');
});
