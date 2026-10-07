import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {documents, historyApi, renderPanel} from './support/history-api.tsx';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
const clock = new Intl.DateTimeFormat('en', {hour: '2-digit', minute: '2-digit', hourCycle: 'h23'});
const path = '/graphs/funny-story';

async function describedChanges(): Promise<(string | undefined)[]> {
  const changes = screen.getByRole('list', {name: 'Changes'});
  await within(changes).findByText('Limits edited');
  return within(changes)
    .getAllByRole('listitem')
    .map((item) => item.children[1]?.textContent);
}

it('shows the working copy, the versions and the described changes of the branch', async () => {
  historyApi();
  const {onClose} = renderPanel();
  expect(screen.getByRole('heading', {name: 'History'})).toBeTruthy();
  const card = await screen.findByRole('region', {name: 'Working copy'});
  const saved = clock.format(new Date('2026-10-04T10:25:00.000Z'));
  expect(within(card).getByText(`1 change since version 2 · saved ${saved}`)).toBeTruthy();
  const versions = screen.getByRole('list', {name: 'Versions'});
  expect(
    within(versions)
      .getAllByRole('listitem')
      .map((item) => item.querySelector('p')?.textContent),
  ).toEqual(['Version 2 · Active', 'Version 1']);
  expect(await describedChanges()).toEqual([
    'Limits edited',
    'Proposer · Prompt editedv2',
    'Moved Story',
    'Added Funny story (Output); Connected Proposer · out → Funny story · inv1',
    'Created the graph',
  ]);
  expect(
    within(screen.getByRole('listitem', {name: 'Change 5'})).getByText('Current'),
  ).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Close history'}));
  expect(onClose).toHaveBeenCalledTimes(1);
});

it('activates the working copy as the next version', async () => {
  const api = historyApi();
  const {onActivated} = renderPanel();
  const card = await screen.findByRole('region', {name: 'Working copy'});
  await userEvent.click(within(card).getByRole('button', {name: 'Activate as v3'}));
  await waitFor(() => {
    expect(onActivated).toHaveBeenCalledWith(3);
  });
  expect(api.last(`POST ${path}/versions`)?.body).toEqual({change: 5});
});

it('activates an earlier version again by restoring it as a change first', async () => {
  const api = historyApi();
  const {onActivated, onRestore} = renderPanel();
  const first = await screen.findByRole('listitem', {name: 'Version 1'});
  expect(
    within(screen.getByRole('listitem', {name: 'Version 2'})).queryByText('Activate as v3'),
  ).toBeNull();
  await userEvent.click(within(first).getByRole('button', {name: 'Activate as v3'}));
  await waitFor(() => {
    expect(onActivated).toHaveBeenCalledWith(3);
  });
  expect(api.last(`POST ${path}/changes`)?.body).toEqual({branch: 'main', document: documents[2]});
  expect(api.last(`POST ${path}/versions`)?.body).toEqual({change: 7});
  expect(onRestore).toHaveBeenCalledWith(documents[2]);
});

it('reports an activation the server refuses, with its first problem', async () => {
  const api = historyApi();
  api.on(`POST ${path}/versions`, {
    status: 422,
    body: {
      error: {
        code: 'invalid_document',
        message: 'The graph has problems.',
        diagnostics: [
          {
            severity: 'error',
            code: 'unknown_port',
            message: 'Proposer has no port x.',
            path: '/connections/0',
            node_id: null,
          },
        ],
      },
    },
  });
  renderPanel();
  const card = await screen.findByRole('region', {name: 'Working copy'});
  await userEvent.click(within(card).getByRole('button', {name: 'Activate as v3'}));
  expect((await screen.findByRole('alert')).textContent).toBe(
    'Activation failed. Proposer has no port x.',
  );
});
