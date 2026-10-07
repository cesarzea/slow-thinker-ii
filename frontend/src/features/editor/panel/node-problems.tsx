import type {ReactElement} from 'react';
import type {Diagnostic} from '../../../api/index.ts';
import {Icon} from '../../../ui/index.ts';

/** The problems of the selected node, or that it has none. */
export function NodeProblems(props: {
  readonly diagnostics: readonly Diagnostic[];
  readonly nodeId: string;
}): ReactElement {
  const problems = props.diagnostics.filter((item) => item.node_id === props.nodeId);
  if (problems.length === 0)
    return (
      <p className="node-ok">
        <Icon name="check" size={14} />
        No problems in this node
      </p>
    );
  return (
    <ul className="node-problems" aria-label="Problems with this node">
      {problems.map((item) => (
        <li key={`${item.code}:${item.path}:${item.message}`} className={item.severity}>
          <Icon name="alert" size={14} />
          {item.message}
        </li>
      ))}
    </ul>
  );
}
