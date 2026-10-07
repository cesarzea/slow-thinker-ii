import type {ReactNode} from 'react';
import type {Limits, PointId, RunSource} from '../../api/index.ts';

/** How many activations each node had and how many messages each connection carried. */
export interface RunCounts {
  readonly activations: Readonly<Record<string, number>>;
  readonly messages: Readonly<Record<string, number>>;
}

/** What the run panel hosted by the editor in run mode knows and can ask of it. */
export interface RunPanelContext {
  readonly graphId: string;
  readonly graphName: string;
  /** The run executed in this run mode, or null before Execute. */
  readonly runId: string | null;
  /** The Trigger's message, the default input, and the limits of the working copy. */
  readonly message: string;
  /** Whether Execute first lets the operator change the message (the Trigger's choice). */
  readonly ask: boolean;
  readonly limits: Limits;
  /** Why Execute is unavailable, or null. */
  readonly blocked: string | null;
  /** Saves pending edits and names what Execute runs: the branch's latest change. */
  readonly prepare: () => Promise<RunSource | null>;
  readonly onStarted: (runId: string) => void;
  /** Ready to execute again. */
  readonly onReset: () => void;
  /** The points whose events the panel shows: every observed point, or the focused one. */
  readonly points: readonly PointId[];
  readonly focus: PointId | null;
  readonly onClearFocus: () => void;
  /** Readable names of the points. */
  readonly labels: Readonly<Partial<Record<PointId, string>>>;
  /** The panel reports the run's counts as they change; the canvas shows them. */
  readonly onCounts: (counts: RunCounts) => void;
  /** Back to editing. */
  readonly onClose: () => void;
}

export type RenderRun = (context: RunPanelContext) => ReactNode;
