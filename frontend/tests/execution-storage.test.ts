import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {createExecutionModel} from '../src/features/execution/index.ts';
import {graph} from './support/operator-data.ts';
import {OperatorServer} from './support/operator-server.ts';

const pendingKey = 'slow-thinker-ii.pending-command';
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

it('blocks mutation when previous command tracking cannot be read', async () => {
  const storage = {
    getItem: (): never => {
      throw new Error('Storage blocked');
    },
    setItem: vi.fn(),
    removeItem: vi.fn(),
  };
  const model = createExecutionModel('key', storage);
  await model.polling.refresh(signal());
  await model.commands.createSession('Research');
  await model.commands.start(graph, 'Task');
  expect(server.mutations).toHaveLength(0);
  expect(model.store.snapshot().message).toContain('No se puede leer');
});

it('does not dispatch a command whose identity could not be persisted', async () => {
  const storage = {
    getItem: (): null => null,
    setItem: (): never => {
      throw new Error('Quota exceeded');
    },
    removeItem: vi.fn(),
  };
  const model = createExecutionModel('key', storage);
  await model.commands.createSession('Research');
  expect(server.mutations).toHaveLength(0);
  expect(model.store.snapshot().pending).toBeNull();
  expect(model.store.snapshot().message).toContain('No se ha enviado');
});

it('keeps a committed receipt recoverable when local deletion fails', async () => {
  const storage = {
    getItem: localStorage.getItem.bind(localStorage),
    setItem: localStorage.setItem.bind(localStorage),
    removeItem: vi.fn().mockImplementation(() => {
      throw new Error('Storage locked');
    }),
  };
  const model = createExecutionModel('key', storage);
  await model.commands.createSession('Research');
  expect(model.store.snapshot().pending).toMatch(/^session-/);
  model.commands.forgetNonStart();
  expect(model.store.snapshot().message).toContain('No se pudo eliminar');
  storage.removeItem.mockImplementation(localStorage.removeItem.bind(localStorage));
  await model.polling.refresh(signal());
  expect(model.store.snapshot().sessionId).toBe('new-session');
  expect(model.store.snapshot().pending).toBeNull();
  expect(server.mutations).toHaveLength(1);
});

it('does not permit local dismissal of an unresolved Start', async () => {
  localStorage.setItem(pendingKey, 'start-unresolved');
  const model = createExecutionModel('key', localStorage);
  model.commands.forgetNonStart();
  await model.commands.retry();
  expect(model.store.snapshot().pending).toBe('start-unresolved');
  expect(server.mutations).toHaveLength(0);
});

it('keeps an unresolved command after receipt lookup fails', async () => {
  localStorage.setItem(pendingKey, 'session-unresolved');
  server.readStatus = 503;
  const model = createExecutionModel('key', localStorage);
  await model.polling.refresh(signal());
  expect(model.store.snapshot().pending).toBe('session-unresolved');
  expect(model.store.snapshot().stale).toBe(true);
  expect(server.mutations).toHaveLength(0);
});
