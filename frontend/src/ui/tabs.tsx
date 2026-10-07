import {Fragment, useId, useRef} from 'react';
import type {KeyboardEvent, ReactElement, ReactNode, RefObject} from 'react';

/** A heading over consecutive tabs, named by its label and drawn with an optional icon. */
export interface TabGroup {
  readonly label: string;
  readonly icon?: ReactNode;
}
interface TabItem {
  readonly key: string;
  readonly title: string;
  readonly marker?: string;
  readonly group?: TabGroup;
}
export interface TabsProps {
  readonly label: string;
  readonly items: readonly TabItem[];
  readonly selected: string;
  readonly onSelect: (key: string) => void;
  readonly children: ReactNode;
  /** Vertical tabs form a list beside the panel and also move with the up and down arrows. */
  readonly orientation?: 'horizontal' | 'vertical';
}
type Move = (index: number, count: number) => number;

const next: Move = (index, count) => (index + 1) % count;
const previous: Move = (index, count) => (index - 1 + count) % count;
const HORIZONTAL: Readonly<Record<string, Move>> = {
  ArrowRight: next,
  ArrowLeft: previous,
  Home: () => 0,
  End: (_index, count) => count - 1,
};
const VERTICAL: Readonly<Record<string, Move>> = {
  ...HORIZONTAL,
  ArrowDown: next,
  ArrowUp: previous,
};

function useTabKeys(
  props: TabsProps,
  selectedIndex: number,
): {list: RefObject<HTMLDivElement | null>; keyDown: (event: KeyboardEvent) => void} {
  const list = useRef<HTMLDivElement>(null);
  const keyDown = (event: KeyboardEvent): void => {
    const move = (props.orientation === 'vertical' ? VERTICAL : HORIZONTAL)[event.key];
    if (move === undefined || props.items.length === 0) return;
    event.preventDefault();
    const target = move(selectedIndex, props.items.length);
    props.onSelect(props.items[target]?.key ?? props.selected);
    list.current?.querySelectorAll<HTMLElement>('[role="tab"]')[target]?.focus();
  };
  return {list, keyDown};
}

/**
 * Tabs named by their titles, with arrow-key navigation and one visible panel. The panel is
 * replaced on every switch, so each section opens at its top.
 */
export function Tabs(props: TabsProps): ReactElement {
  const base = useId();
  const selectedIndex = Math.max(0, props.items.map((item) => item.key).indexOf(props.selected));
  const selectedKey = props.items[selectedIndex]?.key ?? '';
  const {list, keyDown} = useTabKeys(props, selectedIndex);
  const vertical = props.orientation === 'vertical';
  return (
    <div className={vertical ? 'tabs tabs-vertical' : 'tabs'}>
      <div
        role="tablist"
        aria-label={props.label}
        aria-orientation={vertical ? 'vertical' : undefined}
        ref={list}
        onKeyDown={keyDown}
      >
        <TabList {...props} base={base} selectedIndex={selectedIndex} />
      </div>
      <div
        key={selectedKey}
        role="tabpanel"
        id={`${base}-panel`}
        aria-labelledby={`${base}-${selectedKey}`}
        className="tab-panel"
      >
        {props.children}
      </div>
    </div>
  );
}

function TabList(
  props: TabsProps & {readonly base: string; readonly selectedIndex: number},
): ReactElement {
  const label = (index: number): string | undefined => props.items[index]?.group?.label;
  const groupId = (group: string): string =>
    `${props.base}-group-${String(props.items.findIndex((item) => item.group?.label === group))}`;
  return (
    <>
      {props.items.map((item, index) => (
        <Fragment key={item.key}>
          {item.group !== undefined && item.group.label !== label(index - 1) && (
            <span className="tab-group" id={groupId(item.group.label)} aria-hidden="true">
              {item.group.icon}
              {item.group.label}
            </span>
          )}
          <Tab
            base={props.base}
            item={item}
            selected={index === props.selectedIndex}
            describedBy={item.group === undefined ? undefined : groupId(item.group.label)}
            onSelect={props.onSelect}
          />
        </Fragment>
      ))}
    </>
  );
}

function Tab(props: {
  readonly base: string;
  readonly item: TabItem;
  readonly selected: boolean;
  readonly describedBy: string | undefined;
  readonly onSelect: (key: string) => void;
}): ReactElement {
  const {item} = props;
  return (
    <button
      type="button"
      role="tab"
      id={`${props.base}-${item.key}`}
      aria-label={item.title}
      aria-describedby={props.describedBy}
      aria-selected={props.selected}
      aria-controls={`${props.base}-panel`}
      tabIndex={props.selected ? 0 : -1}
      onClick={() => {
        props.onSelect(item.key);
      }}
    >
      {item.title}
      {item.marker !== undefined && <span className="marker">{item.marker}</span>}
    </button>
  );
}
