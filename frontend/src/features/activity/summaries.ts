import type {EventOf, JsonObject, JsonValue, RunEvent, RunEventKind} from '../../api/index.ts';
import {
  durationLabel,
  jsonPreview,
  moneyLabel,
  readPointer,
  runStatusText,
} from '../../ui/index.ts';
import type {Names} from './names.ts';

export type RowGroup = 'message' | 'call' | 'other';
export interface RowText {
  readonly label: string;
  readonly summary: string;
  readonly metrics?: string;
  readonly group?: RowGroup;
}
interface Context {
  readonly names: Names;
  readonly events: readonly RunEvent[];
}
type Summarizer<K extends RunEventKind> = (event: EventOf<K>, context: Context) => RowText;

/** The text of a model reply: its message content, or the whole response. */
export function replyContent(response: JsonObject | undefined): JsonValue | undefined {
  const content = readPointer(response, '/choices/0/message/content');
  return typeof content === 'string' ? content : response;
}

function emitted(event: EventOf<'activation.completed'>): string {
  const ports = event.data.emitted.map((item) => item.port);
  return ports.length === 0 ? 'Completed' : `Completed, emitted on ${ports.join(', ')}`;
}

function errorText(error: {readonly message: string} | null | undefined): string | null {
  if (error === undefined) return null;
  return `Error: ${error?.message ?? 'no detail recorded'}`;
}

function llmRow(event: EventOf<'llm.called'>, {names}: Context): RowText {
  const {usage, error} = event.data;
  const tokens =
    usage === null ? 'tokens unknown' : `${String(usage.input)}/${String(usage.output)}`;
  const reply = errorText(error) ?? jsonPreview(replyContent(event.data.response));
  const metrics = `${tokens} · ${moneyLabel(event.data.cost_usd)} · ${durationLabel(event.data.duration_ms)}`;
  const model = names.llm(event.data.llm ?? 'Unknown model');
  return {label: 'LLM call', group: 'call', summary: `${model} · ${reply}`, metrics};
}

function componentRow(event: EventOf<'component.called'>, {names}: Context): RowText {
  const {data} = event;
  const metrics = durationLabel(data.duration_ms);
  const failed = data.error === undefined ? null : `Failed: ${data.error.message}`;
  if (data.position === 'output') {
    const port = readPointer(data.result, '/port');
    const routed = `${jsonPreview(port)} · ${jsonPreview(readPointer(data.result, '/payload'))}`;
    return {
      label: names.component(data.component).toLowerCase(),
      group: 'call',
      summary: failed ?? routed,
      metrics,
    };
  }
  const summary = failed ?? `${names.component(data.component)} ${data.operation} returned`;
  return {label: 'call', group: 'call', summary, metrics};
}

/** The run's end: its status line, followed by its detail when there is one. */
function endSummary(event: EventOf<'run.finished'>): string {
  const {status, reason, detail} = event.data;
  if (status === 'completed') return 'Completed: no message pending and no node running';
  const line = runStatusText(status, reason);
  return detail === '' ? line : `${line}. ${detail}`;
}

const summaries: {readonly [K in RunEventKind]: Summarizer<K>} = {
  'run.started': (event) => ({
    label: 'start',
    summary: `Started with ${jsonPreview(event.data.input)}`,
  }),
  'host.ready': (event, {names}) => ({
    label: 'start',
    summary: `${names.component(event.data.component)} is ready`,
    metrics: durationLabel(event.data.startup_ms),
  }),
  'host.failed': (event, {names}) => ({
    label: 'start',
    summary: `${names.component(event.data.component)} could not start: ${event.data.error.message}`,
  }),
  'run.running': () => ({label: 'start', summary: 'Running; the time limit starts now'}),
  'message.sent': (event, {names}) => ({
    label: 'message',
    group: 'message',
    summary: `${event.data.from.port} → ${names.node(event.data.to.node_id)} · ${event.data.to.port}: ${jsonPreview(event.data.payload)}`,
  }),
  'message.discarded': (event) => ({
    label: 'message',
    group: 'message',
    summary: `Discarded: output ${event.data.from.port} has no connection`,
  }),
  'message.dropped': (event, {names}) => ({
    label: 'message',
    group: 'message',
    summary: `Dropped before reaching ${names.node(event.data.to.node_id)}: the run was ending`,
  }),
  'activation.started': (event) => ({
    label: 'activation',
    summary: `Activation ${String(event.data.number)} started`,
  }),
  'activation.completed': (event) => ({
    label: 'activation',
    summary: emitted(event),
    metrics: durationLabel(event.data.duration_ms),
  }),
  'activation.failed': (event) => ({
    label: 'activation',
    summary: `Failed: ${event.data.error.message}`,
    metrics: durationLabel(event.data.duration_ms),
  }),
  'activation.cancelled': (event) => ({
    label: 'activation',
    summary: `Cancelled: ${event.data.reason}`,
  }),
  'component.called': componentRow,
  'llm.called': llmRow,
  report: (event, {names, events}) => ({
    label: 'report',
    summary: `Reported by ${names.reporter(event, events)}: ${jsonPreview(event.data.content)}`,
  }),
  'run.result': (event) => ({
    label: 'result',
    summary: `${event.data.name}: ${jsonPreview(event.data.payload)}`,
  }),
  'run.finished': (event) => ({
    label: 'end',
    summary: endSummary(event),
    metrics: durationLabel(event.data.totals.duration_ms),
  }),
};

export function rowText(event: RunEvent, context: Context): RowText {
  const summarize = summaries[event.kind] as Summarizer<RunEventKind>;
  return summarize(event, context);
}
