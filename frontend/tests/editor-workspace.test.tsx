import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  editorApi,
  missingModel,
  renderEditor,
  saved,
  settled,
  toolbarStatus,
} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {copy, j1} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});
const panel = (): HTMLElement => screen.getByRole('complementary', {name: 'Selected node'});
const button = (name: string): HTMLButtonElement =>
  screen.getByRole<HTMLButtonElement>('button', {name});

it('opens the latest version with the palette, platform components first', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  expect(screen.getByRole('heading', {name: 'Funny story', level: 1})).toBeTruthy();
  const palette = screen.getByRole('navigation', {name: 'Components'});
  expect(
    within(palette)
      .getAllByRole('button')
      .map((item) => item.getAttribute('aria-label')),
  ).toEqual(['Add Trigger', 'Add Output', 'Add LLM Call', 'Add Router']);
  await settled();
  expect(toolbarStatus()).toBe('Saved');
  expect(screen.queryByRole('button', {name: 'Save'})).toBeNull();
  expect(button('Run').disabled).toBe(false);
  expect(screen.queryByRole('button', {name: /^Activate/u})).toBeNull();
  expect(screen.getByText('No problems')).toBeTruthy();
});

it('adds a selected node, renames it on Enter and saves a new version', async () => {
  const {api} = await renderEditor(editorApi('funny-story', j1), 'funny-story');
  await userEvent.click(button('Add LLM Call'));
  expect(within(panel()).getByRole('heading', {name: 'LLM Call'})).toBeTruthy();
  const name = within(panel()).getByRole('textbox', {name: 'Node name'});
  await userEvent.clear(name);
  await userEvent.type(name, 'Writer{Enter}');
  expect(screen.getByRole('group', {name: 'Writer'})).toBeTruthy();
  await saved();
  expect(toolbarStatus()).toBe('Saved · 1 change since v1');
  const stored = api.last('POST /graphs/funny-story/changes')?.body as {document: typeof j1};
  expect(stored.document.nodes.at(-1)?.name).toBe('Writer');
  expect(api.count('POST /graphs/funny-story/changes')).toBe(1);
});

it('keeps the name when the field is emptied and commits when focus leaves', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  fireEvent.click(screen.getByRole('group', {name: 'Proposer'}));
  const name = within(panel()).getByRole('textbox', {name: 'Node name'});
  await userEvent.clear(name);
  fireEvent.blur(name);
  expect((name as HTMLInputElement).value).toBe('Proposer');
  await userEvent.type(name, ' 2');
  fireEvent.blur(name);
  expect(screen.getByRole('group', {name: 'Proposer 2'})).toBeTruthy();
});

it('connects and disconnects ports from the side panel', async () => {
  const document = copy(j1);
  document.connections = [];
  await renderEditor(editorApi('funny-story', document), 'funny-story');
  fireEvent.click(screen.getByRole('group', {name: 'Story'}));
  const combo = within(panel()).getByRole('combobox', {name: 'Connect out to'});
  expect(
    within(combo)
      .getAllByRole('option')
      .map((option) => option.textContent),
  ).toEqual(['Connect out to…', 'Proposer · in', 'Funny story · in']);
  await userEvent.selectOptions(combo, 'Proposer · in');
  const remove = within(panel()).getByRole('button', {name: 'Remove connection to Proposer · in'});
  expect(within(combo).queryByRole('option', {name: 'Proposer · in'})).toBeNull();
  await userEvent.click(remove);
  expect(
    within(panel()).queryByRole('button', {name: 'Remove connection to Proposer · in'}),
  ).toBeNull();
});

it('lists every problem from the status bar, on the card and in the inspector', async () => {
  const document = copy(j1);
  const proposer = document.nodes[1];
  if (proposer !== undefined) proposer.config = {...proposer.config, model: null};
  await renderEditor(editorApi('funny-story', document, missingModel), 'funny-story');
  await userEvent.click(await screen.findByRole('button', {name: '1 problem'}));
  const problems = screen.getByRole('list', {name: 'Problems'});
  expect(within(problems).getByText('Select a model.')).toBeTruthy();
  await userEvent.click(within(problems).getByRole('button'));
  expect(within(panel()).getByRole('heading', {name: 'Proposer'})).toBeTruthy();
  expect(
    within(screen.getByRole('group', {name: 'Proposer'})).getByText('Select a model.'),
  ).toBeTruthy();
  expect(within(panel()).getByRole('list', {name: 'Problems with this node'}).textContent).toBe(
    'Select a model.',
  );
  expect(within(panel()).getByRole('region', {name: 'Model'}).textContent).toContain('Not set');
});
