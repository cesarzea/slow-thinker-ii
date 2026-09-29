import {afterEach, expect, it, vi} from 'vitest';
import {OperatorClient} from '../src/api/index.ts';
import {
  boundedDetail,
  executionPage,
  savedDefinition,
  singleDetail,
} from './support/projection-data.ts';
import {reply, runRecord} from './support/operator-data.ts';
const signal = (): AbortSignal => new AbortController().signal;
afterEach(() => {
  vi.unstubAllGlobals();
});

it('validates full definitions and encodes exact identities and snapshot cursors', async () => {
  const fetch = vi
    .fn()
    .mockResolvedValueOnce(reply(boundedDetail))
    .mockResolvedValueOnce(reply(savedDefinition()))
    .mockResolvedValueOnce(reply(executionPage));
  vi.stubGlobal('fetch', fetch);
  const client = new OperatorClient('key');
  expect(await client.graph('bounded-review', 'example-1', signal())).toEqual(boundedDetail);
  expect(await client.definition('run', signal())).toMatchObject(singleDetail);
  expect(await client.execution('run', signal(), 'a/b+')).toEqual(executionPage);
  expect(fetch.mock.calls.map((call) => call[0] as unknown)).toEqual([
    '/api/v1/graphs/bounded-review/revisions/example-1',
    '/api/v1/runs/run/definition',
    '/api/v1/runs/run/execution?cursor=a%2Fb%2B',
  ]);
});
it('rejects state, saved definition and execution records belonging to another run', async () => {
  vi.stubGlobal(
    'fetch',
    vi
      .fn()
      .mockResolvedValueOnce(reply(runRecord('other')))
      .mockResolvedValueOnce(reply(savedDefinition(singleDetail, 'other')))
      .mockResolvedValueOnce(reply({...executionPage, run_id: 'other'})),
  );
  const client = new OperatorClient('key');
  await expect(client.run('run', signal())).rejects.toThrow('otra ejecución');
  await expect(client.definition('run', signal())).rejects.toThrow('otra ejecución');
  await expect(client.execution('run', signal())).rejects.toThrow('otra ejecución');
});
it.each(['another', 'example-9'])(
  'rejects a catalog definition with mismatched requested identity %s',
  async (identity) => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply(singleDetail)));
    const client = new OperatorClient('key');
    await expect(client.graph(identity, singleDetail.revision, signal())).rejects.toThrow();
    await expect(client.graph(singleDetail.graph_id, identity, signal())).rejects.toThrow();
  },
);
it.each([
  {...singleDetail, definition: {}},
  {...singleDetail, graph_id: 'another'},
  {...singleDetail, revision: 'another'},
  {...executionPage, activations: [...executionPage.activations, ...executionPage.activations]},
  {...executionPage, calls: [...executionPage.calls, ...executionPage.calls]},
])('rejects malformed definitions or duplicate evidence identities', async (value) => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply(value)));
  const client = new OperatorClient('key');
  await expect(
    'definition' in value
      ? client.graph('single-agent', 'example-2', signal())
      : client.execution('run', signal()),
  ).rejects.toThrow();
});
