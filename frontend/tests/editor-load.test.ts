import {afterEach, expect, it, vi} from 'vitest';
import {OperatorClient} from '../src/api/index.ts';
import {loadEditor} from '../src/features/editor/state/load.ts';
import {newGraphDocument} from '../src/features/editor/state/defaults.ts';
import {graphServer} from './support/graph-server.ts';
import {failure} from './support/fake-api.ts';
import {j1} from './support/contract.ts';

afterEach(() => {
  vi.unstubAllGlobals();
});
const signal = new AbortController().signal;
const client = (): OperatorClient => new OperatorClient('operator-credential');

it('opens the latest change of the branch with the graph’s versions', async () => {
  const {api, state} = graphServer('funny-story', j1);
  state.changes.push({...j1, name: 'Edited'}, {...j1, name: 'Edited again'});
  api.install();
  const source = await loadEditor(client(), 'funny-story', 'main', null, signal);
  expect(source.document.name).toBe('Edited again');
  expect(source.target).toEqual({graphId: 'funny-story', branch: 'main', exists: true});
  expect(source.stored).toEqual({change: 3, at: '2026-10-04T10:42:00.000Z', revision: 0});
  expect(source.versions).toEqual({
    active: 1,
    activeBranch: 'main',
    next: 2,
    head: 1,
    since: {version: 1},
    pending: 2,
  });
  expect(source.catalog.components.map((item) => item.type)).toContain('llm-call');
  expect(api.last('GET /graphs/funny-story/changes')?.query.get('branch')).toBe('main');
});

it('opens a graph created on the graphs page before it is stored', async () => {
  graphServer('new-one', null).api.install();
  const created = newGraphDocument('new-one', 'New one');
  const source = await loadEditor(client(), 'new-one', 'main', created, signal);
  expect([source.document, source.stored, source.target.exists]).toEqual([created, null, false]);
  expect(source.versions).toEqual({
    active: null,
    activeBranch: null,
    next: 1,
    head: null,
    since: null,
    pending: 0,
  });
  graphServer('missing', null).api.install();
  await expect(loadEditor(client(), 'missing', 'main', created, signal)).rejects.toThrow(
    'This graph does not exist.',
  );
});

it('falls back to the first branch and reports other failures', async () => {
  const {api} = graphServer('funny-story', j1);
  api.install();
  const source = await loadEditor(client(), 'funny-story', 'gone', null, signal);
  expect(source.target.branch).toBe('main');
  api.on('GET /graphs/funny-story', failure(500, 'internal_error', 'Broken.'));
  await expect(loadEditor(client(), 'funny-story', 'main', null, signal)).rejects.toThrow(
    'Broken.',
  );
  api.on('GET /graphs/funny-story', {
    status: 200,
    body: {
      id: 'funny-story',
      name: 'x',
      active_version: null,
      latest_change: 1,
      branches: [],
      versions: [],
    },
  });
  await expect(loadEditor(client(), 'funny-story', 'main', null, signal)).rejects.toThrow(
    'This graph has no branch “main”.',
  );
});
