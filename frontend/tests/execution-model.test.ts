import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {createExecutionModel} from '../src/features/execution/index.ts';
import {graph} from './support/operator-data.ts';
import {OperatorServer} from './support/operator-server.ts';

let server: OperatorServer;
const signal = (): AbortSignal => new AbortController().signal;
const pendingKey = 'slow-thinker-ii.pending-command';

beforeEach(() => {
  localStorage.clear();
  server = new OperatorServer();
  vi.stubGlobal('fetch', server.fetch);
});
afterEach(() => {
  vi.unstubAllGlobals();
});

it('creates a session and executes the selected graph without retaining its prompt', async () => {
  const model = createExecutionModel('secret-access', localStorage);
  await model.polling.refresh(signal());
  await model.commands.createSession('New research');
  await model.polling.refresh(signal());
  expect(model.store.snapshot().sessionId).toBe('new-session');
  await model.commands.start(graph, 'Private research prompt');
  await model.polling.refresh(signal());
  expect(model.store.snapshot().run?.state).toBe('completed');
  expect(model.store.snapshot().history?.items).toHaveLength(1);
  expect(localStorage).toHaveLength(0);
  expect(server.mutations[1]?.body).toContain('Private research prompt');
});

it('retains only the command identity after a lost response and recovers after reload', async () => {
  const first = createExecutionModel('key', localStorage);
  await first.polling.refresh(signal());
  server.loseReply = true;
  await first.commands.start(graph, 'Do not store this prompt');
  const id = localStorage.getItem(pendingKey);
  expect(id).toMatch(/^start-/);
  expect(JSON.stringify(localStorage)).not.toContain('Do not store');
  first.store.setClosed(true);
  const reloaded = createExecutionModel('key', localStorage);
  await reloaded.polling.refresh(signal());
  expect(reloaded.store.snapshot().pending).toBeNull();
  expect(reloaded.store.snapshot().run?.state).toBe('completed');
  expect(server.mutations).toHaveLength(1);
});

it('retries only on explicit action using the original identity and body', async () => {
  const model = createExecutionModel('key', localStorage);
  await model.polling.refresh(signal());
  server.loseReply = true;
  await model.commands.start(graph, 'task');
  server.loseReply = false;
  await model.commands.retry();
  expect(server.mutations[1]).toEqual(server.mutations[0]);
  expect(model.store.snapshot().pending).toBeNull();
});

it('withdraws an unconfirmed Start instead of generating a new intention', async () => {
  localStorage.setItem(pendingKey, 'start-unconfirmed');
  const model = createExecutionModel('key', localStorage);
  await model.polling.refresh(signal());
  expect(model.store.snapshot().message).toContain('unconfirmed');
  await model.commands.start(graph, 'must not dispatch');
  expect(server.mutations).toHaveLength(0);
  await model.commands.withdraw();
  expect(server.mutations[0]?.path).toBe('/commands/start-unconfirmed/withdraw');
  expect(model.store.snapshot().pending).toBeNull();
});

it('stops a running workflow and preserves its acknowledgement before projection refresh', async () => {
  server.pending = true;
  const model = createExecutionModel('key', localStorage);
  await model.polling.refresh(signal());
  await model.commands.start(graph, 'task');
  await model.polling.refresh(signal());
  expect(model.store.snapshot().run?.state).toBe('running');
  await model.commands.stop();
  expect(model.store.snapshot().stopRequested).toBe(true);
  await model.polling.refresh(signal());
  expect(model.store.snapshot().run?.state).toBe('cancelled');
});
