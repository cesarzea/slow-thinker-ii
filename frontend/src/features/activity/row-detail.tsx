import type {ReactElement} from 'react';
import type {EventOf, JsonValue, RunEvent} from '../../api/index.ts';
import {EvidenceContent, isJsonObject, moneyLabel} from '../../ui/index.ts';
import {replyContent} from './summaries.ts';

function Field(props: {readonly label: string; readonly value: unknown}): ReactElement {
  return (
    <div className="detail-field">
      <dt>{props.label}</dt>
      <dd>
        <EvidenceContent value={props.value} />
      </dd>
    </div>
  );
}

function textOf(value: JsonValue | undefined): string {
  return typeof value === 'string' ? value : JSON.stringify(value ?? null);
}

function messages(request: JsonValue): JsonValue {
  const list = isJsonObject(request) ? request['messages'] : undefined;
  if (!Array.isArray(list)) return [];
  return list.map((message) =>
    isJsonObject(message) ? `${textOf(message['role'])}: ${textOf(message['content'])}` : message,
  );
}

function parameters(request: JsonValue): JsonValue {
  if (!isJsonObject(request)) return {};
  return Object.fromEntries(
    Object.entries(request).filter(([name]) => name !== 'messages' && name !== 'model'),
  );
}

function LlmDetail({event}: {readonly event: EventOf<'llm.called'>}): ReactElement {
  const {data} = event;
  const rates = Object.entries(data.rates ?? {}).map(
    ([category, rate]) => `${category} ${rate} USD per million tokens`,
  );
  return (
    <dl>
      <Field label="Request messages" value={messages(data.request)} />
      <Field label="Parameters" value={parameters(data.request)} />
      <Field
        label={data.error === undefined ? 'Reply' : 'Error'}
        value={data.error ?? replyContent(data.response)}
      />
      <Field label="Usage" value={data.usage} />
      <Field label="Reserved" value={moneyLabel(data.reserved_usd)} />
      <Field
        label="Cost"
        value={`${moneyLabel(data.cost_usd)}${data.estimated ? ' (estimated)' : ''}`}
      />
      <Field label="Rates" value={rates} />
    </dl>
  );
}

function CallDetail({event}: {readonly event: EventOf<'component.called'>}): ReactElement {
  const {data} = event;
  return (
    <dl>
      <Field label="Operation" value={data.operation} />
      <Field label="Arguments" value={data.arguments} />
      <Field
        label={data.error === undefined ? 'Result' : 'Error'}
        value={data.error ?? data.result}
      />
    </dl>
  );
}

/** The recorded detail of one timeline row, shown as text and structure. */
export function RowDetail({event}: {readonly event: RunEvent}): ReactElement {
  if (event.kind === 'llm.called') return <LlmDetail event={event} />;
  if (event.kind === 'component.called') return <CallDetail event={event} />;
  return (
    <dl>
      {event.evidence === 'reported' && (
        <Field label="Evidence" value="Reported by the component" />
      )}
      <Field label="Recorded data" value={event.data} />
    </dl>
  );
}
