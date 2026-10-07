import {afterEach, expect, it, vi} from 'vitest';
import {OperatorClient, observeAuthentication} from '../src/api/index.ts';
import {FakeApi, failure} from './support/fake-api.ts';

afterEach(() => {
  vi.unstubAllGlobals();
});

it.each(['token', 'none'])('reads the access mode %s without sending a token', async (mode) => {
  const api = new FakeApi()
    .on('GET /access', {status: 200, body: {authentication: mode}})
    .install();
  expect(await new OperatorClient('operator-credential').access()).toEqual({authentication: mode});
  expect(api.last('GET /access')?.init.headers).not.toHaveProperty('authorization');
});

it('rejects an access mode it does not know', async () => {
  new FakeApi().on('GET /access', {status: 200, body: {authentication: 'cookie'}}).install();
  await expect(new OperatorClient(null).access()).rejects.toMatchObject({code: 'invalid_response'});
});

it('sends no Authorization header without a credential', async () => {
  const api = new FakeApi().on('GET /graphs', {status: 200, body: {graphs: []}}).install();
  expect(await new OperatorClient(null).graphs()).toEqual([]);
  expect(api.last('GET /graphs')?.init.headers).toEqual({accept: 'application/json'});
});

it('tells the connection without a credential when the API answers 401', async () => {
  const invalidated = vi.fn();
  const stop = observeAuthentication(null, invalidated);
  new FakeApi().on('GET /graphs', failure(401, 'unauthorized', 'Token required.')).install();
  await expect(new OperatorClient(null).graphs()).rejects.toThrow();
  stop();
  expect(invalidated).toHaveBeenCalledTimes(1);
});
