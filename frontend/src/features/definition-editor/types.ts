import type {Dispatch, SetStateAction} from 'react';
import type {DefinitionIssue, GraphReference, ValidationResult} from '../../api/index.ts';

export interface DefinitionEditorProps {
  readonly credential: string;
  readonly reference: GraphReference;
  readonly onSaved: (reference: GraphReference) => void;
  readonly onDirtyChange: (dirty: boolean) => void;
}

export interface DraftState {
  readonly source: string;
  readonly baseline: string;
  readonly selectedSource: string;
  readonly loaded: boolean;
  readonly pending: 'load' | 'validate' | 'save' | 'import' | 'draft' | null;
  readonly validation: ValidationResult | null;
  readonly message: string | null;
  readonly issues: readonly DefinitionIssue[];
  readonly frozenSource: string | null;
  readonly uncertain: boolean;
}

export type UpdateDraft = Dispatch<SetStateAction<DraftState>>;

export interface Requests {
  readonly begin: () => AbortController;
  readonly cancel: () => void;
}

export interface EditorModel {
  readonly state: DraftState;
  readonly dirty: boolean;
  readonly edit: (source: string) => void;
  readonly importFile: (file: File) => Promise<void>;
  readonly discard: () => void;
  readonly derive: (graphId: string, revision: string) => Promise<void>;
  readonly validate: () => Promise<void>;
  readonly save: () => Promise<void>;
  readonly retry: () => Promise<void>;
  readonly reload: () => void;
}
