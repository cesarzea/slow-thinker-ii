import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {act, cleanup, render, screen} from '@testing-library/react';
import {OperatorClient} from '../src/api/index.ts';
import {RunsPage} from '../src/features/history/index.ts';
import {POLL_INTERVAL_MS} from '../src/features/history/use-run-list.ts';
import {FakeApi, failure} from './support/fake-api.ts';
import type {Reply} from './support/fake-api.ts';
import {runSummary} from './support/runs.ts';

beforeEach(() => {
  vi.useFakeTimers({shouldAdvanceTime: true});
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});
const running = {status: 200, body: {runs: [runSummary({status: 'running', totals: {}})]}};
const completed = {status: 200, body: {runs: [runSummary()]}};

function serve(reply: () => Reply): FakeApi {
  return new FakeApi()
    .on('GET /graphs', {status: 200, body: {graphs: []}})
    .on('GET /runs', reply)
    .install();
}

function renderPage(): void {
  render(
    <RunsPage
      client={new OperatorClient('credential')}
      graphId={null}
      runHref={() => '#/run'}
      onGraphChange={vi.fn()}
    />,
  );
}

async function wait(intervals: number): Promise<void> {
  await act(async () => vi.advanceTimersByTimeAsync(POLL_INTERVAL_MS * intervals));
}

it('reads the runs again every 5 seconds while one has not finished', async () => {
  let reply: Reply = running;
  const api = serve(() => reply);
  renderPage();
  expect(await screen.findByText('Running')).toBeTruthy();
  reply = completed;
  await wait(1);
  expect(await screen.findByText('Completed')).toBeTruthy();
  await wait(3);
  expect(api.count('GET /runs')).toBe(2);
});

it('keeps the runs and keeps polling after a failed read while a run is active', async () => {
  let reply: Reply = running;
  serve(() => reply);
  renderPage();
  expect(await screen.findByText('Running')).toBeTruthy();
  reply = failure(503, 'unavailable', 'Later.');
  await wait(1);
  expect((await screen.findByRole('alert')).textContent).toContain('Later.');
  expect(screen.getByText('Running')).toBeTruthy();
  reply = completed;
  await wait(1);
  expect(await screen.findByText('Completed')).toBeTruthy();
  expect(screen.queryByRole('alert')).toBeNull();
});
