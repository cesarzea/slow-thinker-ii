import {expect, it} from 'vitest';
import type {ElkNode} from 'elkjs/lib/elk-api.js';
import {elkGraph} from '../src/features/editor/state/elk-graph.ts';
import type {CardGeometry} from '../src/features/editor/state/elk-graph.ts';
import {catalog, j3} from './support/contract.ts';

/** The Reviewer measured with its input on top and revise below. */
const turned: CardGeometry = {
  width: 220,
  height: 199,
  inputs: new Map([['in', {x: 110, y: 0}]]),
  outputs: new Map([
    ['accepted', {x: 220, y: 100}],
    ['revise', {x: 160, y: 199}],
  ]),
};
const geometry = (id: string): CardGeometry | undefined => (id === 'reviewer' ? turned : undefined);
const sided = {
  ...j3,
  port_sides: {reviewer: {in: 'top', revise: 'bottom'}, proposer: {in: 'top'}},
} as const;

function child(graph: ElkNode, id: string): ElkNode {
  const found = graph.children?.find((item) => item.id === id);
  if (found === undefined) throw new Error(`No node ${id}`);
  return found;
}

it('puts ports on the sides the document gives them, spread evenly when not measured', () => {
  const graph = elkGraph(sided, catalog, geometry, 'fit', 1.6);
  const ports = child(graph, 'reviewer').ports ?? [];
  expect(
    ports.map((port) => [port.id, port.x, port.y, port.layoutOptions?.['elk.port.side']]),
  ).toEqual([
    ['reviewer/in/in', 110, 0, 'NORTH'],
    ['reviewer/out/accepted', 220, 100, 'EAST'],
    ['reviewer/out/revise', 160, 199, 'SOUTH'],
  ]);
  expect(child(graph, 'proposer').ports?.map((port) => [port.x, port.y])).toEqual([
    [110, 0],
    [220, 75],
  ]);
});
