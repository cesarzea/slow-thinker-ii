import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {catalog} from './support/contract.ts';
import {documents, historyApi, renderPanel} from './support/history-api.tsx';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
const path = '/graphs/funny-story';

it('restores an earlier change into the editor', async () => {
  historyApi();
  const {onRestore} = renderPanel();
  const change = await screen.findByRole('listitem', {name: 'Change 3'});
  await userEvent.click(within(change).getByRole('button', {name: 'Restore'}));
  await waitFor(() => {
    expect(onRestore).toHaveBeenCalledWith(documents[3]);
  });
});

it('switches branch and starts a new one from the open branch version', async () => {
  const api = historyApi();
  const {onBranchChange} = renderPanel();
  await userEvent.selectOptions(await screen.findByRole('combobox', {name: 'Branch'}), 'draft');
  expect(onBranchChange).toHaveBeenLastCalledWith('draft');
  await userEvent.click(screen.getByRole('button', {name: 'New branch'}));
  const dialog = screen.getByRole('dialog', {name: 'New branch'});
  expect(within(dialog).getByRole<HTMLSelectElement>('combobox', {name: 'Start from'}).value).toBe(
    'version:2',
  );
  await userEvent.type(within(dialog).getByRole('textbox', {name: 'Name'}), '-bad');
  await userEvent.click(within(dialog).getByRole('button', {name: 'Create branch'}));
  expect(within(dialog).getByRole('alert').textContent).toMatch(/^Use 1 to 40 letters/u);
  await userEvent.clear(within(dialog).getByRole('textbox', {name: 'Name'}));
  await userEvent.type(within(dialog).getByRole('textbox', {name: 'Name'}), 'Experiment');
  await userEvent.click(within(dialog).getByRole('button', {name: 'Create branch'}));
  await waitFor(() => {
    expect(onBranchChange).toHaveBeenLastCalledWith('Experiment');
  });
  expect(api.last(`POST ${path}/branches`)?.body).toEqual({name: 'Experiment', from: {version: 2}});
  expect(screen.queryByRole('dialog')).toBeNull();
});

it('branches from a chosen version and opens a version read only', async () => {
  const api = historyApi();
  const {renderGraph} = renderPanel();
  const first = await screen.findByRole('listitem', {name: 'Version 1'});
  await userEvent.click(within(first).getByRole('button', {name: 'Branch from here'}));
  const dialog = screen.getByRole('dialog', {name: 'New branch'});
  expect(within(dialog).getByRole<HTMLSelectElement>('combobox', {name: 'Start from'}).value).toBe(
    'version:1',
  );
  await userEvent.click(within(dialog).getByRole('button', {name: 'Cancel'}));
  expect(api.count(`POST ${path}/branches`)).toBe(0);
  await userEvent.click(within(first).getByRole('button', {name: 'Open read-only'}));
  const preview = screen.getByRole('dialog', {name: 'Version 1 · read only'});
  expect(await within(preview).findByText('Read-only canvas')).toBeTruthy();
  expect(renderGraph).toHaveBeenLastCalledWith({document: documents[2], catalog});
  await userEvent.click(within(preview).getByRole('button', {name: 'Close'}));
  expect(screen.queryByRole('dialog')).toBeNull();
});
