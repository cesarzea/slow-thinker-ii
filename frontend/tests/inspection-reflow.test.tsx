import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {Inspector} from '../src/features/inspector/index.ts';
import {InspectionServer} from './support/inspection-server.ts';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
it('keeps selected evidence visible through asynchronous reflow without stealing refresh focus', async () => {
  const callbacks = new Set<() => void>();
  const scroll = vi.fn();
  vi.stubGlobal('ResizeObserver', resizeObserver(callbacks));
  vi.stubGlobal('fetch', new InspectionServer().fetch);
  const view = render(
    <Inspector credential="key" run="run" selection={{kind: 'call', id: 'child'}} />,
  );
  const heading = await screen.findByRole('heading', {name: 'Llamada child'});
  heading.scrollIntoView = scroll;
  expect(document.activeElement).toBe(heading);
  for (const callback of callbacks) callback();
  expect(scroll).toHaveBeenCalledWith({block: 'nearest'});
  const refresh = screen.getAllByRole('button', {name: 'Actualizar evidencia'}).at(-1);
  if (refresh === undefined) throw new Error('Expected a call refresh control');
  await userEvent.click(refresh);
  await screen.findByText('agent → model.complete');
  for (const callback of callbacks) callback();
  expect(scroll).toHaveBeenCalledTimes(1);
  expect(document.activeElement).toBe(refresh);
  view.unmount();
  expect(callbacks.size).toBe(0);
});
function resizeObserver(callbacks: Set<() => void>): typeof ResizeObserver {
  return class implements ResizeObserver {
    private readonly callback: () => void;
    constructor(callback: ResizeObserverCallback) {
      this.callback = () => {
        callback([], this);
      };
    }
    observe(): void {
      callbacks.add(this.callback);
    }
    unobserve(): void {
      callbacks.delete(this.callback);
    }
    disconnect(): void {
      callbacks.delete(this.callback);
    }
  };
}
