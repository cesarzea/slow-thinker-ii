import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {Inspector} from '../src/features/inspector/index.ts';
import {InspectionServer} from './support/inspection-server.ts';

let server: InspectionServer;
beforeEach(() => {
  server = new InspectionServer();
  vi.stubGlobal('fetch', server.fetch);
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

async function openActivation(): Promise<void> {
  render(<Inspector credential="key" run="run" />);
  await userEvent.click(await screen.findByRole('button', {name: 'View call 3'}));
  await userEvent.click(await screen.findByRole('button', {name: 'View activation'}));
  await screen.findByText('Agent: agent · Node: draft');
}

it('navigates from a resource call to its activation, effective input and eligible output', async () => {
  await openActivation();
  expect(screen.queryByRole('region', {name: 'Call details'})).toBeNull();
  expect(document.activeElement).toBe(screen.getByRole('heading', {name: 'Activation activation'}));
  await userEvent.click(screen.getByRole('button', {name: 'View effective input'}));
  expect(await screen.findByText(/request:parent · Capture state/)).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'View published output'}));
  expect(await screen.findByText('null')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'View input provenance'}));
  expect(await screen.findByText(/bindings:parent · Capture state/)).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'View call'}));
  expect(await screen.findByText('agent → model.complete')).toBeTruthy();
  expect(server.operator.mutations).toHaveLength(0);
});

it('pages calls within the chosen activation and links back to its root call', async () => {
  await openActivation();
  const region = within(screen.getByRole('region', {name: 'Activation details'}));
  await userEvent.click(region.getByRole('button', {name: 'Next page'}));
  await userEvent.click(await region.findByRole('button', {name: 'Back to the beginning'}));
  expect(await region.findByRole('button', {name: 'View call'})).toBeTruthy();
  await userEvent.click(region.getByRole('button', {name: 'View root call'}));
  expect(await screen.findByText('No direct charge recorded for this call.')).toBeTruthy();
  expect(server.reads).toContain('/api/v1/runs/run/activations/activation?cursor=next-activation');
});

it('does not offer a final output when an activation has failed', async () => {
  server.activation.state = 'failed';
  server.activation.reason = 'provider_error';
  server.activation.node_id = null;
  server.activation.output_payload_id = null;
  render(<Inspector credential="key" run="run" />);
  await userEvent.click(await screen.findByRole('button', {name: 'View call 3'}));
  await userEvent.click(await screen.findByRole('button', {name: 'View activation'}));
  expect(await screen.findByText('No output was published for this activation.')).toBeTruthy();
  expect(screen.getByText('State: failed · provider_error')).toBeTruthy();
  expect(screen.queryByRole('button', {name: 'View published output'})).toBeNull();
});
