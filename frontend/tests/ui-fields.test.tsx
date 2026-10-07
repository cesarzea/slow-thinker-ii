import {afterEach, expect, it} from 'vitest';
import {cleanup, fireEvent, screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {UiField} from '../src/api/index.ts';
import {renderField} from './support/field-harness.tsx';

afterEach(cleanup);

const HELP = 'Explains the value.';
const field = (control: UiField['control'], extra: Partial<UiField> = {}): UiField => ({
  path: '/value',
  control,
  label: 'Value',
  help: HELP,
  ...extra,
});
const follows = (first: Node, second: Node): boolean =>
  (first.compareDocumentPosition(second) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0;

it('shows help under the label, before the control it describes', () => {
  const cases: [UiField, string][] = [
    [field('text'), 'textbox'],
    [field('number'), 'spinbutton'],
    [field('choice', {options: [{value: 'a', label: 'A'}]}), 'combobox'],
    [field('multiline'), 'textbox'],
    [field('code'), 'textbox'],
    [field('service'), 'combobox'],
  ];
  for (const [declared, role] of cases) {
    renderField(declared, undefined);
    const help = screen.getByText(HELP);
    const control = screen.getByRole(role, {name: 'Value'});
    expect(follows(screen.getByText('Value'), help) && follows(help, control)).toBe(true);
    expect(control.getAttribute('aria-describedby')?.split(' ')).toContain(help.id);
    cleanup();
  }
  renderField(field('list', {item_label: 'Output'}), []);
  expect(screen.getByRole('group', {name: 'Value'}).getAttribute('aria-describedby')).toBe(
    screen.getByText(HELP).id,
  );
});

it('moves list items up and down and keeps focus on the moved item', async () => {
  const changes = renderField(field('list', {item_label: 'Output'}), ['a', 'b', 'c']);
  const button = (name: string): HTMLElement => screen.getByRole('button', {name});
  expect(button('Move Output 1 up').matches(':disabled')).toBe(true);
  expect(button('Move Output 3 down').matches(':disabled')).toBe(true);
  await userEvent.click(button('Move Output 3 up'));
  expect(changes.latest()).toEqual(['a', 'c', 'b']);
  expect(document.activeElement).toBe(button('Move Output 2 up'));
  await userEvent.click(button('Move Output 2 up'));
  expect(changes.latest()).toEqual(['c', 'a', 'b']);
  expect(document.activeElement).toBe(button('Move Output 1 down'));
  await userEvent.click(button('Move Output 2 down'));
  expect(changes.latest()).toEqual(['c', 'b', 'a']);
  expect(document.activeElement).toBe(button('Move Output 3 up'));
  expect(screen.getByLabelText('Output 2')).toBe(screen.getByRole('textbox', {name: 'Output 2'}));
});

it('numbers the lines of code and keeps the numbers beside them while scrolling', () => {
  renderField(field('code', {label: 'route(received, node_input)'}), 'a\nb\nc');
  const code = screen.getByRole('textbox', {name: 'route(received, node_input)'});
  const gutter = code.previousElementSibling;
  if (!(gutter instanceof HTMLElement)) throw new Error('No line numbers');
  expect([gutter.textContent, gutter.getAttribute('aria-hidden')]).toEqual(['1\n2\n3', 'true']);
  Object.defineProperty(code, 'scrollTop', {value: 40, configurable: true});
  Object.defineProperty(gutter, 'scrollTop', {value: 0, writable: true, configurable: true});
  fireEvent.scroll(code);
  expect(gutter.scrollTop).toBe(40);
});
