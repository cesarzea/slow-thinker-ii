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
  expect(await screen.findByText('1 agent · 1 declared node · 1')).toBeTruthy();
  await userEvent.selectOptions(
    await screen.findByLabelText('Experiment'),
    JSON.stringify(['review', '1']),
  );
  const ordered = within(screen.getByRole('list', {name: 'Experiment nodes'}));
  expect(ordered.getAllByRole('listitem').map((item) => item.textContent)).toEqual([
    'draft: proposer',
    'review: reviewer',
    'revise: proposer',
  ]);
  expect(screen.getByText(/2 agents · 3 declared nodes/)).toBeTruthy();
});

it('exposes a catalogue failure without inventing an experiment', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')));
  render(<App />);
  expect((await screen.findByRole('alert')).textContent).toContain('Could not load');
  expect(screen.queryByRole('combobox')).toBeNull();
});

it('ignores a result after the view unmounts', async () => {
  const reply = Promise.withResolvers<Response>();
  vi.stubGlobal('fetch', vi.fn().mockReturnValue(reply.promise));
  const view = render(<App />);
  expect(screen.getByRole('status').textContent).toContain('Loading');
  view.unmount();
  reply.resolve(new Response(JSON.stringify(examples)));
  await reply.promise;
  expect(screen.queryByRole('combobox')).toBeNull();
});

it('connects and disconnects without storing the operator credential', async () => {
  localStorage.clear();
  vi.stubGlobal('fetch', new OperatorServer().fetch);
  render(<App />);
  await userEvent.type(screen.getByLabelText('Access key'), 'private-operator-key');
  await userEvent.click(screen.getByRole('button', {name: 'Connect operator access'}));
  expect(await screen.findByRole('region', {name: 'Experiment execution'})).toBeTruthy();
  expect(JSON.stringify(localStorage)).not.toContain('private-operator-key');
  await userEvent.click(screen.getByRole('button', {name: 'Disconnect operator access'}));
  expect(screen.queryByRole('region', {name: 'Experiment execution'})).toBeNull();
  expect(screen.getByLabelText<HTMLInputElement>('Access key').value).toBe('');
});
