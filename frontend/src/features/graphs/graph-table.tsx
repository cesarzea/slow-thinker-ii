import {useCallback} from 'react';
import type {ReactElement} from 'react';
import type {GraphSummary, OperatorClient, RunSummary} from '../../api/index.ts';
import {runStatusText, useRead} from '../../ui/index.ts';

export interface GraphTableProps {
  readonly client: OperatorClient;
  readonly graphs: readonly GraphSummary[];
  /** Runs of every graph, newest first: the first of each graph is its last run. */
  readonly runs: readonly RunSummary[];
  readonly graphHref: (id: string) => string;
  readonly runHref: (graphId: string, runId: string) => string;
}

const COLUMNS = ['Graph', 'Active version', 'Branches', 'Last change', 'Last run'];
const changed = new Intl.DateTimeFormat('en', {dateStyle: 'medium', timeStyle: 'short'});

function BranchCount(props: {readonly client: OperatorClient; readonly id: string}): ReactElement {
  const {client, id} = props;
  const read = useCallback(
    async (signal: AbortSignal) => client.branches(id, signal),
    [client, id],
  );
  const {data} = useRead(read);
  return <>{data === null ? '—' : String(data.length)}</>;
}

function LastRun(props: GraphTableProps & {readonly graph: GraphSummary}): ReactElement {
  const run = props.runs.find((candidate) => candidate.graph_id === props.graph.id);
  if (run === undefined) return <span className="detail">No runs</span>;
  return (
    <a className={`status-pill ${run.status}`} href={props.runHref(run.graph_id, run.run_id)}>
      {runStatusText(run.status, run.reason)}
    </a>
  );
}

function GraphRow(props: GraphTableProps & {readonly graph: GraphSummary}): ReactElement {
  const {graph} = props;
  return (
    <tr>
      <th scope="row">
        <a href={props.graphHref(graph.id)}>{graph.name}</a>
      </th>
      <td>
        {graph.active_version === null ? (
          <span className="detail">None</span>
        ) : (
          <span className="version-pill">{`v${String(graph.active_version)}`}</span>
        )}
      </td>
      <td>
        <BranchCount client={props.client} id={graph.id} />
      </td>
      <td>
        {`Change ${String(graph.latest_change)} `}
        <span className="detail">{`· ${changed.format(new Date(graph.updated_at))}`}</span>
      </td>
      <td>
        <LastRun {...props} />
      </td>
    </tr>
  );
}

/** The graphs, most recently changed first, with their versions, branches and last run. */
export function GraphTable(props: GraphTableProps): ReactElement {
  return (
    <div className="table-frame">
      <table className="data-table" aria-label="Graphs">
        <thead>
          <tr>
            {COLUMNS.map((column) => (
              <th key={column} scope="col">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {props.graphs.map((graph) => (
            <GraphRow key={graph.id} {...props} graph={graph} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
