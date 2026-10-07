import {afterEach, expect, it, vi} from 'vitest';
import {ApiError, EVENT_PAGE_LIMIT} from '../src/api/index.ts';
import type {EventPage, RunEvent} from '../src/api/index.ts';
import {EventTracker} from '../src/features/activity/event-tracker.ts';
import {j3Events} from './support/j3-events.ts';

afterEach(() => {
  vi.useRealTimers();
});
const events = j3Events as unknown as RunEvent[];
const page = (list: readonly RunEvent[], finished: boolean): EventPage => ({
  events: [...list],
  last_seq: list.at(-1)?.seq ?? 0,
  finished,
});

it('reads full pages at once and polls while the log is open', async () => {
  vi.useFakeTimers();
  const full = Array.from(
    {length: EVENT_PAGE_LIMIT},
    (_, index) => ({...events[0], seq: index + 1}) as RunEvent,
  );
  const read = vi
    .fn<(after: number, signal: AbortSignal) => Promise<EventPage>>()
    .mockResolvedValueOnce(page(full, true))
    .mockResolvedValueOnce(page([], false))
    .mockRejectedValueOnce(new ApiError(0, 'network_error', 'Offline.'))
    .mockResolvedValue(page([{...events[1], seq: 501} as RunEvent], true));
  const tracker = new EventTracker(read, 1000);
  tracker.start();
  await vi.advanceTimersByTimeAsync(0);
  expect(read.mock.calls.map((call) => call[0])).toEqual([0, 500]);
  expect(tracker.snapshot().finished).toBe(false);
  await vi.advanceTimersByTimeAsync(1000);
  expect(tracker.snapshot().error).toBe('Offline.');
  await vi.advanceTimersByTimeAsync(1000);
  expect(tracker.snapshot()).toMatchObject({finished: true, error: null});
  expect(tracker.snapshot().events).toHaveLength(501);
  tracker.stop();
});

it('ignores replies once stopped', async () => {
  const pending = Promise.withResolvers<EventPage>();
  const failing = Promise.withResolvers<EventPage>();
  const tracker = new EventTracker(
    vi.fn().mockReturnValueOnce(pending.promise).mockReturnValueOnce(failing.promise),
  );
  tracker.start();
  tracker.stop();
  pending.resolve(page(events, true));
  tracker.start();
  tracker.stop();
  failing.reject(new Error('late'));
  await Promise.allSettled([pending.promise, failing.promise]);
  expect(tracker.snapshot()).toEqual({events: [], finished: false, error: null});
});
