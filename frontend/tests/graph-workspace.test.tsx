import type * as ReactFlowModule from '@xyflow/react';
import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {ExecutionWorkspace} from '../src/app/execution-workspace.tsx';
import {InspectionServer} from './support/inspection-server.ts';
import {boundedDetail, repeatedPage, savedDefinition, summary} from './support/projection-data.ts';
import {runRecord} from './support/operator-data.ts';
import {tick} from './support/execution-view.tsx';
vi.mock('@xyflow/react', async (original) => {
  const {Canvas, Empty} = await import('./support/graph-canvas.tsx');
  return {
    ...(await original<typeof ReactFlowModule>()),
    ReactFlow: Canvas,
    Background: Empty,
    Controls: Empty,
  };
});
let server: InspectionServer;
beforeEach(() => {
  localStorage.clear();
  vi.useFakeTimers({toFake: ['setInterval', 'clearInterval']});
  server = new InspectionServer();
  server.operator.detail = boundedDetail;
  server.operator.definition = savedDefinition(boundedDetail);
  server.operator.execution = repeatedPage;
  server.operator.run = {...runRecord(), graph_id: 'bounded-review', graph_revision: 'example-1'};
  server.activation.activation_id = 'draft-two';
  server.activation.node_id = 'propose';
  server.activation.target.instance = 'proposer';
  server.call.call_id = 'worker-call';
  vi.stubGlobal('fetch', server.fetch);
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});
async function selectedRun(): Promise<void> {
  render(<ExecutionWorkspace credential="key" graph={summary(boundedDetail)} />);
  await tick();
  await userEvent.click(
    within(screen.getByRole('region', {name: 'Historial de la sesión'})).getByRole('button'),
  );
  await tick();
}
it('bridges graph objects to configuration and exact repeated activation evidence with visible focus', async () => {
  await selectedRun();
  const live = within(screen.getByRole('region', {name: 'Grafo de la ejecución seleccionada'}));
  await userEvent.click(live.getByText('Explorar componentes, nodos y evidencia en lista'));
  await userEvent.click(live.getByRole('button', {name: 'Componente proposer'}));
  expect(document.activeElement).toBe(screen.getByRole('heading', {name: 'component: proposer'}));
  expect(live.getByRole('region', {name: 'Objeto seleccionado'}).textContent).toContain(
    'instructions',
  );
  await userEvent.click(live.getByRole('button', {name: '#3 · draft-two · running'}));
  expect(document.activeElement).toBe(
    await screen.findByRole('heading', {name: 'Activación draft-two'}),
  );
  expect(server.reads).toContain('/api/v1/runs/run/activations/draft-two');
  expect(server.operator.mutations).toHaveLength(0);
  await userEvent.click(live.getByRole('button', {name: 'Llamada worker-call'}));
  expect(document.activeElement).toBe(
    await screen.findByRole('heading', {name: 'Llamada worker-call'}),
  );
});
it('labels stale graphs on connection failure and resumes without issuing a command', async () => {
  await selectedRun();
  server.operator.projectionStatus = 503;
  await tick();
  expect(screen.getByText(/No se pudo actualizar el grafo/)).toBeTruthy();
  server.operator.projectionStatus = 200;
  await tick();
  expect(screen.queryByText(/No se pudo actualizar el grafo/)).toBeNull();
  expect(server.operator.mutations).toHaveLength(0);
});
it('does not enable Start from a stale or invalid catalog definition', async () => {
  server.operator.detail = {};
  render(<ExecutionWorkspace credential="key" graph={summary(boundedDetail)} />);
  await tick();
  expect(await screen.findByRole('alert')).toHaveProperty(
    'textContent',
    'No se pudo cargar la definición exacta del experimento.',
  );
  await userEvent.type(screen.getByLabelText(/Problema o tarea/), 'task');
  expect(screen.getByRole<HTMLButtonElement>('button', {name: 'Iniciar ejecución'}).disabled).toBe(
    true,
  );
});
