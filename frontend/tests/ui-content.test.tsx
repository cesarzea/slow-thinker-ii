import {useCallback, useState} from 'react';
import type {ReactElement} from 'react';
import {afterEach, expect, it} from 'vitest';
import {act, cleanup, render, screen, waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {ApiError} from '../src/api/index.ts';
import {ActionButton, EvidenceContent, Panel, Tabs, useRead} from '../src/ui/index.ts';

afterEach(cleanup);

it('renders recorded content as text and structure, never as markup', () => {
  const value = {
    reply: '<b>bold</b>',
    score: 8,
    ok: true,
    tags: ['a'],
    empty: [],
    none: null,
    deep: {a: {b: {c: {d: 1}}}},
    blank: {},
  };
  const {container} = render(<EvidenceContent value={value} />);
  expect(screen.getByText('<b>bold</b>')).toBeTruthy();
  expect(container.querySelector('b')).toBeNull();
  expect(screen.getByText('8')).toBeTruthy();
  expect(screen.getByText('Empty list')).toBeTruthy();
  expect(screen.getByText('Empty object')).toBeTruthy();
  expect(screen.getByText('Empty')).toBeTruthy();
  expect(container.querySelector('.evidence-json')?.textContent).toContain('"d": 1');
});

function Reader(props: {readonly fail: boolean}): ReactElement {
  const [count, setCount] = useState(0);
  const read = useCallback(
    async (): Promise<string> =>
      props.fail
        ? Promise.reject(new ApiError(500, 'x', 'Failed to load.'))
        : `Loaded ${String(count)}`,
    [props.fail, count],
  );
  const {data, error, refresh} = useRead(read);
  return (
    <>
      <p>{data ?? error ?? 'Loading'}</p>
      <button onClick={refresh}>Refresh</button>
      <button
        onClick={() => {
          setCount(count + 1);
        }}
      >
        Next
      </button>
    </>
  );
}

it('reads data, reports failures and refreshes on request', async () => {
  const {rerender} = render(<Reader fail={false} />);
  expect(await screen.findByText('Loaded 0')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Next'}));
  expect(await screen.findByText('Loaded 1')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'Refresh'}));
  expect(await screen.findByText('Loaded 1')).toBeTruthy();
  rerender(<Reader fail />);
  expect(await screen.findByText('Failed to load.')).toBeTruthy();
});

it('ignores replies that arrive after the reader is gone', async () => {
  const pending = Promise.withResolvers<string>();
  function Late(): ReactElement {
    const read = useCallback(async (): Promise<string> => pending.promise, []);
    return <p>{useRead(read).data ?? 'Loading'}</p>;
  }
  const view = render(<Late />);
  view.unmount();
  await act(async () => {
    pending.resolve('late');
    await pending.promise;
  });
  expect(screen.queryByText('late')).toBeNull();
});

it('moves between tabs with the arrow keys', async () => {
  function Fixture(): ReactElement {
    const [selected, select] = useState('a');
    const items = [
      {key: 'a', title: 'Prompt'},
      {key: 'b', title: 'Outputs', marker: 'embedded'},
    ];
    return (
      <Tabs label="Sections" items={items} selected={selected} onSelect={select}>
        <p>Panel {selected}</p>
      </Tabs>
    );
  }
  render(<Fixture />);
  screen.getByRole('tab', {name: 'Prompt'}).focus();
  await userEvent.keyboard('{ArrowRight}');
  expect(screen.getByRole('tab', {name: 'Outputs'}).getAttribute('aria-selected')).toBe('true');
  expect(screen.getByRole('tabpanel', {name: 'Outputs'}).textContent).toBe('Panel b');
  await userEvent.keyboard('{Home}{ArrowLeft}{End}{x}');
  await waitFor(() => {
    expect(document.activeElement).toBe(screen.getByRole('tab', {name: 'Outputs'}));
  });
  await userEvent.click(screen.getByRole('tab', {name: 'Prompt'}));
  expect(screen.getByRole('tabpanel').textContent).toBe('Panel a');
});

it('renders titled panels and asynchronous action buttons', async () => {
  let done = 0;
  render(
    <Panel title="Totals">
      <ActionButton
        primary
        label="Run graph"
        action={async () => {
          await Promise.resolve();
          done += 1;
        }}
      >
        Run
      </ActionButton>
    </Panel>,
  );
  await userEvent.click(screen.getByRole('button', {name: 'Run graph'}));
  expect(screen.getByRole('region', {name: 'Totals'})).toBeTruthy();
  expect(done).toBe(1);
});
