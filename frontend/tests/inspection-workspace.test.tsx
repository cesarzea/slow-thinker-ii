import type * as ReactFlowModule from '@xyflow/react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {ExecutionWorkspace} from '../src/app/execution-workspace.tsx';
import {InspectionServer} from './support/inspection-server.ts';
vi.mock('@xyflow/react', async (original) => {
  const {Canvas, Empty, EdgeFrame} = await import('./support/graph-canvas.tsx');
  return {
    ...(await original<typeof ReactFlowModule>()),
    ReactFlow: Canvas,
    Background: Empty,
    Controls: Empty,
    Handle: Empty,
    BaseEdge: EdgeFrame,
  };
});
import {graph, runRecord} from './support/operator-data.ts';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it('opens and closes inspection of a saved execution without issuing a new Start', async () => {
  localStorage.clear();
  const server = new InspectionServer();
  server.operator.run = runRecord();
  vi.stubGlobal('fetch', server.fetch);
  render(<ExecutionWorkspace credential="key" graph={graph} />);
  const history = within(await screen.findByRole('region', {name: 'Session history'}));
  await userEvent.click(history.getByRole('button'));
  await userEvent.click(await screen.findByRole('button', {name: 'Inspect run'}));
  expect(await screen.findByText('call.requested')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Close inspector'}));
  expect(screen.queryByRole('region', {name: 'Run inspector'})).toBeNull();
  expect(server.operator.mutations).toHaveLength(0);
});
