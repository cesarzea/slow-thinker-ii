import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {createExecutionModel} from '../src/features/execution/index.ts';
import {OperatorServer} from './support/operator-server.ts';
import {executionPage, savedDefinition, singleDetail} from './support/projection-data.ts';
import {reply, runRecord} from './support/operator-data.ts';
let server: OperatorServer;
const signal = (): AbortSignal => new AbortController().signal;
beforeEach(() => {
  localStorage.clear();
  server = new OperatorServer();
  server.run = runRecord();
  vi.stubGlobal('fetch', server.fetch);
});
afterEach(() => {
  vi.unstubAllGlobals();
});
function selected(): ReturnType<typeof createExecutionModel> {
  const model = createExecutionModel('key', localStorage);
  model.store.selectRun('run');
  return model;
}
it('assembles each snapshot without mixing pages or losing a complete visible one', async () => {
  const model = selected();
  server.execution = {...executionPage, calls: [], next_cursor: 'page-two'};
  await model.polling.refresh(signal());
  expect(model.store.snapshot().execution?.activations).toHaveLength(1);
  server.execution = {...executionPage, activations: []};
  await model.polling.refresh(signal());
  expect(model.store.snapshot().execution?.calls).toHaveLength(1);
  server.execution = {...executionPage, through_sequence: 20, calls: [], next_cursor: 'new-two'};
  await model.polling.refresh(signal());
  expect(model.store.snapshot().execution?.through_sequence).toBe(10);
  server.execution = {...executionPage, through_sequence: 20, activations: []};
  await model.polling.refresh(signal());
  expect(model.store.snapshot().execution?.through_sequence).toBe(20);
});
it.each([
  {...executionPage, through_sequence: 11},
  {...executionPage, backend_generation: 'other'},
  {...executionPage, graph_revision: 'other'},
  {...executionPage, next_cursor: 'page-two', activations: [], calls: []},
  {...executionPage, calls: []},
  {...executionPage, activations: [], calls: executionPage.calls},
])(
  'rejects an inconsistent or repeated next page without replacing visible evidence',
  async (page) => {
    const model = selected();
    server.execution = {...executionPage, next_cursor: 'page-two'};
    await model.polling.refresh(signal());
    server.execution = page;
    await model.polling.refresh(signal());
    expect(model.store.snapshot().projectionError).toContain('No se pudo actualizar');
    expect(model.store.snapshot().execution?.through_sequence).toBe(10);
  },
);
it('rejects regressed fresh snapshots and recovers without commands', async () => {
  const model = selected();
  await model.polling.refresh(signal());
  server.execution = {...executionPage, through_sequence: 9};
  await model.polling.refresh(signal());
  expect(model.store.snapshot().projectionError).not.toBeNull();
  server.execution = executionPage;
  await model.polling.refresh(signal());
  expect(model.store.snapshot().projectionError).toBeNull();
  expect(server.mutations).toHaveLength(0);
});
it.each(['graph_id', 'revision'] as const)(
  'requires the saved %s to match the selected run',
  async (field) => {
    const model = selected();
    const detail = {
      ...singleDetail,
      [field]: 'another',
      definition: {...singleDetail.definition, [field]: 'another'},
    };
    server.definition = savedDefinition(detail);
    await model.polling.refresh(signal());
    expect(model.store.snapshot().detail).toBeNull();
    expect(model.store.snapshot().projectionError).not.toBeNull();
  },
);
it('discards a late live page when the selected run changes', async () => {
  const pending = Promise.withResolvers<Response>();
  vi.stubGlobal('fetch', (url: string, init?: RequestInit) =>
    url.endsWith('/execution') ? pending.promise : server.fetch(url, init),
  );
  const model = selected();
  const read = model.polling.refresh(signal());
  await vi.waitFor(() => {
    expect(model.store.snapshot().stale).toBe(true);
  });
  model.store.selectRun('other');
  pending.resolve(reply(executionPage));
  await read;
  expect(model.store.snapshot().runId).toBe('other');
  expect(model.store.snapshot().execution).toBeNull();
});
it('discards an aborted live page and does not publish errors', async () => {
  const model = selected();
  const controller = new AbortController();
  vi.stubGlobal('fetch', async (url: string, init?: RequestInit) => {
    if (url.endsWith('/execution')) controller.abort();
    return await server.fetch(url, init);
  });
  await model.polling.refresh(controller.signal);
  expect(model.store.snapshot().execution).toBeNull();
  expect(model.store.snapshot().projectionError).toBeNull();
});
