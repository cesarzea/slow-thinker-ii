import type {History, Run, Workspace} from '../../api/index.ts';
import {emptyProjection} from './projection.ts';
import type {ExecutionProjection} from './projection.ts';

export const pendingKey = 'slow-thinker-ii.pending-command';
export interface ExecutionState extends ExecutionProjection {
  readonly storageReady: boolean;
  readonly workspace: Workspace | null;
  readonly run: Run | null;
  readonly sessionId: string;
  readonly runId: string;
  readonly history: History | null;
  readonly historyCursor: string | undefined;
  readonly workspaceCursor: string | undefined;
  readonly pending: string | null;
  readonly busy: boolean;
  readonly stale: boolean;
  readonly message: string | null;
  readonly stopRequested: boolean;
}
export type IdentityStorage = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>;

export class ExecutionStore {
  private state: ExecutionState;
  private readonly listeners = new Set<() => void>();
  private generation = 0;
  private disposed = false;

  get epoch(): number {
    return this.generation;
  }
  get closed(): boolean {
    return this.disposed;
  }
  invalidate(): void {
    this.generation += 1;
  }

  constructor(storage: IdentityStorage) {
    this.state = {
      ...emptyProjection,
      workspace: null,
      run: null,
      sessionId: '',
      runId: '',
      history: null,
      historyCursor: undefined,
      workspaceCursor: undefined,
      ...readPending(storage),
      busy: false,
      stale: true,
      stopRequested: false,
    };
  }

  readonly snapshot = (): ExecutionState => this.state;
  readonly subscribe = (listener: () => void): (() => void) => {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  };

  setClosed(closed: boolean): void {
    this.disposed = closed;
  }

  update(patch: Partial<ExecutionState>): void {
    if (this.closed) return;
    this.state = {...this.state, ...patch};
    for (const listener of this.listeners) listener();
  }

  selectSession(id: string): void {
    this.invalidate();
    this.update({
      ...emptyProjection,
      sessionId: id,
      history: null,
      historyCursor: undefined,
      runId: '',
      run: null,
      stale: true,
    });
  }

  page(kind: 'workspace' | 'history', cursor: string | undefined): void {
    this.invalidate();
    this.update(
      kind === 'workspace'
        ? {workspaceCursor: cursor, stale: true}
        : {historyCursor: cursor, stale: true},
    );
  }

  selectRun(id: string): void {
    this.invalidate();
    this.update({...emptyProjection, runId: id, run: null, stopRequested: false, stale: true});
  }
}

export function canStart(state: ExecutionState): boolean {
  return (
    state.storageReady &&
    !state.stale &&
    !state.busy &&
    state.pending === null &&
    state.sessionId !== '' &&
    state.workspace?.admission_available === true
  );
}

export function canStop(state: ExecutionState): boolean {
  return (
    state.runId !== '' &&
    !state.busy &&
    state.pending === null &&
    !state.stopRequested &&
    (state.run === null || ['created', 'running', 'stopping'].includes(state.run.state))
  );
}

function readPending(
  storage: IdentityStorage,
): Pick<ExecutionState, 'pending' | 'storageReady' | 'message'> {
  try {
    return {pending: storage.getItem(pendingKey), storageReady: true, message: null};
  } catch {
    return {
      pending: null,
      storageReady: false,
      message: 'Could not read local tracking. Execution is disabled.',
    };
  }
}
