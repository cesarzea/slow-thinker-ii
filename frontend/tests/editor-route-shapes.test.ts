import {expect, it} from 'vitest';
import {halfway, squared} from '../src/features/editor/canvas/routing/geometry.ts';
import {nudged} from '../src/features/editor/canvas/routing/nudge.ts';
import {elbow} from '../src/features/editor/canvas/routing/routes.ts';
import type {HandleEnd} from '../src/features/editor/canvas/routing/scene.ts';

/** Points from x, y pairs. */
const at = (...pairs: [number, number][]) => pairs.map(([x, y]) => ({x, y}));
const end = (x: number, y: number, side: HandleEnd['side']): HandleEnd => ({
  x,
  y,
  side,
  box: {x, y, width: 0, height: 0},
});

it('goes straight out of both handles and across halfway when no route is found', () => {
  const across = elbow({source: end(0, 0, 'right'), target: end(100, 50, 'left')});
  expect(across.map(({x, y}) => ({x, y}))).toEqual(at([0, 0], [50, 0], [50, 50], [100, 50]));
  const down = elbow({source: end(0, 0, 'bottom'), target: end(80, 100, 'top')});
  expect(down.slice(1, -1)).toEqual(at([0, 50], [80, 50]));
});

it('turns slanted pieces into corners along the sides of the handles they leave and reach', () => {
  expect(squared(at([0, 0], [40, 3], [40, 60], [90, 64]), 'right', 'left')).toEqual(
    at([0, 0], [40, 0], [40, 3], [40, 60], [40, 64], [90, 64]),
  );
  expect(squared(at([0, 0], [30, 40]), 'bottom', 'top')).toEqual(at([0, 0], [30, 0], [30, 40]));
});

it('finds the point halfway along a route', () => {
  expect(halfway(at([0, 0], [40, 0], [40, 40]))).toEqual({x: 40, y: 0});
  expect(halfway(at([0, 0], [10, 0], [10, 90]))).toEqual({x: 10, y: 40});
  expect(halfway(at([5, 5]))).toEqual({x: 5, y: 5});
});

it('moves a route’s middle piece off another route it runs on, keeping the pieces at handles', () => {
  const along = at([0, 0], [0, 40], [200, 40]);
  const back = at([150, 0], [150, 40], [-50, 40], [-50, 0]);
  const [first, second] = nudged([along, back], []);
  expect(first).toEqual(along);
  expect(second).toEqual(at([150, 0], [150, 48], [-50, 48], [-50, 0]));
  const walled = nudged([along, back], [{x: -100, y: 42, width: 400, height: 40}]);
  expect(walled[1]).toEqual(at([150, 0], [150, 32], [-50, 32], [-50, 0]));
  const stuck = nudged([along, back], [{x: -100, y: -40, width: 400, height: 200}]);
  expect(stuck[1]).toEqual(back);
});
