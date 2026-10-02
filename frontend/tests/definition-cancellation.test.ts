import {afterEach, expect, it, vi} from 'vitest';
import {DefinitionClient, DefinitionError} from '../src/api/index.ts';
import {reference, target, numericSource, textReply, signal} from './support/definition-api.ts';
import {reply} from './support/operator-data.ts';

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

it('uses explicit read and save timeout signals', async () => {
  const timeout = vi.spyOn(AbortSignal, 'timeout');
  const fetcher = vi
    .fn<typeof fetch>()
    .mockResolvedValueOnce(reply({items: [], next_cursor: null}))
    .mockResolvedValueOnce(reply({...reference, validation_scope: 'definition'}))
    .mockResolvedValueOnce(textReply())
    .mockResolvedValueOnce(textReply(numericSource.replace(reference.revision, target.revision)))
    .mockResolvedValueOnce(reply({...reference, created: true}, 201));
  vi.stubGlobal('fetch', fetcher);
  const client = new DefinitionClient('key');
  await client.list(signal());
  await client.validate(numericSource, signal());
  await client.source(reference, signal());
  await client.draft(reference, target, signal());
  await client.save(numericSource, signal());
  expect(timeout.mock.calls.map((call) => call[0])).toEqual([
    10_000, 10_000, 10_000, 10_000, 65_000,
  ]);
});

it.each(['caller', 'timeout'] as const)(
  'cancels pending reads with the %s signal',
  async (cause) => {
    const caller = new AbortController();
    const timeout = new AbortController();
    vi.spyOn(AbortSignal, 'timeout').mockReturnValue(timeout.signal);
    installAbortableFetch();
    const result = new DefinitionClient('key')
      .source(reference, caller.signal)
      .catch((error: unknown) => error);
    (cause === 'caller' ? caller : timeout).abort();
    expect(await result).toEqual(
      new Error('Could not confirm the definition response. Refresh and try again.'),
    );
  },
);

it.each(['caller', 'timeout'] as const)(
  'makes Save cancellation uncertain for the %s signal',
  async (cause) => {
    const caller = new AbortController();
    const timeout = new AbortController();
    vi.spyOn(AbortSignal, 'timeout').mockReturnValue(timeout.signal);
    installAbortableFetch();
    const result = new DefinitionClient('key')
      .save(numericSource, caller.signal)
      .catch((error: unknown) => error);
    (cause === 'caller' ? caller : timeout).abort();
    expect(await result).not.toBeInstanceOf(DefinitionError);
    expect(await result).toEqual(
      new Error(
        'Could not confirm whether the definition was saved. Replay the unchanged source to recover.',
      ),
    );
  },
);

it('makes network failure during Save uncertain without exposing its exception', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn<typeof fetch>().mockRejectedValue(new Error('private credential exception')),
  );
  await expect(new DefinitionClient('key').save(numericSource, signal())).rejects.toThrow(
    'Replay the unchanged source',
  );
});

function installAbortableFetch(): void {
  vi.stubGlobal(
    'fetch',
    vi.fn<typeof fetch>(
      (_, options) =>
        new Promise<Response>((_resolve, reject) => {
          const abort = (): void => {
            reject(new DOMException('Abort', 'AbortError'));
          };
          if (options?.signal?.aborted === true) abort();
          else options?.signal?.addEventListener('abort', abort, {once: true});
        }),
    ),
  );
}
