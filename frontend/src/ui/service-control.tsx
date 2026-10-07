import type {ReactElement} from 'react';
import type {JsonObject, JsonValue, LlmEntry} from '../api/index.ts';
import {ChoiceControl} from './form-controls.tsx';
import {isJsonObject} from './json.ts';
import {ParameterForm} from './parameter-form.tsx';
import {parameterDefaults} from './parameter-rules.ts';

export interface ServiceSelection {
  readonly llm: string;
  readonly parameters: JsonObject;
}
export interface ServiceControlProps {
  readonly label: string;
  readonly value: JsonValue | undefined;
  readonly onChange: (value: JsonValue) => void;
  readonly services: readonly LlmEntry[];
  readonly disabled?: boolean;
  readonly describedBy?: string;
  readonly help?: string;
}

/** Read a service selection; anything else counts as nothing selected. */
export function serviceSelection(value: JsonValue | undefined): ServiceSelection | null {
  if (!isJsonObject(value) || typeof value['llm'] !== 'string') return null;
  const parameters = value['parameters'];
  return {llm: value['llm'], parameters: isJsonObject(parameters) ? parameters : {}};
}

function newSelection(services: readonly LlmEntry[], id: string): JsonValue {
  const entry = services.find((item) => item.id === id);
  return entry === undefined
    ? null
    : {llm: entry.id, parameters: parameterDefaults(entry.parameters)};
}

function serviceChoices(
  services: readonly LlmEntry[],
  selection: ServiceSelection | null,
): {value: string; label: string}[] {
  const known = services.some((item) => item.id === selection?.llm);
  const missing =
    selection === null || known
      ? []
      : [{value: selection.llm, label: `${selection.llm} (not available)`}];
  return [
    {value: '', label: 'Not selected'},
    ...services.map((item) => ({value: item.id, label: item.label})),
    ...missing,
  ];
}

/** An LLM selector followed by the selected entry's parameter form. */
export function ServiceControl(props: ServiceControlProps): ReactElement {
  const selection = serviceSelection(props.value);
  const entry = props.services.find((item) => item.id === selection?.llm);
  const choices = serviceChoices(props.services, selection);
  const select = (id: string): void => {
    props.onChange(newSelection(props.services, id));
  };
  return (
    <div className="service-control">
      <ChoiceControl
        {...controlProps(props)}
        value={selection?.llm ?? ''}
        choices={choices}
        onValue={select}
      />
      {entry !== undefined && selection !== null && (
        <ParameterForm
          schema={entry.parameters}
          value={selection.parameters}
          disabled={props.disabled === true}
          onChange={(parameters) => {
            props.onChange({llm: entry.id, parameters});
          }}
        />
      )}
    </div>
  );
}

function controlProps(props: ServiceControlProps): {
  label: string;
  disabled: boolean;
  describedBy?: string;
  help?: string;
} {
  return {
    label: props.label,
    disabled: props.disabled === true,
    ...(props.describedBy === undefined ? {} : {describedBy: props.describedBy}),
    ...(props.help === undefined ? {} : {help: props.help}),
  };
}
