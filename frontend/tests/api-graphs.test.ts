import {afterEach, expect, it, vi} from 'vitest';
import {OperatorClient} from '../src/api/index.ts';
import {FakeApi} from './support/fake-api.ts';
import {j1} from './support/contract.ts';

afterEach(() => {
  vi.unstubAllGlobals();
});
const client = (): OperatorClient => new OperatorClient('operator-credential');
const at = '2026-10-04T05:00:00.000Z';
const path = '/graphs/funny-story';

it('lists the branches and starts one from a version or a change', async () => {
  const draft = {
    name: 'draft',
    created_at: at,
    from_version: 2,
    from_change: null,
    latest_change: 9,
    head_version: null,
  };
  const api = new FakeApi()
    .on(`GET ${path}/branches`, {status: 200, body: {branches: [draft]}})
    .on(`POST ${path}/branches`, {status: 201, body: {name: 'draft', change: 9}})
    .install();
  expect(await client().branches('funny-story')).toEqual([draft]);
  expect(await client().createBranch('funny-story', 'draft', {version: 2})).toEqual({
    name: 'draft',
    change: 9,
  });
  expect(api.last(`POST ${path}/branches`)?.body).toEqual({name: 'draft', from: {version: 2}});
  await client().createBranch('funny-story', 'other', {change: 4});
  expect(api.last(`POST ${path}/branches`)?.body).toEqual({name: 'other', from: {change: 4}});
});

it.each([201, 200])('saves a change answered with %s', async (status) => {
  const api = new FakeApi().on(`POST ${path}/changes`, {status, body: {change: 7, at}}).install();
  expect(await client().saveChange('funny-story', 'main', j1)).toEqual({change: 7, at});
  expect(api.last(`POST ${path}/changes`)?.body).toEqual({branch: 'main', document: j1});
});

it('lists changes by branch and page, and reads one', async () => {
  const summary = {change: 7, branch: 'main', at, name: 'Funny story', version: 2};
  const api = new FakeApi()
    .on(`GET ${path}/changes`, {status: 200, body: {changes: [summary]}})
    .on(`GET ${path}/changes/7`, {
      status: 200,
      body: {graph_id: 'funny-story', change: 7, branch: 'main', at, document: j1, version: 2},
    })
    .install();
  expect(await client().changes('funny-story')).toEqual([summary]);
  expect(api.last(`GET ${path}/changes`)?.query.toString()).toBe('');
  await client().changes('funny-story', {branch: 'main', before: 7, limit: 20});
  expect(api.last(`GET ${path}/changes`)?.query.toString()).toBe('branch=main&before=7&limit=20');
  expect((await client().change('funny-story', 7)).document).toEqual(j1);
});

it('activates a change as the next version', async () => {
  const api = new FakeApi()
    .on(`POST ${path}/versions`, {status: 201, body: {version: 3, branch: 'main', change: 7}})
    .install();
  expect(await client().activate('funny-story', 7)).toEqual({
    version: 3,
    branch: 'main',
    change: 7,
  });
  expect(api.last(`POST ${path}/versions`)?.body).toEqual({change: 7});
});
