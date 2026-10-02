import {afterEach, expect, it, vi} from 'vitest';
import {DefinitionClient, DefinitionError} from '../src/api/index.ts';
import {item, reference, signal, numericSource, errorReply} from './support/definition-api.ts';
import {reply} from './support/operator-data.ts';
import {singleDetail} from './support/projection-data.ts';

afterEach(() => vi.unstubAllGlobals());

it('requests a bounded page with explicit operator authority and exact cursor encoding', async () => {
  const fetcher = vi
    .fn<typeof fetch>()
    .mockResolvedValue(reply({items: [item], next_cursor: 'next'}));
  vi.stubGlobal('fetch', fetcher);
  expect(await new DefinitionClient('key').list(signal(), 'a+/ b', 25)).toEqual({
    items: [item],
    next_cursor: 'next',
  });
  expect(fetcher.mock.calls[0]?.[0]).toBe('/api/v1/definitions?cursor=a%2B%2F+b&limit=25');
  expect(fetcher.mock.calls[0]?.[1]).toMatchObject({
    credentials: 'omit',
    cache: 'no-store',
    headers: {authorization: 'Bearer key'},
  });
});

it.each([0, 101, 1.5, Number.NaN])(
  'rejects invalid page size before fetching (%s)',
  async (limit) => {
    const fetcher = vi.fn<typeof fetch>();
    vi.stubGlobal('fetch', fetcher);
    await expect(
      new DefinitionClient('key').list(signal(), undefined, limit),
    ).rejects.toBeInstanceOf(DefinitionError);
    expect(fetcher).not.toHaveBeenCalled();
  },
);

it.each([
  {items: [{...item, origin: 'external'}], next_cursor: null},
  {items: [{...item, input_schema: null}], next_cursor: null},
  {items: [item, item], next_cursor: null},
  {
    items: Array.from({length: 101}, (_, index) => ({...item, revision: String(index)})),
    next_cursor: null,
  },
  {items: [], next_cursor: ''},
  {},
])('rejects malformed or unbounded library pages', async (page) => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(reply(page)));
  await expect(new DefinitionClient('key').list(signal())).rejects.toThrow('Could not confirm');
});

it('encodes and validates exact detail identity using query fields', async () => {
  const detail = {
    ...singleDetail,
    revision: reference.revision,
    definition: {...singleDetail.definition, revision: reference.revision},
  };
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(reply(detail));
  vi.stubGlobal('fetch', fetcher);
  expect(await new DefinitionClient('key').detail(reference, signal())).toEqual(detail);
  expect(fetcher.mock.calls[0]?.[0]).toBe(
    '/api/v1/definitions/detail?graph_id=single-agent&revision=personal+%CE%B1+%2F+one',
  );
});

it('rejects a coherent detail from a different requested identity', async () => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(reply(singleDetail)));
  await expect(new DefinitionClient('key').detail(reference, signal())).rejects.toThrow(
    'Could not confirm',
  );
});

it('posts numeric authoring text unchanged for validation and save', async () => {
  const fetcher = vi
    .fn<typeof fetch>()
    .mockResolvedValueOnce(reply({...reference, validation_scope: 'definition'}))
    .mockResolvedValueOnce(reply({...reference, created: true}, 201));
  vi.stubGlobal('fetch', fetcher);
  const client = new DefinitionClient('key');
  expect(await client.validate(numericSource, signal())).toEqual({
    ...reference,
    validation_scope: 'definition',
  });
  expect(await client.save(numericSource, signal())).toEqual({...reference, created: true});
  expect(fetcher.mock.calls.map((call) => call[1]?.body)).toEqual([numericSource, numericSource]);
});

it('preserves duplicate properties so the backend can reject them', async () => {
  const source = '{"revision":"first","revision":"second"}';
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(errorReply('invalid_json', 400));
  vi.stubGlobal('fetch', fetcher);
  await expect(new DefinitionClient('key').save(source, signal())).rejects.toMatchObject({
    code: 'invalid_json',
  });
  expect(fetcher.mock.calls[0]?.[1]?.body).toBe(source);
});

it('accepts canonical replay only with the 200 replay status', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn<typeof fetch>().mockResolvedValue(reply({...reference, created: false})),
  );
  expect(await new DefinitionClient('key').save(numericSource, signal())).toEqual({
    ...reference,
    created: false,
  });
});

it.each([
  {...reference, validation_scope: 'execution'},
  {graph_id: 'Invalid', revision: 'x', validation_scope: 'definition'},
])('rejects invalid validation identities or scope', async (result) => {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockResolvedValue(reply(result)));
  await expect(new DefinitionClient('key').validate(numericSource, signal())).rejects.toThrow(
    'Could not confirm',
  );
});
