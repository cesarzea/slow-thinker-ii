import type {Activation} from '../../../api/index.ts';
import type {SaveEvent, StoredChange} from './autosave.ts';
import {afterActivation, afterSave} from './versions.ts';
import type {VersionState} from './versions.ts';

type SaveStatus =
  | {readonly kind: 'idle'}
  | {readonly kind: 'saving'}
  | {readonly kind: 'failed'; readonly message: string};

/** What the server holds for the open branch, and the last save or activation problem. */
export interface PersistenceState {
  readonly status: SaveStatus;
  readonly stored: StoredChange | null;
  readonly versions: VersionState;
  readonly activationFailure: string | null;
}
export type PersistenceEvent =
  | SaveEvent
  | {readonly kind: 'versions'; readonly versions: VersionState}
  | {readonly kind: 'activated'; readonly activation: Activation}
  | {readonly kind: 'activation-failed'; readonly message: string};

function stored(
  state: PersistenceState,
  event: Extract<SaveEvent, {kind: 'stored'}>,
): PersistenceState {
  const {change, at, revision} = event;
  return {
    ...state,
    status: {kind: 'idle'},
    stored: {change, at, revision},
    versions: afterSave(state.versions, state.stored?.change ?? null, change),
  };
}

export function persistenceReducer(
  state: PersistenceState,
  event: PersistenceEvent,
): PersistenceState {
  switch (event.kind) {
    case 'saving':
      return {...state, status: {kind: 'saving'}};
    case 'stored':
      return stored(state, event);
    case 'failed':
      return {...state, status: {kind: 'failed', message: event.message}};
    case 'versions':
      return {...state, versions: event.versions};
    case 'activated':
      return {
        ...state,
        versions: afterActivation(state.versions, event.activation),
        activationFailure: null,
      };
    case 'activation-failed':
      return {...state, activationFailure: event.message};
  }
}
