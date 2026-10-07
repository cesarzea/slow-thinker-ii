import {useCallback} from 'react';
import type {ReactElement} from 'react';
import type {GraphSummary, OperatorClient, RunSummary} from '../../api/index.ts';
import {useRead} from '../../ui/index.ts';
import {GraphTable} from './graph-table.tsx';
import {NewGraphDialog} from './new-graph-dialog.tsx';
import type {NewGraph} from './new-graph-dialog.tsx';
import './graphs.css';

export interface GraphsPageProps {
  readonly client: OperatorClient;
  readonly creating: boolean;
  readonly graphHref: (id: string) => string;
  readonly runHref: (graphId: string, runId: string) => string;
  readonly onNew: () => void;
  readonly onCancelNew: () => void;
  /** Creates the graph on the server and opens it; a failure is shown in the dialog. */
  readonly onCreate: (graph: NewGraph) => Promise<void>;
}
interface Listing {
  readonly graphs: GraphSummary[];
  readonly runs: RunSummary[];
}

function newestFirst(graphs: GraphSummary[]): GraphSummary[] {
  return graphs.toSorted((a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at));
}

/** The graphs and the latest runs; the runs are optional, for the Last run column. */
async function readListing(client: OperatorClient, signal: AbortSignal): Promise<Listing> {
  const [graphs, runs] = await Promise.all([
    client.graphs(signal),
    client.runs(undefined, signal).catch((): RunSummary[] => []),
  ]);
  return {graphs: newestFirst(graphs), runs};
}

function Listed(props: GraphsPageProps & {readonly listing: Listing}): ReactElement {
  if (props.listing.graphs.length === 0)
    return (
      <p className="empty-state">
        No graphs yet. Choose New graph, give it a name, then add a Trigger, an LLM Call and an
        Output from the palette.
      </p>
    );
  return <GraphTable {...props} {...props.listing} />;
}

/** The graph list, most recently changed first, with the creation of a new graph. */
export function GraphsPage(props: GraphsPageProps): ReactElement {
  const {client} = props;
  const read = useCallback(async (signal: AbortSignal) => readListing(client, signal), [client]);
  const {data, error, refresh} = useRead(read);
  return (
    <section className="page" aria-labelledby="graphs-heading">
      <div className="page-header">
        <h1 id="graphs-heading">Graphs</h1>
        <button type="button" className="primary" onClick={props.onNew}>
          New graph
        </button>
      </div>
      {error !== null && (
        <div role="alert" className="page-failure">
          <p>Could not load the graphs. {error}</p>
          <button type="button" onClick={refresh}>
            Try again
          </button>
        </div>
      )}
      {data === null && error === null && <p className="muted">Loading graphs…</p>}
      {data !== null && <Listed {...props} listing={data} />}
      {props.creating && <NewGraphDialog onCreate={props.onCreate} onCancel={props.onCancelNew} />}
    </section>
  );
}
