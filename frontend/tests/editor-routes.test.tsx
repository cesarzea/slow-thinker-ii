import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {act, cleanup, fireEvent, render, screen} from '@testing-library/react';
import {GraphPreview} from '../src/features/editor/index.ts';
import {catalog, j3} from './support/contract.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

async function resize(): Promise<void> {
  await act(async () => {
    window.dispatchEvent(new Event('resize'));
    await new Promise((resolve) => setTimeout(resolve, 10));
  });
}

it('frames the view again on resize until the person zooms by hand', async () => {
  const empty = {};
  render(
    <div style={{width: '900px', height: '500px'}}>
      <GraphPreview
        document={{...j3, layout: {}}}
        catalog={catalog}
        activations={empty}
        messages={empty}
      />
    </div>,
  );
  const viewport = (): string =>
    document.querySelector<HTMLElement>('.react-flow__viewport')?.style.transform ?? '';
  const before = viewport();
  await resize();
  expect(viewport()).toBe(before);
  for (const name of ['Zoom In', 'Zoom Out', 'Fit View'])
    fireEvent.click(screen.getByRole('button', {name}));
  await resize();
  const badges = screen.getAllByTitle('Activations').map((badge) => badge.textContent);
  expect(badges).toEqual(['0', '0', '0', '0']);
});
