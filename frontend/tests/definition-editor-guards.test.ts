import {afterEach, expect, it, vi} from 'vitest';
import {act, cleanup} from '@testing-library/react';
import type {SaveResult} from '../src/api/index.ts';
import {EditorModelFixture, attemptLockedActions} from './support/editor-model.ts';
import {draftText, numericSource, personalReference} from './support/editor-view.tsx';

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

it('rejects authoring action callbacks while source loading and saving without validation', async () => {
  const fixture = new EditorModelFixture();
  await fixture.perform(attemptLockedActions);
  expect(fixture.validate).not.toHaveBeenCalled();
  expect(fixture.save).not.toHaveBeenCalled();
  expect(fixture.draft).not.toHaveBeenCalled();
  await fixture.ready();
  await fixture.perform(async (model) => {
    await model.save();
    await model.retry();
  });
  expect(fixture.save).not.toHaveBeenCalled();
  expect(fixture.model.state.source).toBe(numericSource);
});

it('retains the frozen save under concurrent authoring callbacks', async () => {
  const fixture = new EditorModelFixture();
  await fixture.ready();
  await fixture.perform((model) => {
    model.edit(draftText());
  });
  await fixture.perform((model) => model.validate());
  const reply = Promise.withResolvers<SaveResult>();
  fixture.save.mockReturnValue(reply.promise);
  fixture.start((model) => model.save());
  await fixture.perform(attemptLockedActions);
  expect(fixture.model.state.source).toBe(draftText());
  expect(fixture.model.state.pending).toBe('save');
  expect(fixture.save).toHaveBeenCalledTimes(1);
  expect(fixture.validate).toHaveBeenCalledTimes(1);
  expect(fixture.draft).not.toHaveBeenCalled();
  await act(async () => {
    reply.resolve({...personalReference, created: true});
    await reply.promise;
  });
  expect(fixture.model.state.source).toBe(numericSource);
});

it('retains the pending derivation under concurrent authoring callbacks', async () => {
  const fixture = new EditorModelFixture();
  await fixture.ready();
  const reply = Promise.withResolvers<string>();
  fixture.draft.mockReturnValue(reply.promise);
  fixture.start((model) => model.derive('single-agent', 'personal-1'));
  await fixture.perform(attemptLockedActions);
  expect(fixture.model.state.pending).toBe('draft');
  expect(fixture.model.state.source).toBe(numericSource);
  expect(fixture.draft).toHaveBeenCalledTimes(1);
  expect(fixture.save).not.toHaveBeenCalled();
  await act(async () => {
    reply.resolve(draftText());
    await reply.promise;
  });
  expect(fixture.model.state.source).toBe(draftText());
});

it('rejects a concurrent revision request when a dirty draft exists', async () => {
  const fixture = new EditorModelFixture();
  await fixture.ready();
  await fixture.perform((model) => {
    model.edit(draftText());
  });
  await fixture.perform((model) => model.derive('manual-variant', 'ignored'));
  expect(fixture.draft).not.toHaveBeenCalled();
  expect(fixture.model.state.source).toBe(draftText());
});
