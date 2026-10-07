import {expect, it} from 'vitest';
import {componentFacts, originText} from '../src/features/catalog/component-facts.ts';
import {parameterRows} from '../src/features/catalog/llm-parameters.ts';
import {copy, declaration, llm} from './support/contract.ts';

it('names the origin of a component', () => {
  expect([originText('platform'), originText('package')]).toEqual([
    'Platform',
    'Installed package',
  ]);
});

it('describes a stateful component embedded only at outputs, choosing its LLM elsewhere', () => {
  const component = copy(declaration('router'));
  const modified = {
    ...component,
    placements: ['output' as const],
    state: 'stateful' as const,
    uses: [{service: 'llm' as const, pointer: '/judge'}],
  };
  expect(componentFacts(modified)).toEqual([
    ['Use', "Embedded at a node's outputs"],
    ['Inputs', 'in'],
    ['Outputs', 'Outputs from its configuration'],
    ['State', 'Stateful'],
    ['LLM', 'Chosen for each node in its configuration'],
    ['Configuration', 'Outputs, Script'],
  ]);
});

it('reads title, range and default of each LLM parameter', () => {
  expect(parameterRows(llm('openai/gpt-6-luna').parameters)).toEqual([
    {
      name: 'max_completion_tokens',
      title: 'Max output tokens',
      range: '1–128,000',
      initial: '1,024',
    },
  ]);
  const schema = {
    properties: {
      floor: {type: 'number', minimum: 0.5},
      ceiling: {type: 'integer', maximum: 8},
      stream: {type: 'boolean', default: false},
      prefix: {type: 'string'},
      broken: 3,
    },
  };
  expect(parameterRows(schema).map(({title, range, initial}) => [title, range, initial])).toEqual([
    ['floor', 'At least 0.5', '—'],
    ['ceiling', 'At most 8', '—'],
    ['stream', 'true or false', 'false'],
    ['prefix', '—', '—'],
  ]);
  expect(parameterRows({type: 'object'})).toEqual([]);
});
