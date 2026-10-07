import {expect, it} from 'vitest';
import {
  embedComponent,
  embeddable,
  providedConnections,
  removeEmbedded,
} from '../src/features/editor/state/embedding.ts';
import {
  declarationFor,
  inputTargets,
  isTriggerOrOutput,
  nodePorts,
  portLabel,
} from '../src/features/editor/state/ports.ts';
import type {GraphNode} from '../src/api/index.ts';
import {catalog, declaration, j1, j2} from './support/contract.ts';

const node = (component: string, config: GraphNode['config'] = {}): GraphNode => ({
  id: 'n',
  name: 'N',
  component,
  config,
});

it('takes inputs from the host and outputs from its declaration or configuration', () => {
  expect(nodePorts(node('llm-call@1.0.0'), catalog)).toEqual({inputs: ['in'], outputs: ['out']});
  expect(nodePorts(node('trigger@1.0.0'), catalog)).toEqual({inputs: [], outputs: ['out']});
  const router = node('router@1.0.0', {outputs: ['a', 'b', 'a', '', 3]});
  expect(nodePorts(router, catalog)).toEqual({inputs: ['in'], outputs: ['a', 'b']});
  expect(nodePorts(node('router@1.0.0', {outputs: 'a'}), catalog).outputs).toEqual([]);
  expect(nodePorts(node('unknown@1.0.0'), catalog)).toEqual({inputs: [], outputs: []});
});

it('replaces the host outputs with those of an embedded output component', () => {
  const judge = j2.nodes.find((item) => item.id === 'judge');
  if (judge === undefined) throw new Error('Missing judge');
  expect(nodePorts(judge, catalog)).toEqual({inputs: ['in'], outputs: ['funny', 'not_funny']});
  const missing = {
    ...judge,
    embedded: [{position: 'output' as const, component: 'gone@1.0.0', config: {}}],
  };
  expect(nodePorts(missing, catalog).outputs).toEqual([]);
});

it('names input targets and port references for people', () => {
  expect(inputTargets(j1, catalog)).toEqual([
    {ref: 'proposer.in', label: 'Proposer · in'},
    {ref: 'result.in', label: 'Funny story · in'},
  ]);
  expect(portLabel(j1, 'proposer.out')).toBe('Proposer · out');
  expect(portLabel(j1, 'ghost.in')).toBe('ghost.in');
  expect(declarationFor(catalog, undefined)).toBeUndefined();
  expect(isTriggerOrOutput(node('output@1.0.0'))).toBe(true);
  expect(isTriggerOrOutput(node('llm-call@1.0.0'))).toBe(false);
});

it('offers only components embeddable at the output and embeds them', () => {
  expect(embeddable(catalog).map((item) => item.label)).toEqual(['Router']);
  const withProposerOut = j1;
  const document = embedComponent(withProposerOut, 'proposer', declaration('router'), catalog);
  const proposer = document.nodes.find((item) => item.id === 'proposer');
  expect(proposer?.embedded).toEqual([
    {position: 'output', component: 'router@1.0.0', config: declaration('router').initial_config},
  ]);
  expect(nodePorts(proposer ?? node(''), catalog).outputs).toEqual(['yes', 'no']);
  expect(document.connections).toEqual([{from: 'story.out', to: 'proposer.in'}]);
});

it('removes an embedded component with the connections leaving its ports', () => {
  expect(providedConnections(j2, 'judge', catalog)).toEqual([
    {from: 'judge.funny', to: 'funny.in'},
    {from: 'judge.not_funny', to: 'not-funny.in'},
  ]);
  const document = removeEmbedded(j2, 'judge', catalog);
  const judge = document.nodes.find((item) => item.id === 'judge');
  expect(judge !== undefined && 'embedded' in judge).toBe(false);
  expect(document.connections).toEqual([{from: 'story.out', to: 'judge.in'}]);
  expect(nodePorts(judge ?? node(''), catalog).outputs).toEqual(['out']);
  expect(providedConnections(j1, 'proposer', catalog)).toEqual([]);
  expect(providedConnections(j1, 'missing', catalog)).toEqual([]);
});
