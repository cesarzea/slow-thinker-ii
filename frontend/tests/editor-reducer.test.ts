import {expect, it} from 'vitest';
import {editorReducer} from '../src/features/editor/state/editor-state.ts';
import {renameNode} from '../src/features/editor/state/document.ts';
import {declaration, j1} from './support/contract.ts';
import {checked, error, keep, rename, run, saved, warning} from './support/editor-state.ts';

it('tracks changes and selection, and ignores changes that change nothing', () => {
  const choose = {type: 'select', nodeId: 'proposer'} as const;
  const state = run(saved(), choose, {
    type: 'change',
    update: (document) => renameNode(document, 'proposer', 'Writer'),
  });
  expect([state.revision, state.selected, state.past]).toEqual([1, 'proposer', [j1]]);
  expect(run(state, keep)).toBe(state);
  const removed = run(state, {type: 'change', update: (document) => ({...document, nodes: []})});
  expect(removed.selected).toBeNull();
  const select = {
    type: 'change',
    update: (document: typeof j1) => document,
    select: 'story',
  } as const;
  expect(run(state, select).selected).toBe('story');
});

it('adds a node where it is dropped, or at a free position, and selects it', () => {
  const state = run(saved(), {type: 'add', declaration: declaration('router')});
  expect(state.selected).toBe('router');
  expect(state.document.layout?.['router']).toEqual([850, 40]);
  const dropped = run(saved(), {type: 'add', declaration: declaration('router'), position: [5, 7]});
  expect(dropped.document.layout?.['router']).toEqual([5, 7]);
});

it('undoes and redoes this session’s changes, and a new change ends the redo', () => {
  const edited = run(saved(), rename('Tale'), rename('Story time'));
  const undone = run(edited, {type: 'undo'}, {type: 'undo'});
  expect([undone.document, undone.revision, undone.future.length]).toEqual([j1, 4, 2]);
  expect(run(undone, {type: 'undo'})).toBe(undone);
  const redone = run(undone, {type: 'redo'});
  expect(redone.document.nodes[0]?.name).toBe('Tale');
  expect(run(redone, rename('Other')).future).toEqual([]);
  expect(run(edited, {type: 'redo'})).toBe(edited);
  const long = Array.from({length: 120}, (_, index) => rename(`Name ${String(index)}`));
  expect(run(saved(), ...long).past).toHaveLength(100);
});

it('replaces the working copy as an undoable change', () => {
  const other = renameNode(j1, 'story', 'Restored');
  const replaced = editorReducer(run(saved(), {type: 'select', nodeId: 'story'}), {
    type: 'replace',
    document: other,
  });
  expect([replaced.document, replaced.past, replaced.selected]).toEqual([other, [j1], 'story']);
});

it('keeps diagnostics only for the revision they were computed for', () => {
  const changed = run(saved(), rename('Tale'));
  expect(run(changed, checked(0, [error])).diagnostics).toEqual([]);
  const current = run(changed, checked(1, [error]));
  expect(current.checked).toBe(1);
  expect(run(current, {type: 'check-failed', revision: 0, message: 'x'}).checkFailure).toBeNull();
  const offline = run(current, {type: 'check-failed', revision: 1, message: 'Offline'});
  expect(offline.checkFailure).toBe('Offline');
  const applied = run(current, {type: 'applied', document: j1, diagnostics: [warning]});
  expect([applied.revision, applied.checked, applied.diagnostics]).toEqual([2, 2, [warning]]);
});

it('undoes into the branch’s saved changes only after this session’s edits', () => {
  const earlier = {...j1, name: 'Earlier'};
  const seeded = run(saved(), {type: 'seed', changes: [3, 4]});
  expect(seeded.saved).toEqual([3, 4]);
  const stale = run(seeded, {type: 'undo-saved', change: 3, document: earlier});
  expect(stale).toBe(seeded);
  const undone = run(seeded, {type: 'undo-saved', change: 4, document: earlier});
  expect([undone.document.name, undone.saved, undone.future]).toEqual(['Earlier', [3], [j1]]);
  const edited = run(seeded, rename('Other'));
  expect(run(edited, {type: 'undo-saved', change: 4, document: earlier})).toBe(edited);
});
