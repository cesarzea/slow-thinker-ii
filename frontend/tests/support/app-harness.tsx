import {render, screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {App} from '../../src/app/app.tsx';
import type {GraphDocument} from '../../src/api/index.ts';
import {FakeApi} from './fake-api.ts';
import {catalogBody} from './contract.ts';
import {runDetail, runSummary, usageBody, versionBody} from './runs.ts';

export const TOKEN = 'operator-token-for-tests';

const AT = '2026-10-04T05:00:00.000Z';

const MAIN = {
  name: 'main',
  created_at: AT,
  from_version: null,
  from_change: null,
  latest_change: 1,
  head_version: 1,
};

/** Graph routes for one graph: branch main, change 1 activated as version 1. */
function graphRoutes(api: FakeApi, saved: GraphDocument): FakeApi {
  const path = `/graphs/${saved.id}`;
  const version = {version: 1, branch: 'main', parent: null, change: 1, name: saved.name};
  const change = {change: 1, branch: 'main', at: AT, name: saved.name, version: 1};
  const detail = {id: saved.id, name: saved.name, active_version: 1, latest_change: 1};
  const versions = [{...version, created_at: AT}];
  return api
    .on(`GET ${path}`, {status: 200, body: {...detail, branches: [MAIN], versions}})
    .on(`GET ${path}/branches`, {status: 200, body: {branches: [MAIN]}})
    .on(`GET ${path}/changes`, {status: 200, body: {changes: [change]}})
    .on(`GET ${path}/changes/1`, {
      status: 200,
      body: {graph_id: saved.id, change: 1, branch: 'main', at: AT, document: saved, version: 1},
    })
    .on(`GET ${path}/versions/1`, {status: 200, body: versionBody(saved)})
    .on(`POST ${path}/changes`, {status: 201, body: {change: 2, at: AT}})
    .on(`POST ${path}/versions`, {status: 201, body: {version: 2, branch: 'main', change: 2}});
}

/** A fake operator API with one saved graph, its runs and the day's usage. */
export function appApi(saved: GraphDocument): FakeApi {
  const summary = {
    id: saved.id,
    name: saved.name,
    active_version: 1,
    latest_change: 1,
    updated_at: AT,
  };
  const run = {graph_id: saved.id, run_id: 'run-1'};
  const api = new FakeApi()
    .on('GET /access', {status: 200, body: {authentication: 'token'}})
    .on('GET /catalog', {status: 200, body: catalogBody})
    .on('GET /usage', {status: 200, body: usageBody})
    .on('GET /graphs', {status: 200, body: {graphs: [summary]}})
    .on('POST /graphs', {status: 201, body: {id: saved.id, branch: 'main', change: 1}})
    .on('POST /graphs/validate', {status: 200, body: {diagnostics: []}})
    .on('POST /runs', {status: 202, body: {run_id: 'run-1'}})
    .on('GET /runs', {status: 200, body: {runs: [runSummary(run)]}})
    .on('GET /runs/run-1', {status: 200, body: runDetail(run)})
    .on('GET /runs/run-1/events', {status: 200, body: {events: [], last_seq: 0, finished: true}});
  return graphRoutes(api, saved).install();
}

/** Open the application at a hash, without a token kept for the tab, and connect with it. */
export async function connectApp(hash = '#/graphs'): Promise<void> {
  sessionStorage.clear();
  window.history.replaceState(null, '', hash);
  render(
    <div style={{width: '1200px', height: '800px'}}>
      <App />
    </div>,
  );
  await userEvent.type(await screen.findByLabelText('Operator token'), TOKEN);
  await userEvent.click(screen.getByRole('button', {name: 'Connect'}));
}
