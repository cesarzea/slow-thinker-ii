import {afterEach, expect, it, vi} from 'vitest';
import {DefinitionClient, DefinitionError} from '../src/api/index.ts';
import {signal, numericSource, errorReply} from './support/definition-api.ts';
import {reply} from './support/operator-data.ts';

afterEach(() => vi.unstubAllGlobals());

it.each([
  ['invalid_json', 400],
  ['invalid_query', 400],
  ['invalid_cursor', 400],
  ['unsupported_transport_options', 400],
  ['operator_authentication_required', 401],
  ['operator_host_denied', 403],
  ['operator_origin_denied', 403],
  ['definition_not_found', 404],
  ['definition_conflict', 409],
  ['request_too_large', 413],
  ['response_too_large', 413],
  ['json_content_required', 415],
  ['invalid_definition', 422],
  ['definition_parent_missing', 422],
  ['operator_service_unavailable', 503],
])('exposes recognized status-matching read errors (%s)', async (code, status) => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(errorReply(code, status)));
  await expect(new DefinitionClient('key').list(signal())).rejects.toMatchObject({
    code,
    issues: [],
  });
});

it('keeps at most ten bounded diagnostic pointers and messages', async () => {
  const issues = Array.from({length: 10}, () => ({
    pointer: '/' + 'a'.repeat(159),
    message: 'm'.repeat(160),
  }));
  vi.stubGlobal(
    'fetch',
    vi.fn<typeof fetch>().mockResolvedValue(errorReply('invalid_definition', 422, issues)),
  );
  await expect(new DefinitionClient('key').validate(numericSource, signal())).rejects.toMatchObject(
    {code: 'invalid_definition', issues},
  );
});

it.each([
  Array.from({length: 11}, () => ({pointer: '', message: 'Invalid.'})),
  [{pointer: '/' + 'a'.repeat(160), message: 'Invalid.'}],
  [{pointer: '', message: 'm'.repeat(161)}],
  [{pointer: '/invalid~2', message: 'Invalid.'}],
  [{pointer: '', message: ''}],
])('does not expose invalid or oversized issue envelopes', async (issues) => {
  vi.stubGlobal(
    'fetch',
    vi.fn<typeof fetch>().mockResolvedValue(errorReply('invalid_definition', 422, issues)),
  );
  const error: unknown = await new DefinitionClient('key')
    .validate(numericSource, signal())
    .catch((value: unknown) => value);
  expect(error).toBeInstanceOf(Error);
  expect(error).not.toBeInstanceOf(DefinitionError);
});

it.each([
  errorReply('definition_conflict', 422),
  errorReply('private_exception_secret', 503),
  reply({schema_version: 'wrong', error: {code: 'invalid_json'}}, 400),
  reply(
    {
      schema_version: '0.1-draft',
      error: {code: 'invalid_json', message: 'm'.repeat(161), request_id: 'x'},
    },
    400,
  ),
])('rejects mismatched or unsafe error envelopes', async (response) => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(response));
  const result: unknown = await new DefinitionClient('key')
    .list(signal())
    .catch((value: unknown) => value);
  expect(result).not.toBeInstanceOf(DefinitionError);
  expect(result).toEqual(
    new Error('Could not confirm the definition response. Refresh and try again.'),
  );
});

it.each([
  errorReply('operator_service_unavailable', 503),
  errorReply('response_too_large', 413),
  reply({}, 200),
  reply({graph_id: 'single-agent', revision: 'x', created: true}, 200),
  reply({graph_id: 'single-agent', revision: 'x', created: false}, 201),
  reply({graph_id: 'single-agent', revision: 'x', created: true}, 202),
  new Response('private server failure', {status: 502}),
])('classifies unconfirmed saves as uncertain outcomes', async (response) => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(response));
  const result: unknown = await new DefinitionClient('key')
    .save(numericSource, signal())
    .catch((value: unknown) => value);
  expect(result).not.toBeInstanceOf(DefinitionError);
  expect(result).toEqual(
    new Error(
      'Could not confirm whether the definition was saved. Replay the unchanged source to recover.',
    ),
  );
});

it('retains an acknowledged pre-insert Save conflict', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn<typeof fetch>().mockResolvedValue(errorReply('definition_conflict', 409)),
  );
  await expect(new DefinitionClient('key').save(numericSource, signal())).rejects.toMatchObject({
    code: 'definition_conflict',
  });
});
