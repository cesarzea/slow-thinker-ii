import {useId} from 'react';
import type {ReactElement} from 'react';
import {descriptionIds, FieldHelp} from './field-help.tsx';

export interface ListControlProps {
  readonly label: string;
  readonly itemLabel: string;
  readonly value: readonly string[];
  readonly onChange: (value: string[]) => void;
  readonly disabled?: boolean;
  readonly describedBy?: string;
  readonly help?: string;
}
type Direction = 'up' | 'down';
interface ItemProps {
  readonly name: string;
  readonly item: string;
  readonly first: boolean;
  readonly last: boolean;
  readonly onItem: (value: string) => void;
  readonly onMove: (direction: Direction, list: Element | null) => void;
  readonly onRemove: () => void;
}

/** An ordered list of text items, each named by its label and number, with move and remove. */
export function ListControl(props: ListControlProps): ReactElement {
  const help = useId();
  const add = (): void => {
    props.onChange([...props.value, '']);
  };
  return (
    <fieldset
      className="list-control"
      disabled={props.disabled}
      aria-describedby={descriptionIds(help, props.help, props.describedBy)}
    >
      <legend>{props.label}</legend>
      <FieldHelp id={help} text={props.help} />
      <ListItems {...props} />
      <button type="button" className="list-add" onClick={add}>
        Add {props.itemLabel}
      </button>
    </fieldset>
  );
}

function swapped(value: readonly string[], from: number, to: number): string[] {
  const moving = value[from];
  const other = value[to];
  if (moving === undefined || other === undefined) return [...value];
  return value.with(from, other).with(to, moving);
}

/** Move an item and keep focus on its move button, the other one once it reaches an end. */
function moveItem(
  props: ListControlProps,
  from: number,
  direction: Direction,
  list: Element | null,
): void {
  const to = direction === 'up' ? from - 1 : from + 1;
  props.onChange(swapped(props.value, from, to));
  const end = direction === 'up' ? to === 0 : to === props.value.length - 1;
  const opposite: Direction = direction === 'up' ? 'down' : 'up';
  const focus = end ? opposite : direction;
  list?.querySelectorAll<HTMLElement>(`[data-move="${focus}"]`)[to]?.focus();
}

function ListItems(props: ListControlProps): ReactElement {
  const {itemLabel, value, onChange} = props;
  return (
    <ol>
      {value.map((item, index) => (
        <ListItem
          key={`${itemLabel} ${String(index + 1)}`}
          name={`${itemLabel} ${String(index + 1)}`}
          item={item}
          first={index === 0}
          last={index === value.length - 1}
          onItem={(next) => {
            onChange(value.with(index, next));
          }}
          onMove={(direction, list) => {
            moveItem(props, index, direction, list);
          }}
          onRemove={() => {
            onChange(value.filter((_, position) => position !== index));
          }}
        />
      ))}
    </ol>
  );
}

function MoveButton(
  props: ItemProps & {readonly direction: Direction; readonly disabled: boolean},
): ReactElement {
  return (
    <button
      type="button"
      className="icon-button"
      data-move={props.direction}
      aria-label={`Move ${props.name} ${props.direction}`}
      disabled={props.disabled}
      onClick={(event) => {
        props.onMove(props.direction, event.currentTarget.closest('ol'));
      }}
    >
      {props.direction === 'up' ? '↑' : '↓'}
    </button>
  );
}

function ListItem(props: ItemProps): ReactElement {
  const id = useId();
  return (
    <li>
      <label htmlFor={id}>{props.name}</label>
      <input
        id={id}
        type="text"
        value={props.item}
        onChange={(event) => {
          props.onItem(event.target.value);
        }}
      />
      <MoveButton {...props} direction="up" disabled={props.first} />
      <MoveButton {...props} direction="down" disabled={props.last} />
      <button
        type="button"
        className="icon-button"
        aria-label={`Remove ${props.name}`}
        onClick={props.onRemove}
      >
        ×
      </button>
    </li>
  );
}
