import {useState} from 'react';
import type {
  BranchOrigin,
  ChangeSummary,
  GraphDocument,
  OperatorClient,
  VersionSummary,
} from '../../api/index.ts';
import {actionProblem, activateVersion} from './actions.ts';

/** What the editor tells the panel and lets it do: the History context. */
export interface HistoryContext {
  readonly graphId: string;
  readonly branch: string;
  readonly latestChange: number | null;
  readonly activeVersion: number | null;
  readonly onRestore: (document: GraphDocument) => void;
  readonly onBranchChange: (name: string) => void;
  readonly onActivated: (version: number) => void;
  readonly onClose: () => void;
}

export interface PanelActions {
  readonly busy: boolean;
  readonly problem: string | null;
  readonly activateChange: (change: number) => void;
  readonly activateVersion: (version: VersionSummary) => void;
  readonly restore: (change: ChangeSummary) => void;
  /** Creates the branch and opens it; answers the problem, or `null` when it worked. */
  readonly createBranch: (name: string, origin: BranchOrigin) => Promise<string | null>;
}

interface Inputs {
  readonly client: OperatorClient;
  readonly context: HistoryContext;
  readonly documents: ReadonlyMap<number, GraphDocument>;
  readonly refresh: () => void;
}

type Run = (label: string, action: () => Promise<void>) => void;

function activations(
  inputs: Inputs,
  run: Run,
): Pick<PanelActions, 'activateChange' | 'activateVersion'> {
  const {client, context} = inputs;
  return {
    activateChange: (change) => {
      run('Activation', async () => {
        context.onActivated((await client.activate(context.graphId, change)).version);
      });
    },
    activateVersion: (version) => {
      run('Activation', async () => {
        const done = await activateVersion(client, context.graphId, version);
        if (done.branch === context.branch) context.onRestore(done.document);
        context.onActivated(done.version);
      });
    },
  };
}

function restoring(inputs: Inputs, run: Run): PanelActions['restore'] {
  const {client, context, documents} = inputs;
  return (change) => {
    run('Restoring', async () => {
      const known = documents.get(change.change);
      context.onRestore(known ?? (await client.change(context.graphId, change.change)).document);
    });
  };
}

function branching(inputs: Inputs): PanelActions['createBranch'] {
  const {client, context} = inputs;
  return async (name, origin) => {
    try {
      await client.createBranch(context.graphId, name, origin);
      context.onBranchChange(name);
      return null;
    } catch (error) {
      return actionProblem('Creating the branch', error);
    }
  };
}

/** The panel's actions, one at a time, each reporting its failure and refreshing after. */
export function usePanelActions(inputs: Inputs): PanelActions {
  const [busy, setBusy] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const run: Run = (label, action) => {
    setBusy(true);
    setProblem(null);
    action()
      .catch((error: unknown) => {
        setProblem(actionProblem(label, error));
      })
      .finally(() => {
        setBusy(false);
        inputs.refresh();
      });
  };
  return {
    busy,
    problem,
    ...activations(inputs, run),
    restore: restoring(inputs, run),
    createBranch: branching(inputs),
  };
}
