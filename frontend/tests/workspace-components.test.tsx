import {afterEach, expect, it} from 'vitest';
import {cleanup} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import {WorkspaceForm, choose, click, setField} from './support/workspace-form.tsx';
import {configuration} from './support/configuration-data.ts';
import {numericSource} from './support/editor-view.tsx';
afterEach(cleanup);
it('resolves the registered LLM schema and applies a prompt as one raw value', async () => {
  const form = new WorkspaceForm(numericSource);
  await form.select('proposer');
  await form.apply('instructions', 'A new Ω prompt');
  form.expectPatch([
    {
      op: 'replace',
      path: '/components/proposer/config/instructions',
      value_json: '"A new Ω prompt"',
    },
  ]);
  expect(form.source).toContain('9007199254740993');
});
it('uses discovered model identities and exposes only supported reasoning choices', async () => {
  const form = new WorkspaceForm(numericSource.replace('illustrative-provider', 'deepseek-flash'));
  await form.select('model');
  await choose('Model provider profile', 'openai-luna');
  form.expectPatch([
    {op: 'add', path: '/components/model/config/provider_profile', value_json: '"openai-luna"'},
    {op: 'add', path: '/components/model/config/model', value_json: '"gpt-6-luna"'},
  ]);
  await form.select('proposer');
  expect(screen.getByLabelText<HTMLSelectElement>('Reasoning effort').options).toHaveLength(5);
  await choose('Reasoning effort', 'high');
  await click('Apply Reasoning effort');
  form.expectPatch([
    {
      op: 'add',
      path: '/components/proposer/config/parameters/reasoning_effort',
      value_json: '"high"',
    },
  ]);
});
it('binds managed children and resources without granting permissions', async () => {
  const form = new WorkspaceForm();
  await form.select('proposer');
  await choose('Resource slot worker', 'reviewer-worker');
  await click('Apply Resource slot worker');
  form.expectPatch([
    {op: 'replace', path: '/components/proposer/resources/worker', value_json: '"reviewer-worker"'},
  ]);
  await form.apply('proposer managed parent', '"reviewer"');
  form.expectPatch([
    {op: 'add', path: '/components/proposer/contained_by', value_json: '"reviewer"'},
  ]);
});
it('adds a named canonical external component and prevents a duplicate name', async () => {
  const form = new WorkspaceForm();
  setField('New component name', 'external/Ω');
  await choose('Registered component type', JSON.stringify(['example.resource-agent', '0.1.0']));
  await click('Add component instance');
  expect(form.patch.mock.calls[0]?.[0][0]).toMatchObject({
    op: 'add',
    path: '/components/external~1Ω',
  });
  setField('New component name', 'proposer');
  expect(
    screen.getByRole<HTMLButtonElement>('button', {name: 'Add component instance'}).disabled,
  ).toBe(true);
});
it('retains boolean, enum and opaque options of external allOf/reference schemas', async () => {
  const catalog = externalCatalog();
  const source =
    '{"components":{"custom":{"type_id":"external.type","type_version":"1","config":{"enabled":false,"mode":"a","opaque":1.0},"resources":{}}}}';
  const form = new WorkspaceForm(source, catalog);
  await click('Apply enabled');
  form.expectPatch([
    {op: 'replace', path: '/components/custom/config/enabled', value_json: 'false'},
  ]);
  await choose('mode', 'b');
  await click('Apply mode');
  await form.apply('opaque', '9007199254740993');
  form.expectPatch([
    {op: 'replace', path: '/components/custom/config/opaque', value_json: '9007199254740993'},
  ]);
});
it('reports malformed individual JSON without sending a patch', async () => {
  const form = new WorkspaceForm();
  await form.select('shared-memory');
  await form.apply('shared-memory configuration JSON and extensions', '{');
  expect(screen.getByRole('alert').textContent).toContain('valid JSON');
  expect(form.patch).not.toHaveBeenCalled();
});
it('keeps unreadable source editable through the JSON mode', () => {
  const form = new WorkspaceForm('{');
  expect(form.patch).not.toHaveBeenCalled();
  expect(screen.getByRole('status').textContent).toContain('Use the JSON editor');
  expect(screen.queryByLabelText('Component instance')).toBeNull();
});

function externalCatalog(): typeof configuration {
  const descriptor = {
    ...configuration.components[0],
    type_id: 'external.type',
    type_version: '1',
    roles: [],
    resource_slots: {},
    operations: {},
    installation_status: 'ready',
    config_schema: {$ref: 'urn:external'},
  };
  return {
    ...configuration,
    components: [descriptor],
    schema_documents: {
      'urn:external': {
        $defs: {
          options: {
            properties: {
              enabled: {type: 'boolean'},
              mode: {type: 'string', enum: ['a', 'b']},
              opaque: {oneOf: [{type: 'number'}]},
            },
          },
        },
        allOf: [{$ref: '#/$defs/options'}],
      },
    },
  };
}
