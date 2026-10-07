import {useEffect, useRef, useState} from 'react';
import type {FocusEvent, KeyboardEvent, MouseEvent, ReactElement, RefObject} from 'react';
import type {NodeActions} from './node-actions.ts';
import type {CardNode} from './types.ts';

interface Open {
  readonly node: CardNode;
  readonly left: number;
  readonly top: number;
}

function entries(open: Open, actions: NodeActions): {label: string; act: () => void}[] {
  const {node} = open;
  const band = node.data.band;
  return [
    {
      label: 'Edit configuration',
      act: () => {
        actions.edit(node.id);
      },
    },
    {
      label: 'Delete',
      act: () => {
        actions.remove(node.id);
      },
    },
    ...(band === null
      ? []
      : [
          {
            label: `Remove ${band.label}`,
            act: () => {
              actions.removeComponent(node.id);
            },
          },
        ]),
  ];
}

function keys(event: KeyboardEvent<HTMLDivElement>, close: () => void): void {
  const items = [...event.currentTarget.querySelectorAll<HTMLElement>('[role="menuitem"]')];
  const index = items.indexOf(document.activeElement as HTMLElement);
  const step = {ArrowDown: 1, ArrowUp: -1}[event.key];
  if (step !== undefined) {
    event.preventDefault();
    items[(index + step + items.length) % items.length]?.focus();
  }
  if (event.key === 'Escape') close();
}

function CardMenu(props: {
  readonly open: Open;
  readonly actions: NodeActions;
  readonly close: () => void;
}): ReactElement {
  const menu = useRef<HTMLDivElement>(null);
  useEffect(() => {
    menu.current?.querySelector<HTMLElement>('[role="menuitem"]')?.focus();
  }, []);
  const blur = (event: FocusEvent<HTMLDivElement>): void => {
    if (!event.currentTarget.contains(event.relatedTarget)) props.close();
  };
  return (
    <div
      ref={menu}
      role="menu"
      aria-label={`Actions for ${props.open.node.data.name}`}
      className="menu-list card-menu"
      style={{left: props.open.left, top: props.open.top}}
      onBlur={blur}
      onKeyDown={(event) => {
        keys(event, props.close);
      }}
    >
      <MenuEntries {...props} />
    </div>
  );
}

function MenuEntries(props: {
  readonly open: Open;
  readonly actions: NodeActions;
  readonly close: () => void;
}): ReactElement {
  return (
    <>
      {entries(props.open, props.actions).map((entry) => (
        <button
          key={entry.label}
          type="button"
          role="menuitem"
          tabIndex={-1}
          className={entry.label === 'Delete' ? 'menu-item danger' : 'menu-item'}
          onClick={() => {
            props.close();
            entry.act();
          }}
        >
          {entry.label}
        </button>
      ))}
    </>
  );
}

/** A card's right-click menu: Edit configuration, Delete and Remove <component>. */
export function useCardMenu(
  frame: RefObject<HTMLElement | null>,
  actions: NodeActions | null,
): {
  readonly onNodeContextMenu: (event: MouseEvent, node: CardNode) => void;
  readonly menu: ReactElement | null;
} {
  const [open, setOpen] = useState<Open | null>(null);
  const onNodeContextMenu = (event: MouseEvent, node: CardNode): void => {
    const bounds = frame.current?.getBoundingClientRect();
    if (actions === null || bounds === undefined) return;
    event.preventDefault();
    setOpen({node, left: event.clientX - bounds.left, top: event.clientY - bounds.top});
  };
  const close = (): void => {
    setOpen(null);
  };
  const menu =
    open === null || actions === null ? null : (
      <CardMenu open={open} actions={actions} close={close} />
    );
  return {onNodeContextMenu, menu};
}
