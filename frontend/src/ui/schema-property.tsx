import type {ReactElement} from 'react';
import {IconButton} from './button.tsx';
import {NumberInput} from './number-control.tsx';
import {isNumeric, propertyTypes} from './schema-rows.ts';
import type {PropertyRow, PropertyType} from './schema-rows.ts';

interface Props {
  readonly row: PropertyRow;
  readonly position: number;
  readonly disabled: boolean;
  readonly onChange: (row: PropertyRow) => void;
  readonly onRemove: () => void;
}

function retyped(row: PropertyRow, type: PropertyType): PropertyRow {
  return isNumeric(type) ? {...row, type} : {name: row.name, type, required: row.required};
}

/** The column headings of the properties table; each input carries its own name. */
export function PropertyHeadings(): ReactElement {
  return (
    <div className="property-row property-headings" aria-hidden="true">
      <span>Name</span>
      <span>Type</span>
      <span>Required</span>
      <span>Minimum</span>
      <span>Maximum</span>
      <span />
    </div>
  );
}

function Bound(props: Props & {readonly bound: 'minimum' | 'maximum'}): ReactElement {
  const {row, bound} = props;
  if (!isNumeric(row.type)) return <span />;
  return (
    <NumberInput
      name={bound === 'minimum' ? 'Minimum' : 'Maximum'}
      integer={row.type === 'integer'}
      disabled={props.disabled}
      value={row[bound]}
      onValue={(value) => {
        props.onChange({...row, [bound]: value});
      }}
    />
  );
}

function NameCell({row, onChange, disabled}: Props): ReactElement {
  return (
    <input
      type="text"
      aria-label="Property name"
      value={row.name}
      disabled={disabled}
      onChange={(event) => {
        onChange({...row, name: event.target.value});
      }}
    />
  );
}

function TypeCell({row, onChange, disabled}: Props): ReactElement {
  return (
    <select
      aria-label="Type"
      value={row.type}
      disabled={disabled}
      onChange={(event) => {
        onChange(retyped(row, event.target.value as PropertyType));
      }}
    >
      {propertyTypes.map((type) => (
        <option key={type.value} value={type.value}>
          {type.label}
        </option>
      ))}
    </select>
  );
}

function RequiredCell({row, onChange, disabled}: Props): ReactElement {
  return (
    <input
      type="checkbox"
      aria-label="Required"
      checked={row.required}
      disabled={disabled}
      onChange={(event) => {
        onChange({...row, required: event.target.checked});
      }}
    />
  );
}

/** One property of an object schema as a table row: name, type, required, bounds, remove. */
export function SchemaProperty(props: Props): ReactElement {
  return (
    <div role="group" aria-label={`Property ${String(props.position)}`} className="property-row">
      <NameCell {...props} />
      <TypeCell {...props} />
      <RequiredCell {...props} />
      <Bound {...props} bound="minimum" />
      <Bound {...props} bound="maximum" />
      <IconButton
        icon="trash"
        label="Remove property"
        disabled={props.disabled}
        onClick={props.onRemove}
      />
    </div>
  );
}
