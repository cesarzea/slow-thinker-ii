import type {ReactElement} from 'react';
import type {RunRow} from './run-rows.ts';

export type RunLink = (graphId: string, runId: string) => string;

interface TableProps {
  readonly rows: readonly RunRow[];
  readonly runHref: RunLink;
}

const COLUMNS = ['Run', 'Version', 'Status', 'Started', 'Duration', 'LLM calls', 'Cost'];
const NUMERIC: ReadonlySet<string> = new Set(['Version', 'Duration', 'LLM calls', 'Cost']);

function RunRowView(props: Omit<TableProps, 'rows'> & {readonly row: RunRow}): ReactElement {
  const {row} = props;
  return (
    <tr>
      <th scope="row">
        <a href={props.runHref(row.graphId, row.runId)}>{row.name}</a>
      </th>
      <td className="number">{row.version}</td>
      <td>
        <span className={`status-pill ${row.status}`}>{row.statusText}</span>
      </td>
      <td>
        <time dateTime={row.createdAt}>{row.started}</time>
      </td>
      <td className="number">{row.duration}</td>
      <td className="number">{row.llmCalls}</td>
      <td className="number">{row.cost}</td>
    </tr>
  );
}

/** The runs, newest first, each linked to its graph's editor in run mode. */
export function RunsTable(props: TableProps): ReactElement {
  return (
    <div className="table-frame">
      <table className="data-table runs-table" aria-label="Runs">
        <thead>
          <tr>
            {COLUMNS.map((column) => (
              <th key={column} scope="col" className={NUMERIC.has(column) ? 'number' : undefined}>
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {props.rows.map((row) => (
            <RunRowView key={row.runId} row={row} runHref={props.runHref} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
