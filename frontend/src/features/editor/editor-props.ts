import type {GraphDocument, OperatorClient} from '../../api/index.ts';
import type {RenderHistory} from './history.ts';
import type {RenderRun} from './run-slot.ts';
import type {DraftModel} from './state/use-editor.ts';

export interface EditorProps {
  readonly client: OperatorClient;
  readonly graphId: string;
  /** A document created on the graphs page and not stored yet; the editor stores it. */
  readonly created: GraphDocument | null;
  /** Receives the draft model after every render; edits are saved as they are made. */
  readonly onDraft?: (model: DraftModel | null) => void;
  /** The graph's runs page; when given, the header links to it as “Runs”. */
  readonly runsHref?: string;
  /** The graphs page; when given, the breadcrumb links to it. */
  readonly graphsHref?: string;
  /** The history panel; when given, the header offers History. */
  readonly renderHistory?: RenderHistory;
  /** A run to show in run mode, from the address; null or absent for editing. */
  readonly runId?: string | null;
  /** Run mode puts the run it shows in the address, or null when it shows none. */
  readonly onRunChange?: (runId: string | null) => void;
  /** The run panel of run mode; without it, Run shows no panel. */
  readonly renderRun?: RenderRun;
}
