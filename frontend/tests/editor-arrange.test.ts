import {expect, it} from 'vitest';
import type {GraphDocument, GraphNode} from '../src/api/index.ts';
import {arrange, arrangedLayout} from '../src/features/editor/state/arrange.ts';
import {
  forwardLinks,
  graphLinks,
  longestPathLayers,
} from '../src/features/editor/state/arrange-graph.ts';
import {catalog, copy, j2, j3} from './support/contract.ts';

const none = new Map<string, number>();
/** The heights of the J3 cards measured in Chromium. */
const measured = new Map([
  ['story', 111],
  ['proposer', 132],
  ['reviewer', 199],
  ['result', 90],
]);

it('lays the review loop out from left to right, centred on one axis', () => {
  expect(arrangedLayout(j3, catalog, measured)).toEqual({
    story: [40, 84],
    proposer: [350, 74],
    reviewer: [660, 40],
    result: [970, 95],
  });
});

it('sets the loop back to the Proposer aside before giving each node its layer', () => {
  const order = j3.nodes.map((node) => node.id);
  const links = graphLinks(j3, catalog);
  const forward = forwardLinks(order, ['story'], links);
  expect(links.filter((link) => !forward.includes(link))).toEqual([
    {from: 'reviewer', to: 'proposer', rank: 2 / 3},
  ]);
  expect(Object.fromEntries(longestPathLayers(order, forward))).toEqual({
    story: 0,
    proposer: 1,
    reviewer: 2,
    result: 3,
  });
});

it('stacks the targets of a node in the order of its outputs', () => {
  const reversed: GraphDocument = {
    ...j2,
    nodes: [...j2.nodes].reverse(),
    connections: [...j2.connections].reverse(),
  };
  const expected = {story: [40, 135], judge: [350, 135], funny: [660, 40], 'not-funny': [660, 230]};
  expect(arrangedLayout(j2, catalog, none)).toEqual(expected);
  expect(arrangedLayout(reversed, catalog, none)).toEqual(expected);
});

function outputNode(id: string, name: string): GraphNode {
  const found = j2.nodes.find((node) => node.id === 'funny');
  if (found === undefined) throw new Error('J2 has changed');
  return {...copy(found), id, name};
}

it('puts nodes without connections in a row below the arranged graph', () => {
  const spare = outputNode('spare', 'Spare');
  const lonely = outputNode('lonely', 'Lonely');
  const document = {...j2, nodes: [...j2.nodes, spare, lonely]};
  const layout = arrangedLayout(document, catalog, none);
  expect([layout['spare'], layout['lonely']]).toEqual([
    [40, 460],
    [350, 460],
  ]);
  const unconnected = {...document, connections: []};
  expect(Object.values(arrangedLayout(unconnected, catalog, none)).map(([, y]) => y)).toEqual([
    40, 40, 40, 40, 40, 40,
  ]);
});

it('gives the same graph the same layout, and keeps the rest of the document', () => {
  const scrambled = {...j3, layout: {story: [900, 500] as [number, number]}};
  const first = arrange(scrambled, catalog, measured);
  expect(arrange(scrambled, catalog, measured)).toEqual(first);
  expect(first.layout).toEqual(arrangedLayout(j3, catalog, measured));
  expect({...first, layout: j3.layout}).toEqual({...j3});
  expect(arrangedLayout({...j3, nodes: [], connections: []}, catalog, none)).toEqual({});
});

it('breaks loops without a Trigger at the first node reached', () => {
  const [, proposer, reviewer] = j3.nodes;
  if (proposer === undefined || reviewer === undefined) throw new Error('J3 has changed');
  const loop = {...j3, nodes: [proposer, reviewer], connections: j3.connections.slice(1, 3)};
  expect(arrangedLayout(loop, catalog, none)).toEqual({
    proposer: [40, 40],
    reviewer: [350, 40],
  });
});
