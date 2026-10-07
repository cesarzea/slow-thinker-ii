import {afterEach, expect, it, vi} from 'vitest';
import {ApiError, OperatorClient, errorMessage} from '../src/api/index.ts';
import {FakeApi, failure} from './support/fake-api.ts';
import {catalogBody, j1} from './support/contract.ts';

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});
const client = (): OperatorClient => new OperatorClient('operator-credential');
const diagnostic = {
  severity: 'error',
  code: 'service_not_selected',
  message: 'Select a model.',
  path: '/nodes/1/config/model',
  node_id: 'proposer',
};

it('maps invalid documents to an ApiError with their diagnostics', async () => {
  new FakeApi()
    .on('POST /graphs', failure(422, 'invalid_document', 'Invalid.', {diagnostics: [diagnostic]}))
    .install();
  const error = await client()
    .createGraph(j1)
    .catch((caught: unknown) => caught);
  expect(error).toBeInstanceOf(ApiError);
  expect(error).toMatchObject({status: 422, code: 'invalid_document', diagnostics: [diagnostic]});
  expect(errorMessage(error)).toBe('Invalid.');
});

it.each([
  ['graph_exists', 409],
  ['too_many_runs', 409],
  ['graph_not_found', 404],
  ['version_not_found', 404],
])('keeps the documented %s error', async (code, status) => {
  new FakeApi().on('GET /graphs/x', failure(status, code, 'Explained.')).install();
  await expect(client().graph('x')).rejects.toMatchObject({status, code, message: 'Explained.'});
});

it('refuses an error code reported with an undocumented status', async () => {
  new FakeApi().on('GET /graphs/x', failure(500, 'graph_exists', 'Odd.')).install();
  await expect(client().graph('x')).rejects.toMatchObject({code: 'invalid_response'});
});

it.each([
  [{error: {code: 'x', message: 'y', extra: 1}}, 500],
  ['plain', 502],
  [null, 500],
])('rejects error bodies outside the envelope (%#)', async (body, status) => {
  new FakeApi().on('GET /usage', {status, body}).install();
  await expect(client().usage()).rejects.toMatchObject({status, code: 'invalid_response'});
});

it('names refused access when the server sends no error envelope', async () => {
  new FakeApi().on('GET /usage', {status: 401}).install();
  await expect(client().usage()).rejects.toMatchObject({code: 'access_denied'});
});

it('rejects replies with unknown fields or unexpected success statuses', async () => {
  const extra = {...catalogBody, version: 2};
  new FakeApi()
    .on('GET /catalog', {status: 200, body: extra})
    .on('POST /graphs', {status: 200, body: {id: 'x', version: 1}})
    .install();
  await expect(client().catalog()).rejects.toMatchObject({code: 'invalid_response'});
  await expect(client().createGraph(j1)).rejects.toMatchObject({code: 'invalid_response'});
});

it('reports network failures, cancellation and timeouts as ApiErrors', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('offline')));
  await expect(client().usage()).rejects.toMatchObject({code: 'network_error', status: 0});
  const controller = new AbortController();
  controller.abort();
  await expect(client().usage(controller.signal)).rejects.toMatchObject({code: 'aborted'});
  vi.spyOn(AbortSignal, 'timeout').mockReturnValue(AbortSignal.abort());
  await expect(client().usage()).rejects.toMatchObject({code: 'timeout'});
  expect(errorMessage(new Error('x'))).toBe('Something went wrong. Try again.');
});

it('rejects replies that are not JSON', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('<html>', {status: 200})));
  await expect(client().usage()).rejects.toMatchObject({code: 'invalid_response'});
});
