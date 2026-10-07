import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {OperatorClient} from '../src/api/index.ts';
import {ActivityPage} from '../src/features/activity/index.ts';
import {failure} from './support/fake-api.ts';
import {activityApi as api, graphId} from './support/activity-api.ts';
import {j3Events} from './support/j3-events.ts';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it('shows the detail of a refused model call', async () => {
  const refused = {
    ...j3Events[8],
    data: {
      ...(j3Events[8]?.['data'] as object),
      llm: null,
      request: null,
      rates: null,
      response: undefined,
      error: {code: 'budget_exhausted', message: 'The run budget is exhausted.'},
    },
  };
  const events = [...j3Events.slice(0, 8), refused];
  api().on('GET /runs/run-1/events', {status: 200, body: {events, last_seq: 9, finished: true}});
  render(
    <ActivityPage
      client={new OperatorClient('credential')}
      graphId={graphId}
      runId="run-1"
      runHref="#/run"
    />,
  );
  const row = await screen.findByRole('button', {
    name: /Unknown model · Error: The run budget is exhausted\./u,
  });
  await userEvent.click(row);
  const detail = screen.getByRole('region', {name: 'Details of event 9'});
  expect(within(detail).getByText('Error')).toBeTruthy();
  expect(detail.textContent).toContain('budget_exhausted');
});

it('reports events that cannot be read', async () => {
  api().on('GET /runs/run-1/events', failure(503, 'unavailable', 'Events are unavailable.'));
  render(
    <ActivityPage
      client={new OperatorClient('credential')}
      graphId={graphId}
      runId="run-1"
      runHref="#/run"
    />,
  );
  expect((await screen.findByRole('alert')).textContent).toBe(
    'Could not read the activity. Events are unavailable.',
  );
  expect(screen.getByText('Recording…')).toBeTruthy();
});
