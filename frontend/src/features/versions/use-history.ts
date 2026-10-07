import {useEffect, useState} from 'react';
import type {Dispatch, SetStateAction} from 'react';
import {errorMessage} from '../../api/index.ts';
import type {ChangeSummary, GraphDetail, OperatorClient} from '../../api/index.ts';

/** Changes shown per page. */
const PAGE = 30;

interface HistoryState {
  readonly branch: string | null;
  readonly detail: GraphDetail | null;
  /** The branch's changes shown, newest first. */
  readonly changes: readonly ChangeSummary[];
  /** The change just before the oldest one shown, when there are earlier ones. */
  readonly earlier: ChangeSummary | null;
  readonly error: string | null;
}
export type History = HistoryState & {
  readonly refresh: () => void;
  readonly showEarlier: () => void;
};
type SetHistory = Dispatch<SetStateAction<HistoryState>>;
interface Source {
  readonly client: OperatorClient;
  readonly graphId: string;
  readonly branch: string;
}

const EMPTY: HistoryState = {branch: null, detail: null, changes: [], earlier: null, error: null};

function paged(changes: readonly ChangeSummary[]): Pick<HistoryState, 'changes' | 'earlier'> {
  return {changes: changes.slice(0, PAGE), earlier: changes[PAGE] ?? null};
}

async function readHistory(source: Source, signal: AbortSignal): Promise<HistoryState> {
  const {client, graphId, branch} = source;
  const [detail, list] = await Promise.all([
    client.graph(graphId, signal),
    client.changes(graphId, {branch, limit: PAGE + 1}, signal),
  ]);
  return {branch, detail, ...paged(list), error: null};
}

function failed(setState: SetHistory): (error: unknown) => void {
  return (error) => {
    setState((current) => ({...current, error: errorMessage(error)}));
  };
}

/** Appends the page of changes before the oldest one shown. */
function readEarlier(source: Source, oldest: number, setState: SetHistory): void {
  const query = {branch: source.branch, before: oldest, limit: PAGE + 1};
  source.client.changes(source.graphId, query).then((list) => {
    const more = paged(list);
    setState((now) => ({
      ...now,
      changes: [...now.changes, ...more.changes],
      earlier: more.earlier,
    }));
  }, failed(setState));
}

/** Reads the history whenever the source, the stamp or the revision changes. */
function useHistoryRead(source: Source, key: string, setState: SetHistory): void {
  const {client, graphId, branch} = source;
  useEffect(() => {
    const controller = new AbortController();
    const report = failed(setState);
    readHistory({client, graphId, branch}, controller.signal).then(
      (read) => {
        if (!controller.signal.aborted) setState(read);
      },
      (error: unknown) => {
        if (!controller.signal.aborted) report(error);
      },
    );
    return () => {
      controller.abort();
    };
  }, [client, graphId, branch, key, setState]);
}

/**
 * The graph's branches and versions and the newest changes of one branch, read again
 * whenever `stamp` changes, for example after a save or an activation.
 */
export function useHistory(source: Source, stamp: string): History {
  const [state, setState] = useState<HistoryState>(EMPTY);
  const [revision, setRevision] = useState(0);
  useHistoryRead(source, `${stamp}#${String(revision)}`, setState);
  const current = state.branch === source.branch ? state : {...EMPTY, error: state.error};
  const oldest = current.changes.at(-1)?.change;
  return {
    ...current,
    refresh: () => {
      setRevision((value) => value + 1);
    },
    showEarlier: () => {
      if (oldest !== undefined) readEarlier(source, oldest, setState);
    },
  };
}
