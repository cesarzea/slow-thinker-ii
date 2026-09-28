import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {createRoot} from 'react-dom/client';

vi.mock('react-dom/client', () => ({createRoot: vi.fn(() => ({render: vi.fn()}))}));

beforeEach(() => {
  vi.resetModules();
  vi.clearAllMocks();
});
afterEach(() => {
  document.body.replaceChildren();
});

it('mounts the application in the document container', async () => {
  const container = document.createElement('div');
  container.id = 'root';
  document.body.append(container);
  await import('../src/main.tsx');
  expect(createRoot).toHaveBeenCalledWith(container);
});

it('reports a missing mount point', async () => {
  await expect(import('../src/main.tsx')).rejects.toThrow('Falta el contenedor');
  expect(createRoot).not.toHaveBeenCalled();
});
