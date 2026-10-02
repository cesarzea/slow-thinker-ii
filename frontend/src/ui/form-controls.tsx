import type {ReactElement} from 'react';
export interface TextControlProps {
  readonly label: string;
  readonly value: string;
  readonly onValue: (value: string) => void;
  readonly disabled?: boolean;
}
export interface Choice {
  readonly value: string;
  readonly label: string;
  readonly disabled?: boolean;
}
export function TextControl({
  label,
  value,
  onValue,
  disabled = false,
}: TextControlProps): ReactElement {
  return (
    <label>
      {label}
      <input
        value={value}
        disabled={disabled}
        onChange={(event) => {
          onValue(event.target.value);
        }}
      />
    </label>
  );
}
export function ChoiceControl(
  props: TextControlProps & {readonly choices: readonly Choice[]},
): ReactElement {
  return (
    <label>
      {props.label}
      <select
        value={props.value}
        disabled={props.disabled === true}
        onChange={(event) => {
          props.onValue(event.target.value);
        }}
      >
        {props.choices.map((choice) => (
          <option key={choice.value} value={choice.value} disabled={choice.disabled === true}>
            {choice.label}
          </option>
        ))}
      </select>
    </label>
  );
}
