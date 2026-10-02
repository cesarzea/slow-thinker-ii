import {afterEach, expect, it, vi} from 'vitest';
import {cleanup} from '@testing-library/react';
import {DefinitionClient, DefinitionError} from '../src/api/index.ts';
import {EditorModelFixture, attemptLockedActions} from './support/editor-model.ts';
import {numericSource} from './support/editor-view.tsx';
const operations = [{op: 'add' as const, path: '/extension', value_json: '9007199254740993'}];
afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});
it('updates the authoritative source and clears old validation only after a confirmed patch', async () => {
  const patched = numericSource + '\n';
  const patch = vi.spyOn(DefinitionClient.prototype, 'patch').mockResolvedValue(patched);
  const fixture = new EditorModelFixture();
  await fixture.ready();
  await fixture.perform((model) => model.validate());
  await fixture.perform((model) => model.patch(operations));
  expect(patch).toHaveBeenCalledWith(numericSource, operations, expect.any(AbortSignal));
  expect(fixture.model.state.source).toBe(patched);
  expect(fixture.model.state.baseline).toBe(numericSource);
  expect(fixture.model.state.validation).toBeNull();
  expect(fixture.model.dirty).toBe(true);
});
it('locks conflicting actions while a patch is pending and ignores a late reply after unmount', async () => {
  const deferred = Promise.withResolvers<string>();
  const patch = vi.spyOn(DefinitionClient.prototype, 'patch').mockReturnValue(deferred.promise);
  const fixture = new EditorModelFixture();
  await fixture.ready();
  fixture.start((model) => model.patch(operations));
  await fixture.perform(attemptLockedActions);
  await fixture.perform((model) => model.patch(operations));
  expect(patch).toHaveBeenCalledTimes(1);
  expect(fixture.model.state.source).toBe(numericSource);
  fixture.hook.unmount();
  deferred.resolve('{}');
  await deferred.promise;
  expect(patch.mock.calls[0]?.[2].aborted).toBe(true);
});
it.each([
  new DefinitionError('invalid_patch'),
  new Error('lost'),
  'invalid failure',
  '{}'.repeat(600_000),
])('preserves the previous source on failed or oversized patch replies', async (failure) => {
  const patch = vi.spyOn(DefinitionClient.prototype, 'patch');
  if (typeof failure === 'string' && failure.length > 1_048_576) patch.mockResolvedValue(failure);
  else patch.mockRejectedValue(failure);
  const fixture = new EditorModelFixture();
  await fixture.ready();
  await fixture.perform((model) => model.patch(operations));
  expect(fixture.model.state.source).toBe(numericSource);
  expect(fixture.model.state.pending).toBeNull();
  expect(fixture.model.state.message).toBeTruthy();
});
it('does not begin a patch during a pending definition validation', async () => {
  const deferred = Promise.withResolvers<Awaited<ReturnType<DefinitionClient['validate']>>>();
  const patch = vi.spyOn(DefinitionClient.prototype, 'patch');
  const fixture = new EditorModelFixture();
  await fixture.ready();
  fixture.validate.mockReturnValue(deferred.promise);
  fixture.start((model) => model.validate());
  await fixture.perform((model) => model.patch(operations));
  expect(patch).not.toHaveBeenCalled();
  deferred.reject(new Error('cancelled'));
  await expect(deferred.promise).rejects.toThrow('cancelled');
});
