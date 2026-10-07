import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen} from '@testing-library/react';
import type {GraphDocument} from '../src/api/index.ts';
import {GraphPreview} from '../src/features/editor/index.ts';
import {editorApi, renderEditor} from './support/editor-harness.tsx';
import {catalog, j3} from './support/contract.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const turned: GraphDocument = {
  ...j3,
  port_sides: {reviewer: {in: 'top', accepted: 'bottom'}, proposer: {out: 'left'}},
};

function handle(node: string, port: string): HTMLElement {
  const found = document.querySelector<HTMLElement>(
    `.react-flow__node[data-id="${node}"] .react-flow__handle[data-handleid="${port}"]`,
  );
  if (found === null) throw new Error(`No handle ${node}.${port}`);
  return found;
}

const rail = (node: string, side: string): string[] =>
  [
    ...document.querySelectorAll(
      `.react-flow__node[data-id="${node}"] :is(.rail-${side}, .ports-${side}) .port-label`,
    ),
  ].map((label) => label.textContent);

it('draws each port on its side, named beside its handle, also on a read-only canvas', async () => {
  render(
    <div style={{width: '1000px', height: '600px'}}>
      <GraphPreview document={turned} catalog={catalog} />
    </div>,
  );
  await screen.findAllByText('Reviewer');
  const sides = (node: string, ports: string[]): (string | null)[] =>
    ports.map((port) => handle(node, port).getAttribute('data-handlepos'));
  expect(sides('reviewer', ['in', 'accepted', 'revise'])).toEqual(['top', 'bottom', 'right']);
  expect(sides('proposer', ['in', 'out'])).toEqual(['left', 'left']);
  expect([rail('reviewer', 'top'), rail('reviewer', 'bottom'), rail('reviewer', 'right')]).toEqual([
    ['in'],
    ['accepted'],
    ['revise'],
  ]);
  expect(rail('proposer', 'left')).toEqual(['in', 'out']);
});

it('shows a port’s full name and what it is connected to while its handle is hovered', async () => {
  render(
    <div style={{width: '1000px', height: '600px'}}>
      <GraphPreview document={turned} catalog={catalog} />
    </div>,
  );
  await screen.findAllByText('Reviewer');
  fireEvent.mouseEnter(handle('reviewer', 'revise'));
  expect(screen.getByRole('tooltip').textContent).toBe('reviseTo Proposer · in');
  fireEvent.mouseLeave(handle('reviewer', 'revise'));
  expect(screen.queryByRole('tooltip')).toBeNull();
  fireEvent.mouseEnter(handle('proposer', 'in'));
  expect(screen.getByRole('tooltip').textContent).toBe('inFrom Story · out, Reviewer · revise');
});

it('shows the tip of a handle in focus on the editor, and of a port with no connection', async () => {
  const lonely = {...j3, connections: j3.connections.filter((item) => item.to !== 'result.in')};
  await renderEditor(editorApi('funny-story-with-review', lonely), 'funny-story-with-review');
  const accepted = screen.getByRole('button', {name: 'Reviewer output accepted'});
  fireEvent.focus(accepted);
  expect(screen.getByRole('tooltip').textContent).toBe('acceptedNot connected');
  fireEvent.blur(accepted);
  expect(screen.queryByRole('tooltip')).toBeNull();
});
