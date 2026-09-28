import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, act} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {executionView, tick} from './support/execution-view.tsx';
import {OperatorServer} from './support/operator-server.ts';

beforeEach(() => {
  localStorage.clear();
  vi.useFakeTimers({toFake: ['setInterval', 'clearInterval']});
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

it('creates a saved session, starts a graph and displays results and authoritative money', async () => {
  const server = executionView();
  await tick();
  await userEvent.type(screen.getByLabelText('Nueva sesión'), 'New research');
  await userEvent.click(screen.getByRole('button', {name: 'Crear sesión'}));
  await tick();
  await userEvent.type(screen.getByLabelText('Problema o tarea'), 'Solve this');
  await userEvent.click(screen.getByRole('button', {name: 'Iniciar ejecución'}));
  await tick();
  expect(screen.getByRole('heading', {name: 'Completada'})).toBeTruthy();
  expect(screen.getByRole('region', {name: 'Resultado final'}).textContent).toContain(
    'A test result',
  );
  expect(server.mutations).toHaveLength(2);
  await userEvent.click(
    within(screen.getByRole('region', {name: 'Historial de la sesión'})).getByRole('button'),
  );
  await tick();
  expect(screen.getByRole('heading', {name: 'Completada'})).toBeTruthy();
});

it('stops a running graph without displaying a successful final output', async () => {
  const server = new OperatorServer();
  server.pending = true;
  executionView(server);
  await tick();
  await userEvent.type(screen.getByLabelText('Problema o tarea'), 'Wait');
  await userEvent.click(screen.getByRole('button', {name: 'Iniciar ejecución'}));
  await tick();
  await userEvent.click(screen.getByRole('button', {name: 'Detener ejecución'}));
  await tick();
  expect(screen.getByRole('heading', {name: 'Cancelada'})).toBeTruthy();
  expect(screen.queryByRole('region', {name: 'Resultado final'})).toBeNull();
});

it('can withdraw a recovered Start with missing input instead of reconstructing a prompt', async () => {
  localStorage.setItem('slow-thinker-ii.pending-command', 'start-lost');
  executionView();
  await tick();
  expect(screen.getByRole('complementary', {name: 'Solicitud pendiente'})).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Consultar recibo'}));
  await userEvent.click(screen.getByRole('button', {name: 'Retirar inicio pendiente'}));
  await tick();
  expect(screen.queryByRole('complementary', {name: 'Solicitud pendiente'})).toBeNull();
});

it('reports disconnection while keeping execution unavailable', async () => {
  const server = executionView();
  await tick();
  server.readStatus = 503;
  await tick();
  await userEvent.type(screen.getByLabelText('Problema o tarea'), 'Task');
  expect(screen.getByRole('button', {name: 'Iniciar ejecución'}).hasAttribute('disabled')).toBe(
    true,
  );
  expect(screen.getByText(/No se pudo confirmar/)).toBeTruthy();
});

it('allows explicit dismissal of a non-Start receipt without cancelling it on the server', async () => {
  localStorage.setItem('slow-thinker-ii.pending-command', 'session-lost');
  const server = executionView();
  await tick();
  await act(async () => {
    await userEvent.click(screen.getByRole('button', {name: 'Dejar de seguir esta solicitud'}));
  });
  expect(localStorage.getItem('slow-thinker-ii.pending-command')).toBeNull();
  expect(server.mutations).toHaveLength(0);
});
