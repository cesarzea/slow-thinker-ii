import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {createExecutionModel} from '../src/features/execution/index.ts';
import {reply, runRecord, workspace} from './support/operator-data.ts';
import {OperatorServer} from './support/operator-server.ts';

const signal = (): AbortSignal => new AbortController().signal;
let server: OperatorServer;
beforeEach(() => {
  localStorage.clear();
  server = new OperatorServer();
  vi.stubGlobal('fetch', server.fetch);
});
afterEach(() => {
  vi.unstubAllGlobals();
});

it('does not overlap polls or overwrite a selection changed during a read', async () => {
  const response = Promise.withResolvers<Response>();
  const fetch = vi.fn().mockReturnValue(response.promise);
  vi.stubGlobal('fetch', fetch);
  const model = createExecutionModel('key', localStorage);
  const first = model.polling.refresh(signal());
  await model.polling.refresh(signal());
  model.store.selectSession('another-session');
  response.resolve(reply(workspace));
  await first;
  expect(model.store.snapshot().sessionId).toBe('another-session');
  expect(model.store.snapshot().workspace).toBeNull();
  expect(model.store.snapshot().stale).toBe(true);
  expect(fetch).toHaveBeenCalledTimes(2);
});

it('keeps the last projection when an event sequence regresses', async () => {
  server.run = runRecord();
  const model = createExecutionModel('key', localStorage);
  model.store.selectRun('run');
  await model.polling.refresh(signal());
  server.run.last_event_sequence = 9;
  server.run.state = 'running';
  await model.polling.refresh(signal());
  expect(model.store.snapshot().run?.state).toBe('completed');
  expect(model.store.snapshot().run?.last_event_sequence).toBe(10);
  server.run.backend_generation = 'restarted';
  await model.polling.refresh(signal());
  expect(model.store.snapshot().run?.backend_generation).toBe('restarted');
});

it('does not replace visible state or show errors after an aborted read', async () => {
  const response = Promise.withResolvers<Response>();
  vi.stubGlobal('fetch', vi.fn().mockReturnValue(response.promise));
  const model = createExecutionModel('key', localStorage);
  const controller = new AbortController();
  const pending = model.polling.refresh(controller.signal);
  controller.abort();
  response.reject(new Error('Aborted'));
  await pending;
  expect(model.store.snapshot().message).toBeNull();
  expect(model.store.snapshot().workspace).toBeNull();
});

it('ignores updates and polls after disconnecting the operator', async () => {
  const fetch = vi.fn(server.fetch);
  vi.stubGlobal('fetch', fetch);
  const model = createExecutionModel('key', localStorage);
  model.store.setClosed(true);
  model.store.selectRun('ignored');
  await model.polling.refresh(signal());
  await model.commands.createSession('Ignored');
  expect(model.store.snapshot().runId).toBe('');
  expect(fetch).not.toHaveBeenCalled();
});

it('supports an empty workspace without inventing a session or fetching history', async () => {
  server.workspace.sessions.items = [];
  const fetch = vi.fn(server.fetch);
  vi.stubGlobal('fetch', fetch);
  const model = createExecutionModel('key', localStorage);
  await model.polling.refresh(signal());
  expect(model.store.snapshot().sessionId).toBe('');
  expect(model.store.snapshot().history).toBeNull();
  expect(fetch).toHaveBeenCalledTimes(1);
});
