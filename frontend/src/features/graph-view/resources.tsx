import type {ReactElement} from 'react';
import type {GraphStructure} from '../../api/index.ts';
import type {GraphViewProps} from './types.ts';

interface Props extends Pick<GraphViewProps, 'onSelect'> {
  readonly structure: GraphStructure;
}
export function Resources({structure, onSelect}: Props): ReactElement {
  const resources = structure.components.filter((item) => item.roles.includes('resource'));
  return (
    <section className="graph-resources" aria-label="Resources">
      <h3>Resources</h3>
      {resources.length === 0 ? (
        <p>No declared resources available.</p>
      ) : (
        <ul>
          {resources.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => {
                  onSelect?.({kind: 'component', id: item.id});
                }}
              >
                {item.id}
              </button>
              {' · '}
              {item.type_id}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
