import {useState} from 'react';
import type {ReactElement} from 'react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {ConfigurationDialog, ConfigurationSummary, Tabs} from '../src/ui/index.ts';

afterEach(cleanup);

function Sections(): ReactElement {
  const [selected, select] = useState('prompt');
  const items = [
    {key: 'prompt', title: 'Prompt', group: {label: 'LLM Call'}},
    {key: 'outputs', title: 'Outputs', group: {label: 'Router', icon: <b>R</b>}},
    {key: 'script', title: 'Script', group: {label: 'Router', icon: <b>R</b>}},
  ];
  return (
    <Tabs
      label="Sections"
      orientation="vertical"
      items={items}
      selected={selected}
      onSelect={select}
    >
      <p>Section {selected}</p>
    </Tabs>
  );
}

it('lists vertical sections with a heading for each embedded group', async () => {
  render(<Sections />);
  const list = screen.getByRole('tablist', {name: 'Sections'});
  expect(list.getAttribute('aria-orientation')).toBe('vertical');
  const heading = within(list).getByText('Router');
  expect(heading.getAttribute('aria-hidden')).toBe('true');
  expect(heading.textContent).toBe('RRouter');
  expect(within(list).getAllByText('Router')).toHaveLength(1);
  const tab = (name: string): HTMLElement => screen.getByRole('tab', {name});
  expect(
    [tab('Outputs'), tab('Script')].map((item) => item.getAttribute('aria-describedby')),
  ).toEqual([heading.id, heading.id]);
  expect(tab('Prompt').getAttribute('aria-describedby')).toBe(
    within(list).getByText('LLM Call').id,
  );
  const first = screen.getByRole('tabpanel');
  tab('Prompt').focus();
  await userEvent.keyboard('{ArrowDown}');
  expect(screen.getByRole('tabpanel', {name: 'Outputs'}).textContent).toBe('Section outputs');
  expect(screen.getByRole('tabpanel')).not.toBe(first);
  await userEvent.keyboard('{ArrowDown}{ArrowUp}{ArrowUp}');
  expect(document.activeElement).toBe(tab('Prompt'));
});

it('puts further actions at the start of a fixed dialog footer', async () => {
  const remove = vi.fn();
  render(
    <ConfigurationDialog
      title="Judge"
      fixed
      actions={
        <button type="button" onClick={remove}>
          Remove Router
        </button>
      }
      onApply={vi.fn()}
      onCancel={vi.fn()}
    >
      <p>Fields</p>
    </ConfigurationDialog>,
  );
  const dialog = screen.getByRole('dialog', {name: 'Judge'});
  const names = within(dialog)
    .getAllByRole('button')
    .map((button) => button.textContent);
  expect(names.slice(-3)).toEqual(['Remove Router', 'Cancel', 'Apply']);
  await userEvent.click(within(dialog).getByRole('button', {name: 'Remove Router'}));
  expect(remove).toHaveBeenCalledOnce();
});

it('collapses a summary card behind its title when the card can toggle', async () => {
  const toggle = vi.fn();
  const values = [{label: 'LLM', value: 'Not set'}];
  const card = (expanded: boolean): ReactElement => (
    <ConfigurationSummary
      title="Model"
      values={values}
      expanded={expanded}
      onToggle={toggle}
      onEdit={vi.fn()}
    />
  );
  const view = render(card(false));
  const title = screen.getByRole('button', {name: 'Model'});
  expect(title.getAttribute('aria-expanded')).toBe('false');
  expect(screen.queryByRole('term')).toBeNull();
  expect(screen.getByRole('button', {name: 'Edit Model'})).toBeTruthy();
  expect(screen.getByRole('region', {name: 'Model'}).textContent).toContain('Not set');
  await userEvent.click(title);
  expect(toggle).toHaveBeenCalledOnce();
  view.rerender(card(true));
  expect(title.getAttribute('aria-expanded')).toBe('true');
  expect(screen.getByRole('term').textContent).toBe('LLM');
  view.rerender(<ConfigurationSummary title="Model" values={values} onEdit={vi.fn()} />);
  expect(screen.queryByRole('button', {name: 'Model'})).toBeNull();
  expect(screen.getByRole('term').textContent).toBe('LLM');
});
