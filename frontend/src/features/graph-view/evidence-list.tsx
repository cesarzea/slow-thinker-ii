import type {ReactElement} from 'react';
import type {ActivationView, CommunicationView} from '../../api/index.ts';
import type {GraphViewProps} from './types.ts';

type Props = Pick<GraphViewProps, 'onSelect'> & {
  readonly execution: GraphViewProps['execution'];
};
export function EvidenceList({execution, onSelect}: Props): ReactElement {
  if (execution === undefined) return <p>Recorded evidence unavailable.</p>;
  return (
    <>
      <h3>Recorded activations</h3>
      {execution.activations.length === 0 && <p>No recorded activations.</p>}
      <ol aria-label="Recorded activations">
        {execution.activations.map((item) => (
          <ActivationItem key={item.id} item={item} onSelect={onSelect} />
        ))}
      </ol>
      <h3>Observed communications</h3>
      {execution.calls.length === 0 && <p>No observed communications.</p>}
      <ul aria-label="Observed communications">
        {execution.calls.map((item) => (
          <CallItem key={item.id} item={item} onSelect={onSelect} />
        ))}
      </ul>
    </>
  );
}
function ActivationItem({
  item,
  onSelect,
}: Pick<Props, 'onSelect'> & {readonly item: ActivationView}): ReactElement {
  return (
    <li>
      <button
        onClick={() => {
          onSelect?.({kind: 'activation', id: item.id});
        }}
      >
        Activation #{item.ordinal}: {item.node}
      </button>
      {' · '}
      {item.id} · {item.component} · {item.state} · Port:{' '}
      {item.selected_port ?? 'No recorded selection'}
    </li>
  );
}
function CallItem({
  item,
  onSelect,
}: Pick<Props, 'onSelect'> & {readonly item: CommunicationView}): ReactElement {
  return (
    <li>
      <button
        onClick={() => {
          onSelect?.({kind: 'call', id: item.id});
        }}
      >
        Call {item.id}
      </button>
      {' · '}
      {item.caller || 'Orchestrator'} → {item.target}.{item.operation} · {item.state} · Activation:{' '}
      {item.activation_id ?? 'Not applicable'} · Parent: {item.parent_call_id ?? 'Root'}
    </li>
  );
}
