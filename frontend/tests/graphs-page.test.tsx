import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {ApiError} from '../src/api/index.ts';
import {FakeApi, failure} from './support/fake-api.ts';
import {cells, newer, older, renderPage, serve} from './support/graphs-page.tsx';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
it('tables the graphs, most recently changed first, linked by name', async () => {
  serve([older, newer]);
  const {onNew} = renderPage();
  expect(screen.getByRole('heading', {name: 'Graphs'})).toBeTruthy();
  const table = await screen.findByRole('table', {name: 'Graphs'});
  const links = within(table)
    .getAllByRole('rowheader')
    .map((cell) => within(cell).getByRole('link'));
  expect(links.map((link) => [link.textContent, link.getAttribute('href')])).toEqual([
    ['Newer graph', '#/graphs/newer'],
    ['Older graph', '#/graphs/older'],
  ]);
  await userEvent.click(screen.getByRole('button', {name: 'New graph'}));
  expect(onNew).toHaveBeenCalledTimes(1);
});

it('shows the active version, branches, last change and last run of each graph', async () => {
  serve([newer, older]);
  renderPage();
  const table = await screen.findByRole('table', {name: 'Graphs'});
  const [header, first, second] = within(table).getAllByRole('row');
  expect(cells(header)).toEqual(['Graph', 'Active version', 'Branches', 'Last change', 'Last run']);
  await within(table).findAllByText('2');
  const changed = new Intl.DateTimeFormat('en', {dateStyle: 'medium', timeStyle: 'short'});
  expect(cells(first)).toEqual([
    'Newer graph',
    'v3',
    '2',
    `Change 27 · ${changed.format(new Date(newer.updated_at))}`,
    'Failed: time limit reached',
  ]);
  expect(cells(second).slice(1, 3)).toEqual(['None', '1']);
  expect(cells(second)[4]).toBe('No runs');
  const run = within(table).getByRole('link', {name: 'Failed: time limit reached'});
  expect(run.getAttribute('href')).toBe('#/graphs/newer/runs/r9');
});

it('explains how to start when there are no graphs', async () => {
  serve([]);
  renderPage();
  expect(await screen.findByText(/No graphs yet/u)).toBeTruthy();
});

it('reports a list that cannot be read and tries again', async () => {
  const api = new FakeApi().on('GET /graphs', failure(503, 'unavailable', 'Later.')).install();
  renderPage();
  expect((await screen.findByRole('alert')).textContent).toContain(
    'Could not load the graphs. Later.',
  );
  api.on('GET /graphs', {status: 200, body: {graphs: [older]}});
  await userEvent.click(screen.getByRole('button', {name: 'Try again'}));
  expect(await screen.findByRole('link', {name: 'Older graph'})).toBeTruthy();
});

it('asks for a name, creates the graph with a slug identifier and reports a refusal', async () => {
  serve([]);
  const {onCreate, onCancelNew} = renderPage(true);
  const dialog = screen.getByRole('dialog', {name: 'New graph'});
  await userEvent.click(within(dialog).getByRole('button', {name: 'Create'}));
  expect(within(dialog).getByRole('alert').textContent).toBe(
    'Enter a name of 1 to 120 characters.',
  );
  await userEvent.type(within(dialog).getByRole('textbox', {name: 'Name'}), '  Funny story ');
  await userEvent.click(within(dialog).getByRole('button', {name: 'Create'}));
  const created = vi.mocked(onCreate).mock.calls[0]?.[0];
  expect(created?.name).toBe('Funny story');
  expect(created?.id).toMatch(/^funny-story-[0-9a-f]{4}$/u);
  vi.mocked(onCreate).mockRejectedValueOnce(new ApiError(409, 'graph_exists', 'Taken.'));
  await userEvent.click(within(dialog).getByRole('button', {name: 'Create'}));
  expect(within(dialog).getByRole('alert').textContent).toBe(
    'The graph could not be created. Taken.',
  );
  await userEvent.click(within(dialog).getByRole('button', {name: 'Cancel'}));
  expect(onCancelNew).toHaveBeenCalledTimes(1);
});
