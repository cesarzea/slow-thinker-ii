import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, render} from '@testing-library/react';
import {screen, within} from '@testing-library/dom';
import userEvent from '@testing-library/user-event';
import {Inspector} from '../src/features/inspector/index.ts';
import {InspectionServer} from './support/inspection-server.ts';
let server: InspectionServer;
beforeEach(() => {
  server = new InspectionServer();
  vi.stubGlobal('fetch', server.fetch);
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
it('opens external evidence visibly and repeats focus without overriding internal navigation', async () => {
  const view = render(
    <Inspector credential="key" run="run" selection={{kind: 'activation', id: 'activation'}} />,
  );
  const heading = await screen.findByRole('heading', {name: 'Activation activation'});
  expect(document.activeElement).toBe(heading);
  await userEvent.click(await screen.findByRole('button', {name: 'View effective input'}));
  expect(document.activeElement).toBe(screen.getByRole('heading', {name: 'Retained content'}));
  view.rerender(
    <Inspector credential="key" run="run" selection={{kind: 'activation', id: 'activation'}} />,
  );
  expect(document.activeElement).toBe(heading);
  expect(screen.queryByRole('region', {name: 'Retained content'})).toBeNull();
  view.rerender(
    <Inspector credential="key" run="run" selection={{kind: 'payload', id: 'direct'}} />,
  );
  expect(await screen.findByText(/direct · Capture state/)).toBeTruthy();
});
it('labels reported information, source timestamps and unavailable payloads without inventing reasoning', async () => {
  server.call.reports = [
    {
      event_sequence: 8,
      kind: 'reasoning',
      schema_version: '1',
      evidence: 'reported',
      payload_id: 'report',
      source_occurred_at: 20,
    },
    {
      event_sequence: 9,
      kind: 'diagnostic',
      schema_version: '1',
      evidence: 'reported',
      payload_id: null,
      source_occurred_at: null,
    },
  ];
  render(<Inspector credential="key" run="run" selection={{kind: 'call', id: 'child'}} />);
  expect(await screen.findByText(/reasoning · Reported/)).toBeTruthy();
  expect(screen.getByText(/Source timestamp: 20/)).toBeTruthy();
  expect(screen.getByText('Report content unavailable.')).toBeTruthy();
  await userEvent.click(screen.getByRole('button', {name: 'View report'}));
  expect(await screen.findByText(/report · Capture state/)).toBeTruthy();
});
it('makes absent reasoning explicit for both calls and activations', async () => {
  const view = render(
    <Inspector credential="key" run="run" selection={{kind: 'call', id: 'child'}} />,
  );
  expect(await screen.findByText(/Reasoning unavailable/)).toBeTruthy();
  view.rerender(
    <Inspector credential="key" run="run" selection={{kind: 'activation', id: 'activation'}} />,
  );
  const region = within(await screen.findByRole('region', {name: 'Activation details'}));
  expect(await region.findByText(/Reasoning unavailable/)).toBeTruthy();
});
