import {useMemo} from 'react';
import type {ReactElement} from 'react';
import type {OperatorClient} from '../api/index.ts';
import {ObservationFeed} from '../features/activity/index.ts';
import {ComponentsPage} from '../features/catalog/index.ts';
import {Editor, newGraphDocument} from '../features/editor/index.ts';
import type {DraftModel, RenderRun} from '../features/editor/index.ts';
import {RunPanel} from '../features/runs/index.ts';
import {GraphsPage} from '../features/graphs/index.ts';
import {historyPanel} from './history.tsx';
import {GRAPHS, routeHash} from './routes.ts';
import type {Route} from './routes.ts';
import {Activity, Runs, runHref} from './run-pages.tsx';
import type {Navigate} from './use-route.ts';

export interface PagesProps {
  readonly client: OperatorClient;
  readonly route: Route;
  readonly navigate: Navigate;
  readonly onDraft: (model: DraftModel | null) => void;
}

const editorHref = (graphId: string): string => routeHash({kind: 'editor', graphId});

function Graphs(props: PagesProps & {readonly creating: boolean}): ReactElement {
  return (
    <GraphsPage
      client={props.client}
      creating={props.creating}
      graphHref={editorHref}
      onNew={() => {
        props.navigate({kind: 'graphs', creating: true});
      }}
      onCancelNew={() => {
        props.navigate(GRAPHS);
      }}
      runHref={runHref}
      onCreate={async ({id, name}) => {
        await props.client.createGraph(newGraphDocument(id, name));
        props.navigate({kind: 'editor', graphId: id});
      }}
    />
  );
}

/** Run mode's panel, with the observed points' events from the activity feature. */
function runPanel(client: OperatorClient): RenderRun {
  return function InPlaceRun(context) {
    return (
      <RunPanel
        {...context}
        client={client}
        feed={(runId) => (
          <ObservationFeed
            client={client}
            runId={runId}
            points={context.points}
            focus={context.focus}
            labels={context.labels}
            onClearFocus={context.onClearFocus}
          />
        )}
      />
    );
  };
}

function GraphEditor(
  props: PagesProps & {readonly graphId: string; readonly runId: string | null},
): ReactElement {
  const {client, graphId, navigate} = props;
  const renderHistory = useMemo(() => historyPanel(client), [client]);
  const renderRun = useMemo(() => runPanel(client), [client]);
  return (
    <Editor
      client={client}
      graphId={props.graphId}
      created={null}
      runsHref={routeHash({kind: 'runs', graphId: props.graphId})}
      graphsHref={routeHash(GRAPHS)}
      renderHistory={renderHistory}
      renderRun={renderRun}
      runId={props.runId}
      onRunChange={(runId) => {
        navigate(runId === null ? {kind: 'editor', graphId} : {kind: 'run', graphId, runId}, false);
      }}
      onDraft={props.onDraft}
    />
  );
}

/** The page of the current route. */
export function Pages(props: PagesProps): ReactElement {
  const {route, client, navigate} = props;
  switch (route.kind) {
    case 'graphs':
      return <Graphs {...props} creating={route.creating} />;
    case 'editor':
    case 'run':
      return (
        <GraphEditor
          key={route.graphId}
          {...props}
          graphId={route.graphId}
          runId={route.kind === 'run' ? route.runId : null}
        />
      );
    case 'activity':
      return (
        <Activity key={route.runId} client={client} graphId={route.graphId} runId={route.runId} />
      );
    case 'runs':
      return <Runs client={client} navigate={navigate} graphId={route.graphId} />;
    case 'components':
      return <ComponentsPage client={client} />;
  }
}
