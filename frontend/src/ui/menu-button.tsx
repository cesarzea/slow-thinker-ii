import {useEffect, useId, useState} from 'react';
import type {FocusEvent, ReactElement} from 'react';
import {Icon} from './icons.tsx';
import type {IconName} from './icons.tsx';
import {MenuList, items} from './menu-list.tsx';
import type {MenuItem} from './menu-list.tsx';

interface MenuButtonProps {
  readonly label: string;
  readonly items: readonly MenuItem[];
  /** The trigger's icon; three dots unless given. */
  readonly icon?: IconName;
  /** The side of the trigger the menu lines up with; the end unless given. */
  readonly align?: 'start' | 'end';
  readonly disabled?: boolean;
  /** Text shown beside the icon; the trigger is then a small ghost button. */
  readonly text?: string;
}

function MenuTrigger(
  props: MenuButtonProps & {
    readonly id: string;
    readonly open: boolean;
    readonly onToggle: () => void;
  },
): ReactElement {
  return (
    <button
      id={props.id}
      type="button"
      className={props.text === undefined ? 'icon-button' : 'btn btn-ghost btn-sm'}
      aria-label={props.label}
      title={props.label}
      aria-haspopup="menu"
      aria-expanded={props.open}
      disabled={props.disabled === true}
      onClick={props.onToggle}
    >
      <Icon name={props.icon ?? 'more'} />
      {props.text}
    </button>
  );
}

/** A button that opens a short menu of actions, named by its label. */
export function MenuButton(props: MenuButtonProps): ReactElement {
  const [open, setOpen] = useState(false);
  const menu = useId();
  useEffect(() => {
    if (open) items(document.getElementById(menu))[0]?.focus();
  }, [open, menu]);
  const close = (): void => {
    setOpen(false);
    document.getElementById(`${menu}-button`)?.focus();
  };
  const blur = (event: FocusEvent<HTMLDivElement>): void => {
    if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
  };
  const toggle = (): void => {
    setOpen(!open);
  };
  return (
    <div className="menu" onBlur={blur}>
      <MenuTrigger {...props} id={`${menu}-button`} open={open} onToggle={toggle} />
      {open && <MenuList {...props} id={menu} close={close} />}
    </div>
  );
}
