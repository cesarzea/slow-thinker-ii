/** Run mode: executing what is on screen, its failures, stops and running again. */
import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {appApi, connectApp} from './support/app-harness.tsx';
import {copy, j1} from './support/contract.ts';
import {failure} from './support/fake-api.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {openRun, runPanel} from './support/run-mode.ts';
import {runDetail} from './support/runs.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});

it('sends the Trigger message without asking when the Trigger says so', async () => {
  const sending = copy(j1);
  const trigger = sending.nodes.find((node) => node.id === 'story');
  if (trigger !== undefined) trigger.config = {...trigger.config, manual_runs: 'send'};
  const api = appApi(sending);
  await connectApp('#/graphs/funny-story');
  await userEvent.click(await screen.findByRole('button', {name: 'Run'}));
  expect(within(runPanel()).queryByRole('textbox', {name: 'Message'})).toBeNull();
  expect(within(runPanel()).getByText(/^Sends the Trigger's message/u)).toBeTruthy();
  await userEvent.click(within(runPanel()).getByRole('button', {name: 'Execute'}));
  await waitFor(() => {
    expect(api.last('POST /runs')?.body).toMatchObject({input: 'A cat tried to learn to fly.'});
  });
});

it('reports a run that does not start and stops a running one', async () => {
  const api = appApi(j1).on('POST /runs', failure(409, 'too_many_runs', 'Four runs are active.'));
  await connectApp('#/graphs/funny-story');
  await userEvent.click(await screen.findByRole('button', {name: 'Run'}));
  await userEvent.click(within(runPanel()).getByRole('button', {name: 'Execute'}));
  expect((await within(runPanel()).findByRole('alert')).textContent).toBe(
    'The run did not start. Four runs are active.',
  );
  api
    .on('POST /runs', {status: 202, body: {run_id: 'run-1'}})
    .on('GET /runs/run-1', {status: 200, body: runDetail({status: 'running', ended_at: null})})
    .on('POST /runs/run-1/stop', {status: 202, body: {status: 'cancelled'}});
  await userEvent.click(within(runPanel()).getByRole('button', {name: 'Execute'}));
  await userEvent.click(await within(runPanel()).findByRole('button', {name: 'Stop'}));
  expect(api.count('POST /runs/run-1/stop')).toBe(1);
});

it('runs again from the panel and goes back to editing', async () => {
  await openRun();
  await userEvent.click(await within(runPanel()).findByRole('button', {name: 'Run again'}));
  expect(within(runPanel()).getByRole('button', {name: 'Execute'})).toBeTruthy();
  expect(window.location.hash).toBe('#/graphs/funny-story-with-review');
  const [close, back] = within(runPanel()).getAllByRole('button', {name: 'Back to editing'});
  if (close === undefined || back === undefined) throw new Error('No way back to editing');
  expect(close.classList.contains('icon-button')).toBe(true);
  await userEvent.click(back);
  expect(screen.getByRole('navigation', {name: 'Components'})).toBeTruthy();
});
