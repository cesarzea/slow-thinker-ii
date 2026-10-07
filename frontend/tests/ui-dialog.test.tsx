import {useState} from 'react';
import type {ReactElement} from 'react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, render, screen, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {ConfigurationDialog, Dialog} from '../src/ui/index.ts';

afterEach(cleanup);

function useToggle(): [boolean, () => void, () => void] {
  const [open, setOpen] = useState(false);
  const show = (): void => {
    setOpen(true);
  };
  const hide = (): void => {
    setOpen(false);
  };
  return [open, show, hide];
}

function NestedDialog(): ReactElement {
  const [open, show, hide] = useToggle();
  return (
    <>
      <button onClick={show}>Nested</button>
      {open && (
        <Dialog title="Inner" onClose={hide}>
          <button>Inner action</button>
        </Dialog>
      )}
    </>
  );
}

function DialogFixture(): ReactElement {
  const [open, show, hide] = useToggle();
  return (
    <>
      <button onClick={show}>Open</button>
      {open && (
        <Dialog title="Configuration" subtitle="LLM Call" onClose={hide}>
          <input aria-label="Visible" />
          <details>
            <summary>Advanced</summary>
            <input aria-label="Collapsed" />
          </details>
          <div hidden>
            <button>Hidden</button>
          </div>
          <NestedDialog />
        </Dialog>
      )}
    </>
  );
}

it('keeps focus inside a dialog, closes on Escape and restores focus', async () => {
  render(<DialogFixture />);
  const trigger = screen.getByRole('button', {name: 'Open'});
  await userEvent.click(trigger);
  const dialog = screen.getByRole('dialog', {name: 'Configuration'});
  expect(within(dialog).getByText('LLM Call')).toBeTruthy();
  const close = within(dialog).getByRole('button', {name: 'Close Configuration'});
  expect(document.activeElement).toBe(close);
  await userEvent.tab({shift: true});
  expect(document.activeElement).toBe(within(dialog).getByRole('button', {name: 'Nested'}));
  await userEvent.tab();
  expect(document.activeElement).toBe(close);
  await userEvent.keyboard('{Escape}');
  expect(screen.queryByRole('dialog')).toBeNull();
  expect(document.activeElement).toBe(trigger);
});

it('lets a nested dialog handle its own keys without closing the outer one', async () => {
  render(<DialogFixture />);
  await userEvent.click(screen.getByRole('button', {name: 'Open'}));
  await userEvent.click(screen.getByRole('button', {name: 'Nested'}));
  const inner = screen.getByRole('dialog', {name: 'Inner'});
  await userEvent.tab();
  expect(inner.contains(document.activeElement)).toBe(true);
  await userEvent.keyboard('{Escape}');
  expect(screen.queryByRole('dialog', {name: 'Inner'})).toBeNull();
  expect(screen.getByRole('dialog', {name: 'Configuration'})).toBeTruthy();
});

it('applies through an asynchronous action and reports a failed apply', async () => {
  const onApply = vi.fn().mockRejectedValueOnce(new Error('no')).mockResolvedValueOnce(undefined);
  const onCancel = vi.fn();
  render(
    <ConfigurationDialog
      title="Limits"
      description="Run limits."
      onApply={onApply}
      onCancel={onCancel}
    >
      <input aria-label="Field" />
    </ConfigurationDialog>,
  );
  const dialog = screen.getByRole('dialog', {name: 'Limits'});
  await userEvent.click(within(dialog).getByRole('button', {name: 'Apply'}));
  expect(within(dialog).getByRole('alert').textContent).toContain('Could not apply the changes');
  await userEvent.click(within(dialog).getByRole('button', {name: 'Apply'}));
  expect(within(dialog).queryByRole('alert')).toBeNull();
  await userEvent.click(within(dialog).getByRole('button', {name: 'Cancel'}));
  expect(onApply).toHaveBeenCalledTimes(2);
  expect(onCancel).toHaveBeenCalledTimes(1);
});

it('shows an error supplied by the owner of the dialog', () => {
  render(
    <ConfigurationDialog
      title="Node"
      subtitle="LLM Call"
      wide
      error="Select a model."
      onApply={vi.fn()}
      onCancel={vi.fn()}
    >
      <p>Fields</p>
    </ConfigurationDialog>,
  );
  expect(screen.getByRole('alert').textContent).toBe('Select a model.');
});
