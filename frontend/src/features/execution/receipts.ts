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
    return `Solicitud rechazada: ${receipt.reason ?? 'sin motivo disponible'}.`;
  if (receipt.disposition === 'withdrawn')
    return 'Inicio retirado. Se está comprobando el estado final.';
  if (receipt.disposition === 'already_terminal') return 'La ejecución ya había terminado.';
  const messages = {
    session: 'Sesión creada.',
    start: 'Ejecución admitida.',
    stop: 'Parada solicitada.',
  };
  return messages[receipt.kind];
}

export function failureMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'No se pudo confirmar la solicitud.';
}
