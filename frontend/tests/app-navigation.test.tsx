import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {act, cleanup, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {appApi, connectApp} from './support/app-harness.tsx';
import {failure} from './support/fake-api.ts';
import type {FakeApi} from './support/fake-api.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j1} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});
const editorHash = '#/graphs/funny-story';

/** Opens the editor, makes its autosave fail and edits, so that leaving asks first. */
async function editWithFailedSave(api: FakeApi): Promise<void> {
  api.on('POST /graphs/funny-story/changes', failure(503, 'unavailable', 'Busy.'));
  await connectApp(editorHash);
  await userEvent.click(await screen.findByRole('button', {name: 'Add Output'}));
  await screen.findByText(/^Not saved: /u, undefined, {timeout: 3000});
}

function followHash(hash: string): void {
  act(() => {
    window.location.hash = hash;
  });
}

function mainLink(name: string): HTMLElement {
  return within(screen.getByRole('navigation', {name: 'Main'})).getByRole('link', {name});
}

it('asks before leaving a working copy whose save failed, and lets the person stay', async () => {
  await editWithFailedSave(appApi(j1));
  followHash('#/graphs');
  const guard = await screen.findByRole('dialog', {name: 'Unsaved changes'});
  expect(window.location.hash).toBe(editorHash);
  await userEvent.click(within(guard).getByRole('button', {name: 'Stay'}));
  expect(screen.getByRole('button', {name: 'Add Output'})).toBeTruthy();
  await userEvent.click(mainLink('Runs'));
  await userEvent.click(await screen.findByRole('button', {name: 'Discard'}));
  expect(await screen.findByRole('heading', {name: 'Runs', level: 1})).toBeTruthy();
  expect(window.location.hash).toBe('#/runs');
});

it('leaves a saved working copy without asking, from the main navigation or the editor', async () => {
  appApi(j1);
  await connectApp(editorHash);
  await screen.findByRole('button', {name: 'Add Output'});
  const runs = screen.getAllByRole('link', {name: 'Runs'}).map((link) => link.getAttribute('href'));
  expect(runs).toEqual(['#/runs', '#/graphs/funny-story/runs']);
  await userEvent.click(mainLink('Components'));
  expect(await screen.findByRole('heading', {name: 'Components', level: 1})).toBeTruthy();
  expect(screen.queryByRole('dialog')).toBeNull();
});

it('enters run mode without executing, executes what is on screen and keeps the run', async () => {
  const api = appApi(j1);
  await connectApp(editorHash);
  await userEvent.click(await screen.findByRole('button', {name: 'Run'}));
  expect(await screen.findByRole('navigation', {name: 'Observation points'})).toBeTruthy();
  expect(api.count('POST /runs')).toBe(0);
  const panel = screen.getByRole('complementary', {name: 'Run'});
  await userEvent.click(within(panel).getByRole('button', {name: 'Execute'}));
  expect(await within(panel).findByText('Completed')).toBeTruthy();
  expect(api.last('POST /runs')?.body).toEqual({
    graph_id: 'funny-story',
    change: 1,
    input: 'A cat tried to learn to fly.',
  });
  expect(window.location.hash).toBe('#/graphs/funny-story/runs/run-1');
  followHash('#/graphs/funny-story/runs/run-1/activity');
  expect(await screen.findByRole('heading', {name: 'Activity'})).toBeTruthy();
  followHash('#/graphs/funny-story/runs/run-1');
  expect(await screen.findByRole('navigation', {name: 'Observation points'})).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Edit'}));
  expect(window.location.hash).toBe(editorHash);
  expect(await screen.findByRole('navigation', {name: 'Components'})).toBeTruthy();
});

it('filters the runs by graph through the routes and opens a run in run mode', async () => {
  appApi(j1);
  await connectApp('#/runs');
  const select = await screen.findByRole('combobox', {name: 'Graph'});
  await screen.findByRole('option', {name: 'Funny story'});
  await userEvent.selectOptions(select, 'Funny story');
  expect(await screen.findByRole('heading', {name: 'Runs of Funny story'})).toBeTruthy();
  expect(window.location.hash).toBe('#/graphs/funny-story/runs');
  expect(screen.getByRole('combobox', {name: 'Graph'})).toBe(select);
  await userEvent.click(await screen.findByRole('link', {name: 'Funny story · Run 1'}));
  expect(await screen.findByRole('navigation', {name: 'Observation points'})).toBeTruthy();
  expect(window.location.hash).toBe('#/graphs/funny-story/runs/run-1');
});
