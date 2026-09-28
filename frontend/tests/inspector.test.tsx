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
  await userEvent.click(await screen.findByRole('button', {name: 'Ver llamada 3'}));
  expect(await screen.findByText('agent → model.complete')).toBeTruthy();
  expect(screen.getByText(/Coste propio: USD 0.000000003/)).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Ver argumentos'}));
  expect(await screen.findByText(/private input/)).toBeTruthy();
  expect(document.querySelector('script')).toBeNull();
  await userEvent.click(screen.getByRole('button', {name: 'Ver base de cálculo'}));
  expect(await screen.findByText(/pricing:child/)).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Ver llamada de origen'}));
  expect(await screen.findByText('Sin cargo directo registrado para esta llamada.')).toBeTruthy();
  expect(screen.getByText('No hay respuestas registradas.')).toBeTruthy();
  expect(screen.queryByRole('region', {name: 'Contenido conservado'})).toBeNull();
  expect(server.operator.mutations).toHaveLength(0);
});

it('distinguishes a retained JSON null from missing usage', async () => {
  server.missingUsage = true;
  render(<Inspector credential="key" run="run" />);
  await userEvent.click(await screen.findByRole('button', {name: 'Ver llamada 3'}));
  await userEvent.click(await screen.findByRole('button', {name: 'Ver respuesta'}));
  expect(await screen.findByText('null')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Ver uso comunicado'}));
  expect(await screen.findByText('Contenido no disponible.')).toBeTruthy();
  expect(screen.getByText('Motivo: not_recorded')).toBeTruthy();
});

it('pages through the frozen event view and returns to a fresh first page', async () => {
  render(<Inspector credential="key" run="run" />);
  await userEvent.click(await screen.findByRole('button', {name: 'Página siguiente'}));
  expect(await screen.findByText('No hay eventos registrados.')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Volver al principio'}));
  expect(await screen.findByText('call.requested')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Ver contenido 1'}));
  expect(await screen.findByText(/event:1 · Estado/)).toBeTruthy();
  expect(server.reads).toContain('/api/v1/runs/run/events?cursor=next-events');
});

it('recovers an explicit read failure without sending a command', async () => {
  server.failed = true;
  render(<Inspector credential="key" run="run" />);
  expect(await screen.findByRole('alert')).toBeTruthy();
  server.failed = false;
  await userEvent.click(screen.getByRole('button', {name: 'Actualizar evidencia'}));
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
  await userEvent.click(await screen.findByRole('button', {name: 'Ver llamada 3'}));
  expect(await screen.findByText(/Sin importe confirmado/)).toBeTruthy();
  expect(screen.getByText(/No publicada como resultado/)).toBeTruthy();
  const region = within(screen.getByRole('region', {name: 'Detalle de llamada'}));
  await userEvent.click(region.getByRole('button', {name: 'Página siguiente'}));
  expect(await region.findByText('No hay respuestas registradas.')).toBeTruthy();
  expect(server.reads).toContain('/api/v1/runs/run/calls/child?cursor=next-receipt');
});
