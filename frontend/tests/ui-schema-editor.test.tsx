import {afterEach, expect, it} from 'vitest';
import {cleanup, render, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {UiField} from '../src/api/index.ts';
import {SchemaEditor} from '../src/ui/index.ts';
import {renderField} from './support/field-harness.tsx';

afterEach(cleanup);

const output: UiField = {path: '/output_format/schema', control: 'schema', label: 'JSON schema'};
const input: UiField = {...output, label: 'Expected input', empty_label: 'Any text'};
const SCORE = {
  type: 'object',
  additionalProperties: false,
  properties: {score: {type: 'integer', minimum: 1, maximum: 10}},
  required: ['score'],
};

it('builds the score schema of the journeys property by property', async () => {
  const changes = renderField(output, undefined);
  await userEvent.click(screen.getByRole('button', {name: 'Add property'}));
  const property = screen.getByRole('group', {name: 'Property 1'});
  await userEvent.type(within(property).getByRole('textbox', {name: 'Property name'}), 'score');
  await userEvent.selectOptions(within(property).getByRole('combobox', {name: 'Type'}), 'Integer');
  await userEvent.click(within(property).getByRole('checkbox', {name: 'Required'}));
  await userEvent.type(within(property).getByRole('spinbutton', {name: 'Minimum'}), '1');
  await userEvent.type(within(property).getByRole('spinbutton', {name: 'Maximum'}), '10');
  expect(changes.latest()).toEqual(SCORE);
  expect(screen.queryByRole('textbox', {name: /schema/iu})).toBeNull();
});

it('edits an existing schema and leaves out unnamed or repeated properties', async () => {
  const changes = renderField(output, SCORE);
  expect(screen.getByRole<HTMLInputElement>('textbox', {name: 'Property name'}).value).toBe(
    'score',
  );
  await userEvent.click(screen.getByRole('button', {name: 'Add property'}));
  const second = screen.getByRole('group', {name: 'Property 2'});
  expect(changes.latest()).toEqual(SCORE);
  await userEvent.selectOptions(
    within(second).getByRole('combobox', {name: 'Type'}),
    'List of text',
  );
  await userEvent.type(within(second).getByRole('textbox', {name: 'Property name'}), 'score');
  expect(changes.latest()).toEqual(SCORE);
  await userEvent.clear(within(second).getByRole('textbox', {name: 'Property name'}));
  await userEvent.type(within(second).getByRole('textbox', {name: 'Property name'}), 'tags');
  expect(changes.latest()).toMatchObject({
    properties: {tags: {type: 'array', items: {type: 'string'}}},
  });
  const first = screen.getByRole('group', {name: 'Property 1'});
  await userEvent.selectOptions(within(first).getByRole('combobox', {name: 'Type'}), 'Text');
  await userEvent.click(within(first).getByRole('button', {name: 'Remove property'}));
  expect(changes.latest()).toEqual({
    type: 'object',
    additionalProperties: false,
    properties: {tags: {type: 'array', items: {type: 'string'}}},
    required: [],
  });
});

it('offers the empty label or a JSON schema as a radio group named by the field', async () => {
  const changes = renderField(input, null);
  const format = screen.getByRole('radiogroup', {name: 'Expected input'});
  expect(within(format).getByRole<HTMLInputElement>('radio', {name: 'Any text'}).checked).toBe(
    true,
  );
  expect(screen.queryByRole('button', {name: 'Add property'})).toBeNull();
  await userEvent.click(within(format).getByRole('radio', {name: 'JSON schema'}));
  expect(changes.latest()).toEqual({
    type: 'object',
    additionalProperties: false,
    properties: {},
    required: [],
  });
  await userEvent.click(screen.getByRole('button', {name: 'Add property'}));
  await userEvent.click(within(format).getByRole('radio', {name: 'Any text'}));
  expect(changes.latest()).toBeNull();
});

it.each([
  {type: 'object', properties: {a: {type: 'object'}}},
  {type: 'object', properties: {a: {type: 'string', minLength: 1}}},
  {type: 'object', properties: {a: {type: 'integer', exclusiveMinimum: 1}}},
  {type: 'object', properties: {a: {type: 'number', minimum: 'one'}}},
  {type: 'object', required: ['missing']},
  {type: 'object', required: 'a'},
  {type: 'object', additionalProperties: true},
  {type: 'array'},
  'text',
])('keeps schemas it cannot edit and shows them read-only (%#)', (schema) => {
  renderField(output, schema);
  expect(screen.getByText('This schema can be kept but not edited here.')).toBeTruthy();
  expect(screen.queryByRole('button', {name: 'Add property'})).toBeNull();
  expect(screen.queryByRole('textbox')).toBeNull();
});

it('can be used on its own and disabled', () => {
  render(
    <SchemaEditor
      label="Expected input"
      emptyLabel="Any text"
      value={SCORE}
      onChange={() => undefined}
      disabled
    />,
  );
  const format = screen.getByRole('radiogroup', {name: 'Expected input'});
  expect(within(format).getByRole<HTMLInputElement>('radio', {name: 'JSON schema'}).checked).toBe(
    true,
  );
  expect(screen.getByRole<HTMLButtonElement>('button', {name: 'Add property'}).disabled).toBe(true);
});
