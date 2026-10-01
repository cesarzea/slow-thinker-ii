import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, act} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {executionView, tick} from './support/execution-view.tsx';
import {OperatorServer} from './support/operator-server.ts';

beforeEach(() => {
  localStorage.clear();
  vi.useFakeTimers({toFake: ['setInterval', 'clearInterval']});
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

it('creates a saved session, starts a graph and displays results and authoritative money', async () => {
  const server = executionView();
  await tick();
  await userEvent.type(screen.getByLabelText('New session'), 'New research');
  await userEvent.click(screen.getByRole('button', {name: 'Create session'}));
  await tick();
  await userEvent.type(screen.getByLabelText(/Task or problem/), 'Solve this');
  await userEvent.click(screen.getByRole('button', {name: 'Start run'}));
  await tick();
  expect(screen.getByRole('heading', {name: 'Completed'})).toBeTruthy();
  expect(screen.getByRole('region', {name: 'Final result'}).textContent).toContain('A test result');
  expect(server.mutations).toHaveLength(2);
  await userEvent.click(
    within(screen.getByRole('region', {name: 'Session history'})).getByRole('button'),
  );
  await tick();
  expect(screen.getByRole('heading', {name: 'Completed'})).toBeTruthy();
});

it('stops a running graph without displaying a successful final output', async () => {
  const server = new OperatorServer();
  server.pending = true;
  executionView(server);
  await tick();
  await userEvent.type(screen.getByLabelText(/Task or problem/), 'Wait');
  await userEvent.click(screen.getByRole('button', {name: 'Start run'}));
  await tick();
  await userEvent.click(screen.getByRole('button', {name: 'Stop run'}));
  await tick();
  expect(screen.getByRole('heading', {name: 'Cancelled'})).toBeTruthy();
  expect(screen.queryByRole('region', {name: 'Final result'})).toBeNull();
});

it('can withdraw a recovered Start with missing input instead of reconstructing a prompt', async () => {
  localStorage.setItem('slow-thinker-ii.pending-command', 'start-lost');
  executionView();
  await tick();
  expect(screen.getByRole('complementary', {name: 'Pending request'})).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Check receipt'}));
  await userEvent.click(screen.getByRole('button', {name: 'Withdraw pending start'}));
  await tick();
  expect(screen.queryByRole('complementary', {name: 'Pending request'})).toBeNull();
});

it('reports disconnection while keeping execution unavailable', async () => {
  const server = executionView();
  await tick();
  server.readStatus = 503;
  await tick();
  await userEvent.type(screen.getByLabelText(/Task or problem/), 'Task');
  expect(screen.getByRole('button', {name: 'Start run'}).hasAttribute('disabled')).toBe(true);
  expect(screen.getByText(/Could not confirm/)).toBeTruthy();
});

it('allows explicit dismissal of a non-Start receipt without cancelling it on the server', async () => {
  localStorage.setItem('slow-thinker-ii.pending-command', 'session-lost');
  const server = executionView();
  await tick();
  await act(async () => {
    await userEvent.click(screen.getByRole('button', {name: 'Stop tracking this request'}));
  });
  expect(localStorage.getItem('slow-thinker-ii.pending-command')).toBeNull();
  expect(server.mutations).toHaveLength(0);
});
