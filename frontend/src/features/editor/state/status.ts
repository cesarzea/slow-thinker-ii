import type {Diagnostic} from '../../../api/index.ts';
import type {EditorState} from './editor-state.ts';
import type {Persistence} from './use-persistence.ts';

const clock = new Intl.DateTimeFormat('en-GB', {hour: '2-digit', minute: '2-digit'});

/** “Saving…”, “Saved” or the reason the last save failed. */
export function saveText(persistence: Persistence): string {
  if (persistence.status.kind === 'failed') return `Not saved: ${persistence.status.message}`;
  return persistence.unsaved || persistence.status.kind === 'saving' ? 'Saving…' : 'Saved';
}

/** How far the branch's working copy is from its own head, or from where it started. */
export function pendingText(persistence: Persistence): string | null {
  const {since, pending} = persistence.versions;
  if (since === null) return 'not activated yet';
  if (pending === 0) return null;
  const count = `${pending >= 100 ? '100+' : String(pending)} ${pending === 1 ? 'change' : 'changes'}`;
  const base = 'version' in since ? `v${String(since.version)}` : `change ${String(since.change)}`;
  return `${count} since ${base}`;
}

/** “v3 · Active”, naming the branch of the active version when it is not the open one. */
export function activeText(persistence: Persistence): string {
  const {active, activeBranch} = persistence.versions;
  if (active === null) return 'No active version';
  const elsewhere = activeBranch !== null && activeBranch !== persistence.target.branch;
  const branch = elsewhere ? ` · ${activeBranch}` : '';
  return `v${String(active)} · Active${branch}`;
}

/** “Saved 10:42 · change 27” for the status bar. */
export function storedText(persistence: Persistence): string {
  const {stored} = persistence;
  if (stored === null) return 'Not saved yet';
  return `Saved ${clock.format(new Date(stored.at))} · change ${String(stored.change)}`;
}

function errors(state: EditorState): Diagnostic[] {
  return state.diagnostics.filter((item) => item.severity === 'error');
}

/** Why the working copy cannot be activated now, or null when it can. */
export function activationBlock(state: EditorState, persistence: Persistence): string | null {
  if (persistence.status.kind === 'failed') return 'Save the working copy first.';
  if (state.checkFailure !== null) return `Could not check the graph: ${state.checkFailure}`;
  if (state.checked !== state.revision) return 'Checking the graph…';
  return errors(state).length > 0 ? 'Fix the problems in the graph before activating it.' : null;
}

/** Whether the header offers activation: the branch has no version yet, or moved past it. */
export function canOfferActivation(persistence: Persistence): boolean {
  const {head, pending} = persistence.versions;
  return persistence.stored !== null && (head === null || pending > 0 || persistence.unsaved);
}
