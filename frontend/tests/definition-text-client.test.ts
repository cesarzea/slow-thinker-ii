import {afterEach, expect, it, vi} from 'vitest';
import {DefinitionClient} from '../src/api/index.ts';
import {
  reference,
  target,
  signal,
  numericSource,
  textReply,
  errorReply,
  item,
} from './support/definition-api.ts';

afterEach(() => vi.unstubAllGlobals());

it('loads exact original source text without rounding or normalizing it', async () => {
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(textReply());
  vi.stubGlobal('fetch', fetcher);
  const source = await new DefinitionClient('key').source(reference, signal());
  expect(source).toBe(numericSource);
  expect(source).toContain('1.0');
  expect(source).toContain('9007199254740993');
  expect(fetcher.mock.calls[0]?.[0]).toBe(
    '/api/v1/definitions/source?graph_id=single-agent&revision=personal+%CE%B1+%2F+one',
  );
});

it('drafts with identity strings only and returns original numeric text', async () => {
  const source = numericSource.replace(reference.revision, target.revision);
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(textReply(source));
  vi.stubGlobal('fetch', fetcher);
  expect(await new DefinitionClient('key').draft(item, target, signal())).toBe(source);
  expect(fetcher.mock.calls[0]?.[0]).toBe('/api/v1/definitions/draft');
  expect(fetcher.mock.calls[0]?.[1]?.body).toBe(JSON.stringify({source: reference, target}));
});

it.each([
  [
    'different revision',
    numericSource.replace(reference.revision, 'other'),
    200,
    'application/json',
  ],
  ['different graph', numericSource.replace('single-agent', 'another'), 200, 'application/json'],
  ['wrong status', numericSource, 201, 'application/json'],
  ['wrong content type', numericSource, 200, 'text/plain'],
  ['malformed text', '{', 200, 'application/json'],
  ['invalid identity', '{"graph_id":"Invalid","revision":"x"}', 200, 'application/json'],
])('rejects source responses with %s', async (_, source, status, contentType) => {
  vi.stubGlobal(
    'fetch',
    vi.fn<typeof fetch>().mockResolvedValue(textReply(source, status, contentType)),
  );
  await expect(new DefinitionClient('key').source(reference, signal())).rejects.toThrow(
    'Could not confirm',
  );
});

it('requires the exact target identity in draft replies', async () => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(textReply()));
  await expect(new DefinitionClient('key').draft(reference, target, signal())).rejects.toThrow(
    'Could not confirm',
  );
});

it('accepts JSON content parameters while preserving text', async () => {
  vi.stubGlobal(
    'fetch',
    vi
      .fn<typeof fetch>()
      .mockResolvedValue(textReply(numericSource, 200, 'application/json; charset=utf-8')),
  );
  expect(await new DefinitionClient('key').source(reference, signal())).toBe(numericSource);
});

it('retains stable source and draft rejections', async () => {
  vi.stubGlobal(
    'fetch',
    vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(errorReply('definition_not_found', 404))
      .mockResolvedValueOnce(errorReply('invalid_definition', 422)),
  );
  const client = new DefinitionClient('key');
  await expect(client.source(reference, signal())).rejects.toMatchObject({
    code: 'definition_not_found',
  });
  await expect(client.draft(reference, target, signal())).rejects.toMatchObject({
    code: 'invalid_definition',
  });
});
