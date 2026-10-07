import type {ReactElement} from 'react';

/** A field's help text, shown under its label. */
export function FieldHelp(props: {
  readonly id: string;
  readonly text: string | undefined;
}): ReactElement | null {
  if (props.text === undefined) return null;
  return (
    <p id={props.id} className="field-help">
      {props.text}
    </p>
  );
}

/** The ids that describe a control: its help text first, then any other description. */
export function descriptionIds(
  helpId: string,
  help: string | undefined,
  other: string | undefined,
): string | undefined {
  const ids = [help === undefined ? undefined : helpId, other].filter(
    (id): id is string => id !== undefined,
  );
  return ids.length === 0 ? undefined : ids.join(' ');
}
