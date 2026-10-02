import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, waitFor} from '@testing-library/react';
import {screen} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {SettingsView, settingsReceipt} from './support/settings-view.tsx';
import {errorReply} from './support/definition-api.ts';
import {configuration} from './support/configuration-data.ts';
import {ConfigurationSettings} from '../src/features/workspace/index.tsx';
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
it('changes duration/count/decimal budgets with only explicit fields under the captured revision', async () => {
  const fixture = new SettingsView();
  fixture.edit('Run deadline (seconds)', '50.5');
  fixture.edit('Maximum calls', '99');
  fixture.edit('Run budget (USD)', '0.000000001');
  await fixture.apply();
  expect(JSON.parse(fixture.bodies[0] ?? '{}')).toMatchObject({
    expected_revision: configuration.configuration_revision,
    limits: {run_seconds: 50.5, max_calls: 99, run_budget: '0.000000001'},
  });
  fixture.expectMessage('Settings confirmed under revision workspace-2');
  expect(fixture.refresh).toHaveBeenCalledOnce();
  expect(
    screen.getByLabelText<HTMLInputElement>('Run deadline (seconds)', {exact: false}).value,
  ).toBe('50.5');
});
it.each([
  ['invalid_limits', 422],
  ['configuration_conflict', 409],
  ['configuration_active', 409],
  ['budget_below_commitments', 422],
])('shows definitive %s without claiming a save', async (code, status) => {
  const fixture = new SettingsView();
  fixture.fetcher.mockResolvedValue(errorReply(code, status));
  fixture.edit('Run deadline (seconds)', '31');
  await fixture.apply();
  fixture.expectMessage(code);
  expect(fixture.refresh).not.toHaveBeenCalled();
  expect(screen.queryByRole('button', {name: 'Replay unchanged settings command'})).toBeNull();
});
it('freezes an uncertain command and replays exactly the same bytes', async () => {
  const fixture = new SettingsView();
  fixture.fetcher.mockImplementationOnce((_, init) => {
    if (typeof init?.body !== 'string') throw new Error('Missing exact command');
    fixture.bodies.push(init.body);
    return Promise.reject(new Error('lost'));
  });
  fixture.edit('Call deadline (seconds)', '15.5');
  await fixture.apply();
  fixture.expectMessage('unconfirmed');
  const field = screen.getByLabelText<HTMLInputElement>('Call deadline (seconds)', {exact: false});
  expect(field.closest('fieldset')?.disabled).toBe(true);
  await userEvent.click(screen.getByRole('button', {name: 'Replay unchanged settings command'}));
  expect(fixture.bodies).toHaveLength(2);
  expect(fixture.bodies[0]).toBe(fixture.bodies[1]);
  fixture.expectMessage('Settings confirmed');
});
it('locks while pending and ignores a reply after disconnect/unmount', async () => {
  const fixture = new SettingsView();
  const deferred = Promise.withResolvers<Response>();
  fixture.fetcher.mockReturnValue(deferred.promise);
  fixture.edit('Startup deadline (seconds)', '1');
  await fixture.apply();
  expect(
    screen.getByLabelText('Startup deadline (seconds)', {exact: false}).closest('fieldset')
      ?.disabled,
  ).toBe(true);
  const body = fixture.fetcher.mock.calls[0]?.[1]?.body;
  if (typeof body !== 'string') throw new Error('Missing exact command');
  const signal = fixture.fetcher.mock.calls[0]?.[1]?.signal;
  fixture.view.unmount();
  deferred.resolve(settingsReceipt(body));
  await deferred.promise;
  expect(signal?.aborted).toBe(true);
  expect(fixture.refresh).not.toHaveBeenCalled();
});
it('loads the latest discovered settings explicitly without discarding a pending command', async () => {
  const fixture = new SettingsView();
  fixture.edit('Run deadline (seconds)', '1');
  const catalog = {
    ...configuration,
    configuration_revision: 'external-revision',
    limits: {...configuration.limits, current: {...configuration.limits.current, run_seconds: 70}},
  };
  fixture.view.rerender(
    <ConfigurationSettings credential="key" catalog={catalog} refresh={fixture.refresh} />,
  );
  await userEvent.click(screen.getByRole('button', {name: 'Use latest server limits'}));
  expect(
    screen.getByLabelText<HTMLInputElement>('Run deadline (seconds)', {exact: false}).value,
  ).toBe('70');
  fixture.edit('Run deadline (seconds)', '65');
  await fixture.apply();
  await waitFor(() => {
    expect(fixture.refresh).toHaveBeenCalledOnce();
  });
  expect(JSON.parse(fixture.bodies[0] ?? '{}')).toMatchObject({
    expected_revision: 'external-revision',
  });
});
