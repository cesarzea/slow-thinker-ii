import {screen, within} from '@testing-library/react';
import type {GraphDocument} from '../../src/api/index.ts';
import {appApi, connectApp} from './app-harness.tsx';
import type {FakeApi} from './fake-api.ts';
import {j3} from './contract.ts';
import {j3Events} from './j3-events.ts';

const runHash = '#/graphs/funny-story-with-review/runs/run-1';

/** The J3 graph with its recorded run, opened in run mode at that run. */
export async function openRun(): Promise<FakeApi> {
  const api = appApi(j3).on('GET /runs/run-1/events', {
    status: 200,
    body: {events: j3Events, last_seq: j3Events.length, finished: true},
  });
  await connectApp(runHash);
  await screen.findByRole('navigation', {name: 'Observation points'});
  return api;
}

export const points = (): HTMLElement =>
  screen.getByRole('navigation', {name: 'Observation points'});
export const runPanel = (): HTMLElement => screen.getByRole('complementary', {name: 'Run'});
export const feed = (): HTMLElement =>
  within(runPanel()).getByRole('region', {name: /^(Observed|Activity of)/u});
export const items = (): string[] =>
  within(feed())
    .queryAllByRole('listitem')
    .map((item) => item.querySelector('.feed-point')?.textContent ?? '');

/** The observed points the last saved change kept. */
export function savedObserve(api: FakeApi): unknown {
  const body = api.last('POST /graphs/funny-story-with-review/changes')?.body as
    {document: GraphDocument} | undefined;
  return body?.document.view?.observe;
}
