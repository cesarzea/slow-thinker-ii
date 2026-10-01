import type * as ReactFlowModule from '@xyflow/react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {GraphView} from '../src/features/graph-view/index.ts';
import {singleDetail, summary} from './support/projection-data.ts';
import type {GraphDetail} from '../src/api/index.ts';
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
it('renders the saved model and enforced effort instead of illustrative graph configuration', async () => {
  const detail: GraphDetail = {
    ...singleDetail,
    execution: {
      instances: {
        proposer: {config: {parameters: {reasoning_effort: 'high'}, token: 'do-not-show'}},
        model: {config: {model: 'actual-model'}, operations: [operation('complete', 'none')]},
      },
    },
  };
  await show(detail);
  expect(screen.getByText('actual-model')).toBeTruthy();
  expect(screen.getByText('none')).toBeTruthy();
  expect(screen.getAllByText('Saved configuration')).toHaveLength(2);
  expect(screen.queryByText('illustrative-model')).toBeNull();
  expect(screen.queryByText('do-not-show')).toBeNull();
});
it('retains generic extension labels and safely handles malformed optional metadata', async () => {
  const detail: GraphDetail = {
    ...singleDetail,
    execution: {instances: {model: {config: []}}},
    structure: {
      ...singleDetail.structure,
      components: singleDetail.structure.components.map((item) =>
        item.id === 'proposer' ? {...item, type_id: 'custom.review'} : item,
      ),
    },
    definition: {...singleDetail.definition, components: {proposer: {type_id: 'custom.review'}}},
  };
  await show(detail);
  expect(screen.getByRole('img', {name: 'Component'})).toBeTruthy();
  expect(screen.getByText('custom.review')).toBeTruthy();
  expect(screen.getByText('Unavailable')).toBeTruthy();
  expect(screen.getByText('Not specified')).toBeTruthy();
});
async function show(detail: GraphDetail): Promise<void> {
  render(<GraphView graph={summary(detail)} detail={detail} />);
  await userEvent.click(screen.getByLabelText('Show configuration'));
}
function operation(name: string, effort: string): GraphDetail['definition'] {
  return {
    name,
    input_schema: {properties: {request: {properties: {reasoning_effort: {const: effort}}}}},
  };
}
