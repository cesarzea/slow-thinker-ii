import type {ReactElement} from 'react';
import type {useSelection} from './selection.ts';
import type {InspectionSource} from './types.ts';
import {ActivationView} from './activation-view.tsx';
import {CallView} from './call-view.tsx';
import {PayloadView} from './payload-view.tsx';

type Props = InspectionSource & {
  readonly selection: ReturnType<typeof useSelection>;
};

export function SelectedEvidence({selection, ...source}: Props): ReactElement {
  const {payload, focused, revision} = selection;
  return (
    <>
      <SelectedActivation {...source} selection={selection} />
      <SelectedCall {...source} selection={selection} />
      {payload !== undefined && (
        <PayloadView
          key={payload}
          {...source}
          id={payload}
          focusRequest={focused === 'payload' ? revision : undefined}
        />
      )}
    </>
  );
}

function SelectedActivation({selection, ...source}: Props): ReactElement | null {
  const {activation, focused, revision, onCall, onPayload} = selection;
  if (activation === undefined) return null;
  return (
    <ActivationView
      key={activation}
      {...source}
      id={activation}
      focusRequest={focused === 'activation' ? revision : undefined}
      onCall={onCall}
      onPayload={onPayload}
    />
  );
}

function SelectedCall({selection, ...source}: Props): ReactElement | null {
  const {call, focused, revision, onCall, onPayload, onActivation} = selection;
  if (call === undefined) return null;
  return (
    <CallView
      key={call}
      {...source}
      id={call}
      focusRequest={focused === 'call' ? revision : undefined}
      onCall={onCall}
      onPayload={onPayload}
      onActivation={onActivation}
    />
  );
}
