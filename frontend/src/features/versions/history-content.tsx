import type {ReactElement} from 'react';
import type {
  BranchOrigin,
  Catalog,
  GraphDetail,
  GraphDocument,
  VersionSummary,
} from '../../api/index.ts';
import {BranchBar} from './branch-bar.tsx';
import {ChangeList} from './change-list.tsx';
import type {HistoryContext, PanelActions} from './panel-actions.ts';
import type {History} from './use-history.ts';
import {VersionList} from './version-list.tsx';
import {WorkingCopy} from './working-copy.tsx';

export type ContentProps = HistoryContext & {
  readonly history: History;
  readonly catalog: Catalog | null;
  readonly documents: ReadonlyMap<number, GraphDocument>;
  readonly actions: PanelActions;
  /** The number the next activation gets. */
  readonly next: number;
  readonly onNewBranch: (origin: BranchOrigin) => void;
  readonly onOpen: (version: VersionSummary) => void;
};
type LoadedProps = ContentProps & {readonly detail: GraphDetail};

/** Where a new branch starts by default: the open branch's version, else its latest change. */
function defaultOrigin(props: LoadedProps): BranchOrigin {
  const record = props.detail.branches.find((branch) => branch.name === props.branch);
  const version = record?.head_version ?? props.detail.active_version;
  if (version !== null) return {version};
  return {change: record?.latest_change ?? props.detail.latest_change};
}

/** The working copy of the open branch and the choice of branch. */
function BranchState(props: LoadedProps): ReactElement {
  const {history, actions, detail} = props;
  return (
    <>
      <WorkingCopy
        busy={actions.busy}
        next={props.next}
        changes={history.changes}
        earlier={history.earlier}
        detail={detail}
        branch={props.branch}
        onActivate={actions.activateChange}
      />
      <BranchBar
        branches={detail.branches}
        branch={props.branch}
        busy={actions.busy}
        onChange={props.onBranchChange}
        onNew={() => {
          props.onNewBranch(defaultOrigin(props));
        }}
      />
    </>
  );
}

function Changes(props: LoadedProps): ReactElement {
  const {history, detail} = props;
  return (
    <ChangeList
      changes={history.changes}
      earlier={history.earlier}
      documents={props.documents}
      catalog={props.catalog}
      branch={detail.branches.find((branch) => branch.name === props.branch)}
      busy={props.actions.busy}
      onRestore={props.actions.restore}
      onEarlier={history.showEarlier}
    />
  );
}

function Loaded(props: LoadedProps): ReactElement {
  return (
    <>
      <BranchState {...props} />
      <h3 className="history-section-title">Versions</h3>
      <VersionList
        busy={props.actions.busy}
        next={props.next}
        detail={props.detail}
        onActivate={props.actions.activateVersion}
        onBranch={(version) => {
          props.onNewBranch({version: version.version});
        }}
        onOpen={props.onOpen}
      />
      <h3 className="history-section-title">Changes</h3>
      <Changes {...props} />
    </>
  );
}

/** The panel's scrolling body: problems, then the history once it is read. */
export function HistoryContent(props: ContentProps): ReactElement {
  const {history, actions} = props;
  return (
    <div className="history-body">
      {actions.problem !== null && <p role="alert">{actions.problem}</p>}
      {history.error !== null && (
        <div role="alert" className="history-failure">
          <p>Could not read the history. {history.error}</p>
          <button type="button" className="small" onClick={history.refresh}>
            Try again
          </button>
        </div>
      )}
      {history.detail === null ? (
        history.error === null && <p className="history-note">Loading the history…</p>
      ) : (
        <Loaded {...props} detail={history.detail} />
      )}
    </div>
  );
}
