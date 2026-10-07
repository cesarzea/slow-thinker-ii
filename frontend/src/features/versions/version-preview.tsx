import {useCallback} from 'react';
import type {ReactElement, ReactNode} from 'react';
import type {Catalog, GraphDocument, OperatorClient, VersionSummary} from '../../api/index.ts';
import {Dialog, useRead} from '../../ui/index.ts';
import {dayTime} from './times.ts';

/** What the application draws read-only: a document with the catalog it uses. */
export interface PreviewGraph {
  readonly document: GraphDocument;
  readonly catalog: Catalog;
}

interface PreviewProps {
  readonly client: OperatorClient;
  readonly graphId: string;
  readonly version: VersionSummary;
  readonly catalog: Catalog | null;
  /** Why the catalog could not be read, if it could not. */
  readonly catalogError: string | null;
  readonly renderGraph: (graph: PreviewGraph) => ReactNode;
  readonly onClose: () => void;
}

function PreviewCanvas(props: PreviewProps): ReactElement {
  const {client, graphId, version, catalog} = props;
  const read = useCallback(
    async (signal: AbortSignal) => client.version(graphId, version.version, signal),
    [client, graphId, version.version],
  );
  const loaded = useRead(read);
  const error = loaded.error ?? props.catalogError;
  const {data} = loaded;
  return (
    <div className="version-canvas">
      {error !== null && <p role="alert">Could not open the version. {error}</p>}
      {error === null && (data === null || catalog === null) && (
        <p className="muted">Loading the version…</p>
      )}
      {data !== null && catalog !== null && props.renderGraph({document: data.document, catalog})}
    </div>
  );
}

/** A version's canvas, read only, in a dialog. */
export function VersionPreview(props: PreviewProps): ReactElement {
  const {version} = props;
  const subtitle = `${version.branch} · ${dayTime(version.created_at)} · change ${String(version.change)}`;
  return (
    <Dialog
      title={`Version ${String(version.version)} · read only`}
      subtitle={subtitle}
      onClose={props.onClose}
      wide
    >
      <PreviewCanvas {...props} />
      <div className="dialog-actions">
        <button type="button" onClick={props.onClose}>
          Close
        </button>
      </div>
    </Dialog>
  );
}
