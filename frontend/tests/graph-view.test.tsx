import type * as ReactFlowModule from '@xyflow/react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import type {GraphDetail} from '../src/api/index.ts';
import {GraphView} from '../src/features/graph-view/index.ts';
import {boundedDetail, repeatedPage, summary} from './support/projection-data.ts';
vi.mock('@xyflow/react', async (original) => {
  const {Canvas, Empty} = await import('./support/graph-canvas.tsx');
  return {
    ...(await original<typeof ReactFlowModule>()),
    ReactFlow: Canvas,
    Background: Empty,
    Controls: Empty,
  };
});
afterEach(cleanup);
function view(): ReturnType<typeof vi.fn> {
  const select = vi.fn();
  render(
    <GraphView
      graph={summary(boundedDetail)}
      detail={boundedDetail}
      execution={repeatedPage}
      onSelect={select}
    />,
  );
  return select;
}
it('separates conditional control, permission, binding and observed-call layers with optional internals', async () => {
  view();
  expect(screen.getByRole('button', {name: 'control: revise'})).toBeTruthy();
  expect(screen.getByTestId('terminal:exit')).toBeTruthy();
  expect(screen.queryByTestId('component:review-worker')).toBeNull();
  await userEvent.click(screen.getByLabelText('Permisos'));
  await userEvent.click(screen.getByLabelText('Recursos'));
  expect(
    screen.getByRole('button', {name: 'permission: generate'}).getAttribute('data-target'),
  ).toBe('component:reviewer');
  await userEvent.click(screen.getByLabelText('Mostrar componentes internos'));
  expect(screen.getByTestId('component:review-worker')).toBeTruthy();
  expect(screen.getByRole('button', {name: 'binding: worker'}).getAttribute('data-target')).toBe(
    'component:review-worker',
  );
  await userEvent.click(screen.getByLabelText('Control'));
  expect(screen.queryByTestId('node:review')).toBeNull();
  await userEvent.click(screen.getByLabelText('Llamadas observadas'));
  expect(screen.queryByRole('button', {name: /Observada:/})).toBeNull();
});
it('selects repeated activation and exact calls through canvas and keyboard list without substituting agents', async () => {
  const select = view();
  await userEvent.click(screen.getByText('Explorar componentes, nodos y evidencia en lista'));
  await userEvent.click(screen.getByRole('button', {name: 'Activación #3: propose'}));
  expect(select).toHaveBeenLastCalledWith({kind: 'activation', id: 'draft-two'});
  await userEvent.click(screen.getByRole('button', {name: /Observada: generate/}));
  expect(select).toHaveBeenLastCalledWith({kind: 'call', id: 'worker-call'});
  const call = screen.getByRole('button', {name: 'Llamada worker-call'});
  call.focus();
  await userEvent.keyboard('{Enter}');
  expect(select).toHaveBeenLastCalledWith({kind: 'call', id: 'worker-call'});
  await userEvent.click(screen.getByRole('button', {name: 'Componente review-worker'}));
  expect(select).toHaveBeenLastCalledWith({kind: 'component', id: 'review-worker'});
  await userEvent.click(screen.getByRole('button', {name: 'Nodo review'}));
  expect(select).toHaveBeenLastCalledWith({kind: 'node', id: 'review'});
});
it('preserves positions through status updates, then reorganizes only on request', async () => {
  const props = {graph: summary(boundedDetail), detail: boundedDetail, execution: repeatedPage};
  const mounted = render(<GraphView {...props} />);
  await userEvent.click(screen.getByRole('button', {name: 'Move activation:draft-two'}));
  mounted.rerender(<GraphView {...props} execution={{...repeatedPage, calls: []}} />);
  expect(screen.getByTestId('activation:draft-two').getAttribute('data-position')).toBe('800,900');
  await userEvent.click(screen.getByRole('button', {name: 'Reorganizar grafo'}));
  expect(screen.getByTestId('activation:draft-two').getAttribute('data-position')).toBe('500,480');
});
it('retains the catalog fallback and distinguishes unavailable execution from an empty recorded snapshot', async () => {
  render(<GraphView graph={summary(boundedDetail)} />);
  await userEvent.click(screen.getByRole('button', {name: 'Ejecución'}));
  expect(screen.getByText('No hay activaciones registradas disponibles.')).toBeTruthy();
  expect(screen.getByText(/Estructura detallada no disponible/)).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Estructura'}));
  const canvas = within(screen.getByLabelText('Test canvas'));
  await userEvent.click(canvas.getByRole('button', {name: 'Nodo: review · reviewer'}));
});

it('distinguishes declared roles in text and shape while preserving extension labels and IDs', async () => {
  const detail = roleFixture();
  const select = vi.fn();
  render(<GraphView graph={summary(detail)} detail={detail} onSelect={select} />);
  expect(screen.getByRole('button', {name: 'Agente: proposer'})).toBeTruthy();
  expect(screen.getByRole('button', {name: 'Recurso: proposer-model'})).toBeTruthy();
  expect(screen.getByRole('button', {name: 'Control: flow'})).toBeTruthy();
  expect(screen.getByRole('button', {name: 'custom-role: reviewer'})).toBeTruthy();
  expect(screen.getByTestId('component:proposer').style.borderStyle).toBe('solid');
  expect(screen.getByTestId('component:proposer-model').style.borderStyle).toBe('dashed');
  expect(screen.getByTestId('component:flow').style.borderStyle).toBe('double');
  await userEvent.click(screen.getByText('Explorar componentes, nodos y evidencia en lista'));
  const objects = within(screen.getByRole('list', {name: 'Objetos del grafo'}));
  expect(objects.getByText('· custom-role')).toBeTruthy();
  await userEvent.click(objects.getByRole('button', {name: 'Componente reviewer'}));
  expect(select).toHaveBeenCalledWith({kind: 'component', id: 'reviewer'});
});

function roleFixture(): GraphDetail {
  const roles: Readonly<Record<string, string[]>> = {
    proposer: ['agent'],
    reviewer: ['custom-role'],
    flow: ['control'],
    'proposer-model': ['resource'],
  };
  const detail = {
    ...boundedDetail,
    structure: {
      ...boundedDetail.structure,
      components: boundedDetail.structure.components.map((item) => ({
        ...item,
        roles: roles[item.id] ?? [],
      })),
    },
  };
  return detail;
}
