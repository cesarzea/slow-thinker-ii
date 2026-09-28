import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {ExecutionWorkspace} from '../src/app/execution-workspace.tsx';
import {InspectionServer} from './support/inspection-server.ts';
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
  const history = within(await screen.findByRole('region', {name: 'Historial de la sesión'}));
  await userEvent.click(history.getByRole('button'));
  await userEvent.click(await screen.findByRole('button', {name: 'Inspeccionar ejecución'}));
  expect(await screen.findByText('call.requested')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Cerrar inspector'}));
  expect(screen.queryByRole('region', {name: 'Inspector de ejecución'})).toBeNull();
  expect(server.operator.mutations).toHaveLength(0);
});
