import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {ExecutionPanel, createExecutionModel} from '../src/features/execution/index.ts';
import type {GraphSummary} from '../src/api/index.ts';
import {graph} from './support/operator-data.ts';
import {OperatorServer} from './support/operator-server.ts';
import {tick} from './support/execution-view.tsx';
let server: OperatorServer;
beforeEach(() => {
  localStorage.clear();
  vi.useFakeTimers({toFake: ['setInterval', 'clearInterval']});
  server = new OperatorServer();
  vi.stubGlobal('fetch', server.fetch);
});
afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});
function view(input_schema: GraphSummary['input_schema']): void {
  render(
    <ExecutionPanel
      credential="key"
      graph={{...graph, ...(input_schema === undefined ? {} : {input_schema})}}
      onInspect={vi.fn()}
    />,
  );
}
function input(name: string | RegExp, value: string): void {
  fireEvent.change(screen.getByLabelText(name), {target: {value}});
}
function start(): HTMLButtonElement {
  return screen.getByRole('button', {name: 'Start run'});
}
it('collects typed primitive properties, rejects invalid values and omits untouched optional fields', async () => {
  view({
    type: 'object',
    properties: {
      count: {type: 'integer', minimum: 1, title: 'Count'},
      allowed: {type: 'boolean'},
      note: {type: 'string'},
      score: {type: 'number'},
    },
    required: ['count', 'allowed'],
    additionalProperties: false,
  });
  await tick();
  expect(start().disabled).toBe(true);
  input(/Count/, '1.5');
  await userEvent.selectOptions(screen.getByLabelText(/allowed/), 'true');
  expect(start().disabled).toBe(true);
  input(/Count/, '2');
  input('score', '0.75');
  await userEvent.click(start());
  expect(JSON.parse(server.mutations[0]?.body ?? '{}') as unknown).toMatchObject({
    input: {count: 2, allowed: true, score: 0.75},
  });
  expect(server.mutations[0]?.body).not.toContain('note');
  expect(JSON.stringify(localStorage)).not.toContain('count');
});
it('validates nested JSON input and sends the exact supported object', async () => {
  view({
    type: 'object',
    properties: {
      items: {
        type: 'array',
        items: {
          type: 'object',
          properties: {name: {type: 'string'}},
          required: ['name'],
          additionalProperties: false,
        },
      },
    },
    required: ['items'],
  });
  await tick();
  input('JSON input', '{');
  expect(start().disabled).toBe(true);
  expect(screen.getByText('Enter valid JSON input.')).toBeTruthy();
  input('JSON input', '{"items":[{}]}');
  expect(start().disabled).toBe(true);
  input('JSON input', '{"items":[{"name":"private"}]}');
  await userEvent.click(start());
  expect(JSON.parse(server.mutations[0]?.body ?? '{}') as unknown).toMatchObject({
    input: {items: [{name: 'private'}]},
  });
});
it.each([
  ['string', '"value"'],
  ['array', '[]'],
  ['null', 'null'],
])('rejects a root %s clearly without dispatching', async (type, value) => {
  view(type === 'array' ? {type, items: {type: 'string'}} : {type});
  await tick();
  input('JSON input', value);
  expect(screen.getByText('Run input must be a JSON object.')).toBeTruthy();
  expect(start().disabled).toBe(true);
  await userEvent.click(start());
  expect(server.mutations).toHaveLength(0);
});
it.each([
  {$ref: 'https://unavailable.invalid/schema'},
  {type: 'made-up'},
  {type: 'object', properties: {value: null}},
])('disables submission for unsupported schemas', async (schema) => {
  view(schema);
  await tick();
  expect(start().disabled).toBe(true);
  expect(screen.getByText(/Unsupported input schema/)).toBeTruthy();
  expect(server.mutations).toHaveLength(0);
});
it('validates command input independently of the rendered form', async () => {
  const model = createExecutionModel('key', localStorage);
  await model.polling.refresh(new AbortController().signal);
  await model.commands.start(
    {
      ...graph,
      input_schema: {
        type: 'object',
        properties: {required: {type: 'string'}},
        required: ['required'],
      },
    },
    {},
  );
  expect(server.mutations).toHaveLength(0);
});
it('resets input on revision change and keeps start disabled until the exact definition is available', async () => {
  const mounted = render(
    <ExecutionPanel credential="key" graph={graph} onInspect={vi.fn()} inputUnavailable />,
  );
  await tick();
  input(/Task or problem/, 'private');
  expect(start().disabled).toBe(true);
  mounted.rerender(
    <ExecutionPanel credential="key" graph={{...graph, revision: 'new'}} onInspect={vi.fn()} />,
  );
  expect(screen.getByLabelText<HTMLTextAreaElement>(/Task or problem/).value).toBe('');
});
