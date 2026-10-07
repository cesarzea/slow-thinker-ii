import {useState} from 'react';
import type {ReactElement} from 'react';
import type {Catalog, GraphNode} from '../../../api/index.ts';
import {Button, ConfigurationSummary} from '../../../ui/index.ts';
import {sectionPreview, sectionSummary} from '../dialogs/sections.ts';
import type {NodeSection} from '../dialogs/sections.ts';

/** Which section rows show their values; every row starts collapsed. */
export interface Expansion {
  readonly expanded: ReadonlySet<string>;
  readonly all: boolean;
  readonly toggle: (key: string) => void;
  readonly toggleAll: () => void;
}

export function useExpansion(keys: readonly string[]): Expansion {
  const [expanded, setExpanded] = useState<ReadonlySet<string>>(() => new Set());
  const all = keys.length > 0 && keys.every((key) => expanded.has(key));
  const toggle = (key: string): void => {
    setExpanded((current) =>
      current.has(key)
        ? new Set([...current].filter((item) => item !== key))
        : new Set([...current, key]),
    );
  };
  const toggleAll = (): void => {
    setExpanded(all ? new Set() : new Set(keys));
  };
  return {expanded, all, toggle, toggleAll};
}

/** Expand all, or Collapse all once every row is expanded. */
export function ExpandAll(props: {readonly expansion: Expansion}): ReactElement {
  return (
    <Button size="sm" variant="ghost" onClick={props.expansion.toggleAll}>
      {props.expansion.all ? 'Collapse all' : 'Expand all'}
    </Button>
  );
}

/** One row per section: a click shows its values, the pencil opens its editor. */
export function SectionRows(props: {
  readonly node: GraphNode;
  readonly catalog: Catalog;
  readonly sections: readonly NodeSection[];
  readonly expansion: Expansion;
  readonly onEdit: (section: string) => void;
}): ReactElement {
  const {node, catalog, expansion} = props;
  return (
    <div className="section-rows">
      {props.sections.map((entry) => (
        <ConfigurationSummary
          key={entry.key}
          title={entry.section.title}
          {...(entry.embedded ? {marker: entry.declaration.label} : {})}
          preview={sectionPreview(node, entry, catalog)}
          values={sectionSummary(node, entry, catalog)}
          expanded={expansion.expanded.has(entry.key)}
          onToggle={() => {
            expansion.toggle(entry.key);
          }}
          onEdit={() => {
            props.onEdit(entry.key);
          }}
        />
      ))}
    </div>
  );
}
