import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {act, cleanup, fireEvent, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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

async function rename(name: string): Promise<void> {
  const field = within(panel()).getByRole('textbox', {name: 'Node name'});
  await userEvent.clear(field);
  await userEvent.type(field, `${name}{Enter}`);
}

it('undoes and redoes edits, each saved as a new change', async () => {
  const {api} = await renderEditor(editorApi('funny-story', j1), 'funny-story');
  expect(button('Undo').disabled).toBe(true);
  fireEvent.click(screen.getByRole('group', {name: 'Story'}));
  await rename('Opening');
  await saved();
  await userEvent.click(button('Undo'));
  expect(screen.getByRole('group', {name: 'Story'})).toBeTruthy();
  await saved();
  const restored = api.last('POST /graphs/funny-story/changes')?.body as {document: typeof j1};
  expect(restored.document.nodes[0]?.name).toBe('Story');
  await userEvent.click(button('Redo'));
  expect(screen.getByRole('group', {name: 'Opening'})).toBeTruthy();
  fireEvent.keyDown(document.body, {key: 'z', ctrlKey: true});
  expect(screen.getByRole('group', {name: 'Story'})).toBeTruthy();
  fireEvent.keyDown(document.body, {key: 'z', metaKey: true, shiftKey: true});
  expect(screen.getByRole('group', {name: 'Opening'})).toBeTruthy();
  await saved();
  // Redo, undo and redo within the autosave delay are saved once, as their final state.
  expect(api.count('POST /graphs/funny-story/changes')).toBe(3);
});

it('reports a failed save, keeps the edit and saves it when asked again', async () => {
  const {api, draft} = await renderEditor(editorApi('funny-story', j1), 'funny-story');
  const route = 'POST /graphs/funny-story/changes';
  api.on(route, failure(503, 'unavailable', 'The server is busy.'));
  fireEvent.click(screen.getByRole('group', {name: 'Story'}));
  await rename('Opening');
  await waitFor(() => {
    expect(toolbarStatus()).toContain('Not saved: The server is busy.');
  });
  expect(draft().dirty).toBe(true);
  api.on(route, {status: 201, body: {change: 2, at: '2026-10-04T10:43:00.000Z'}});
  await userEvent.click(button('Try again'));
  await saved();
  expect(draft().dirty).toBe(false);
  expect(await act(async () => draft().save())).toBe('saved');
  draft().discard();
});

it('saves pending edits when the editor closes, and withdraws the draft model', async () => {
  const {api, onDraft} = await renderEditor(editorApi('funny-story', j1), 'funny-story');
  fireEvent.click(screen.getByRole('group', {name: 'Story'}));
  await rename('Opening');
  cleanup();
  await waitFor(() => {
    expect(api.count('POST /graphs/funny-story/changes')).toBe(1);
  });
  expect(onDraft).toHaveBeenLastCalledWith(null);
});
