import {DefinitionError} from '../../api/index.ts';
import type {DraftState} from './types.ts';

export const MAX_SOURCE_BYTES = 1_048_576;

export class DraftError extends Error {}

export function initialDraft(): DraftState {
  return {
    source: '',
    baseline: '',
    selectedSource: '',
    loaded: false,
    pending: 'load',
    validation: null,
    message: null,
    issues: [],
    frozenSource: null,
    uncertain: false,
  };
}

export function sourceSize(source: string): number {
  return new TextEncoder().encode(source).byteLength;
}

export function locked(state: DraftState): boolean {
  return (
    !state.loaded ||
    state.pending === 'save' ||
    state.pending === 'import' ||
    state.pending === 'draft' ||
    state.uncertain
  );
}

export function changeSource(state: DraftState, source: string): DraftState {
  return {...state, source, pending: null, validation: null, message: null, issues: []};
}

export function rejected(state: DraftState, error: unknown, fallback: string): DraftState {
  return {
    ...state,
    pending: null,
    validation: null,
    message: error instanceof DefinitionError ? error.message : fallback,
    issues: error instanceof DefinitionError ? error.issues : [],
  };
}

export async function importSource(file: File): Promise<string> {
  if (file.size > MAX_SOURCE_BYTES) throw new DraftError('The JSON file exceeds the 1 MiB limit.');
  const bytes = await file.arrayBuffer();
  if (bytes.byteLength > MAX_SOURCE_BYTES)
    throw new DraftError('The JSON file exceeds the 1 MiB limit.');
  try {
    return new TextDecoder('utf-8', {fatal: true, ignoreBOM: true}).decode(bytes);
  } catch {
    throw new DraftError('Import a JSON file encoded as valid UTF-8.');
  }
}
