import {expect, it} from 'vitest';
import type {ElkNode} from 'elkjs/lib/elk-api.js';
import {arrangeOptions, elkGraph, elkPositions} from '../src/features/editor/state/elk-graph.ts';
import type {CardGeometry} from '../src/features/editor/state/elk-graph.ts';
import {catalog, j2, j3} from './support/contract.ts';

/** The Reviewer as React Flow measured it: two outputs, accepted above revise. */
const reviewer: CardGeometry = {
  width: 220,
  height: 199,
  inputs: new Map([['in', {x: 0, y: 88}]]),
  outputs: new Map([
    ['accepted', {x: 220, y: 150}],
    ['revise', {x: 220, y: 168}],
  ]),
};
const geometry = (id: string): CardGeometry | undefined =>
  id === 'reviewer' ? reviewer : undefined;

function child(graph: ElkNode, id: string): ElkNode {
  const found = graph.children?.find((item) => item.id === id);
  if (found === undefined) throw new Error(`No node ${id}`);
  return found;
}

it('maps each card to a node with its inputs west and outputs east, where it draws them', () => {
  const graph = elkGraph(j3, catalog, geometry, 'flow', 1.6);
  const node = child(graph, 'reviewer');
  expect([node.width, node.height, node.layoutOptions]).toEqual([
    220,
    199,
    {'elk.portConstraints': 'FIXED_POS'},
  ]);
  expect(
    node.ports?.map((port) => [port.id, port.x, port.y, port.layoutOptions?.['elk.port.side']]),
  ).toEqual([
    ['reviewer/in/in', 0, 88, 'WEST'],
    ['reviewer/out/accepted', 220, 150, 'EAST'],
    ['reviewer/out/revise', 220, 168, 'EAST'],
  ]);
  const proposer = child(graph, 'proposer');
  expect([proposer.width, proposer.height]).toEqual([220, 150]);
  expect(proposer.ports?.map((port) => [port.x, port.y])).toEqual([
    [0, 75],
    [220, 75],
  ]);
});

it('keeps Triggers in the first layer and connects ports that exist', () => {
  const stale = {
    ...j3,
    connections: [...j3.connections, {from: 'reviewer.maybe', to: 'result.in'}],
  };
  const graph = elkGraph(stale, catalog, geometry, 'flow', 1.6);
  expect(child(graph, 'story').layoutOptions?.['elk.layered.layering.layerConstraint']).toBe(
    'FIRST',
  );
  expect(graph.edges?.map((edge) => [edge.id, edge.sources, edge.targets])).toEqual([
    ['story.out->proposer.in', ['story/out/out'], ['proposer/in/in']],
    ['proposer.out->reviewer.in', ['proposer/out/out'], ['reviewer/in/in']],
    ['reviewer.revise->proposer.in', ['reviewer/out/revise'], ['proposer/in/in']],
    ['reviewer.accepted->result.in', ['reviewer/out/accepted'], ['result/in/in']],
  ]);
});

it('lays out by flow in one row of layers, to fit the screen, or compactly', () => {
  const flow = arrangeOptions('flow', 2);
  expect(flow).toMatchObject({
    'elk.algorithm': 'layered',
    'elk.direction': 'RIGHT',
    'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
    'elk.layered.nodePlacement.strategy': 'NETWORK_SIMPLEX',
    'elk.layered.cycleBreaking.strategy': 'DEPTH_FIRST',
    'elk.layered.wrapping.strategy': 'OFF',
  });
  expect(flow['elk.aspectRatio']).toBeUndefined();
  expect(arrangeOptions('fit', 1440 / 760)).toMatchObject({
    'elk.layered.wrapping.strategy': 'MULTI_EDGE',
    'elk.aspectRatio': '1.89',
    'elk.spacing.nodeNode': '56',
  });
  expect(arrangeOptions('compact', 1.5)).toMatchObject({
    'elk.layered.wrapping.strategy': 'MULTI_EDGE',
    'elk.layered.wrapping.cutting.strategy': 'MSD',
    'elk.spacing.nodeNode': '24',
    'elk.layered.spacing.nodeNodeBetweenLayers': '48',
    'elk.aspectRatio': '1.50',
  });
  expect(arrangeOptions('fit', Number.NaN)['elk.aspectRatio']).toBe('1.60');
  expect(elkGraph(j2, catalog, geometry, 'fit', 2).layoutOptions?.['elk.aspectRatio']).toBe('2.00');
});

it('moves ELK’s positions to start at the canvas margin', () => {
  const result: ElkNode = {
    id: 'graph',
    children: [{id: 'story', x: 12, y: 30.4}, {id: 'proposer', x: 322, y: 12}, {id: 'unplaced'}],
  };
  expect(elkPositions(result)).toEqual({story: [40, 58], proposer: [350, 40]});
  expect(elkPositions({id: 'graph'})).toEqual({});
});
