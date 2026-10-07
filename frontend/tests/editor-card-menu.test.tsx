import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {editorApi, renderEditor} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j3} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const GRAPH = 'funny-story-with-review';

it('moves through a card’s menu with the arrow keys and closes it with Escape', async () => {
  await renderEditor(editorApi(GRAPH, j3), GRAPH);
  fireEvent.contextMenu(screen.getByRole('group', {name: 'Reviewer'}));
  const menu = screen.getByRole('menu', {name: 'Actions for Reviewer'});
  const [edit, remove, router] = within(menu).getAllByRole('menuitem');
  expect(document.activeElement).toBe(edit);
  await userEvent.keyboard('{ArrowDown}');
  expect(document.activeElement).toBe(remove);
  await userEvent.keyboard('{ArrowUp}{ArrowUp}');
  expect(document.activeElement).toBe(router);
  await userEvent.keyboard('{Escape}');
  expect(screen.queryByRole('menu', {name: 'Actions for Reviewer'})).toBeNull();
});

it('closes a card’s menu when the focus leaves it', async () => {
  await renderEditor(editorApi(GRAPH, j3), GRAPH);
  fireEvent.contextMenu(screen.getByRole('group', {name: 'Story'}));
  const menu = screen.getByRole('menu', {name: 'Actions for Story'});
  fireEvent.blur(menu, {relatedTarget: document.body});
  expect(screen.queryByRole('menu', {name: 'Actions for Story'})).toBeNull();
});
