import type * as ReactFlowModule from '@xyflow/react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {GraphView} from '../src/features/graph-view/index.ts';
import {boundedDetail, repeatedPage, singleDetail, summary} from './support/projection-data.ts';
vi.mock('@xyflow/react', async (original) => {
  const {Canvas, Empty, EdgeFrame} = await import('./support/graph-canvas.tsx');
  return {
    ...(await original<typeof ReactFlowModule>()),
    ReactFlow: Canvas,
    Background: Empty,
    Controls: Empty,
    Handle: Empty,
    BaseEdge: EdgeFrame,
  };
});
afterEach(cleanup);
it('renders a single AI card, entry and exit arrows and resources outside the canvas', () => {
  render(<GraphView graph={summary(singleDetail)} detail={singleDetail} />);
  const canvas = within(screen.getByLabelText('Test canvas'));
  expect(canvas.getByRole('img', {name: 'AI agent'})).toBeTruthy();
  expect(canvas.getByText('LLMCall')).toBeTruthy();
  expect(canvas.getByText('Proposer')).toBeTruthy();
  expect(canvas.getByText('next')).toBeTruthy();
  expect(canvas.getAllByTestId('entry:draft')).toHaveLength(2);
  expect(canvas.queryByText('model')).toBeNull();
  expect(canvas.queryByRole('button', {name: /terminal|activation|controller/i})).toBeNull();
  expect(within(screen.getByRole('region', {name: 'Resources'})).getByText('model')).toBeTruthy();
  expect(screen.queryByRole('img', {name: 'System mediation'})).toBeNull();
  expect(screen.queryByText('Reasoning effort')).toBeNull();
});
it('shows inline configuration and symbolic noninteractive midpoint and endpoint circles', async () => {
  render(<GraphView graph={summary(singleDetail)} detail={singleDetail} />);
  await userEvent.click(screen.getByLabelText('Show configuration'));
  expect(screen.getByText('illustrative-model')).toBeTruthy();
  expect(screen.getByText('Not specified')).toBeTruthy();
  await userEvent.click(screen.getByLabelText('Show system elements'));
  const markers = screen.getAllByRole('img', {name: 'System mediation'});
  expect(markers.flatMap((marker) => [...marker.querySelectorAll('circle')])).toHaveLength(3);
  expect(markers.every((marker) => marker.closest('button') === null)).toBe(true);
  await userEvent.click(screen.getByLabelText('Show configuration'));
  expect(screen.queryByText('Reasoning effort')).toBeNull();
  await userEvent.click(screen.getByLabelText('Show system elements'));
  expect(screen.queryByRole('img', {name: 'System mediation'})).toBeNull();
});
it('keeps repeated activations on their declared steps and selects exact evidence by keyboard', async () => {
  const select = vi.fn();
  render(
    <GraphView
      graph={summary(boundedDetail)}
      detail={boundedDetail}
      execution={repeatedPage}
      onSelect={select}
    />,
  );
  expect(screen.getAllByRole('img', {name: 'AI agent'})).toHaveLength(2);
  expect(screen.getByText('running · 2 recorded activations')).toBeTruthy();
  await userEvent.click(screen.getByText('Explore graph and evidence'));
  const chosen = screen.getByRole('button', {name: 'Activation #3: propose'});
  chosen.focus();
  await userEvent.keyboard('{Enter}');
  expect(select).toHaveBeenLastCalledWith({kind: 'activation', id: 'draft-two'});
  await userEvent.click(screen.getByRole('button', {name: 'Call worker-call'}));
  expect(select).toHaveBeenLastCalledWith({kind: 'call', id: 'worker-call'});
  await userEvent.click(screen.getByRole('button', {name: 'Component review-worker'}));
  expect(select).toHaveBeenLastCalledWith({kind: 'component', id: 'review-worker'});
  await userEvent.click(screen.getByRole('button', {name: 'Step review'}));
  expect(select).toHaveBeenLastCalledWith({kind: 'node', id: 'review'});
  await userEvent.click(screen.getByRole('button', {name: 'Structure'}));
  expect(screen.queryByText('running · 2 recorded activations')).toBeNull();
  expect(screen.getByRole('button', {name: 'Call worker-call'})).toBeTruthy();
});
it('preserves dragged positions through polling and resets only when reorganized', async () => {
  const props = {graph: summary(boundedDetail), detail: boundedDetail, execution: repeatedPage};
  const mounted = render(<GraphView {...props} />);
  await userEvent.click(screen.getByRole('button', {name: 'Move node:propose'}));
  mounted.rerender(<GraphView {...props} execution={{...repeatedPage, calls: []}} />);
  expect(screen.getByTestId('node:propose').getAttribute('data-position')).toBe('800,900');
  await userEvent.click(screen.getByRole('button', {name: 'Reorganize graph'}));
  expect(screen.getByTestId('node:propose').getAttribute('data-position')).toBe('0,60');
});
it('distinguishes missing detail, missing execution and recorded empty evidence', async () => {
  const graph = summary(singleDetail);
  const mounted = render(<GraphView graph={graph} />);
  expect(screen.getByText(/Detailed structure unavailable/)).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Execution'}));
  expect(screen.getByText('No recorded activations available.')).toBeTruthy();
  mounted.rerender(
    <GraphView
      graph={graph}
      detail={singleDetail}
      execution={{...repeatedPage, activations: [], calls: []}}
    />,
  );
  expect(screen.queryByText(/Detailed structure unavailable/)).toBeNull();
  expect(screen.getByText('No recorded activations')).toBeTruthy();
  await userEvent.click(screen.getByText('Explore graph and evidence'));
  expect(screen.getByText('No recorded activations.')).toBeTruthy();
  expect(screen.getByText('No observed communications.')).toBeTruthy();
});
