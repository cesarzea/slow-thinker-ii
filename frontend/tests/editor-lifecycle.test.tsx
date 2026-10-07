import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {act, cleanup, fireEvent, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {newGraphDocument} from '../src/features/editor/index.ts';
import {editorApi, renderEditor, saved, toolbarStatus} from './support/editor-harness.tsx';
import {failure} from './support/fake-api.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j1} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
const button = (name: string): HTMLButtonElement =>
  screen.getByRole<HTMLButtonElement>('button', {name});
const panel = (): HTMLElement => screen.getByRole('complementary', {name: 'Selected node'});

it('enters run mode with the observation points and leaves it without running', async () => {
  const {api} = await renderEditor(editorApi('funny-story', j1), 'funny-story');
  await userEvent.click(button('Run'));
  const points = screen.getByRole('navigation', {name: 'Observation points'});
  expect(within(points).getByRole('checkbox', {name: 'Observe Story → Proposer'})).toBeTruthy();
  expect(screen.queryByRole('navigation', {name: 'Components'})).toBeNull();
  expect(api.count('POST /runs')).toBe(0);
  await userEvent.click(button('Edit'));
  expect(screen.getByRole('navigation', {name: 'Components'})).toBeTruthy();
});

it('deletes the selected node from its menu and lists the graph in the outline', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  fireEvent.click(screen.getByRole('group', {name: 'Proposer'}));
  await userEvent.click(within(panel()).getByRole('button', {name: 'More actions for Proposer'}));
  await userEvent.click(screen.getByRole('menuitem', {name: 'Delete node'}));
  expect(screen.queryByRole('group', {name: 'Proposer'})).toBeNull();
  await userEvent.click(button('Outline'));
  const outline = screen.getByRole('list', {name: 'Outline'});
  expect(within(outline).getAllByRole('listitem')).toHaveLength(2);
  await userEvent.click(within(outline).getByRole('button', {name: /^Funny story/u}));
  expect(within(panel()).getByRole('heading', {name: 'Funny story'})).toBeTruthy();
  expect(button('Zoom in').disabled).toBe(true);
});

it('stores a new graph at once, saves each edit and activates the first version', async () => {
  const created = newGraphDocument('new-one-ab12', 'New one');
  const {api} = await renderEditor(editorApi('new-one-ab12', null), 'new-one-ab12', created);
  expect(screen.getByRole('complementary', {name: 'Graph'})).toBeTruthy();
  await saved();
  expect(api.count('POST /graphs')).toBe(1);
  await userEvent.click(button('Add Trigger'));
  await saved();
  expect(api.count('POST /graphs/new-one-ab12/changes')).toBe(1);
  expect(toolbarStatus()).toBe('Saved · not activated yet');
  await waitFor(() => {
    expect(button('Activate as v1').disabled).toBe(false);
  });
  await userEvent.click(button('Activate as v1'));
  expect(await screen.findByText('v1 · Active')).toBeTruthy();
  expect(api.last('POST /graphs/new-one-ab12/versions')?.body).toEqual({change: 2});
  expect(screen.queryByRole('button', {name: /^Activate/u})).toBeNull();
});

it('reports a graph that cannot be opened and tries again', async () => {
  const api = editorApi('gone', null);
  await act(async () => {
    await renderEditor(api, 'gone').catch(() => undefined);
  });
  expect(screen.getByRole('alert').textContent).toContain('This graph does not exist.');
  api.on('GET /graphs/gone', failure(503, 'unavailable', 'Later.'));
  await userEvent.click(button('Try again'));
  await waitFor(() => {
    expect(screen.getByRole('alert').textContent).toContain('Later.');
  });
});

it('offers to check again when validation cannot be reached', async () => {
  const api = editorApi('funny-story', j1);
  api.on('POST /graphs/validate', failure(503, 'unavailable', 'Validation is unavailable.'));
  await renderEditor(api, 'funny-story');
  expect(
    await screen.findByText(/Could not check the graph: Validation is unavailable\./u),
  ).toBeTruthy();
  api.on('POST /graphs/validate', {status: 200, body: {diagnostics: []}});
  await userEvent.click(button('Check again'));
  expect(await screen.findByText('No problems')).toBeTruthy();
});
