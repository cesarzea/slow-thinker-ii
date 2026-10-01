import {afterEach, expect, it, vi} from 'vitest';
import {loadGraphs} from '../src/api/index.ts';

const example = {
  graph_id: 'review',
  revision: '1',
  participants: 2,
  nodes: [{id: 'draft', component: 'a'}],
};

afterEach(() => {
  vi.unstubAllGlobals();
});

it('validates the catalogue response', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify([example]))));
  expect(await loadGraphs(new AbortController().signal)).toEqual([example]);
});

it('rejects an HTTP failure', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('', {status: 503})));
  await expect(loadGraphs(new AbortController().signal)).rejects.toThrow('catalog');
});

it('rejects a malformed successful response', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('[{}]')));
  await expect(loadGraphs(new AbortController().signal)).rejects.toThrow();
});
