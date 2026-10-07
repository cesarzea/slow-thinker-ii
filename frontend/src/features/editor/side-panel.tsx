import {useState} from 'react';
import type {ReactElement} from 'react';
import {Icon} from '../../ui/index.ts';

type Side = 'left' | 'right';

function stored(key: string): boolean {
  try {
    return localStorage.getItem(key) === 'true';
  } catch {
    return false;
  }
}

function store(key: string, collapsed: boolean): void {
  try {
    localStorage.setItem(key, String(collapsed));
  } catch {
    return;
  }
}

/** Whether a side panel is collapsed to a rail; remembered in this browser when storage allows. */
export function usePanelCollapsed(side: Side): [boolean, () => void] {
  const key = `slow-thinker-ii.${side}-panel-collapsed`;
  const [collapsed, setCollapsed] = useState(() => stored(key));
  const toggle = (): void => {
    store(key, !collapsed);
    setCollapsed(!collapsed);
  };
  return [collapsed, toggle];
}

/** The one collapse control of both side panels: a round button on the panel's inner edge. */
export function PanelToggle(props: {
  readonly side: Side;
  readonly name: string;
  readonly collapsed: boolean;
  readonly onToggle: () => void;
}): ReactElement {
  const label = `${props.collapsed ? 'Show' : 'Hide'} ${props.name}`;
  const pointsLeft = (props.side === 'left') !== props.collapsed;
  return (
    <button
      type="button"
      className={`panel-toggle ${props.side} ${pointsLeft ? 'points-left' : 'points-right'}`}
      aria-label={label}
      title={label}
      aria-expanded={!props.collapsed}
      onClick={props.onToggle}
    >
      <Icon name="chevron-down" size={14} />
    </button>
  );
}

const WIDTH_KEY = 'slow-thinker-ii.right-panel-width';
const MIN_WIDTH = 260;

function storedWidth(): number {
  try {
    const value = Number(localStorage.getItem(WIDTH_KEY));
    return Number.isFinite(value) && value >= MIN_WIDTH ? value : 320;
  } catch {
    return 320;
  }
}

/** The right panel's width in pixels; remembered in this browser when storage allows. */
export function usePanelWidth(): [number, (width: number) => void] {
  const [width, setWidth] = useState(storedWidth);
  return [
    width,
    (next) => {
      setWidth(next);
      try {
        localStorage.setItem(WIDTH_KEY, String(Math.round(next)));
      } catch {
        // The width then lasts until the page is left.
      }
    },
  ];
}

/** The widest the right panel can be: the editor body less the left panel. */
function widest(handle: HTMLElement): number {
  const body = handle.parentElement;
  const left = body?.firstElementChild?.getBoundingClientRect().width ?? 0;
  return (body?.getBoundingClientRect().width ?? 0) - left;
}

/** Follows the pointer until it is released, resizing from the body's right edge. */
function dragFrom(handle: HTMLElement, pointerId: number, onResize: (width: number) => void): void {
  handle.setPointerCapture(pointerId);
  const right = handle.parentElement?.getBoundingClientRect().right ?? 0;
  const max = widest(handle);
  const move = (moved: PointerEvent): void => {
    onResize(Math.min(max, Math.max(MIN_WIDTH, right - moved.clientX)));
  };
  const stop = (): void => {
    handle.removeEventListener('pointermove', move);
    handle.removeEventListener('pointerup', stop);
  };
  handle.addEventListener('pointermove', move);
  handle.addEventListener('pointerup', stop);
}

/**
 * The right panel's resize handle on its inner edge: drag to any width, up to covering the
 * whole canvas; a double click switches between full width and the usual width.
 */
export function PanelResizer(props: {
  readonly width: number;
  readonly onResize: (width: number) => void;
}): ReactElement {
  return (
    <div
      className="panel-resizer"
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize the panel"
      title="Drag to resize; double-click to fill or restore"
      onPointerDown={(event) => {
        dragFrom(event.currentTarget, event.pointerId, props.onResize);
      }}
      onDoubleClick={(event) => {
        const max = widest(event.currentTarget);
        props.onResize(props.width >= max - 1 ? 320 : max);
      }}
    />
  );
}
