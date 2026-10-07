import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {App} from '../src/app/app.tsx';
import {TOKEN, appApi, connectApp} from './support/app-harness.tsx';
import {failure} from './support/fake-api.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j1} from './support/contract.ts';

beforeEach(installFlowEnvironment);

function spending(banner: HTMLElement): string[] {
  return Array.from(banner.querySelectorAll('.usage > span'), (span) => span.textContent);
}
afterEach(() => {
  cleanup();
  localStorage.clear();
  sessionStorage.clear();
  vi.unstubAllGlobals();
});

it('asks for the operator token before showing the product', async () => {
  const api = appApi(j1);
  window.history.replaceState(null, '', '#/nowhere');
  render(<App />);
  expect(screen.getByText('Connecting…')).toBeTruthy();
  const connect = await screen.findByRole<HTMLButtonElement>('button', {name: 'Connect'});
  expect(connect.disabled).toBe(true);
  await userEvent.type(screen.getByLabelText('Operator token'), TOKEN);
  await userEvent.click(screen.getByRole('button', {name: 'Connect'}));
  expect(await screen.findByRole('heading', {name: 'Graphs'})).toBeTruthy();
  expect(window.location.hash).toBe('#/graphs');
  expect(api.last('GET /graphs')?.init.headers).toMatchObject({authorization: `Bearer ${TOKEN}`});
});

it('shows the product name, navigation, the day and month spending and Disconnect', async () => {
  appApi(j1);
  await connectApp();
  const banner = screen.getByRole('banner');
  expect(within(banner).getByText('Slow Thinker II')).toBeTruthy();
  const links = within(within(banner).getByRole('navigation', {name: 'Main'})).getAllByRole('link');
  expect(links.map((link) => [link.textContent, link.getAttribute('href')])).toEqual([
    ['Graphs', '#/graphs'],
    ['Runs', '#/runs'],
    ['Components', '#/components'],
  ]);
  await waitFor(() => {
    expect(spending(banner)).toEqual(['Today <$0.001 of $1.00', 'This month $0.500 of $20.00']);
  });
  await userEvent.click(within(banner).getByRole('button', {name: 'Disconnect'}));
  expect(screen.getByLabelText('Operator token')).toBeTruthy();
});

it('moves between the sections and marks the current one', async () => {
  appApi(j1);
  await connectApp('#/runs');
  const navigation = within(screen.getByRole('banner')).getByRole('navigation', {name: 'Main'});
  const current = (): string[] =>
    within(navigation)
      .getAllByRole('link')
      .filter((link) => link.getAttribute('aria-current') === 'page')
      .map((link) => link.textContent);
  expect(await screen.findByRole('heading', {name: 'Runs', level: 1})).toBeTruthy();
  expect(current()).toEqual(['Runs']);
  await userEvent.click(within(navigation).getByRole('link', {name: 'Components'}));
  expect(await screen.findByRole('heading', {name: 'Components', level: 1})).toBeTruthy();
  expect(window.location.hash).toBe('#/components');
  expect(current()).toEqual(['Components']);
  await userEvent.click(within(navigation).getByRole('link', {name: 'Graphs'}));
  expect(await screen.findByRole('heading', {name: 'Graphs'})).toBeTruthy();
  expect(current()).toEqual(['Graphs']);
});

it('says when spending cannot be read', async () => {
  appApi(j1).on('GET /usage', failure(503, 'unavailable', 'Later.'));
  await connectApp();
  expect(await screen.findByText('Spending unavailable')).toBeTruthy();
});

it('returns to the access entry when the token is no longer accepted', async () => {
  appApi(j1).on('GET /graphs', failure(401, 'unauthorized', 'Token required.'));
  await connectApp();
  expect((await screen.findByRole('alert')).textContent).toBe(
    'The operator token is no longer accepted. Connect again to continue.',
  );
  expect(screen.getByLabelText('Operator token')).toBeTruthy();
});

it('creates a graph on the server from the list and opens it', async () => {
  const api = appApi(j1);
  vi.spyOn(crypto, 'getRandomValues').mockImplementation((array) => array);
  await connectApp();
  await userEvent.click(await screen.findByRole('button', {name: 'New graph'}));
  expect(window.location.hash).toBe('#/graphs/new');
  const dialog = screen.getByRole('dialog', {name: 'New graph'});
  await userEvent.click(within(dialog).getByRole('button', {name: 'Cancel'}));
  expect(window.location.hash).toBe('#/graphs');
  await userEvent.click(screen.getByRole('button', {name: 'New graph'}));
  await userEvent.type(screen.getByRole('textbox', {name: 'Name'}), 'Plan A');
  await userEvent.click(screen.getByRole('button', {name: 'Create'}));
  await waitFor(() => {
    expect(window.location.hash).toBe('#/graphs/plan-a-0000');
  });
  expect(api.last('POST /graphs')?.body).toMatchObject({
    document: {id: 'plan-a-0000', name: 'Plan A'},
  });
});
