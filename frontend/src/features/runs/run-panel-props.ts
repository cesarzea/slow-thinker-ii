import type {ReactNode} from 'react';
import type {Limits, OperatorClient, RunSource} from '../../api/index.ts';

interface Counts {
  readonly activations: Readonly<Record<string, number>>;
  readonly messages: Readonly<Record<string, number>>;
}

export interface RunPanelProps {
  readonly client: OperatorClient;
  readonly graphId: string;
  readonly graphName: string;
  readonly runId: string | null;
  readonly message: string;
  readonly ask: boolean;
  readonly limits: Limits;
  readonly blocked: string | null;
  readonly prepare: () => Promise<RunSource | null>;
  readonly onStarted: (runId: string) => void;
  readonly onReset: () => void;
  readonly onCounts: (counts: Counts) => void;
  readonly onClose: () => void;
  /** The observed points' events: shown live while the run executes and afterwards. */
  readonly feed: (runId: string) => ReactNode;
}
