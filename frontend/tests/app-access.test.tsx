import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {App} from '../src/app/app.tsx';
import {TOKEN, appApi} from './support/app-harness.tsx';
import {failure} from './support/fake-api.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j1} from './support/contract.ts';

const KEPT = 'slow-thinker-ii.operator-token';
const refused = failure(401, 'unauthorized', 'Token required.');

beforeEach(() => {
  installFlowEnvironment();
  window.history.replaceState(null, '', '#/graphs');
});
afterEach(() => {
  cleanup();
  sessionStorage.clear();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

async function openGraphs(): Promise<HTMLElement> {
  render(<App />);
  await screen.findByRole('heading', {name: 'Graphs'});
  return screen.getByRole('banner');
}

async function connect(): Promise<void> {
  render(<App />);
  await userEvent.type(await screen.findByLabelText('Operator token'), TOKEN);
  await userEvent.click(screen.getByRole('button', {name: 'Connect'}));
  await screen.findByRole('heading', {name: 'Graphs'});
}

it('opens the product at once on a server without operator authentication', async () => {
  const api = appApi(j1).on('GET /access', {status: 200, body: {authentication: 'none'}});
  const banner = await openGraphs();
  expect(screen.queryByLabelText('Operator token')).toBeNull();
  expect(within(banner).queryByRole('button', {name: 'Disconnect'})).toBeNull();
  expect(api.last('GET /graphs')?.init.headers).not.toHaveProperty('authorization');
  api.on('GET /catalog', refused);
  await userEvent.click(within(banner).getByRole('link', {name: 'Components'}));
  expect(await screen.findByLabelText('Operator token')).toBeTruthy();
  expect(screen.getByRole('alert').textContent).toBe(
    'This server now asks for the operator token. Connect to continue.',
  );
});

it('asks for the token when the access mode cannot be read', async () => {
  appApi(j1).on('GET /access', failure(404, 'not_found', 'No route.'));
  render(<App />);
  expect(await screen.findByLabelText('Operator token')).toBeTruthy();
});

it('reconnects a reloaded tab with the kept token until Disconnect', async () => {
  const api = appApi(j1);
  await connect();
  cleanup();
  const banner = await openGraphs();
  expect(api.last('GET /graphs')?.init.headers).toMatchObject({authorization: `Bearer ${TOKEN}`});
  await userEvent.click(within(banner).getByRole('button', {name: 'Disconnect'}));
  expect(sessionStorage.getItem(KEPT)).toBeNull();
  cleanup();
  render(<App />);
  expect(await screen.findByLabelText('Operator token')).toBeTruthy();
});

it('forgets the kept token when it is no longer accepted', async () => {
  sessionStorage.setItem(KEPT, 'old-token');
  appApi(j1).on('GET /graphs', refused);
  render(<App />);
  expect(await screen.findByLabelText('Operator token')).toBeTruthy();
  expect(screen.getByRole('alert').textContent).toBe(
    'The operator token is no longer accepted. Connect again to continue.',
  );
  expect(sessionStorage.getItem(KEPT)).toBeNull();
});

it('asks again after a reload when the tab cannot keep the token', async () => {
  const denied = (): never => {
    throw new Error('Storage is not available.');
  };
  vi.spyOn(Storage.prototype, 'getItem').mockImplementation(denied);
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(denied);
  vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(denied);
  appApi(j1);
  await connect();
  await userEvent.click(screen.getByRole('button', {name: 'Disconnect'}));
  cleanup();
  render(<App />);
  expect(await screen.findByLabelText('Operator token')).toBeTruthy();
});
