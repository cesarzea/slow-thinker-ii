import {expect, it} from 'vitest';
import type {GraphDocument, GraphNode} from '../src/api/index.ts';
import {deleteNode} from '../src/features/editor/state/document.ts';
import {removeEmbedded} from '../src/features/editor/state/embedding.ts';
import {
  changedSides,
  nodeSides,
  portSide,
  sidesMode,
  verticalSides,
  withSides,
} from '../src/features/editor/state/port-sides.ts';
import {catalog, j3} from './support/contract.ts';

const sided = (port_sides: GraphDocument['port_sides']): GraphDocument => ({...j3, port_sides});
function node(id: string): GraphNode {
  const found = j3.nodes.find((item) => item.id === id);
  if (found === undefined) throw new Error(`No node ${id}`);
  return found;
}

it('puts inputs on the left and outputs on the right unless the document says otherwise', () => {
  const document = sided({reviewer: {revise: 'bottom'}});
  expect(portSide(document, 'reviewer', 'in', 'input')).toBe('left');
  expect(portSide(document, 'reviewer', 'accepted', 'output')).toBe('right');
  expect(portSide(document, 'reviewer', 'revise', 'output')).toBe('bottom');
  expect(nodeSides(document, node('reviewer'), catalog)).toEqual({
    in: 'left',
    accepted: 'right',
    revise: 'bottom',
  });
});

it('tells left and right, top and bottom, and custom sides apart', () => {
  const reviewer = node('reviewer');
  expect(sidesMode(j3, reviewer, catalog)).toBe('sides');
  expect(sidesMode(sided({reviewer: {gone: 'top'}}), reviewer, catalog)).toBe('sides');
  const vertical = verticalSides(reviewer, catalog);
  expect(vertical).toEqual({in: 'top', accepted: 'bottom', revise: 'bottom'});
  expect(sidesMode(sided({reviewer: vertical}), reviewer, catalog)).toBe('vertical');
  expect(sidesMode(sided({reviewer: {in: 'left'}}), reviewer, catalog)).toBe('custom');
});

it('keeps only the sides that differ from the default, for ports that exist', () => {
  expect(
    changedSides(node('reviewer'), catalog, {
      in: 'left',
      accepted: 'top',
      revise: 'right',
      gone: 'bottom',
    }),
  ).toEqual({accepted: 'top'});
});

it('replaces a node’s sides and drops entries and the field once empty', () => {
  const first = withSides(j3, 'reviewer', {revise: 'left'});
  expect(first.port_sides).toEqual({reviewer: {revise: 'left'}});
  const second = withSides(first, 'proposer', {out: 'bottom'});
  expect(second.port_sides).toEqual({reviewer: {revise: 'left'}, proposer: {out: 'bottom'}});
  expect(withSides(second, 'reviewer', {}).port_sides).toEqual({proposer: {out: 'bottom'}});
  expect('port_sides' in withSides(first, 'reviewer', null)).toBe(false);
});

it('forgets a deleted node’s sides', () => {
  const document = sided({reviewer: {revise: 'left'}, proposer: {out: 'bottom'}});
  expect(deleteNode(document, 'reviewer').port_sides).toEqual({proposer: {out: 'bottom'}});
  expect('port_sides' in deleteNode(j3, 'reviewer')).toBe(false);
});

it('forgets the sides of ports a node no longer has', () => {
  const document = sided({reviewer: {in: 'top', revise: 'left'}});
  expect(removeEmbedded(document, 'reviewer', catalog).port_sides).toEqual({reviewer: {in: 'top'}});
  const only = sided({reviewer: {revise: 'left'}});
  expect('port_sides' in removeEmbedded(only, 'reviewer', catalog)).toBe(false);
});
