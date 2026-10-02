import {afterEach, expect, it} from 'vitest';
import {cleanup} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import {WorkspaceForm, choose} from './support/workspace-form.tsx';
import {configuration} from './support/configuration-data.ts';
import {numericSource} from './support/editor-view.tsx';
afterEach(cleanup);
it('locks temperature when the chosen profile cannot accept it or reasoning is active', async () => {
  const form = new WorkspaceForm(
    numericSource
      .replace('illustrative-provider', 'deepseek-flash')
      .replace('"temperature":1.0', '"reasoning_effort":"high","temperature":1.0'),
  );
  await form.select('proposer');
  expect(screen.getByLabelText<HTMLTextAreaElement>('Temperature').disabled).toBe(true);
  form.view.unmount();
  const unsupported = new WorkspaceForm(
    numericSource.replace('illustrative-provider', 'openai-luna'),
  );
  await unsupported.select('proposer');
  expect(screen.getByLabelText<HTMLSelectElement>('Reasoning effort').options).toHaveLength(2);
  expect(screen.getByLabelText<HTMLTextAreaElement>('Temperature').disabled).toBe(true);
});
it('explains missing profile/parameters and accepts temperature only without active reasoning', async () => {
  const missing = new WorkspaceForm(numericSource, {...configuration, models: []});
  await missing.select('proposer');
  expect(screen.getByText(/Bound model: No discovered model profile/)).toBeTruthy();
  expect(screen.getByLabelText<HTMLTextAreaElement>('Reasoning effort').disabled).toBe(true);
  missing.view.unmount();
  const form = new WorkspaceForm(numericSource.replace('illustrative-provider', 'deepseek-flash'));
  await form.select('proposer');
  expect(screen.getByLabelText<HTMLTextAreaElement>('Temperature').disabled).toBe(false);
});
it('keeps a generic JSON configuration path when no descriptor/config is present', async () => {
  const form = new WorkspaceForm(
    '{"components":{"custom":{"type_id":"unknown","type_version":"1"}},"nodes":{}}',
    null,
  );
  expect(screen.getByText('Not registered', {exact: false})).toBeTruthy();
  await form.apply('custom configuration JSON and extensions', '{"new":1.0}');
  form.expectPatch([{op: 'add', path: '/components/custom/config', value_json: '{"new":1.0}'}]);
});
it('does not create a component before a registered ready type is selected', async () => {
  const descriptor = configuration.components[0];
  if (descriptor === undefined) throw new Error('Missing canonical descriptor');
  const form = new WorkspaceForm('{"components":{},"nodes":{}}', {
    ...configuration,
    components: [{...descriptor, installation_status: 'unavailable'}],
  });
  const choice = screen.getByLabelText<HTMLSelectElement>('Registered component type');
  expect(choice.options[1]?.disabled).toBe(true);
  expect(
    screen.getByRole<HTMLButtonElement>('button', {name: 'Add component instance'}).disabled,
  ).toBe(true);
  await choose('Registered component type', '');
  expect(form.patch).not.toHaveBeenCalled();
});
