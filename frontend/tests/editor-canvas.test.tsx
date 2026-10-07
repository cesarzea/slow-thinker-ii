import type {ReactElement} from 'react';
import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, within} from '@testing-library/react';
import {ReactFlowProvider} from '@xyflow/react';
import {flowEdges, flowNodes} from '../src/features/editor/canvas/flow-model.ts';
import {DEFAULT_VIEW} from '../src/features/editor/canvas/connection-style.ts';
import {GraphCanvas} from '../src/features/editor/canvas/graph-canvas.tsx';
import {GraphPreview} from '../src/features/editor/index.ts';
import type {GraphDocument} from '../src/api/index.ts';
import {catalog, j2, j3} from './support/contract.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

interface Handlers {
  readonly onSelect: (id: string | null) => void;
  readonly onConnect: (from: string, to: string) => void;
  readonly onMove: (id: string, position: [number, number]) => void;
}

function Editable({
  document,
  ...handlers
}: Handlers & {readonly document: GraphDocument}): ReactElement {
  const input = {document, catalog, editable: true, selected: 'reviewer'};
  const nodes = flowNodes(input);
  return (
    <div style={{width: '1000px', height: '600px'}}>
      <ReactFlowProvider>
        <GraphCanvas
          nodes={nodes}
          edges={flowEdges(input, nodes)}
          view={DEFAULT_VIEW}
          editable
          label="Graph canvas"
          {...handlers}
        />
      </ReactFlowProvider>
    </div>
  );
}

function handlers(): Handlers {
  return {onSelect: vi.fn(), onConnect: vi.fn(), onMove: vi.fn()};
}

it('shows each node as a group named by the node, with buttons for its ports', () => {
  render(<Editable document={j3} {...handlers()} />);
  const reviewer = screen.getByRole('group', {name: 'Reviewer'});
  expect(within(reviewer).getByText('Router')).toBeTruthy();
  expect(screen.getByRole('button', {name: 'Reviewer output accepted'})).toBeTruthy();
  expect(screen.getByRole('button', {name: 'Reviewer output revise'})).toBeTruthy();
  expect(screen.queryByRole('button', {name: 'Reviewer output out'})).toBeNull();
  expect(screen.getByRole('button', {name: 'Proposer input in'})).toBeTruthy();
  expect(
    within(screen.getByRole('group', {name: 'Story'})).getByText('A cat tried to learn to fly.'),
  ).toBeTruthy();
});

it('selects a node when it is clicked and clears the selection on the pane', () => {
  const events = handlers();
  render(<Editable document={j2} {...events} />);
  fireEvent.click(screen.getByRole('group', {name: 'Judge'}));
  expect(events.onSelect).toHaveBeenCalledWith('judge');
  const pane = document.querySelector('.react-flow__pane');
  if (pane === null) throw new Error('Missing pane');
  fireEvent.click(pane);
  expect(events.onSelect).toHaveBeenLastCalledWith(null);
});

it('connects an output to an input by clicking their handles, also from the keyboard', () => {
  const events = handlers();
  render(<Editable document={{...j2, connections: []}} {...events} />);
  fireEvent.click(screen.getByRole('button', {name: 'Story output out'}));
  fireEvent.click(screen.getByRole('button', {name: 'Judge input in'}));
  expect(events.onConnect).toHaveBeenCalledWith('story.out', 'judge.in');
  fireEvent.keyDown(screen.getByRole('button', {name: 'Judge output funny'}), {key: 'Enter'});
  fireEvent.keyDown(screen.getByRole('button', {name: 'Funny input in'}), {key: ' '});
  fireEvent.keyDown(screen.getByRole('button', {name: 'Funny input in'}), {key: 'a'});
  expect(events.onConnect).toHaveBeenLastCalledWith('judge.funny', 'funny.in');
});

it('refuses a connection that already exists', () => {
  const events = handlers();
  render(<Editable document={j2} {...events} />);
  fireEvent.click(screen.getByRole('button', {name: 'Story output out'}));
  fireEvent.click(screen.getByRole('button', {name: 'Judge input in'}));
  expect(events.onConnect).not.toHaveBeenCalled();
});

it('shows a read-only preview with activation and message counts', () => {
  const activations = {story: 1, proposer: 2, reviewer: 2, result: 1};
  const messages = {'reviewer.revise -> proposer.in': 1};
  render(
    <div style={{width: '900px', height: '500px'}}>
      <GraphPreview document={j3} catalog={catalog} activations={activations} messages={messages} />
    </div>,
  );
  expect(screen.getByRole('region', {name: 'Run graph'})).toBeTruthy();
  expect(screen.queryByRole('button', {name: 'Story output out'})).toBeNull();
  expect(screen.getAllByTitle('Activations').map((badge) => badge.textContent)).toEqual([
    '1',
    '2',
    '2',
    '1',
  ]);
});
