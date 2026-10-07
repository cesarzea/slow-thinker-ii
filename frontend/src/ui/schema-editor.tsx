import {useId, useState} from 'react';
import type {ReactElement} from 'react';
import type {JsonValue} from '../api/index.ts';
import {descriptionIds, FieldHelp} from './field-help.tsx';
import {Button} from './button.tsx';
import {PropertyHeadings, SchemaProperty} from './schema-property.tsx';
import {rowsFromSchema, schemaFromRows} from './schema-rows.ts';
import type {PropertyRow} from './schema-rows.ts';

export interface SchemaEditorProps {
  readonly label: string;
  readonly value: JsonValue | undefined;
  readonly onChange: (value: JsonValue) => void;
  readonly emptyLabel?: string;
  readonly disabled?: boolean;
  readonly describedBy?: string;
  readonly help?: string;
}
interface KeyedRow {
  readonly key: number;
  readonly row: PropertyRow;
}
type Change = (value: JsonValue) => void;

/** Edits an object schema property by property; other schemas are kept and shown read-only. */
export function SchemaEditor(props: SchemaEditorProps): ReactElement {
  const empty = props.emptyLabel !== undefined && (props.value ?? null) === null;
  const disabled = props.disabled === true;
  const help = useId();
  return (
    <fieldset
      className="schema-editor"
      aria-describedby={descriptionIds(help, props.help, props.describedBy)}
    >
      <legend>{props.label}</legend>
      <FieldHelp id={help} text={props.help} />
      {props.emptyLabel !== undefined && (
        <FormatChoice {...props} emptyLabel={props.emptyLabel} empty={empty} disabled={disabled} />
      )}
      {!empty && <SchemaBody value={props.value} onChange={props.onChange} disabled={disabled} />}
    </fieldset>
  );
}

function FormatChoice(props: {
  readonly label: string;
  readonly emptyLabel: string;
  readonly empty: boolean;
  readonly disabled: boolean;
  readonly onChange: Change;
}): ReactElement {
  const name = useId();
  const option = (label: string, checked: boolean, value: JsonValue): ReactElement => (
    <label className="radio">
      <input
        type="radio"
        name={name}
        checked={checked}
        disabled={props.disabled}
        onChange={() => {
          props.onChange(value);
        }}
      />
      {label}
    </label>
  );
  return (
    <div role="radiogroup" aria-label={props.label} className="format-choice">
      {option(props.emptyLabel, props.empty, null)}
      {option('JSON schema', !props.empty, schemaFromRows([]))}
    </div>
  );
}

function SchemaBody(props: {
  readonly value: JsonValue | undefined;
  readonly onChange: Change;
  readonly disabled: boolean;
}): ReactElement {
  const rows = rowsFromSchema(props.value);
  if (rows === null)
    return (
      <div className="schema-read-only">
        <p className="field-note">This schema can be kept but not edited here.</p>
        <pre>{JSON.stringify(props.value, null, 2)}</pre>
      </div>
    );
  return <PropertyEditor initial={rows} onChange={props.onChange} disabled={props.disabled} />;
}

interface EditorProps {
  readonly initial: readonly PropertyRow[];
  readonly onChange: Change;
  readonly disabled: boolean;
}

function useRows(props: EditorProps): {
  rows: readonly KeyedRow[];
  update: (next: readonly KeyedRow[]) => void;
  add: () => void;
} {
  const [rows, setRows] = useState<readonly KeyedRow[]>(() =>
    props.initial.map((row, key) => ({key, row})),
  );
  const update = (next: readonly KeyedRow[]): void => {
    setRows(next);
    props.onChange(schemaFromRows(next.map((entry) => entry.row)));
  };
  const key = Math.max(-1, ...rows.map((entry) => entry.key)) + 1;
  const add = (): void => {
    update([...rows, {key, row: {name: '', type: 'string', required: false}}]);
  };
  return {rows, update, add};
}

function PropertyRows(props: EditorProps & ReturnType<typeof useRows>): ReactElement {
  const {rows, update} = props;
  if (rows.length === 0) return <p className="field-note">No properties yet.</p>;
  return (
    <div className="property-table">
      <PropertyHeadings />
      {rows.map((entry, index) => (
        <SchemaProperty
          key={entry.key}
          row={entry.row}
          position={index + 1}
          disabled={props.disabled}
          onChange={(row) => {
            update(rows.with(index, {key: entry.key, row}));
          }}
          onRemove={() => {
            update(rows.filter((item) => item.key !== entry.key));
          }}
        />
      ))}
    </div>
  );
}

function PropertyEditor(props: EditorProps): ReactElement {
  const rows = useRows(props);
  return (
    <div className="schema-properties">
      <PropertyRows {...props} {...rows} />
      <Button variant="ghost" size="sm" icon="plus" disabled={props.disabled} onClick={rows.add}>
        Add property
      </Button>
    </div>
  );
}
