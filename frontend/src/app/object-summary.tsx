import {useEffect, useRef} from 'react';
import type {ReactElement} from 'react';
import type {GraphDetail, ExecutionPage} from '../api/index.ts';
import type {GraphSelection} from '../features/graph-view/index.ts';

interface Props {
  readonly detail: GraphDetail;
  readonly selection: GraphSelection;
  readonly execution?: ExecutionPage;
  readonly onSelect?: (selection: GraphSelection) => void;
}
export function ObjectSummary(props: Props): ReactElement | null {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    heading.current?.focus();
  }, [props.selection]);
  if (props.selection.kind !== 'component' && props.selection.kind !== 'node') return null;
  const section = props.selection.kind === 'component' ? 'components' : 'nodes';
  const record = props.detail.definition[section];
  const selected =
    record !== null && typeof record === 'object' && !Array.isArray(record)
      ? record[props.selection.id]
      : undefined;
  return (
    <section aria-label="Selected object">
      <h3 ref={heading} tabIndex={-1}>
        {props.selection.kind}: {props.selection.id}
      </h3>
      <pre>
        {selected === undefined ? 'Configuration unavailable.' : JSON.stringify(selected, null, 2)}
      </pre>
      <ObjectActivations {...props} />
    </section>
  );
}
function ObjectActivations({selection, execution, onSelect}: Props): ReactElement {
  const items =
    execution?.activations.filter((item) =>
      selection.kind === 'node' ? item.node === selection.id : item.component === selection.id,
    ) ?? [];
  return (
    <>
      <h4>Activations for this object</h4>
      {items.length === 0 && <p>No activations in the visible snapshot.</p>}
      <ul>
        {items.map((item) => (
          <li key={item.id}>
            <button
              onClick={() => {
                onSelect?.({kind: 'activation', id: item.id});
              }}
            >
              #{item.ordinal} · {item.id} · {item.state}
            </button>
          </li>
        ))}
      </ul>
    </>
  );
}
