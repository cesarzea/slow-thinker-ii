import type {DragEvent, ReactElement} from 'react';
import type {ComponentDeclaration} from '../../api/index.ts';
import {KindTile} from '../../ui/index.ts';
import {COMPONENT_DRAG_TYPE} from './canvas/drop.ts';
import {componentRef} from './state/ports.ts';

export type Add = (declaration: ComponentDeclaration) => void;

function startDrag(event: DragEvent<HTMLButtonElement>, component: ComponentDeclaration): void {
  event.dataTransfer.setData(COMPONENT_DRAG_TYPE, componentRef(component));
  event.dataTransfer.effectAllowed = 'copy';
}

function PaletteText({component}: {readonly component: ComponentDeclaration}): ReactElement {
  return (
    <span className="palette-text">
      <span className="palette-name">{component.label}</span>
      <span className="palette-description">{component.description}</span>
    </span>
  );
}

/** A component to add by a click or by dragging it onto the canvas; only its tile when compact. */
export function PaletteItem(props: {
  readonly component: ComponentDeclaration;
  readonly onAdd: Add;
  readonly compact?: boolean;
}): ReactElement {
  const {component} = props;
  const compact = props.compact === true;
  return (
    <li>
      <button
        type="button"
        className={compact ? 'palette-item compact' : 'palette-item'}
        aria-label={`Add ${component.label}`}
        title={compact ? `${component.label}: ${component.description}` : component.description}
        draggable
        onDragStart={(event) => {
          startDrag(event, component);
        }}
        onClick={() => {
          // A compact tile's click expands the collapsed palette instead; dragging still adds.
          if (!compact) props.onAdd(component);
        }}
      >
        <KindTile icon={component.icon} />
        {!compact && <PaletteText component={component} />}
      </button>
    </li>
  );
}
