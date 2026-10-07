import {expect, it} from 'vitest';
import {
  activationBlock,
  activeText,
  canOfferActivation,
  pendingText,
  saveText,
  storedText,
} from '../src/features/editor/state/status.ts';
import type {Persistence} from '../src/features/editor/state/use-persistence.ts';
import {checked, error, rename, run, saved} from './support/editor-state.ts';

function persistence(fields: Partial<Persistence> = {}): Persistence {
  return {
    status: {kind: 'idle'},
    stored: {change: 27, at: '2026-10-04T10:42:00.000Z', revision: 0},
    versions: {active: 3, activeBranch: 'main', next: 4, head: 3, since: {version: 3}, pending: 2},
    activationFailure: null,
    target: {graphId: 'g', branch: 'main', exists: true},
    unsaved: false,
    flush: async () => Promise.resolve(true),
    activate: async () => Promise.resolve(),
    refreshVersions: async () => Promise.resolve(),
    ...fields,
  };
}

it('says whether the working copy is saved, saving or not saved', () => {
  expect(saveText(persistence())).toBe('Saved');
  expect(saveText(persistence({unsaved: true}))).toBe('Saving…');
  expect(saveText(persistence({status: {kind: 'saving'}}))).toBe('Saving…');
  const failed = persistence({status: {kind: 'failed', message: 'Offline.'}});
  expect(saveText(failed)).toBe('Not saved: Offline.');
  expect(storedText(persistence())).toMatch(/^Saved \d\d:\d\d · change 27$/u);
  expect(storedText(persistence({stored: null}))).toBe('Not saved yet');
});

const versions = (fields: Partial<Persistence['versions']>): Partial<Persistence> => ({
  versions: {...persistence().versions, ...fields},
});

it('counts the changes since the branch’s own head, or since where it started', () => {
  expect(pendingText(persistence())).toBe('2 changes since v3');
  expect(pendingText(persistence(versions({pending: 1})))).toBe('1 change since v3');
  expect(pendingText(persistence(versions({pending: 150})))).toBe('100+ changes since v3');
  expect(pendingText(persistence(versions({pending: 0})))).toBeNull();
  const started = versions({head: null, since: {change: 7}, pending: 1});
  expect(pendingText(persistence(started))).toBe('1 change since change 7');
  expect(pendingText(persistence(versions({head: null, since: null})))).toBe('not activated yet');
});

it('names the active version, and its branch when it is not the open one', () => {
  expect(activeText(persistence())).toBe('v3 · Active');
  const elsewhere = versions({activeBranch: 'Low temperature'});
  expect(activeText(persistence(elsewhere))).toBe('v3 · Active · Low temperature');
  expect(activeText(persistence(versions({active: null, activeBranch: null})))).toBe(
    'No active version',
  );
});

it('offers activation for changes not in the active version, once they check clean', () => {
  const clean = run(saved(), rename('Tale'), checked(1));
  expect(canOfferActivation(persistence())).toBe(true);
  expect(canOfferActivation(persistence(versions({pending: 0})))).toBe(false);
  expect(canOfferActivation(persistence({...versions({pending: 0}), unsaved: true}))).toBe(true);
  expect(canOfferActivation(persistence(versions({head: null, pending: 0})))).toBe(true);
  expect(canOfferActivation(persistence({stored: null}))).toBe(false);
  expect(activationBlock(clean, persistence())).toBeNull();
  expect(activationBlock(run(saved(), rename('Tale')), persistence())).toBe('Checking the graph…');
  expect(activationBlock(run(saved(), rename('Tale'), checked(1, [error])), persistence())).toBe(
    'Fix the problems in the graph before activating it.',
  );
  const offline = run(saved(), rename('Tale'), {type: 'check-failed', revision: 1, message: 'x'});
  expect(activationBlock(offline, persistence())).toBe('Could not check the graph: x');
  const failed = persistence({status: {kind: 'failed', message: 'x'}});
  expect(activationBlock(clean, failed)).toBe('Save the working copy first.');
});
