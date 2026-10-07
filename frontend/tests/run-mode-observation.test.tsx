/** Run mode: the observation points, what they record, and the messages they show. */
import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, screen, waitFor, within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type {GraphDocument} from '../src/api/index.ts';
import {appApi, connectApp} from './support/app-harness.tsx';
import {copy, j3} from './support/contract.ts';
import {installFlowEnvironment} from './support/flow-environment.ts';
import {feed, items, openRun, points, runPanel, savedObserve} from './support/run-mode.ts';

beforeEach(installFlowEnvironment);
afterEach(() => {
  cleanup();
  localStorage.clear();
  vi.unstubAllGlobals();
});

it('shows the messages of every connection by default, to the millisecond', async () => {
  await openRun();
  expect(await within(runPanel()).findByText('Completed')).toBeTruthy();
  await waitFor(() => {
    expect(items()).toHaveLength(5);
  });
  expect(items()[0]).toBe('Story → Proposer');
  const [first] = within(feed()).getAllByRole('listitem');
  if (first === undefined) throw new Error('No message shown');
  expect(first.querySelector('.feed-time')?.textContent).toBe('0.800 s');
  expect(first.textContent).toContain('A cat tried to learn to fly.');
  await userEvent.click(within(first).getByRole('button', {name: 'Details'}));
  expect(within(first).getByText('Recorded data')).toBeTruthy();
  const checked = within(points())
    .getAllByRole<HTMLInputElement>('checkbox')
    .filter((box) => box.checked)
    .map((box) => box.getAttribute('aria-label'));
  expect(checked).toEqual([
    'Observe Story → Proposer',
    'Observe Proposer → Reviewer',
    'Observe Reviewer → Proposer',
    'Observe Reviewer → Funny story',
  ]);
});

it('unfolds a node into what it records and shows the activity of one facet or the node', async () => {
  await openRun();
  await userEvent.click(within(points()).getByRole('button', {name: 'Show what Reviewer records'}));
  const facets = within(points()).getByRole('list', {name: 'What Reviewer records'});
  expect(
    within(facets)
      .getAllByRole('checkbox')
      .map((box) => box.getAttribute('aria-label')),
  ).toEqual([
    'Observe Activity',
    'Observe Component calls',
    'Observe LLM calls',
    'Observe Reports',
    'Observe Router',
  ]);
  await userEvent.click(within(facets).getByRole('button', {name: 'Router'}));
  expect(
    within(runPanel()).getByRole('heading', {name: 'Activity of Reviewer · Router'}),
  ).toBeTruthy();
  await waitFor(() => {
    expect(items()).toEqual(['Reviewer · Router', 'Reviewer · Router']);
  });
});

it('shows a whole node without its lifecycle events unless every event is asked for', async () => {
  await openRun();
  await userEvent.click(within(points()).getByRole('button', {name: /^Proposer\s*LLM Call$/u}));
  expect(within(runPanel()).getByRole('heading', {name: 'Activity of Proposer'})).toBeTruthy();
  const content = items();
  expect(content).toContain('Proposer · LLM calls');
  expect(content).toContain('Proposer · Reports');
  expect(content).not.toContain('Proposer · Activity');
  await userEvent.click(within(runPanel()).getByRole('button', {name: 'All events'}));
  expect(items()).toContain('Proposer · Activity');
  expect(localStorage.getItem('slow-thinker-ii.observation-view')).toBe('all');
  await userEvent.click(within(runPanel()).getByRole('button', {name: 'All observed'}));
  expect(within(runPanel()).getByRole('heading', {name: 'Observed'})).toBeTruthy();
});

it('saves the observed points with the graph, a node at once or facet by facet', async () => {
  const api = await openRun();
  const reviewer = within(points()).getByRole<HTMLInputElement>('checkbox', {
    name: 'Observe Reviewer',
  });
  await userEvent.click(reviewer);
  await waitFor(() => {
    expect(savedObserve(api)).toContain('node:reviewer/output');
  });
  expect(savedObserve(api)).toContain('connection:story.out->proposer.in');
  await userEvent.click(within(points()).getByRole('button', {name: 'Show what Reviewer records'}));
  const facets = within(points()).getByRole('list', {name: 'What Reviewer records'});
  await userEvent.click(within(facets).getByRole('checkbox', {name: 'Observe Reports'}));
  await waitFor(() => {
    expect(reviewer.indeterminate).toBe(true);
  });
  await userEvent.click(within(points()).getByRole('button', {name: 'None'}));
  await waitFor(() => {
    expect(savedObserve(api)).toEqual([]);
  });
  expect(within(feed()).getByText('Check points on the left to observe them.')).toBeTruthy();
  await userEvent.click(within(points()).getByRole('button', {name: 'All'}));
  await waitFor(() => {
    expect(savedObserve(api)).toContain('run');
  });
});

it('observes a connection from the dot at its middle on the canvas', async () => {
  const api = await openRun();
  const dot = await screen.findByRole('button', {name: 'Observe Story · out to Proposer · in'});
  expect(dot.getAttribute('aria-pressed')).toBe('true');
  fireEvent.click(dot);
  await waitFor(() => {
    expect(savedObserve(api)).not.toContain('connection:story.out->proposer.in');
  });
});

it('keeps an observed node saved before facets as all of its facets', async () => {
  const saved = copy(j3);
  const observed: GraphDocument = {...saved, view: {observe: ['node:proposer', 'gone']}};
  appApi(observed);
  await connectApp('#/graphs/funny-story-with-review');
  await userEvent.click(await screen.findByRole('button', {name: 'Run'}));
  const proposer = within(points()).getByRole<HTMLInputElement>('checkbox', {
    name: 'Observe Proposer',
  });
  expect(proposer.checked).toBe(true);
  expect(
    within(points()).getByRole<HTMLInputElement>('checkbox', {name: 'Observe Run'}).checked,
  ).toBe(false);
});
