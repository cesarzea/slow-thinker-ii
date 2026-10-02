import {afterEach, expect, it} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import {
  ComponentInventory,
  ConfigurationSettings,
  ResourceInventory,
} from '../src/features/workspace/index.tsx';
import {configuration} from './support/configuration-data.ts';
import {singleDetail, executionPage} from './support/projection-data.ts';
const source = JSON.stringify({
  components: {
    shared: {
      type_id: 'key-value-memory',
      type_version: '0.1.0',
      config: {retention: 'persistent', namespace: 'research'},
    },
    private: {type_id: 'calculator', type_version: '0.1.0', config: {}},
    unused: {
      type_id: 'model-provider',
      type_version: '0.1.0',
      config: {provider_profile: 'deepseek-flash'},
    },
    a: {resources: {memory: 'shared', calculator: 'private'}},
    b: {resources: {memory: 'shared'}},
  },
});
afterEach(cleanup);
it('distinguishes private, shared and unbound declared instances without inferring authority', () => {
  render(
    <ResourceInventory
      source={source}
      catalog={configuration}
      detail={null}
      execution={null}
      run={null}
    />,
  );
  const resources = within(screen.getByRole('region', {name: 'Experiment resource inventory'}));
  expect(resources.getByText(/Shared by selected consumers/).textContent).toContain('a, b');
  expect(resources.getByText(/One bound consumer/).textContent).toContain('a');
  expect(resources.getByText(/Unbound instance/).textContent).toContain('No consumers');
  expect(resources.getByText('Retention: persistent')).toBeTruthy();
  expect(resources.getByText('Namespace: research')).toBeTruthy();
  expect(resources.getByText('Model profile: deepseek-flash')).toBeTruthy();
  expect(resources.getByText(/Binding grants no authority/)).toBeTruthy();
  expect(resources.getByText(/Select a saved run/)).toBeTruthy();
});
it('uses the admitted resource roles for recorded activity despite different draft bindings', () => {
  const original = executionPage.calls[0];
  if (original === undefined) throw new Error('Missing admitted call');
  const execution = {
    ...executionPage,
    calls: [...executionPage.calls, {...original, id: 'draft-only', target: 'shared'}],
  };
  render(
    <ResourceInventory
      source={source}
      catalog={configuration}
      detail={null}
      activityDetail={singleDetail}
      execution={execution}
      run="run"
    />,
  );
  const activity = within(screen.getByRole('region', {name: 'Recorded resource activity'}));
  expect(activity.getByText(/child: proposer → model.complete/)).toBeTruthy();
  expect(activity.queryByText(/draft-only/)).toBeNull();
});
it('uses exact detail roles when discovery is missing and reports empty recorded snapshots', () => {
  const view = render(
    <ResourceInventory
      source={JSON.stringify(singleDetail.definition)}
      catalog={null}
      detail={singleDetail}
      execution={executionPage}
      run="run"
    />,
  );
  expect(screen.getByRole('heading', {name: 'model'})).toBeTruthy();
  expect(screen.getByText(/No resource calls are recorded/)).toBeTruthy();
  view.rerender(
    <ResourceInventory source="{" catalog={null} detail={null} execution={null} run={null} />,
  );
  expect(screen.getByText(/No configured resource instances/)).toBeTruthy();
});
it('shows trustworthy empty discovery states without inventing installed types or models', () => {
  const view = render(<ComponentInventory catalog={null} />);
  expect(screen.getByText(/Connect and load configuration/)).toBeTruthy();
  const empty = {...configuration, components: [], models: []};
  view.rerender(
    <>
      <ComponentInventory catalog={empty} />
      <ConfigurationSettings credential="key" catalog={empty} refresh={() => undefined} />
    </>,
  );
  expect(screen.getByText('No component types are registered.')).toBeTruthy();
  expect(screen.getByText('No model profiles are configured.')).toBeTruthy();
});
it('reports unavailable installations and capability details from discovery', () => {
  const catalog = unavailableCatalog();
  render(
    <>
      <ComponentInventory catalog={catalog} />
      <ConfigurationSettings credential="key" catalog={catalog} refresh={() => undefined} />
    </>,
  );
  expect(screen.getByRole('cell', {name: 'unavailable'})).toBeTruthy();
  expect(screen.getByText('No roles reported')).toBeTruthy();
  expect(screen.getByText('No operations reported')).toBeTruthy();
  expect(screen.getByText('Reasoning: No reasoning options reported')).toBeTruthy();
  expect(screen.getByText('Reviewed until Unavailable')).toBeTruthy();
  expect(screen.getByText('Temperature: Unsupported')).toBeTruthy();
});

function unavailableCatalog(): typeof configuration {
  const first = configuration.models[0];
  if (first === undefined) throw new Error('Missing discovered model');
  return {
    ...configuration,
    components: [
      {
        type_id: 'external',
        type_version: '1',
        roles: [],
        config_schema: {},
        resource_slots: {},
        operations: {},
        installation_status: 'unavailable',
      },
    ],
    models: [
      {...first, review_expires_at: 1e20, reasoning_efforts: [], supports_temperature: false},
    ],
  };
}
