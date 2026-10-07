import {useId} from 'react';
import type {ReactElement} from 'react';
import {descriptionIds, FieldHelp} from './field-help.tsx';

export interface Choice {
  readonly value: string;
  readonly label: string;
}
export interface ControlProps {
  readonly label: string;
  readonly disabled?: boolean;
  readonly describedBy?: string;
  /** Shown under the label and read as the control's description. */
  readonly help?: string;
}
export interface TextControlProps extends ControlProps {
  readonly value: string;
  readonly onValue: (value: string) => void;
  readonly placeholder?: string;
}

/** The label of a control with its help text underneath. */
export function ControlLabel(props: ControlProps & {readonly id: string}): ReactElement {
  return (
    <>
      <label htmlFor={props.id}>{props.label}</label>
      <FieldHelp id={`${props.id}-help`} text={props.help} />
    </>
  );
}

export const described = (id: string, props: ControlProps): string | undefined =>
  descriptionIds(`${id}-help`, props.help, props.describedBy);

/** A single-line text box named by its label. */
export function TextControl(props: TextControlProps): ReactElement {
  const id = useId();
  return (
    <div className="control">
      <ControlLabel {...props} id={id} />
      <input
        id={id}
        type="text"
        value={props.value}
        disabled={props.disabled === true}
        placeholder={props.placeholder}
        aria-describedby={described(id, props)}
        onChange={(event) => {
          props.onValue(event.target.value);
        }}
      />
    </div>
  );
}

/** A native select named by its label. */
export function ChoiceControl(
  props: TextControlProps & {readonly choices: readonly Choice[]},
): ReactElement {
  const id = useId();
  return (
    <div className="control">
      <ControlLabel {...props} id={id} />
      <select
        id={id}
        value={props.value}
        disabled={props.disabled === true}
        aria-describedby={described(id, props)}
        onChange={(event) => {
          props.onValue(event.target.value);
        }}
      >
        {props.choices.map((choice) => (
          <option key={choice.value} value={choice.value}>
            {choice.label}
          </option>
        ))}
      </select>
    </div>
  );
}
