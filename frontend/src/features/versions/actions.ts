import {ApiError, errorMessage} from '../../api/index.ts';
import type {GraphDocument, OperatorClient, VersionSummary} from '../../api/index.ts';

/** An earlier version activated again: its document, its branch and the new version. */
export interface Reactivated {
  readonly version: number;
  readonly branch: string;
  readonly document: GraphDocument;
}

/**
 * Restores an earlier version's document as a change on its branch, then activates that
 * change as the next version.
 */
export async function activateVersion(
  client: OperatorClient,
  graphId: string,
  version: VersionSummary,
): Promise<Reactivated> {
  const {document} = await client.version(graphId, version.version);
  const saved = await client.saveChange(graphId, version.branch, document);
  const activated = await client.activate(graphId, saved.change);
  return {version: activated.version, branch: activated.branch, document};
}

/** The text of a failed history action, naming the first problem of a refused document. */
export function actionProblem(action: string, error: unknown): string {
  const first = error instanceof ApiError ? error.diagnostics[0]?.message : undefined;
  return `${action} failed. ${first ?? errorMessage(error)}`;
}

/** The next version number: versions are numbered per graph. */
export function nextVersion(versions: readonly VersionSummary[]): number {
  return versions.reduce((highest, version) => Math.max(highest, version.version), 0) + 1;
}

/** The branch name rule of the operator API. */
export const BRANCH_NAME = /^[A-Za-z0-9][A-Za-z0-9 ._-]{0,39}$/u;
