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
it('opens external evidence visibly and repeats focus without overriding internal navigation', async () => {
  const view = render(
    <Inspector credential="key" run="run" selection={{kind: 'activation', id: 'activation'}} />,
  );
  const heading = await screen.findByRole('heading', {name: 'Activación activation'});
  expect(document.activeElement).toBe(heading);
  await userEvent.click(await screen.findByRole('button', {name: 'Ver entrada efectiva'}));
  expect(document.activeElement).toBe(screen.getByRole('heading', {name: 'Contenido conservado'}));
  view.rerender(
    <Inspector credential="key" run="run" selection={{kind: 'activation', id: 'activation'}} />,
  );
  expect(document.activeElement).toBe(heading);
  expect(screen.queryByRole('region', {name: 'Contenido conservado'})).toBeNull();
  view.rerender(
    <Inspector credential="key" run="run" selection={{kind: 'payload', id: 'direct'}} />,
  );
  expect(await screen.findByText(/direct · Estado/)).toBeTruthy();
});
it('labels reported information, source timestamps and unavailable payloads without inventing reasoning', async () => {
  server.call.reports = [
    {
      event_sequence: 8,
      kind: 'reasoning',
      schema_version: '1',
      evidence: 'reported',
      payload_id: 'report',
      source_occurred_at: 20,
    },
    {
      event_sequence: 9,
      kind: 'diagnostic',
      schema_version: '1',
      evidence: 'reported',
      payload_id: null,
      source_occurred_at: null,
    },
  ];
  render(<Inspector credential="key" run="run" selection={{kind: 'call', id: 'child'}} />);
  expect(await screen.findByText(/reasoning · Declarado/)).toBeTruthy();
  expect(screen.getByText(/Marca temporal de origen: 20/)).toBeTruthy();
  expect(screen.getByText('Contenido del informe no disponible.')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Abrir informe'}));
  expect(await screen.findByText(/report · Estado/)).toBeTruthy();
});
it('makes absent reasoning explicit for both calls and activations', async () => {
  const view = render(
    <Inspector credential="key" run="run" selection={{kind: 'call', id: 'child'}} />,
  );
  expect(await screen.findByText(/Razonamiento no disponible/)).toBeTruthy();
  view.rerender(
    <Inspector credential="key" run="run" selection={{kind: 'activation', id: 'activation'}} />,
  );
  const region = within(await screen.findByRole('region', {name: 'Detalle de activación'}));
  expect(await region.findByText(/Razonamiento no disponible/)).toBeTruthy();
});
