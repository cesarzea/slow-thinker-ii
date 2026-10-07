import {render} from '@testing-library/react';
import {vi} from 'vitest';
import {OperatorClient} from '../../src/api/index.ts';
import {GraphsPage} from '../../src/features/graphs/index.ts';
import type {GraphsPageProps} from '../../src/features/graphs/graphs-page.tsx';
import {FakeApi} from './fake-api.ts';
import {runSummary} from './runs.ts';

export const older = {
  id: 'older',
  name: 'Older graph',
  active_version: null,
  latest_change: 2,
  updated_at: '2026-10-01T05:00:00.000Z',
};
export const newer = {
  id: 'newer',
  name: 'Newer graph',
  active_version: 3,
  latest_change: 27,
  updated_at: '2026-10-03T05:00:00.000Z',
};
const main = {
  name: 'main',
  created_at: '2026-10-01T05:00:00.000Z',
  from_version: null,
  from_change: null,
  latest_change: 2,
  head_version: null,
};

export function serve(graphs: unknown[]): FakeApi {
  const runs = [
    runSummary({graph_id: 'newer', run_id: 'r9', status: 'failed', reason: 'time_limit'}),
  ];
  return new FakeApi()
    .on('GET /graphs', {status: 200, body: {graphs}})
    .on('GET /runs', {status: 200, body: {runs}})
    .on('GET /graphs/newer/branches', {
      status: 200,
      body: {branches: [main, {...main, name: 'draft'}]},
    })
    .on('GET /graphs/older/branches', {status: 200, body: {branches: [main]}})
    .install();
}

type Handlers = Pick<GraphsPageProps, 'onNew' | 'onCancelNew' | 'onCreate'>;

export function renderPage(creating = false): Handlers {
  const handlers = {
    onNew: vi.fn(),
    onCancelNew: vi.fn(),
    onCreate: vi.fn(async () => Promise.resolve()),
  };
  const hrefs = {
    graphHref: (id: string) => `#/graphs/${id}`,
    runHref: (id: string, run: string) => `#/graphs/${id}/runs/${run}`,
  };
  render(
    <GraphsPage
      client={new OperatorClient('credential')}
      creating={creating}
      {...hrefs}
      {...handlers}
    />,
  );
  return handlers;
}

export function cells(row: HTMLElement | undefined): string[] {
  return Array.from(row?.children ?? [], (cell) => cell.textContent);
}
