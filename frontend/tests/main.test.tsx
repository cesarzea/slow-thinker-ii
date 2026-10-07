import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {createRoot} from 'react-dom/client';
import documentHtml from '../index.html?raw';

vi.mock('react-dom/client', () => ({createRoot: vi.fn(() => ({render: vi.fn()}))}));

beforeEach(() => {
  vi.resetModules();
  vi.clearAllMocks();
});
afterEach(() => {
  document.body.replaceChildren();
});

it('declares English as the document language', () => {
  const page = new DOMParser().parseFromString(documentHtml, 'text/html');
  expect(page.documentElement.lang).toBe('en');
  expect(page.querySelector('script')?.getAttribute('src')).toBe('/src/main.tsx');
});

it('mounts the application in the document container', async () => {
  const container = document.createElement('div');
  container.id = 'root';
  document.body.append(container);
  await import('../src/main.tsx');
  expect(createRoot).toHaveBeenCalledWith(container);
});

it('reports a missing mount point', async () => {
  await expect(import('../src/main.tsx')).rejects.toThrow('The application container is missing');
  expect(createRoot).not.toHaveBeenCalled();
});
