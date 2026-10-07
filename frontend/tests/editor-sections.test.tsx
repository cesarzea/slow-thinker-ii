import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {editorApi, renderEditor} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j2, j3} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});
const panel = (): HTMLElement => screen.getByRole('complementary', {name: 'Selected node'});
const SECTIONS = ['Prompt', 'Model', 'Input format', 'Output format', 'Outputs', 'Script'];

/** Whether each section row of the inspector shows its values. */
function expanded(): (string | null)[] {
  return SECTIONS.map((name) =>
    within(panel()).getByRole('button', {name}).getAttribute('aria-expanded'),
  );
}

it('starts every section row collapsed, with its value and its pencil to edit it', async () => {
  await renderEditor(editorApi('funny-story-with-review', j3), 'funny-story-with-review');
  fireEvent.click(screen.getByRole('group', {name: 'Reviewer'}));
  expect(within(panel()).getByRole('heading', {name: 'Reviewer', level: 2})).toBeTruthy();
  expect(within(panel()).getByText('LLM Call · 1.0.0 · with Router')).toBeTruthy();
  expect(expanded()).toEqual(SECTIONS.map(() => 'false'));
  expect(within(panel()).queryAllByRole('term')).toHaveLength(0);
  for (const name of SECTIONS)
    expect(within(panel()).getByRole('button', {name: `Edit ${name}`})).toBeTruthy();
  const outputs = within(panel()).getByRole('button', {name: 'Outputs'});
  const preview = document.getElementById(outputs.getAttribute('aria-describedby') ?? '');
  expect(preview?.textContent).toBe('accepted, revise');
  expect(within(panel()).getByRole('region', {name: 'Outputs'}).textContent).toContain('Router');
});

it('expands the rows one by one or all at once, and starts again for another node', async () => {
  await renderEditor(editorApi('funny-story-with-review', j3), 'funny-story-with-review');
  fireEvent.click(screen.getByRole('group', {name: 'Reviewer'}));
  await userEvent.click(within(panel()).getByRole('button', {name: 'Model'}));
  expect(expanded()).toEqual(['false', 'true', 'false', 'false', 'false', 'false']);
  expect(within(panel()).getByRole('term').textContent).toBe('LLM');
  await userEvent.click(within(panel()).getByRole('button', {name: 'Expand all'}));
  expect(expanded()).toEqual(SECTIONS.map(() => 'true'));
  await userEvent.click(within(panel()).getByRole('button', {name: 'Collapse all'}));
  expect(expanded()).toEqual(SECTIONS.map(() => 'false'));
  await userEvent.click(within(panel()).getByRole('button', {name: 'Expand all'}));
  fireEvent.click(screen.getByRole('group', {name: 'Proposer'}));
  expect(within(panel()).getByRole('button', {name: 'Prompt'}).getAttribute('aria-expanded')).toBe(
    'false',
  );
  fireEvent.click(screen.getByRole('group', {name: 'Funny story'}));
  expect(within(panel()).queryByRole('button', {name: 'Expand all'})).toBeNull();
});

it('lists the sections down the side of a node dialog, with Remove in the footer', async () => {
  await renderEditor(editorApi('story-triage', j2), 'story-triage');
  fireEvent.click(screen.getByRole('group', {name: 'Judge'}));
  await userEvent.click(within(panel()).getByRole('button', {name: 'Edit Prompt'}));
  const dialog = screen.getByRole('dialog', {name: 'Judge'});
  const list = within(dialog).getByRole('tablist', {name: 'Sections'});
  expect(list.getAttribute('aria-orientation')).toBe('vertical');
  expect(
    within(list)
      .getAllByRole('tab')
      .map((tab) => tab.getAttribute('aria-label')),
  ).toEqual(SECTIONS);
  const group = within(list).getByText('Router');
  expect(within(list).getByRole('tab', {name: 'Script'}).getAttribute('aria-describedby')).toBe(
    group.id,
  );
  expect(within(dialog).queryByRole('button', {name: 'Remove Router'})).toBeNull();
  within(list).getByRole('tab', {name: 'Prompt'}).focus();
  await userEvent.keyboard('{ArrowDown}');
  expect(within(dialog).getByRole('tabpanel', {name: 'Model'})).toBeTruthy();
  await userEvent.click(within(list).getByRole('tab', {name: 'Script'}));
  expect(within(dialog).getByRole('button', {name: 'Remove Router'})).toBeTruthy();
});
