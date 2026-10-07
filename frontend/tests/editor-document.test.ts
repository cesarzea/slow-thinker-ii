import {expect, it} from 'vitest';
import {
  addNode,
  connect,
  deleteNode,
  disconnect,
  moveNode,
  renameNode,
  setEmbeddedConfig,
  setLimits,
  setNodeConfig,
  staleConnections,
} from '../src/features/editor/state/document.ts';
import {freePosition, newGraphDocument} from '../src/features/editor/state/defaults.ts';
import {catalog, copy, declaration, j2, j3} from './support/contract.ts';

it('creates new graphs with the default limits and no nodes', () => {
  expect(newGraphDocument('funny-story-ab12', 'Funny story')).toEqual({
    format: 'slow-thinker.graph/1',
    id: 'funny-story-ab12',
    name: 'Funny story',
    limits: {
      max_activations: 20,
      max_running_nodes: 4,
      time_limit_seconds: 300,
      budget_usd: '0.10',
    },
    nodes: [],
    connections: [],
    layout: {},
  });
});

it('adds nodes from declarations with unique identifiers, names and initial configuration', () => {
  let document = newGraphDocument('g-0000', 'G');
  const llm = declaration('llm-call');
  document = addNode(document, llm, [40, 40]);
  document = addNode(document, llm, freePosition(document));
  document = addNode(document, llm, freePosition(document));
  expect(document.nodes.map((node) => [node.id, node.name])).toEqual([
    ['llm-call', 'LLM Call'],
    ['llm-call-2', 'LLM Call 2'],
    ['llm-call-3', 'LLM Call 3'],
  ]);
  expect(document.nodes[0]?.config).toEqual(llm.initial_config);
  expect(document.nodes[0]?.config).not.toBe(llm.initial_config);
  expect(document.nodes[0]?.component).toBe('llm-call@1.0.0');
  expect(document.layout).toEqual({
    'llm-call': [40, 40],
    'llm-call-2': [310, 40],
    'llm-call-3': [580, 40],
  });
});

it('finds free positions on a grid around existing nodes', () => {
  const crowded = {
    ...newGraphDocument('g-0000', 'G'),
    layout: {a: [40, 40], b: [310, 40], c: [580, 40], d: [850, 40]} as Record<
      string,
      [number, number]
    >,
  };
  expect(freePosition(crowded)).toEqual([40, 280]);
  const document = newGraphDocument('g-0000', 'G');
  Reflect.deleteProperty(document, 'layout');
  expect(freePosition(document)).toEqual([40, 40]);
  const full = Object.fromEntries(
    Array.from({length: 1000}, (_, index) => [
      `n${String(index)}`,
      [40 + (index % 4) * 270, 40 + Math.floor(index / 4) * 240] as [number, number],
    ]),
  );
  expect(freePosition({...document, layout: full})).toEqual([40, 40 + 250 * 240]);
});

/** Cards are 220px wide; the tallest step 1 card, an LLM Call with an embedded Router, is 199px. */
function gap([x, y]: readonly [number, number], [left, top]: readonly [number, number]): number {
  return Math.max(Math.abs(left - x) - 220, Math.abs(top - y) - 199);
}

it('keeps at least 24px between a new card and every other card', () => {
  const document = newGraphDocument('g-0000', 'G');
  const placed: [number, number][] = [];
  for (let count = 0; count < 9; count += 1) {
    const layout = Object.fromEntries(placed.map((position, index) => [String(index), position]));
    const position = freePosition({...document, layout});
    expect(placed.filter((other) => gap(position, other) < 24)).toEqual([]);
    placed.push(position);
  }
  expect(placed.at(-1)).toEqual([40, 520]);
  // Cards moved by hand would leave 10px beside or 11px below the next grid slot: it is skipped.
  const beside = {a: [40, 40], b: [540, 40]} as Record<string, [number, number]>;
  expect(freePosition({...document, layout: beside})).toEqual([850, 40]);
  const below = {a: [40, 250]} as Record<string, [number, number]>;
  expect(freePosition({...document, layout: below})).toEqual([310, 40]);
});

it('renames, moves and reconfigures nodes and sets limits', () => {
  let document = renameNode(j2, 'judge', 'Critic');
  document = moveNode(document, 'judge', [10.6, 20.2]);
  document = setNodeConfig(document, 'story', {message: 'Hello'});
  document = setEmbeddedConfig(document, 'judge', {outputs: ['yes'], script: 'pass'});
  document = setLimits(document, {...document.limits, max_activations: 3});
  const judge = document.nodes.find((node) => node.id === 'judge');
  expect(judge?.name).toBe('Critic');
  expect(judge?.embedded?.[0]?.config).toEqual({outputs: ['yes'], script: 'pass'});
  expect(document.layout?.['judge']).toEqual([11, 20]);
  expect(document.nodes[0]?.config).toEqual({message: 'Hello'});
  expect(document.limits.max_activations).toBe(3);
  expect(setEmbeddedConfig(document, 'story', {}).nodes[0]?.embedded).toEqual([]);
});

it('deletes a node with its connections and layout entry', () => {
  const document = deleteNode(j3, 'reviewer');
  expect(document.nodes.map((node) => node.id)).toEqual(['story', 'proposer', 'result']);
  expect(document.connections).toEqual([{from: 'story.out', to: 'proposer.in'}]);
  expect(Object.keys(document.layout ?? {})).toEqual(['story', 'proposer', 'result']);
  const unlaid = copy(j3);
  Reflect.deleteProperty(unlaid, 'layout');
  expect(deleteNode(unlaid, 'story').layout).toEqual({});
});

it('connects once and disconnects exactly the given connection', () => {
  const document = connect(j2, 'story.out', 'funny.in');
  expect(document.connections.at(-1)).toEqual({from: 'story.out', to: 'funny.in'});
  expect(connect(document, 'story.out', 'funny.in')).toBe(document);
  expect(disconnect(document, 'story.out', 'funny.in').connections).toEqual(j2.connections);
});

it('finds connections that leave ports a node no longer has', () => {
  const document = connect(j2, 'judge.maybe', 'funny.in');
  expect(staleConnections(document, 'judge', catalog)).toEqual([
    {from: 'judge.maybe', to: 'funny.in'},
  ]);
  expect(staleConnections(document, 'missing', catalog)).toEqual([]);
});
