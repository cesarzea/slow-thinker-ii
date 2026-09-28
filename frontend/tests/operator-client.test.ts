import {afterEach, expect, it, vi} from 'vitest';
import {OperatorClient} from '../src/api/index.ts';
import {reply, runRecord, workspace} from './support/operator-data.ts';

const signal = (): AbortSignal => new AbortController().signal;
afterEach(() => {
  vi.unstubAllGlobals();
});

it('uses explicit operator authority and encodes cursor/path data', async () => {
  const fetcher = vi.fn().mockResolvedValue(reply(workspace));
  vi.stubGlobal('fetch', fetcher);
  await new OperatorClient('credential').workspace(signal(), 'a+b/c');
  expect(fetcher).toHaveBeenCalledWith(
    '/api/v1/workspace?cursor=a%2Bb%2Fc',
    expect.objectContaining({
      credentials: 'omit',
      cache: 'no-store',
      headers: expect.objectContaining({authorization: 'Bearer credential'}) as unknown,
    }),
  );
});

it.each([401, 403, 404, 503])('rejects a failed authoritative read (%s)', async (status) => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply({}, status)));
  await expect(new OperatorClient('key').workspace(signal())).rejects.toThrow();
});

it('rejects malformed schemas without inventing run state', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue(reply({...runRecord(), state: 'maybe-finished'})),
  );
  await expect(new OperatorClient('key').run('run', signal())).rejects.toThrow();
});

it('separates a missing receipt from an authentication or storage failure', async () => {
  const fetcher = vi
    .fn()
    .mockResolvedValueOnce(reply({}, 404))
    .mockResolvedValueOnce(reply({}, 503));
  vi.stubGlobal('fetch', fetcher);
  const client = new OperatorClient('key');
  expect(await client.command('missing', signal())).toBeNull();
  await expect(client.command('existing', signal())).rejects.toThrow();
});

it('keeps durable rejection receipts even when HTTP reports a rejected command', async () => {
  const receipt = {
    command_id: 'x',
    kind: 'start',
    disposition: 'rejected',
    target_id: null,
    reason: 'budget',
  };
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply(receipt, 409)));
  expect(await new OperatorClient('key').send('/runs', {command_id: 'x'})).toEqual(receipt);
});

it('does not treat an unstructured server error as an accepted command', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply({error: 'failed'}, 503)));
  await expect(new OperatorClient('key').send('/runs', {})).rejects.toThrow();
});

it('makes unavailable results explicit and preserves arbitrary valid JSON', async () => {
  const fetcher = vi
    .fn()
    .mockResolvedValueOnce(reply({status: 'unavailable', content: null}))
    .mockResolvedValueOnce(reply({status: 'recorded', content: ['value', null]}));
  vi.stubGlobal('fetch', fetcher);
  const client = new OperatorClient('key');
  expect(await client.result('run', signal())).toContain('No hay resultado');
  expect(JSON.parse(await client.result('run', signal())) as unknown).toEqual(['value', null]);
});

it('reads the next page of session history through its exact opaque cursor', async () => {
  const fetcher = vi.fn().mockResolvedValue(reply({items: [], next_cursor: null}));
  vi.stubGlobal('fetch', fetcher);
  await new OperatorClient('key').history('a/b', signal(), 'x/y');
  expect(fetcher).toHaveBeenCalledWith(
    '/api/v1/sessions/a%2Fb/runs?cursor=x%2Fy',
    expect.any(Object),
  );
});
