import type {ReactElement} from 'react';
import type {ExecutionPage, GraphStructure} from '../../api/index.ts';
import {componentRole} from './component-role.ts';
import type {GraphSelection} from './types.ts';

interface Props {
  readonly structure: GraphStructure;
  readonly execution: ExecutionPage | undefined;
  readonly onSelect: ((selection: GraphSelection) => void) | undefined;
}
export function GraphList({structure, execution, onSelect}: Props): ReactElement {
  return (
    <details>
      <summary>Explorar componentes, nodos y evidencia en lista</summary>
      <Objects structure={structure} onSelect={onSelect} />
      <ExecutionList execution={execution} onSelect={onSelect} />
    </details>
  );
}
function ExecutionList({execution, onSelect}: Omit<Props, 'structure'>): ReactElement | null {
  if (execution === undefined) return null;
  return (
    <>
      <ol aria-label="Activaciones registradas">
        {execution.activations.map((item) => (
          <li key={item.id}>
            <button
              onClick={() => {
                onSelect?.({kind: 'activation', id: item.id});
              }}
            >
              Activación #{item.ordinal}: {item.node}
            </button>{' '}
            · {item.id} · {item.component} · {item.state} · Puerto:{' '}
            {item.selected_port ?? 'Sin selección registrada'}
          </li>
        ))}
      </ol>
      <CallItems execution={execution} onSelect={onSelect} />
    </>
  );
}

function Objects({structure, onSelect}: Omit<Props, 'execution'>): ReactElement {
  return (
    <ul aria-label="Objetos del grafo">
      <ComponentItems structure={structure} onSelect={onSelect} />
      {structure.nodes.map((item) => (
        <li key={`node:${item.id}`}>
          <button
            onClick={() => {
              onSelect?.({kind: 'node', id: item.id});
            }}
          >
            Nodo {item.id}
          </button>{' '}
          · {item.component}
        </li>
      ))}
    </ul>
  );
}

function ComponentItems({structure, onSelect}: Omit<Props, 'execution'>): ReactElement {
  return (
    <>
      {structure.components.map((item) => (
        <li key={`component:${item.id}`}>
          <button
            onClick={() => {
              onSelect?.({kind: 'component', id: item.id});
            }}
          >
            Componente {item.id}
          </button>
          {' · '}
          {componentRole(item)}
          {item.contained_by !== null && ` · Dentro de ${item.contained_by}`}
        </li>
      ))}
    </>
  );
}

function CallItems({execution, onSelect}: Omit<Props, 'structure'>): ReactElement {
  return (
    <ul aria-label="Comunicaciones observadas">
      {execution?.calls.map((item) => (
        <li key={item.id}>
          <button
            onClick={() => {
              onSelect?.({kind: 'call', id: item.id});
            }}
          >
            Llamada {item.id}
          </button>{' '}
          · {item.caller || 'Orquestador'} → {item.target}.{item.operation} · {item.state} ·
          Activación: {item.activation_id ?? 'No aplicable'} · Origen:{' '}
          {item.parent_call_id ?? 'Raíz'}
        </li>
      ))}
    </ul>
  );
}
