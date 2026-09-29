import {afterEach, expect, it, vi} from 'vitest';
import {OperatorClient} from '../src/api/index.ts';
import {boundedDetail} from './support/projection-data.ts';
import {reply} from './support/operator-data.ts';
const component = {
  id: 'extra',
  type_id: 'worker',
  type_version: '1',
  roles: [],
  contained_by: null,
};
const node = {id: 'missing', component: 'unknown'};
const edge = {id: 'edge', kind: 'control', source: 'absent', target: 'review', label: 'next'};
afterEach(() => {
  vi.unstubAllGlobals();
});

it.each([
  {components: [component, component]},
  {nodes: [node, node]},
  {nodes: [node]},
  {edges: [edge, edge]},
  {edges: [edge]},
  {edges: [{...edge, source: 'review', target: 'absent'}]},
  {components: [...boundedDetail.structure.components, {...component, contained_by: 'unknown'}]},
  {components: [...boundedDetail.structure.components, {...component, contained_by: 'extra'}]},
])('rejects dangling, cyclic or duplicated structural identities', async (patch) => {
  const value = {...boundedDetail, structure: {...boundedDetail.structure, ...patch}};
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply(value)));
  await expect(
    new OperatorClient('key').graph('bounded-review', 'example-1', new AbortController().signal),
  ).rejects.toThrow();
});
