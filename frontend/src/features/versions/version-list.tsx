import {useId} from 'react';
import type {ReactElement} from 'react';
import type {GraphDetail, VersionSummary} from '../../api/index.ts';
import {LaneCell, lanesWidth} from './lane-cell.tsx';
import {laneGraph} from './lanes.ts';
import type {LaneRow} from './lanes.ts';
import {dayTime} from './times.ts';

export interface VersionActions {
  readonly busy: boolean;
  /** The number the next activation gets. */
  readonly next: number;
  readonly onActivate: (version: VersionSummary) => void;
  readonly onBranch: (version: VersionSummary) => void;
  readonly onOpen: (version: VersionSummary) => void;
}

type RowProps = VersionActions & {
  readonly row: LaneRow;
  readonly lanes: number;
  readonly active: boolean;
};

const GLYPHS = {
  branch:
    'M6 3.5v13M6 16.5a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5M18 3a2.5 2.5 0 1 0 0 5a2.5 2.5 0 1 0 0-5M18 8c0 5-6 4-12 8.5',
  open: 'M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12zM12 9a3 3 0 1 0 0 6a3 3 0 1 0 0-6',
} as const;

/** A compact button named by its label, which also shows as its tooltip. */
function IconButton(props: {
  readonly label: string;
  readonly glyph: keyof typeof GLYPHS;
  readonly disabled: boolean;
  readonly onClick: () => void;
}): ReactElement {
  return (
    <button
      type="button"
      className="small ghost icon"
      aria-label={props.label}
      title={props.label}
      disabled={props.disabled}
      onClick={props.onClick}
    >
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d={GLYPHS[props.glyph]} />
      </svg>
    </button>
  );
}

/** Activate as the next version (except the active one), branch from it, or look at it. */
function VersionButtons(props: RowProps): ReactElement {
  const {version} = props.row;
  const act = (action: (version: VersionSummary) => void) => (): void => {
    action(version);
  };
  const branch = {label: 'Branch from here', glyph: 'branch', disabled: props.busy} as const;
  const open = {label: 'Open read-only', glyph: 'open', disabled: false} as const;
  return (
    <div className="version-actions">
      {!props.active && (
        <button
          type="button"
          className="small"
          disabled={props.busy}
          onClick={act(props.onActivate)}
        >
          {`Activate as v${String(props.next)}`}
        </button>
      )}
      <IconButton {...branch} onClick={act(props.onBranch)} />
      <IconButton {...open} onClick={act(props.onOpen)} />
    </div>
  );
}

function VersionRow(props: RowProps): ReactElement {
  const id = useId();
  const {version} = props.row;
  return (
    <li
      className={props.active ? 'version-row active' : 'version-row'}
      aria-labelledby={id}
      style={{paddingLeft: `${String(14 + lanesWidth(props.lanes))}px`}}
    >
      <LaneCell row={props.row} lanes={props.lanes} active={props.active} />
      <span className="lane-badge">{`v${String(version.version)}`}</span>
      <div className="version-text">
        <p>
          <span id={id}>{`Version ${String(version.version)}`}</span>
          {props.active && ' · Active'}
        </p>
        <p className="version-meta">
          {`${version.branch} · ${dayTime(version.created_at)} · change ${String(version.change)}`}
        </p>
        <VersionButtons {...props} />
      </div>
    </li>
  );
}

/** The versions, newest first, on one lane per branch with the active one highlighted. */
export function VersionList(props: VersionActions & {readonly detail: GraphDetail}): ReactElement {
  const graph = laneGraph(props.detail.versions, props.detail.branches);
  if (graph.rows.length === 0)
    return (
      <p className="history-note">
        No versions yet. Activate the working copy to create version 1.
      </p>
    );
  return (
    <ul className="version-list" aria-label="Versions">
      {graph.rows.map((row) => (
        <VersionRow
          key={row.version.version}
          {...props}
          row={row}
          lanes={graph.lanes.length}
          active={row.version.version === props.detail.active_version}
        />
      ))}
    </ul>
  );
}
