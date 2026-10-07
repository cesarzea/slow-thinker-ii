import type {GraphDocument} from '../../api/index.ts';

function trigger(document: GraphDocument) {
  return document.nodes.find((node) => node.component.startsWith('trigger@'));
}

/** Whether a manual run asks for the message: the Trigger's “On manual runs”, ask by default. */
export function asksForMessage(document: GraphDocument): boolean {
  return trigger(document)?.config['manual_runs'] !== 'send';
}

/** The Trigger's configured message, the default input of a run. */
export function triggerMessage(document: GraphDocument): string {
  const message = trigger(document)?.config['message'];
  return typeof message === 'string' ? message : '';
}
