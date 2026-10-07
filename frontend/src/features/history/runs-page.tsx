import {useCallback, useId} from 'react';
import type {ReactElement} from 'react';
import type {GraphSummary, OperatorClient, RunSummary} from '../../api/index.ts';
import {useRead} from '../../ui/index.ts';
import {runRows} from './run-rows.ts';
import {RunsTable} from './runs-table.tsx';
import type {RunLink} from './runs-table.tsx';
import {useRunList} from './use-run-list.ts';
import './history.css';

export interface RunsPageProps {
  readonly client: OperatorClient;
  /** The graph whose runs are listed, or `null` for the runs of every graph. */
  readonly graphId: string | null;
  readonly runHref: RunLink;
  /** The Graph filter changed: `null` selects all graphs. */
  readonly onGraphChange: (graphId: string | null) => void;
}
type Names = ReadonlyMap<string, string>;
type ListProps = RunsPageProps & {readonly names: Names};

/** Graph names by id, including the listed graph even when it is not known. */
function graphNames(graphs: readonly GraphSummary[] | null, graphId: string | null): Names {
  const names = new Map((graphs ?? []).map((graph) => [graph.id, graph.name]));
  if (graphId !== null && !names.has(graphId)) names.set(graphId, graphId);
  return names;
}

function GraphFilter(props: {
  readonly names: Names;
  readonly value: string | null;
  readonly onChange: (graphId: string | null) => void;
}): ReactElement {
  const id = useId();
  const options = [...props.names].toSorted(([, a], [, b]) => a.localeCompare(b, 'en'));
  return (
    <div className="graph-filter">
      <label htmlFor={id}>Graph</label>
      <select
        id={id}
        value={props.value ?? ''}
        onChange={(event) => {
          props.onChange(event.target.value === '' ? null : event.target.value);
        }}
      >
        <option value="">All graphs</option>
        {options.map(([graphId, name]) => (
          <option key={graphId} value={graphId}>
            {name}
          </option>
        ))}
      </select>
    </div>
  );
}

function RunsBody(props: ListProps & {readonly runs: readonly RunSummary[]}): ReactElement {
  if (props.runs.length === 0)
    return (
      <p className="empty-state">
        {props.graphId === null
          ? 'No runs yet. Open a graph and choose Run to start one.'
          : 'This graph has no runs yet. Open it and choose Run to start one.'}
      </p>
    );
  const rows = runRows(props.runs, props.names);
  return <RunsTable rows={rows} runHref={props.runHref} />;
}

function RunListView(props: ListProps): ReactElement {
  const list = useRunList(props.client, props.graphId);
  return (
    <>
      {list.error !== null && (
        <div role="alert" className="page-failure">
          <p>Could not load the runs. {list.error}</p>
          <button type="button" onClick={list.retry}>
            Try again
          </button>
        </div>
      )}
      {list.runs === null ? (
        list.error === null && <p className="muted">Loading the runs…</p>
      ) : (
        <RunsBody {...props} runs={list.runs} />
      )}
    </>
  );
}

/**
 * The runs of every graph or of one graph, newest first, refreshed while any is active.
 * The list starts afresh when the graph changes; the heading and the filter stay.
 */
export function RunsPage(props: RunsPageProps): ReactElement {
  const id = useId();
  const {client, graphId} = props;
  const read = useCallback(async (signal: AbortSignal) => client.graphs(signal), [client]);
  const names = graphNames(useRead(read).data, graphId);
  return (
    <section className="page" aria-labelledby={id}>
      <div className="page-header">
        <h1 id={id}>{graphId === null ? 'Runs' : `Runs of ${names.get(graphId) ?? graphId}`}</h1>
        <GraphFilter names={names} value={graphId} onChange={props.onGraphChange} />
      </div>
      <RunListView key={graphId ?? ''} {...props} names={names} />
    </section>
  );
}
