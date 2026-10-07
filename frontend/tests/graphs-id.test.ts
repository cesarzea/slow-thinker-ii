import {expect, it} from 'vitest';
import {graphId, graphSlug} from '../src/features/graphs/graph-id.ts';

it('derives identifiers that always start with a letter', () => {
  expect(graphSlug('Café crème!')).toBe('cafe-creme');
  expect(graphSlug('2 agents')).toBe('graph-2-agents');
  expect(graphSlug('***')).toBe('graph');
  expect(graphSlug('a'.repeat(80))).toHaveLength(59);
  expect(graphSlug(`${'a'.repeat(58)} b`)).toBe('a'.repeat(58));
  expect(graphId('Story triage', '0f3a')).toBe('story-triage-0f3a');
});
