import {useState} from 'react';
import type {ReactElement} from 'react';
import {render} from '@testing-library/react';
import type {JsonObject, JsonValue, LlmEntry, UiField} from '../../src/api/index.ts';
import {ConfigurationField, ParameterForm} from '../../src/ui/index.ts';
import {catalog} from './contract.ts';

export interface Changes<T> {
  readonly values: T[];
  readonly latest: () => T | undefined;
}

function recorder<T>(): Changes<T> {
  const values: T[] = [];
  return {values, latest: () => values.at(-1)};
}

interface FieldOptions {
  readonly schema?: JsonObject;
  readonly services?: readonly LlmEntry[];
  readonly disabled?: boolean;
}

/** Render one configuration field around local state and record every change. */
export function renderField(
  field: UiField,
  initial: JsonValue | undefined,
  options: FieldOptions = {},
): Changes<JsonValue | undefined> {
  const changes = recorder<JsonValue | undefined>();
  function Harness(): ReactElement {
    const [value, setValue] = useState(initial);
    return (
      <ConfigurationField
        field={field}
        schema={options.schema}
        value={value}
        services={options.services ?? catalog.llms}
        disabled={options.disabled === true}
        onChange={(next) => {
          changes.values.push(next);
          setValue(next);
        }}
      />
    );
  }
  render(<Harness />);
  return changes;
}

/** Render a provider parameter form around local state and record every change. */
export function renderParameters(schema: JsonObject, initial: JsonObject): Changes<JsonObject> {
  const changes = recorder<JsonObject>();
  function Harness(): ReactElement {
    const [value, setValue] = useState(initial);
    return (
      <ParameterForm
        schema={schema}
        value={value}
        onChange={(next) => {
          changes.values.push(next);
          setValue(next);
        }}
      />
    );
  }
  render(<Harness />);
  return changes;
}
