import type {ReactElement} from 'react';
import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {act, cleanup, render, screen, waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {OperatorClient} from '../src/api/index.ts';
import {Editor, GraphPreview} from '../src/features/editor/index.ts';
import type {HistoryContext} from '../src/features/editor/index.ts';
import {renameNode} from '../src/features/editor/state/document.ts';
import {saved, toolbarStatus} from './support/editor-harness.tsx';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {graphServer} from './support/graph-server.ts';
import {catalog, j1} from './support/contract.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function Panel({context}: {readonly context: HistoryContext}): ReactElement {
  return (
    <aside aria-label="History">
      <p>{`${context.graphId} · ${context.branch} · change ${String(context.latestChange)}`}</p>
      <p>{`Active v${String(context.activeVersion)}`}</p>
      <button
        type="button"
        onClick={() => {
          context.onRestore(renameNode(j1, 'story', 'Restored'));
        }}
      >
        Restore
      </button>
      <button
        type="button"
        onClick={() => {
          context.onActivated(2);
        }}
      >
        Activated
      </button>
      <button type="button" onClick={context.onClose}>
        Close history
      </button>
    </aside>
  );
}

it('hosts the history panel in place of the inspector, with what it needs', async () => {
  const {api, state} = graphServer('funny-story', j1);
  api.install();
  render(
    <Editor
      client={new OperatorClient('credential')}
      graphId="funny-story"
      created={null}
      renderHistory={(context) => <Panel context={context} />}
    />,
  );
  await userEvent.click(await screen.findByRole('button', {name: 'History'}));
  expect(screen.getByRole('button', {name: 'History'}).getAttribute('aria-pressed')).toBe('true');
  expect(screen.getByText('funny-story · main · change 1')).toBeTruthy();
  expect(screen.queryByRole('complementary', {name: 'Graph'})).toBeNull();
  await userEvent.click(screen.getByRole('button', {name: 'Restore'}));
  expect(await screen.findByRole('group', {name: 'Restored'})).toBeTruthy();
  await saved();
  expect(screen.getByText('funny-story · main · change 2')).toBeTruthy();
  state.versions.push(2);
  await userEvent.click(screen.getByRole('button', {name: 'Activated'}));
  expect(await screen.findByText('v2 · Active')).toBeTruthy();
  expect(screen.getByTitle('Branch; switch branches in History').textContent).toBe('main');
  expect(toolbarStatus()).toBe('Saved');
  await userEvent.click(screen.getByRole('button', {name: 'Close history'}));
  expect(screen.getByRole('complementary', {name: 'Graph'})).toBeTruthy();
});

it('opens another branch and keeps the history panel open', async () => {
  const {api} = graphServer('funny-story', j1);
  api.install();
  let open: HistoryContext | null = null;
  render(
    <Editor
      client={new OperatorClient('credential')}
      graphId="funny-story"
      created={null}
      renderHistory={(context) => {
        open = context;
        return <Panel context={context} />;
      }}
    />,
  );
  await userEvent.click(await screen.findByRole('button', {name: 'History'}));
  const context = open as HistoryContext | null;
  act(() => {
    context?.onBranchChange('experiment');
  });
  await waitFor(() => {
    expect(api.count('GET /graphs/funny-story')).toBeGreaterThan(1);
  });
  expect(await screen.findByText('funny-story · main · change 1')).toBeTruthy();
});

it('shows a graph without counts when none are given', () => {
  render(
    <div style={{width: '900px', height: '500px'}}>
      <GraphPreview document={j1} catalog={catalog} />
    </div>,
  );
  expect(screen.queryAllByTitle('Activations')).toHaveLength(0);
});
