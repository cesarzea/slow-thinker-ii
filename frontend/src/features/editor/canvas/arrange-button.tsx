import type {ReactElement} from 'react';
import type {Catalog, GraphDocument} from '../../../api/index.ts';
import {Button, MenuButton} from '../../../ui/index.ts';
import type {LayoutChoice as ArrangeMode} from '../state/layouts.ts';
import {useArrange} from './use-arrange.ts';
import type {Placement} from './use-arrange.ts';

interface Props {
  readonly document: GraphDocument;
  readonly catalog: Catalog;
  /** Takes the arranged positions: a saved change in the editor, a local view in a run. */
  readonly onArrange: (placed: Placement) => void;
}

/** The arrangements by group: the port-aware ones, then React Flow's layout examples. */
const ARRANGEMENTS: readonly (readonly [string, string, ArrangeMode])[] = [
  ['ELK with ports', 'Fit to screen', 'fit'],
  ['ELK with ports', 'Compact', 'compact'],
  ['ELK with ports', 'ELK with ports (by flow)', 'flow'],
  ['ELK tree', 'ELK tree, left to right', 'elk-right'],
  ['ELK tree', 'ELK tree, top to bottom', 'elk-down'],
  ['Dagre tree', 'Dagre tree, left to right (horizontal flow)', 'dagre-right'],
  ['Dagre tree', 'Dagre tree, top to bottom', 'dagre-down'],
];

function ArrangeMenu(props: {
  readonly disabled: boolean;
  readonly arrange: (mode: ArrangeMode) => void;
}): ReactElement {
  const items = ARRANGEMENTS.map(([group, label, mode]) => ({
    group,
    label,
    name: `Arrange: ${label.replace(' (horizontal flow)', '')}`,
    onSelect: () => {
      props.arrange(mode);
    },
  }));
  return (
    <MenuButton
      label="Arrange options"
      icon="chevron-down"
      align="start"
      disabled={props.disabled}
      items={items}
    />
  );
}

/** Arrange to fit the screen, or choose another arrangement from the menu beside it. */
export function Arrange({document, catalog, onArrange}: Props): ReactElement {
  const {busy, arrange} = useArrange(document, catalog, onArrange);
  const disabled = busy || document.nodes.length === 0;
  const start = (mode: ArrangeMode): void => {
    void arrange(mode);
  };
  return (
    <span className="split-button">
      <Button
        size="sm"
        variant="ghost"
        icon="arrange"
        label="Arrange the graph"
        title="Arrange the graph to fit the screen"
        disabled={disabled}
        onClick={() => {
          start('fit');
        }}
      >
        Arrange
      </Button>
      <ArrangeMenu disabled={disabled} arrange={start} />
    </span>
  );
}
