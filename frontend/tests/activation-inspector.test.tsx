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
  await userEvent.click(await screen.findByRole('button', {name: 'Ver llamada 3'}));
  await userEvent.click(await screen.findByRole('button', {name: 'Ver activación'}));
  await screen.findByText('Agente: agent · Nodo: draft');
}

it('navigates from a resource call to its activation, effective input and eligible output', async () => {
  await openActivation();
  expect(screen.queryByRole('region', {name: 'Detalle de llamada'})).toBeNull();
  expect(document.activeElement).toBe(screen.getByRole('heading', {name: 'Activación activation'}));
  await userEvent.click(screen.getByRole('button', {name: 'Ver entrada efectiva'}));
  expect(await screen.findByText(/request:parent · Estado/)).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Ver salida publicada'}));
  expect(await screen.findByText('null')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Ver procedencia de entradas'}));
  expect(await screen.findByText(/bindings:parent · Estado/)).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Abrir llamada'}));
  expect(await screen.findByText('agent → model.complete')).toBeTruthy();
  expect(server.operator.mutations).toHaveLength(0);
});

it('pages calls within the chosen activation and links back to its root call', async () => {
  await openActivation();
  const region = within(screen.getByRole('region', {name: 'Detalle de activación'}));
  await userEvent.click(region.getByRole('button', {name: 'Página siguiente'}));
  await userEvent.click(await region.findByRole('button', {name: 'Volver al principio'}));
  expect(await region.findByRole('button', {name: 'Abrir llamada'})).toBeTruthy();
  await userEvent.click(region.getByRole('button', {name: 'Ver llamada principal'}));
  expect(await screen.findByText('Sin cargo directo registrado para esta llamada.')).toBeTruthy();
  expect(server.reads).toContain('/api/v1/runs/run/activations/activation?cursor=next-activation');
});

it('does not offer a final output when an activation has failed', async () => {
  server.activation.state = 'failed';
  server.activation.reason = 'provider_error';
  server.activation.node_id = null;
  server.activation.output_payload_id = null;
  render(<Inspector credential="key" run="run" />);
  await userEvent.click(await screen.findByRole('button', {name: 'Ver llamada 3'}));
  await userEvent.click(await screen.findByRole('button', {name: 'Ver activación'}));
  expect(await screen.findByText('No hay salida publicada para esta activación.')).toBeTruthy();
  expect(screen.getByText('Estado: failed · provider_error')).toBeTruthy();
  expect(screen.queryByRole('button', {name: 'Ver salida publicada'})).toBeNull();
});
