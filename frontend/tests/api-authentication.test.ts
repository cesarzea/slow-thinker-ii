import {afterEach, expect, it, vi} from 'vitest';
import {OperatorClient, observeAuthentication} from '../src/api/index.ts';
import {reply} from './support/fake-api.ts';

const credential = 'authentication-fixture';
const cleanups: (() => void)[] = [];
afterEach(() => {
  for (const cleanup of cleanups.splice(0)) cleanup();
  vi.unstubAllGlobals();
});

it.each([401, 403])('notifies the active connection when the API answers %s', async (status) => {
  const invalidated = vi.fn();
  cleanups.push(observeAuthentication(credential, invalidated));
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply({}, status)));
  await expect(new OperatorClient(credential).graphs()).rejects.toThrow();
  expect(invalidated).toHaveBeenCalledTimes(1);
});

it('captures the lease before the request and ignores obsolete replies', async () => {
  const old = vi.fn();
  cleanups.push(observeAuthentication(credential, old));
  const deferred = Promise.withResolvers<Response>();
  vi.stubGlobal('fetch', vi.fn().mockReturnValue(deferred.promise));
  const request = new OperatorClient(credential).graphs().catch(() => undefined);
  const current = vi.fn();
  cleanups.push(observeAuthentication(credential, current));
  deferred.resolve(reply({}, 403));
  await request;
  expect(old).not.toHaveBeenCalled();
  expect(current).not.toHaveBeenCalled();
});

it('does not invalidate after cancellation or once the connection is gone', async () => {
  const invalidated = vi.fn();
  const disconnect = observeAuthentication(credential, invalidated);
  cleanups.push(disconnect);
  const deferred = Promise.withResolvers<Response>();
  vi.stubGlobal('fetch', vi.fn().mockReturnValue(deferred.promise));
  const controller = new AbortController();
  const request = new OperatorClient(credential).graphs(controller.signal).catch(() => undefined);
  controller.abort();
  disconnect();
  disconnect();
  deferred.resolve(reply({}, 401));
  await request;
  expect(invalidated).not.toHaveBeenCalled();
});

it('keeps the connection on other errors', async () => {
  const invalidated = vi.fn();
  cleanups.push(observeAuthentication(credential, invalidated));
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply({}, 422)));
  await expect(new OperatorClient(credential).graphs()).rejects.toThrow();
  expect(invalidated).not.toHaveBeenCalled();
});
