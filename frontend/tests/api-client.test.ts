import {afterEach, expect, it, vi} from 'vitest';
import {OperatorClient} from '../src/api/index.ts';
import type {GraphDetail} from '../src/api/index.ts';
import {FakeApi} from './support/fake-api.ts';
import {catalogBody, j1} from './support/contract.ts';
import {runDetail, runSummary, usageBody} from './support/runs.ts';

afterEach(() => {
  vi.unstubAllGlobals();
});
const client = (): OperatorClient => new OperatorClient('operator-credential');
const at = '2026-10-04T05:00:00.000Z';
const branch = {
  name: 'main',
  created_at: at,
  from_version: null,
  from_change: null,
  latest_change: 3,
  head_version: 1,
};

it('reads the catalog with the bearer credential, no cookies and no cache', async () => {
  const api = new FakeApi().on('GET /catalog', {status: 200, body: catalogBody}).install();
  const catalog = await client().catalog();
  expect(catalog.components.map((component) => component.label)).toEqual([
    'Trigger',
    'Output',
    'LLM Call',
    'Router',
  ]);
  const call = api.last('GET /catalog');
  expect(call?.init).toMatchObject({credentials: 'omit', cache: 'no-store', method: 'GET'});
  expect(call?.init.headers).toMatchObject({authorization: 'Bearer operator-credential'});
});

it('validates and creates graph documents', async () => {
  const diagnostic = {
    severity: 'warning',
    code: 'no_output_node',
    message: 'The graph has no Output node, so runs produce no results.',
    path: '/nodes',
    node_id: null,
  };
  const api = new FakeApi()
    .on('POST /graphs/validate', {status: 200, body: {diagnostics: [diagnostic]}})
    .on('POST /graphs', {status: 201, body: {id: 'funny-story', branch: 'main', change: 1}})
    .install();
  expect(await client().validate(j1)).toEqual([diagnostic]);
  expect(await client().createGraph(j1)).toEqual({id: 'funny-story', branch: 'main', change: 1});
  expect(api.last('POST /graphs')?.body).toEqual({document: j1});
  expect(api.last('POST /graphs')?.init.headers).toMatchObject({
    'content-type': 'application/json',
  });
});

const summary = {
  id: 'funny-story',
  name: 'Funny story',
  active_version: null,
  latest_change: 3,
  updated_at: at,
};
const versions = [
  {version: 1, branch: 'main', parent: null, change: 2, name: 'Funny story', created_at: at},
];
const detail = {
  id: 'funny-story',
  name: 'Funny story',
  active_version: 1,
  latest_change: 3,
  branches: [branch],
  versions,
};

it('reads graph lists, details and versions', async () => {
  const version = {graph_id: 'funny-story', version: 1, branch: 'main', parent: null, change: 2};
  new FakeApi()
    .on('GET /graphs', {status: 200, body: {graphs: [summary]}})
    .on('GET /graphs/funny-story', {status: 200, body: detail})
    .on('GET /graphs/funny-story/versions/1', {
      status: 200,
      body: {...version, created_at: at, document: j1},
    })
    .install();
  expect(await client().graphs()).toEqual([summary]);
  const read: GraphDetail = await client().graph('funny-story');
  expect([read.versions, read.branches]).toEqual([versions, [branch]]);
  expect(await client().version('funny-story', 1)).toMatchObject({...version, document: j1});
});

it('starts, lists, reads and stops runs', async () => {
  const api = new FakeApi()
    .on('POST /runs', {status: 202, body: {run_id: 'run-1'}})
    .on('GET /runs', {status: 200, body: {runs: [runSummary()]}})
    .on('GET /runs/run-1', {status: 200, body: runDetail()})
    .on('POST /runs/run-1/stop', {status: 202, body: {status: 'cancelled'}})
    .install();
  const input = 'A cat tried to learn to fly.';
  expect(await client().startRun('funny-story', {version: 1}, input)).toBe('run-1');
  expect(api.last('POST /runs')?.body).toEqual({graph_id: 'funny-story', version: 1, input});
  await client().startRun('funny-story', {change: 4}, null);
  expect(api.last('POST /runs')?.body).toEqual({graph_id: 'funny-story', change: 4, input: null});
  expect(await client().runs('funny-story')).toHaveLength(1);
  expect(api.last('GET /runs')?.query.get('graph_id')).toBe('funny-story');
  expect(api.last('GET /runs')?.query.get('limit')).toBe('100');
  await client().runs();
  expect(api.last('GET /runs')?.query.has('graph_id')).toBe(false);
  expect((await client().run('run-1')).results[0]?.name).toBe('Funny story');
  expect(await client().stopRun('run-1')).toBe('cancelled');
  expect(api.last('POST /runs/run-1/stop')?.body).toEqual({});
});

it('pages events after a sequence and reads usage', async () => {
  const api = new FakeApi()
    .on('GET /runs/run-1/events', {status: 200, body: {events: [], last_seq: 4, finished: true}})
    .on('GET /usage', {status: 200, body: usageBody})
    .install();
  expect(await client().events('run-1', 4)).toEqual({events: [], last_seq: 4, finished: true});
  expect(api.last('GET /runs/run-1/events')?.query.get('after')).toBe('4');
  expect(api.last('GET /runs/run-1/events')?.query.get('limit')).toBe('500');
  expect(await client().usage()).toEqual(usageBody);
});

it('encodes identifiers placed in paths', async () => {
  const api = new FakeApi().install();
  await expect(client().graph('a/b')).rejects.toMatchObject({status: 404});
  expect(api.calls[0]?.path).toBe('/graphs/a%2Fb');
});
