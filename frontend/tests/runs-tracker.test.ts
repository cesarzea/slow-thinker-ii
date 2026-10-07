import {afterEach, expect, it, vi} from 'vitest';
import {ApiError} from '../src/api/index.ts';
import type {RunDetail, RunReason, RunStatus} from '../src/api/index.ts';
import {RunTracker} from '../src/features/runs/run-tracker.ts';
import {durationLabel, runStatusText} from '../src/ui/index.ts';
import {runDetail} from './support/runs.ts';

afterEach(() => {
  vi.useRealTimers();
});
const detail = (status: RunStatus): RunDetail => runDetail({status}) as unknown as RunDetail;

it('polls every interval until the run reaches a terminal status', async () => {
  vi.useFakeTimers();
  const read = vi
    .fn<(signal: AbortSignal) => Promise<RunDetail>>()
    .mockResolvedValueOnce(detail('starting'))
    .mockRejectedValueOnce(new ApiError(0, 'network_error', 'Could not reach the server.'))
    .mockResolvedValueOnce(detail('running'))
    .mockResolvedValue(detail('completed'));
  const tracker = new RunTracker(read, 1000);
  const changes = vi.fn();
  const unsubscribe = tracker.subscribe(changes);
  tracker.start();
  await vi.advanceTimersByTimeAsync(0);
  expect(tracker.snapshot().run?.status).toBe('starting');
  await vi.advanceTimersByTimeAsync(1000);
  expect(tracker.snapshot().error).toBe('Could not reach the server.');
  await vi.advanceTimersByTimeAsync(2000);
  expect(tracker.snapshot()).toMatchObject({error: null, run: {status: 'completed'}});
  await vi.advanceTimersByTimeAsync(5000);
  expect(read).toHaveBeenCalledTimes(4);
  expect(changes).toHaveBeenCalledTimes(4);
  unsubscribe();
});

it('stops polling, ignores replies after stopping and refreshes on request', async () => {
  vi.useFakeTimers();
  const pending = Promise.withResolvers<RunDetail>();
  const read = vi
    .fn<(signal: AbortSignal) => Promise<RunDetail>>()
    .mockReturnValueOnce(pending.promise)
    .mockResolvedValue(detail('running'));
  const tracker = new RunTracker(read);
  tracker.start();
  tracker.refresh();
  tracker.stop();
  pending.resolve(detail('running'));
  await vi.advanceTimersByTimeAsync(3000);
  expect(tracker.snapshot().run).toBeNull();
  tracker.refresh();
  expect(read).toHaveBeenCalledTimes(1);
  tracker.start();
  await vi.advanceTimersByTimeAsync(0);
  tracker.refresh();
  await vi.advanceTimersByTimeAsync(0);
  expect(read).toHaveBeenCalledTimes(3);
  tracker.stop();
  read.mockRejectedValueOnce(new Error('late'));
  await vi.advanceTimersByTimeAsync(1000);
  expect(tracker.snapshot().error).toBeNull();
});

it.each<[RunStatus, RunReason | null, string]>([
  ['starting', null, 'Starting'],
  ['running', null, 'Running'],
  ['completed', null, 'Completed'],
  ['stopped', 'activation_limit', 'Stopped: activation limit reached'],
  ['stopped', 'time_limit', 'Stopped: time limit reached'],
  ['stopped', 'budget_run', 'Stopped: run budget exhausted'],
  ['stopped', 'budget_day', 'Stopped: daily budget exhausted'],
  ['stopped', 'budget_month', 'Stopped: monthly budget exhausted'],
  ['stopped', null, 'Stopped'],
  ['failed', 'startup_failed', 'Failed: a component could not start'],
  ['failed', 'activation_failed', 'Failed: an activation failed'],
  ['failed', 'interrupted', 'Failed: interrupted by a server restart'],
  ['failed', 'internal_error', 'Failed: internal error'],
  ['failed', null, 'Failed'],
  ['cancelled', 'cancelled', 'Cancelled'],
])('describes %s with %s', (status, reason, text) => {
  expect(runStatusText(status, reason)).toBe(text);
});

it('formats durations', () => {
  expect([durationLabel(null), durationLabel(250), durationLabel(1340)]).toEqual([
    '—',
    '250 ms',
    '1.3 s',
  ]);
});
