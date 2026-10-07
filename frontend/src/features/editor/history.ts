import type {ReactNode} from 'react';
import type {GraphDocument} from '../../api/index.ts';

/** What the history panel hosted by the editor knows and can ask of it. */
export interface HistoryContext {
  readonly graphId: string;
  /** The branch the editor shows. */
  readonly branch: string;
  /** The latest saved change of that branch; the panel reads again when it changes. */
  readonly latestChange: number | null;
  /** The graph's active version. */
  readonly activeVersion: number | null;
  /** The editor replaces its working copy and autosaves it as a new change. */
  readonly onRestore: (document: GraphDocument) => void;
  /** The editor opens that branch's latest change. */
  readonly onBranchChange: (name: string) => void;
  /** After the panel activates, the editor refreshes its version badge and activation. */
  readonly onActivated: (version: number) => void;
  /** Closes the panel; the panel draws its own header with ×. */
  readonly onClose: () => void;
}

export type RenderHistory = (context: HistoryContext) => ReactNode;
