import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {GraphDocument} from '../src/api/index.ts';
import {renderEditor, saved} from './support/editor-harness.tsx';
import {graphServer} from './support/graph-server.ts';
import {j3} from './support/contract.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const GRAPH = 'funny-story-with-review';
const moved: GraphDocument = {...j3, layout: {...j3.layout, proposer: [500, 500]}};
type Api = Awaited<ReturnType<typeof renderEditor>>['api'];
const stored = (api: Api): GraphDocument | undefined =>
  (api.last(`POST /graphs/${GRAPH}/changes`)?.body as {document: GraphDocument} | undefined)
    ?.document;
const notice = (): string => document.querySelector('.status-notice')?.textContent ?? '';
const button = (name: string): HTMLButtonElement =>
  screen.getByRole<HTMLButtonElement>('button', {name: new RegExp(`^${name}$`, 'u')});

/** The review graph stored as two changes: as given, then with the Proposer moved. */
async function reloaded(): Promise<Api> {
  const server = graphServer(GRAPH, j3);
  server.state.changes.push(moved);
  const {api} = await renderEditor(server.api.install(), GRAPH);
  await waitFor(() => {
    expect(button('Undo').disabled).toBe(false);
  });
  return api;
}

it('undoes the branch’s saved changes after a reload, as new changes, and redoes them', async () => {
  const api = await reloaded();
  expect(button('Undo').title).toMatch(/^Undo \((⌘Z|Ctrl\+Z)\)$/u);
  expect(button('Redo').disabled).toBe(true);
  await userEvent.click(button('Undo'));
  await saved();
  expect(stored(api)?.layout?.['proposer']).toEqual(j3.layout?.['proposer']);
  expect(notice()).toBe('Undone: Moved Proposer');
  expect(button('Undo').disabled).toBe(true);
  await userEvent.click(button('Redo'));
  await saved();
  expect(stored(api)?.layout?.['proposer']).toEqual([500, 500]);
  expect(notice()).toBe('Redone: Moved Proposer');
  expect(api.count(`POST /graphs/${GRAPH}/changes`)).toBe(2);
});

it('deletes the selected node with Delete, says so, and undoes it from the status bar', async () => {
  const api = await reloaded();
  fireEvent.click(screen.getByRole('group', {name: 'Reviewer'}));
  fireEvent.keyDown(document.body, {key: 'Delete'});
  await saved();
  expect(stored(api)?.nodes.map((node) => node.id)).toEqual(['story', 'proposer', 'result']);
  expect(stored(api)?.connections).toEqual([{from: 'story.out', to: 'proposer.in'}]);
  expect(notice()).toBe('Deleted Reviewer · Undo');
  expect(button('Redo').disabled).toBe(true);
  await userEvent.click(screen.getByRole('button', {name: 'Undo: Deleted Reviewer'}));
  await saved();
  expect(stored(api)?.nodes).toHaveLength(4);
  expect(stored(api)?.connections).toHaveLength(4);
});

it('never deletes a node while typing in a field, and deletes it with the trash button', async () => {
  const api = await reloaded();
  fireEvent.click(screen.getByRole('group', {name: 'Reviewer'}));
  const panel = screen.getByRole('complementary', {name: 'Selected node'});
  const name = within(panel).getByRole('textbox', {name: 'Node name'});
  fireEvent.keyDown(name, {key: 'Backspace'});
  expect(screen.getByRole('group', {name: 'Reviewer'})).toBeTruthy();
  await userEvent.click(within(panel).getByRole('button', {name: 'Delete node'}));
  await saved();
  expect(stored(api)?.nodes.map((node) => node.id)).not.toContain('reviewer');
  expect(notice()).toBe('Deleted Reviewer · Undo');
});
