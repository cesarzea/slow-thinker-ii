import type {ReactElement} from 'react';
import type {OperatorClient} from '../api/index.ts';
import {ActivityPage} from '../features/activity/index.ts';
import {RunsPage} from '../features/history/index.ts';
import {routeHash} from './routes.ts';
import type {Navigate} from './use-route.ts';

interface RunPageProps {
  readonly client: OperatorClient;
  readonly navigate: Navigate;
  readonly graphId: string;
  readonly runId: string;
}

/** The hash of a run: its graph's editor in run mode, showing that run. */
export const runHref = (graphId: string, runId: string): string =>
  routeHash({kind: 'run', graphId, runId});

/** The activity of a run, with the link back to the run. */
export function Activity(props: Omit<RunPageProps, 'navigate'>): ReactElement {
  const {graphId, runId} = props;
  return (
    <ActivityPage
      client={props.client}
      graphId={graphId}
      runId={runId}
      runHref={runHref(graphId, runId)}
    />
  );
}

/** The runs of every graph or of one graph; the Graph filter moves between both routes. */
export function Runs(
  props: Omit<RunPageProps, 'runId' | 'graphId'> & {
    readonly graphId: string | null;
  },
): ReactElement {
  return (
    <RunsPage
      client={props.client}
      graphId={props.graphId}
      runHref={runHref}
      onGraphChange={(graphId) => {
        props.navigate({kind: 'runs', graphId});
      }}
    />
  );
}
