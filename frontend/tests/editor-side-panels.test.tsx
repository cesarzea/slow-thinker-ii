import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {editorApi, renderEditor} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j1} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

const body = (): HTMLElement => {
  const found = document.querySelector<HTMLElement>('.editor-body');
  if (found === null) throw new Error('No editor body');
  return found;
};

/** A 1200 px editor body whose components panel is 232 px wide. */
function measure(): void {
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockImplementation(function (
    this: HTMLElement,
  ) {
    const width = this.classList.contains('editor-body') ? 1200 : 232;
    return {x: 0, y: 0, top: 0, left: 0, bottom: 800, right: width, width, height: 800} as DOMRect;
  });
  Object.assign(HTMLElement.prototype, {setPointerCapture: vi.fn()});
}

it('collapses either side panel with the same control and opens it from anywhere on its rail', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  await userEvent.click(screen.getByRole('button', {name: 'Hide panel'}));
  expect(body().dataset['right']).toBe('collapsed');
  expect(localStorage.getItem('slow-thinker-ii.right-panel-collapsed')).toBe('true');
  fireEvent.click(screen.getByRole('complementary', {name: 'Panel'}));
  expect(body().dataset['right']).toBe('open');
  await userEvent.click(screen.getByRole('button', {name: 'Hide components'}));
  expect(body().dataset['left']).toBe('collapsed');
  fireEvent.click(screen.getByRole('navigation', {name: 'Components'}));
  expect(body().dataset['left']).toBe('open');
  expect(screen.getByRole('searchbox', {name: 'Search components'})).toBeTruthy();
});

it('resizes the right panel by dragging its edge, up to covering the canvas', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  measure();
  const edge = screen.getByRole('separator', {name: 'Resize the panel'});
  fireEvent.pointerDown(edge, {pointerId: 1, clientX: 880});
  fireEvent.pointerMove(edge, {pointerId: 1, clientX: 700});
  expect(body().style.getPropertyValue('--right')).toBe('500px');
  fireEvent.pointerMove(edge, {pointerId: 1, clientX: 1150});
  expect(body().style.getPropertyValue('--right')).toBe('260px');
  fireEvent.pointerUp(edge, {pointerId: 1});
  fireEvent.pointerMove(edge, {pointerId: 1, clientX: 100});
  expect(body().style.getPropertyValue('--right')).toBe('260px');
  expect(localStorage.getItem('slow-thinker-ii.right-panel-width')).toBe('260');
  fireEvent.doubleClick(edge);
  expect(body().style.getPropertyValue('--right')).toBe('968px');
  fireEvent.doubleClick(edge);
  expect(body().style.getPropertyValue('--right')).toBe('320px');
  cleanup();
  localStorage.setItem('slow-thinker-ii.right-panel-width', '480');
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  expect(body().style.getPropertyValue('--right')).toBe('480px');
});

it('arranges, undoes and restyles the graph shown in run mode without saving it', async () => {
  const api = editorApi('funny-story', j1);
  await renderEditor(api, 'funny-story');
  const saved = api.count('POST /graphs/funny-story/changes');
  await userEvent.click(screen.getByRole('button', {name: 'Run'}));
  const tools = screen.getByRole('group', {name: 'Canvas tools'});
  const undo = within(tools).getByRole<HTMLButtonElement>('button', {name: /^Undo/u});
  expect(undo.disabled).toBe(true);
  await userEvent.click(within(tools).getByRole('button', {name: 'Arrange the graph'}));
  await waitFor(() => {
    expect(undo.disabled).toBe(false);
  });
  await userEvent.click(undo);
  const redo = within(tools).getByRole<HTMLButtonElement>('button', {name: /^Redo/u});
  expect(redo.disabled).toBe(false);
  await userEvent.click(redo);
  expect(redo.disabled).toBe(true);
  await userEvent.click(within(tools).getByRole('button', {name: 'Connection style'}));
  await userEvent.click(screen.getByRole('menuitemradio', {name: 'Simple curve connections'}));
  await userEvent.click(within(tools).getByRole('button', {name: 'Outline'}));
  expect(screen.getByRole('list', {name: 'Outline'})).toBeTruthy();
  expect(screen.queryByRole('button', {name: /^Delete /u})).toBeNull();
  expect(api.count('POST /graphs/funny-story/changes')).toBe(saved);
});
