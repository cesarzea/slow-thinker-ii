import {useCallback, useState} from 'react';
import {documentPoints, isPoint} from '../../api/index.ts';
import type {Catalog, GraphDocument, OperatorClient, PointId, RunSource} from '../../api/index.ts';
import {useRead} from '../../ui/index.ts';
import type {EditorModel} from './state/use-editor.ts';

/** What run mode shows: nothing executed yet, or a run, and the point it focuses. */
export interface Mode {
  readonly runId: string | null;
  readonly focus: PointId | null;
}

/**
 * The observed points that still exist; every connection until a choice is saved. A whole
 * node saved before nodes had facets stands for all of them.
 */
export function observedPoints(document: GraphDocument, catalog: Catalog): Set<PointId> {
  const existing = documentPoints(document, catalog);
  const saved = document.view?.observe;
  if (saved === undefined) return new Set(existing.filter((id) => id.startsWith('connection:')));
  const expanded = saved.flatMap((id): PointId[] =>
    isPoint(id) && existing.includes(id)
      ? [id]
      : existing.filter((item) => item.startsWith(`${id}/`)),
  );
  return new Set(expanded);
}

export function runBlock(editor: EditorModel): string | null {
  if (editor.state.diagnostics.some((item) => item.severity === 'error'))
    return 'Fix the problems in the graph to execute it.';
  return editor.persistence.stored === null ? 'The graph is not saved yet.' : null;
}

/** Saves pending edits, then names the branch's latest change: what is on screen. */
export async function prepare(
  client: OperatorClient,
  editor: EditorModel,
): Promise<RunSource | null> {
  if (!(await editor.persistence.flush())) return null;
  const {graphId, branch} = editor.persistence.target;
  const [latest] = await client.changes(graphId, {branch, limit: 1});
  return latest === undefined ? null : {change: latest.change};
}

/** The document a run executed, or null before Execute. */
export function useExecuted(client: OperatorClient, runId: string | null): GraphDocument | null {
  const read = useCallback(
    async (signal: AbortSignal): Promise<GraphDocument | null> =>
      runId === null ? null : client.runDocument(await client.run(runId, signal), signal),
    [client, runId],
  );
  return useRead(read).data;
}

/** What run mode shows: the executed document laid out and observed as the working copy. */
export function shownDocument(
  working: GraphDocument,
  executed: GraphDocument | null,
): GraphDocument {
  if (executed === null) return working;
  const {port_sides: sides, view} = working;
  return {
    ...executed,
    layout: {...executed.layout, ...working.layout},
    ...(sides === undefined ? {} : {port_sides: sides}),
    ...(view === undefined ? {} : {view}),
  };
}

/** Follows the route: a run in the address opens it; leaving it there closes it. */
export function useRouteRun(
  routeRun: string | null,
  mode: Mode | null,
  setMode: (mode: Mode | null) => void,
): void {
  const [seen, setSeen] = useState<string | null | undefined>(undefined);
  if (seen === routeRun) return;
  setSeen(routeRun);
  if (routeRun !== null && mode?.runId !== routeRun) setMode({runId: routeRun, focus: null});
  if (routeRun === null && mode !== null && mode.runId !== null) setMode(null);
}
