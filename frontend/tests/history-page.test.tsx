import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {OperatorClient} from '../src/api/index.ts';
import {RunsPage} from '../src/features/history/index.ts';
import {FakeApi, failure} from './support/fake-api.ts';
import type {Reply} from './support/fake-api.ts';
import {runSummary} from './support/runs.ts';

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});
const at = '2026-10-04T05:00:00.000Z';
const graph = (id: string, name: string): Record<string, unknown> => ({
  id,
  name,
  active_version: 1,
  latest_change: 1,
  updated_at: at,
});
const graphs = {graphs: [graph('story', 'Funny story'), graph('triage', 'Story triage')]};

function serve(runs: Reply | (() => Reply)): FakeApi {
  return new FakeApi()
    .on('GET /graphs', {status: 200, body: graphs})
    .on('GET /runs', runs)
    .install();
}

function renderPage(graphId: string | null = null): (graphId: string | null) => void {
  const onGraphChange = vi.fn();
  render(
    <RunsPage
      client={new OperatorClient('credential')}
      graphId={graphId}
      runHref={(id, run) => `#/graphs/${id}/runs/${run}`}
      onGraphChange={onGraphChange}
    />,
  );
  return onGraphChange;
}

const listed = [
  runSummary({run_id: 's2', graph_id: 'story', version: 2}),
  runSummary({run_id: 't1', graph_id: 'triage', status: 'failed', reason: 'activation_failed'}),
  runSummary({run_id: 's1', graph_id: 'story'}),
];

it('lists the runs of every graph newest first, each linked to its run', async () => {
  const api = serve({status: 200, body: {runs: listed}});
  renderPage();
  expect(screen.getByRole('heading', {name: 'Runs', level: 1})).toBeTruthy();
  const table = await screen.findByRole('table', {name: 'Runs'});
  const links = within(table)
    .getAllByRole('rowheader')
    .map((header) => within(header).getByRole('link'));
  expect(links.map((link) => [link.textContent, link.getAttribute('href')])).toEqual([
    ['Funny story · Run 2', '#/graphs/story/runs/s2'],
    ['Story triage · Run 1', '#/graphs/triage/runs/t1'],
    ['Funny story · Run 1', '#/graphs/story/runs/s1'],
  ]);
  expect(api.last('GET /runs')?.query.toString()).toBe('limit=100');
});

it('shows version, status, start, duration, LLM calls and cost of each run', async () => {
  serve({status: 200, body: {runs: listed}});
  renderPage();
  const table = await screen.findByRole('table', {name: 'Runs'});
  const headers = within(table).getAllByRole('columnheader');
  expect(headers.map((header) => header.textContent)).toEqual([
    ...['Run', 'Version', 'Status', 'Started', 'Duration', 'LLM calls', 'Cost'],
  ]);
  const local = new Intl.DateTimeFormat('en', {dateStyle: 'medium', timeStyle: 'medium'});
  const [, newest, failed] = within(table).getAllByRole('row');
  expect(Array.from(newest?.children ?? [], (cell) => cell.textContent)).toEqual([
    ...['Funny story · Run 2', 'v2', 'Completed', local.format(new Date(at)), '6.0 s', '4'],
    '$0.000083',
  ]);
  expect(failed?.children[2]?.textContent).toBe('Failed: an activation failed');
});

it('filters by graph through the Graph select', async () => {
  const api = serve({status: 200, body: {runs: [runSummary({graph_id: 'story'})]}});
  const onGraphChange = renderPage('story');
  expect(await screen.findByRole('heading', {name: 'Runs of Funny story'})).toBeTruthy();
  expect(api.last('GET /runs')?.query.get('graph_id')).toBe('story');
  const select = screen.getByRole<HTMLSelectElement>('combobox', {name: 'Graph'});
  expect(select.value).toBe('story');
  const options = within(select).getAllByRole('option');
  expect(options.map((option) => option.textContent)).toEqual([
    'All graphs',
    'Funny story',
    'Story triage',
  ]);
  await userEvent.selectOptions(select, 'Story triage');
  await userEvent.selectOptions(select, 'All graphs');
  expect(vi.mocked(onGraphChange).mock.calls).toEqual([['triage'], [null]]);
});

it('explains when there are no runs', async () => {
  serve({status: 200, body: {runs: []}});
  renderPage();
  expect(
    await screen.findByText('No runs yet. Open a graph and choose Run to start one.'),
  ).toBeTruthy();
  cleanup();
  renderPage('unknown');
  expect(await screen.findByText(/This graph has no runs yet/u)).toBeTruthy();
  expect(screen.getByRole('heading', {name: 'Runs of unknown'})).toBeTruthy();
  expect(screen.getByRole<HTMLSelectElement>('combobox', {name: 'Graph'}).value).toBe('unknown');
});

it('reports a read that fails and tries again', async () => {
  const api = serve(failure(503, 'unavailable', 'Later.'));
  renderPage();
  expect((await screen.findByRole('alert')).textContent).toContain(
    'Could not load the runs. Later.',
  );
  api.on('GET /runs', {status: 200, body: {runs: [runSummary({graph_id: 'story'})]}});
  await userEvent.click(screen.getByRole('button', {name: 'Try again'}));
  expect(await screen.findByRole('link', {name: 'Funny story · Run 1'})).toBeTruthy();
  expect(screen.queryByRole('alert')).toBeNull();
});
