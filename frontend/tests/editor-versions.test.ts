import {expect, it} from 'vitest';
import type {ChangeSummary, GraphDetail} from '../src/api/index.ts';
import {afterActivation, afterSave, versionState} from '../src/features/editor/state/versions.ts';

const AT = '2026-10-04T10:42:00.000Z';
const LOW = 'Low temperature';
const branch = (name: string, fields: Partial<GraphDetail['branches'][number]>) => ({
  name,
  created_at: AT,
  from_version: null,
  from_change: null,
  latest_change: 1,
  head_version: null,
  ...fields,
});
const version = (number: number, on: string, change: number) => ({
  version: number,
  branch: on,
  parent: null,
  change,
  name: 'Funny story',
  created_at: AT,
});
const change = (number: number, on: string): ChangeSummary => ({
  change: number,
  branch: on,
  at: AT,
  name: 'Funny story',
  version: null,
});

/** v1 and v2 on main; “Low temperature” started from v1 and was activated as v3. */
const detail: GraphDetail = {
  id: 'funny-story',
  name: 'Funny story',
  active_version: 3,
  latest_change: 6,
  branches: [
    branch('main', {latest_change: 4, head_version: 2}),
    branch(LOW, {from_version: 1, latest_change: 6, head_version: 3}),
    branch('Fresh', {from_version: 2, latest_change: 8}),
    branch('Scratch', {from_change: 5, latest_change: 9}),
  ],
  versions: [version(1, 'main', 1), version(2, 'main', 4), version(3, LOW, 6)],
};

it('compares main with its own head when the active version is on another branch', () => {
  const main = [change(4, 'main'), change(3, 'main'), change(2, 'main'), change(1, 'main')];
  expect(versionState(detail, 'main', main)).toEqual({
    active: 3,
    activeBranch: LOW,
    next: 4,
    head: 2,
    since: {version: 2},
    pending: 0,
  });
  const edited = versionState(detail, 'main', [change(10, 'main'), ...main]);
  expect([edited.since, edited.pending]).toEqual([{version: 2}, 1]);
});

it('compares a branch without a version with where it started, not its first change', () => {
  const fresh = versionState(detail, 'Fresh', [change(11, 'Fresh'), change(8, 'Fresh')]);
  expect([fresh.head, fresh.since, fresh.pending]).toEqual([null, {version: 2}, 1]);
  const scratch = versionState(detail, 'Scratch', [change(9, 'Scratch')]);
  expect([scratch.since, scratch.pending]).toEqual([{change: 5}, 0]);
  const empty = {...detail, branches: [], versions: [], active_version: null};
  expect(versionState(empty, 'main', [change(1, 'main')])).toMatchObject({
    active: null,
    activeBranch: null,
    next: 1,
    since: null,
    pending: 1,
  });
});

it('counts new changes and makes an activation the branch’s head and the active version', () => {
  const main = versionState(detail, 'main', [change(4, 'main')]);
  expect(afterSave(main, 4, 4)).toBe(main);
  expect(afterSave(main, 4, 12).pending).toBe(1);
  expect(afterActivation(main, {version: 4, branch: 'main', change: 12})).toEqual({
    active: 4,
    activeBranch: 'main',
    next: 5,
    head: 4,
    since: {version: 4},
    pending: 0,
  });
});
