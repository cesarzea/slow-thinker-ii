import {afterEach, expect, it} from 'vitest';
import {cleanup, screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {UiField} from '../src/api/index.ts';
import {renderField} from './support/field-harness.tsx';

afterEach(cleanup);

const field = (control: UiField['control'], extra: Partial<UiField> = {}): UiField => ({
  path: '/value',
  control,
  label: 'Value',
  help: 'Explains the value.',
  ...extra,
});

it('renders text and multiline controls as text boxes named by the label', async () => {
  const changes = renderField(field('text', {placeholder: 'Name'}), 'a');
  const box = screen.getByRole('textbox', {name: 'Value'});
  expect(box.getAttribute('aria-describedby')).toBe(screen.getByText('Explains the value.').id);
  await userEvent.type(box, 'b');
  expect(changes.latest()).toBe('ab');
  cleanup();
  const lines = renderField(field('multiline', {label: 'Instructions'}), undefined);
  await userEvent.type(screen.getByRole('textbox', {name: 'Instructions'}), 'Hi');
  expect(lines.latest()).toBe('Hi');
});

it('expands a multiline control inside a dialog-free page into its own dialog', async () => {
  renderField(field('multiline', {label: 'Instructions'}), 'Text');
  await userEvent.click(screen.getByRole('button', {name: 'Expand Instructions'}));
  expect(screen.getByRole('dialog', {name: 'Instructions'})).toBeTruthy();
});

it('renders numbers as spin buttons honouring schema bounds', async () => {
  const changes = renderField(field('number'), 5, {
    schema: {type: 'integer', minimum: 1, maximum: 9},
  });
  const spin = screen.getByRole<HTMLInputElement>('spinbutton', {name: 'Value'});
  expect([spin.min, spin.max, spin.step]).toEqual(['1', '9', '1']);
  await userEvent.clear(spin);
  expect(changes.latest()).toBeUndefined();
  await userEvent.type(spin, '7');
  expect(changes.latest()).toBe(7);
});

it('renders choices as a combobox and offers Not set for unknown values', async () => {
  const options = [
    {value: 'text', label: 'Text'},
    {value: 'json', label: 'JSON'},
  ];
  const changes = renderField(field('choice', {label: 'Format', options}), 'xml');
  const combo = screen.getByRole('combobox', {name: 'Format'});
  expect(screen.getByRole('option', {name: 'Not set'})).toBeTruthy();
  await userEvent.selectOptions(combo, 'JSON');
  expect(changes.latest()).toBe('json');
  await userEvent.selectOptions(combo, 'Text');
  expect(changes.latest()).toBe('text');
});

it('edits a list with numbered items, add and remove', async () => {
  const changes = renderField(field('list', {item_label: 'Output'}), ['yes', 'no']);
  await userEvent.clear(screen.getByRole('textbox', {name: 'Output 1'}));
  await userEvent.type(screen.getByRole('textbox', {name: 'Output 1'}), 'funny');
  await userEvent.click(screen.getByRole('button', {name: 'Add Output'}));
  expect(changes.latest()).toEqual(['funny', 'no', '']);
  await userEvent.click(screen.getByRole('button', {name: 'Remove Output 2'}));
  expect(changes.latest()).toEqual(['funny', '']);
  cleanup();
  renderField(field('list'), 'not a list');
  expect(screen.getByRole('button', {name: 'Add Item'})).toBeTruthy();
});

it('renders code as a monospaced multi-line text box named by the label', async () => {
  const label = 'route(received, node_input)';
  const changes = renderField(field('code', {label, language: 'python'}), 'pass');
  const code = screen.getByRole('textbox', {name: label});
  expect(code.tagName).toBe('TEXTAREA');
  expect(code.classList.contains('code')).toBe(true);
  await userEvent.type(code, '!');
  expect(changes.latest()).toBe('pass!');
});

it('disables every control when asked', () => {
  renderField(field('list'), ['a'], {disabled: true});
  expect(screen.getByRole<HTMLInputElement>('textbox', {name: 'Item 1'}).matches(':disabled')).toBe(
    true,
  );
});
