import {useId} from 'react';
import type {ReactElement} from 'react';
import type {ComponentDeclaration} from '../../api/index.ts';
import {componentFacts, originText} from './component-facts.ts';
import type {Fact} from './component-facts.ts';
import {ComponentTile} from './component-tile.tsx';

/** Terms and their descriptions. */
export function Facts({facts}: {readonly facts: readonly Fact[]}): ReactElement {
  return (
    <dl className="catalog-facts">
      {facts.map(([term, description]) => (
        <div key={term}>
          <dt>{term}</dt>
          <dd>{description}</dd>
        </div>
      ))}
    </dl>
  );
}

function ComponentCard({component}: {readonly component: ComponentDeclaration}): ReactElement {
  const id = useId();
  return (
    <li className="catalog-card" aria-labelledby={id}>
      <div className="catalog-card-heading">
        <ComponentTile icon={component.icon} />
        <div className="catalog-title">
          <h3 id={id}>{component.label}</h3>
          <code className="catalog-identity">{`${component.type}@${component.version}`}</code>
        </div>
        <span className={`catalog-origin ${component.origin}`}>{originText(component.origin)}</span>
      </div>
      <p className="catalog-description">{component.description}</p>
      <Facts facts={componentFacts(component)} />
    </li>
  );
}

/** Every component of the catalog, platform and installed packages, in catalog order. */
export function ComponentList(props: {
  readonly components: readonly ComponentDeclaration[];
}): ReactElement {
  if (props.components.length === 0)
    return <p className="empty-state">No components are available.</p>;
  return (
    <ul className="catalog-cards">
      {props.components.map((component) => (
        <ComponentCard key={`${component.type}@${component.version}`} component={component} />
      ))}
    </ul>
  );
}
