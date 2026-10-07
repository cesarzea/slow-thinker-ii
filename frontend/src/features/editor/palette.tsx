import {useState} from 'react';
import {insideOnly} from './state/embed-into.ts';
import type {ReactElement} from 'react';
import type {Catalog, ComponentDeclaration} from '../../api/index.ts';
import {Icon} from '../../ui/index.ts';
import {PaletteItem} from './palette-item.tsx';
import type {Add} from './palette-item.tsx';
import {componentRef} from './state/ports.ts';

function PaletteGroup(props: {
  readonly title: string;
  readonly components: readonly ComponentDeclaration[];
  readonly onAdd: Add;
}): ReactElement | null {
  if (props.components.length === 0) return null;
  return (
    <section className="palette-group" aria-label={props.title}>
      <h3>{props.title}</h3>
      <ul>
        {props.components.map((component) => (
          <PaletteItem key={componentRef(component)} component={component} onAdd={props.onAdd} />
        ))}
      </ul>
    </section>
  );
}

function matching(catalog: Catalog, query: string): ComponentDeclaration[] {
  const words = query.toLowerCase().split(/\s+/u).filter(Boolean);
  return catalog.components.filter((component) => {
    const text = `${component.label} ${component.description}`.toLowerCase();
    return words.every((word) => text.includes(word));
  });
}

function SearchBox(props: {
  readonly query: string;
  readonly onQuery: (query: string) => void;
}): ReactElement {
  return (
    <label className="search">
      <Icon name="search" size={14} />
      <input
        type="search"
        aria-label="Search components"
        placeholder="Search components"
        value={props.query}
        onChange={(event) => {
          props.onQuery(event.target.value);
        }}
      />
    </label>
  );
}

/** The collapsed palette: a narrow rail of component tiles, still clickable and draggable. */
function PaletteRail(props: PaletteProps & {readonly onExpand: () => void}): ReactElement {
  const components = matching(props.catalog, '').toSorted(
    (a, b) => Number(a.origin !== 'platform') - Number(b.origin !== 'platform'),
  );
  return (
    <nav className="palette collapsed" aria-label="Components" onClick={props.onExpand}>
      <ul className="palette-rail">
        {components.map((component) => (
          <PaletteItem
            key={componentRef(component)}
            component={component}
            onAdd={props.onAdd}
            compact
          />
        ))}
      </ul>
    </nav>
  );
}

interface PaletteProps {
  readonly catalog: Catalog;
  readonly onAdd: Add;
}

/** The palette's groups: platform nodes, installed nodes, and what goes inside a node. */
const GROUPS: readonly (readonly [string, (item: ComponentDeclaration) => boolean])[] = [
  ['Platform', (item) => item.origin === 'platform' && !insideOnly(item)],
  ['Installed', (item) => item.origin !== 'platform' && !insideOnly(item)],
  ['Inside a node', insideOnly],
];

function FullPalette(props: PaletteProps): ReactElement {
  const [query, setQuery] = useState('');
  const found = matching(props.catalog, query);
  return (
    <nav className="palette" aria-label="Components">
      <div className="palette-heading">
        <h2 className="panel-title">Components</h2>
      </div>
      <SearchBox query={query} onQuery={setQuery} />
      {GROUPS.map(([title, belongs]) => (
        <PaletteGroup
          key={title}
          title={title}
          components={found.filter(belongs)}
          onAdd={props.onAdd}
        />
      ))}
      {found.length === 0 && <p className="muted">No component matches “{query}”.</p>}
      <p className="palette-hint">
        Drag onto the canvas, or click to add. Drag “Inside a node” components onto a node.
      </p>
    </nav>
  );
}

/**
 * Every component that can be a node, platform components first, searchable; it collapses
 * to a rail of tiles.
 */
export function Palette(
  props: PaletteProps & {readonly collapsed: boolean; readonly onExpand: () => void},
): ReactElement {
  return props.collapsed ? <PaletteRail {...props} /> : <FullPalette {...props} />;
}
