import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {act, cleanup, render} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {Inspector} from '../src/features/inspector/index.ts';
import {InspectionServer} from './support/inspection-server.ts';
import {reply} from './support/operator-data.ts';
import {events} from './support/inspection-data.ts';

let server: InspectionServer;
beforeEach(() => {
  server = new InspectionServer();
  vi.stubGlobal('fetch', server.fetch);
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it('links durable events to causal calls, exact own cost and escaped retained arguments', async () => {
  render(<Inspector credential="key" run="run" />);
  await userEvent.click(await screen.findByRole('button', {name: 'View call 3'}));
  expect(await screen.findByText('agent → model.complete')).toBeTruthy();
  expect(screen.getByText(/Own cost: USD 0.000000003/)).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'View arguments'}));
  expect(await screen.findByText(/private input/)).toBeTruthy();
  expect(document.querySelector('script')).toBeNull();
  await userEvent.click(screen.getByRole('button', {name: 'View pricing basis'}));
  expect(await screen.findByText(/pricing:child/)).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'View parent call'}));
  expect(await screen.findByText('No direct charge recorded for this call.')).toBeTruthy();
  expect(screen.getByText('No responses recorded.')).toBeTruthy();
  expect(screen.queryByRole('region', {name: 'Retained content'})).toBeNull();
  expect(server.operator.mutations).toHaveLength(0);
});

it('distinguishes a retained JSON null from missing usage', async () => {
  server.missingUsage = true;
  render(<Inspector credential="key" run="run" />);
  await userEvent.click(await screen.findByRole('button', {name: 'View call 3'}));
  await userEvent.click(await screen.findByRole('button', {name: 'View response'}));
  expect(await screen.findByText('null')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'View reported usage'}));
  expect(await screen.findByText('Content unavailable.')).toBeTruthy();
  expect(screen.getByText('Reason: not_recorded')).toBeTruthy();
});

it('pages through the frozen event view and returns to a fresh first page', async () => {
  render(<Inspector credential="key" run="run" />);
  await userEvent.click(await screen.findByRole('button', {name: 'Next page'}));
  expect(await screen.findByText('No events recorded.')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Back to the beginning'}));
  expect(await screen.findByText('call.requested')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'View content 1'}));
  expect(await screen.findByText(/event:1 · Capture state/)).toBeTruthy();
  expect(server.reads).toContain('/api/v1/runs/run/events?cursor=next-events');
});

it('recovers an explicit read failure without sending a command', async () => {
  server.failed = true;
  render(<Inspector credential="key" run="run" />);
  expect(await screen.findByRole('alert')).toBeTruthy();
  server.failed = false;
  await userEvent.click(screen.getByRole('button', {name: 'Refresh evidence'}));
  expect(await screen.findByText('call.requested')).toBeTruthy();
  expect(server.operator.mutations).toHaveLength(0);
});

it.each(['resolve', 'reject'])('ignores a late %s after closing the inspector', async (outcome) => {
  const response = Promise.withResolvers<Response>();
  vi.stubGlobal('fetch', vi.fn().mockReturnValue(response.promise));
  const view = render(<Inspector credential="key" run="run" />);
  view.unmount();
  await act(async () => {
    if (outcome === 'resolve') response.resolve(reply(events));
    else response.reject(new Error('closed'));
    await Promise.resolve();
  });
  expect(screen.queryByRole('alert')).toBeNull();
  expect(screen.queryByText('call.requested')).toBeNull();
});

it('pages call receipts and distinguishes unconfirmed spending and late response errors', async () => {
  server.call.receipts.next_cursor = 'next-receipt';
  server.call.reason = 'cancelled';
  if (server.call.accounting !== null) {
    server.call.accounting.amount = null;
    server.call.accounting.source = null;
  }
  const receipt = server.call.receipts.items[0];
  if (receipt !== undefined) {
    receipt.publish = false;
    receipt.succeeded = false;
    receipt.reason = 'late';
  }
  render(<Inspector credential="key" run="run" />);
  await userEvent.click(await screen.findByRole('button', {name: 'View call 3'}));
  expect(await screen.findByText(/No confirmed amount/)).toBeTruthy();
  expect(screen.getByText(/Not published as the result/)).toBeTruthy();
  const region = within(screen.getByRole('region', {name: 'Call details'}));
  await userEvent.click(region.getByRole('button', {name: 'Next page'}));
  expect(await region.findByText('No responses recorded.')).toBeTruthy();
  expect(server.reads).toContain('/api/v1/runs/run/calls/child?cursor=next-receipt');
});

it('focuses selected evidence on repeated opening without stealing focus on refresh', async () => {
  render(<Inspector credential="key" run="run" />);
  expect(document.activeElement).toBe(screen.getByRole('heading', {name: 'Run inspector'}));
  const callButton = await screen.findByRole('button', {name: 'View call 3'});
  for (const name of ['View call 3', 'View call 3', 'View content 1', 'View content 1']) {
    await userEvent.click(screen.getByRole('button', {name}));
    const heading = name.includes('call') ? 'Call child' : 'Retained content';
    expect(document.activeElement).toBe(screen.getByRole('heading', {name: heading}));
  }
  const payload = within(screen.getByRole('region', {name: 'Retained content'}));
  const refresh = payload.getByRole('button', {name: 'Refresh evidence'});
  await userEvent.click(refresh);
  await payload.findByText(/event:1 · Capture state/);
  expect(document.activeElement).toBe(refresh);
  await userEvent.click(callButton);
  expect(document.activeElement).toBe(screen.getByRole('heading', {name: 'Call child'}));
});
