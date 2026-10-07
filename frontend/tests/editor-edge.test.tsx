import type {ReactElement} from 'react';
import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen} from '@testing-library/react';
import {Position, ReactFlowProvider} from '@xyflow/react';
import type {EdgeProps} from '@xyflow/react';
import {RouteEdge} from '../src/features/editor/canvas/route-edge.tsx';
import type {EdgeRoute} from '../src/features/editor/canvas/routing/edge-routes.ts';
import {RoutesContext} from '../src/features/editor/canvas/routing/use-routes.ts';
import type {RouteEdgeType} from '../src/features/editor/canvas/types.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const data = {from: 'a.out', to: 'b.in', route: 'A · out to B · in'};

function Edge(props: {readonly routes: ReadonlyMap<string, EdgeRoute>}): ReactElement {
  const edgeProps = {
    id: 'e',
    source: 'a',
    target: 'b',
    sourceX: 300,
    sourceY: 100,
    targetX: 40,
    targetY: 100,
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
    data,
    label: '3',
  } as unknown as EdgeProps<RouteEdgeType>;
  return (
    <ReactFlowProvider>
      <RoutesContext value={props.routes}>
        <svg>
          <RouteEdge {...edgeProps} />
        </svg>
      </RoutesContext>
    </ReactFlowProvider>
  );
}

const path = (): string | null =>
  document.querySelector('.react-flow__edge-path')?.getAttribute('d') ?? null;

it('draws a curve between the handles until the canvas has routed the connection', () => {
  render(<Edge routes={new Map()} />);
  expect(path()).toMatch(/^M300,100 C/u);
});

it('draws the route the canvas found, with its message count at the route’s middle', () => {
  const route = {
    path: 'M 300,100 L 330,100 L 330,200 L 40,200',
    points: [
      {x: 300, y: 100},
      {x: 330, y: 100},
      {x: 330, y: 200},
      {x: 40, y: 200},
    ],
    guide: [],
    middle: {x: 330, y: 150},
  };
  render(<Edge routes={new Map([['e', {route, label: null}]])} />);
  expect(path()).toBe('M 300,100 L 330,100 L 330,200 L 40,200');
  // The count is centred on the route's middle; jsdom measures it as 12 by 12.
  expect(screen.getByText('3').closest('g')?.getAttribute('transform')).toBe('translate(324 144)');
});
