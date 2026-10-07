import {expect, it} from 'vitest';
import type {UiField} from '../src/api/index.ts';
import {NOT_SET, fieldVisible, jsonPreview, summaryValue, textPreview} from '../src/ui/index.ts';
import {catalog, declaration} from './support/contract.ts';

const field = (control: UiField['control'], extra: Partial<UiField> = {}): UiField => ({
  path: '/value',
  control,
  label: 'Value',
  ...extra,
});
const summary = (control: UiField['control'], value: unknown, extra: Partial<UiField> = {}) =>
  summaryValue(field(control, extra), value as never, catalog.llms);

it('previews text and multiline values up to 120 characters', () => {
  expect(summary('multiline', 'Rewrite\n this   story')).toBe('Rewrite this story');
  const long = summary('text', 'x'.repeat(200));
  expect(long).toHaveLength(120);
  expect(long.endsWith('…')).toBe(true);
  expect(summary('text', '')).toBe(NOT_SET);
  expect(summary('text', undefined)).toBe(NOT_SET);
  expect(textPreview('   ')).toBe(NOT_SET);
  expect(jsonPreview({a: 1})).toBe('{"a":1}');
});

it('summarizes choices, lists, code, numbers and schemas', () => {
  const options = [{value: 'json', label: 'JSON'}];
  expect(summary('choice', 'json', {options})).toBe('JSON');
  expect(summary('choice', 'other', {options})).toBe('other');
  expect(summary('list', ['funny', 'not_funny'])).toBe('funny, not_funny');
  expect(summary('list', [])).toBe(NOT_SET);
  expect(summary('code', 'def route():\n    return 1\n')).toBe('2 lines');
  expect(summary('code', 'pass')).toBe('1 line');
  expect(summary('code', '')).toBe(NOT_SET);
  expect(summary('number', 3)).toBe('3');
  expect(summary('schema', {type: 'object'})).toBe('JSON schema');
  expect(summary('schema', null, {empty_label: 'Any text'})).toBe('Any text');
  expect(summary('schema', null)).toBe(NOT_SET);
});

it('summarizes a service selection as the entry label and its parameter values', () => {
  const luna = {llm: 'openai/gpt-6-luna', parameters: {max_completion_tokens: 300}};
  expect(summary('service', luna)).toBe('OpenAI · GPT-6 Luna · Max output tokens 300');
  const flash = {
    llm: 'deepseek/deepseek-flash',
    parameters: {reasoning_effort: 'none', temperature: 0.2},
  };
  expect(summary('service', flash)).toBe(
    'DeepSeek · DeepSeek Flash · Reasoning none · Temperature 0.2',
  );
  expect(summary('service', {llm: 'gone/model', parameters: {}})).toBe(
    'gone/model (not available)',
  );
  expect(summary('service', null)).toBe(NOT_SET);
  expect(summary('service', {model: 'x'})).toBe(NOT_SET);
});

it('shows a field only while its when condition holds', () => {
  const output = declaration('llm-call').ui.sections.find((section) => section.id === 'output');
  const schemaField = output?.fields[1];
  if (schemaField === undefined) throw new Error('Missing schema field');
  expect(fieldVisible(schemaField, {output_format: {type: 'json'}})).toBe(true);
  expect(fieldVisible(schemaField, {output_format: {type: 'text'}})).toBe(false);
  expect(fieldVisible(field('text'), {})).toBe(true);
});
