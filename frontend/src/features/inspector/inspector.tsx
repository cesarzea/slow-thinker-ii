import type {ReactElement} from 'react';
import {useSelection} from './selection.ts';
import {ActivationView} from './activation-view.tsx';
import {EventView} from './event-view.tsx';
import {CallView} from './call-view.tsx';
import {PayloadView} from './payload-view.tsx';
import type {InspectionSource} from './types.ts';

export function Inspector(props: InspectionSource): ReactElement {
  const selection = useSelection();
  const {onCall, onPayload} = selection;
  return (
    <section className="inspector" aria-label="Inspector de ejecución">
      <h2>Inspector de ejecución</h2>
      <p>
        Ejecución: <code>{props.run}</code>
      </p>
      <EventView {...props} onCall={onCall} onPayload={onPayload} />
      <SelectedEvidence {...props} selection={selection} />
    </section>
  );
}

type SelectionProps = InspectionSource & {
  readonly selection: ReturnType<typeof useSelection>;
};

function SelectedEvidence({selection, ...props}: SelectionProps): ReactElement {
  const {call, payload, activation, onCall, onPayload, onActivation} = selection;
  return (
    <>
      {activation !== undefined && (
        <ActivationView
          key={activation}
          {...props}
          id={activation}
          onCall={onCall}
          onPayload={onPayload}
        />
      )}
      {call !== undefined && (
        <CallView
          key={call}
          {...props}
          id={call}
          onCall={onCall}
          onPayload={onPayload}
          onActivation={onActivation}
        />
      )}
      {payload !== undefined && <PayloadView key={payload} {...props} id={payload} />}
    </>
  );
}
