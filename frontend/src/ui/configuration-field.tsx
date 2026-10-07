import type {ReactElement} from 'react';
import type {JsonObject, JsonValue, LlmEntry, UiField} from '../api/index.ts';
import {CodeControl} from './code-control.tsx';
import {ExpandableTextArea} from './expandable-text-area.tsx';
import {ChoiceControl, TextControl} from './form-controls.tsx';
import {NumberControl} from './number-control.tsx';
import {ListControl} from './list-control.tsx';
import {fieldClass} from './presentation.ts';
import {SchemaEditor} from './schema-editor.tsx';
import {ServiceControl} from './service-control.tsx';

export interface ConfigurationFieldProps {
  readonly field: UiField;
  readonly schema: JsonObject | undefined;
  readonly value: JsonValue | undefined;
  readonly onChange: (value: JsonValue | undefined) => void;
  readonly services: readonly LlmEntry[];
  readonly disabled?: boolean;
}
interface ControlProps extends ConfigurationFieldProps {
  readonly common: {label: string; disabled: boolean; help?: string};
}
type Renderer = (props: ControlProps) => ReactElement;

const text = (value: JsonValue | undefined): string => (typeof value === 'string' ? value : '');
const placeholder = (field: UiField): {placeholder?: string} =>
  field.placeholder === undefined ? {} : {placeholder: field.placeholder};

const renderers: Readonly<Record<UiField['control'], Renderer>> = {
  text: (props) => (
    <TextControl
      {...props.common}
      {...placeholder(props.field)}
      value={text(props.value)}
      onValue={props.onChange}
    />
  ),
  multiline: (props) => (
    <ExpandableTextArea
      {...props.common}
      {...placeholder(props.field)}
      value={text(props.value)}
      onChange={props.onChange}
    />
  ),
  code: (props) => (
    <CodeControl
      {...props.common}
      {...placeholder(props.field)}
      {...(props.field.language === undefined ? {} : {language: props.field.language})}
      value={text(props.value)}
      onChange={props.onChange}
    />
  ),
  number: (props) => (
    <NumberControl
      {...props.common}
      integer={props.schema?.['type'] === 'integer'}
      {...bounds(props.schema)}
      {...numberFormat(props.field)}
      value={typeof props.value === 'number' ? props.value : undefined}
      onValue={props.onChange}
    />
  ),
  choice: (props) => <ChoiceField {...props} />,
  list: (props) => (
    <ListControl
      {...props.common}
      itemLabel={props.field.item_label ?? 'Item'}
      value={Array.isArray(props.value) ? props.value.map(String) : []}
      onChange={props.onChange}
    />
  ),
  schema: (props) => (
    <SchemaEditor
      {...props.common}
      {...(props.field.empty_label === undefined ? {} : {emptyLabel: props.field.empty_label})}
      value={props.value}
      onChange={props.onChange}
    />
  ),
  service: (props) => (
    <ServiceControl
      {...props.common}
      value={props.value}
      onChange={props.onChange}
      services={props.services}
    />
  ),
};

/**
 * One declared configuration field, rendered by its control with its help text under the
 * label; values are plain JSON. The wrapper's classes carry the declared presentation: width,
 * alignment and label position, with the declaration's defaults.
 */
export function ConfigurationField(props: ConfigurationFieldProps): ReactElement {
  const help = props.field.help === undefined ? {} : {help: props.field.help};
  const common = {label: props.field.label, disabled: props.disabled === true, ...help};
  return (
    <div className={fieldClass(props.field)}>
      {renderers[props.field.control]({...props, common})}
    </div>
  );
}

function numberFormat(field: UiField): {decimals?: number; prefix?: string; suffix?: string} {
  const {decimals, prefix, suffix} = field.format ?? {};
  return {
    ...(decimals === undefined ? {} : {decimals}),
    ...(prefix === undefined ? {} : {prefix}),
    ...(suffix === undefined ? {} : {suffix}),
  };
}

function bounds(schema: JsonObject | undefined): {minimum?: number; maximum?: number} {
  const minimum = schema?.['minimum'];
  const maximum = schema?.['maximum'];
  return {
    ...(typeof minimum === 'number' ? {minimum} : {}),
    ...(typeof maximum === 'number' ? {maximum} : {}),
  };
}

function ChoiceField(props: ControlProps): ReactElement {
  const options = props.field.options ?? [];
  const value = text(props.value);
  const known = options.some((option) => option.value === value);
  const choices = known ? options : [{value: '', label: 'Not set'}, ...options];
  return (
    <ChoiceControl
      {...props.common}
      value={known ? value : ''}
      choices={choices}
      onValue={(next) => {
        props.onChange(next === '' ? undefined : next);
      }}
    />
  );
}
