import {useId} from 'react';
import type {ReactElement} from 'react';
import type {JsonObject, JsonValue} from '../api/index.ts';
import {TextControl} from './form-controls.tsx';
import {BooleanInput, EnumInput} from './parameter-inputs.tsx';
import type {CommonProps, InputProps} from './parameter-inputs.tsx';
import {NumberControl} from './number-control.tsx';
import {
  numericBounds,
  orderedParameters,
  parameterClass,
  parameterHelp,
} from './parameter-fields.ts';
import {disabledProperties, withoutDisabled} from './parameter-rules.ts';

export interface ParameterFormProps {
  readonly schema: JsonObject;
  readonly value: JsonObject;
  readonly onChange: (value: JsonObject) => void;
  readonly disabled?: boolean;
}

/**
 * A form generated from a provider's parameter schema, honouring its if/else rules: ordinary
 * fields in two columns under the subheading “Parameters”.
 */
export function ParameterForm(props: ParameterFormProps): ReactElement {
  const unavailable = disabledProperties(props.schema, props.value);
  const change = (name: string, next: JsonValue | undefined): void => {
    const updated = {...props.value};
    if (next === undefined) Reflect.deleteProperty(updated, name);
    else updated[name] = next;
    props.onChange(withoutDisabled(props.schema, updated));
  };
  return (
    <div className="parameter-form">
      <h4 className="form-subhead">Parameters</h4>
      {orderedParameters(props.schema).map(([name, schema]) => (
        <ParameterField
          key={name}
          name={name}
          schema={schema}
          value={props.value[name]}
          unavailable={unavailable.has(name)}
          disabled={props.disabled === true}
          onChange={(next) => {
            change(name, next);
          }}
        />
      ))}
    </div>
  );
}

function ParameterField(
  props: Omit<InputProps, 'describedBy'> & {readonly unavailable: boolean},
): ReactElement {
  const note = useId();
  return (
    <div className={`config-field parameter label-top ${parameterClass(props.schema)}`}>
      <ParameterInput
        {...props}
        disabled={props.disabled || props.unavailable}
        describedBy={props.unavailable ? note : undefined}
      />
      {props.unavailable && (
        <p id={note} className="field-note">
          Not available with the current settings.
        </p>
      )}
    </div>
  );
}

function commonProps(props: InputProps, label: string): CommonProps {
  const help = parameterHelp(props.schema);
  return {
    label,
    disabled: props.disabled,
    ...described(props.describedBy),
    ...(help === undefined ? {} : {help}),
  };
}

function ParameterInput(props: InputProps): ReactElement {
  const label = typeof props.schema['title'] === 'string' ? props.schema['title'] : props.name;
  const common = commonProps(props, label);
  const values = props.schema['enum'];
  if (Array.isArray(values)) return <EnumInput {...props} common={common} values={values} />;
  const type = props.schema['type'];
  if (type === 'boolean') return <BooleanInput {...props} label={label} />;
  if (type === 'integer' || type === 'number') {
    const bounds = numericBounds(props.schema, type === 'integer');
    const value = typeof props.value === 'number' ? props.value : undefined;
    return <NumberControl {...common} {...bounds} value={value} onValue={props.onChange} />;
  }
  const text = typeof props.value === 'string' ? props.value : '';
  return <TextControl {...common} value={text} onValue={props.onChange} />;
}

function described(id: string | undefined): {describedBy?: string} {
  return id === undefined ? {} : {describedBy: id};
}
