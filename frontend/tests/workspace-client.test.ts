import {afterEach, expect, it, vi} from 'vitest';
import {ConfigurationClient, DefinitionClient} from '../src/api/index.ts';
import {configuration} from './support/configuration-data.ts';
import {reply} from './support/operator-data.ts';
import {errorReply, numericSource, signal, textReply} from './support/definition-api.ts';
const command = {
  command_id: 'a'.repeat(32),
  expected_revision: 'workspace-1',
  limits: {run_seconds: 50.5, run_budget: '0.000000001'},
};
const receipt = {...command, configuration_revision: 'workspace-2', replayed: false};
afterEach(() => vi.unstubAllGlobals());

it('reads validated canonical registered descriptors and trusted local schemas', async () => {
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(reply(configuration));
  vi.stubGlobal('fetch', fetcher);
  expect(await new ConfigurationClient('private-key').catalog(signal())).toEqual(configuration);
  expect(fetcher.mock.calls[0]?.[1]).toMatchObject({cache: 'no-store', credentials: 'omit'});
});
it('sends exact source and raw patch values and accepts incomplete object text', async () => {
  const fetcher = vi
    .fn<typeof fetch>()
    .mockResolvedValue(textReply('{"x":1.0,"large":9007199254740993}'));
  vi.stubGlobal('fetch', fetcher);
  const operations = [{op: 'add' as const, path: '/x', value_json: '1.0'}];
  expect(await new DefinitionClient('key').patch(numericSource, operations, signal())).toContain(
    '9007199254740993',
  );
  expect(fetcher.mock.calls[0]?.[1]?.body).toBe(
    JSON.stringify({source: numericSource, operations}),
  );
});
it.each(['[]', 'null', '{', '"text"'])('rejects non-object patch replies: %s', async (source) => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(textReply(source)));
  await expect(
    new DefinitionClient('key').patch('{}', [{op: 'remove', path: '/x'}], signal()),
  ).rejects.toThrow('Could not confirm');
});
it.each([
  [201, 'application/json'],
  [200, 'text/plain'],
])('rejects patch status/content-type %s/%s', async (status, contentType) => {
  vi.stubGlobal(
    'fetch',
    vi.fn<typeof fetch>().mockResolvedValue(textReply('{}', status, contentType)),
  );
  await expect(
    new DefinitionClient('key').patch('{}', [{op: 'remove', path: '/x'}], signal()),
  ).rejects.toThrow('Could not confirm');
});
it('keeps a validated patch rejection definitive', async () => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(errorReply('invalid_patch', 422)));
  await expect(
    new DefinitionClient('key').patch('{}', [{op: 'remove', path: '/x'}], signal()),
  ).rejects.toMatchObject({code: 'invalid_patch'});
});
it('submits unchanged configuration command bytes and matches its receipt', async () => {
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(reply(receipt));
  vi.stubGlobal('fetch', fetcher);
  const body = `\n${JSON.stringify(command)}\n`;
  await new ConfigurationClient('key').limits(body, signal());
  expect(fetcher.mock.calls[0]?.[1]?.body).toBe(body);
});
it.each([
  '{',
  '{}',
  JSON.stringify({...command, limits: {run_seconds: 0}}),
  JSON.stringify({...command, limits: {run_budget: '0.1234567891'}}),
])('rejects malformed local commands before transport', async (body) => {
  const fetcher = vi.fn<typeof fetch>();
  vi.stubGlobal('fetch', fetcher);
  await expect(new ConfigurationClient('key').limits(body, signal())).rejects.toMatchObject({
    code: 'invalid_limits',
  });
  expect(fetcher).not.toHaveBeenCalled();
});
it.each([
  ['invalid_limits', 422],
  ['configuration_conflict', 409],
  ['configuration_active', 409],
  ['budget_below_commitments', 422],
])('retains definitive configuration %s', async (code, status) => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(errorReply(code, status)));
  await expect(
    new ConfigurationClient('key').limits(JSON.stringify(command), signal()),
  ).rejects.toMatchObject({code});
});
it.each([
  errorReply('operator_service_unavailable', 503),
  errorReply('response_too_large', 413),
  reply({...receipt, command_id: 'b'.repeat(32)}),
  reply({}),
  textReply('{'),
])('classifies unconfirmed configuration replies for safe replay', async (response) => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(response));
  await expect(
    new ConfigurationClient('key').limits(JSON.stringify(command), signal()),
  ).rejects.toThrow('Replay the unchanged command');
});
it('classifies a lost configuration response for unchanged replay', async () => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockRejectedValue(new Error('lost')));
  await expect(
    new ConfigurationClient('key').limits(JSON.stringify(command), signal()),
  ).rejects.toThrow('Replay the unchanged command');
});
