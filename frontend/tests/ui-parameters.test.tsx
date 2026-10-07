import {afterEach, expect, it} from 'vitest';
import {cleanup, screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {UiField} from '../src/api/index.ts';
import {renderField, renderParameters} from './support/field-harness.tsx';
import {llm} from './support/contract.ts';

afterEach(cleanup);

const model: UiField = {path: '/model', control: 'service', service: 'llm', label: 'LLM'};
const NOTE = 'Not available with the current settings.';

it('lists the catalog LLMs and starts a selection from the entry defaults', async () => {
  const changes = renderField(model, null);
  const combo = screen.getByRole('combobox', {name: 'LLM'});
  expect(screen.getAllByRole('option').map((option) => option.textContent)).toEqual([
    'Not selected',
    'OpenAI · GPT-6 Luna',
    'DeepSeek · DeepSeek Flash',
  ]);
  await userEvent.selectOptions(combo, 'OpenAI · GPT-6 Luna');
  expect(changes.latest()).toEqual({
    llm: 'openai/gpt-6-luna',
    parameters: {max_completion_tokens: 1024},
  });
  const tokens = screen.getByRole('spinbutton', {name: 'Max output tokens'});
  await userEvent.clear(tokens);
  await userEvent.type(tokens, '300');
  expect(changes.latest()).toEqual({
    llm: 'openai/gpt-6-luna',
    parameters: {max_completion_tokens: 300},
  });
  await userEvent.selectOptions(combo, 'Not selected');
  expect(changes.latest()).toBeNull();
});

it('keeps a selection whose entry is no longer in the catalog visible', () => {
  renderField(model, {llm: 'gone/model', parameters: {}});
  expect(screen.getByRole('option', {name: 'gone/model (not available)'})).toBeTruthy();
});

it('disables Temperature unless DeepSeek reasoning is none, keeping its name and a note', async () => {
  const schema = llm('deepseek/deepseek-flash').parameters;
  const changes = renderParameters(schema, {reasoning_effort: 'none', temperature: 0.2});
  const reasoning = screen.getByRole('combobox', {name: 'Reasoning'});
  const temperature = screen.getByRole<HTMLInputElement>('spinbutton', {name: 'Temperature'});
  expect(screen.getByRole('option', {name: 'Default (none)'})).toBeTruthy();
  expect(temperature.disabled).toBe(false);
  await userEvent.selectOptions(reasoning, 'high');
  expect(temperature.disabled).toBe(true);
  expect(temperature.getAttribute('aria-describedby')?.split(' ')).toContain(
    screen.getByText(NOTE).id,
  );
  expect(changes.latest()).toEqual({reasoning_effort: 'high'});
  await userEvent.selectOptions(reasoning, 'none');
  expect(temperature.disabled).toBe(false);
  expect(screen.queryByText(NOTE)).toBeNull();
});

const MIXED = {
  type: 'object',
  properties: {
    stop: {type: 'string', title: 'Stop text'},
    stream: {type: 'boolean', title: 'Stream'},
    mode: {enum: ['fast', 1]},
    ignored: true,
  },
  allOf: [
    {
      if: {properties: {stream: {const: true}}, required: ['stream']},
      then: {properties: {stop: false}},
    },
  ],
};

it('renders strings, booleans, unset enums and untitled properties', async () => {
  const changes = renderParameters(MIXED, {});
  await userEvent.type(screen.getByRole('textbox', {name: 'Stop text'}), 'x');
  expect(changes.latest()).toEqual({stop: 'x'});
  await userEvent.selectOptions(screen.getByRole('combobox', {name: 'mode'}), '1');
  expect(changes.latest()).toEqual({stop: 'x', mode: 1});
  expect(screen.getAllByRole('option').map((option) => option.textContent)).toEqual([
    'Not set',
    'fast',
    '1',
  ]);
  await userEvent.selectOptions(screen.getByRole('combobox', {name: 'mode'}), 'Not set');
  await userEvent.click(screen.getByRole('checkbox', {name: 'Stream'}));
  expect(changes.latest()).toEqual({stream: true});
  expect(screen.getByRole<HTMLInputElement>('textbox', {name: 'Stop text'}).disabled).toBe(true);
});

it('treats unusable conditions as satisfied', () => {
  const schema = {
    properties: {a: {type: 'number', title: 'A'}},
    if: {type: 'nonsense'},
    else: {properties: {a: false}},
  };
  renderParameters(schema, {a: 1});
  expect(screen.getByRole<HTMLInputElement>('spinbutton', {name: 'A'}).disabled).toBe(false);
  cleanup();
  renderParameters({properties: {a: {title: 'A'}}, if: false, else: {properties: {a: false}}}, {});
  expect(screen.getByRole<HTMLInputElement>('textbox', {name: 'A'}).disabled).toBe(true);
});
