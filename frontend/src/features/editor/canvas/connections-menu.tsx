import {useId, useState} from 'react';
import type {FocusEvent, KeyboardEvent, ReactElement} from 'react';
import {Icon} from '../../../ui/index.ts';
import {viewOf, withView} from './connection-style.ts';
import type {ConnectionStyle} from './connection-style.ts';

import {Curvature} from './curvature-slider.tsx';
import type {ViewProps as Props} from './curvature-slider.tsx';

const STYLES: readonly {label: string; name: string; value: ConnectionStyle}[] = [
  {label: 'Curved', name: 'Curved connections', value: 'curved'},
  {label: 'Simple curve', name: 'Simple curve connections', value: 'simple'},
  {label: 'Routed around boxes', name: 'Connections routed around boxes', value: 'routed'},
];

function StyleChoices(props: Props): ReactElement {
  const {model} = props;
  const style = viewOf(model.document).connections;
  const choose = (connections: ConnectionStyle): void => {
    if (connections !== style) model.change((value) => withView(value, {connections}));
  };
  return (
    <div role="menu" aria-label="Connection style">
      {STYLES.map((item) => (
        <button
          key={item.value}
          type="button"
          role="menuitemradio"
          aria-checked={style === item.value}
          aria-label={item.name}
          className="menu-item"
          onClick={() => {
            choose(item.value);
          }}
        >
          {style === item.value && <Icon name="tick" size={14} />}
          {item.label}
        </button>
      ))}
    </div>
  );
}

/** The menu closes when focus leaves it, or with Escape back to its button. */
function closing(trigger: string, setOpen: (open: boolean) => void) {
  return {
    onBlur: (event: FocusEvent<HTMLDivElement>): void => {
      if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
    },
    onKeyDown: (event: KeyboardEvent<HTMLDivElement>): void => {
      if (event.key !== 'Escape') return;
      setOpen(false);
      document.getElementById(trigger)?.focus();
    },
  };
}

function TriggerButton(props: {
  readonly id: string;
  readonly open: boolean;
  readonly onToggle: () => void;
}): ReactElement {
  return (
    <button
      id={props.id}
      type="button"
      className="btn btn-ghost btn-sm"
      aria-label="Connection style"
      title="Connection style"
      aria-expanded={props.open}
      onClick={props.onToggle}
    >
      <Icon name="connection" />
      Connections
    </button>
  );
}

/**
 * How this graph's connections are drawn, saved with the graph in the editor: curved, with their
 * curvature, or routed around the boxes. Every choice is an ordinary, undoable change.
 */
export function ConnectionsMenu(props: Props): ReactElement {
  const [open, setOpen] = useState(false);
  const trigger = useId();
  const curved = viewOf(props.model.document).connections === 'curved';
  return (
    <div className="menu" {...closing(trigger, setOpen)}>
      <TriggerButton
        id={trigger}
        open={open}
        onToggle={() => {
          setOpen(!open);
        }}
      />
      {open && (
        <div className="menu-list align-start connections-menu">
          <StyleChoices {...props} />
          {curved && <Curvature {...props} />}
        </div>
      )}
    </div>
  );
}
