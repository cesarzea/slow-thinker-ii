import type {ReactElement} from 'react';
import type {ChangeSummary, GraphDetail} from '../../api/index.ts';
import {clockTime} from './times.ts';

interface WorkingCopyProps {
  readonly branch: string;
  readonly detail: GraphDetail;
  readonly changes: readonly ChangeSummary[];
  readonly earlier: ChangeSummary | null;
  readonly next: number;
  readonly busy: boolean;
  readonly onActivate: (change: number) => void;
}

const plural = (count: string, one: boolean): string => `${count} ${one ? 'change' : 'changes'}`;

/** The open branch's latest version and the change it was activated from. */
function branchHead(props: WorkingCopyProps): {version: number | null; change: number | null} {
  const record = props.detail.branches.find((branch) => branch.name === props.branch);
  const version = record?.head_version ?? null;
  const change = props.detail.versions.find((item) => item.version === version)?.change;
  return {version, change: change ?? null};
}

/** “2 changes since version 3”, counted in the changes read so far. */
function sinceHead(props: WorkingCopyProps): string {
  const head = branchHead(props);
  const newer = props.changes.filter((item) => head.change === null || item.change > head.change);
  const more = props.earlier !== null && newer.length === props.changes.length ? '+' : '';
  const count = plural(`${String(newer.length)}${more}`, newer.length === 1 && more === '');
  if (head.version === null) return `${count}, no version yet`;
  const version = String(head.version);
  return newer.length === 0
    ? `No changes since version ${version}`
    : `${count} since version ${version}`;
}

/** The branch's working copy: its changes since its last version and its activation. */
export function WorkingCopy(props: WorkingCopyProps): ReactElement {
  const latest = props.changes[0];
  const pending = latest?.version === null;
  return (
    <section className="working-copy" aria-label="Working copy">
      <h3>
        Working copy <span className="branch-chip">{props.branch}</span>
      </h3>
      <p>
        {sinceHead(props)}
        {latest !== undefined && ` · saved ${clockTime(latest.at)}`}
      </p>
      <button
        type="button"
        className="primary small"
        disabled={!pending || props.busy}
        onClick={() => {
          if (latest !== undefined) props.onActivate(latest.change);
        }}
      >
        {`Activate as v${String(props.next)}`}
      </button>
    </section>
  );
}
