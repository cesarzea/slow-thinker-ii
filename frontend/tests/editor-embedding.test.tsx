import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {editorApi, renderEditor} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {j1, j2} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});
const panel = (): HTMLElement => screen.getByRole('complementary', {name: 'Selected node'});

it('embeds a Router whose outputs replace the node outputs', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  fireEvent.click(screen.getByRole('group', {name: 'Proposer'}));
  await userEvent.click(within(panel()).getByRole('button', {name: 'Add component'}));
  const add = screen.getByRole('dialog', {name: 'Add component'});
  expect(within(add).getByText(/outgoing connections are removed/u)).toBeTruthy();
  await userEvent.click(within(add).getByRole('button', {name: 'Router'}));
  expect(screen.getByRole('button', {name: 'Proposer output yes'})).toBeTruthy();
  expect(screen.queryByRole('button', {name: 'Proposer output out'})).toBeNull();
  expect(within(panel()).getByRole('region', {name: 'Outputs'}).textContent).toContain('Router');
  await userEvent.click(within(panel()).getByRole('button', {name: 'Edit Outputs'}));
  const dialog = screen.getByRole('dialog', {name: 'Proposer'});
  expect(within(dialog).getByText('LLM Call · with Router')).toBeTruthy();
  const first = within(dialog).getByRole('textbox', {name: 'Output 1'});
  await userEvent.clear(first);
  await userEvent.type(first, 'funny');
  await userEvent.click(within(dialog).getByRole('tab', {name: 'Script'}));
  expect(within(dialog).getByRole('textbox', {name: 'route(received, node_input)'})).toBeTruthy();
  await userEvent.click(within(dialog).getByRole('button', {name: 'Apply'}));
  await screen.findByRole('button', {name: 'Proposer output funny'});
});

it('cancels adding a component', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  fireEvent.click(screen.getByRole('group', {name: 'Story'}));
  expect(within(panel()).queryByRole('button', {name: 'Add component'})).toBeNull();
  fireEvent.click(screen.getByRole('group', {name: 'Proposer'}));
  await userEvent.click(within(panel()).getByRole('button', {name: 'Add component'}));
  await userEvent.keyboard('{Escape}');
  expect(screen.queryByRole('dialog')).toBeNull();
});

it('removes the Router from the node menu after listing the connections it takes', async () => {
  await renderEditor(editorApi('story-triage', j2), 'story-triage');
  fireEvent.click(screen.getByRole('group', {name: 'Judge'}));
  await userEvent.click(within(panel()).getByRole('button', {name: 'More actions for Judge'}));
  await userEvent.click(screen.getByRole('menuitem', {name: 'Remove Router'}));
  const confirm = screen.getByRole('dialog', {name: 'Remove Router'});
  expect(within(confirm).getByRole('list', {name: 'Connections to remove'}).textContent).toBe(
    'Judge · funny → Funny · inJudge · not_funny → Not funny · in',
  );
  await userEvent.click(within(confirm).getByRole('button', {name: 'Remove'}));
  expect(screen.getByRole('button', {name: 'Judge output out'})).toBeTruthy();
  expect(within(panel()).getByRole('button', {name: 'Add component'})).toBeTruthy();
});

it('removes the Router inside the node dialog and applies the result', async () => {
  await renderEditor(editorApi('story-triage', j2), 'story-triage');
  fireEvent.click(screen.getByRole('group', {name: 'Judge'}));
  await userEvent.click(within(panel()).getByRole('button', {name: 'Edit Script'}));
  const dialog = screen.getByRole('dialog', {name: 'Judge'});
  await userEvent.click(within(dialog).getByRole('button', {name: 'Remove Router'}));
  await userEvent.click(
    within(screen.getByRole('dialog', {name: 'Remove Router'})).getByRole('button', {
      name: 'Cancel',
    }),
  );
  await userEvent.click(within(dialog).getByRole('button', {name: 'Remove Router'}));
  await userEvent.click(
    within(screen.getByRole('dialog', {name: 'Remove Router'})).getByRole('button', {
      name: 'Remove',
    }),
  );
  expect(
    within(dialog)
      .getAllByRole('tab')
      .map((tab) => tab.getAttribute('aria-label')),
  ).toEqual(['Prompt', 'Model', 'Input format', 'Output format']);
  await userEvent.click(within(dialog).getByRole('button', {name: 'Apply'}));
  await screen.findByRole('button', {name: 'Judge output out'});
});
