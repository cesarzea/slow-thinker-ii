import {useCallback, useId, useState} from 'react';
import type {ReactElement, ReactNode} from 'react';
import type {
  BranchOrigin,
  Catalog,
  GraphDocument,
  OperatorClient,
  VersionSummary,
} from '../../api/index.ts';
import {useRead} from '../../ui/index.ts';
import type {ReadResult} from '../../ui/index.ts';
import {nextVersion} from './actions.ts';
import {BranchDialog} from './branch-dialog.tsx';
import {HistoryContent} from './history-content.tsx';
import {usePanelActions} from './panel-actions.ts';
import type {HistoryContext, PanelActions} from './panel-actions.ts';
import {useChangeDocuments} from './use-change-documents.ts';
import {useHistory} from './use-history.ts';
import type {History} from './use-history.ts';
import {VersionPreview} from './version-preview.tsx';
import type {PreviewGraph} from './version-preview.tsx';
import './versions.css';

export type HistoryPanelProps = HistoryContext & {
  readonly client: OperatorClient;
  /** Draws a document read only, for “Open read-only”. */
  readonly renderGraph: (graph: PreviewGraph) => ReactNode;
};
type Shown = {readonly branch: BranchOrigin} | {readonly preview: VersionSummary} | null;
interface DialogProps {
  readonly panel: HistoryPanelProps;
  readonly shown: Shown;
  readonly history: History;
  readonly catalog: ReadResult<Catalog>;
  readonly actions: PanelActions;
  readonly close: () => void;
}

function HistoryHead(props: {readonly id: string; readonly onClose: () => void}): ReactElement {
  return (
    <header className="history-head">
      <svg className="history-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M3 12a9 9 0 1 0 3-6.7L3 8M3 3v5h5M12 7v5l3 2" />
      </svg>
      <h2 id={props.id}>History</h2>
      <button
        type="button"
        className="history-close"
        aria-label="Close history"
        onClick={props.onClose}
      >
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M18 6 6 18M6 6l12 12" />
        </svg>
      </button>
    </header>
  );
}

function BranchCreation({
  history,
  actions,
  shown,
  close,
}: DialogProps & {readonly shown: {readonly branch: BranchOrigin}}): ReactElement {
  return (
    <BranchDialog
      versions={history.detail?.versions ?? []}
      changes={history.changes}
      origin={shown.branch}
      onCancel={close}
      onCreate={async (name, origin) => {
        const problem = await actions.createBranch(name, origin);
        if (problem === null) close();
        return problem;
      }}
    />
  );
}

function PanelDialogs(props: DialogProps): ReactElement | null {
  const {shown, catalog} = props;
  if (shown === null) return null;
  if ('branch' in shown) return <BranchCreation {...props} shown={shown} />;
  return (
    <VersionPreview
      {...props.panel}
      version={shown.preview}
      catalog={catalog.data}
      catalogError={catalog.error}
      onClose={props.close}
    />
  );
}

/** The panel's data and actions. */
function usePanel(props: HistoryPanelProps): Omit<DialogProps, 'shown' | 'close' | 'panel'> & {
  readonly documents: ReadonlyMap<number, GraphDocument>;
} {
  const {client, graphId, branch} = props;
  const stamp = `${String(props.latestChange)}:${String(props.activeVersion)}`;
  const history = useHistory({client, graphId, branch}, stamp);
  const read = useCallback(async (signal: AbortSignal) => client.catalog(signal), [client]);
  const catalog = useRead(read);
  const listed = [...history.changes, ...(history.earlier === null ? [] : [history.earlier])];
  const documents = useChangeDocuments(
    client,
    graphId,
    listed.map((change) => change.change),
  );
  const actions = usePanelActions({client, context: props, documents, refresh: history.refresh});
  return {history, catalog, documents, actions};
}

/**
 * The History panel of the editor: the working copy, the branches, the versions on their
 * branch lanes and the changes of the open branch.
 */
export function HistoryPanel(props: HistoryPanelProps): ReactElement {
  const id = useId();
  const panel = usePanel(props);
  const [shown, setShown] = useState<Shown>(null);
  const close = (): void => {
    setShown(null);
  };
  return (
    <section className="history-panel" aria-labelledby={id}>
      <HistoryHead id={id} onClose={props.onClose} />
      <HistoryContent
        {...props}
        {...panel}
        catalog={panel.catalog.data}
        next={nextVersion(panel.history.detail?.versions ?? [])}
        onNewBranch={(origin) => {
          setShown({branch: origin});
        }}
        onOpen={(version) => {
          setShown({preview: version});
        }}
      />
      <PanelDialogs {...panel} panel={props} shown={shown} close={close} />
    </section>
  );
}
