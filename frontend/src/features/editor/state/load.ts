import {ApiError} from '../../../api/index.ts';
import type {Catalog, GraphDocument, OperatorClient} from '../../../api/index.ts';
import type {SaveTarget, StoredChange} from './autosave.ts';
import {NO_VERSIONS, readVersions} from './versions.ts';
import type {VersionState} from './versions.ts';

/** What the editor opens: the branch's latest change, or a graph not stored yet. */
export interface EditorSource {
  readonly catalog: Catalog;
  readonly document: GraphDocument;
  readonly target: SaveTarget;
  readonly stored: StoredChange | null;
  readonly versions: VersionState;
}
type Stored = Omit<EditorSource, 'catalog'>;

export const MAIN_BRANCH = 'main';

async function storedGraph(
  client: OperatorClient,
  graphId: string,
  branch: string,
  signal: AbortSignal,
): Promise<Stored | null> {
  try {
    const detail = await client.graph(graphId, signal);
    const head = detail.branches.find((item) => item.name === branch) ?? detail.branches[0];
    if (head === undefined)
      throw new ApiError(404, 'branch_not_found', `This graph has no branch “${branch}”.`);
    const [record, versions] = await Promise.all([
      client.change(graphId, head.latest_change, signal),
      readVersions(client, graphId, head.name, signal),
    ]);
    return {
      document: record.document,
      target: {graphId, branch: head.name, exists: true},
      stored: {change: record.change, at: record.at, revision: 0},
      versions,
    };
  } catch (error) {
    if (error instanceof ApiError && error.code === 'graph_not_found') return null;
    throw error;
  }
}

function newGraph(graphId: string, created: GraphDocument | null): Stored {
  if (created?.id !== graphId)
    throw new ApiError(404, 'graph_not_found', 'This graph does not exist.');
  return {
    document: created,
    target: {graphId, branch: MAIN_BRANCH, exists: false},
    stored: null,
    versions: NO_VERSIONS,
  };
}

/**
 * Load the latest change of a branch with the graph's versions; a graph created on the graphs
 * page and not stored yet opens from its document and is stored by the first autosave.
 */
export async function loadEditor(
  client: OperatorClient,
  graphId: string,
  branch: string,
  created: GraphDocument | null,
  signal: AbortSignal,
): Promise<EditorSource> {
  const [catalog, stored] = await Promise.all([
    client.catalog(signal),
    storedGraph(client, graphId, branch, signal),
  ]);
  return {catalog, ...(stored ?? newGraph(graphId, created))};
}
