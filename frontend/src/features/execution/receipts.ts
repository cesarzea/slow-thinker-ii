import type {Receipt} from '../../api/index.ts';
import {pendingKey} from './state.ts';
import type {IdentityStorage, ExecutionStore} from './state.ts';

export function acceptReceipt(
  store: ExecutionStore,
  storage: IdentityStorage,
  receipt: Receipt,
): void {
  if (store.closed || store.snapshot().pending !== receipt.command_id) return;
  storage.removeItem(pendingKey);
  store.invalidate();
  store.update({pending: null, busy: false, stale: true, message: receiptMessage(receipt)});
  if (receipt.disposition !== 'accepted' || receipt.target_id === null) return;
  if (receipt.kind === 'session') store.selectSession(receipt.target_id);
  if (receipt.kind === 'start') store.selectRun(receipt.target_id);
  if (receipt.kind === 'stop') store.update({stopRequested: true});
}

function receiptMessage(receipt: Receipt): string {
  if (receipt.disposition === 'rejected')
    return `Request rejected: ${receipt.reason ?? 'no reason available'}.`;
  if (receipt.disposition === 'withdrawn') return 'Start withdrawn. Checking the final state.';
  if (receipt.disposition === 'already_terminal') return 'The run had already ended.';
  const messages = {
    session: 'Session created.',
    start: 'Run admitted.',
    stop: 'Stop requested.',
  };
  return messages[receipt.kind];
}

export function failureMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'Could not confirm the request.';
}
