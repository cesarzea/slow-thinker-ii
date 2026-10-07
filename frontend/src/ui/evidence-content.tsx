import type {ReactElement} from 'react';

interface ContentProps {
  readonly value: unknown;
  readonly depth?: number;
}

/** Render recorded content as text or structured JSON, never as markup. */
export function EvidenceContent({value, depth = 0}: ContentProps): ReactElement {
  if (value === undefined || value === null) return <span className="empty-value">Empty</span>;
  if (typeof value !== 'object') return <ScalarContent value={value} />;
  if (depth >= 4) return <pre className="evidence-json">{JSON.stringify(value, null, 2)}</pre>;
  return Array.isArray(value) ? (
    <ArrayContent value={value} depth={depth} />
  ) : (
    <ObjectContent value={value} depth={depth} />
  );
}

function ScalarContent({value}: {readonly value: unknown}): ReactElement {
  return typeof value === 'string' ? (
    <pre className="evidence-text">{value}</pre>
  ) : (
    <span className="evidence-scalar">{JSON.stringify(value)}</span>
  );
}

function ArrayContent(props: {
  readonly value: readonly unknown[];
  readonly depth: number;
}): ReactElement {
  if (props.value.length === 0) return <span className="empty-value">Empty list</span>;
  return (
    <ol className="evidence-list">
      {props.value.map((item, index) => (
        <li key={index}>
          <EvidenceContent value={item} depth={props.depth + 1} />
        </li>
      ))}
    </ol>
  );
}

function ObjectContent(props: {readonly value: object; readonly depth: number}): ReactElement {
  const entries = Object.entries(props.value as Readonly<Record<string, unknown>>);
  if (entries.length === 0) return <span className="empty-value">Empty object</span>;
  return (
    <dl className="evidence-fields">
      {entries.map(([name, item]) => (
        <div key={name}>
          <dt>{name}</dt>
          <dd>
            <EvidenceContent value={item} depth={props.depth + 1} />
          </dd>
        </div>
      ))}
    </dl>
  );
}
