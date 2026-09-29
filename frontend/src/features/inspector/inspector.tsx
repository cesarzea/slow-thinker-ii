import type {ReactElement} from 'react';
import {useSelection} from './selection.ts';
import {EventView} from './event-view.tsx';
import {SelectedEvidence} from './selected-evidence.tsx';
import {FocusHeading} from './focus-heading.tsx';
import type {InspectionSource, InspectionSelection} from './types.ts';

export function Inspector(
  props: InspectionSource & {readonly selection?: InspectionSelection},
): ReactElement {
  const selection = useSelection(props.selection);
  const {onCall, onPayload} = selection;
  return (
    <section className="inspector" aria-label="Inspector de ejecución">
      <FocusHeading level="h2" request={0}>
        Inspector de ejecución
      </FocusHeading>
      <p>
        Ejecución: <code>{props.run}</code>
      </p>
      <EventView {...props} onCall={onCall} onPayload={onPayload} />
      <SelectedEvidence {...props} selection={selection} />
    </section>
  );
}
