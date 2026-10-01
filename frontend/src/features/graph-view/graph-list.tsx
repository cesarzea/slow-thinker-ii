import type {ReactElement} from 'react';
import type {ExecutionPage, GraphStructure, ComponentView} from '../../api/index.ts';
import {componentRole} from './component-role.ts';
import {EvidenceList} from './evidence-list.tsx';
import type {GraphViewProps} from './types.ts';

interface Props extends Pick<GraphViewProps, 'onSelect'> {
  readonly structure: GraphStructure;
  readonly execution: ExecutionPage | undefined;
}
export function GraphList({structure, execution, onSelect}: Props): ReactElement {
  return (
    <details className="graph-evidence">
      <summary>Explore graph and evidence</summary>
      <Objects structure={structure} onSelect={onSelect} />
      <EvidenceList execution={execution} onSelect={onSelect} />
    </details>
  );
}
function Objects({structure, onSelect}: Omit<Props, 'execution'>): ReactElement {
  return (
    <ul aria-label="Graph objects">
      {structure.components.map((item) => (
        <ComponentItem key={item.id} item={item} onSelect={onSelect} />
      ))}
      {structure.nodes.map((item) => (
        <li key={`node:${item.id}`}>
          <button
            onClick={() => {
              onSelect?.({kind: 'node', id: item.id});
            }}
          >
            Step {item.id}
          </button>
          {' · '}
          {item.component}
        </li>
      ))}
    </ul>
  );
}
function ComponentItem({
  item,
  onSelect,
}: Pick<Props, 'onSelect'> & {readonly item: ComponentView}): ReactElement {
  return (
    <li>
      <button
        onClick={() => {
          onSelect?.({kind: 'component', id: item.id});
        }}
      >
        Component {item.id}
      </button>
      {' · '}
      {componentRole(item)}
      {item.contained_by !== null && ` · Inside ${item.contained_by}`}
    </li>
  );
}
