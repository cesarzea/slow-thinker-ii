import {expect, it} from 'vitest';
import type {Branch, VersionSummary} from '../src/api/index.ts';
import {laneGraph} from '../src/features/versions/lanes.ts';

const at = '2026-10-04T05:00:00.000Z';
const version = (number: number, branch: string, parent: number | null): VersionSummary => ({
  version: number,
  branch,
  parent,
  change: number * 2,
  name: 'Funny story',
  created_at: at,
});
const branch = (name: string): Branch => ({
  name,
  created_at: at,
  from_version: null,
  from_change: null,
  latest_change: 1,
  head_version: null,
});

it('lays versions out newest first on one lane per branch, forking from the parent', () => {
  const versions = [
    version(1, 'main', null),
    version(2, 'main', 1),
    version(3, 'draft', 1),
    version(4, 'main', 2),
  ];
  const graph = laneGraph(versions, [branch('main'), branch('draft')]);
  expect(graph.lanes).toEqual(['main', 'draft']);
  expect(
    graph.rows.map((row) => [row.version.version, row.lane, row.down, row.through, row.into]),
  ).toEqual([
    [4, 0, true, [], []],
    [3, 1, true, [0], []],
    [2, 0, true, [1], [0]],
    [1, 0, false, [], [0, 1]],
  ]);
});

it('starts a lane without a fork for a branch begun from a change', () => {
  const versions = [version(1, 'main', null), version(2, 'zeta', null), version(3, 'alpha', null)];
  const graph = laneGraph(versions, [branch('main')]);
  expect(graph.lanes).toEqual(['main', 'alpha', 'zeta']);
  expect(graph.rows.map((row) => [row.lane, row.down, row.into])).toEqual([
    [1, false, []],
    [2, false, []],
    [0, false, []],
  ]);
  expect(laneGraph([], [branch('main')])).toEqual({lanes: [], rows: []});
});
