import {useEffect, useReducer, useState} from 'react';
import {errorMessage} from '../../../api/index.ts';
import type {GraphDocument, OperatorClient} from '../../../api/index.ts';
import {Autosaver} from './autosave.ts';
import type {SaveTarget, StoredChange} from './autosave.ts';
import {persistenceReducer} from './persistence-state.ts';
import type {PersistenceEvent, PersistenceState} from './persistence-state.ts';
import {readVersions} from './versions.ts';
import type {VersionState} from './versions.ts';

export interface PersistenceSource {
  readonly target: SaveTarget;
  readonly stored: StoredChange | null;
  readonly versions: VersionState;
}
/** The working copy's saving, the open branch and the graph's versions. */
export interface Persistence extends PersistenceState {
  readonly target: SaveTarget;
  /** True while the working copy has edits that are not stored yet. */
  readonly unsaved: boolean;
  /** Save pending edits now; true when everything is stored. */
  readonly flush: () => Promise<boolean>;
  readonly activate: () => Promise<void>;
  readonly refreshVersions: () => Promise<void>;
}

function initialPersistence(source: PersistenceSource): PersistenceState {
  return {
    status: {kind: 'idle'},
    stored: source.stored,
    versions: source.versions,
    activationFailure: null,
  };
}

/** Save what is pending, then activate the latest change as the next version. */
function useActivation(
  client: OperatorClient,
  graphId: string,
  saver: Autosaver,
  report: (event: PersistenceEvent) => void,
): () => Promise<void> {
  return async () => {
    await saver.flush();
    const latest = saver.latest;
    if (latest === null) return;
    try {
      report({kind: 'activated', activation: await client.activate(graphId, latest.change)});
    } catch (error) {
      report({kind: 'activation-failed', message: errorMessage(error)});
    }
  };
}

function useAutosaver(
  client: OperatorClient,
  source: PersistenceSource,
  report: (event: PersistenceEvent) => void,
): Autosaver {
  const [saver] = useState(() => new Autosaver(client, source, report));
  useEffect(
    () => () => {
      void saver.flush();
    },
    [saver],
  );
  return saver;
}

/**
 * Autosave the working copy as changes of the open branch, and activate the latest change
 * as the graph's next version. Pending edits are saved when the editor closes.
 */
export function usePersistence(
  client: OperatorClient,
  source: PersistenceSource,
  document: GraphDocument,
  revision: number,
): Persistence {
  const [state, dispatch] = useReducer(persistenceReducer, source, initialPersistence);
  const saver = useAutosaver(client, source, dispatch);
  const storedRevision = state.stored?.revision;
  useEffect(() => {
    if (storedRevision !== revision) saver.schedule(document, revision);
  }, [saver, document, revision, storedRevision]);
  const {graphId, branch} = source.target;
  const activate = useActivation(client, graphId, saver, dispatch);
  return {
    ...state,
    target: source.target,
    unsaved: storedRevision !== revision,
    flush: async () => saver.flush(),
    activate,
    refreshVersions: async () => {
      try {
        dispatch({kind: 'versions', versions: await readVersions(client, graphId, branch)});
      } catch {
        // The badge keeps the versions it knows; the next change or activation corrects it.
      }
    },
  };
}
