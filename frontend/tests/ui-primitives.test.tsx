import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  Button,
  ButtonLink,
  IconButton,
  KindTile,
  MenuButton,
  NumberControl,
} from '../src/ui/index.ts';
import {boundsText, fieldClass, formatNumber} from '../src/ui/presentation.ts';
import type {UiField} from '../src/api/index.ts';

afterEach(cleanup);

it('draws buttons by variant, with icons and names', async () => {
  const click = vi.fn();
  render(
    <>
      <Button variant="primary" icon="play" onClick={click}>
        Run v1
      </Button>
      <Button size="sm" variant="ghost" label="Arrange the graph" pressed onClick={click}>
        Arrange
      </Button>
      <ButtonLink href="#/runs" icon="runs">
        Runs
      </ButtonLink>
    </>,
  );
  await userEvent.click(screen.getByRole('button', {name: 'Run v1'}));
  expect(click).toHaveBeenCalledOnce();
  expect(screen.getByRole('button', {name: 'Run v1'}).className).toBe('btn btn-primary');
  expect(screen.getByRole('button', {name: 'Arrange the graph'}).className).toBe(
    'btn btn-ghost btn-sm',
  );
  expect(screen.getByRole('link', {name: 'Runs'}).getAttribute('href')).toBe('#/runs');
});

it('names icon buttons by their tooltip and draws kind tiles as decoration', async () => {
  const click = vi.fn();
  render(
    <>
      <IconButton icon="undo" label="Undo" size="sm" tone="danger" onClick={click} />
      <KindTile icon="agent" size="sm" />
    </>,
  );
  const undo = screen.getByRole('button', {name: 'Undo'});
  expect([undo.title, undo.className]).toEqual([
    'Undo',
    'icon-button icon-button-sm icon-button-danger',
  ]);
  await userEvent.click(undo);
  expect(click).toHaveBeenCalledOnce();
  expect(document.querySelector('.tile-llm.tile-sm')?.getAttribute('aria-hidden')).toBe('true');
});

it('opens a menu of actions, moves with the arrows and closes with Escape', async () => {
  const remove = vi.fn();
  render(
    <MenuButton
      label="More actions for Reviewer"
      items={[
        {label: 'Remove Router', onSelect: remove},
        {label: 'Delete node', danger: true, onSelect: vi.fn()},
      ]}
    />,
  );
  const trigger = screen.getByRole('button', {name: 'More actions for Reviewer'});
  await userEvent.click(trigger);
  expect(trigger.getAttribute('aria-expanded')).toBe('true');
  expect(document.activeElement).toBe(screen.getByRole('menuitem', {name: 'Remove Router'}));
  await userEvent.keyboard('{ArrowDown}');
  expect(document.activeElement).toBe(screen.getByRole('menuitem', {name: 'Delete node'}));
  await userEvent.keyboard('{ArrowDown}{ArrowUp}{ArrowUp}');
  expect(document.activeElement).toBe(screen.getByRole('menuitem', {name: 'Remove Router'}));
  await userEvent.keyboard('{Escape}');
  expect(screen.queryByRole('menu')).toBeNull();
  expect(document.activeElement).toBe(trigger);
  await userEvent.click(trigger);
  await userEvent.click(screen.getByRole('menuitem', {name: 'Remove Router'}));
  expect(remove).toHaveBeenCalledOnce();
  expect(screen.queryByRole('menu')).toBeNull();
});

const field = (control: UiField['control'], extra: Partial<UiField> = {}): UiField => ({
  path: '/value',
  control,
  label: 'Value',
  ...extra,
});

it('lays fields out by their declared presentation, with the defaults', () => {
  expect(fieldClass(field('number'))).toBe(
    'config-field field-number width-sm align-end label-top',
  );
  expect(fieldClass(field('choice'))).toContain('width-md align-start');
  expect(fieldClass(field('text'))).toContain('width-lg');
  expect(fieldClass(field('code'))).toContain('width-full');
  const declared = field('text', {width: 'xs', align: 'center', label_position: 'start'});
  expect(fieldClass(declared)).toBe('config-field field-text width-xs align-center label-start');
});

it('formats numbers with decimals, grouping, prefix and suffix', () => {
  expect(formatNumber(1234.5, {decimals: 2, grouping: true, prefix: '$'})).toBe('$1,234.50');
  expect(formatNumber(50, {suffix: 'tokens'})).toBe('50 tokens');
  expect(formatNumber(5, {suffix: '%'})).toBe('5%');
  expect(formatNumber(384000, undefined)).toBe('384000');
  expect(boundsText(1, 384000)).toBe('1 to 384,000');
  expect([boundsText(0, undefined), boundsText(undefined, 2)]).toEqual(['From 0', 'Up to 2']);
  expect(boundsText(undefined, undefined)).toBeUndefined();
});

it('shows a number with its prefix, suffix and decimal step', () => {
  render(
    <NumberControl
      label="Budget"
      help="Per run"
      prefix="$"
      suffix="USD"
      decimals={2}
      value={1.5}
      onValue={vi.fn()}
    />,
  );
  const input = screen.getByRole('spinbutton', {name: 'Budget'});
  expect(input.getAttribute('step')).toBe('0.01');
  expect(input.parentElement?.textContent).toBe('$USD');
  expect(document.getElementById(input.getAttribute('aria-describedby') ?? '')?.textContent).toBe(
    'Per run',
  );
});
