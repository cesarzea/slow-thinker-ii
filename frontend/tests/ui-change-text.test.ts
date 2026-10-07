import {expect, it} from 'vitest';
import type {GraphDocument} from '../src/api/index.ts';
import {describeChange} from '../src/ui/index.ts';
import {catalog, copy, j1} from './support/contract.ts';

function edited(change: (document: GraphDocument) => void): GraphDocument {
  const document = copy(j1);
  change(document);
  return document;
}

it('names added and removed nodes with their component', () => {
  const without = edited((document) => {
    document.nodes = document.nodes.filter((node) => node.id !== 'result');
    document.connections = document.connections.filter((link) => link.to !== 'result.in');
  });
  expect(describeChange(without, j1, catalog)).toBe(
    'Added Funny story (Output); Connected Proposer · out → Funny story · in',
  );
  expect(describeChange(j1, without, catalog)).toBe(
    'Removed Funny story (Output); Disconnected Proposer · out → Funny story · in',
  );
});

it('names renamed nodes and the sections whose fields changed', () => {
  const after = edited((document) => {
    const proposer = document.nodes.find((node) => node.id === 'proposer');
    if (proposer === undefined) throw new Error('No proposer');
    proposer.name = 'Writer';
    proposer.config['prompt'] = 'Write a shorter story.';
  });
  expect(describeChange(j1, after, catalog)).toBe(
    'Renamed Proposer to Writer; Writer · Prompt edited',
  );
  expect(describeChange(j1, after, null)).toBe(
    'Renamed Proposer to Writer; Writer · Configuration edited',
  );
});

it('tells a moved node from an arranged graph, and names graph-level edits', () => {
  const moved = edited((document) => {
    document.layout = {...document.layout, story: [40, 100]};
  });
  expect(describeChange(j1, moved, catalog)).toBe('Moved Story');
  const arranged = edited((document) => {
    document.layout = {story: [0, 0], proposer: [200, 0], result: [400, 0]};
  });
  expect(describeChange(j1, arranged, catalog)).toBe('Arranged the graph');
  const renamed = edited((document) => {
    document.name = 'Funnier story';
    document.limits.max_activations = 30;
    document.layout = {...document.layout, story: [40, 100]};
  });
  expect(describeChange(j1, renamed, catalog)).toBe(
    'Renamed the graph to Funnier story; Limits edited; and 1 more',
  );
  expect(describeChange(j1, copy(j1), catalog)).toBe('No visible change');
});
