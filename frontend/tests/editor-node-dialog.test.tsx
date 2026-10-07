import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {Diagnostic, GraphDocument} from '../src/api/index.ts';
import {editorApi, missingModel, renderEditor} from './support/editor-harness.tsx';
import {failure} from './support/fake-api.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {copy, j1} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});
const panel = (): HTMLElement => screen.getByRole('complementary', {name: 'Selected node'});

async function openSection(node: string, section: string): Promise<HTMLElement> {
  fireEvent.click(screen.getByRole('group', {name: node}));
  await userEvent.click(within(panel()).getByRole('button', {name: `Edit ${section}`}));
  return screen.getByRole('dialog', {name: node});
}

const emptyPrompt = (document: GraphDocument): Diagnostic[] =>
  document.nodes[1]?.config['prompt'] === ''
    ? [
        {
          severity: 'error',
          code: 'invalid_config',
          message: 'Instructions is required.',
          path: '/nodes/1/config/prompt',
          node_id: 'proposer',
        },
      ]
    : [];

it('opens the dialog at the edited section and applies after validating the whole document', async () => {
  const {api} = await renderEditor(editorApi('funny-story', j1), 'funny-story');
  const dialog = await openSection('Proposer', 'Prompt');
  expect(within(dialog).getByRole('tab', {name: 'Prompt'}).getAttribute('aria-selected')).toBe(
    'true',
  );
  expect(
    within(dialog)
      .getAllByRole('tab')
      .map((tab) => tab.getAttribute('aria-label')),
  ).toEqual(['Prompt', 'Model', 'Input format', 'Output format']);
  const instructions = within(dialog).getByRole('textbox', {name: 'Instructions'});
  await userEvent.clear(instructions);
  await userEvent.type(instructions, 'Be brief.');
  const before = api.count('POST /graphs/validate');
  await userEvent.click(within(dialog).getByRole('button', {name: 'Apply'}));
  await waitFor(() => {
    expect(screen.queryByRole('dialog')).toBeNull();
  });
  expect(api.count('POST /graphs/validate')).toBe(before + 2);
  expect(within(panel()).getByRole('region', {name: 'Prompt'}).textContent).toContain('Be brief.');
});

it('keeps the dialog open with the errors its changes would introduce', async () => {
  await renderEditor(editorApi('funny-story', j1, emptyPrompt), 'funny-story');
  const dialog = await openSection('Proposer', 'Prompt');
  await userEvent.clear(within(dialog).getByRole('textbox', {name: 'Instructions'}));
  await userEvent.click(within(dialog).getByRole('button', {name: 'Apply'}));
  const problems = await within(dialog).findByText('Instructions is required.');
  expect(problems.closest('[role="alert"]')).not.toBeNull();
  await userEvent.click(within(dialog).getByRole('button', {name: 'Cancel'}));
  expect(within(panel()).getByRole('region', {name: 'Prompt'}).textContent).toContain(
    'Rewrite this story',
  );
});

it('applies changes that leave earlier errors of the node in place', async () => {
  const document = copy(j1);
  const proposer = document.nodes[1];
  if (proposer !== undefined) proposer.config = {...proposer.config, model: null};
  await renderEditor(editorApi('funny-story', document, missingModel), 'funny-story');
  const dialog = await openSection('Proposer', 'Prompt');
  await userEvent.type(within(dialog).getByRole('textbox', {name: 'Instructions'}), '!');
  await userEvent.click(within(dialog).getByRole('button', {name: 'Apply'}));
  await waitFor(() => {
    expect(screen.queryByRole('dialog')).toBeNull();
  });
});

it('reports a dialog that cannot be checked', async () => {
  const api = editorApi('funny-story', j1);
  await renderEditor(api, 'funny-story');
  const dialog = await openSection('Story', 'Message');
  api.on('POST /graphs/validate', failure(503, 'unavailable', 'Validation is unavailable.'));
  await userEvent.click(within(dialog).getByRole('button', {name: 'Apply'}));
  expect((await within(dialog).findByRole('alert')).textContent).toBe(
    'Could not check the changes: Validation is unavailable.',
  );
});

it('selects an LLM and its parameters in the Model section', async () => {
  await renderEditor(editorApi('funny-story', j1), 'funny-story');
  const dialog = await openSection('Proposer', 'Model');
  await userEvent.selectOptions(
    within(dialog).getByRole('combobox', {name: 'LLM'}),
    'DeepSeek · DeepSeek Flash',
  );
  await userEvent.selectOptions(within(dialog).getByRole('combobox', {name: 'Reasoning'}), 'high');
  expect(
    within(dialog).getByRole<HTMLInputElement>('spinbutton', {name: 'Temperature'}).disabled,
  ).toBe(true);
  await userEvent.click(within(dialog).getByRole('tab', {name: 'Output format'}));
  await userEvent.selectOptions(within(dialog).getByRole('combobox', {name: 'Format'}), 'JSON');
  expect(within(dialog).getByRole('button', {name: 'Add property'})).toBeTruthy();
  await userEvent.click(within(dialog).getByRole('button', {name: 'Apply'}));
  await waitFor(() => {
    expect(screen.queryByRole('dialog')).toBeNull();
  });
  expect(within(panel()).getByRole('region', {name: 'Model'}).textContent).toContain(
    'DeepSeek · DeepSeek Flash · Reasoning high',
  );
});
