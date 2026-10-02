import {afterEach, expect, it, vi} from 'vitest';
import {act, cleanup, renderHook, waitFor} from '@testing-library/react';
import {useDiscovery} from '../src/features/workspace/index.tsx';
import {configuration} from './support/configuration-data.ts';
import {reply} from './support/operator-data.ts';
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
it('keeps viewer discovery idle and retries a failed authenticated read explicitly', async () => {
  const fetcher = vi
    .fn<typeof fetch>()
    .mockRejectedValueOnce(new Error('offline'))
    .mockResolvedValue(reply(configuration));
  vi.stubGlobal('fetch', fetcher);
  const viewer = renderHook(() => useDiscovery(undefined));
  expect(viewer.result.current).toMatchObject({catalog: null, loading: false, error: null});
  expect(fetcher).not.toHaveBeenCalled();
  const view = renderHook(() => useDiscovery('key'));
  await waitFor(() => {
    expect(view.result.current.error).toContain('Refresh');
  });
  act(() => {
    view.result.current.refresh();
  });
  await waitFor(() => {
    expect(view.result.current.catalog?.configuration_revision).toBe(
      configuration.configuration_revision,
    );
  });
  expect(view.result.current).toMatchObject({loading: false, error: null});
});
it('aborts superseded and disconnected discovery replies without accepting stale catalog data', async () => {
  const old = Promise.withResolvers<Response>();
  const fetcher = vi
    .fn<typeof fetch>()
    .mockReturnValueOnce(old.promise)
    .mockResolvedValue(reply({...configuration, configuration_revision: 'new'}));
  vi.stubGlobal('fetch', fetcher);
  const view = renderHook(({credential}) => useDiscovery(credential), {
    initialProps: {credential: 'old'},
  });
  view.rerender({credential: 'new'});
  await waitFor(() => {
    expect(view.result.current.catalog?.configuration_revision).toBe('new');
  });
  await act(async () => {
    old.resolve(reply(configuration));
    await old.promise;
  });
  expect(view.result.current.catalog?.configuration_revision).toBe('new');
  expect(fetcher.mock.calls[0]?.[1]?.signal?.aborted).toBe(true);
  view.unmount();
  expect(fetcher.mock.calls[1]?.[1]?.signal?.aborted).toBe(true);
});
it('ignores a failed discovery read after unmount', async () => {
  const deferred = Promise.withResolvers<Response>();
  vi.stubGlobal('fetch', vi.fn<typeof fetch>().mockReturnValue(deferred.promise));
  const view = renderHook(() => useDiscovery('key'));
  view.unmount();
  await act(async () => {
    deferred.reject(new Error('closed'));
    await deferred.promise.catch(() => undefined);
  });
  expect(view.result.current.error).toBeNull();
});
