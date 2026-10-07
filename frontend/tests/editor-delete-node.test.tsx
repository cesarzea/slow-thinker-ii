import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {GraphDocument} from '../src/api/index.ts';
import {editorApi, renderEditor, saved} from './support/editor-harness.tsx';
import {j3} from './support/contract.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const GRAPH = 'funny-story-with-review';
type Api = Awaited<ReturnType<typeof renderEditor>>['api'];
const nodes = (api: Api): string[] =>
  (
    api.last(`POST /graphs/${GRAPH}/changes`)?.body as {document: GraphDocument} | undefined
  )?.document.nodes.map((node) => node.id) ?? [];
const notice = (): string => document.querySelector('.status-notice')?.textContent ?? '';

it('deletes a selected card with the button on its corner', async () => {
  const {api} = await renderEditor(editorApi(GRAPH, j3), GRAPH);
  expect(screen.queryByRole('button', {name: 'Delete Reviewer'})).toBeNull();
  fireEvent.click(screen.getByRole('group', {name: 'Reviewer'}));
  await userEvent.click(screen.getByRole('button', {name: 'Delete Reviewer'}));
  await saved();
  expect(nodes(api)).toEqual(['story', 'proposer', 'result']);
  expect(notice()).toBe('Deleted Reviewer · Undo');
});

it('offers editing, deleting and removing the component from a card’s own menu', async () => {
  const {api} = await renderEditor(editorApi(GRAPH, j3), GRAPH);
  fireEvent.contextMenu(screen.getByRole('group', {name: 'Reviewer'}));
  const menu = screen.getByRole('menu', {name: 'Actions for Reviewer'});
  expect(
    within(menu)
      .getAllByRole('menuitem')
      .map((item) => item.textContent),
  ).toEqual(['Edit configuration', 'Delete', 'Remove Router']);
  await userEvent.click(within(menu).getByRole('menuitem', {name: 'Edit configuration'}));
  expect(screen.getByRole('dialog', {name: 'Reviewer'})).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Cancel'}));
  fireEvent.contextMenu(screen.getByRole('group', {name: 'Reviewer'}));
  await userEvent.click(screen.getByRole('menuitem', {name: 'Remove Router'}));
  expect(screen.getByRole('dialog', {name: 'Remove Router'})).toBeTruthy();
  await userEvent.keyboard('{Escape}');
  fireEvent.contextMenu(screen.getByRole('group', {name: 'Story'}));
  const story = screen.getByRole('menu', {name: 'Actions for Story'});
  expect(within(story).getAllByRole('menuitem')).toHaveLength(2);
  await userEvent.click(within(story).getByRole('menuitem', {name: 'Delete'}));
  await saved();
  expect(nodes(api)).toEqual(['proposer', 'reviewer', 'result']);
});

it('deletes a node from its entry in the outline', async () => {
  const {api} = await renderEditor(editorApi(GRAPH, j3), GRAPH);
  await userEvent.click(screen.getByRole('button', {name: 'Outline'}));
  const outline = screen.getByRole('list', {name: 'Outline'});
  await userEvent.click(within(outline).getByRole('button', {name: 'Delete Funny story'}));
  await saved();
  expect(nodes(api)).toEqual(['story', 'proposer', 'reviewer']);
  expect(notice()).toBe('Deleted Funny story · Undo');
});
