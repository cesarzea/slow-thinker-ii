import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {executionView, tick} from './support/execution-view.tsx';
import {OperatorServer} from './support/operator-server.ts';
import {runRecord} from './support/operator-data.ts';

beforeEach(() => {
  localStorage.clear();
  vi.useFakeTimers({toFake: ['setInterval', 'clearInterval']});
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

it('navigates session and execution pages while preserving the selected session', async () => {
  const server = new OperatorServer();
  server.workspace.sessions.next_cursor = 'next-session';
  server.historyCursor = 'next-run';
  executionView(server);
  await tick();
  await userEvent.selectOptions(screen.getByLabelText('Saved session'), 'session');
  await tick();
  await userEvent.click(screen.getByRole('button', {name: 'More sessions'}));
  server.workspace.sessions.items = [];
  await tick();
  expect(screen.getByRole('option', {name: 'Selected session'})).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'First sessions'}));
  await tick();
  expect(screen.queryByRole('button', {name: 'First sessions'})).toBeNull();
  await userEvent.click(screen.getByRole('button', {name: 'More runs'}));
  await tick();
  await userEvent.click(screen.getByRole('button', {name: 'First runs'}));
  await tick();
  expect(screen.queryByRole('button', {name: 'First runs'})).toBeNull();
});

it('opens the blocking run and reports a result retrieval failure explicitly', async () => {
  const server = new OperatorServer();
  server.workspace.blocking_run_id = 'run';
  server.workspace.admission_available = false;
  server.run = runRecord();
  server.run.reason = 'recorded-reason';
  server.resultStatus = 503;
  executionView(server);
  await tick();
  await userEvent.click(screen.getByRole('button', {name: 'View the run blocking new starts'}));
  await tick();
  expect(screen.getByText('Could not load the result.')).toBeTruthy();
  expect(screen.getByText('Reason: recorded-reason')).toBeTruthy();
});

it('retries a lost command response explicitly from the pending controls', async () => {
  const server = executionView();
  server.loseReply = true;
  await tick();
  await userEvent.type(screen.getByLabelText(/Task or problem/), 'Private task');
  await userEvent.click(screen.getByRole('button', {name: 'Start run'}));
  server.loseReply = false;
  await userEvent.click(await screen.findByRole('button', {name: 'Resend the same command'}));
  expect(server.mutations[0]).toEqual(server.mutations[1]);
  expect(screen.queryByRole('complementary', {name: 'Pending request'})).toBeNull();
});
