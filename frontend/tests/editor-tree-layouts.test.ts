import {expect, it} from 'vitest';
import * as dagre from '@dagrejs/dagre';
import {dagreLayout} from '../src/features/editor/state/dagre-graph.ts';
import type {CardGeometry} from '../src/features/editor/state/elk-graph.ts';
import {elkTreeGraph} from '../src/features/editor/state/elk-tree.ts';
import {catalog, j3} from './support/contract.ts';

const sizes: Record<string, [number, number]> = {
  story: [220, 100],
  proposer: [220, 120],
  reviewer: [220, 150],
  result: [220, 80],
};
const geometry = (id: string): CardGeometry | undefined => {
  const [width, height] = sizes[id] ?? [220, 100];
  return {width, height, inputs: new Map(), outputs: new Map()};
};

it('lays the graph out as a dagre tree from left to right with the measured sizes', () => {
  const layout = dagreLayout(dagre, j3, catalog, geometry, 'LR');
  expect(layout).toEqual({
    story: [40, 65],
    proposer: [340, 55],
    reviewer: [640, 40],
    result: [940, 75],
  });
});

it('lays the graph out as a dagre tree from top to bottom, ranks 80px apart', () => {
  const layout = dagreLayout(dagre, j3, catalog, geometry, 'TB');
  const tops = ['story', 'proposer', 'reviewer', 'result'].map((id) => layout[id]?.[1]);
  expect(tops[0]).toBe(40);
  // Each rank starts below the tallest card of the one above it and dagre's gap.
  expect((tops[1] ?? 0) - (tops[0] ?? 0)).toBeGreaterThanOrEqual(100 + 80);
  expect(new Set(Object.values(layout).map(([x]) => x)).size).toBeLessThanOrEqual(2);
});

it('gives ELK the cards node to node, without ports, as React Flow’s elkjs example', () => {
  const stale = {
    ...j3,
    connections: [...j3.connections, {from: 'reviewer.maybe', to: 'result.in'}],
  };
  const graph = elkTreeGraph(stale, catalog, geometry, 'DOWN');
  expect(graph.layoutOptions).toEqual({
    'elk.algorithm': 'layered',
    'elk.direction': 'DOWN',
    'elk.layered.spacing.nodeNodeBetweenLayers': '100',
    'elk.spacing.nodeNode': '80',
  });
  expect(graph.children?.find((child) => child.id === 'reviewer')).toEqual({
    id: 'reviewer',
    width: 220,
    height: 150,
  });
  expect(graph.edges?.map((edge) => [edge.sources, edge.targets])).toEqual([
    [['story'], ['proposer']],
    [['proposer'], ['reviewer']],
    [['reviewer'], ['proposer']],
    [['reviewer'], ['result']],
  ]);
});
