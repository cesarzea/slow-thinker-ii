import {createContext, useContext, useMemo, useState} from 'react';
import type {ReactElement, RefObject} from 'react';
import type {CardPort} from './types.ts';

interface PortTips {
  readonly show: (port: CardPort, handle: Element) => void;
  readonly hide: () => void;
}
interface Shown {
  readonly port: CardPort;
  readonly left: number;
  readonly top: number;
}

/** Shows the tip of the handle under the pointer or in focus; every canvas provides it. */
export const PortTipContext = createContext<PortTips | null>(null);

export function usePortTip(): PortTips | null {
  return useContext(PortTipContext);
}

const GAP = 8;

/** The point beside the handle, away from its card, where the tip starts. */
function anchor(port: CardPort, handle: DOMRect, frame: DOMRect): {left: number; top: number} {
  const middle = {left: handle.left + handle.width / 2, top: handle.top + handle.height / 2};
  const points = {
    left: {left: handle.left - GAP, top: middle.top},
    right: {left: handle.right + GAP, top: middle.top},
    top: {left: middle.left, top: handle.top - GAP},
    bottom: {left: middle.left, top: handle.bottom + GAP},
  };
  const point = points[port.side];
  return {left: point.left - frame.left, top: point.top - frame.top};
}

function linkText(port: CardPort): string {
  if (port.links.length === 0) return 'Not connected';
  return `${port.kind === 'output' ? 'To' : 'From'} ${port.links.join(', ')}`;
}

function PortTip({shown}: {readonly shown: Shown}): ReactElement {
  const {port} = shown;
  return (
    <div
      role="tooltip"
      className={`port-tip tip-${port.side}`}
      style={{left: shown.left, top: shown.top}}
    >
      <strong>{port.name}</strong>
      <span>{linkText(port)}</span>
    </div>
  );
}

/** The canvas's port tips: the full name of a port and what it is connected to. */
export function usePortTips(frame: RefObject<HTMLElement | null>): {
  readonly tips: PortTips;
  readonly tip: ReactElement | null;
} {
  const [shown, setShown] = useState<Shown | null>(null);
  const tips = useMemo<PortTips>(
    () => ({
      show: (port, handle) => {
        const bounds = frame.current?.getBoundingClientRect();
        if (bounds === undefined) return;
        setShown({port, ...anchor(port, handle.getBoundingClientRect(), bounds)});
      },
      hide: () => {
        setShown(null);
      },
    }),
    [frame],
  );
  return {tips, tip: shown === null ? null : <PortTip shown={shown} />};
}
