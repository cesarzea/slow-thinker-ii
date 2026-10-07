import type {ReactElement} from 'react';
import type {JsonObject, JsonValue} from '../api/index.ts';
import {ChoiceControl} from './form-controls.tsx';
import {scalarText} from './parameter-fields.ts';

export interface InputProps {
  readonly name: string;
  readonly schema: JsonObject;
  readonly value: JsonValue | undefined;
  readonly disabled: boolean;
  readonly describedBy: string | undefined;
  readonly onChange: (value: JsonValue | undefined) => void;
}
export interface CommonProps {
  readonly label: string;
  readonly disabled: boolean;
  readonly describedBy?: string;
  readonly help?: string;
}

export function EnumInput(
  props: InputProps & {
    readonly common: CommonProps;
    readonly values: JsonValue[];
  },
): ReactElement {
  const index = props.values.findIndex((value) => value === props.value);
  const choices = props.values.map((value, position) => ({
    value: String(position),
    label: scalarText(value),
  }));
  const fallback = props.schema['default'];
  const unset = fallback === undefined ? 'Not set' : `Default (${scalarText(fallback)})`;
  const options = [{value: '', label: unset}, ...choices];
  return (
    <ChoiceControl
      {...props.common}
      value={index < 0 ? '' : String(index)}
      choices={options}
      onValue={(value) => {
        props.onChange(value === '' ? undefined : props.values[Number(value)]);
      }}
    />
  );
}

export function BooleanInput(props: InputProps & {readonly label: string}): ReactElement {
  return (
    <label className="checkbox">
      <input
        type="checkbox"
        checked={props.value === true}
        disabled={props.disabled}
        aria-describedby={props.describedBy}
        onChange={(event) => {
          props.onChange(event.target.checked);
        }}
      />
      {props.label}
    </label>
  );
}
