import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {App} from '../src/app/app.tsx';
import {OperatorServer} from './support/operator-server.ts';

const examples = [
  {
    graph_id: 'single',
    revision: '1',
    participants: 1,
    nodes: [{id: 'draft', component: 'proposer'}],
  },
  {
    graph_id: 'review',
    revision: '1',
    participants: 2,
    nodes: [
      {id: 'draft', component: 'proposer'},
      {id: 'review', component: 'reviewer'},
      {id: 'revise', component: 'proposer'},
    ],
  },
];

beforeEach(() => {
  vi.stubGlobal(
    'ResizeObserver',
    class {
      observe(): void {
        /* Layout is verified in browser journeys. */
      }
      unobserve(): void {
        /* No native observer exists in jsdom. */
      }
      disconnect(): void {
        /* No native observer exists in jsdom. */
      }
    },
  );
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it('ignores a failed request after the view unmounts', async () => {
  const reply = Promise.withResolvers<Response>();
  vi.stubGlobal('fetch', vi.fn().mockReturnValue(reply.promise));
  const view = render(<App />);
  view.unmount();
  reply.reject(new Error('aborted'));
  await expect(reply.promise).rejects.toThrow('aborted');
  expect(screen.queryByRole('alert')).toBeNull();
});

it('selects a graph while retaining repeated participant identities', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(examples))));
  render(<App />);
  await userEvent.selectOptions(await screen.findByLabelText('Experimento'), 'review');
  const ordered = within(screen.getByRole('list', {name: 'Orden de ejecución'}));
  expect(ordered.getAllByRole('listitem').map((item) => item.textContent)).toEqual([
    'draft: proposer',
    'review: reviewer',
    'revise: proposer',
  ]);
  expect(screen.getByText(/2 agentes · 3 activaciones/)).toBeTruthy();
});

it('exposes a catalogue failure without inventing an experiment', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
  render(<App />);
  expect((await screen.findByRole('alert')).textContent).toContain('No se pudo cargar');
  expect(screen.queryByRole('combobox')).toBeNull();
});

it('ignores a result after the view unmounts', async () => {
  const reply = Promise.withResolvers<Response>();
  vi.stubGlobal('fetch', vi.fn().mockReturnValue(reply.promise));
  const view = render(<App />);
  expect(screen.getByRole('status').textContent).toContain('Cargando');
  view.unmount();
  reply.resolve(new Response(JSON.stringify(examples)));
  await reply.promise;
  expect(screen.queryByRole('combobox')).toBeNull();
});

it('connects and disconnects without storing the operator credential', async () => {
  localStorage.clear();
  vi.stubGlobal('fetch', new OperatorServer().fetch);
  render(<App />);
  await userEvent.type(screen.getByLabelText('Clave de acceso'), 'private-operator-key');
  await userEvent.click(screen.getByRole('button', {name: 'Conectar para ejecutar'}));
  expect(await screen.findByRole('region', {name: 'Ejecución del experimento'})).toBeTruthy();
  expect(JSON.stringify(localStorage)).not.toContain('private-operator-key');
  await userEvent.click(screen.getByRole('button', {name: 'Desconectar acceso de operador'}));
  expect(screen.queryByRole('region', {name: 'Ejecución del experimento'})).toBeNull();
  expect(screen.getByLabelText<HTMLInputElement>('Clave de acceso').value).toBe('');
});
