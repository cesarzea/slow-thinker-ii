import {afterEach, expect, it} from 'vitest';
import {cleanup} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import {WorkspaceForm, choose, click, setField} from './support/workspace-form.tsx';
import bounded from '../../docs/contracts/examples/bounded-review.graph.json';
import collaboration from '../../docs/contracts/examples/resource-collaboration.graph.json';
afterEach(cleanup);
it('creates/removes declared nodes and patches component/operation/output fields', async () => {
  const form = new WorkspaceForm();
  setField('New node ID', 'new/Ω');
  await click('Add node');
  form.expectPatch([
    {op: 'add', path: '/nodes/new~1Ω', value_json: '{"component":"","operation":"","inputs":{}}'},
  ]);
  await choose('Node component', 'reviewer');
  await click('Apply Node component');
  form.expectPatch([{op: 'replace', path: '/nodes/draft/component', value_json: '"reviewer"'}]);
  await choose('Node operation', 'invoke');
  await click('Apply Node operation');
  await form.apply('Node output port', '"next"');
  form.expectPatch([{op: 'add', path: '/nodes/draft/output', value_json: '"next"'}]);
  await click('Remove node draft');
  form.expectPatch([{op: 'remove', path: '/nodes/draft'}]);
});
it('builds explicit run-input and latest-completed-node bindings', async () => {
  const form = new WorkspaceForm();
  setField('Input field', 'feedback/Ω');
  setField('JSON Pointer', '/value');
  await click('Apply input binding');
  form.expectPatch([
    {
      op: 'add',
      path: '/nodes/draft/inputs/feedback~1Ω',
      value_json: '{"source":"run_input","pointer":"/value"}',
    },
  ]);
  await choose('Input source', 'node_output');
  expect(
    screen.getByRole<HTMLButtonElement>('button', {name: 'Apply input binding'}).disabled,
  ).toBe(true);
  await choose('Source node', 'review');
  await click('Apply input binding');
  form.expectPatch([
    {
      op: 'add',
      path: '/nodes/draft/inputs/feedback~1Ω',
      value_json:
        '{"source":"node_output","node":"review","pointer":"/value","activation":"latest_completed"}',
    },
  ]);
});
it('reorders exact sequence tokens and retains endpoint controls', async () => {
  const form = new WorkspaceForm();
  expect(screen.getByRole<HTMLButtonElement>('button', {name: 'Move step 1 up'}).disabled).toBe(
    true,
  );
  await click('Move step 1 down');
  form.expectPatch([
    {op: 'replace', path: '/components/sequence/config/steps', value_json: '["review","draft"]'},
  ]);
  await click('Move step 2 up');
  form.expectPatch([
    {op: 'replace', path: '/components/sequence/config/steps', value_json: '["review","draft"]'},
  ]);
  await form.apply('Sequence node order', '["draft","review"]');
});
it('edits conditional entry, activation limits and existing selected-port routes', async () => {
  const form = new WorkspaceForm(JSON.stringify(bounded));
  await form.apply('Entry node', '"review"');
  await form.apply('Maximum activations', '7');
  setField('Route source node', 'review');
  setField('Selected output port', 'accept');
  await click('Apply conditional route');
  form.expectPatch([
    {op: 'add', path: '/components/flow/config/routes/review/accept', value_json: 'null'},
  ]);
  setField('Target node (empty exits)', 'propose');
  await click('Apply conditional route');
  form.expectPatch([
    {op: 'add', path: '/components/flow/config/routes/review/accept', value_json: '"propose"'},
  ]);
});
it('creates missing route parents atomically in incomplete drafts', async () => {
  const source =
    '{"execution_profile":"bounded-conditional","controller":{"component":"flow"},"components":{"flow":{"config":{"entry":"n"}}},"nodes":{"n":{"inputs":{}}}}';
  const form = new WorkspaceForm(source);
  setField('Route source node', 'n/1');
  setField('Selected output port', 'yes');
  await click('Apply conditional route');
  expect(form.patch.mock.calls[0]?.[0]).toEqual([
    {op: 'add', path: '/components/flow/config/routes', value_json: '{}'},
    {op: 'add', path: '/components/flow/config/routes/n~11', value_json: '{}'},
    {op: 'add', path: '/components/flow/config/routes/n~11/yes', value_json: 'null'},
  ]);
});
it('grants permissions only through the deliberate grant action', async () => {
  const form = new WorkspaceForm();
  setField('Authorized caller', 'proposer');
  setField('Authorized target', 'calculator');
  setField('Authorized operation', 'calculate');
  await click('Grant declared operation');
  form.expectPatch([
    {
      op: 'add',
      path: '/permissions/-',
      value_json: '{"caller":"proposer","target":"calculator","operations":["calculate"]}',
    },
  ]);
});
it('creates a missing permissions array only through a grant', async () => {
  const form = new WorkspaceForm('{"components":{}}');
  setField('Authorized caller', 'a');
  setField('Authorized target', 'b');
  setField('Authorized operation', 'invoke');
  await click('Grant declared operation');
  form.expectPatch([
    {
      op: 'add',
      path: '/permissions',
      value_json: '[{"caller":"a","target":"b","operations":["invoke"]}]',
    },
  ]);
  expect(screen.getByRole<HTMLButtonElement>('button', {name: 'Add node'}).disabled).toBe(true);
});
it('keeps supported profile choice and graph extension fields on the same patch path', async () => {
  const form = new WorkspaceForm();
  await choose('Execution profile', 'bounded-conditional');
  form.expectPatch([{op: 'add', path: '/execution_profile', value_json: '"bounded-conditional"'}]);
  await form.apply('Run input schema', JSON.stringify(collaboration.input_schema));
  await form.apply('Controller component and operation', '{"component":"flow","operation":"next"}');
  await form.apply(
    'Final result binding',
    '{"source":"node_output","node":"review","activation":"latest_completed","pointer":""}',
  );
});
