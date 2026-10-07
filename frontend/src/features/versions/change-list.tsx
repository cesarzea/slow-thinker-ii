import type {ReactElement} from 'react';
import type {Branch, Catalog, ChangeSummary, GraphDocument} from '../../api/index.ts';
import {describeChange} from '../../ui/index.ts';
import {shortTime} from './times.ts';

export interface ChangeListProps {
  readonly changes: readonly ChangeSummary[];
  readonly earlier: ChangeSummary | null;
  readonly documents: ReadonlyMap<number, GraphDocument>;
  readonly catalog: Catalog | null;
  /** The branch shown, for the description of its first change. */
  readonly branch: Branch | undefined;
  readonly busy: boolean;
  readonly onRestore: (change: ChangeSummary) => void;
  readonly onEarlier: () => void;
}

function branchStart(branch: Branch | undefined): string {
  const version = branch?.from_version ?? null;
  const change = branch?.from_change ?? null;
  if (version !== null) return `Started from v${String(version)}`;
  return change === null ? 'Created the graph' : `Started from change ${String(change)}`;
}

/** What a change did, from its document and the previous change of the branch. */
function description(props: ChangeListProps, index: number): string {
  const change = props.changes[index];
  if (change === undefined) return '';
  const previous = props.changes[index + 1] ?? props.earlier;
  if (previous === null) return branchStart(props.branch);
  const before = props.documents.get(previous.change);
  const after = props.documents.get(change.change);
  if (before === undefined || after === undefined) return `Change ${String(change.change)}`;
  return describeChange(before, after, props.catalog);
}

function ChangeAction(props: ChangeListProps & {readonly change: ChangeSummary}): ReactElement {
  if (props.change === props.changes[0]) return <span className="change-current">Current</span>;
  return (
    <button
      type="button"
      className="small ghost"
      disabled={props.busy}
      onClick={() => {
        props.onRestore(props.change);
      }}
    >
      Restore
    </button>
  );
}

function ChangeRow(props: ChangeListProps & {readonly index: number}): ReactElement | null {
  const change = props.changes[props.index];
  if (change === undefined) return null;
  return (
    <li
      className={props.index === 0 ? 'change-row current' : 'change-row'}
      aria-label={`Change ${String(change.change)}`}
    >
      <time className="change-time" dateTime={change.at}>
        {shortTime(change.at)}
      </time>
      <span className="change-text">
        {description(props, props.index)}
        {change.version !== null && (
          <span className="version-mark">{`v${String(change.version)}`}</span>
        )}
      </span>
      <ChangeAction {...props} change={change} />
    </li>
  );
}

/** The branch's changes, newest first, each described and restorable. */
export function ChangeList(props: ChangeListProps): ReactElement {
  if (props.changes.length === 0) return <p className="history-note">No changes yet.</p>;
  return (
    <>
      <ul className="change-list" aria-label="Changes">
        {props.changes.map((change, index) => (
          <ChangeRow key={change.change} {...props} index={index} />
        ))}
      </ul>
      {props.earlier !== null && (
        <button type="button" className="small ghost history-more" onClick={props.onEarlier}>
          Show earlier changes
        </button>
      )}
    </>
  );
}
