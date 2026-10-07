import type {KeyboardEvent, ReactElement} from 'react';
import {Icon} from './icons.tsx';

export interface MenuItem {
  readonly label: string;
  readonly onSelect: () => void;
  readonly danger?: boolean;
  /** The accessible name, when it differs from the label. */
  readonly name?: string;
  /** One of a set of choices, shown with a tick when chosen. */
  readonly checked?: boolean;
  /** A heading over this item and those after it with the same group. */
  readonly group?: string;
}

/** Consecutive items with the same group, each run under its heading. */
function grouped(all: readonly MenuItem[]): {heading?: string; items: MenuItem[]}[] {
  const runs: {heading?: string; items: MenuItem[]}[] = [];
  for (const item of all) {
    const last = runs.at(-1);
    if (last !== undefined && last.heading === item.group) last.items.push(item);
    else runs.push({...(item.group === undefined ? {} : {heading: item.group}), items: [item]});
  }
  return runs;
}

export function items(menu: HTMLElement | null): HTMLElement[] {
  return [...(menu?.querySelectorAll<HTMLElement>('[role^="menuitem"]') ?? [])];
}

/** Arrow keys move between items; Escape closes and returns to the button. */
function menuKey(event: KeyboardEvent<HTMLDivElement>, close: () => void): void {
  const all = items(event.currentTarget);
  const index = all.indexOf(document.activeElement as HTMLElement);
  const step = {ArrowDown: 1, ArrowUp: -1}[event.key];
  if (step !== undefined) {
    event.preventDefault();
    all[(index + step + all.length) % all.length]?.focus();
  }
  if (event.key === 'Escape') {
    event.preventDefault();
    event.stopPropagation();
    close();
  }
}

function MenuEntry(props: {readonly item: MenuItem; readonly close: () => void}): ReactElement {
  const {item} = props;
  const choice = item.checked === undefined ? {} : {'aria-checked': item.checked};
  return (
    <button
      type="button"
      role={item.checked === undefined ? 'menuitem' : 'menuitemradio'}
      {...choice}
      aria-label={item.name}
      tabIndex={-1}
      className={item.danger === true ? 'menu-item danger' : 'menu-item'}
      onClick={() => {
        props.close();
        item.onSelect();
      }}
    >
      {item.checked === true && <Icon name="tick" size={14} />}
      {item.label}
    </button>
  );
}

/** A run of items under its heading, if it has one. */
function MenuGroup(props: {
  readonly heading?: string;
  readonly items: readonly MenuItem[];
  readonly close: () => void;
}): ReactElement {
  return (
    <div role="group" aria-label={props.heading} className="menu-group">
      {props.heading !== undefined && (
        <span className="menu-heading" aria-hidden="true">
          {props.heading}
        </span>
      )}
      {props.items.map((item) => (
        <MenuEntry key={item.label} item={item} close={props.close} />
      ))}
    </div>
  );
}

/** The open menu: its items in their groups, moved through with the arrow keys. */
export function MenuList(props: {
  readonly id: string;
  readonly label: string;
  readonly items: readonly MenuItem[];
  readonly align?: 'start' | 'end';
  readonly close: () => void;
}): ReactElement {
  return (
    <div
      id={props.id}
      role="menu"
      aria-label={props.label}
      className={props.align === 'start' ? 'menu-list align-start' : 'menu-list'}
      onKeyDown={(event) => {
        menuKey(event, props.close);
      }}
    >
      {grouped(props.items).map((run) => (
        <MenuGroup key={run.heading ?? run.items[0]?.label} {...run} close={props.close} />
      ))}
    </div>
  );
}
