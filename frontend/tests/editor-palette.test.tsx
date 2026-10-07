import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, within} from '@testing-library/react';
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
const DRAG = 'application/x-slow-thinker-component';

it('groups the components by origin and finds them by name or description', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  const palette = screen.getByRole('navigation', {name: 'Components'});
  const group = (name: string): HTMLElement => within(palette).getByRole('region', {name});
  expect(within(group('Platform')).getAllByRole('button')).toHaveLength(2);
  expect(within(group('Installed')).getAllByRole('button')).toHaveLength(2);
  const search = within(palette).getByRole('searchbox', {name: 'Search components'});
  await userEvent.type(search, 'llm');
  expect(
    within(palette)
      .getAllByRole('button', {name: /^Add /u})
      .map((item) => item.getAttribute('aria-label')),
  ).toEqual(['Add LLM Call']);
  expect(within(palette).queryByRole('region', {name: 'Platform'})).toBeNull();
  await userEvent.type(search, ' nothing like this');
  expect(within(palette).getByText(/No component matches/u)).toBeTruthy();
});

it('adds a component dragged from the palette where it is dropped', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  const item = screen.getByRole('button', {name: 'Add Router'});
  const data = new Map<string, string>();
  const transfer = {
    types: [DRAG],
    setData: (type: string, value: string) => data.set(type, value),
    getData: (type: string) => data.get(type) ?? '',
    effectAllowed: 'all',
    dropEffect: 'none',
  };
  fireEvent.dragStart(item, {dataTransfer: transfer});
  expect(data.get(DRAG)).toBe('router@1.0.0');
  const canvas = document.querySelector('.react-flow');
  if (canvas === null) throw new Error('No canvas');
  fireEvent.dragOver(canvas, {dataTransfer: transfer});
  expect(transfer.dropEffect).toBe('copy');
  fireEvent.drop(canvas, {dataTransfer: transfer, clientX: 400, clientY: 300});
  expect(await screen.findByRole('group', {name: 'Router'})).toBeTruthy();
  expect(screen.getByRole('complementary', {name: 'Selected node'})).toBeTruthy();
  fireEvent.drop(canvas, {dataTransfer: {...transfer, getData: () => ''}});
  expect(screen.getAllByRole('group', {name: /^Router/u})).toHaveLength(1);
});

it('collapses to a rail of tiles that expand it again, and remembers it in this browser', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  await userEvent.click(screen.getByRole('button', {name: 'Hide components'}));
  const rail = screen.getByRole('navigation', {name: 'Components'});
  expect(within(rail).queryByRole('searchbox')).toBeNull();
  const tiles = within(rail).getAllByRole('button', {name: /^Add /u});
  expect(tiles.map((tile) => tile.getAttribute('aria-label'))).toEqual([
    'Add Trigger',
    'Add Output',
    'Add LLM Call',
    'Add Router',
  ]);
  expect(tiles[1]?.getAttribute('title')).toMatch(/^Output: /u);
  expect(localStorage.getItem('slow-thinker-ii.left-panel-collapsed')).toBe('true');
  await userEvent.click(within(rail).getByRole('button', {name: 'Add Output'}));
  expect(screen.queryByRole('group', {name: 'Output'})).toBeNull();
  expect(screen.getByRole('searchbox', {name: 'Search components'})).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Hide components'}));
  cleanup();
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  await userEvent.click(screen.getByRole('button', {name: 'Show components'}));
  expect(screen.getByRole('searchbox', {name: 'Search components'})).toBeTruthy();
  expect(localStorage.getItem('slow-thinker-ii.left-panel-collapsed')).toBe('false');
});

it('keeps the palette open when this browser cannot store the choice', async () => {
  vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
    throw new Error('Storage is not available.');
  });
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
    throw new Error('Storage is not available.');
  });
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  await userEvent.click(screen.getByRole('button', {name: 'Hide components'}));
  expect(screen.getByRole('button', {name: 'Show components'})).toBeTruthy();
});
